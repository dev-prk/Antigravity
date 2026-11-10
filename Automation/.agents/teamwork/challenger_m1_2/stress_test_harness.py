#!/usr/bin/env python3
"""
Empirical Adversarial Stress Test Harness for solver/extractor.py
Milestone 1: Filtering & Extractor Foundation (Challenger 2)

Tests pathological HTML/DOM inputs, CSS leak regressions, malformed tags,
and legitimate competitive programming inputs/outputs with braces.
"""

import sys
import os
import unittest
from typing import List, Dict, Any

# Ensure workspace is on sys.path
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../zenclass_guvi"))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from solver.extractor import ProblemExtractor, ProblemSpecification, SampleCase


class TestPathologicalMalformedTags(unittest.TestCase):
    """Stress-test malformed and unclosed style/template tags."""

    def test_unclosed_style_swallows_semantic_tags(self):
        """Unclosed <style> before <section> or <article> swallows problem description."""
        html = """
        <style>
        .editor { font-family: monospace; }
        <section>Problem Statement: Calculate factorial of n.</section>
        <p>Sample Input: 5</p>
        <p>Sample Output: 120</p>
        """
        spec = ProblemExtractor.extract(html)
        # Empirical finding: lookahead lacks semantic HTML5 tags (section, article, main)
        # Description is swallowed because regex runs until <p>
        self.assertEqual(spec.description, "Calculate factorial of n.",
                         "Unclosed <style> swallowed <section> Problem Statement")

    def test_spaced_closing_tags(self):
        """Spaced closing tags like </style > and </template > should be stripped."""
        html = """
        <style type="text/css"> body { color: red; } </style >
        <template id="tmpl"> <div>shadow</div> </template >
        <div class="problem-title">Spaced Tags</div>
        <div class="problem-statement">Compute the square.</div>
        <div class="sample-input">6</div>
        <div class="sample-output">36</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(spec.title, "Spaced Tags")
        self.assertEqual(spec.description, "Compute the square.")
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text, "6")
        self.assertEqual(spec.sample_cases[0].expected_output, "36")


class TestComplexInlineCSS(unittest.TestCase):
    """Stress-test complex inline CSS with @media, @keyframes, and pseudo-elements."""

    def test_keyframes_leakage(self):
        """@keyframes declaration blocks leak percentage tokens into text."""
        html = """
        <div class="problem-title">Animation Problem</div>
        <div class="problem-statement">
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        Rotate the array k times.
        </div>
        <div class="sample-input">1 2 3 4 5</div>
        <div class="sample-output">5 1 2 3 4</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertNotIn("{ 0% 100% }", spec.description, "@keyframes leaked residual tokens { 0% 100% }")
        self.assertNotIn("0%", spec.description)

    def test_class_selector_leakage(self):
        """Class selectors like div.card or input.styled leak selector names into text."""
        html = """
        <div class="problem-title">Card Layout</div>
        <div class="problem-statement">
        div.card { border: 1px solid black; }
        span.badge { display: inline-block; }
        Sort cards by suit.
        </div>
        <div class="sample-input">hearts spades</div>
        <div class="sample-output">spades hearts</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertNotIn("div.card", spec.description, "CSS selector 'div.card' leaked into description")
        self.assertNotIn("span.badge", spec.description, "CSS selector 'span.badge' leaked into description")

    def test_pseudo_element_leakage(self):
        """Pseudo-elements like output::after leak because lookahead matches 'output:'."""
        raw_css = "output::after { content: ' '; position: absolute; }"
        cleaned = ProblemExtractor._clean_text(raw_css)
        self.assertEqual(cleaned.strip(), "", "output::after selector leaked into cleaned text")


class TestCSSSelectorsMatchingHTMLTags(unittest.TestCase):
    """Test CSS selectors matching input, output, textarea, form, button, body, html."""

    def test_bare_input_and_output_selectors_in_strategy_2(self):
        """Bare CSS rules matching 'input' and 'output' must not be confused with sample cases."""
        html = """
        <h1>Form Processor</h1>
        <p>Problem Statement: Process user form fields.</p>
        input {
            display: inline-flex;
            font-size: inherit;
            line-height: inherit;
            flex: 1;
        }
        output {
            display: block;
            margin: 10px;
        }
        <p>Sample Input:
        user_name
        </p>
        <p>Sample Output:
        USER_NAME
        </p>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1, "Bare input/output CSS rules falsely matched as sample cases")
        self.assertEqual(spec.sample_cases[0].input_text.strip(), "user_name")
        self.assertEqual(spec.sample_cases[0].expected_output.strip(), "USER_NAME")


class TestRealWorldCSSLeaks(unittest.TestCase):
    """Test real-world CSS leaks and sample case filtering."""

    def test_real_world_css_leak_dropping(self):
        """A sample input that is pure CSS should be dropped entirely, not preserved with empty input."""
        html = """
        <div class="problem-title">Real World Leak</div>
        <div class="problem-statement">Find maximum element.</div>
        <div class="sample-input">{display:inline-flex;font-size:inherit;line-height:inherit;flex:1}</div>
        <div class="sample-output">42</div>
        <div class="sample-input">1 5 3</div>
        <div class="sample-output">5</div>
        """
        spec = ProblemExtractor.extract(html)
        # If the first case's input was pure CSS leak, it should NOT be retained as SampleCase(input_text='', expected_output='42')
        self.assertEqual(len(spec.sample_cases), 1,
                         f"CSS leak was retained with empty input: {spec.sample_cases}")
        self.assertEqual(spec.sample_cases[0].input_text, "1 5 3")
        self.assertEqual(spec.sample_cases[0].expected_output, "5")


class TestLegitimateBracesPreservation(unittest.TestCase):
    """Test 100% preservation of valid JSON, Python dicts, Python sets, and code blocks."""

    def test_valid_json_with_css_property_names(self):
        """JSON containing 'display', 'flex', 'font' must be 100% preserved."""
        json_str = '{"name": "test", "display": "flex", "count": 42}'
        html = f"""
        <div class="problem-title">JSON Config</div>
        <div class="problem-statement">Parse the configuration.</div>
        <div class="sample-input">{json_str}</div>
        <div class="sample-output">flex</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text, json_str)
        self.assertEqual(spec.sample_cases[0].expected_output, "flex")

    def test_valid_python_dictionary_with_single_quotes(self):
        """Python dictionary with single quotes and CSS keywords must NOT be discarded."""
        dict_str = "{'display': 'inline', 'val': 100}"
        html = f"""
        <div class="problem-title">Python Dict Parsing</div>
        <div class="problem-statement">Extract val from dict string.</div>
        <div class="sample-input">{dict_str}</div>
        <div class="sample-output">100</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1,
                         "Legitimate Python dict with single quotes was discarded by _is_pure_css")
        self.assertEqual(spec.sample_cases[0].input_text, dict_str)
        self.assertEqual(spec.sample_cases[0].expected_output, "100")

    def test_valid_python_dict_outputs_with_common_properties(self):
        """Common competitive programming outputs formatted as Python dicts must NOT be discarded."""
        test_dicts = [
            "{'width': 10, 'height': 20}",
            "{'color': 'red', 'count': 5}",
            "{'position': (0, 0)}",
            "{'border': 1}",
            "{'margin': 5, 'padding': 10}",
        ]
        for d in test_dicts:
            with self.subTest(dict_str=d):
                html = f"""
                <div class="sample-input">input_val</div>
                <div class="sample-output">{d}</div>
                """
                spec = ProblemExtractor.extract(html)
                self.assertEqual(len(spec.sample_cases), 1,
                                 f"Sample case with dict output {d} was discarded by _is_pure_css")
                self.assertEqual(spec.sample_cases[0].expected_output, d)

    def test_valid_python_set(self):
        """Python sets like {1, 2, 3, 4} must be 100% preserved."""
        set_str = "{1, 2, 3, 4}"
        html = f"""
        <div class="sample-input">{set_str}</div>
        <div class="sample-output">4</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text, set_str)
        self.assertEqual(spec.sample_cases[0].expected_output, "4")

    def test_valid_python_set_of_css_keywords(self):
        """Python set of strings with single quotes like {'display', 'flex'} must NOT be discarded."""
        set_str = "{'display', 'flex', 'inline'}"
        html = f"""
        <div class="sample-input">{set_str}</div>
        <div class="sample-output">3</div>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1,
                         f"Python set with single quotes {set_str} was discarded by _is_pure_css")
        self.assertEqual(spec.sample_cases[0].input_text, set_str)

    def test_cpp_code_snippets_and_generics_preservation(self):
        """C++ code with generics, headers, or comparisons must not have angle brackets stripped."""
        cases = [
            ("comparison", "5 < 10 and 20 > 15", "True"),
            ("generics", "vector<int> nums", "int"),
            ("c_header", "#include <stdio.h>", "stdio.h"),
        ]
        for name, inp, out in cases:
            with self.subTest(case_name=name):
                # HTML entity encoded as received from Qwik SSR / Guvi DOM
                html = f"""
                <div class="sample-input">{inp.replace('<', '&lt;').replace('>', '&gt;')}</div>
                <div class="sample-output">{out}</div>
                """
                spec = ProblemExtractor.extract(html)
                self.assertEqual(len(spec.sample_cases), 1)
                self.assertEqual(spec.sample_cases[0].input_text, inp,
                                 f"Input {inp} was corrupted to {spec.sample_cases[0].input_text}")

    def test_multiline_matrix_preservation(self):
        """Multiline inputs with whitespace and newlines must preserve internal structure."""
        matrix_input = "3 3\n1 2 3\n4 5 6\n7 8 9"
        html = f"""
        <h1>Matrix Trace</h1>
        <p>Sample Input:
        {matrix_input}
        </p>
        <p>Sample Output:
        15
        </p>
        """
        spec = ProblemExtractor.extract(html)
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text.strip(), matrix_input)
        self.assertEqual(spec.sample_cases[0].expected_output.strip(), "15")


if __name__ == "__main__":
    unittest.main(verbosity=2)
