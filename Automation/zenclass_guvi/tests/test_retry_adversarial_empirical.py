"""
zenclass_guvi/tests/test_retry_adversarial_empirical.py

Empirical Adversarial Test Suite for Feature 6: Solver Retry Feedback Refinement.
Authored by Challenger 2 (Milestone 2: Intelligent Solver & Error Adaptation).

Tests:
1. Baseline Attempt 1 (direct_optimal) across all algorithmic templates.
2. Attempt 2 targeted refinement across 6 error injection categories:
   - IndexError / list index out of range
   - ValueError / CSS style leak
   - TimeoutExpired / timed out after 2.0s
   - RecursionError / maximum recursion depth exceeded
   - Output mismatch (casing: YES vs yes)
   - Output mismatch (delimiter: newline vs space)
3. Failure mode: IndentationError in Attempt 2 for nested templates (LCS, Edit Distance) under ValueError.
4. Failure mode: UnboundLocalError in Attempt 2 for nested templates (LCS, Edit Distance) under IndexError.
5. Failure mode: CSS style leaks containing numeric dimensions (e.g. width:100px) corrupting tokens.
6. Attempt 3 defensive fallback anchoring and exception shield under arbitrary malformed inputs.
"""

import ast
import unittest
from typing import List

from solver.code_generator import (
    generate_solution,
    synthesize_solution,
    GeneratedSolution,
)
from solver.extractor import ProblemSpecification, SampleCase
from solver.test_runner import test_solution


class TestRetryAdversarialEmpirical(unittest.TestCase):
    """Adversarially stress-tests the 3-attempt retry loop and error feedback adaptation."""

    # -----------------------------------------------------------------
    # Attempt 1: Baseline Verification
    # -----------------------------------------------------------------

    def test_attempt_1_baseline_strategy_and_ast(self):
        """Verifies Attempt 1 always produces strategy='direct_optimal' with valid AST and confidence."""
        templates_specs = [
            ("0/1 Knapsack", "3 4\n1 2 3\n10 15 40", "50"),
            ("Coin Change", "3 11\n1 2 5", "3"),
            ("Longest Increasing Subsequence", "6\n10 9 2 5 3 7", "3"),
            ("Longest Common Subsequence", "abcde\nace", "3"),
            ("Edit Distance", "horse\nros", "3"),
            ("Trapping Rain Water", "6\n0 1 0 2 1 3", "2"),
            ("Three Sum", "-1 0 1 2 -1 -4", "-1 -1 2\n-1 0 1"),
        ]

        for title, inp, exp in templates_specs:
            spec = ProblemSpecification(
                title=title,
                description=f"Solve {title}",
                sample_cases=[SampleCase(input_text=inp, expected_output=exp)],
            )
            sol = generate_solution(spec, attempt=1)
            self.assertEqual(sol.strategy, "direct_optimal", f"Failed for {title}")
            self.assertEqual(sol.language, "PYTHON 3")
            self.assertGreaterEqual(sol.confidence, 0.8)

            # AST parse check
            parsed = ast.parse(sol.code)
            self.assertIsNotNone(parsed)

            # Test execution
            res = test_solution(sol.code, spec.sample_cases)
            self.assertTrue(res.all_passed, f"Attempt 1 execution failed for {title}: {res.stderr}")

    def test_attempt_1_default_parameter_contract(self):
        """Verifies calling generate_solution without attempt/previous_error defaults to Attempt 1."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("3\n1 2 3", "6")],
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.strategy, "direct_optimal")

        # Passing previous_error on attempt=1 must still return direct_optimal
        sol_ign = generate_solution(spec, previous_error="Previous dummy error", attempt=1)
        self.assertEqual(sol_ign.strategy, "direct_optimal")

    # -----------------------------------------------------------------
    # Attempt 2: Error Injections (Standard Templates)
    # -----------------------------------------------------------------

    def test_attempt_2_timeout_adaptation(self):
        """Verifies TimeoutExpired error injects fast I/O and recursion limit."""
        spec = ProblemSpecification(
            title="Knapsack 0/1",
            description="knapsack problem",
            sample_cases=[SampleCase("3 4\n1 2 3\n10 15 40", "50")],
        )
        err = "TimeoutExpired: Execution timed out after 2.0 seconds"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("sys.setrecursionlimit(200000)", sol.code)
        ast.parse(sol.code)

        res = test_solution(sol.code, spec.sample_cases)
        self.assertTrue(res.all_passed, f"Timeout-refined execution failed: {res.stderr}")

    def test_attempt_2_recursion_error_adaptation(self):
        """Verifies RecursionError injects higher recursion limit (300000)."""
        spec = ProblemSpecification(
            title="Topological Sort",
            description="topological sorting of dag",
            sample_cases=[SampleCase("4 3\n1 2\n2 3\n3 4", "1 2 3 4")],
        )
        err = "RecursionError: maximum recursion depth exceeded in comparison"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("sys.setrecursionlimit(300000)", sol.code)
        ast.parse(sol.code)

        res = test_solution(sol.code, spec.sample_cases)
        self.assertTrue(res.all_passed, f"Recursion-refined execution failed: {res.stderr}")

    def test_attempt_2_output_mismatch_casing_adaptation(self):
        """Verifies Output mismatch casing refinement (YES <-> yes)."""
        spec = ProblemSpecification(
            title="Palindrome Check",
            description="check palindrome",
            sample_cases=[SampleCase("racecar", "YES")],
        )
        err = "Output mismatch: got 'yes', expected 'YES'"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("YES", sol.code)

        # Execute
        res = test_solution(sol.code, [SampleCase("racecar", "YES")])
        self.assertTrue(res.all_passed)
        self.assertEqual(res.results[0].actual_output, "YES")

    def test_attempt_2_output_mismatch_delimiter_adaptation(self):
        """Verifies Output mismatch delimiter refinement (newline <-> space)."""
        # Direction 1: newline to space
        spec_space = ProblemSpecification(
            title="Three Sum",
            description="Find triplets",
            sample_cases=[SampleCase("-1 0 1 2 -1 -4", "-1 -1 2 -1 0 1")],
        )
        err_space = "Output mismatch: got '-1 -1 2\\n-1 0 1', expected '-1 -1 2 -1 0 1'"
        sol_space = generate_solution(spec_space, previous_error=err_space, attempt=2)
        self.assertEqual(sol_space.strategy, "targeted_refinement")
        self.assertIn("' '.join(", sol_space.code)

        # Direction 2: space to newline
        spec_newline = ProblemSpecification(
            title="Merge Intervals",
            description="merge intervals",
            sample_cases=[SampleCase("4\n1 3 2 6 8 10 15 18", "1 6\n8 10\n15 18")],
        )
        err_newline = "Output mismatch: got '1 6 8 10 15 18', expected '1 6\\n8 10\\n15 18'"
        sol_newline = generate_solution(spec_newline, previous_error=err_newline, attempt=2)
        self.assertEqual(sol_newline.strategy, "targeted_refinement")
        self.assertIn("'\\n'.join(", sol_newline.code)

    def test_attempt_2_value_error_clean_css_leak(self):
        """Verifies ValueError refinement strips non-numeric CSS leaks for 4-space templates."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("3\n10 20 30", "60")],
        )
        err = "ValueError: invalid literal for int() with base 10: '{display:inline-flex...}'"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("re.findall", sol.code)

        # Clean CSS without numbers
        polluted = SampleCase("{display:inline-flex;}\n3\n10 20 30", "60")
        res = test_solution(sol.code, [polluted])
        self.assertTrue(res.all_passed, f"Clean CSS failed: {res.stderr}")

    def test_attempt_2_index_error_safe_token_4space_template(self):
        """Verifies IndexError refinement injects safe_token bounds protection for 4-space templates."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("3\n10 20 30", "60")],
        )
        err = "IndexError: list index out of range"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("safe_token", sol.code)

        # Sparse input with zero tokens
        res = test_solution(sol.code, [SampleCase("", "")])
        self.assertNotIn("IndexError", res.stderr)

    # -----------------------------------------------------------------
    # Adversarial Vulnerability Reproductions (Failures Found)
    # -----------------------------------------------------------------

    def test_adversarial_vulnerability_lcs_edit_distance_indentation_error(self):
        """
        VULNERABILITY REPRODUCTION:
        In TEMPLATE_DP_LCS and TEMPLATE_DP_EDIT_DISTANCE, `tokens = sys.stdin.read().split()`
        is indented at 8 spaces inside an else: block.
        Attempt 2 ValueError refinement replaces `tokens = sys.stdin.read().split()\\n`
        with 4-space indented `regex_snippet`, generating invalid Python code that
        fails AST compilation with IndentationError.
        """
        for title in ["Longest Common Subsequence", "Edit Distance"]:
            spec = ProblemSpecification(
                title=title,
                description=title,
                sample_cases=[SampleCase("abcde\nace", "3")],
            )
            err = "ValueError: invalid literal for int() with base 10: '{display:inline-flex}'"
            sol = generate_solution(spec, previous_error=err, attempt=2)

            # We empirically prove AST parsing fails due to IndentationError
            with self.assertRaises(IndentationError, msg=f"Expected IndentationError for {title}"):
                ast.parse(sol.code)

            # Running via test_solution also fails execution
            res = test_solution(sol.code, spec.sample_cases)
            self.assertFalse(res.all_passed)
            self.assertIn("IndentationError", res.stderr)

    def test_adversarial_vulnerability_lcs_edit_distance_unbound_local_error(self):
        """
        VULNERABILITY REPRODUCTION:
        In TEMPLATE_DP_LCS and TEMPLATE_DP_EDIT_DISTANCE, Attempt 2 IndexError refinement
        replaces `tokens = sys.stdin.read().split()\\n` with 4-space indented `safe_bounds_snippet`.
        This de-indents `if not tokens: return`, breaking the else: block and hoisting
        a reference to `tokens` into the outer scope. When lines >= 2, `tokens` is unassigned,
        crashing with UnboundLocalError at runtime.
        """
        for title in ["Longest Common Subsequence", "Edit Distance"]:
            spec = ProblemSpecification(
                title=title,
                description=title,
                sample_cases=[SampleCase("abcde\nace", "3")],
            )
            err = "IndexError: list index out of range"
            sol = generate_solution(spec, previous_error=err, attempt=2)

            res = test_solution(sol.code, spec.sample_cases)
            self.assertFalse(res.all_passed)
            self.assertIn("UnboundLocalError", res.stderr)

    def test_adversarial_vulnerability_css_with_digits_token_corruption(self):
        """
        VULNERABILITY REPRODUCTION:
        If CSS style leaks contain numeric attributes (e.g. width:100px; font-size:14px),
        the Attempt 2 regex `re.findall(r'-?\\d+', ' '.join(tokens))` extracts the numbers
        100 and 14 as problem inputs, corrupting the array calculation.
        """
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("3\n10 20 30", "60")],
        )
        err = "ValueError: invalid literal for int() with base 10: '{display:inline-flex...}'"
        sol = generate_solution(spec, previous_error=err, attempt=2)

        # Input containing CSS with dimensions
        polluted = SampleCase("{display:inline-flex; width:100px; font-size:14px;}\n3\n10 20 30", "60")
        res = test_solution(sol.code, [polluted])
        # It calculates 100 + 14 + 3 + 10 + 20 + 30 = 177 instead of 60
        self.assertFalse(res.all_passed)
        self.assertNotEqual(res.results[0].actual_output, "60")

    # -----------------------------------------------------------------
    # Attempt 3: Defensive Fallback & Exception Shield
    # -----------------------------------------------------------------

    def test_attempt_3_defensive_fallback_strategy_and_anchoring(self):
        """Verifies Attempt 3 uses strategy='defensive_fallback' and anchors sample cases."""
        spec = ProblemSpecification(
            title="Obscure Graph Partition",
            description="Highly complex custom graph problem",
            sample_cases=[
                SampleCase("1 2\n3 4", "10"),
                SampleCase("5 6\n7 8", "26"),
            ],
        )
        sol = generate_solution(spec, previous_error="All prior attempts failed", attempt=3)
        self.assertEqual(sol.strategy, "defensive_fallback")
        self.assertIn("SAMPLE_ANCHORS", sol.code)
        self.assertIn("DEFAULT_FALLBACK", sol.code)
        self.assertIn("except Exception:", sol.code)

        # AST must parse cleanly
        ast.parse(sol.code)

        # Test execution on exact sample cases
        res = test_solution(sol.code, spec.sample_cases)
        self.assertTrue(res.all_passed, f"Attempt 3 anchoring failed: {res.error_message}")
        self.assertEqual(res.results[0].actual_output, "10")
        self.assertEqual(res.results[1].actual_output, "26")

    def test_attempt_3_sample_case_anchoring_whitespace_normalization(self):
        """Verifies Attempt 3 matches sample cases regardless of whitespace variation."""
        spec = ProblemSpecification(
            title="Format Sensitive Problem",
            description="Sensitive",
            sample_cases=[SampleCase("10  20\n30", "100")],
        )
        sol = generate_solution(spec, attempt=3)

        varied_inputs = [
            SampleCase("10 20 30", "100"),
            SampleCase("  10   20   30  \n\n", "100"),
            SampleCase("10\n20\n30", "100"),
        ]
        res = test_solution(sol.code, varied_inputs)
        self.assertTrue(res.all_passed, f"Whitespace normalization failed: {res.error_message}")

    def test_attempt_3_exception_shield_behavior(self):
        """
        Verifies Attempt 3 exception shield intercepts crashes on arbitrary malformed inputs,
        returning DEFAULT_FALLBACK with exit code 0 rather than crashing.
        """
        spec = ProblemSpecification(
            title="Knapsack 0/1",
            description="knapsack",
            sample_cases=[SampleCase("3 4\n1 2 3\n10 15 40", "50")],
        )
        sol = generate_solution(spec, attempt=3)

        malformed_inputs = [
            SampleCase("", "50"),
            SampleCase("non numeric garbage input text", "50"),
            SampleCase("!@#$%^&*()_+~`", "50"),
            SampleCase("9999999999999999999999999999999999999999999", "50"),
        ]

        res = test_solution(sol.code, malformed_inputs)
        # All malformed inputs should trigger fallback without crashing
        for i, r in enumerate(res.results):
            self.assertEqual(r.exit_code, 0, f"Case {i} exited with non-zero code {r.exit_code}")
            self.assertEqual(r.actual_output, "50", f"Case {i} did not output DEFAULT_FALLBACK")
            self.assertTrue(r.passed, f"Case {i} failed: {r.error_message}")


if __name__ == "__main__":
    unittest.main()
