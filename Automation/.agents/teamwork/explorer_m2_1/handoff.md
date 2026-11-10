# Handoff Report: Milestone 2 Problem Extractor and Ace Editor Adapter Blueprint

**Date**: 2026-11-10T15:42:00Z  
**Agent ID**: `explorer_m2_1`  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1`  
**Handoff Type**: Hard (Task Complete)  

---

## 1. Observation

Direct code and DOM analysis was performed across the Guvi CodeKata workspace specifications, E2E test suite fixtures, contract loaders, and existing system components:

1. **Test Suite Expectations and Contracts**:
   - `zenclass_guvi/tests/e2e/tier1_features/test_f05_extractor.py` (lines 17-26, 28-40):
     - Expects `extractor(html_text) -> spec`.
     - Fields accessed: `spec.title`, `spec.description`, `spec.input_desc`, `spec.output_desc`, `spec.sample_input`, `spec.sample_output`.
     - Tests graceful degradation on sparse HTML (lines 30-40) and empty HTML in `tests/e2e/tier2_boundaries/test_b01_empty_zero_inputs.py` (lines 32-38) expecting `title == "Unknown"`, `sample_input == ""`, `sample_output == ""`.
   - `zenclass_guvi/tests/e2e/tier1_features/test_f08_ace_adapter.py` (lines 13-32):
     - Expects container selector `div#editor` / `class="ace_editor"` and input textarea `class="ace_text-input"`.
     - Specifies the 4-step CDP injection command sequence:
       `("click", "div#editor textarea.ace_text-input")`, `("press", "Meta+A")`, `("press", "Backspace")`, `("insert_text", sample_code)`.
   - `zenclass_guvi/tests/e2e/harness/contract_loader.py` (lines 88-111):
     - Dynamic loader attempts `from solver.extractor import extract_problem_spec`.
   - `PROJECT.md` Interface Contracts (lines 69-74):
     - `extract_problem_spec(page: Page) -> ProblemSpec`
     - `inject_code_into_ace(page: Page, code: str) -> bool`
   - `requirements.txt`:
     - Contains only `playwright>=1.40.0` and `pytest>=7.0.0`. External parsing libraries such as `beautifulsoup4` (`bs4`) or `lxml` are NOT installed in the environment (`ModuleNotFoundError: No module named 'bs4'`). All parsing must rely strictly on standard library `re`, `html`, `dataclasses`, `typing`, and Playwright.

2. **Guvi CodeKata DOM Architecture (from spec_miner_survey_2 §10, §11, §13)**:
   - Problem Details:
     - Heading `.problem-title` or `h1`
     - Category / Difficulty: `.question-status`
     - Structural sections: `.problem-statement`, `.input-description`, `.output-description`, `.sample-input`, `.sample-output`, `.constraints`.
     - Labeled text headings in Qwik SSR: `Problem Statement:`, `Input Description:`, `Output Description:`, `Sample Input:`, `Sample Output:`, `Constraints:`, `Explanation:`.
   - Editor Pane:
     - Engine: **Ace Editor** (NOT Monaco Editor; `window.monaco` is `undefined`).
     - Container: `div#editor.ace_editor`
     - Text Input: `textarea.ace_text-input`
     - Line Nodes: `div.ace_line` inside `.ace_layer.ace_text-layer`
     - Global API: `window.ace` or DOM property `document.getElementById('editor').env.editor`.

---

## 2. Logic Chain

1. **Unifying Data Contracts (`ProblemSpecification` vs `ProblemSpec`)**:
   - The user dispatch requires `ProblemSpecification` with fields: `title`, `description`, `input_spec`, `output_spec`, `sample_cases: List[SampleCase]`, `constraints`, `category`, and `raw_text`.
   - Existing E2E tests (`test_f05_extractor.py`) access `spec.input_desc`, `spec.output_desc`, `spec.sample_input`, `spec.sample_output`.
   - *Inference*: By defining `ProblemSpecification` with property getters for `input_desc -> input_spec`, `output_desc -> output_spec`, `sample_input -> sample_cases[0].input_text`, and `sample_output -> sample_cases[0].expected_output`, plus setting `ProblemSpec = ProblemSpecification`, both legacy and new contracts are fulfilled simultaneously with zero breakage.

2. **Dual-Input Extractor (`Page` or `str`)**:
   - In live execution (`drivers/guvi_driver.py`), `extract_problem_spec` receives a Playwright `Page`.
   - In automated E2E tests (`test_f05_extractor.py`), it receives an HTML string `str`.
   - *Inference*: `extract_problem_spec(source: Any)` inspects `source`. If `hasattr(source, 'content')`, it extracts `source.content()` while maintaining the page handle for optional live DOM inspection; if `isinstance(source, str)`, it processes the string directly.

3. **Multi-Strategy Parsing Pipeline**:
   - Strategy 1 (CSS Class Selectors): Checks `.problem-title`, `.problem-statement`, `.input-description`, `.output-description`, `.sample-input`, `.sample-output`, `.constraints`.
   - Strategy 2 (Labeled Text Headings): When explicit CSS classes are missing (e.g. Qwik SSR / Markdown markup), parses labeled text blocks (`Problem Statement:`, `Input Description:`, etc.).
   - Strategy 3 (Negative Lookahead Regex on Sample Cases):
     A naive regex on `Input:` inadvertently matches `Input Description:`. By employing negative lookaheads:
     `r"(?:(?:Sample\s+Input)|(?:Input(?!\s*(?:Description|Specification|Format))))\s*(?:Case\s*)?(?P<num>\d+)?\s*[:\-]?\s*"`
     we cleanly isolate true sample cases from specification descriptions and capture multiple sample cases and optional explanations.

4. **Multiline Formatting Preservation**:
   - Standard competitive programming inputs contain line breaks (e.g. `5\n1 2 3 4 5`).
   - *Inference*: While descriptions and titles can have excess whitespace collapsed, `sample_input` and `sample_output` must preserve internal `\n` line feeds, only stripping outer leading/trailing whitespace.

5. **Ace Editor CDP Keyboard Injection Protocol**:
   - Ace Editor captures keyboard input via hidden `textarea.ace_text-input` and ignores synthetic JavaScript paste events.
   - Playwright's `page.keyboard.insert_text(code)` sends CDP `Input.insertText` events, which Chromium handles as trusted native OS keystrokes.
   - Operating system modifier detection: On macOS (Apple Silicon), `Meta+A` triggers Select All; on Linux/Windows, `Control+A` triggers Select All. Using `modifier = "Meta" if sys.platform == "darwin" else "Control"` ensures robust platform-native behavior.
   - Two-tier fallback: If CDP keyboard insertion encounters any issue or verification detects a buffer mismatch, direct JavaScript execution via `page.evaluate("([id, c]) => ace.edit(id).setValue(c, 1)", ["editor", code])` (with `el.env.editor` fallback) guarantees insertion.
   - Retrieval via `get_editor_code`: Queries `ace.edit('editor').getValue()`, falling back to `el.env.editor.getValue()`, then concatenating `.ace_line` text nodes.
   - Readiness via `wait_for_editor`: Awaits `textarea.ace_text-input` in DOM and checks `window.ace || el.env.editor || lines.length > 0`.

---

## 3. Caveats

1. **No External BeautifulSoup Dependency**: `bs4` is not installed in the workspace environment. The blueprints use Python standard library regex (`re`) and HTML unescaping (`html.unescape`). This ensures zero runtime dependency failures.
2. **Dynamic Language Switch Boilerplate**: If starter boilerplate code in Ace Editor triggers a `<dialog id="reset_language_modal">` ("Keep Code Changes?"), the 4-step clear-and-insert sequence overwrites the buffer cleanly, but the caller (`guvi_driver.py`) should ensure the language is set to `PYTHON 3` before code injection.
3. **Ace Virtual Scrolling on Very Large Buffers**: When reading code via `.ace_line` concatenation fallback, Ace virtualizes lines outside the viewport. For solutions larger than ~50 lines, the primary strategy (`getValue()`) must be used rather than DOM line scraping.

---

## 4. Conclusion

Complete, production-ready blueprints have been developed, verified, and saved in the agent workspace:

1. **`solver/extractor.py` Blueprint (`proposed_extractor.py`)**:
   - Data structures: `SampleCase` and `ProblemSpecification` (with `ProblemSpec` alias).
   - Functions: `extract_problem_spec(source: Any) -> ProblemSpecification` and `ProblemExtractor.extract`.
   - Multi-strategy parsing supporting both Playwright `Page` and raw HTML `str`.
   - Passes 100% of existing E2E tests (`test_f05_extractor.py`, `test_b01_empty_zero_inputs.py`, `test_p02_discovery_to_solver_sandbox.py`).

2. **`solver/ace_adapter.py` Blueprint (`proposed_ace_adapter.py`)**:
   - Class: `AceEditorAdapter` with singleton `_default_adapter`.
   - Functions: `inject_code(page: Any, code: str) -> bool`, `get_editor_code(page: Any) -> str`, `wait_for_editor(page: Any, timeout: float = 10.0) -> bool`.
   - Contract alias: `inject_code_into_ace = inject_code`.
   - 4-step CDP keyboard injection sequence with native modifier detection and JavaScript `ace.edit().setValue()` fallback.

---

## 5. Verification Method

To independently verify the blueprints against all E2E test vectors and mock specifications:

1. **Run Explorer Self-Verification Suite (12 unit tests)**:
   ```bash
   PYTHONPATH="/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1" \
     python3 /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1/test_blueprints.py
   ```
   *Expected Output*:
   ```
   Ran 12 tests in 0.007s
   OK
   ```

2. **Verify Against Existing E2E Extractor Test Suite**:
   ```bash
   PYTHONPATH="/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi:/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1" \
     python3 -c "
   import tests.e2e.tier1_features.test_f05_extractor as t05
   import proposed_extractor
   t05.get_problem_extractor = lambda: (proposed_extractor.extract_problem_spec, 'blueprint')
   import unittest
   suite = unittest.defaultTestLoader.loadTestsFromTestCase(t05.TestFeature05ProblemExtractor)
   res = unittest.TextTestRunner(verbosity=2).run(suite)
   assert res.wasSuccessful()
   "
   ```
   *Expected Output*: `Ran 2 tests in 0.003s ... OK`.

3. **Verify Against Boundary Empty/Zero Inputs Suite**:
   ```bash
   PYTHONPATH="/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi:/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1" \
     python3 -c "
   import tests.e2e.tier2_boundaries.test_b01_empty_zero_inputs as tb01
   import proposed_extractor
   tb01.get_problem_extractor = lambda: (proposed_extractor.extract_problem_spec, 'blueprint')
   import unittest
   suite = unittest.defaultTestLoader.loadTestsFromTestCase(tb01.TestBoundaryEmptyZeroInputs)
   res = unittest.TextTestRunner(verbosity=2).run(suite)
   assert res.wasSuccessful()
   "
   ```
   *Expected Output*: `Ran 5 tests in 0.105s ... OK`.

4. **Verify Against Pairwise Extractor-to-Sandbox Pipeline**:
   ```bash
   PYTHONPATH="/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi:/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1" \
     python3 -c "
   import tests.e2e.tier3_pairwise.test_p02_discovery_to_solver_sandbox as tp02
   import proposed_extractor
   tp02.get_problem_extractor = lambda: (proposed_extractor.extract_problem_spec, 'blueprint')
   import unittest
   suite = unittest.defaultTestLoader.loadTestsFromTestCase(tp02.TestPairwiseDiscoveryToSolverSandbox)
   res = unittest.TextTestRunner(verbosity=2).run(suite)
   assert res.wasSuccessful()
   "
   ```
   *Expected Output*: `Ran 1 test in 0.021s ... OK`.

### Invalidation Conditions
- If Guvi modifies Ace Editor container ID away from `#editor` or removes `.ace_editor`.
- If Guvi stops rendering sample test cases in `.sample-input` / `.sample-output` or labeled text headings.
- If Playwright introduces breaking changes to `page.keyboard.insert_text` CDP protocol handler.
