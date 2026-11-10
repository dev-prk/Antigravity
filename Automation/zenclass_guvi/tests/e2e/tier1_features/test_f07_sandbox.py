"""
Test Feature 7: Subprocess Test Sandbox.
Verifies sandboxed execution of candidate solutions against sample inputs/outputs.
"""

import unittest
from tests.e2e.harness.contract_loader import get_sandbox
from tests.e2e.harness.reference_oracle import CANONICAL_PROBLEMS


class TestFeature07SubprocessSandbox(unittest.TestCase):
    """Verifies Subprocess Test Sandbox specifications from PROJECT.md §Feature 7 & ORIGINAL_REQUEST §R2."""

    def setUp(self):
        self.sandbox, self.source = get_sandbox()

    def test_sandbox_executes_correct_solution(self):
        """Authoritative source: CANONICAL_PROBLEMS ground truth test vectors."""
        problem = CANONICAL_PROBLEMS["odd-or-even-sum"]
        code = problem["canonical_solution"]
        vector = problem["test_vectors"][0]  # "9 2" -> "odd"

        result = self.sandbox.validate_solution(code, vector["input"], vector["expected"])
        self.assertTrue(result.passed)
        self.assertEqual(result.stdout, "odd")
        self.assertEqual(result.exit_code, 0)

    def test_sandbox_catches_wrong_output(self):
        """Verifies sandbox marks mismatched outputs as failed."""
        faulty_code = "print('incorrect_output')"
        result = self.sandbox.validate_solution(faulty_code, "9 2", "odd")
        self.assertFalse(result.passed)
        self.assertEqual(result.stdout, "incorrect_output")

    def test_sandbox_catches_runtime_exceptions(self):
        """Verifies runtime errors (e.g. ZeroDivisionError) are caught and reported."""
        crash_code = "import sys\n1/0\n"
        result = self.sandbox.validate_solution(crash_code, "test", "test")
        self.assertFalse(result.passed)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("ZeroDivisionError", result.stderr)

    def test_sandbox_timeout_enforcement(self):
        """Verifies sandbox kills infinite loops after timeout."""
        infinite_loop = "while True: pass"
        result = self.sandbox.validate_solution(infinite_loop, "input", "expected", timeout_sec=0.5)
        self.assertFalse(result.passed)
        self.assertIn("timed out", (result.error_message or "").lower())


if __name__ == "__main__":
    unittest.main()
