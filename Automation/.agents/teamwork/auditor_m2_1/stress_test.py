"""
Auditor Forensic Stress Test for Milestone 2 Solver Components.
Executes adversarial checks against SubprocessSandbox, ProblemExtractor, CodeGenerator, and AceEditorAdapter.
"""

import ast
import math
import os
import subprocess
import sys
import time
from unittest.mock import MagicMock

# Add zenclass_guvi to sys.path
ZENCLASS_ROOT = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if ZENCLASS_ROOT not in sys.path:
    sys.path.insert(0, ZENCLASS_ROOT)

from solver.extractor import ProblemExtractor, extract_problem_spec, ProblemSpecification, SampleCase
from solver.code_generator import generate_solution, synthesize_solution, CANONICAL_SOLVERS
from solver.test_runner import SubprocessSandbox, validate_solution, test_solution, outputs_match, normalize_output
from solver.ace_adapter import AceEditorAdapter, inject_code, get_editor_code, wait_for_editor


def run_all_stress_tests():
    print("=== STARTING FORENSIC ADVERSARIAL STRESS TESTS ===")
    failures = []

    # -------------------------------------------------------------
    # 1. Subprocess Sandbox Forensic & Adversarial Checks
    # -------------------------------------------------------------
    print("\n--- [1] Subprocess Sandbox Tests ---")

    # 1.1 Real Python execution and pipe verification
    real_code = "import sys; a, b = map(int, sys.stdin.read().split()); print(a * b + 42)"
    res = validate_solution(real_code, "7 8", "98")
    if not res.passed or res.stdout != "98" or res.exit_code != 0:
        failures.append(f"1.1 Real execution failed: got {res.stdout}, exit={res.exit_code}")
    else:
        print("  ✓ 1.1 Real subprocess computation and stdin/stdout pipe verified.")

    # 1.2 Non-zero exit code
    exit_code = "import sys; sys.exit(77)"
    res = validate_solution(exit_code, "", "")
    if res.passed or res.exit_code != 77:
        failures.append(f"1.2 Non-zero exit code failed: passed={res.passed}, exit={res.exit_code}")
    else:
        print("  ✓ 1.2 Non-zero exit code (77) correctly detected.")

    # 1.3 Syntax error handling
    bad_code = "def foo( invalid syntax here"
    res = validate_solution(bad_code, "", "")
    if res.passed or res.exit_code == 0 or "SyntaxError" not in res.stderr:
        failures.append(f"1.3 Syntax error check failed: passed={res.passed}, stderr={res.stderr}")
    else:
        print("  ✓ 1.3 Syntax error in candidate code correctly flagged.")

    # 1.4 Busy infinite loop timeout and process termination
    t0 = time.time()
    res = validate_solution("while True: pass", "", "", timeout_sec=0.5)
    elapsed = time.time() - t0
    if res.passed or res.exit_code != -1 or "timed out" not in (res.error_message or "").lower():
        failures.append(f"1.4 Infinite loop timeout failed: passed={res.passed}, err={res.error_message}")
    elif elapsed > 2.0:
        failures.append(f"1.4 Timeout took too long: {elapsed:.2f}s instead of ~0.5s")
    else:
        print(f"  ✓ 1.4 Infinite loop cleanly killed after {elapsed:.2f}s with exit_code=-1.")

    # 1.5 Sleeping process timeout
    t0 = time.time()
    res = validate_solution("import time; time.sleep(10)", "", "", timeout_sec=0.4)
    elapsed = time.time() - t0
    if res.passed or res.exit_code != -1 or "timed out" not in (res.error_message or "").lower():
        failures.append(f"1.5 Sleep timeout failed: passed={res.passed}, err={res.error_message}")
    else:
        print(f"  ✓ 1.5 Sleep process cleanly killed after {elapsed:.2f}s.")

    # 1.6 Large output stream handling (100k chars)
    large_code = "print('A' * 100000)"
    res = validate_solution(large_code, "", "A" * 100000)
    if not res.passed or len(res.stdout) != 100000:
        failures.append(f"1.6 Large output failed: len={len(res.stdout)}")
    else:
        print("  ✓ 1.6 Large stdout stream (100,000 chars) captured without buffer truncation.")

    # 1.7 UTF-8 encoding and multilingual Unicode
    utf8_code = "import sys; print('Testing: ' + sys.stdin.read().strip() + ' -> नमस्ते | 🚀 | 你好')"
    res = validate_solution(utf8_code, "Input", "Testing: Input -> नमस्ते | 🚀 | 你好")
    if not res.passed:
        failures.append(f"1.7 UTF-8 multilingual failed: {res.stdout}")
    else:
        print("  ✓ 1.7 Multilingual UTF-8 Unicode characters handled seamlessly.")

    # 1.8 Float tolerance matching
    if not outputs_match("3.14159265", "3.1416"):
        failures.append("1.8 Float tolerance failed for close values")
    if outputs_match("3.1415", "3.2000"):
        failures.append("1.8 Float tolerance incorrectly matched distant values")
    print("  ✓ 1.8 Float tolerance math.isclose checks verified.")

    # -------------------------------------------------------------
    # 2. Problem Extractor Adversarial Checks
    # -------------------------------------------------------------
    print("\n--- [2] Problem Extractor Tests ---")

    # 2.1 Malformed HTML with missing closing tags but labeled text
    malformed_html = """
    <div class="problem-title">Calculate &amp; Compare &lt;X&gt;</div>
    <div class="problem-statement">Given two numbers &quot;a&quot; &amp; &quot;b&#39;s&quot;, output difference.</div>
    <div class="input-description">Line 1: two integers</div>
    <div class="output-description">Difference</div>
    <div class="sample-input">15 5</div>
    <div class="sample-output">10</div>
    """
    spec = extract_problem_spec(malformed_html)
    if spec.title != "Calculate & Compare <X>":
        failures.append(f"2.1 Title entity decoding failed: '{spec.title}'")
    elif "15 5" not in spec.sample_input or "10" not in spec.sample_output:
        failures.append(f"2.1 Sample extraction failed: in='{spec.sample_input}', out='{spec.sample_output}'")
    else:
        print(f"  ✓ 2.1 Malformed HTML and entities unescaped correctly: Title='{spec.title}'")

    # 2.2 Multiple sample cases with Explanation
    multi_case_html = """
    <h1>Array Problem</h1>
    <div>Sample Input 1:</div>
    <pre>3 4</pre>
    <div>Sample Output 1:</div>
    <pre>7</pre>
    <div>Sample Explanation 1: 3 + 4 = 7</div>
    <div>Sample Input 2:</div>
    <pre>10 20</pre>
    <div>Sample Output 2:</div>
    <pre>30</pre>
    """
    spec2 = extract_problem_spec(multi_case_html)
    if len(spec2.sample_cases) < 2:
        failures.append(f"2.2 Multi-case extraction failed: count={len(spec2.sample_cases)}")
    else:
        print(f"  ✓ 2.2 Multiple sample test cases extracted: {len(spec2.sample_cases)} cases found.")

    # 2.3 Degraded inputs (None, empty, numbers)
    spec_none = extract_problem_spec(None)
    spec_num = extract_problem_spec(12345)
    if spec_none.title != "Unknown" or spec_num.title != "Unknown":
        failures.append("2.3 Degraded input failed")
    else:
        print("  ✓ 2.3 Non-string and None inputs handled safely without crashes.")

    # -------------------------------------------------------------
    # 3. Code Generator Empirical Verification
    # -------------------------------------------------------------
    print("\n--- [3] Code Generator Empirical Tests ---")

    # 3.1 Verify EVERY canonical solver executes and passes its test vector
    test_vectors = {
        "odd-or-even-sum": ("9 2", "odd"),
        "reverse-a-string": ("developer", "repoleved"),
        "sum-of-array": ("5 1 2 3 4 5", "15"),
        "palindrome-check": ("racecar", "yes"),
        "prime-numbers-count": ("2 10", "4")
    }

    for slug, (in_data, exp_out) in test_vectors.items():
        code = synthesize_solution(slug)
        # AST check
        try:
            ast.parse(code)
        except Exception as e:
            failures.append(f"3.1 AST validation failed for {slug}: {e}")
            continue

        # Execute in real sandbox
        val = validate_solution(code, in_data, exp_out)
        if not val.passed:
            failures.append(f"3.1 Execution failed for canonical solver {slug}: got '{val.stdout}', expected '{exp_out}', err='{val.error_message}'")
        else:
            print(f"  ✓ 3.1 Canonical solver '{slug}' generated, AST-parsed, and passed sandbox execution.")

    # 3.2 Verify algorithmic templates
    template_tests = [
        (ProblemSpecification(title="Find GCD and LCM of two numbers", description="greatest common divisor"), "12 18", "6 36"),
        (ProblemSpecification(title="Factorial calculation", description="factorial of n"), "5", "120"),
        (ProblemSpecification(title="Fibonacci numbers", description="fibonacci sequence"), "6", "1 1 2 3 5 8"),
        (ProblemSpecification(title="Count Vowels in string", description="vowel count"), "Antigravity", "4"),
        (ProblemSpecification(title="Sort Array elements", description="sort numbers in array"), "5 4 5 1 3 2", "1 2 3 4 5"),
        (ProblemSpecification(title="Remove Duplicates from array", description="remove duplicate"), "5 1 2 2 3 1", "1 2 3"),
        (ProblemSpecification(title="Maximum Subarray Sum", description="kadane algorithm largest contiguous sum"), "5 -2 1 -3 4 -1 2 1 -5 4", "7"),
    ]

    for spec, in_data, exp_out in template_tests:
        code = synthesize_solution(spec)
        ast.parse(code)
        val = validate_solution(code, in_data, exp_out)
        if not val.passed:
            failures.append(f"3.2 Template for '{spec.title}' failed: got '{val.stdout}', expected '{exp_out}'")
        else:
            print(f"  ✓ 3.2 Template '{spec.title}' verified: {in_data} -> {val.stdout}")

    # 3.3 Unknown problem fallback generates valid AST
    unknown_spec = ProblemSpecification(title="Quantum Chrono Warp Quantum Logic", description="unrecognized prompt")
    unknown_code = synthesize_solution(unknown_spec)
    try:
        ast.parse(unknown_code)
        val = validate_solution(unknown_code, "test-data", "test-data")
        if not val.passed:
            failures.append(f"3.3 Fallback echo failed: {val.error_message}")
        else:
            print("  ✓ 3.3 Fallback code for unrecognized problem parses AST and executes.")
    except Exception as e:
        failures.append(f"3.3 Fallback code failed AST: {e}")

    # -------------------------------------------------------------
    # 4. Ace Editor Adapter Verification
    # -------------------------------------------------------------
    print("\n--- [4] Ace Editor Adapter Tests ---")

    # 4.1 Mock page CDP injection sequence
    page_mock = MagicMock()
    page_mock.evaluate.return_value = "code_verified"
    success = inject_code(page_mock, "code_verified")
    if not success:
        failures.append("4.1 Ace adapter inject_code returned False")
    else:
        print("  ✓ 4.1 Ace adapter inject_code executed successfully with verify=True.")

    # 4.2 Adapter wait_for_editor with timeout handling
    page_mock_slow = MagicMock()
    page_mock_slow.wait_for_selector.side_effect = Exception("Timeout")
    page_mock_slow.query_selector.return_value = None
    ready = wait_for_editor(page_mock_slow, timeout=0.1)
    if ready:
        failures.append("4.2 wait_for_editor should return False on selector failure")
    else:
        print("  ✓ 4.2 wait_for_editor correctly returns False on element absence.")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    print("\n=== SUMMARY OF STRESS TEST RESULTS ===")
    if failures:
        print(f"FAILED: {len(failures)} checks failed:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("ALL 18 FORENSIC STRESS CHECKS PASSED EMPIRICALLY!")
        return True


if __name__ == "__main__":
    success = run_all_stress_tests()
    sys.exit(0 if success else 1)
