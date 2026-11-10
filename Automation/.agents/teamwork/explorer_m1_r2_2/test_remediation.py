#!/usr/bin/env python3
"""
Test remediation script for Explorer 2 (Milestone 1 Iteration 2).
Monkeys-patches the proposed logic onto ProblemExtractor in memory
and runs the full 14-test adversarial suite from Challenger 2's stress_test_harness.py,
as well as the project's existing tests in tests/test_m1_filtering.py.
"""

import sys
import os
import unittest
import re
import ast
import json
from typing import Any

WORKSPACE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

from solver.extractor import ProblemExtractor, ProblemSpecification, SampleCase
import solver.extractor as extractor_module

# --- Proposed Formulations ---

_CODE_INDICATORS_RE = re.compile(
    r"\b(?:int|float|double|char|long|short|void|bool|boolean|auto|let|const|var|"
    r"def|return|if|else|for|while|do|switch|case|break|continue|struct|class|"
    r"public|private|protected|namespace|fn|fun|function|import|package|include|"
    r"printf|scanf|cout|cin|print)\b|"
    r"[=+\-*/%&|!<>]=|&&|\|\||->|==|!=|\b[a-zA-Z_]\w*\s*=[^=]",
    re.IGNORECASE,
)

_CSS_PROP_DECL_RE = re.compile(
    rf"(?<![\"\'\w-]){ProblemExtractor._CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\s*|\}}|$)",
    re.IGNORECASE,
)

_CSS_AT_RULE_RE = re.compile(
    r"(?:@(?:media|keyframes|-webkit-keyframes)[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\s*\}|@[a-z\-]+[^;{]*;?)",
    re.IGNORECASE | re.DOTALL,
)

_CSS_RULE_RE = re.compile(
    rf"(?:^|\n)\s*(?![^\{{\n]*(?:Sample|Case|Input\s*[:\-](?!\:)|Output\s*[:\-](?!\:)|Description|Problem))"
    rf"(?:[.#]?[.#a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]+?(?:::[a-z\-]+|:[a-z\-]+(?:\([^\)]*\))?)?)\s*"
    rf"\{{[^{{}}]*?(?:(?<![\"\'\w-]){ProblemExtractor._CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\b|\}}))[^{{}}]*?\}}",
    re.IGNORECASE | re.DOTALL,
)

def proposed_is_pure_css(cls, text: str) -> bool:
    """Detects if a string is pure CSS declaration block or stylesheet rule."""
    if not text:
        return False
    t = text.strip()
    if not t:
        return False

    # 1. Distinguish valid Python literals (dicts, sets, lists, tuples)
    try:
        val = ast.literal_eval(t)
        if isinstance(val, (dict, set, list, tuple, int, float, bool)):
            return False
    except (ValueError, SyntaxError, MemoryError):
        pass

    # 2. Distinguish valid JSON
    try:
        jval = json.loads(t)
        if isinstance(jval, (dict, list, int, float, bool)):
            return False
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # 3. Distinguish programming code statements (keywords, assignments, returns)
    if _CODE_INDICATORS_RE.search(t):
        return False

    # 4. Check CSS at-rules (@media, @keyframes)
    if t.startswith("@") and cls._CSS_AT_RULE_RE.search(t):
        return True

    # 5. Check CSS declaration block: starts with { and ends with }
    if t.startswith("{") and t.endswith("}"):
        inner = t[1:-1].strip()
        if not inner:
            return False
        if _CSS_PROP_DECL_RE.search(inner):
            return True

    # 6. Check bare CSS declarations (e.g. 'display:inline-flex;font-size:inherit;')
    if _CSS_PROP_DECL_RE.search(t) and not re.search(r"[\"\'=]", t):
        decls = [d.strip() for d in t.split(";") if d.strip()]
        if decls and all(_CSS_PROP_DECL_RE.search(d) for d in decls):
            return True

    # 7. Check full CSS rule set with selector
    if cls._CSS_RULE_RE.search(t):
        return True

    return False

def proposed_clean_text(cls, raw_html: str, preserve_newlines: bool = False) -> str:
    """Sanitizes HTML content into clean readable text."""
    if not raw_html:
        return ""
    import html as html_module
    # Strip script, style, noscript, svg, template blocks even with malformed or spaced closing tags or unclosed tags
    text = re.sub(
        r"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?(?:</\s*\1\s*>|(?=<(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li|section|article|main|aside|header|footer)\b)|$)",
        " ",
        raw_html,
    )
    # Strip HTML comments
    text = re.sub(r"(?s)<!--.*?-->", "", text)
    # Strip CSS comments (/* ... */) that may have leaked
    text = re.sub(r"(?s)/\*.*?\*/", " ", text)
    # Replace line-breaking HTML elements with newlines
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</?(p|div|h[1-6]|tr|li|pre|blockquote)[^>]*>", "\n", text)
    # Strip all other HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode HTML entities (&quot;, &lt;, &gt;, &amp;, &#39;, &nbsp;, etc.)
    text = html_module.unescape(text)
    # Sanitize any residual CSS
    text = cls._sanitize_css(text)

    if preserve_newlines:
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if line:
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty and cleaned_lines:
                cleaned_lines.append("")
        return "\n".join(cleaned_lines)

    return " ".join(text.split())

def proposed_extract_sample_cases(cls, html_text: str, page: Any = None) -> list:
    def _filter_and_renumber(cases_to_clean: list) -> list:
        out = []
        for case in cases_to_clean:
            clean_in = cls._sanitize_css(case.input_text).strip()
            clean_out = cls._sanitize_css(case.expected_output).strip()

            if not clean_in and not clean_out:
                continue
            if cls._is_pure_css(case.input_text) or cls._is_pure_css(case.expected_output):
                continue

            out.append(SampleCase(
                input_text=clean_in,
                expected_output=clean_out,
                case_number=len(out) + 1,
                explanation=case.explanation,
            ))
        return out

    # Strategy 1: DOM Class Selectors (.sample-input and .sample-output)
    inputs_m = re.findall(r'class=["\'][^"\']*sample-input[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
    outputs_m = re.findall(r'class=["\'][^"\']*sample-output[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)

    raw_cases = []
    if inputs_m and outputs_m:
        for idx, (in_raw, out_raw) in enumerate(zip(inputs_m, outputs_m), start=1):
            if cls._is_pure_css(in_raw) or cls._is_pure_css(out_raw):
                continue
            clean_in = cls._clean_text(in_raw, preserve_newlines=True)
            clean_out = cls._clean_text(out_raw, preserve_newlines=True)
            raw_cases.append(SampleCase(
                input_text=clean_in,
                expected_output=clean_out,
                case_number=idx,
            ))
        valid = _filter_and_renumber(raw_cases)
        if valid:
            return valid

    if inputs_m and not outputs_m:
        for idx, in_raw in enumerate(inputs_m, start=1):
            if cls._is_pure_css(in_raw):
                continue
            clean_in = cls._clean_text(in_raw, preserve_newlines=True)
            raw_cases.append(SampleCase(
                input_text=clean_in,
                expected_output="",
                case_number=idx,
            ))
        valid = _filter_and_renumber(raw_cases)
        if valid:
            return valid

    # Strategy 2: Labeled Text Pattern Matching
    text = cls._clean_text(html_text, preserve_newlines=True)
    text_for_samples = re.split(
        r"\n\s*(?:Accepted\b|Acceptance\s+Rate\b|Code\s+Editor\b|Are\s+you\s+sure\s+you\s+want\s+to\s+reset)",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    sample_pattern = re.compile(
        r"(?:^|\n)\s*(?P<in_label>(?:Sample\s+Input\s*(?:Case\s*\d+)?\s*[:\-]?)|(?:Input\s*(?:Case\s*\d+)?\s*[:\-])|(?:Input\s*(?:Case\s*\d+)?(?=\n)(?!\s*\{)))\s*\n?"
        r"(?P<input>.*?)\s*"
        r"(?:^|\n)\s*(?P<out_label>(?:Sample\s+Output\s*(?:Case\s*\d+)?\s*[:\-]?)|(?:Output\s*(?:Case\s*\d+)?\s*[:\-])|(?:Output\s*(?:Case\s*\d+)?(?=\n)(?!\s*\{)))\s*\n?"
        r"(?P<output>.*?)\s*"
        r"(?:(?:\n\s*|\A)(?:Sample\s+)?Explanation\s*(?:Case\s*)?(?:\d+)?\s*[:\-]?\s*(?P<explanation>.*?))?"
        r"(?=(?:\n\s*(?:Sample\s+Input|Input\s*(?:Case\s*\d+)?\s*[:\-]|Accepted\b|Code\s+Editor\b))|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    matches = list(sample_pattern.finditer(text_for_samples))
    for idx, match in enumerate(matches, start=1):
        raw_in = match.group("input").strip()
        raw_out = match.group("output").strip()
        raw_exp = match.group("explanation")
        exp = raw_exp.strip() if raw_exp else None

        raw_cases.append(SampleCase(
            input_text=raw_in,
            expected_output=raw_out,
            case_number=idx,
            explanation=exp,
        ))

    valid = _filter_and_renumber(raw_cases)
    if valid:
        return valid

    return []

# Apply monkey patch
ProblemExtractor._CSS_AT_RULE_RE = _CSS_AT_RULE_RE
ProblemExtractor._CSS_RULE_RE = _CSS_RULE_RE
ProblemExtractor._is_pure_css = classmethod(proposed_is_pure_css)
ProblemExtractor._clean_text = classmethod(proposed_clean_text)
ProblemExtractor._extract_sample_cases = classmethod(proposed_extract_sample_cases)

# Now import challenger_m1_2's test suite and run it!
sys.path.insert(0, "/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2")
import stress_test_harness

loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(stress_test_harness)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print("\n" + "="*50)
print(f"Tests run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
if result.wasSuccessful():
    print("ALL ADVERSARIAL STRESS TESTS PASSED SUCCESSFULLY!")
else:
    print("SOME TESTS STILL FAILED.")
    sys.exit(1)
