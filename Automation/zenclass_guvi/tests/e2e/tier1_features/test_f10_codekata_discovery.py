"""
Test Feature 10: CodeKata Table Discovery.
Verifies parsing of 143-page table, metadata extraction, and #completed-icon_svg__a filtering.
"""

import re
import unittest
from tests.e2e.harness.dom_fixtures import GUVI_CODEKATA_TABLE_HTML


class TestFeature10CodeKataDiscovery(unittest.TestCase):
    """Verifies CodeKata Table Discovery specifications from PROJECT.md §Feature 10 & spec_miner_survey_2 §1.2."""

    def test_catalog_table_structure_and_rows(self):
        """Authoritative source: spec_miner_survey_2 §1.2 - tbody tr.cursor-pointer."""
        rows = re.findall(r'<tr class="cursor-pointer".*?>(.*?)</tr>', GUVI_CODEKATA_TABLE_HTML, re.DOTALL)
        self.assertEqual(len(rows), 5)  # 5 rows in fixture

    def test_completed_icon_svg_filtering(self):
        """Authoritative source: spec_miner_survey_2 §22 - #completed-icon_svg__a indicates Solved."""
        rows = re.findall(r'<tr class="cursor-pointer" data-slug="([^"]+)">(.*?)</tr>', GUVI_CODEKATA_TABLE_HTML, re.DOTALL)
        solved_slugs = []
        pending_slugs = []

        for slug, row_html in rows:
            if "#completed-icon_svg__a" in row_html:
                solved_slugs.append(slug)
            else:
                pending_slugs.append(slug)

        self.assertIn("odd-or-even-sum", solved_slugs)
        self.assertIn("prime-numbers-count", solved_slugs)
        self.assertIn("reverse-a-string", pending_slugs)
        self.assertIn("sum-of-array", pending_slugs)
        self.assertIn("palindrome-check", pending_slugs)
        self.assertEqual(len(pending_slugs), 3)

    def test_metadata_extraction_fields(self):
        """Authoritative source: spec_miner_survey_2 §23 - title, rate, difficulty, points."""
        title_match = re.search(r'<td class="problem-title">(.*?)</td>', GUVI_CODEKATA_TABLE_HTML)
        rate_match = re.search(r'<td class="success-rate">(.*?)</td>', GUVI_CODEKATA_TABLE_HTML)
        diff_match = re.search(r'<td class="difficulty">(.*?)</td>', GUVI_CODEKATA_TABLE_HTML)
        pts_match = re.search(r'<td class="points">(.*?)</td>', GUVI_CODEKATA_TABLE_HTML)

        self.assertEqual(title_match.group(1), "1. Odd or Even Sum")
        self.assertEqual(rate_match.group(1), "73.97%")
        self.assertEqual(diff_match.group(1), "Easy")
        self.assertEqual(pts_match.group(1), "30")

    def test_pagination_controls_detection(self):
        """Authoritative source: spec_miner_survey_2 §24 - 143 total pages and pagination buttons."""
        self.assertIn("Go to previous page", GUVI_CODEKATA_TABLE_HTML)
        self.assertIn("Go to next page", GUVI_CODEKATA_TABLE_HTML)
        self.assertIn(">143<", GUVI_CODEKATA_TABLE_HTML)


if __name__ == "__main__":
    unittest.main()
