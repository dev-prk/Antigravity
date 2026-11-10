"""
test_blueprints.py - Self-Verification Test Suite for Explorer M2.1 Blueprints.
Validates proposed_extractor.py and proposed_ace_adapter.py against all E2E test vectors.
"""

import sys
import unittest
from unittest.mock import MagicMock, call

# Ensure agent directory is in path
from proposed_extractor import (
    ProblemSpecification,
    ProblemSpec,
    SampleCase,
    ProblemExtractor,
    extract_problem_spec
)
from proposed_ace_adapter import (
    AceEditorAdapter,
    inject_code,
    get_editor_code,
    wait_for_editor,
    inject_code_into_ace,
    ACE_EDITOR_CONTAINER,
    ACE_TEXT_INPUT,
    ACE_LINE_LAYER
)

# Workspace HTML Fixture from tests/e2e/harness/dom_fixtures.py
GUVI_WORKSPACE_HTML = """<!DOCTYPE html>
<html lang="en">
<head><title>Odd or Even Sum - CodeKata - GUVI</title></head>
<body>
  <div class="workspace-container">
    <div class="problem-details-pane">
      <h1 class="problem-title">Odd or Even Sum</h1>
      <span class="question-status">Unsolved</span>
      <div class="problem-statement">
        Given two numbers N and M, add them and state whether the sum is even or odd.
      </div>
      <div class="input-description">
        Two integers N and M separated by space.
      </div>
      <div class="output-description">
        Print "even" or "odd" without quotes.
      </div>
      <div class="sample-input">
        9 2
      </div>
      <div class="sample-output">
        odd
      </div>
    </div>
    <div class="editor-pane">
      <div id="editor" class="ace_editor">
        <textarea class="ace_text-input" spellcheck="false"></textarea>
      </div>
    </div>
  </div>
</body>
</html>"""


class TestProblemExtractorBlueprint(unittest.TestCase):
    """Verifies proposed_extractor satisfies all requirements from test_f05_extractor and test_b01."""

    def test_extract_guvi_workspace_html(self):
        """Matches test_f05_extractor.py test_extract_problem_specification_fields."""
        spec = extract_problem_spec(GUVI_WORKSPACE_HTML)

        self.assertEqual(spec.title, "Odd or Even Sum")
        self.assertIn("add them and state whether the sum is even or odd", spec.description)
        self.assertIn("Two integers N and M", spec.input_desc)
        self.assertIn("Print \"even\" or \"odd\"", spec.output_desc)
        self.assertEqual(spec.sample_input, "9 2")
        self.assertEqual(spec.sample_output, "odd")

        # Verify new M2 fields
        self.assertEqual(spec.input_spec, spec.input_desc)
        self.assertEqual(spec.output_spec, spec.output_desc)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text, "9 2")
        self.assertEqual(spec.sample_cases[0].expected_output, "odd")
        self.assertEqual(spec.sample_cases[0].case_number, 1)

    def test_extract_handles_missing_sections_gracefully(self):
        """Matches test_f05_extractor.py test_extract_handles_missing_sections_gracefully."""
        sparse_html = """
        <div class="workspace-container">
          <h1 class="problem-title">Simple Problem</h1>
          <div class="sample-input">123</div>
        </div>
        """
        spec = extract_problem_spec(sparse_html)
        self.assertEqual(spec.title, "Simple Problem")
        self.assertEqual(spec.sample_input, "123")
        self.assertEqual(spec.sample_output, "")
        self.assertEqual(len(spec.sample_cases), 1)

    def test_extract_with_empty_or_zero_html(self):
        """Matches test_b01_empty_zero_inputs.py test_extractor_with_empty_html."""
        spec = extract_problem_spec("")
        self.assertEqual(spec.title, "Unknown")
        self.assertEqual(spec.sample_input, "")
        self.assertEqual(spec.sample_output, "")
        self.assertEqual(len(spec.sample_cases), 0)

        spec_none = extract_problem_spec(None)
        self.assertEqual(spec_none.title, "Unknown")

    def test_extract_multiple_sample_cases_dom(self):
        """Verifies multi-sample case parsing from DOM."""
        multi_html = """
        <div class="workspace-container">
          <h1 class="problem-title">Sum of Two</h1>
          <div class="problem-statement">Add two numbers.</div>
          <div class="sample-input">1 2</div>
          <div class="sample-output">3</div>
          <div class="sample-input">10 20</div>
          <div class="sample-output">30</div>
        </div>
        """
        spec = extract_problem_spec(multi_html)
        self.assertEqual(len(spec.sample_cases), 2)
        self.assertEqual(spec.sample_cases[0].input_text, "1 2")
        self.assertEqual(spec.sample_cases[0].expected_output, "3")
        self.assertEqual(spec.sample_cases[1].input_text, "10 20")
        self.assertEqual(spec.sample_cases[1].expected_output, "30")
        self.assertEqual(spec.sample_input, "1 2")
        self.assertEqual(spec.sample_output, "3")

    def test_extract_labeled_text_format(self):
        """Verifies fallback regex extraction from plain labeled text without CSS classes."""
        plain_html = """
        <div>
          <h3>Problem Statement:</h3>
          <p>Find if number is prime or not.</p>
          <h3>Input Description:</h3>
          <p>A single integer N.</p>
          <h3>Output Description:</h3>
          <p>yes or no.</p>
          <h3>Constraints:</h3>
          <p>1 &lt;= N &lt;= 100000</p>
          <h3>Sample Input 1:</h3>
          <pre>7</pre>
          <h3>Sample Output 1:</h3>
          <pre>yes</pre>
          <h3>Explanation 1:</h3>
          <p>7 has no divisors other than 1 and 7.</p>
          <h3>Sample Input 2:</h3>
          <pre>10</pre>
          <h3>Sample Output 2:</h3>
          <pre>no</pre>
        </div>
        """
        spec = extract_problem_spec(plain_html)
        self.assertIn("Find if number is prime", spec.description)
        self.assertIn("single integer N", spec.input_spec)
        self.assertIn("yes or no", spec.output_spec)
        self.assertIn("1 <= N <= 100000", spec.constraints)
        self.assertEqual(len(spec.sample_cases), 2)
        self.assertEqual(spec.sample_cases[0].input_text, "7")
        self.assertEqual(spec.sample_cases[0].expected_output, "yes")
        self.assertEqual(spec.sample_cases[0].explanation, "7 has no divisors other than 1 and 7.")
        self.assertEqual(spec.sample_cases[1].input_text, "10")
        self.assertEqual(spec.sample_cases[1].expected_output, "no")

    def test_multiline_sample_input_preservation(self):
        """Verifies that internal newlines in sample input/output are preserved."""
        multiline_html = """
        <div class="workspace-container">
          <h1 class="problem-title">Array Sum</h1>
          <div class="sample-input">
            5
            1 2 3 4 5
          </div>
          <div class="sample-output">
            15
          </div>
        </div>
        """
        spec = extract_problem_spec(multiline_html)
        self.assertEqual(spec.sample_input, "5\n1 2 3 4 5")
        self.assertEqual(spec.sample_output, "15")


class TestAceAdapterBlueprint(unittest.TestCase):
    """Verifies proposed_ace_adapter satisfies all requirements from test_f08_ace_adapter and PROJECT.md."""

    def test_selectors_and_contract(self):
        """Matches test_f08_ace_adapter.py test_ace_editor_container_and_textarea_selectors."""
        self.assertIn('id="editor"', GUVI_WORKSPACE_HTML)
        self.assertIn('class="ace_editor"', GUVI_WORKSPACE_HTML)
        self.assertIn('class="ace_text-input"', GUVI_WORKSPACE_HTML)

    def test_cdp_keyboard_injection_call_sequence(self):
        """Matches test_f08_ace_adapter.py test_ace_injection_command_format."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "print('Hello Guvi')"  # verification passes

        code = "print('Hello Guvi')"
        success = inject_code(mock_page, code)
        self.assertTrue(success)

        # Verify calls on mock_page
        mock_page.click.assert_called_with("#editor textarea.ace_text-input", timeout=5000)
        # Select All (Meta+A on mac, Control+A on linux)
        modifier = "Meta" if sys.platform == "darwin" else "Control"
        mock_page.keyboard.press.assert_any_call(f"{modifier}+A")
        mock_page.keyboard.press.assert_any_call("Backspace")
        mock_page.keyboard.insert_text.assert_called_with(code)

    def test_js_fallback_when_cdp_fails(self):
        """Verifies JS API fallback executes if keyboard injection encounters error."""
        mock_page = MagicMock()
        # Simulate click raising exception (e.g. element covered or CDP unavailable)
        mock_page.click.side_effect = Exception("Element not clickable")
        mock_page.evaluate.side_effect = [
            True,                   # _inject_via_js_api returns True
            "print('fallback')",    # get_code returns injected code
        ]

        code = "print('fallback')"
        success = inject_code(mock_page, code)
        self.assertTrue(success)
        self.assertTrue(mock_page.evaluate.called)

    def test_get_editor_code(self):
        """Verifies get_editor_code retrieves string from editor."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "def solve(): pass"
        code = get_editor_code(mock_page)
        self.assertEqual(code, "def solve(): pass")

    def test_wait_for_editor(self):
        """Verifies wait_for_editor waits for selector and function."""
        mock_page = MagicMock()
        ready = wait_for_editor(mock_page, timeout=5.0)
        self.assertTrue(ready)
        mock_page.wait_for_selector.assert_called_with(
            "#editor textarea.ace_text-input",
            state="attached",
            timeout=5000
        )
        self.assertTrue(mock_page.wait_for_function.called)

    def test_alias_equivalence(self):
        """Verifies inject_code_into_ace is identical to inject_code."""
        self.assertIs(inject_code_into_ace, inject_code)


if __name__ == "__main__":
    unittest.main()
