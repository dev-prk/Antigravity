"""
Test Feature 20: Project Submission & Verification.
Verifies project form submission with user links and platform response verification.
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer


class TestFeature20ProjectSubmit(unittest.TestCase):
    """Verifies Project Submission specifications from PROJECT.md §Feature 20 & spec_miner_survey_3 §117."""

    def test_submit_project_api_payload(self):
        """Authoritative source: spec_miner_survey_3 §117-119 - POST /projects/submit-project."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/projects/submit-project"
            payload = json.dumps({
                "submissionId": "proj-501",
                "submission": {
                    "github_Url": "https://github.com/devsh/zen-capstone",
                    "frontEnd_Deployed_Url": "https://zen-capstone.vercel.app"
                }
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["submissionId"], "proj-501")
            self.assertIn("Project submitted successfully", data["message"])


if __name__ == "__main__":
    unittest.main()
