"""
Tier 2 Boundary Tests: Empty and Zero Inputs.
Verifies graceful handling of empty inputs, zero items, blank credentials, and boundary quantities.
"""

import unittest
from tests.e2e.harness.contract_loader import get_state_manager, get_problem_extractor, get_sandbox


class TestBoundaryEmptyZeroInputs(unittest.TestCase):
    """Verifies robustness against empty, zero, and boundary inputs."""

    def setUp(self):
        self.state_mgr, _ = get_state_manager(":memory:")
        self.extractor, _ = get_problem_extractor()
        self.sandbox, _ = get_sandbox()

    def test_state_manager_with_zero_tasks(self):
        """Verifies summary statistics when database has zero tasks."""
        stats = self.state_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 0)
        self.assertEqual(stats["total_completed"], 0)
        self.assertEqual(stats["total_pending"], 0)
        self.assertEqual(stats["total_blocked"], 0)
        self.assertEqual(stats["success_rate_percent"], 0.0)

    def test_get_pending_tasks_empty_database(self):
        """Verifies querying pending tasks on an empty database returns empty list."""
        pending = self.state_mgr.get_pending_tasks()
        self.assertEqual(pending, [])

    def test_extractor_with_empty_html(self):
        """Verifies extractor handles completely empty or blank HTML without raising exceptions."""
        spec = self.extractor("")
        self.assertEqual(spec.title, "Unknown")
        self.assertEqual(spec.sample_input, "")
        self.assertEqual(spec.sample_output, "")

    def test_sandbox_with_empty_code_and_input(self):
        """Verifies sandbox handles empty code and empty stdin gracefully."""
        res = self.sandbox.validate_solution("", "", "")
        self.assertTrue(res.passed)
        self.assertEqual(res.stdout, "")
        self.assertEqual(res.exit_code, 0)

    def test_zero_division_candidate_solution(self):
        """Verifies boundary calculation with zero division in solution."""
        zero_code = "print(10 // 0)"
        res = self.sandbox.validate_solution(zero_code, "0", "0")
        self.assertFalse(res.passed)
        self.assertIn("ZeroDivisionError", res.stderr)


if __name__ == "__main__":
    unittest.main()
