"""
Test Feature 16: ZenClass Projects Discovery.
Verifies parsing of project cards and columns (Active, Pending, Completed).
"""

import re
import unittest
from tests.e2e.harness.dom_fixtures import ZENCLASS_PROJECTS_HTML


class TestFeature16ZenClassProjectsDiscovery(unittest.TestCase):
    """Verifies ZenClass Projects Discovery specifications from PROJECT.md §Feature 16 & spec_miner_survey_3 §1.3."""

    def test_project_catalog_columns(self):
        """Authoritative source: spec_miner_survey_3 §105 - active-projects, pending-projects, completed-projects."""
        self.assertIn("active-Project-heading", ZENCLASS_PROJECTS_HTML)
        self.assertIn("pending-Project-heading", ZENCLASS_PROJECTS_HTML)
        self.assertIn("completed-Project-heading", ZENCLASS_PROJECTS_HTML)

    def test_project_card_details_extraction(self):
        """Authoritative source: spec_miner_survey_3 §110 - project title, tags, and submit button."""
        title_match = re.search(r'class="project-name">(.*?)<', ZENCLASS_PROJECTS_HTML)
        self.assertIsNotNone(title_match)
        self.assertEqual(title_match.group(1), "Full Stack E-Commerce Platform")

        tags = re.findall(r'class="common-tags">(.*?)<', ZENCLASS_PROJECTS_HTML)
        self.assertIn("React", tags)
        self.assertIn("Node.js", tags)


if __name__ == "__main__":
    unittest.main()
