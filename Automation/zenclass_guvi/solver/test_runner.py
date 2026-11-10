"""
solver/test_runner.py - Sandboxed Subprocess Test Runner.

Executes candidate Python 3 solutions in an isolated subprocess sandbox.
Features:
- Subprocess isolation via `sys.executable -c <code>`
- Stdin feeding and stdout/stderr capture with full UTF-8 encoding fidelity
- Strict configurable timeout enforcement (default 2.0s) with clean process termination
- Intelligent output normalization (CRLF -> LF, line trailing whitespace, float tolerance)
- Zero-leak process cleanup with zero zombie processes
- Full multi-case and single-case backward compatibility
"""

import logging
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any, List, Optional

from solver.extractor import SampleCase

logger = logging.getLogger(__name__)


@dataclass
class TestCaseResult:
    """Detailed execution result for an individual test case."""
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    error_message: str
    duration: float  # seconds
    stderr: str = ""
    exit_code: int = 0

    __test__ = False


@dataclass
class ValidationResult:
    """Aggregated validation result across one or more test cases."""
    all_passed: bool
    passed_count: int
    total_count: int
    results: List[TestCaseResult]

    # --- Backward compatibility properties for E2E harness ---
    @property
    def passed(self) -> bool:
        """Alias for all_passed."""
        return self.all_passed

    @property
    def stdout(self) -> str:
        """Primary test case actual output."""
        return self.results[0].actual_output if self.results else ""

    @property
    def stderr(self) -> str:
        """Primary test case standard error."""
        return self.results[0].stderr if self.results else ""

    @property
    def exit_code(self) -> int:
        """Primary test case process exit code."""
        return self.results[0].exit_code if self.results else 0

    @property
    def duration_ms(self) -> float:
        """Total execution duration in milliseconds."""
        return sum(r.duration for r in self.results) * 1000.0

    @property
    def error_message(self) -> Optional[str]:
        """First encountered failure or timeout message."""
        for r in self.results:
            if not r.passed and r.error_message:
                return r.error_message
        return None


def normalize_output(text: str) -> str:
    """
    Normalizes whitespace and line breaks while preserving logical output:
    1. Normalizes CRLF and CR to LF
    2. Strips trailing whitespace on each line
    3. Strips outer leading/trailing empty lines and whitespace
    """
    if not text:
        return ""
    # Replace CRLF / CR
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    # Join and strip outer whitespace
    return "\n".join(lines).strip()


def outputs_match(actual: str, expected: str) -> bool:
    """
    Compares normalized actual output against expected output.
    Supports exact match, per-token match, and numerical float tolerance.
    """
    norm_actual = normalize_output(actual)
    norm_expected = normalize_output(expected)

    if norm_actual == norm_expected:
        return True

    # Check case-insensitive equality for common yes/no/true/false/even/odd tokens
    if norm_actual.lower() == norm_expected.lower() and norm_expected.lower() in {
        "yes", "no", "true", "false", "even", "odd"
    }:
        return True

    # Check token-by-token comparison with float tolerance
    act_tokens = norm_actual.split()
    exp_tokens = norm_expected.split()
    if len(act_tokens) == len(exp_tokens) and len(act_tokens) > 0:
        match = True
        for a, e in zip(act_tokens, exp_tokens):
            if a == e:
                continue
            try:
                fa, fe = float(a), float(e)
                if not math.isclose(fa, fe, rel_tol=1e-4, abs_tol=1e-4):
                    match = False
                    break
            except ValueError:
                match = False
                break
        if match:
            return True

    return False


def _run_single_case(code: str, input_data: str, expected_output: str, timeout: float) -> TestCaseResult:
    """Executes a single test case in a sandboxed subprocess."""
    # Special boundary condition: empty code, empty input, empty expected output
    if not code.strip():
        if not expected_output.strip():
            return TestCaseResult(
                passed=True,
                input_data=input_data,
                expected_output=expected_output,
                actual_output="",
                error_message="",
                duration=0.0,
                stderr="",
                exit_code=0
            )
        else:
            return TestCaseResult(
                passed=False,
                input_data=input_data,
                expected_output=expected_output,
                actual_output="",
                error_message="Empty code provided for non-empty expected output",
                duration=0.0,
                stderr="",
                exit_code=1
            )

    start_time = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            input=input_data,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        duration = time.time() - start_time
        actual_raw = proc.stdout
        norm_actual = normalize_output(actual_raw)
        norm_expected = normalize_output(expected_output)

        passed = (proc.returncode == 0) and outputs_match(norm_actual, norm_expected)
        err_msg = ""
        if not passed:
            if proc.returncode != 0:
                err_msg = proc.stderr.strip() or f"Process failed with exit code {proc.returncode}"
            else:
                err_msg = f"Output mismatch: got '{norm_actual}', expected '{norm_expected}'"

        return TestCaseResult(
            passed=passed,
            input_data=input_data,
            expected_output=norm_expected,
            actual_output=norm_actual,
            error_message=err_msg,
            duration=duration,
            stderr=proc.stderr.strip(),
            exit_code=proc.returncode
        )

    except subprocess.TimeoutExpired:
        duration = timeout
        return TestCaseResult(
            passed=False,
            input_data=input_data,
            expected_output=normalize_output(expected_output),
            actual_output="",
            error_message=f"Execution timed out after {timeout} seconds",
            duration=duration,
            stderr="TimeoutExpired",
            exit_code=-1
        )
    except Exception as ex:
        duration = time.time() - start_time
        return TestCaseResult(
            passed=False,
            input_data=input_data,
            expected_output=normalize_output(expected_output),
            actual_output="",
            error_message=str(ex),
            duration=duration,
            stderr=str(ex),
            exit_code=-1
        )


def test_solution(code: str, sample_cases: List[Any], timeout: float = 2.0) -> ValidationResult:
    """
    Tests solution code against multiple sample cases.
    Accepts SampleCase instances, dicts, or objects with input/expected attributes.
    """
    if not sample_cases:
        return ValidationResult(
            all_passed=True,
            passed_count=0,
            total_count=0,
            results=[]
        )

    results: List[TestCaseResult] = []
    for sc in sample_cases:
        if isinstance(sc, dict):
            inp = sc.get("input_data", sc.get("input_text", sc.get("input", "")))
            exp = sc.get("expected_output", sc.get("expected", ""))
        else:
            inp = getattr(sc, "input_data", getattr(sc, "input_text", getattr(sc, "input", "")))
            exp = getattr(sc, "expected_output", getattr(sc, "expected", ""))
        res = _run_single_case(code, inp, exp, timeout)
        results.append(res)

    all_passed = all(r.passed for r in results)
    passed_count = sum(1 for r in results if r.passed)

    return ValidationResult(
        all_passed=all_passed,
        passed_count=passed_count,
        total_count=len(results),
        results=results
    )


# Tell pytest not to collect test_solution as a test function
test_solution.__test__ = False


def validate_solution(
    code: str,
    sample_input: str,
    expected_output: str,
    timeout_sec: float = 2.0
) -> ValidationResult:
    """
    Module-level single-case validation function matching PROJECT.md interface.
    """
    res = _run_single_case(code, sample_input, expected_output, timeout_sec)
    return ValidationResult(
        all_passed=res.passed,
        passed_count=1 if res.passed else 0,
        total_count=1,
        results=[res]
    )


class SubprocessSandbox:
    """
    Subprocess sandbox class matching E2E test harness contract.
    Provides static methods for single-case and multi-case testing.
    """
    @staticmethod
    def validate_solution(
        code: str,
        sample_input: str,
        expected_output: str,
        timeout_sec: float = 2.0
    ) -> ValidationResult:
        return validate_solution(code, sample_input, expected_output, timeout_sec)

    @staticmethod
    def test_solution(
        code: str,
        sample_cases: List[Any],
        timeout: float = 2.0
    ) -> ValidationResult:
        return test_solution(code, sample_cases, timeout)
