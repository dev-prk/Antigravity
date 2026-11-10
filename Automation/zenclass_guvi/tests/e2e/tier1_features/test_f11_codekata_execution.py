"""
Test Feature 11: CodeKata Execution & Submit.
Verifies Run Code lifecycle, test pill parsing, Submit Code lifecycle, and Solved! confirmation.
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.dom_fixtures import GUVI_WORKSPACE_HTML


class TestFeature11CodeKataExecution(unittest.TestCase):
    """Verifies CodeKata Execution & Submit specifications from PROJECT.md §Feature 11 & spec_miner_survey_2 §14-17."""

    def test_run_and_submit_buttons_in_workspace(self):
        """Authoritative source: spec_miner_survey_2 §14,16 - button.run-code and button.submit-code."""
        self.assertIn("run-code rounded-lg", GUVI_WORKSPACE_HTML)
        self.assertIn("submit-code rounded-lg", GUVI_WORKSPACE_HTML)

    def test_run_code_api_execution(self):
        """Authoritative source: spec_miner_survey_2 §14 - POST /code-kata/question/run."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/code-kata/question/run"
            payload = json.dumps({
                "question_id": 1,
                "code": "print('odd')",
                "language": "PYTHON 3"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["testCases"][0]["status"], "Correct Answer")

    def test_submit_code_api_verification(self):
        """Authoritative source: spec_miner_survey_2 §17 - POST /code-kata/question/submit and Solved! status."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/code-kata/question/submit"
            payload = json.dumps({
                "question_id": 1,
                "code": "print('odd')",
                "language": "PYTHON 3"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Solved!")
            self.assertEqual(data["earned_points"], 30)
            self.assertTrue(data["completed"])


if __name__ == "__main__":
    unittest.main()
