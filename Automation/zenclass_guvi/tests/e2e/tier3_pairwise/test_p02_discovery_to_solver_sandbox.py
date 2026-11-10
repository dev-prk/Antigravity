"""
Tier 3 Pairwise Tests: Discovery to Solver and Subprocess Sandbox.
Verifies handover from parsed problem statement to code synthesizer and sandboxed validation.
"""

import unittest
from tests.e2e.harness.contract_loader import (
    get_problem_extractor,
    get_code_generator,
    get_sandbox
)
from tests.e2e.harness.dom_fixtures import GUVI_WORKSPACE_HTML


class TestPairwiseDiscoveryToSolverSandbox(unittest.TestCase):
    """Verifies that discovered problem specs are correctly transformed into verified code solutions."""

    def setUp(self):
        self.extractor, _ = get_problem_extractor()
        self.code_gen, _ = get_code_generator()
        self.sandbox, _ = get_sandbox()

    def test_end_to_end_extractor_to_sandbox_pipeline(self):
        """Pipeline: Problem HTML -> Extractor -> Code Synthesizer -> Subprocess Sandbox -> Result."""
        # 1. Extract specification from problem workspace DOM
        spec = self.extractor(GUVI_WORKSPACE_HTML)
        self.assertEqual(spec.title, "Odd or Even Sum")
        self.assertTrue(len(spec.sample_input) > 0)
        self.assertTrue(len(spec.sample_output) > 0)

        # 2. Synthesize candidate code
        candidate_code = self.code_gen("odd-or-even-sum")
        self.assertIn("def solve", candidate_code)

        # 3. Validate candidate code in subprocess sandbox
        val_result = self.sandbox.validate_solution(
            code=candidate_code,
            sample_input=spec.sample_input,
            expected_output=spec.sample_output
        )

        self.assertTrue(val_result.passed, f"Sandbox validation failed: {val_result.error_message}")
        self.assertEqual(val_result.stdout, spec.sample_output)
        self.assertEqual(val_result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
