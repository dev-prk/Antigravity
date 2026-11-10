# Adversarial Challenge & Stress-Test Report: Milestone 1 Extractor

- **Agent**: Challenger 2 (`challenger_m1_2`)
- **Roles**: critic, specialist
- **Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`
- **State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2`
- **Target Target**: `zenclass_guvi/solver/extractor.py`
- **Verdict**: **`REQUEST_CHANGES`**
- **Date**: 2026-11-10T23:02:00Z

---

## 1. Observation

A dedicated empirical stress-test harness containing 14 adversarial test scenarios (`stress_test_harness.py`) was executed against `zenclass_guvi/solver/extractor.py`.

### 1.1 Verbatim Command & Test Execution Output
Command executed:
```sh
python3 /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2/stress_test_harness.py
```
Verbatim failure summary:
```
FAILED (failures=15)
Ran 14 tests in 0.126s
```

### 1.2 Specific Empirical Defects Observed

#### Defect 1: Deletion of Valid Python Dictionaries & Sets with Single Quotes (`_is_pure_css`)
- **Location**: `zenclass_guvi/solver/extractor.py:196-198`
  ```python
  if t.startswith("{") and re.search(cls._CSS_PROP_PATTERN, t, re.IGNORECASE):
      if not re.search(r'^\s*\{\s*"', t):
          return True
  ```
- **Observed Behavior**:
  Line 197 checks only for double quote `"` (`r'^\s*\{\s*"'`). Valid Python dictionaries that use single quotes `'` (e.g. `{'display': 'inline', 'val': 100}` or `{'width': 10, 'height': 20}`) fail this regex test, evaluating `not re.search(...)` to `True`. Consequently, `_is_pure_css()` classifies legitimate Python dictionaries and sets as pure CSS.
  When passed to `_filter_and_renumber` (line 464):
  ```python
  if cls._is_pure_css(case.input_text) or cls._is_pure_css(case.expected_output):
      continue
  ```
  The entire sample test case is dropped from `spec.sample_cases`.
- **Verbatim Failure Output**:
  ```
  FAIL: test_valid_python_dictionary_with_single_quotes (__main__.TestLegitimateBracesPreservation)
  AssertionError: 0 != 1 : Legitimate Python dict with single quotes was discarded by _is_pure_css

  FAIL: test_valid_python_dict_outputs_with_common_properties (__main__.TestLegitimateBracesPreservation) (dict_str="{'width': 10, 'height': 20}")
  AssertionError: 0 != 1 : Sample case with dict output {'width': 10, 'height': 20} was discarded by _is_pure_css

  FAIL: test_valid_python_set_of_css_keywords (__main__.TestLegitimateBracesPreservation)
  AssertionError: 0 != 1 : Python set with single quotes {'display', 'flex', 'inline'} was discarded by _is_pure_css
  ```
  Impacted keys tested: `width`, `height`, `font`, `border`, `flex`, `margin`, `padding`, `display`, `position`, `color`.

#### Defect 2: Input & Output Corruption via Redundant Angle-Bracket Stripping
- **Location**: `zenclass_guvi/solver/extractor.py:459-460`
  ```python
  clean_in = re.sub(r"<[^>]+>", "", clean_in).strip()
  clean_out = re.sub(r"<[^>]+>", "", clean_out).strip()
  ```
- **Observed Behavior**:
  In `_clean_text`, HTML tags are stripped (`text = re.sub(r"<[^>]+>", " ", text)` line 284) *before* decoding entities (`text = html.unescape(text)` line 286). This correctly converts `&lt;int&gt;` or `&lt;stdio.h&gt;` into `<int>` and `<stdio.h>`.
  However, in `_filter_and_renumber` (lines 459-460), `re.sub(r"<[^>]+>", "", clean_in)` runs *again* on the unescaped text.
  This strips legitimate code, C/C++ generics, headers, and comparison operators:
  - `"vector<int> nums"` is corrupted into `"vector nums"`
  - `"#include <stdio.h>"` is corrupted into `"#include"`
  - `"5 < 10 and 20 > 15"` is corrupted into `"5  15"`
- **Verbatim Failure Output**:
  ```
  FAIL: test_cpp_code_snippets_and_generics_preservation (__main__.TestLegitimateBracesPreservation) (case_name='comparison')
  AssertionError: '5  15' != '5 < 10 and 20 > 15'

  FAIL: test_cpp_code_snippets_and_generics_preservation (__main__.TestLegitimateBracesPreservation) (case_name='generics')
  AssertionError: 'vector nums' != 'vector<int> nums'

  FAIL: test_cpp_code_snippets_and_generics_preservation (__main__.TestLegitimateBracesPreservation) (case_name='c_header')
  AssertionError: '#include' != '#include <stdio.h>'
  ```

#### Defect 3: CSS Leaks Retained as Empty Test Cases
- **Location**: `zenclass_guvi/solver/extractor.py:457-465, 482-488`
- **Observed Behavior**:
  In Strategy 1, `clean_in = cls._clean_text(in_raw, preserve_newlines=True)` runs *before* adding to `raw_cases`. When `in_raw` is a pure CSS declaration leak (e.g. `{display:inline-flex;font-size:inherit;line-height:inherit;flex:1}`), `_clean_text` wipes it out to `""`.
  Then `raw_cases` contains `SampleCase(input_text="", expected_output="42")`.
  In `_filter_and_renumber`:
  ```python
  if not clean_in and not clean_out:
      continue
  if cls._is_pure_css(case.input_text) or cls._is_pure_css(case.expected_output):
      continue
  ```
  Because `case.input_text` is already `""`, `_is_pure_css("")` returns `False`.
  Because `clean_out` is `"42"`, `not clean_in and not clean_out` evaluates to `False`.
  As a result, the test case is **not dropped**, but retained as `SampleCase(input_text='', expected_output='42')`.
- **Verbatim Failure Output**:
  ```
  FAIL: test_real_world_css_leak_dropping (__main__.TestRealWorldCSSLeaks)
  AssertionError: 2 != 1 : CSS leak was retained with empty input: [SampleCase(input_text='', expected_output='42', case_number=1, explanation=None), SampleCase(input_text='1 5 3', expected_output='5', case_number=2, explanation=None)]
  ```

#### Defect 4: Compound CSS Selectors & @keyframes Leak into Description / Text
- **Location**: `zenclass_guvi/solver/extractor.py:153-165`
- **Observed Behavior**:
  1. `_CSS_AT_RULE_RE` only matches `@media` nested blocks and single `@rule ...;` rules. For `@keyframes spin { 0% { ... } 100% { ... } }`, it leaves `{ 0% 100% }` behind in problem descriptions.
  2. In `_CSS_RULE_RE`:
     `rf"(?:[.#]?[a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]+?(?:::[a-z\-]+|:[a-z\-]+(?:\([^\)]*\))?)?)\s*"`
     `[.#]?` only matches at the start of selector tokens. The character class `[a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]` omits `.` and `#`.
     Consequently, selectors like `div.card`, `span.badge`, and `div#container` fail to match `_CSS_RULE_RE`. Only their declaration blocks `{ ... }` are stripped, leaking selector names (`div.card`, `span.badge`, `div#container`) into descriptions and raw text.
  3. `_CSS_RULE_RE` lookahead `(?![^\{\n]*(?:Sample|Case|Input\s*[:\-]|Output\s*[:\-]|Description|Problem))` matches `output:` in `output::after`, preventing pseudo-elements like `output::after` from being stripped as CSS.
- **Verbatim Failure Output**:
  ```
  FAIL: test_class_selector_leakage (__main__.TestComplexInlineCSS)
  AssertionError: 'div.card' unexpectedly found in 'div.card span.badge Sort cards by suit.'

  FAIL: test_keyframes_leakage (__main__.TestComplexInlineCSS)
  AssertionError: '{ 0% 100% }' unexpectedly found in '{ 0% 100% } Rotate the array k times.'

  FAIL: test_pseudo_element_leakage (__main__.TestComplexInlineCSS)
  AssertionError: 'output::after' != ''
  ```

#### Defect 5: Unclosed `<style>` Swallowing Semantic HTML5 Containers
- **Location**: `zenclass_guvi/solver/extractor.py:272`
- **Observed Behavior**:
  The unclosed style lookahead tag list is `(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li)`. It lacks semantic HTML5 tags: `section`, `article`, `main`, `aside`, `header`, `footer`.
  When an unclosed `<style>` tag is followed by `<section>Problem Statement: ...</section>`, the regex swallows the section block entirely up to the first recognized block tag (such as `<p>Sample Input: ...</p>`), causing `spec.description` to be empty (`""`).
- **Verbatim Failure Output**:
  ```
  FAIL: test_unclosed_style_swallows_semantic_tags (__main__.TestPathologicalMalformedTags)
  AssertionError: '' != 'Calculate factorial of n.'
  + Calculate factorial of n. : Unclosed <style> swallowed <section> Problem Statement
  ```

---

## 2. Logic Chain

1. **Premise**: In competitive programming (including CodeKata), problems frequently involve dictionaries, sets, code snippets, generics, and comparison operators.
2. **Defect 1 Impact**:
   - `_is_pure_css` in `solver/extractor.py:197` checks `if not re.search(r'^\s*\{\s*"', t): return True`.
   - Python string representations of dictionaries (e.g., `{'display': 'inline', 'val': 100}` or `{'width': 10, 'height': 20}`) use single quotes `'`.
   - Because of this missing single quote check, `_is_pure_css` flags valid dictionaries as CSS declaration blocks.
   - `_filter_and_renumber` discards the entire test case.
   - When a problem tests dictionary output (such as counting frequencies, geometry with `width`/`height`, or graph positions), the code generator and test runner will find 0 sample cases or misaligned sample cases.
3. **Defect 2 Impact**:
   - Lines 459-460 run `re.sub(r"<[^>]+>", "", clean_in)` on strings that have already been unescaped from HTML entities.
   - Any `<` and `>` pair in the input (such as `5 < 10 and 20 > 15`, `vector<int>`, or `#include <stdio.h>`) is stripped as if it were an HTML tag.
   - This corrupts the problem's sample input text before passing it to the solver.
4. **Defect 3 Impact**:
   - Live production tasks like `guvi-97` failed with `ValueError: invalid literal for int() with base 10: '{display:inline-flex...}'`.
   - The worker's current fix wipes out the input to `""` via `_clean_text`, but `_filter_and_renumber` does not drop the test case if `expected_output` is non-empty.
   - This leaves behind an invalid `SampleCase(input_text='', expected_output='42')`.
5. **Conclusion**:
   The current implementation of `solver/extractor.py` introduces false test case deletions, corrupted code inputs, and CSS selector leakage. Milestone 1 cannot be approved in this state.

---

## 3. Caveats

- **Existing Tests Passing**: All 28 tests in `tests/test_m1_filtering.py` pass because they only tested double-quoted JSON strings (`{"name": "test", "display": "flex", "count": 42}`) and numbers. They did not test single-quoted Python dictionaries, C++ generics, or compound CSS class selectors.
- **Review-Only Constraint**: In strict adherence to agent role constraints, challenger has NOT modified `zenclass_guvi/solver/extractor.py`. Remediation instructions are provided below for the worker.

---

## 4. Conclusion & Required Remediations

### Final Verdict: **`REQUEST_CHANGES`**

The worker must address the following remediations in `zenclass_guvi/solver/extractor.py`:

### Concrete Remediation Plan for Worker:

1. **Fix `_is_pure_css` (lines 196-198)**:
   - Allow single quotes (`'`) as well as double quotes (`"`) after `{`:
     ```python
     if t.startswith("{") and re.search(cls._CSS_PROP_PATTERN, t, re.IGNORECASE):
         if not re.search(r"""^\s*\{\s*["']""", t):
             return True
     ```
   - Furthermore, check if the content has CSS declaration syntax (i.e. unquoted property followed by colon without quotes around values or ending with semicolon, vs Python dict/set syntax). If a string parses as valid JSON or valid Python literal via `ast.literal_eval`, it is NOT pure CSS!

2. **Remove Redundant HTML Stripping in `_filter_and_renumber` (lines 459-460)**:
   - Remove lines 459-460:
     ```python
     # REMOVE THESE LINES:
     # clean_in = re.sub(r"<[^>]+>", "", clean_in).strip()
     # clean_out = re.sub(r"<[^>]+>", "", clean_out).strip()
     ```
   - HTML stripping is already performed correctly by `_clean_text` before entity unescaping. Applying it after entity unescaping destroys legitimate angle brackets in code and comparison expressions.

3. **Check `_is_pure_css` on Raw Input Before Sanitization & Drop Empty-Input Cases (lines 456-473, 480-491)**:
   - Track whether raw input or output was pure CSS before `_clean_text` wiped it out.
   - If a test case's input was pure CSS, drop the entire case rather than retaining `SampleCase(input_text="", expected_output=...)`.

4. **Improve Selector & Keyframe Regexes in `_sanitize_css`**:
   - In `_CSS_RULE_RE`, include `.` and `#` inside the selector character class: `[.#a-zA-Z0-9_\-,>+~\[\]\=\"\'\s]`.
   - In `_CSS_AT_RULE_RE`, support `@keyframes` with nested brace blocks:
     `r"(?:@(?:media|keyframes|-webkit-keyframes)[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\s*\}|@[a-z\-]+[^;{]*;?)"`
   - In lookahead for `_CSS_RULE_RE`, ensure pseudo-elements like `output::` are not confused with `Output:`. Require whitespace or non-colon character after label matching: e.g. `(?![^\{\n]*(?:Sample|Case|Input\s*[:\-](?!\:)|Output\s*[:\-](?!\:)|Description|Problem))`.

5. **Expand Block Tag Lookahead in `_clean_text` (line 272)**:
   - Add semantic HTML5 container elements:
     `(?=<(?:p|div|h[1-6]|span|body|html|br|pre|table|ul|li|section|article|main|aside|header|footer)\b)`

---

## 5. Verification Method

### 5.1 Project Test Command & Reproduction
Run the adversarial test harness directly:
```sh
cd /Users/devesh/Documents/Antigravity/Automation
python3 /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2/stress_test_harness.py
```
**Expected outcome for approval**: All 14 tests must pass with 0 failures.

### 5.2 Files to Inspect
- `zenclass_guvi/solver/extractor.py` (lines 153-174, 190-202, 270-275, 454-474, 480-492)
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m1_2/stress_test_harness.py`

### 5.3 Invalidation Conditions
- Any change that passes `stress_test_harness.py` but breaks existing baseline tests in `tests/test_m1_filtering.py` or `tests/test_extractor.py` will invalidate the remediation.
- The worker must run both `stress_test_harness.py` AND `pytest tests/` to confirm complete resolution.
