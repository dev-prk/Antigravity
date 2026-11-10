"""
Test Feature 19: Project Human Pause Protocol.
Verifies interactive pause protocol prompting user for repository and deployment URLs.
"""

import unittest
from tests.e2e.harness.contract_loader import get_hitl_handler


class TestFeature19ProjectHITL(unittest.TestCase):
    """Verifies Project Human Pause Protocol specifications from PROJECT.md §Feature 19 & spec_miner_survey_3 §140-167."""

    def setUp(self):
        self.hitl, self.source = get_hitl_handler()

    def test_hitl_prompt_collects_required_urls(self):
        """Authoritative source: spec_miner_survey_3 §151-166 - interactive prompt for github_Url and frontEnd_Deployed_Url."""
        user_response = {
            "github_Url": "https://github.com/devsh/ecommerce-capstone",
            "frontEnd_Deployed_Url": "https://ecommerce-capstone.vercel.app"
        }

        collected = self.hitl.request_project_links(
            project_title="Full Stack E-Commerce Platform",
            project_id="proj-501",
            local_code_dir="/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/projects/ecommerce-capstone",
            required_fields=["github_Url", "frontEnd_Deployed_Url"],
            user_inputs=user_response
        )

        self.assertEqual(collected["github_Url"], "https://github.com/devsh/ecommerce-capstone")
        self.assertEqual(collected["frontEnd_Deployed_Url"], "https://ecommerce-capstone.vercel.app")


if __name__ == "__main__":
    unittest.main()
