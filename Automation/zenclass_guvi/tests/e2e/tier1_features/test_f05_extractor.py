"""
Test Feature 5: Problem Statement Extractor.
Verifies parsing of CodeKata problem title, description, constraints, and sample I/O.
"""

import unittest
from tests.e2e.harness.contract_loader import get_problem_extractor
from tests.e2e.harness.dom_fixtures import GUVI_WORKSPACE_HTML


class TestFeature05ProblemExtractor(unittest.TestCase):
    """Verifies Problem Statement Extractor specifications from PROJECT.md §Feature 5 & Survey §2."""

    def setUp(self):
        self.extractor, self.source = get_problem_extractor()

    def test_extract_problem_specification_fields(self):
        """Authoritative source: spec_miner_survey_2 §10 - DOM sections Problem Statement, Sample I/O."""
        spec = self.extractor(GUVI_WORKSPACE_HTML)

        self.assertEqual(spec.title, "Odd or Even Sum")
        self.assertIn("add them and state whether the sum is even or odd", spec.description)
        self.assertIn("Two integers N and M", spec.input_desc)
        self.assertIn("Print \"even\" or \"odd\"", spec.output_desc)
        self.assertEqual(spec.sample_input, "9 2")
        self.assertEqual(spec.sample_output, "odd")

    def test_extract_handles_missing_sections_gracefully(self):
        """Verifies robust fallback when some DOM sections are absent."""
        sparse_html = """
        <div class="workspace-container">
          <h1 class="problem-title">Simple Problem</h1>
          <div class="sample-input">123</div>
        </div>
        """
        spec = self.extractor(sparse_html)
        self.assertEqual(spec.title, "Simple Problem")
        self.assertEqual(spec.sample_input, "123")
        self.assertEqual(spec.sample_output, "")


if __name__ == "__main__":
    unittest.main()
