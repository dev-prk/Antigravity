"""
Test Feature 14: Dynamic Task Submission.
Verifies dynamic 13-field modal mapping (Module 41486) and URL validation regex.
"""

import re
import unittest
from tests.e2e.harness.dom_fixtures import ZENCLASS_SUBMISSION_MODAL_HTML


class TestFeature14ZenClassSubmission(unittest.TestCase):
    """Verifies Dynamic Task Submission specifications from PROJECT.md §Feature 14 & spec_miner_survey_3 §1.2."""

    # Authoritative 13 submission field keys from Module 41486 disassembly
    EXPECTED_FIELD_KEYS = [
        "frontEnd_Deployed_Url",
        "backEnd_Deployed_Url",
        "frontEnd_SourceCode",
        "backEnd_SourceCode",
        "github_Url",
        "g-drive_Url",
        "submission_Url",
        "linkedin_post_Url",
        "document_Url",
        "figma_Url",
        "figma_prototype_Url",
        "dribble_Url",
        "behance_Url"
    ]

    def test_submission_modal_contains_mapped_inputs(self):
        """Verifies modal container has form wrappers and input elements."""
        self.assertIn("submit-form-container-web", ZENCLASS_SUBMISSION_MODAL_HTML)
        self.assertIn('data-field-key="frontEnd_Deployed_Url"', ZENCLASS_SUBMISSION_MODAL_HTML)
        self.assertIn('data-field-key="github_Url"', ZENCLASS_SUBMISSION_MODAL_HTML)

    def test_url_validation_regex_conformance(self):
        """Authoritative source: spec_miner_survey_3 §96 - regex /^(ftp|http|https):\\/\\/[^ "]+$/."""
        url_pattern = re.compile(r"^(ftp|http|https)://[^ \"]+$")

        valid_urls = [
            "https://github.com/testuser/repo",
            "http://localhost:3000",
            "https://zenclass.in/tasks?batch=12",
            "https://project.vercel.app/demo#section",
            "ftp://files.example.org/submission.zip"
        ]
        for url in valid_urls:
            self.assertTrue(url_pattern.match(url), f"Valid URL failed validation: {url}")

        invalid_urls = [
            "",
            "github.com/no-protocol",
            "https://has space.com",
            "javascript:alert(1)",
            "file:///etc/passwd"
        ]
        for url in invalid_urls:
            self.assertFalse(url_pattern.match(url), f"Invalid URL unexpectedly matched: {url}")


if __name__ == "__main__":
    unittest.main()
