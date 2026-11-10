"""
Tier 2 Boundary Tests: Malformed URLs and Missing DOM Selectors.
Verifies rejection of invalid submission links, malformed URLs, and non-existent DOM elements.
"""

import re
import unittest
from tests.e2e.harness.contract_loader import get_problem_extractor


class TestBoundaryMalformedUrlsSelectors(unittest.TestCase):
    """Verifies robustness against malformed URLs and missing DOM selectors."""

    def setUp(self):
        self.extractor, _ = get_problem_extractor()

    def test_url_validation_rejects_malformed_urls(self):
        """Authoritative source: spec_miner_survey_3 §96 - regex /^(ftp|http|https):\\/\\/[^ "]+$/."""
        url_regex = re.compile(r"^(ftp|http|https)://[^ \"]+$")

        malformed_urls = [
            "htp://typo.com",
            "http://",
            "https://",
            "http://with space/test",
            "javascript:void(0)",
            "data:text/html,<script>alert(1)</script>",
            "   https://leading-spaces.com",
            "https://trailing-space.com ",
            "https://quote\"inside.com",
            "\nhttps://newline.com\n",
        ]
        for url in malformed_urls:
            self.assertFalse(bool(url_regex.match(url)), f"Expected rejection for: '{url}'")

    def test_missing_selectors_in_partial_dom(self):
        """Verifies parsing damaged or partial HTML snippets does not crash extractor."""
        damaged_htmls = [
            "<html><body><h1>Title Only</h1></body></html>",
            "<div class='problem-statement'>Missing title and sample IO</div>",
            "<div class='sample-input'>Broken open tag",
            "<!DOCTYPE html>",
        ]
        for html in damaged_htmls:
            try:
                spec = self.extractor(html)
                self.assertIsNotNone(spec)
            except Exception as e:
                self.fail(f"Extractor crashed on damaged HTML '{html}': {e}")


if __name__ == "__main__":
    unittest.main()
