#!/usr/bin/env python3
"""
harness_4_float_normalization.py - Empirical Stress Harness for Float Tolerance and Output Normalization.

Adversarially tests:
1. CRLF (\r\n), CR (\r), and LF (\n) normalization
2. Trailing spaces and tabs per line
3. Outer leading/trailing empty lines
4. Float tolerances (3.141592 vs 3.1416, 1e-4 relative and absolute tolerance)
5. Mixed text + float token comparison
6. Case insensitivity for boolean/parity tokens (even/odd/yes/no/true/false)
7. Actual subprocess execution comparing computed floats vs rounded expected outputs
"""

import math
import sys

BASE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from solver.test_runner import normalize_output, outputs_match, validate_solution


def test_float_and_normalization():
    print("=" * 70)
    print("STARTING HARNESS 4: Float Tolerance & Output Normalization")
    print("=" * 70)

    # 1. Normalization unit tests
    norm_cases = [
        ("CRLF line endings", "hello\r\nworld\r\n", "hello\nworld"),
        ("CR line endings", "hello\rworld\r", "hello\nworld"),
        ("Mixed CRLF and LF", "line1\r\nline2\nline3\r\n", "line1\nline2\nline3"),
        ("Trailing spaces per line", "line1   \nline2  \t \nline3 ", "line1\nline2\nline3"),
        ("Outer blank lines", "\n\n\nhello\nworld\n\n\n", "hello\nworld"),
        ("Spaces with trailing newline", "  data  \n", "data"),
        ("Empty string", "", ""),
        ("Whitespace only string", "   \r\n\t  \n  ", ""),
    ]

    all_passed = True
    norm_results = []
    print("\n--- Testing normalize_output ---")
    for label, raw_input, expected in norm_cases:
        actual = normalize_output(raw_input)
        ok = (actual == expected)
        print(f"  {label:<30} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(f"    Expected: {expected!r}, Got: {actual!r}")
            all_passed = False
        norm_results.append((label, ok))

    # 2. outputs_match equivalence and float tolerance
    match_cases = [
        # Whitespace and formatting
        ("Exact match string", "abc", "abc", True),
        ("CRLF vs LF", "foo\r\nbar", "foo\nbar", True),
        ("Trailing spaces mismatch", "foo   \nbar ", "foo\nbar", True),
        ("Surrounding newlines mismatch", "\nfoo\nbar\n", "foo\nbar", True),

        # Case insensitive tokens
        ("Case-insensitive YES/yes", "YES", "yes", True),
        ("Case-insensitive No/no", "No", "no", True),
        ("Case-insensitive TRUE/true", "TRUE", "true", True),
        ("Case-insensitive FALSE/false", "FALSE", "false", True),
        ("Case-insensitive EVEN/even", "EVEN", "even", True),
        ("Case-insensitive Odd/odd", "Odd", "odd", True),
        ("Case-sensitive non-token mismatch", "HELLO", "hello", False),

        # Float tolerance
        ("Pi: 3.141592 vs 3.1416 (within 1e-4)", "3.141592", "3.1416", True),
        ("Small numbers: 0.00001 vs 0.00002 (abs_tol <= 1e-4)", "0.00001", "0.00002", True),
        ("Large numbers: 100.005 vs 100.0 (rel_tol <= 1e-4)", "100.005", "100.0", True),
        ("Float mismatch outside 1e-4", "100.1", "100.0", False),
        ("Different numbers", "1.0", "2.0", False),
        ("Scientific notation match", "1e-5", "0.00001", True),
        ("Scientific notation vs standard", "1.23e2", "123.0", True),
        ("Multiple floats in vector", "1.00001 2.00002 3.00003", "1.0 2.0 3.0", True),
        ("Mixed text and float", "Area = 3.141592 sq cm", "Area = 3.1416 sq cm", True),
        ("Mixed text mismatch", "Area = 3.141592 sq m", "Area = 3.1416 sq cm", False),
        ("Different token count", "1.0 2.0 3.0", "1.0 2.0", False),
        ("String vs number mismatch", "abc", "123", False),
    ]

    print("\n--- Testing outputs_match ---")
    match_results = []
    for label, act, exp, expected_match in match_cases:
        res = outputs_match(act, exp)
        ok = (res == expected_match)
        print(f"  {label:<45} -> {'PASS' if ok else 'FAIL'} (got: {res}, expected: {expected_match})")
        if not ok:
            all_passed = False
        match_results.append((label, ok))

    # 3. Subprocess execution with live float calculation
    print("\n--- Testing Live Subprocess with Float Calculation ---")
    calc_code = (
        "import sys, math\n"
        "r = float(sys.stdin.read().strip())\n"
        "area = math.pi * r * r\n"
        "print(area)\n"
    )
    # radius = 2.0 -> area = 4 * pi = 12.566370614359172
    # expected rounded to 4 decimals = 12.5664
    live_res = validate_solution(calc_code, "2.0", "12.5664", timeout_sec=2.0)
    print(f"  Live Float calculation: radius 2.0 -> actual: {live_res.stdout}, expected: '12.5664'")
    print(f"  Live result passed: {live_res.passed}")
    live_ok = live_res.passed and live_res.exit_code == 0
    if not live_ok:
        all_passed = False
        print(f"  [FAIL] Live float comparison failed: {live_res.error_message}")
    else:
        print("  [PASS] Live float calculation matches expected within tolerance.")

    print("\n" + "=" * 70)
    print("HARNESS 4 SUMMARY:")
    total = len(norm_results) + len(match_results) + 1
    passed = sum(1 for _, ok in norm_results if ok) + sum(1 for _, ok in match_results if ok) + (1 if live_ok else 0)
    print(f"Total Tests: {total}, Passed: {passed}, Failed: {total - passed}")
    print(f"OVERALL HARNESS 4: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = test_float_and_normalization()
    sys.exit(0 if success else 1)
