#!/usr/bin/env python3
"""
harness_1_timeout_zombies.py - Empirical Stress Harness for Subprocess Timeout and Zombie Leakage.

Adversarially tests:
1. Infinite CPU loop (`while True: pass`)
2. Infinite sleep loop (`while True: time.sleep(0.05)`)
3. Infinite stdout flood (`while True: sys.stdout.write('A'*4096)`)
4. Deep recursive calls in infinite loop (`def r(n): ...`)
5. Unbounded recursion hitting RecursionError (runtime exception vs timeout)
6. Subprocess spawn attempt with sleep child
7. Multi-case timeout isolation
8. Process table inspection for zombie / defunct processes
"""

import os
import subprocess
import sys
import time

BASE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from solver.test_runner import validate_solution, test_solution, SubprocessSandbox


def check_zombies():
    """Checks if any defunct / zombie processes exist in process table."""
    try:
        res = subprocess.run(
            ["ps", "-eo", "pid,state,command"],
            capture_output=True,
            text=True,
            check=True
        )
        zombies = [line for line in res.stdout.strip().split("\n") if " Z " in line or "defunct" in line]
        return zombies
    except Exception as e:
        print(f"Error checking zombies: {e}")
        return []


def run_tests():
    print("=" * 70)
    print("STARTING HARNESS 1: Subprocess Timeout & Zombie Process Leakage")
    print("=" * 70)

    initial_zombies = check_zombies()
    print(f"Initial zombie processes count: {len(initial_zombies)}")

    timeout_cases = [
        (
            "Infinite CPU loop (while True: pass)",
            "while True:\n    pass\n",
            "dummy_in",
            "dummy_out",
            0.2
        ),
        (
            "Infinite sleep loop",
            "import time\nwhile True:\n    time.sleep(0.05)\n",
            "input_val",
            "expected_val",
            0.2
        ),
        (
            "Infinite stdout flood",
            "import sys\nwhile True:\n    sys.stdout.write('A' * 4096)\n    sys.stdout.flush()\n",
            "test_in",
            "test_out",
            0.3
        ),
        (
            "Deep recursive calls in infinite loop",
            "def loop():\n    while True:\n        def r(n):\n            if n > 0:\n                r(n - 1)\n        r(500)\nloop()\n",
            "in",
            "out",
            0.2
        ),
        (
            "Process spawn attempt with sleep child",
            "import subprocess, sys\nsubprocess.Popen([sys.executable, '-c', 'import time; time.sleep(0.5)'])\nwhile True: pass\n",
            "in",
            "out",
            0.2
        ),
    ]

    all_passed = True
    results = []

    for name, code, in_data, exp_data, timeout in timeout_cases:
        print(f"\n[TEST] {name} (timeout={timeout}s)")
        t0 = time.time()
        val_res = validate_solution(code, in_data, exp_data, timeout_sec=timeout)
        duration = time.time() - t0

        print(f"  Duration elapsed: {duration:.4f}s (budget: {timeout}s)")
        print(f"  Result passed: {val_res.passed}")
        print(f"  Exit code: {val_res.exit_code}")
        print(f"  Stderr: {val_res.stderr!r}")
        print(f"  Error message: {val_res.error_message}")

        passed_test = True
        if val_res.passed is not False:
            print(f"  [FAIL] Expected passed=False, got {val_res.passed}")
            passed_test = False
        if val_res.exit_code != -1:
            print(f"  [FAIL] Expected exit_code=-1, got {val_res.exit_code}")
            passed_test = False
        if "timed out" not in (val_res.error_message or "").lower():
            print(f"  [FAIL] Expected error_message containing 'timed out', got {val_res.error_message}")
            passed_test = False
        if val_res.stderr != "TimeoutExpired":
            print(f"  [FAIL] Expected stderr='TimeoutExpired', got {val_res.stderr}")
            passed_test = False
        if duration > timeout + 1.5:
            print(f"  [FAIL] Subprocess took too long to terminate: {duration:.2f}s > {timeout + 1.5}s")
            passed_test = False

        if passed_test:
            print("  [PASS] Clean timeout and termination verified.")
        else:
            all_passed = False
        results.append((name, passed_test))

    # Test unbounded recursion hitting RecursionError (runtime exception, not timeout)
    print("\n[TEST] Unbounded recursion hitting RecursionError (runtime failure)")
    rec_code = "def f(): f()\nf()\n"
    rec_res = validate_solution(rec_code, "in", "out", timeout_sec=2.0)
    print(f"  RecursionError exit_code: {rec_res.exit_code} (expected != 0)")
    print(f"  RecursionError in stderr: {'RecursionError' in rec_res.stderr}")
    rec_ok = (not rec_res.passed) and (rec_res.exit_code != 0) and ("RecursionError" in rec_res.stderr)
    if rec_ok:
        print("  [PASS] Runtime exception captured cleanly.")
    else:
        print("  [FAIL] Runtime exception failed to capture properly.")
        all_passed = False
    results.append(("Unbounded recursion exception handling", rec_ok))

    # Test multi-case test_solution with mixed normal and timeout cases
    print("\n[TEST] Multi-case test_solution with mixed normal and timeout cases")
    multi_cases = [
        {"input": "1 2", "expected": "3"},
        {"input": "while", "expected": "timeout_expected"},
        {"input": "5 5", "expected": "10"}
    ]
    mixed_code = (
        "import sys, time\n"
        "s = sys.stdin.read().strip()\n"
        "if s == 'while':\n"
        "    while True: time.sleep(0.1)\n"
        "else:\n"
        "    parts = [int(x) for x in s.split()]\n"
        "    print(sum(parts))\n"
    )
    val_multi = test_solution(mixed_code, multi_cases, timeout=0.2)
    print(f"  Multi-case all_passed: {val_multi.all_passed} (expected: False)")
    print(f"  Passed count: {val_multi.passed_count}/{val_multi.total_count} (expected: 2/3)")
    print(f"  Results exit codes: {[r.exit_code for r in val_multi.results]}")

    multi_ok = (not val_multi.all_passed) and (val_multi.passed_count == 2) and (val_multi.results[1].exit_code == -1)
    if multi_ok:
        print("  [PASS] Multi-case timeout isolation verified.")
    else:
        print("  [FAIL] Multi-case timeout isolation failed.")
        all_passed = False
    results.append(("Multi-case timeout isolation", multi_ok))

    # Post-check zombies
    time.sleep(0.5)
    final_zombies = check_zombies()
    print(f"\nFinal zombie processes count: {len(final_zombies)}")
    if len(final_zombies) > len(initial_zombies):
        print(f"  [FAIL] New zombie processes detected: {final_zombies}")
        all_passed = False
        results.append(("Zombie process leakage", False))
    else:
        print("  [PASS] Zero zombie process leakage confirmed.")
        results.append(("Zombie process leakage", True))

    print("\n" + "=" * 70)
    print("HARNESS 1 SUMMARY:")
    for name, status in results:
        print(f"  {'PASS' if status else 'FAIL'}: {name}")
    print(f"OVERALL HARNESS 1: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
