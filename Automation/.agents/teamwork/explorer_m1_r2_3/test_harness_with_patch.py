import sys
import os
import unittest

WORKSPACE_DIR = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

import solver.extractor as ext

# Save original methods/attributes if needed
orig_clean_text = ext.ProblemExtractor._clean_text
orig_extract_sample_cases = ext.ProblemExtractor._extract_sample_cases

# Apply proposed fixes to ProblemExtractor dynamically
import re
import html

ext.ProblemExtractor._CSS_AT_RULE_RE = re.compile(
    r"(?:@(?:media|keyframes|-webkit-keyframes|supports|container)\b[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\s*\}|@[a-z\-]+[^;{]*;?)",
    re.IGNORECASE | re.DOTALL,
)

ext.ProblemExtractor._CSS_RULE_RE = re.compile(
    rf"(?:^|\n)\s*(?![^\{{\n]*(?:Sample|Case|Input\s*[:\-](?!\:)|Output\s*[:\-](?!\:)|Description|Problem))"
    rf"(?:[.#a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]+?(?:::[a-z\-]+|:[a-z\-]+(?:\([^\)]*\))?)*)\s*"
    rf"\{{[^{{}}]*?(?:(?<![\"\'\w-]){ext.ProblemExtractor._CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\b|\}}))[^{{}}]*?\}}",
    re.IGNORECASE | re.DOTALL,
)

@classmethod
def patched_is_pure_css(cls, text: str) -> bool:
    if not text:
        return False
    t = re.sub(r"<[^>]+>", " ", text).strip()
    if not t:
        return False
    if t.startswith("{") and t.endswith("}"):
        try:
            import ast
            val = ast.literal_eval(t)
            if isinstance(val, (dict, set, list, tuple)):
                return False
        except Exception:
            pass
        try:
            import json
            val = json.loads(t)
            if isinstance(val, (dict, list)):
                return False
        except Exception:
            pass

    if t.startswith("{") and re.search(cls._CSS_PROP_PATTERN + r"\s*:", t, re.IGNORECASE):
        if not re.search(r"""^\s*\{\s*["']""", t):
            return True
    if cls._CSS_RULE_RE.search(t):
        return True
    return False

ext.ProblemExtractor._is_pure_css = patched_is_pure_css

@classmethod
def patched_clean_text(cls, raw_html: str, preserve_newlines: bool = False) -> str:
    if not raw_html:
        return ""
    # Include HTML5 semantic tags in lookahead
    text = re.sub(
        r"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?(?:</\s*\1\s*>|(?=<(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li|section|article|main|aside|header|footer|nav)\b)|$)",
        " ",
        raw_html,
    )
    text = re.sub(r"(?s)<!--.*?-->", "", text)
    text = re.sub(r"(?s)/\*.*?\*/", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</?(p|div|h[1-6]|tr|li|pre|blockquote)[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
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
                prev_empty = True
        return "\n".join(cleaned_lines).strip()
    else:
        return " ".join(text.split()).strip()

ext.ProblemExtractor._clean_text = patched_clean_text

@classmethod
def patched_extract_sample_cases(cls, html_text: str):
    def _filter_and_renumber(cases_to_clean):
        out = []
        for case in cases_to_clean:
            if cls._is_pure_css(case.input_text) or cls._is_pure_css(case.expected_output):
                continue

            clean_in = cls._sanitize_css(case.input_text).strip()
            clean_out = cls._sanitize_css(case.expected_output).strip()
            # REMOVED redundant lines 459-460:
            # clean_in = re.sub(r"<[^>]+>", "", clean_in).strip()
            # clean_out = re.sub(r"<[^>]+>", "", clean_out).strip()

            if not clean_in and not clean_out:
                continue
            if case.input_text.strip() and not clean_in:
                continue
            if case.expected_output.strip() and not clean_out:
                continue
            if cls._is_pure_css(clean_in) or cls._is_pure_css(clean_out):
                continue

            out.append(ext.SampleCase(
                input_text=clean_in,
                expected_output=clean_out,
                case_number=len(out) + 1,
                explanation=case.explanation,
            ))
        return out

    inputs_m = re.findall(r'class=["\'][^"\']*sample-input[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)
    outputs_m = re.findall(r'class=["\'][^"\']*sample-output[^"\']*["\'][^>]*>(.*?)</div>', html_text, re.IGNORECASE | re.DOTALL)

    raw_cases = []
    if inputs_m and outputs_m:
        for idx, (in_raw, out_raw) in enumerate(zip(inputs_m, outputs_m), start=1):
            if cls._is_pure_css(in_raw) or cls._is_pure_css(out_raw):
                continue
            clean_in = cls._clean_text(in_raw, preserve_newlines=True)
            clean_out = cls._clean_text(out_raw, preserve_newlines=True)
            if in_raw.strip() and not clean_in:
                continue
            if out_raw.strip() and not clean_out:
                continue
            raw_cases.append(ext.SampleCase(
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
            if in_raw.strip() and not clean_in:
                continue
            raw_cases.append(ext.SampleCase(
                input_text=clean_in,
                expected_output="",
                case_number=idx,
            ))
        valid = _filter_and_renumber(raw_cases)
        if valid:
            return valid

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
        r"(?=(?:\n\s*(?:Sample\s+)?Input\b)|(?:\n\s*Constraints)|(?:\n\s*Accepted\b)|(?:\n\s*Topics\b)|(?:\n\s*Code\s+Editor)|$)",
        re.DOTALL | re.IGNORECASE,
    )

    matches = list(sample_pattern.finditer(text_for_samples))
    raw_cases = []
    if matches:
        for idx, m in enumerate(matches, start=1):
            inp = m.group("input").strip()
            out = m.group("output").strip()
            exp = m.group("explanation").strip() if m.group("explanation") else None
            raw_cases.append(ext.SampleCase(
                input_text=inp,
                expected_output=out,
                case_number=idx,
                explanation=exp,
            ))

    return _filter_and_renumber(raw_cases)

ext.ProblemExtractor._extract_sample_cases = patched_extract_sample_cases

# Now run the Challenger 2 stress test harness
import importlib.util
harness_path = "/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2/stress_test_harness.py"
spec = importlib.util.spec_from_file_location("stress_test_harness", harness_path)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(harness)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
print("ALL 14 ADVERSARIAL STRESS TESTS PASSED SUCCESSFULLY!")
