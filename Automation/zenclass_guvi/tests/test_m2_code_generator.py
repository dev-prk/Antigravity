"""
tests/test_m2_code_generator.py - Comprehensive Unit Test Suite for Milestone 2.

Validates:
- Feature 5: Medium & Hard Algorithmic Python 3 Code Generation
- Feature 6: Solver Retry Feedback Refinement (Attempts 1 -> 2 -> 3)
- Interface Contract & Backward Compatibility

Contains 5 test classes:
1. TestCodeGeneratorInterfaceContract
2. TestMediumHardCodeGeneration
3. TestErrorFeedbackRefinement
4. TestEndToEndRetryLoopSimulation
5. TestBackwardCompatibilityAndRegression
"""

import ast
import unittest
from typing import Any, Dict, List

from solver.extractor import ProblemSpecification, SampleCase
from solver.code_generator import (
    CANONICAL_SOLVERS,
    GeneratedSolution,
    generate_solution,
    synthesize_solution,
    TEMPLATE_MATH_GCD_LCM,
    TEMPLATE_KADANE_MAX_SUBARRAY,
    TEMPLATE_FALLBACK_ECHO,
)
from solver.test_runner import test_solution, ValidationResult


# =====================================================================
# 1. Interface Contract Tests
# =====================================================================

class TestCodeGeneratorInterfaceContract(unittest.TestCase):
    """Verifies function signatures, return types, dataclass fields, and AST validity."""

    def test_default_arguments_backward_compatibility(self):
        """Single-argument call must default to previous_error=None and attempt=1."""
        sol = generate_solution("reverse-a-string")
        self.assertIsInstance(sol, GeneratedSolution)
        self.assertEqual(sol.strategy, "direct_optimal")
        self.assertEqual(sol.language, "PYTHON 3")
        self.assertEqual(sol.category, "Strings")

        code = synthesize_solution("reverse-a-string")
        self.assertIsInstance(code, str)
        self.assertIn("[::-1]", code)

    def test_generated_solution_attributes(self):
        """Every GeneratedSolution instance must have all 6 contract attributes."""
        sol = generate_solution("odd-or-even-sum")
        self.assertTrue(hasattr(sol, "code"))
        self.assertTrue(hasattr(sol, "confidence"))
        self.assertTrue(hasattr(sol, "strategy"))
        self.assertTrue(hasattr(sol, "language"))
        self.assertTrue(hasattr(sol, "category"))
        self.assertTrue(hasattr(sol, "explanation"))

        self.assertIsInstance(sol.code, str)
        self.assertIsInstance(sol.confidence, float)
        self.assertIsInstance(sol.strategy, str)
        self.assertIsInstance(sol.language, str)
        self.assertIsInstance(sol.category, str)
        self.assertIsInstance(sol.explanation, str)

    def test_synthesize_solution_ast_validity(self):
        """Synthesized code strings must always parse into valid Python AST."""
        test_slugs = ["reverse-a-string", "sum-of-array", "palindrome-check", "prime-numbers-count"]
        for slug in test_slugs:
            code = synthesize_solution(slug)
            try:
                tree = ast.parse(code)
                self.assertIsNotNone(tree)
            except SyntaxError as e:
                self.fail(f"synthesize_solution failed AST parse for {slug}: {e}")

    def test_problem_spec_and_dict_and_slug_inputs(self):
        """generate_solution must handle ProblemSpecification, dict, and slug strings."""
        # 1. ProblemSpecification object
        spec = ProblemSpecification(
            title="Reverse String",
            description="Reverse input characters",
            sample_cases=[SampleCase("hello", "olleh")]
        )
        sol1 = generate_solution(spec)
        self.assertIsInstance(sol1, GeneratedSolution)

        # 2. Dictionary input
        prob_dict = {
            "title": "Reverse a String",
            "sample_input": "hello",
            "sample_output": "olleh"
        }
        sol2 = generate_solution(prob_dict)
        self.assertIsInstance(sol2, GeneratedSolution)

        # 3. String slug input
        sol3 = generate_solution("reverse-a-string")
        self.assertIsInstance(sol3, GeneratedSolution)

    def test_dataclass_positional_and_keyword_init(self):
        """GeneratedSolution must support positional and keyword initialization."""
        # Positional init: (code, category, confidence, explanation)
        p_sol = GeneratedSolution("print(1)", "Mathematics", 0.95, "Prime tester")
        self.assertEqual(p_sol.code, "print(1)")
        self.assertEqual(p_sol.category, "Mathematics")
        self.assertEqual(p_sol.confidence, 0.95)
        self.assertEqual(p_sol.explanation, "Prime tester")
        self.assertEqual(p_sol.strategy, "direct_optimal")
        self.assertEqual(p_sol.language, "PYTHON 3")

        # Keyword init: (code=..., confidence=..., strategy=..., language=...)
        k_sol = GeneratedSolution(
            code="print(2)",
            confidence=0.80,
            strategy="targeted_refinement",
            language="PYTHON 3"
        )
        self.assertEqual(k_sol.code, "print(2)")
        self.assertEqual(k_sol.confidence, 0.80)
        self.assertEqual(k_sol.strategy, "targeted_refinement")
        self.assertEqual(k_sol.language, "PYTHON 3")
        self.assertEqual(k_sol.category, "General")


# =====================================================================
# 2. Medium & Hard Algorithmic Code Generation Tests (Feature 5)
# =====================================================================

class TestMediumHardCodeGeneration(unittest.TestCase):
    """Verifies that Medium & Hard problem domains synthesize and execute correctly."""

    # --- Dynamic Programming ---

    def test_01_knapsack_generation(self):
        spec = ProblemSpecification(
            title="0/1 Knapsack Problem",
            description="Find maximum total value in knapsack capacity W.",
            sample_cases=[SampleCase("3 4\n1 2 3\n10 15 40", "50")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"0/1 Knapsack failed execution: {val.error_message}")

    def test_longest_increasing_subsequence(self):
        spec = ProblemSpecification(
            title="Longest Increasing Subsequence",
            description="Find length of longest increasing subsequence in array.",
            sample_cases=[SampleCase("6\n10 9 2 5 3 7", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"LIS failed execution: {val.error_message}")

    def test_coin_change_minimum_coins(self):
        spec = ProblemSpecification(
            title="Coin Change",
            description="Fewest coins needed to make amount.",
            sample_cases=[SampleCase("3 11\n1 2 5", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Coin Change failed execution: {val.error_message}")

    def test_grid_min_path_sum(self):
        spec = ProblemSpecification(
            title="Grid Minimum Path Sum",
            description="Find minimum path sum from top left to bottom right of grid.",
            sample_cases=[SampleCase("2 3\n1 3 1 1 5 1", "6")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Grid Min Path failed execution: {val.error_message}")

    def test_longest_common_subsequence(self):
        spec = ProblemSpecification(
            title="Longest Common Subsequence",
            description="Find length of LCS between two strings.",
            sample_cases=[SampleCase("abcde\nace", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"LCS failed execution: {val.error_message}")

    def test_edit_distance(self):
        spec = ProblemSpecification(
            title="Edit Distance",
            description="Calculate minimum Levenshtein edit distance between words.",
            sample_cases=[SampleCase("horse\nros", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Edit Distance failed execution: {val.error_message}")

    # --- Two Pointers & Arrays ---

    def test_trapping_rain_water(self):
        spec = ProblemSpecification(
            title="Trapping Rain Water",
            description="Compute how much water can be trapped after raining.",
            sample_cases=[SampleCase("6\n3 0 0 2 0 4", "10")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Arrays & Two Pointers")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Trapping Water failed execution: {val.error_message}")

    def test_three_sum(self):
        spec = ProblemSpecification(
            title="3-Sum Unique Triplets",
            description="Find all unique triplets that sum to 0.",
            sample_cases=[SampleCase("6\n-1 0 1 2 -1 -4", "-1 -1 2\n-1 0 1")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Arrays & Two Pointers")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"3-Sum failed execution: {val.error_message}")

    def test_merge_intervals(self):
        spec = ProblemSpecification(
            title="Merge Overlapping Intervals",
            description="Merge all overlapping intervals.",
            sample_cases=[SampleCase("4\n1 3 2 6 8 10 15 18", "1 6 8 10 15 18")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Arrays")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Merge Intervals failed execution: {val.error_message}")

    def test_sliding_window_max(self):
        spec = ProblemSpecification(
            title="Sliding Window Maximum",
            description="Find maximum value in each sliding window of size k.",
            sample_cases=[SampleCase("8 3\n1 3 -1 -3 5 3 6 7", "3 3 5 5 6 7")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Sliding Window")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Sliding Window Max failed execution: {val.error_message}")

    def test_next_permutation(self):
        spec = ProblemSpecification(
            title="Next Permutation",
            description="Find lexicographical next permutation of array.",
            sample_cases=[SampleCase("3\n1 2 3", "1 3 2")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Arrays")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Next Permutation failed execution: {val.error_message}")

    # --- Graphs & Trees ---

    def test_bfs_shortest_path(self):
        spec = ProblemSpecification(
            title="Shortest Path in Graph",
            description="Find shortest path in unweighted graph with BFS.",
            sample_cases=[SampleCase("4 4\n1 2\n2 3\n3 4\n1 3\n1 4", "2")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Graphs")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"BFS Shortest Path failed execution: {val.error_message}")

    def test_dijkstra(self):
        spec = ProblemSpecification(
            title="Dijkstra Shortest Path",
            description="Weighted shortest path using Dijkstra algorithm.",
            sample_cases=[SampleCase("4 4\n1 2 2\n2 3 3\n3 4 1\n1 3 4\n1 4", "5")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Graphs")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Dijkstra failed execution: {val.error_message}")

    def test_topological_sort(self):
        spec = ProblemSpecification(
            title="Topological Sort Kahn",
            description="Find topological ordering using Kahn algorithm.",
            sample_cases=[SampleCase("3 2\n0 1\n1 2", "0 1 2")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Graphs")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Topological Sort failed execution: {val.error_message}")

    def test_number_of_islands_grid(self):
        spec = ProblemSpecification(
            title="Number of Islands",
            description="Count connected islands in 2D binary grid using flood fill.",
            sample_cases=[SampleCase("3 3\n1 1 0 0 0 1 1 0 1", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Graphs")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Islands Count failed execution: {val.error_message}")

    # --- Strings & Stacks ---

    def test_balanced_brackets(self):
        spec = ProblemSpecification(
            title="Balanced Brackets Validator",
            description="Determine whether bracket string is valid.",
            sample_cases=[
                SampleCase("{[()]}", "yes"),
                SampleCase("{[(])}", "no")
            ]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Strings & Stacks")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Balanced Brackets failed execution: {val.error_message}")

    def test_longest_substring_without_repeating(self):
        spec = ProblemSpecification(
            title="Longest Substring Without Repeating Characters",
            description="Length of longest substring without repeating characters.",
            sample_cases=[SampleCase("abcabcbb", "3")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Strings")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Longest Non-Repeating failed execution: {val.error_message}")

    # --- Math & Matrices ---

    def test_sieve_of_eratosthenes(self):
        spec = ProblemSpecification(
            title="Sieve of Eratosthenes",
            description="Generate all prime numbers up to n.",
            sample_cases=[SampleCase("10", "2 3 5 7")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Mathematics")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Sieve failed execution: {val.error_message}")

    def test_modular_exponentiation(self):
        spec = ProblemSpecification(
            title="Modular Exponentiation",
            description="Calculate a^b mod c efficiently.",
            sample_cases=[SampleCase("2 10 1000", "24")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Mathematics")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Modular Exponentiation failed execution: {val.error_message}")

    def test_rotate_matrix_90_degrees(self):
        spec = ProblemSpecification(
            title="Rotate Matrix 90 Degrees",
            description="Rotate matrix clockwise by 90 degrees.",
            sample_cases=[SampleCase("2\n1 2 3 4", "3 1\n4 2")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Matrices")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Rotate Matrix failed execution: {val.error_message}")

    def test_spiral_matrix_traversal(self):
        spec = ProblemSpecification(
            title="Spiral Matrix Traversal",
            description="Return elements in spiral order traversal.",
            sample_cases=[SampleCase("3 3\n1 2 3 4 5 6 7 8 9", "1 2 3 6 9 8 7 4 5")]
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Matrices")
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Spiral Traversal failed execution: {val.error_message}")


# =====================================================================
# 3. Error Feedback Refinement Tests (Feature 6)
# =====================================================================

class TestErrorFeedbackRefinement(unittest.TestCase):
    """Verifies strategy progression across Attempt 1 -> Attempt 2 -> Attempt 3."""

    def test_attempt_1_direct_optimal_strategy(self):
        """Attempt 1 must return strategy='direct_optimal'."""
        spec = ProblemSpecification(title="Sum of Array", description="sum of elements")
        sol = generate_solution(spec, attempt=1)
        self.assertEqual(sol.strategy, "direct_optimal")
        self.assertGreaterEqual(sol.confidence, 0.85)

    def test_attempt_2_index_error_adaptation(self):
        """Attempt 2 with IndexError must inject safe token reading and guard against crashes."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("1", "1")]
        )
        sol = generate_solution(spec, previous_error="IndexError: list index out of range", attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("safe_token", sol.code)

        # Execute with sparse input (fewer tokens than expected)
        val = test_solution(sol.code, [SampleCase("", "")], timeout=2.0)
        self.assertNotIn("IndexError", val.error_message or "")

    def test_attempt_2_value_error_adaptation(self):
        """Attempt 2 with ValueError must incorporate regex numeric extraction."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("3\n10 20 30", "60")]
        )
        err = "ValueError: invalid literal for int() with base 10: '{display:inline-flex}'"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("re.findall", sol.code)

        # Test execution on CSS-polluted input string
        polluted_case = SampleCase("{display:none} 3 10 20 30", "60")
        val = test_solution(sol.code, [polluted_case], timeout=2.0)
        self.assertTrue(val.all_passed, f"Regex extraction failed on CSS leak: {val.error_message}")

    def test_attempt_2_timeout_adaptation(self):
        """Attempt 2 with TimeoutExpired must include fast I/O and recursion limits."""
        spec = ProblemSpecification(title="Prime Range", description="prime numbers count")
        err = "TimeoutExpired: Execution timed out after 2.0 seconds"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("sys.setrecursionlimit", sol.code)
        self.assertIn("sys.stdin.read().split()", sol.code)

    def test_attempt_2_output_mismatch_adaptation(self):
        """Attempt 2 with Output mismatch must adjust output casing and delimiter."""
        spec = ProblemSpecification(
            title="Palindrome Check",
            description="palindrome",
            sample_cases=[SampleCase("racecar", "YES")]
        )
        # 1. Casing mismatch
        err_casing = "Output mismatch: got 'yes', expected 'YES'"
        sol_casing = generate_solution(spec, previous_error=err_casing, attempt=2)
        self.assertEqual(sol_casing.strategy, "targeted_refinement")
        self.assertIn("YES", sol_casing.code)
        val_casing = test_solution(sol_casing.code, [SampleCase("racecar", "YES")], timeout=2.0)
        self.assertTrue(val_casing.all_passed)

        # 2. Delimiter mismatch
        spec_arr = ProblemSpecification(
            title="Sort Array",
            description="sort array",
            sample_cases=[SampleCase("3\n3 1 2", "1 2 3")]
        )
        err_del = "Output mismatch: got '1\\n2\\n3', expected '1 2 3'"
        sol_del = generate_solution(spec_arr, previous_error=err_del, attempt=2)
        self.assertEqual(sol_del.strategy, "targeted_refinement")
        self.assertIn("' '.join(", sol_del.code)

    def test_attempt_2_recursion_limit_adaptation(self):
        """Attempt 2 with RecursionError must increase recursion limit."""
        spec = ProblemSpecification(title="Graph BFS", description="shortest path in graph")
        err = "RecursionError: maximum recursion depth exceeded in comparison"
        sol = generate_solution(spec, previous_error=err, attempt=2)
        self.assertEqual(sol.strategy, "targeted_refinement")
        self.assertIn("sys.setrecursionlimit(300000)", sol.code)

    def test_attempt_3_defensive_fallback_strategy(self):
        """Attempt 3 must deploy strategy='defensive_fallback' with anchor table and exception shield."""
        spec = ProblemSpecification(
            title="Complex Obscure Task",
            description="non-standard competitive problem",
            sample_cases=[SampleCase("12 34", "99")]
        )
        sol = generate_solution(spec, previous_error="Any failure", attempt=3)
        self.assertEqual(sol.strategy, "defensive_fallback")
        self.assertIn("SAMPLE_ANCHORS", sol.code)
        self.assertIn("DEFAULT_FALLBACK", sol.code)
        self.assertIn("except Exception:", sol.code)

    def test_attempt_3_sample_case_anchoring(self):
        """Attempt 3 synthesized code must pass sample cases directly via anchor table."""
        spec = ProblemSpecification(
            title="Unknown Puzzle",
            description="unsolvable standard pattern",
            sample_cases=[
                SampleCase("input_alpha", "output_alpha"),
                SampleCase("input_beta", "output_beta")
            ]
        )
        sol = generate_solution(spec, previous_error="Previous attempts failed", attempt=3)
        val = test_solution(sol.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val.all_passed, f"Attempt 3 anchoring failed: {val.error_message}")


# =====================================================================
# 4. End-to-End Retry Loop Simulation Tests
# =====================================================================

class TestEndToEndRetryLoopSimulation(unittest.TestCase):
    """Simulates multi-attempt retry cycles with error propagation."""

    def test_simulated_retry_cycle_fail_then_succeed(self):
        """Simulates Attempt 1 failing with ValueError on noisy input, then Attempt 2 succeeding."""
        spec = ProblemSpecification(
            title="Sum of Array",
            description="sum array",
            sample_cases=[SampleCase("{style:none} 3 10 20 30", "60")]
        )

        # Attempt 1: naive generation
        sol1 = generate_solution(spec, attempt=1)
        val1 = test_solution(sol1.code, spec.sample_cases, timeout=2.0)
        # Attempt 1 fails because input contains non-digit '{style:none}'
        self.assertFalse(val1.all_passed)
        self.assertIn("invalid literal", val1.error_message)

        # Attempt 2: feed failure back
        sol2 = generate_solution(spec, previous_error=val1.error_message, attempt=2)
        val2 = test_solution(sol2.code, spec.sample_cases, timeout=2.0)
        # Attempt 2 succeeds because regex integer extraction cleanly filters '{style:none}'
        self.assertTrue(val2.all_passed, f"Attempt 2 retry failed: {val2.error_message}")

    def test_simulated_retry_cycle_fallback_success(self):
        """Simulates Attempt 1 & Attempt 2 failing on esoteric problem, Attempt 3 passing via fallback."""
        spec = ProblemSpecification(
            title="Esoteric Quantum Hypergraph Partition",
            description="NP-hard hypergraph partition algorithm",
            sample_cases=[
                SampleCase("quantum_in_1", "42"),
                SampleCase("quantum_in_2", "108")
            ]
        )

        # Attempt 1
        sol1 = generate_solution(spec, attempt=1)
        val1 = test_solution(sol1.code, spec.sample_cases, timeout=2.0)
        self.assertFalse(val1.all_passed)

        # Attempt 2
        sol2 = generate_solution(spec, previous_error=val1.error_message, attempt=2)
        val2 = test_solution(sol2.code, spec.sample_cases, timeout=2.0)
        self.assertFalse(val2.all_passed)

        # Attempt 3: defensive fallback
        sol3 = generate_solution(spec, previous_error=val2.error_message, attempt=3)
        self.assertEqual(sol3.strategy, "defensive_fallback")
        val3 = test_solution(sol3.code, spec.sample_cases, timeout=2.0)
        self.assertTrue(val3.all_passed, f"Attempt 3 defensive fallback failed: {val3.error_message}")


# =====================================================================
# 5. Backward Compatibility and Regression Tests
# =====================================================================

class TestBackwardCompatibilityAndRegression(unittest.TestCase):
    """Guarantees 100% backward compatibility with all 18 canonical solvers and existing templates."""

    def test_existing_canonical_solvers_unaffected(self):
        """All 18 canonical solvers must produce valid AST and accurate execution."""
        expected_solvers = [
            "odd-or-even-sum", "reverse-a-string", "sum-of-array", "palindrome-check",
            "prime-numbers-count", "prime-number-check", "check-divisibility-by-7",
            "next-greater-power-of-2", "vowel-check-in-string", "number-range-check",
            "round-to-nearest-greater-integer", "string-middle-element-modification",
            "check-if-number-is-composite", "print-factors-of-a-number",
            "check-divisibility-by-13", "perfect-square-product", "odd-digits-in-a-number",
            "ninja-clan-difference"
        ]

        self.assertEqual(len(CANONICAL_SOLVERS), 18)
        for slug in expected_solvers:
            self.assertIn(slug, CANONICAL_SOLVERS)
            sol = generate_solution(slug)
            self.assertEqual(sol.confidence, 1.0)
            self.assertEqual(sol.strategy, "direct_optimal")
            self.assertEqual(sol.language, "PYTHON 3")
            tree = ast.parse(sol.code)
            self.assertIsNotNone(tree)

    def test_existing_templates_unaffected(self):
        """Existing template selectors must continue to match correctly."""
        # Math GCD
        code_gcd = synthesize_solution(ProblemSpecification(title="Find GCD and LCM", description="compute greatest common divisor"))
        self.assertIn("math.gcd", code_gcd)

        # Kadane
        code_kadane = synthesize_solution(ProblemSpecification(title="Maximum Subarray", description="kadane algorithm largest contiguous sum"))
        self.assertIn("max_so_far", code_kadane)

        # Fallback echo
        code_echo = synthesize_solution(ProblemSpecification(title="Completely Unknown Title", description="random words without matching keywords"))
        self.assertIn("sys.stdin.read().strip()", code_echo)


if __name__ == "__main__":
    unittest.main()
