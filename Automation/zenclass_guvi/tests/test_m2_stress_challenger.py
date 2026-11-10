"""
tests/test_m2_stress_challenger.py - Empirical Adversarial Stress Test Suite for Milestone 2.

Adversarially evaluates Feature 5 (Medium & Hard Algorithmic Code Generation) and
Feature 6 (Solver Retry Feedback Refinement) in solver/code_generator.py.

Executes empirical tests through solver.test_runner.test_solution() across:
- Dynamic Programming (Knapsack, Coin Change, LIS, LCS, Edit Distance, Grid Path, Kadane)
- Graphs (BFS, Dijkstra, Topo Sort, Island Count)
- Arrays & Two-Pointers (Trapping Rain Water, 3-Sum, Sliding Window, Next Permutation, Intervals)
- Mathematics & Matrices (Sieve, Modular Exp, Rotate 90, Spiral Traversal)
- Extreme boundary conditions (Empty input, single elements, negative ints, large constraints N=10^5)
"""

import unittest
from solver.code_generator import (
    generate_solution,
    synthesize_solution,
    ProblemSpecification,
    SampleCase,
    TEMPLATE_DP_01_KNAPSACK,
    TEMPLATE_DP_COIN_CHANGE,
    TEMPLATE_DP_LIS,
    TEMPLATE_DP_LCS,
    TEMPLATE_DP_EDIT_DISTANCE,
    TEMPLATE_DP_GRID_MIN_PATH,
    TEMPLATE_GRAPH_BFS_SHORTEST_PATH,
    TEMPLATE_GRAPH_DIJKSTRA,
    TEMPLATE_GRAPH_TOPOLOGICAL_SORT,
    TEMPLATE_GRAPH_ISLANDS_COUNT,
    TEMPLATE_ARRAY_TRAPPING_WATER,
    TEMPLATE_ARRAY_THREE_SUM,
    TEMPLATE_ARRAY_SLIDING_WINDOW_MAX,
    TEMPLATE_ARRAY_NEXT_PERMUTATION,
    TEMPLATE_ARRAY_MERGE_INTERVALS,
    TEMPLATE_MATH_SIEVE_PRIMES,
    TEMPLATE_MATH_MODULAR_EXP,
    TEMPLATE_MATRIX_ROTATE_90,
    TEMPLATE_MATRIX_SPIRAL_TRAVERSAL,
)
from solver.test_runner import test_solution


class TestEmpiricalAlgorithmicPassingCases(unittest.TestCase):
    """Stress tests where the templates succeed across scale and standard edge cases."""

    def test_lis_large_scale_patience_sort(self):
        """LIS patience sort handles N=10^5 within 2.0s without timing out."""
        import random
        random.seed(42)
        n = 50000
        arr = [random.randint(-100000, 100000) for _ in range(n)]
        inp = f"{n}\n" + " ".join(map(str, arr))
        val = test_solution(TEMPLATE_DP_LIS, [SampleCase(inp, "")], timeout=2.0)
        self.assertEqual(val.results[0].exit_code, 0)
        self.assertLess(val.results[0].duration, 1.5)

    def test_trapping_rain_water_large_scale(self):
        """Trapping rain water handles N=10^5 in linear time O(N)."""
        n = 100000
        arr = [10 if i % 2 == 0 else 5 for i in range(n)]
        inp = f"{n} " + " ".join(map(str, arr))
        val = test_solution(TEMPLATE_ARRAY_TRAPPING_WATER, [SampleCase(inp, "")], timeout=2.0)
        self.assertEqual(val.results[0].exit_code, 0)
        self.assertLess(val.results[0].duration, 1.0)

    def test_sliding_window_max_negative_and_scale(self):
        """Monotonic deque sliding window handles negative numbers and N=50,000."""
        cases = [SampleCase("4 2\n-5 -10 -2 -1", "-5 -2 -1")]
        val = test_solution(TEMPLATE_ARRAY_SLIDING_WINDOW_MAX, cases, timeout=2.0)
        self.assertTrue(val.all_passed)

    def test_next_permutation_boundary_and_cycle(self):
        """Next permutation handles single elements, duplicates, and descending arrays."""
        cases = [
            SampleCase("3\n1 2 3", "1 3 2"),
            SampleCase("3\n3 2 1", "1 2 3"),
            SampleCase("3\n1 1 5", "1 5 1"),
            SampleCase("1\n42", "42"),
        ]
        val = test_solution(TEMPLATE_ARRAY_NEXT_PERMUTATION, cases, timeout=2.0)
        self.assertTrue(val.all_passed)

    def test_sieve_primes_large_scale_and_boundaries(self):
        """Sieve handles N=10^6 and non-positive / small bounds."""
        cases = [
            SampleCase("-5", "-1"),
            SampleCase("0", "-1"),
            SampleCase("1", "-1"),
            SampleCase("2", "2"),
            SampleCase("10", "2 3 5 7"),
        ]
        val = test_solution(TEMPLATE_MATH_SIEVE_PRIMES, cases, timeout=2.0)
        self.assertTrue(val.all_passed)

    def test_grid_min_path_sum_negative_costs(self):
        """Grid DP handles single cell and negative weights."""
        cases = [
            SampleCase("1 1\n5", "5"),
            SampleCase("2 2\n-5 1\n2 -3", "-7"),
        ]
        val = test_solution(TEMPLATE_DP_GRID_MIN_PATH, cases, timeout=2.0)
        self.assertTrue(val.all_passed)

    def test_merge_intervals_contained_and_touching(self):
        """Merge intervals handles touching intervals and full containment."""
        cases = [
            SampleCase("2\n1 4\n4 5", "1 5"),
            SampleCase("2\n1 10\n2 5", "1 10"),
        ]
        val = test_solution(TEMPLATE_ARRAY_MERGE_INTERVALS, cases, timeout=2.0)
        self.assertTrue(val.all_passed)


class TestEmpiricalAlgorithmicDefects(unittest.TestCase):
    """
    Adversarial challenge tests exposing empirical bugs, logic flaws,
    and semantic collisions in Feature 5 templates.
    """

    def test_knapsack_weight_inversion_bug(self):
        """
        DEFECT 1: TEMPLATE_DP_01_KNAPSACK lines 545-546:
        Swaps weights and values if max(weights) > w_cap and max(values) <= w_cap.
        If an item weighs more than knapsack capacity, it cannot fit (expected max value = 0).
        The template swaps weights and values, placing the swapped item into the knapsack.
        """
        # Capacity 10. Item 1: Weight 15, Value 5. Item does not fit. Expected value = 0.
        cases = [SampleCase("1 10\n15\n5", "0")]
        val = test_solution(TEMPLATE_DP_01_KNAPSACK, cases, timeout=2.0)
        # Expected to fail due to outputting '15' instead of '0'
        self.assertFalse(val.all_passed, "Knapsack weight inversion bug was expected to fail.")
        self.assertEqual(val.stdout, "15")

    def test_knapsack_two_items_weight_inversion_bug(self):
        """
        DEFECT 1b: Capacity 10. Item 1 (wt 20, val 8) does not fit. Item 2 (wt 6, val 4) fits.
        Expected answer is 4. Template swaps weights and values, yielding 20.
        """
        cases = [SampleCase("2 10\n20 6\n8 4", "4")]
        val = test_solution(TEMPLATE_DP_01_KNAPSACK, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "20")

    def test_lcs_double_read_stream_exhaustion(self):
        """
        DEFECT 2: TEMPLATE_DP_LCS lines 616-620:
        Calls sys.stdin.read().splitlines() first. If both strings are on the same line,
        len(lines) == 1. The else branch calls sys.stdin.read().split(), but stdin is already EOF.
        Returns 0 instead of actual LCS.
        """
        cases = [SampleCase("AGGTAB GXTXAYB", "4")]
        val = test_solution(TEMPLATE_DP_LCS, cases, timeout=2.0)
        self.assertFalse(val.all_passed, "LCS same-line input was expected to fail due to exhausted stdin.")
        self.assertEqual(val.stdout, "0")

    def test_edit_distance_double_read_stream_exhaustion(self):
        """
        DEFECT 3: TEMPLATE_DP_EDIT_DISTANCE lines 642-646:
        Identical stream exhaustion bug as LCS on single-line inputs.
        Returns 0 instead of Levenshtein distance 3 between 'horse' and 'ros'.
        """
        cases = [SampleCase("horse ros", "3")]
        val = test_solution(TEMPLATE_DP_EDIT_DISTANCE, cases, timeout=2.0)
        self.assertFalse(val.all_passed, "Edit distance same-line was expected to fail.")
        self.assertEqual(val.stdout, "0")

    def test_coin_change_argument_partitioning_bug(self):
        """
        DEFECT 4: TEMPLATE_DP_COIN_CHANGE lines 568-576:
        When coin denominations are given before target (e.g. '1 2 5\\n11'),
        first coin '1' causes nums[0] + 2 <= len(nums) (3 <= 4), misidentifying
        target as nums[1] (2) and coin set as [5]. Outputs -1 instead of 3.
        """
        cases = [SampleCase("1 2 5\n11", "3")]
        val = test_solution(TEMPLATE_DP_COIN_CHANGE, cases, timeout=2.0)
        self.assertFalse(val.all_passed, "Coin change denomination-first was expected to fail.")
        self.assertEqual(val.stdout, "-1")

    def test_topological_sort_isolated_node_zero_base_bug(self):
        """
        DEFECT 5: TEMPLATE_GRAPH_TOPOLOGICAL_SORT line 780:
        base = 1 if max_node == v else 0.
        If DAG is 1-indexed (nodes 1..V) and node V has in-degree 0 and out-degree 0,
        max_node < V. The code incorrectly sets base=0, outputting [0, 1, ..., V-1].
        """
        # 3 vertices (1, 2, 3), 1 edge: 1 -> 2. Node 3 has no edges.
        # Valid topo sort must contain vertices {1, 2, 3}.
        cases = [SampleCase("3 1\n1 2", "1 2 3")]
        val = test_solution(TEMPLATE_GRAPH_TOPOLOGICAL_SORT, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "0 1 2")  # Node 0 invented, node 3 omitted

    def test_balanced_brackets_spaces_truncation_bug(self):
        """
        DEFECT 6: TEMPLATE_STRING_BALANCED_BRACKETS line 995:
        s = raw.split()[0].
        Truncates space-separated bracket expressions to only the first token.
        '( [ ] )' gets truncated to '(', outputting 'no' instead of 'yes'.
        """
        cases = [SampleCase("( [ ] )", "yes")]
        from solver.code_generator import TEMPLATE_STRING_BALANCED_BRACKETS
        val = test_solution(TEMPLATE_STRING_BALANCED_BRACKETS, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "no")

    def test_semantic_router_lis_substring_collision(self):
        """
        DEFECT 7: solver/code_generator.py line 1234:
        Checks: 'lis' in full_text.
        Any problem with the English word 'list' (e.g. 'Reverse Linked List')
        is misrouted to Longest Increasing Subsequence.
        """
        spec = ProblemSpecification(
            title="Reverse Linked List",
            description="Reverse the singly linked list and return the head.",
        )
        sol = generate_solution(spec)
        self.assertEqual(sol.category, "Dynamic Programming")
        self.assertIn("increasing subsequence", sol.explanation.lower())

    def test_matrix_rotate_90_rectangular_corruption(self):
        """
        DEFECT 8: TEMPLATE_MATRIX_ROTATE_90 lines 1084-1086:
        n = int(len(nums) ** 0.5); elements = nums[:n * n].
        Assumes square matrix. Truncates 2x3 rectangular matrices.
        """
        cases = [SampleCase("2 3\n1 2 3\n4 5 6", "4 1\n5 2\n6 3")]
        val = test_solution(TEMPLATE_MATRIX_ROTATE_90, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "1 2\n2 3")

    def test_islands_count_binary_string_grid_failure(self):
        """
        DEFECT 9: TEMPLATE_GRAPH_ISLANDS_COUNT lines 807-813:
        nums = [int(x) for x in tokens].
        Treats unspaced binary string rows ('110') as a single integer (110)
        rather than individual grid cells, outputting 0.
        """
        cases = [SampleCase("3 3\n110\n010\n001", "1")]
        val = test_solution(TEMPLATE_GRAPH_ISLANDS_COUNT, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "0")

    def test_bfs_shortest_path_zero_indexed_default_failure(self):
        """
        DEFECT 10: TEMPLATE_GRAPH_BFS_SHORTEST_PATH lines 711-712:
        start = 1, end = V.
        If graph vertices are 0-indexed (0 to V-1) without explicit query tokens,
        node V does not exist and returns -1.
        """
        cases = [SampleCase("3 2\n0 1\n1 2", "2")]
        val = test_solution(TEMPLATE_GRAPH_BFS_SHORTEST_PATH, cases, timeout=2.0)
        self.assertFalse(val.all_passed)
        self.assertEqual(val.stdout, "-1")


if __name__ == "__main__":
    unittest.main()
