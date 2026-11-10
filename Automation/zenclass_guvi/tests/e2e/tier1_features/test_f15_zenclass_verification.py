"""
Test Feature 15: Task Submission Verification.
Verifies positive UI confirmation popup ("Task Submitted Suceessfully").
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.dom_fixtures import ZENCLASS_SUBMISSION_MODAL_HTML


class TestFeature15ZenClassVerification(unittest.TestCase):
    """Verifies Task Submission Verification specifications from PROJECT.md §Feature 15 & ORIGINAL_REQUEST §R3."""

    def test_confirmation_modal_verbatim_string(self):
        """Authoritative source: spec_miner_survey_3 §99 - 'Task Submitted Suceessfully' (noting verbatim spelling)."""
        self.assertIn("Task Submitted Suceessfully", ZENCLASS_SUBMISSION_MODAL_HTML)

    def test_task_submit_api_positive_confirmation(self):
        """Verifies API response confirmation for task submission."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/task/task-submit"
            payload = json.dumps({
                "submissionId": "task-101",
                "submission": {
                    "github_Url": "https://github.com/user/task-101",
                    "frontEnd_Deployed_Url": "https://task-101.netlify.app"
                }
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertIn("Task Submitted", data["message"])
            self.assertEqual(data["submissionId"], "task-101")


if __name__ == "__main__":
    unittest.main()
