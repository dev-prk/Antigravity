#!/usr/bin/env python3
"""
harness_3_canonical_accuracy.py - Empirical Accuracy Harness for Canonical Problems.

Tests the 5 canonical problems:
1. odd-or-even-sum
2. reverse-a-string
3. sum-of-array
4. palindrome-check
5. prime-numbers-count

For each problem:
- Synthesizes code via synthesize_solution (using both slug and rich ProblemSpecification)
- Runs all canonical test vectors via validate_solution
- Tests multi-case batch testing via test_solution
- Asserts 100% pass rate across all vectors
"""

import sys

BASE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from solver.extractor import ProblemSpecification, SampleCase
from solver.code_generator import synthesize_solution, generate_solution
from solver.test_runner import validate_solution, test_solution, SubprocessSandbox


CANONICAL_TEST_SUITE = {
    "odd-or-even-sum": {
        "title": "Odd or Even Sum",
        "description": "Given two numbers N and M, add them and state whether the sum is even or odd.",
        "input_desc": "Two integers N and M separated by space.",
        "output_desc": "Print 'even' or 'odd'.",
        "vectors": [
            ("9 2", "odd"),
            ("10 20", "even"),
            ("0 0", "even"),
            ("-5 5", "even"),
            ("-3 4", "odd"),
            ("1000000000 1000000001", "odd"),
            ("   1   3   ", "even"),
            ("7\n8\n", "odd"),
            ("-2 -4", "even"),
        ]
    },
    "reverse-a-string": {
        "title": "Reverse a String",
        "description": "Given a string S, print its reverse.",
        "input_desc": "A single line containing string S.",
        "output_desc": "Reversed string.",
        "vectors": [
            ("hello", "olleh"),
            ("guvi", "ivug"),
            ("a", "a"),
            ("12345", "54321"),
            ("racecar", "racecar"),
            ("Hello World!", "!dlroW olleH"),
            ("abc def", "fed cba"),
        ]
    },
    "sum-of-array": {
        "title": "Sum of Array Elements",
        "description": "Given N elements, compute their total sum.",
        "input_desc": "First line: N. Second line: N space-separated integers.",
        "output_desc": "Total sum as a single integer.",
        "vectors": [
            ("5\n1 2 3 4 5", "15"),
            ("3\n10 -10 0", "0"),
            ("1\n42", "42"),
            ("4\n-1 -2 -3 -4", "-10"),
            ("3 10 20 30", "60"),
            ("2\n100 200", "300"),
            ("6\n0 0 0 0 0 0", "0"),
        ]
    },
    "palindrome-check": {
        "title": "Palindrome Checker",
        "description": "Determine if the given string is a palindrome.",
        "input_desc": "Single string S.",
        "output_desc": "Print 'yes' if palindrome, 'no' otherwise.",
        "vectors": [
            ("racecar", "yes"),
            ("madam", "yes"),
            ("automation", "no"),
            ("a", "yes"),
            ("noon", "yes"),
            ("python", "no"),
            ("12321", "yes"),
            ("12345", "no"),
        ]
    },
    "prime-numbers-count": {
        "title": "Prime Numbers Count",
        "description": "Given two numbers L and R, count the prime numbers between L and R inclusive. Or given a single number test if prime.",
        "input_desc": "Two space separated integers L and R, or single integer N.",
        "output_desc": "Count of primes, or yes/no for single integer.",
        "vectors": [
            ("2 10", "4"),
            ("1 10", "4"),
            ("10 20", "4"),
            ("20 30", "2"),
            ("1 1", "0"),
            ("0 1", "0"),
            ("2 2", "1"),
            ("2", "yes"),
            ("3", "yes"),
            ("4", "no"),
            ("17", "yes"),
            ("1", "no"),
            ("0", "no"),
        ]
    }
}


def run_canonical_accuracy_tests():
    print("=" * 70)
    print("STARTING HARNESS 3: Execution Accuracy on Canonical Problems")
    print("=" * 70)

    total_vectors = 0
    passed_vectors = 0
    all_passed = True

    for slug, prob in CANONICAL_TEST_SUITE.items():
        print(f"\n--- Testing Problem: {slug} ('{prob['title']}') ---")

        # Synthesize code via both slug string and rich ProblemSpecification
        code_by_slug = synthesize_solution(slug)
        spec = ProblemSpecification(
            title=prob["title"],
            description=prob["description"],
            input_spec=prob["input_desc"],
            output_spec=prob["output_desc"],
            _slug=slug
        )
        code_by_spec = synthesize_solution(spec)

        print(f"  Code synthesized by slug: {len(code_by_slug)} bytes")
        print(f"  Code synthesized by spec: {len(code_by_spec)} bytes")

        # Test each vector with code_by_slug
        for inp, exp in prob["vectors"]:
            total_vectors += 1
            disp_inp = inp.replace('\n', '\\n')
            res = validate_solution(code_by_slug, inp, exp, timeout_sec=2.0)
            if res.passed:
                passed_vectors += 1
                print(f"  [PASS] In: '{disp_inp}' -> Out: '{res.stdout}' (Expected: '{exp}')")
            else:
                all_passed = False
                print(f"  [FAIL] In: '{disp_inp}' -> Out: '{res.stdout}', Expected: '{exp}', Err: '{res.error_message}'")

        # Test multi-case batch testing via test_solution with code_by_spec
        batch_cases = [{"input": inp, "expected": exp} for inp, exp in prob["vectors"]]
        batch_res = test_solution(code_by_spec, batch_cases, timeout=2.0)
        print(f"  Batch test_solution result: {batch_res.passed_count}/{batch_res.total_count} passed (all_passed={batch_res.all_passed})")
        if not batch_res.all_passed:
            all_passed = False
            print(f"  [FAIL] Batch execution failed for {slug}")

        # Also test via SubprocessSandbox class
        sandbox_res = SubprocessSandbox.validate_solution(code_by_slug, prob["vectors"][0][0], prob["vectors"][0][1])
        if not sandbox_res.passed:
            all_passed = False
            print(f"  [FAIL] SubprocessSandbox contract check failed for {slug}")

    print("\n" + "=" * 70)
    print("HARNESS 3 SUMMARY:")
    print(f"Total Test Vectors: {total_vectors}")
    print(f"Passed Test Vectors: {passed_vectors}")
    print(f"Success Rate: {(passed_vectors / total_vectors * 100):.2f}%")
    print(f"OVERALL HARNESS 3: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = run_canonical_accuracy_tests()
    sys.exit(0 if success else 1)
