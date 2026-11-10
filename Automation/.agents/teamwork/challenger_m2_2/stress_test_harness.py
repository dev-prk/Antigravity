"""
stress_test_harness.py - Empirical Adversarial Stress Harness for Milestone 2 Solver.

Adversarially validates:
1. Problem Extractor Robustness:
   - Malformed, truncated, empty, unclosed tags, JS injection strings
   - Title extraction fallbacks and edge cases
   - Multi-sample case extraction (numbered and unnumbered)
   - Property backward compatibility (ProblemSpec / ProblemSpecification, SampleCase aliases)
2. Ace Editor Adapter:
   - Playwright Page CDP keyboard 4-step sequence
   - Platform modifier logic (Meta+A vs Control+A)
   - Graceful fallback to JavaScript API when CDP fails
   - Editor code retrieval across all 4 strategies
   - Editor readiness waiting and timeout behaviors
"""

import ast
import os
import re
import sys
import unittest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, call, patch

# Ensure zenclass_guvi is in sys.path
ZENCLASS_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if ZENCLASS_DIR not in sys.path:
    sys.path.insert(0, ZENCLASS_DIR)

import solver
from solver.extractor import (
    SampleCase,
    ProblemSpecification,
    ProblemSpec,
    ProblemExtractor,
    extract_problem_spec,
)
from solver.ace_adapter import (
    AceEditorAdapter,
    inject_code,
    inject_code_into_ace,
    get_editor_code,
    wait_for_editor,
)


class TestExtractorAdversarial(unittest.TestCase):
    """Stress tests for ProblemExtractor under adversarial and malformed inputs."""

    def test_null_and_empty_inputs_never_crash(self):
        """Verify that extractor never crashes on null, empty, or whitespace inputs."""
        test_inputs = [
            None,
            "",
            "   ",
            "\n\t\r\n",
            "\x00\x01\x02",
            12345,
            {"arbitrary": "object"},
            object(),
        ]
        for val in test_inputs:
            spec = extract_problem_spec(val)
            self.assertIsInstance(spec, ProblemSpecification)
            self.assertEqual(spec.title, "Unknown")
            self.assertEqual(spec.sample_input, "")
            self.assertEqual(spec.sample_output, "")
            self.assertEqual(spec.sample_cases, [])

    def test_severely_malformed_html(self):
        """Stress-test HTML parser with truncated, unclosed, and broken tags."""
        malformed_snippets = [
            "<div class='problem-title'>Truncated without closing",
            "<<<>>>><<div class='problem-title'>Double Angle</div>",
            "<h1 class='problem-title'>Nested <p>Unclosed <b>Bold</h1>",
            "<title>Unclosed Title Tag<div class='sample-input'>Input",
            "<div class='sample-input'>Input 1<div class='sample-output'>Output 1<div class='sample-input'>Input 2",
            "<!DOCTYPE html><html><head><title>Odd or Even - CodeKata - GUVI</title></head><body><!-- unclosed comment",
            "<div class=\"problem-statement\">Description without end",
        ]
        for snippet in malformed_snippets:
            try:
                spec = extract_problem_spec(snippet)
                self.assertIsInstance(spec, ProblemSpecification)
            except Exception as e:
                self.fail(f"Extractor crashed on malformed snippet: {e!r}\nSnippet: {snippet}")

    def test_javascript_injection_strings_sanitization(self):
        """Verify script tags and injection payloads do not execute or break parser."""
        xss_payloads = [
            "<div class='problem-title'><script>alert('XSS')</script>Safe Title</div>",
            "<h1><img src=x onerror=alert(1)>Attack Title</h1>",
            "<div class='problem-statement'><script type='text/javascript'>malicious();</script>Real statement</div>",
            "<div class='sample-input'>1 2<script>alert(1)</script> 3</div>",
        ]
        for payload in xss_payloads:
            spec = extract_problem_spec(payload)
            self.assertIsInstance(spec, ProblemSpecification)
            # Ensure raw <script> tags are stripped out of extracted strings
            self.assertNotIn("<script>", spec.title.lower())
            self.assertNotIn("</script>", spec.title.lower())
            self.assertNotIn("<script>", spec.description.lower())
            self.assertNotIn("<script>", spec.sample_input.lower())

    def test_html_entity_decoding(self):
        """Verify HTML entities are properly unescaped in text and sample I/O."""
        html_content = """
        <div class="problem-title">&lt;Binary&gt; &amp; &quot;Hex&quot; Problem</div>
        <div class="problem-statement">Given A &amp; B where A &lt; B &#39;test&#39;</div>
        <div class="sample-input">5 &amp; 3</div>
        <div class="sample-output">&quot;odd&quot;</div>
        """
        spec = extract_problem_spec(html_content)
        self.assertEqual(spec.title, '<Binary> & "Hex" Problem')
        self.assertIn("Given A & B where A < B 'test'", spec.description)
        self.assertEqual(spec.sample_input, '5 & 3')
        self.assertEqual(spec.sample_output, '"odd"')

    def test_multi_sample_case_numbered_extraction(self):
        """Verify extraction of multiple numbered sample cases."""
        text_html = """
        <div class="problem-details">
          <h1>Multiple Sample Cases</h1>
          <p>Sample Input 1:
          5
          1 2 3 4 5</p>
          <p>Sample Output 1:
          15</p>
          <p>Explanation 1:
          Sum of 1+2+3+4+5 is 15</p>
          <p>Sample Input 2:
          3
          10 20 30</p>
          <p>Sample Output 2:
          60</p>
          <p>Explanation 2:
          Sum is 60</p>
        </div>
        """
        spec = extract_problem_spec(text_html)
        self.assertEqual(len(spec.sample_cases), 2)
        self.assertEqual(spec.sample_cases[0].case_number, 1)
        self.assertEqual(spec.sample_cases[0].input_text, "5\n1 2 3 4 5")
        self.assertEqual(spec.sample_cases[0].expected_output, "15")
        self.assertIn("Sum of 1+2+3+4+5 is 15", spec.sample_cases[0].explanation or "")

        self.assertEqual(spec.sample_cases[1].case_number, 2)
        self.assertEqual(spec.sample_cases[1].input_text, "3\n10 20 30")
        self.assertEqual(spec.sample_cases[1].expected_output, "60")

        # Primary sample_input and sample_output must point to case 1
        self.assertEqual(spec.sample_input, "5\n1 2 3 4 5")
        self.assertEqual(spec.sample_output, "15")

    def test_multi_sample_case_dom_class_extraction(self):
        """Verify extraction of multiple sample cases via CSS classes."""
        dom_html = """
        <div class="problem-title">Multiple CSS Cases</div>
        <div class="sample-input">10 20</div>
        <div class="sample-output">30</div>
        <div class="sample-input">40 50</div>
        <div class="sample-output">90</div>
        <div class="sample-input">1 1</div>
        <div class="sample-output">2</div>
        """
        spec = extract_problem_spec(dom_html)
        self.assertEqual(len(spec.sample_cases), 3)
        self.assertEqual(spec.sample_cases[0].input_text, "10 20")
        self.assertEqual(spec.sample_cases[0].expected_output, "30")
        self.assertEqual(spec.sample_cases[1].input_text, "40 50")
        self.assertEqual(spec.sample_cases[1].expected_output, "90")
        self.assertEqual(spec.sample_cases[2].input_text, "1 1")
        self.assertEqual(spec.sample_cases[2].expected_output, "2")
        self.assertEqual(spec.sample_input, "10 20")
        self.assertEqual(spec.sample_output, "30")

    def test_backward_compatibility_properties(self):
        """Verify complete backward compatibility with older ProblemSpec API."""
        spec = ProblemSpecification(
            title="Backward Test",
            input_spec="Input string",
            output_spec="Output string",
            sample_cases=[SampleCase(input_text="123", expected_output="456")]
        )
        # Property getters
        self.assertEqual(spec.input_desc, "Input string")
        self.assertEqual(spec.output_desc, "Output string")
        self.assertEqual(spec.sample_input, "123")
        self.assertEqual(spec.sample_output, "456")

        # Property setters
        spec.input_desc = "New Input Spec"
        spec.output_desc = "New Output Spec"
        self.assertEqual(spec.input_spec, "New Input Spec")
        self.assertEqual(spec.output_spec, "New Output Spec")

        # SampleCase alias compatibility
        sc = spec.sample_cases[0]
        self.assertEqual(sc.input_data, "123")
        self.assertEqual(sc.input, "123")
        self.assertEqual(sc.expected, "456")
        sc.input_data = "789"
        self.assertEqual(sc.input_text, "789")

        # Canonical alias
        self.assertIs(ProblemSpec, ProblemSpecification)

    def test_case_insensitivity_and_mixed_casing(self):
        """Verify case insensitive handling of tags and attributes."""
        mixed_html = """
        <DIV CLASS="PROBLEM-TITLE">Mixed Casing Title</DIV>
        <DIV CLASS="PROBLEM-STATEMENT">Mixed statement</DIV>
        <DIV CLASS="INPUT-DESCRIPTION">Mixed input</DIV>
        <DIV CLASS="OUTPUT-DESCRIPTION">Mixed output</DIV>
        <DIV CLASS="CONSTRAINTS">Mixed constraints</DIV>
        <DIV CLASS="SAMPLE-INPUT">1 2 3</DIV>
        <DIV CLASS="SAMPLE-OUTPUT">6</DIV>
        """
        spec = extract_problem_spec(mixed_html)
        self.assertEqual(spec.title, "Mixed Casing Title")
        self.assertEqual(spec.description, "Mixed statement")
        self.assertEqual(spec.input_spec, "Mixed input")
        self.assertEqual(spec.output_spec, "Mixed output")
        self.assertEqual(spec.constraints, "Mixed constraints")
        self.assertEqual(spec.sample_input, "1 2 3")
        self.assertEqual(spec.sample_output, "6")


class TestAceAdapterAdversarial(unittest.TestCase):
    """Stress tests for AceEditorAdapter CDP injection, fallbacks, and retrieval."""

    def test_exact_4_step_cdp_keyboard_sequence(self):
        """Verify the exact 4-step CDP keyboard injection sequence on darwin and linux."""
        sample_code = "print('CDP Test')\n"

        for platform_name, expected_mod in [("darwin", "Meta+A"), ("linux", "Control+A"), ("win32", "Control+A")]:
            with patch("sys.platform", platform_name):
                mock_page = MagicMock()
                recorded_calls = []

                mock_page.click.side_effect = lambda sel, **kw: recorded_calls.append(("click", sel))
                mock_page.keyboard.press.side_effect = lambda key: recorded_calls.append(("press", key))
                mock_page.keyboard.insert_text.side_effect = lambda text: recorded_calls.append(("insert_text", text))
                mock_page.evaluate.return_value = sample_code

                adapter = AceEditorAdapter()
                res = adapter.inject_code(mock_page, sample_code, verify=True)

                self.assertTrue(res)
                self.assertEqual(len(recorded_calls), 4)
                self.assertEqual(recorded_calls[0], ("click", "#editor textarea.ace_text-input"))
                self.assertEqual(recorded_calls[1], ("press", expected_mod))
                self.assertEqual(recorded_calls[2], ("press", "Backspace"))
                self.assertEqual(recorded_calls[3], ("insert_text", sample_code))

    def test_keyboard_failure_triggers_js_api_fallback(self):
        """Verify that when page.keyboard raises an exception, _inject_via_js_api is invoked."""
        mock_page = MagicMock()
        mock_page.keyboard.press.side_effect = RuntimeError("CDP Keyboard connection broken")
        
        # JS evaluate returns True
        eval_calls = []
        def eval_mock(script, args=None):
            eval_calls.append((script, args))
            if "getValue" in script:
                return "fallback_code"
            return True

        mock_page.evaluate.side_effect = eval_mock

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, "fallback_code", verify=True)

        self.assertTrue(success)
        # Verify evaluate was called with the JS fallback script containing ace.edit or env.editor
        self.assertTrue(any("window.ace.edit" in s[0] for s in eval_calls))

    def test_keyboard_none_triggers_js_api_fallback(self):
        """Verify that when page.keyboard is None (headless/mock), JS API fallback is called."""
        mock_page = MagicMock()
        mock_page.keyboard = None
        mock_page.evaluate.side_effect = lambda script, arg=None: "code_via_js" if "getValue" in script else True

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, "code_via_js", verify=True)
        self.assertTrue(success)

    def test_js_api_fallback_handles_evaluate_exception(self):
        """Verify inject_code returns False gracefully when both keyboard and JS API fail."""
        mock_page = MagicMock()
        mock_page.keyboard.press.side_effect = RuntimeError("Keyboard dead")
        mock_page.evaluate.side_effect = RuntimeError("JS runtime crashed")

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, "failing_code", verify=False)
        self.assertFalse(success)

    def test_get_editor_code_all_4_strategies(self):
        """
        Verify get_editor_code executes the JS script designed to query all 4 strategies:
          1. window.ace.edit('editor').getValue()
          2. document.getElementById('editor').env.editor.getValue()
          3. Concatenate all div.ace_line text nodes
          4. textarea.value fallback
        """
        mock_page = MagicMock()

        # Strategy script verification
        eval_scripts = []
        def eval_recorder(script, arg=None):
            eval_scripts.append(script)
            return "var a = 10;"

        mock_page.evaluate.side_effect = eval_recorder
        code = get_editor_code(mock_page)

        self.assertEqual(code, "var a = 10;")
        self.assertEqual(len(eval_scripts), 1)
        executed_js = eval_scripts[0]

        # Verify all 4 strategies are present in the evaluate script
        self.assertIn("window.ace.edit", executed_js, "Strategy 1 missing")
        self.assertIn("env.editor.getValue", executed_js, "Strategy 2 missing")
        self.assertIn(".ace_line", executed_js, "Strategy 3 missing")
        self.assertIn("textarea.ace_text-input", executed_js, "Strategy 4 missing")

    def test_wait_for_editor_readiness_and_timeout(self):
        """Verify wait_for_editor handles success, timeout, and degraded environments."""
        # 1. Normal success
        mock_page_ok = MagicMock()
        mock_page_ok.wait_for_selector.return_value = None
        mock_page_ok.wait_for_function.return_value = None
        self.assertTrue(wait_for_editor(mock_page_ok, timeout=0.5))

        # 2. Timeout on wait_for_function but textarea exists
        mock_page_degraded = MagicMock()
        mock_page_degraded.wait_for_selector.return_value = None
        mock_page_degraded.wait_for_function.side_effect = TimeoutError("Wait function timed out")
        mock_page_degraded.query_selector.return_value = MagicMock() # Textarea found
        self.assertTrue(wait_for_editor(mock_page_degraded, timeout=0.1))

        # 3. Timeout and textarea does not exist
        mock_page_failed = MagicMock()
        mock_page_failed.wait_for_selector.side_effect = TimeoutError("Selector timed out")
        mock_page_failed.query_selector.return_value = None
        self.assertFalse(wait_for_editor(mock_page_failed, timeout=0.1))

        # 4. Mock page without wait_for_selector
        plain_mock = object()
        self.assertTrue(wait_for_editor(plain_mock, timeout=0.1))

    def test_verify_mismatch_triggers_js_api_and_returns_false_if_still_failing(self):
        """Verify inject_code falls back to JS API on code mismatch and returns False if mismatch persists."""
        mock_page = MagicMock()
        target_code = "print('target')"
        # get_code returns bad code every time
        mock_page.evaluate.return_value = "print('corrupted')"

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, target_code, verify=True)
        self.assertFalse(success)

    def test_page_content_exception_handling(self):
        """Verify extractor handles page.content() raising exception without crashing."""
        broken_page = MagicMock()
        broken_page.content.side_effect = RuntimeError("Playwright target page closed")

        spec = extract_problem_spec(broken_page)
        self.assertEqual(spec.title, "Unknown")
        self.assertEqual(spec.sample_input, "")

    def test_empty_and_multiline_code_injection(self):
        """Verify inject_code handles empty strings and CRLF normalization cleanly."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "line1\nline2"

        adapter = AceEditorAdapter()
        res = adapter.inject_code(mock_page, "line1\r\nline2\r\n", verify=True)
        self.assertTrue(res)
        mock_page.keyboard.insert_text.assert_called_with("line1\nline2\n")

    def test_sample_input_containing_keywords(self):
        """Verify extractor correctly extracts sample input even when it contains tricky keywords."""
        html_snippet = """
        <div class="problem-details">
          <h1>Keyword Problem</h1>
          <p>Sample Input 1:
          Input: 10 20
          Constraints: none</p>
          <p>Sample Output 1:
          Output: 30</p>
        </div>
        """
        spec = extract_problem_spec(html_snippet)
        self.assertEqual(spec.title, "Keyword Problem")
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertIn("10 20", spec.sample_cases[0].input_text)
        self.assertIn("30", spec.sample_cases[0].expected_output)


if __name__ == "__main__":
    unittest.main()

