# Handoff Report: Problem Statement Extraction, CSS Leakage Root Cause & Sanitization Architecture

- **Agent**: Explorer 2 (Milestone 1: Filtering & Extractor Foundation)
- **Role**: Investigator & Synthesizer
- **Target Project**: `zenclass_guvi` (`/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`)
- **Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`
- **State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_2`
- **Handoff Type**: Hard (Self-Contained Investigation Complete)

---

## 1. Observation

### Observation 1.1: Live Production Failure Records in SQLite Database
Inspecting the persistent SQLite database at `zenclass_guvi/data/automation_state.db` revealed real-world task failures caused by CSS pollution:
- **Command**:
  ```bash
  sqlite3 data/automation_state.db "SELECT task_id, failure_reason FROM task_attempts WHERE status='FAILED';"
  ```
- **Verbatim Output**:
  ```
  guvi-97|Traceback (most recent call last):
    File "<string>", line 28, in <module>
    File "<string>", line 20, in solve
  ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'
  guvi-37|Traceback (most recent call last):
    File "<string>", line 28, in <module>
    File "<string>", line 20, in solve
  ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'
  guvi-48|Traceback (most recent call last):
    File "<string>", line 28, in <module>
    File "<string>", line 20, in solve
  ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'
  guvi-15|Traceback (most recent call last):
    File "<string>", line 28, in <module>
    File "<string>", line 20, in solve
  ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'
  guvi-prime-number-check|Traceback (most recent call last):
    File "<string>", line 28, in <module>
    File "<string>", line 24, in solve
  ValueError: invalid literal for int() with base 10: '/'
  ```
- **Inspecting Task Attempt Code Snapshot for `guvi-97`**:
  ```python
  def solve():
      tokens = sys.stdin.read().split()
      if len(tokens) >= 2:
          l, r = int(tokens[0]), int(tokens[1])
          count = sum(1 for x in range(l, r + 1) if is_prime(x))
          print(count)
      elif len(tokens) == 1:
          n = int(tokens[0])
          print('yes' if is_prime(n) else 'no')
  ```
- **Root Symptom**: `sys.stdin.read().split()[0]` was passed `{display:inline-flex;font-size:inherit;line-height:inherit;flex:1` because `spec.sample_cases[0].input_text` contained this CSS string instead of the actual test input.

---

### Observation 1.2: Current Extraction Architecture in `solver/extractor.py`
Examining `solver/extractor.py` (lines 143–204, 206–236, 377–447):
1. **Source Resolution (`extractor.py:151-166`)**:
   ```python
   if isinstance(source, str):
       html_text = source
   elif hasattr(source, "content") and callable(getattr(source, "content")):
       page = source
       try:
           html_text = source.content()
       except Exception as e:
           logger.warning("Failed to obtain HTML via page.content(): %s", e)
           html_text = ""
   else:
       html_text = str(source)
   ```
   When extracting from a live Playwright `Page`, `source.content()` dumps the full serialized DOM of the workspace, including inline stylesheets injected by Ace Editor, Qwik SSR scoped styling, and modals.

2. **Text Cleaning Defect in `_clean_text` (`extractor.py:211-220`)**:
   ```python
   # Strip script, style, noscript, svg blocks and HTML comments completely
   text = re.sub(r"(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1>", " ", raw_html)
   text = re.sub(r"(?s)<!--.*?-->", "", text)
   # Replace line-breaking HTML elements with newlines
   text = re.sub(r"(?i)<br\s*/?>", "\n", text)
   text = re.sub(r"(?i)</?(p|div|h[1-6]|tr|li|pre|blockquote)[^>]*>", "\n", text)
   # Strip all other HTML tags
   text = re.sub(r"<[^>]+>", " ", text)
   # Decode HTML entities (&quot;, &lt;, &gt;, &amp;, &#39;, &nbsp;, etc.)
   text = html.unescape(text)
   ```
   - **Defect A (Closing Tag Variation)**: `</\1>` strictly requires `</style>` with zero spaces. Valid HTML closing tags with whitespace (`</style >`, `</ style>`, `</style\n>`) fail to match and remain completely unstripped.
   - **Defect B (Unclosed `<style>`)**: Unclosed or dynamically injected style tags fail to match `.*?</\1>` and leak into text.
   - **Defect C (Omitted `<template>`)**: `<template>` tags containing scoped styles or markup are not stripped.
   - **Defect D (Missing CSS Comment Stripping)**: `/* ... */` CSS comments are never stripped (only HTML comments `<!-- ... -->` are stripped). This caused the `ValueError: invalid literal for int() with base 10: '/'` error in `guvi-prime-number-check`.

3. **Pattern Matching False-Positive Defect in Strategy 2 (`extractor.py:423-431`)**:
   ```python
   sample_pattern = re.compile(
       r"(?:^|\n)\s*(?:(?:Sample\s+Input)|(?:Input(?!\s*(?:Description|Specification|Format|Size))))\s*(?:Case\s*)?(?P<num>\d+)?\s*[:\-]?\s*\n?"
       r"(?P<input>.*?)\s*"
       r"(?:^|\n)\s*(?:(?:Sample\s+Output)|(?:Output(?!\s*(?:Description|Specification|Format))))\s*(?:Case\s*)?(?P=num)?\s*[:\-]?\s*\n?"
       r"(?P<output>.*?)\s*"
       r"(?:(?:\n\s*|\A)(?:Sample\s+)?Explanation\s*(?:Case\s*)?(?:\d+)?\s*[:\-]?\s*(?P<explanation>.*?))?"
       r"(?=(?:\n\s*(?:Sample\s+)?Input(?!\s*(?:Description|Specification|Format|Size))\s*(?:Case\s*)?\d*\s*[:\-])|(?:\n\s*Constraints)|(?:\n\s*Accepted\b)|(?:\n\s*Topics\b)|(?:\n\s*Code\s+Editor)|$)",
       re.DOTALL | re.IGNORECASE
   )
   ```
   - In CSS stylesheets, `input` and `output` are standard HTML element selectors.
   - For example:
     ```css
     input {display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}
     output {display:block;}
     ```
   - Because `[:\-]` and `\n` are optional (`[:\-]?\s*\n?`), `input` matches `(?:Input(?!\s*(?:Description...)))`.
   - `(?P<input>.*?)` matches `{display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}`.
   - `output` matches `(?:Output(?!\s*(?:Description...)))`.
   - `(?P<output>.*?)` matches `{display:block;}`.
   - This constructs a completely fabricated `SampleCase(input_text='{display:inline-flex...}', expected_output='{display:block;}', case_number=1)`!

4. **Zero Post-Extraction Validation (`extractor.py:392-447`)**:
   Neither Strategy 1 nor Strategy 2 validates or sanitizes extracted `SampleCase.input_text` or `SampleCase.expected_output`. Bogus CSS cases are returned as `spec.sample_cases[0]`.

---

### Observation 1.3: Empirical Reproduction of the Defect
Running an empirical reproduction script:
```python
html_with_css_and_real = """
<div>
  <p>Problem Statement: Given N, check prime.</p>
  input {display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}
  output {display:block;}
  <p>Sample Input: 5</p>
  <p>Sample Output: yes</p>
</div>
"""
spec = ProblemExtractor.extract(html_with_css_and_real)
```
- **Output**:
  ```
  Found cases count: 2
  Case 1: input='{display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}', output='{display:block;}'
  Case 2: input='5', output='yes'
  ```
- **Result**:
  `spec.sample_input` (which aliases `sample_cases[0].input_text`) returned `'{display:inline-flex;font-size:inherit;line-height:inherit;flex:1;}'`.
  When `solver/test_runner.py:test_solution()` executed the candidate code against `spec.sample_cases[0]`, the subprocess failed immediately with:
  `ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'`

---

### Observation 1.4: Existing Extractor Test Coverage
- **File**: `tests/test_m2_solver.py` (lines 141–221):
  Contains `TestProblemExtractor` with 6 test cases:
  1. `test_extract_from_full_workspace_html`: Tests static fixture `GUVI_WORKSPACE_HTML`.
  2. `test_extract_sparse_html_fallback`: Tests sparse HTML snippet.
  3. `test_extract_empty_and_none`: Tests `""`, `None`, and whitespace.
  4. `test_extract_labeled_text_headings`: Tests standard labeled headings.
  5. `test_extract_multiline_sample_io`: Tests multiline inputs.
  6. `test_extract_from_playwright_page_mock`: Tests mock Playwright page content.
- **File**: `tests/e2e/tier1_features/test_f05_extractor.py` (lines 11–40):
  Contains `TestFeature05ProblemExtractor` with 2 tests verifying fields and missing sections.
- **Current Test Suite Baseline**:
  - Command: `/Users/devesh/Library/Python/3.9/bin/pytest /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests -q`
  - Result: `268 passed in 69.39s (0:01:09)`
- **Test Gap**: Currently **ZERO** tests in the test suite verify CSS sanitization, unclosed/spaced style tags, CSS comments, or preservation of legitimate JSON, dicts, and set inputs.

---

## 2. Logic Chain

1. **Step 1: Identifying the Crash Vector**:
   - Observations 1.1 and 1.3 show that tasks `guvi-97`, `guvi-37`, `guvi-48`, `guvi-15` crashed with `ValueError: invalid literal for int() with base 10: '{display:inline-flex;font-size:inherit;line-height:inherit;flex:1'`.
   - The string passed to `sys.stdin` originated from `spec.sample_cases[0].input_text`.
   - Therefore, the problem extractor is generating test cases containing CSS declaration blocks.

2. **Step 2: Tracing Why CSS Escaped HTML Cleaning**:
   - Observation 1.2 demonstrates that `_clean_text` uses `re.sub(r"(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1>", " ", raw_html)`.
   - This regex fails when `<style>` tags have attributes or closing tags containing whitespace (`</style >`, `</ style>`), when tags are unclosed, when CSS comments `/* ... */` are present, or when CSS rules are rendered into text nodes by modern UI frameworks (Qwik/Tailwind/Ace Editor).

3. **Step 3: Tracing Why CSS Was Interpreted as a Test Case**:
   - Observation 1.2 and 1.3 show that Strategy 2's regex (`sample_pattern`) matches `input` and `output` element selectors case-insensitively without requiring a colon or newline.
   - When `input {display:...}` and `output {...}` appear in text, `sample_pattern` captures `{display:...}` as `sample_input`.
   - The fake CSS case is placed at index 0 of `sample_cases`, displacing legitimate test cases and causing immediate failure in the local sandbox test runner.

4. **Step 4: Designing Safe Sanitization Without Corrupting Legitimate Inputs**:
   - A naive regex that strips all `{...}` would destroy legitimate competitive programming inputs/outputs (e.g. JSON `{"display": "inline-flex"}`, Python dicts `{'key': 'value'}`, sets `{1, 2, 3}`, or C code blocks `{ int x = 0; }`).
   - Legitimate JSON features quoted keys: `(?<!["'\w-])"property":`.
   - Legitimate Python dicts feature quoted keys: `(?<!["'\w-])'property':`.
   - Legitimate sets and C code blocks do not contain unquoted CSS property names (`display:`, `font-size:`, `line-height:`, `flex:`, `margin:`, `padding:`, `border:`, etc.) followed by CSS values.
   - By requiring unquoted CSS property names preceded by non-word and non-quote boundaries (`(?<!["'\w-])(?:display|position|flex|margin|padding|color|background|font|font-size|line-height|border|width|height|z-index|overflow|opacity|visibility|align-items|justify-content|box-sizing)\s*:`), we can precisely eliminate CSS declaration blocks and rules while leaving JSON, sets, and code completely intact.

5. **Step 5: Enforcing Defense-in-Depth**:
   - Fixing `_clean_text` prevents `<style>` leaks.
   - Adding `_sanitize_css()` removes residual CSS declaration blocks, CSS rules, at-rules (`@media`), and CSS comments (`/* ... */`) from text.
   - Tightening `sample_pattern` prevents bare `input` and `output` CSS selectors from triggering test case extraction.
   - Adding post-extraction validation discards purely bogus CSS cases and renumbers valid cases.

---

## 3. Caveats

1. **Read-Only Investigation**: As Explorer 2, no code or test files in `zenclass_guvi/` were modified. Complete proposed implementations and tests are documented herein for the implementer (Worker M1).
2. **Platform CSS Diversity**: Guvi CodeKata dynamically updates frontend bundles (Qwik SSR, Ace Editor, KaTeX). The proposed sanitization addresses all standard CSS properties and rules, but should be verified against new live CodeKata pages as they are encountered.
3. **No LLM Fallback in Extractor**: The extractor relies entirely on deterministic DOM parsing, semantic headings, and regex sanitization. It does not invoke external LLM APIs for parsing.

---

## 4. Conclusion & Concrete Recommendations

### 4.1 Recommended Code Changes for `solver/extractor.py`

#### Change 1: Robust HTML Tag & Comment Sanitization in `_clean_text`
Replace lines 211–212 in `solver/extractor.py`:
```python
# Before:
text = re.sub(r"(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1>", " ", raw_html)
text = re.sub(r"(?s)<!--.*?-->", "", text)

# After:
# Strip script, style, noscript, svg, template blocks even with malformed or spaced closing tags or unclosed tags
text = re.sub(r"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?(?:</\s*\1\s*>|$)", " ", raw_html)
# Strip HTML comments
text = re.sub(r"(?s)<!--.*?-->", "", text)
# Strip CSS comments (/* ... */) that may have leaked
text = re.sub(r"(?s)/\*.*?\*/", " ", text)
```

#### Change 2: CSS Sanitization Function `_sanitize_css`
Add a dedicated CSS cleaning method in `ProblemExtractor`:
```python
# Canonical list of CSS properties used to detect unquoted CSS declaration blocks
_CSS_PROP_PATTERN = (
    r"(?:display|position|flex|margin|padding|color|background|font|font-size|"
    r"font-family|line-height|border|width|height|z-index|overflow|opacity|"
    r"visibility|align-items|justify-content|box-sizing|cursor|outline|"
    r"pointer-events|transition|transform|animation|white-space|text-align|"
    r"vertical-align|user-select)"
)

# Matches CSS at-rules (@media, @import, @keyframes)
_CSS_AT_RULE_RE = re.compile(
    r"(?:@media[^{]*\{[^{}]*\{[^{}]*\}\s*\}|@[a-z\-]+[^;{]*;?)",
    re.IGNORECASE | re.DOTALL
)

# Matches CSS rule sets with selectors: e.g. input { display: inline-flex; }
_CSS_RULE_RE = re.compile(
    rf"(?:^|\n)\s*(?:[.#]?[a-zA-Z0-9_\-:\s,>+~\[\]\=\"\']+?)\s*"
    rf"\{{[^{{}}]*?(?:(?<![\"\'\w-]){_CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\b|\}}))[^{{}}]*?\}}",
    re.IGNORECASE | re.DOTALL
)

# Matches standalone CSS declaration blocks: e.g. {display:inline-flex;font-size:inherit;}
# Safeguard: requires unquoted CSS properties, preserving legitimate JSON ('{"display": "inline-flex"}'),
# Python dicts, sets ({1, 2, 3}), and code blocks ({ int x = 0; }).
_CSS_DECL_BLOCK_RE = re.compile(
    rf"\{{[^{{}}]*?(?:(?<![\"\'\w-]){_CSS_PROP_PATTERN}\s*:\s*[^;{{}}]+(?:;|\b|\}}))[^{{}}]*?\}}",
    re.IGNORECASE | re.DOTALL
)

@classmethod
def _sanitize_css(cls, text: str) -> str:
    """Removes CSS at-rules, rule sets, and unquoted CSS declaration blocks."""
    if not text:
        return ""
    # Strip CSS comments
    text = re.sub(r"(?s)/\*.*?\*/", " ", text)
    # Strip at-rules
    text = cls._CSS_AT_RULE_RE.sub(" ", text)
    # Strip selector rule blocks
    text = cls._CSS_RULE_RE.sub(" ", text)
    # Strip standalone declaration blocks
    text = cls._CSS_DECL_BLOCK_RE.sub(" ", text)
    return text
```

Call `_sanitize_css` inside `_clean_text`, and when extracting `description`, `input_spec`, `output_spec`, and `constraints`.

#### Change 3: Tighter `sample_pattern` Matching in Strategy 2
Update lines 423–431 in `solver/extractor.py`:
```python
sample_pattern = re.compile(
    r"(?:^|\n)\s*(?P<in_label>(?:Sample\s+Input\s*(?:Case\s*\d+)?\s*[:\-]?)|(?:Input\s*(?:Case\s*\d+)?\s*[:\-])|(?:Input\s*(?:Case\s*\d+)?(?=\n)(?!\s*\{)))\s*\n?"
    r"(?P<input>.*?)\s*"
    r"(?:^|\n)\s*(?P<out_label>(?:Sample\s+Output\s*(?:Case\s*\d+)?\s*[:\-]?)|(?:Output\s*(?:Case\s*\d+)?\s*[:\-])|(?:Output\s*(?:Case\s*\d+)?(?=\n)(?!\s*\{)))\s*\n?"
    r"(?P<output>.*?)\s*"
    r"(?:(?:\n\s*|\A)(?:Sample\s+)?Explanation\s*(?:Case\s*)?(?:\d+)?\s*[:\-]?\s*(?P<explanation>.*?))?"
    r"(?=(?:\n\s*(?:Sample\s+)?Input\b)|(?:\n\s*Constraints)|(?:\n\s*Accepted\b)|(?:\n\s*Topics\b)|(?:\n\s*Code\s+Editor)|$)",
    re.DOTALL | re.IGNORECASE
)
```
*Rationale*: If the label is just `Input` or `Output` (without `Sample`), it **must** be followed by a colon/dash `[:\-]` or a newline, and **must not** be followed by `{`. This completely prevents CSS selectors (`input { ... }`) from triggering.

#### Change 4: Post-Extraction Case Sanitization and Filtering
In `_extract_sample_cases`, after collecting cases from Strategy 1 or Strategy 2, sanitize and validate each case:
```python
valid_cases: List[SampleCase] = []
for case in raw_cases:
    # 1. Clean CSS noise from input and output
    clean_in = cls._sanitize_css(case.input_text).strip()
    clean_out = cls._sanitize_css(case.expected_output).strip()
    # Strip any leftover HTML tags
    clean_in = re.sub(r"<[^>]+>", "", clean_in).strip()
    clean_out = re.sub(r"<[^>]+>", "", clean_out).strip()

    # 2. Skip bogus cases that only contained CSS
    if not clean_in and not clean_out:
        continue
    if cls._is_pure_css(case.input_text):
        continue

    valid_cases.append(SampleCase(
        input_text=clean_in,
        expected_output=clean_out,
        case_number=len(valid_cases) + 1,
        explanation=case.explanation,
    ))
return valid_cases
```

Helper `_is_pure_css(text: str) -> bool`:
```python
@classmethod
def _is_pure_css(cls, text: str) -> bool:
    """Detects if a string is pure CSS declaration block or stylesheet rule."""
    if not text:
        return False
    t = text.strip()
    # If text starts with '{' and contains display/flex/font-size and ends with '}'
    if t.startswith("{") and re.search(cls._CSS_PROP_PATTERN, t, re.IGNORECASE):
        # Ensure it's not valid JSON
        if not re.search(r'^\s*\{\s*"', t):
            return True
    return False
```

---

### 4.2 Recommended Test Suite Additions
Add the following dedicated unit tests (in `tests/test_m1_filtering.py` or `tests/test_extractor.py`):

1. **`test_extract_sanitizes_unclosed_and_spaced_style_tags`**:
   - Inputs HTML with `<style type="text/css"> ... </style >`, `<style> ... </ style>`, and unclosed `<style>`.
   - Asserts zero style rules leak into `raw_text` or `description`.
2. **`test_extract_sanitizes_css_declaration_block_in_sample_input`**:
   - Inputs HTML where sample input has `{display:inline-flex;font-size:inherit;line-height:inherit;flex:1}\n9 2`.
   - Asserts `spec.sample_input == "9 2"`.
3. **`test_extract_ignores_css_input_output_selectors`**:
   - Inputs HTML containing `input {display:inline-flex;} output {display:block;}` followed by `Sample Input: 5\nSample Output: yes`.
   - Asserts `len(spec.sample_cases) == 1`, `spec.sample_input == "5"`, `spec.sample_output == "yes"`.
4. **`test_extract_preserves_legitimate_json_and_sets`**:
   - Inputs problem where Sample Input is JSON `{"display": "inline-flex", "count": 2}` and Sample Output is `{1, 2, 3}`.
   - Asserts `spec.sample_input == '{"display": "inline-flex", "count": 2}'` and `spec.sample_output == '{1, 2, 3}'`.
5. **`test_extract_sanitizes_css_comments`**:
   - Inputs problem containing `/* css comment */` before input.
   - Asserts no stray `/` or `*` appears in `sample_input`.
6. **`test_extract_multi_case_with_bogus_css_first`**:
   - Verifies that when a bogus CSS case precedes legitimate cases, the bogus case is discarded and the remaining cases are renumbered starting at 1.

---

## 5. Verification Method

To independently verify all findings and test proposals:

1. **Inspect Live Database Failure Records**:
   ```bash
   sqlite3 /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/data/automation_state.db \
     "SELECT task_id, failure_reason FROM task_attempts WHERE status='FAILED' AND failure_reason LIKE '%display:inline-flex%';"
   ```
2. **Verify Regex Flaw with Python One-Liner**:
   ```bash
   python3 -c "
   import re
   raw = '<style>input {display:inline-flex;}</style >'
   print('Current regex fails to strip:', repr(re.sub(r'(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1>', ' ', raw)))
   "
   ```
3. **Verify Empirical Bug Reproduction**:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi')
   from solver.extractor import ProblemExtractor
   html = 'input {display:inline-flex;flex:1}\noutput {color:red}\nSample Input: 5\nSample Output: yes'
   spec = ProblemExtractor.extract(html)
   print('Bogus Case 1:', spec.sample_cases[0].input_text)
   "
   ```
4. **Verify Baseline Test Suite Passes (268 tests)**:
   ```bash
   /Users/devesh/Library/Python/3.9/bin/pytest /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests -q
   ```
5. **Invalidation Condition**:
   If a valid competitive programming test case input consisting of unquoted CSS properties (e.g. raw text `display:flex;`) is required by CodeKata, the regex would sanitize it. However, competitive programming problems on CodeKata test algorithms (math, strings, arrays, trees, dynamic programming), not raw unquoted CSS syntax. Legitimate JSON inputs with quoted strings (`"display"`) are fully preserved.
