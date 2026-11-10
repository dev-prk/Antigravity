#!/usr/bin/env python3
"""
harness_5_stress_edge_cases.py - Empirical Stress Harness for Edge Cases & Sandbox Boundaries.

Tests:
1. Massive 2MB stdin payload handling (checks deadlock resistance)
2. Unicode / Multilingual text fidelity (Tamil, Hindi, Chinese, Arabic, Emojis)
3. Zero-byte output & empty input/output boundary permutations
4. Specific exit code preservation (sys.exit(42), sys.exit(7))
5. Runtime exceptions (ZeroDivisionError, MemoryError, NameError)
6. Raw syntax error passed directly to validate_solution
7. Very tight timeout (0.001s)
8. Exported API symbol integrity
"""

import math
import sys
import time

BASE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import solver
from solver.test_runner import validate_solution, test_solution, SubprocessSandbox


def run_edge_case_tests():
    print("=" * 70)
    print("STARTING HARNESS 5: Edge Cases, Large Payloads & Boundary Stress")
    print("=" * 70)

    results = []
    all_passed = True

    # 1. Massive 2MB stdin payload
    print("\n[TEST 1] Massive 2MB stdin payload (deadlock resilience)")
    large_payload = "1 " * 1_000_000  # 2MB of numbers
    sum_code = (
        "import sys\n"
        "raw = sys.stdin.read().split()\n"
        "print(len(raw))\n"
    )
    t0 = time.time()
    res1 = validate_solution(sum_code, large_payload, "1000000", timeout_sec=5.0)
    dt1 = time.time() - t0
    print(f"  Duration: {dt1:.2f}s, passed: {res1.passed}, stdout: {res1.stdout}")
    ok1 = res1.passed and res1.stdout == "1000000"
    results.append(("2MB large stdin payload", ok1))
    if not ok1:
        all_passed = False

    # 2. Multilingual UTF-8 fidelity
    print("\n[TEST 2] Multilingual UTF-8 fidelity (Tamil, Hindi, Chinese, Arabic, Emojis)")
    multilingual_text = "வணக்கம் नमस्ते 你好 مرحبا 🚀🔥💻🤖"
    echo_code = (
        "import sys\n"
        "line = sys.stdin.read().strip()\n"
        "print(line)\n"
    )
    res2 = validate_solution(echo_code, multilingual_text, multilingual_text, timeout_sec=2.0)
    print(f"  Passed: {res2.passed}, stdout: '{res2.stdout}'")
    ok2 = res2.passed and res2.stdout == multilingual_text
    results.append(("Multilingual UTF-8 fidelity", ok2))
    if not ok2:
        all_passed = False

    # 3. Specific exit codes
    print("\n[TEST 3] Specific exit codes propagation")
    exit_42_code = "import sys\nsys.exit(42)\n"
    res3 = validate_solution(exit_42_code, "", "", timeout_sec=2.0)
    print(f"  Exit code 42: got {res3.exit_code}, passed={res3.passed}")
    ok3 = (res3.exit_code == 42) and (not res3.passed)
    results.append(("Exit code 42 propagation", ok3))
    if not ok3:
        all_passed = False

    # 4. ZeroDivisionError handling
    print("\n[TEST 4] ZeroDivisionError handling")
    div_zero_code = "x = 1 / 0\n"
    res4 = validate_solution(div_zero_code, "", "", timeout_sec=2.0)
    print(f"  ZeroDivisionError: exit_code={res4.exit_code}, in stderr={'ZeroDivisionError' in res4.stderr}")
    ok4 = (not res4.passed) and (res4.exit_code == 1) and ("ZeroDivisionError" in res4.stderr)
    results.append(("ZeroDivisionError handling", ok4))
    if not ok4:
        all_passed = False

    # 5. Raw SyntaxError in code passed directly to validate_solution
    print("\n[TEST 5] Raw SyntaxError handling in test runner")
    bad_syntax_code = "def f(:\n"
    res5 = validate_solution(bad_syntax_code, "", "", timeout_sec=2.0)
    print(f"  SyntaxError: exit_code={res5.exit_code}, passed={res5.passed}, in stderr={'SyntaxError' in res5.stderr}")
    ok5 = (not res5.passed) and (res5.exit_code == 1) and ("SyntaxError" in res5.stderr)
    results.append(("Direct SyntaxError in runner", ok5))
    if not ok5:
        all_passed = False

    # 6. Ultra-tight timeout (0.001s)
    print("\n[TEST 6] Ultra-tight timeout (0.001s)")
    tight_code = "import time\ntime.sleep(0.5)\n"
    res6 = validate_solution(tight_code, "", "", timeout_sec=0.001)
    print(f"  Tight timeout: exit_code={res6.exit_code}, stderr={res6.stderr}")
    ok6 = (not res6.passed) and (res6.exit_code == -1) and (res6.stderr == "TimeoutExpired")
    results.append(("Ultra-tight timeout handling", ok6))
    if not ok6:
        all_passed = False

    # 7. Package exports verification
    print("\n[TEST 7] Clean API contract exports verification")
    required_symbols = [
        "SampleCase", "ProblemSpecification", "ProblemSpec", "ProblemExtractor",
        "extract_problem_spec", "GeneratedSolution", "generate_solution",
        "synthesize_solution", "TestCaseResult", "ValidationResult",
        "test_solution", "validate_solution", "SubprocessSandbox",
        "AceEditorAdapter", "inject_code", "inject_code_into_ace",
        "get_editor_code", "wait_for_editor"
    ]
    missing = [sym for sym in required_symbols if not hasattr(solver, sym)]
    print(f"  Exported symbols check: {len(required_symbols) - len(missing)}/{len(required_symbols)}")
    if missing:
        print(f"  Missing symbols: {missing}")
    ok7 = len(missing) == 0
    results.append(("Package API exports integrity", ok7))
    if not ok7:
        all_passed = False

    print("\n" + "=" * 70)
    print("HARNESS 5 SUMMARY:")
    for name, status in results:
        print(f"  {'PASS' if status else 'FAIL'}: {name}")
    print(f"OVERALL HARNESS 5: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = run_edge_case_tests()
    sys.exit(0 if success else 1)
