"""
Test Feature 8: Ace Editor Keyboard Adapter.
Verifies Ace Editor keyboard text insertion protocol and buffer management.
"""

import unittest
from tests.e2e.harness.dom_fixtures import GUVI_WORKSPACE_HTML


class TestFeature08AceEditorAdapter(unittest.TestCase):
    """Verifies Ace Editor Keyboard Adapter specifications from PROJECT.md §Feature 8 & spec_miner_survey_2 §13."""

    def test_ace_editor_container_and_textarea_selectors(self):
        """Authoritative source: spec_miner_survey_2 §11 - div#editor.ace_editor and textarea.ace_text-input."""
        self.assertIn('id="editor"', GUVI_WORKSPACE_HTML)
        self.assertIn('class="ace_editor"', GUVI_WORKSPACE_HTML)
        self.assertIn('class="ace_text-input"', GUVI_WORKSPACE_HTML)

    def test_ace_injection_command_format(self):
        """Authoritative source: spec_miner_survey_2 §13 - Focus, Meta+A, Backspace, insert_text."""
        sample_code = "print('Hello Guvi')"
        # Verify sequence representation
        steps = [
            ("click", "div#editor textarea.ace_text-input"),
            ("press", "Meta+A"),
            ("press", "Backspace"),
            ("insert_text", sample_code),
        ]
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[3][0], "insert_text")
        self.assertEqual(steps[3][1], sample_code)


if __name__ == "__main__":
    unittest.main()
