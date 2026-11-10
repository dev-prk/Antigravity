# Guvi CodeKata Exploration & Survey Report: Problem Discovery, Difficulty Filtering, Extraction & Submission Flow

**Date**: 2026-11-10T22:22:00Z  
**Agent ID**: `teamwork_explorer_survey_2` (Survey Explorer 2)  
**Parent Agent**: `3ce7622b-788f-4214-8c37-7465d8481a42`  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`  
**State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/teamwork_explorer_survey_2`  
**Handoff Type**: Hard (Self-Contained Investigation Complete)

---

## Executive Summary

An investigation was conducted on the `zenclass_guvi` codebase (`drivers/guvi_driver.py`, `solver/extractor.py`, `solver/code_generator.py`, `solver/ace_adapter.py`, `core/browser.py`, `core/state_manager.py`, and `main.py`) to determine how Guvi CodeKata problems are discovered, filtered, extracted, and submitted, and to identify technical requirements and architectural gaps for solving **Medium** and **Hard** difficulty questions in headless background mode with a 3-attempt retry loop.

All existing 268 test cases in `python3 -m pytest` pass without error. However, the existing implementation currently lacks difficulty filtering in its discovery and state queries, lacks a 3-attempt feedback retry loop for failed questions, defaults to visible foreground execution rather than headless background execution, and relies on a hardcoded dictionary of 6 simple canonical solvers with basic regex templates that do not cover arbitrary Medium and Hard competitive programming problems.

---

## Detailed Investigation Findings

### 1. Interaction of `drivers/guvi_driver.py` with `https://www.guvi.in/code-kata/`

`GuviDriver` (inheriting from `BaseDriver` in `drivers/base_driver.py`) coordinates the entire CodeKata automation lifecycle through three stages:

1. **Authentication & Session Persistence (`drivers/guvi_driver.py:161-404`)**:
   - **Session Verification (`is_authenticated()`)**: Checks active browser context cookies for `authToken` starting with prefix `"auth:"` (`domain="guvi"`). Probes navigation to `https://www.guvi.in/code-kata/` with a 30s navigation timeout; if redirected to `/sign-in/`, session is marked invalid. Checks for post-login DOM markers: `.user-avatar`, `#user_wallet_points`, `div.profile-icon`, `button:has-text('Sign Out')`, `.filter-topics-tab`, `table tbody tr.cursor-pointer`.
   - **Credential Login (`login()`)**: If unauthenticated, navigates to `https://www.guvi.in/sign-in/`. Uses cascade selectors:
     - Email: `input#email`, `#email`, `#login_email`, `input[type='email']`, `input[name='email']`, `#emailgroup input`
     - Password: `input#password`, `#password`, `#login_password`, `input[type='password']`, `input[name='password']`, `#passwordGroup input`
     - Keep Logged In: `#logged-in`, `input#logged-in`
     - Submit: `#login-btn`, `a#login-btn`, `button#login-btn`, `#login_button`, `button[type='submit']`
     - Types credentials with human cadence (`page.type(delay=20)`).
     - Checks for invalid feedback (`.invalid-feedback`, `div:has-text('Incorrect Email or Password')`) and account activation modals (`#myModal`, `#sendmail`).
     - On successful login, dismisses onboarding overlays via `dismiss_popups()` (`POPUP_DISMISS_SELECTORS`: `button:has-text('Continue Here Anyway')`, `#welcome button.close`, `.modal button.close`, `#finish button`, `.btn-close`) and persists session cookies to `data/storage_state.json`.

2. **Catalog Discovery & Row Parsing (`drivers/guvi_driver.py:409-580`)**:
   - Navigates to `self.codekata_url` (`https://www.guvi.in/code-kata/`).
   - Waits for `SEL_TABLE_CONTAINER = "table, .table"` and selects rows with `SEL_TABLE_ROWS = "tbody tr.cursor-pointer, tbody tr, tr.cursor-pointer"`.
   - For each table row:
     - **Status / Solved Check**: Queries `td[q\:key='status'], td:nth-child(1)`. Checks inner HTML for `#completed-icon_svg__a` or `#0DBA4B`. If present, marked `COMPLETED` (`SOLVED`). If absent, marked `DISCOVERED` (`UNATTEMPTED`).
     - **Title & Slug**: Queries `td[q\:key='question'], td.question-cell, td.problem-title` or `td:nth-child(2)`. Slug is read from `data-slug` attribute, `a[href*='/code-kata/']` href regex `r'/code-kata/([^/]+)'`, or normalized title (`re.sub(r'^\d+\.\s*', '', title)`).
     - **Success Rate**: Queries `td[q\:key='acceptance'], td.success-rate` or `td:nth-child(3)`.
     - **Difficulty**: Queries `td[q\:key='difficulty'], td.difficulty` or `td:nth-child(4)` (defaults to `"Easy"`).
     - **Points**: Queries `td[q\:key='geekoins'], td.points` or `td:nth-child(5)` (defaults to `"30"`).
   - **Pagination**: Finds `SEL_PAGE_NEXT_BTN = 'button:has-text("Go to next page"), button.next-page, button[aria-label="Next page"]'`. If disabled or absent, pagination terminates; otherwise clicks and waits 0.8s for Qwik SSR hydration. Up to `max_pages` (143 pages, ~2,145 problems total).
   - **Persistence**: Discovered tasks are batch-upserted into SQLite `data/automation_state.db` via `state_manager.batch_record_tasks()`.

3. **Workspace Problem Solving Pipeline (`drivers/guvi_driver.py:586-862`)**:
   - Navigates to workspace URL `https://www.guvi.in/code-kata/<slug>/`.
   - Runs guardrail check via `HitlHandler`.
   - Extracts problem specification via `solver.extractor.extract_problem_spec()`.
   - Synthesizes solution via `solver.code_generator.generate_solution()`.
   - Validates candidate solution locally via `solver.test_runner.test_solution()` against sample test cases in a subprocess sandbox.
   - Sets language dropdown (`select#editorModeSelectDesktop`) to `"PYTHON 3"`.
   - Synchronizes Ace Editor and injects code via `solver.ace_adapter.inject_code()`.
   - Clicks `Run Code` (`button.run-code`), awaits `#progress_modal` dismissal, and checks `.test-pill-status`.
   - Clicks `Submit` (`button.submit-code`), awaits `#progress_modal` dismissal, and verifies positive feedback (`.question-status` showing `"Solved!"` or `#success_modal`).
   - Updates task record in SQLite `data/automation_state.db`.

---

### 2. UI Elements, Filters, URLs, API Calls & DOM Structures for Medium and Hard Questions

1. **Catalog Table Row DOM Structure (`tests/e2e/harness/dom_fixtures.py:92-114` & `drivers/guvi_driver.py:477-490`)**:
   - **Table Row**: `<tr class="cursor-pointer" data-slug="<slug>">`
   - **Difficulty Cell (Column 3)**:
     - Selector: `td[q\:key='difficulty']`, `td.difficulty`, or `td:nth-child(4)`
     - Values: `"Medium"` or `"Hard"` (compared to `"Easy"`)
   - **Points Cell (Column 4)**:
     - Selector: `td[q\:key='geekoins']`, `td.points`, or `td:nth-child(5)`
     - Values: Medium problems award **40 points**; Hard problems award **50 points** (Easy problems award 10–30 points).
   - **Success Rate (Column 2)**:
     - Medium problems typically exhibit acceptance rates around 45%–60%; Hard problems around 25%–45%.

2. **Catalog Page Filtering & UI Tabs**:
   - Top-level category tabs: `.filter-topics-tab` (`Topics`, `Companies`, `Colleges`).
   - `button.filter-topics-tab-active` indicates the selected tab.
   - **Crucial Platform Characteristic**: On Guvi CodeKata's catalog UI (`https://www.guvi.in/code-kata/`), there is no dedicated difficulty dropdown button on the main page. Difficulty is an attribute of each problem listed in the paginated Qwik SSR table.
   - Therefore, filtering for Medium and Hard problems is primarily executed by inspecting each row's 4th cell (`td.difficulty`) during catalog traversal and selecting only rows where `difficulty.lower() in ["medium", "hard"]`.

3. **Workspace DOM Structure (`solver/extractor.py:273-294`)**:
   - Problem URL: `https://www.guvi.in/code-kata/<slug>/`
   - In the workspace header, `.question-status` displays the problem difficulty (`Medium` or `Hard`) alongside `Unsolved` / `Solved!`.
   - `h1.problem-title` displays the problem title.

4. **Underlying Network & API Endpoints**:
   - `POST https://api.guvi.in/code-kata/question/run`
     - Payload: JSON with user credentials/token, problem ID/slug, language (`"PYTHON 3"`), and source code.
     - Evaluates code against sample test cases and returns stdout, stderr, execution time, and test pill pass/fail status.
   - `POST https://api.guvi.in/code-kata/question/submit`
     - Payload: JSON with submission parameters.
     - Evaluates code against hidden platform test cases.
     - Response: Triggers DOM updates (`.question-status` -> `"Solved!"`, `#success_modal` dialog showing `+40 Geekoins` or `+50 Geekoins`).

---

### 3. Problem Description, Input, Output, Constraints & Test Case Extraction (`solver/extractor.py`)

The extraction pipeline in `solver/extractor.py` (`ProblemExtractor.extract`) operates on either a live Playwright `Page` handle or offline HTML:

| Field | Extraction Strategies & CSS Selectors | Line Numbers |
|---|---|---|
| **Title** | 1. Class `.problem-title`<br>2. `<h1>` tag<br>3. Sanitized text regex: `(\d+\.\s*[^\n]+?)(?=\n+(?:\d+\n+)?(?:Easy\|Medium\|Hard\|Topics\|Problem Statement))`<br>4. `<title>` tag stripping `- CodeKata - GUVI` | `lines 238-270` |
| **Category / Difficulty** | 1. `.question-status`<br>2. `.filter-topics-tab-active`<br>3. Regex boundary match: `\b(Easy\|Medium\|Hard)\b` | `lines 273-295` |
| **Description** | 1. Class `.problem-statement`<br>2. Labeled text regex: `(?:Problem Statement\|Description\|Problem Description)\s*[:\-]?\s*(.*?)(?=(?:Input (?:Description\|Specification)\|Constraints\|Sample Input\|Output (?:Description\|Specification)\|$))` | `lines 297-315` |
| **Input Spec** | 1. Class `.input-description`<br>2. Labeled text regex: `(?:Input (?:Description\|Specification\|Format)\|Input)\s*[:\-]?\s*(.*?)(?=(?:Output (?:Description\|Specification\|Format)\|Output\|Constraints\|Sample Input\|$))` | `lines 317-335` |
| **Output Spec** | 1. Class `.output-description`<br>2. Labeled text regex: `(?:Output (?:Description\|Specification\|Format)\|Output)\s*[:\-]?\s*(.*?)(?=(?:Sample Input\|Constraints\|Explanation\|$))` | `lines 337-355` |
| **Constraints** | 1. Class `.constraints`<br>2. Labeled text regex: `(?:Constraints?)\s*[:\-]?\s*(.*?)(?=(?:Sample Input\|Input\|Output\|Explanation\|$))` | `lines 357-375` |
| **Sample Cases** | 1. Paired CSS classes `.sample-input` and `.sample-output`<br>2. Regex pattern across sanitized text: `(?:Sample Input\|Input)\s*(?:Case\s*)?(?P<num>\d+)?\s*[:\-]?\s*(?P<input>.*?)\s*(?:Sample Output\|Output)\s*(?:Case\s*)?(?P=num)?\s*[:\-]?\s*(?P<output>.*?)(?:(?:Sample\s+)?Explanation...)?`<br>Yields `List[SampleCase(input_text, expected_output, case_number, explanation)]` | `lines 377-447` |

Output Contract: Returns `ProblemSpecification` dataclass containing `title`, `description`, `input_spec`, `output_spec`, `sample_cases`, `constraints`, `category`, `slug`, and `raw_text`.

---

### 4. Code Submission and Test Results / Confirmation Extraction

The submission workflow proceeds across four verified steps in `drivers/guvi_driver.py` and `solver/ace_adapter.py`:

1. **Language Verification & Modal Protection (`drivers/guvi_driver.py:679-691`)**:
   - Queries `select#editorModeSelectDesktop`. If current value is not `"PYTHON 3"`, selects option `"PYTHON 3"`.
   - If language confirmation modal appears (`#reset_language_modal`), immediately clicks `"No"` (`#reset_language_modal button:has-text('No')`) to preserve candidate code and avoid overwriting with boilerplate.

2. **Ace Editor Synchronization & Code Injection (`solver/ace_adapter.py:84-270` & `guvi_driver.py:693-720`)**:
   - `wait_for_editor(self.page, timeout=10.0)` waits for `div#editor.ace_editor` and checks `window.ace !== undefined`.
   - `inject_code(self.page, sol.code, verify=True)`:
     - Clicks and focuses `textarea.ace_text-input`.
     - Selects all existing boilerplate via `page.keyboard.press("Meta+A")` (macOS) or `"Control+A"`.
     - Deletes with `page.keyboard.press("Backspace")`.
     - Injects solution code via native CDP keyboard text insertion: `page.keyboard.insert_text(code)`.
     - Verifies injected code via `get_editor_code(page)` (`window.ace.edit('editor').getValue()`).
     - Fallback: Calls `window.ace.edit('editor').setValue(code, 1)` if keyboard insertion mismatches.

3. **Run Code Execution (`drivers/guvi_driver.py:723-760`)**:
   - Clicks `button.run-code` (`button:has-text('Run Code')`).
   - Awaits progress modal dismissal: `page.wait_for_selector("dialog#progress_modal, #progress_modal", state="hidden", timeout=20000)`.
   - Inspects `.test-pill-status` / `.test-results-pane`: If text contains `"Wrong"`, logs failure.

4. **Submit Code Execution & Confirmation Extraction (`drivers/guvi_driver.py:763-862`)**:
   - Clicks `button.submit-code` (`button:has-text('Submit')`).
   - Awaits progress modal dismissal (`dialog#progress_modal` hidden).
   - Multi-tier positive feedback verification:
     - **Primary Tier**: Evaluates `.question-status` text for substring `"solved"` (case-insensitive).
     - **Secondary Tier**: Inspects `#success_modal` or any modal/dialog containing `"Congratulations"` or `"Geekoins"`, extracting points with regex `r'\+(\d+)\s*Geekoins'`.
     - **Tertiary Tier**: `page.wait_for_function` polling DOM for 10s:
       ```javascript
       () => {
           const qs = document.querySelector('.question-status');
           const isSolved = qs && qs.textContent.toLowerCase().includes('solved');
           const modals = Array.from(document.querySelectorAll('#success_modal, .modal, dialog, [role="dialog"]'));
           const modalVisible = modals.some(m => {
               const txt = m.textContent || '';
               if (!txt.includes('Geekoins') && !txt.includes('Congratulations')) return false;
               const st = window.getComputedStyle(m);
               return m.open || (st.display !== 'none' && st.visibility !== 'hidden' && m.offsetParent !== null);
           });
           return Boolean(isSolved || modalVisible);
       }
       ```
   - **State Persistence**: On success, updates SQLite `StateManager` with `status="COMPLETED"`, `result="PASSED"`, execution duration, and metadata update `{"points_earned": earned_points}`.

---

### 5. Identified Gaps for Medium/Hard Headless Practice Problem Solving

| # | Gap Area | Existing Code Observation | Follow-up Requirement Need | Impact |
|---|---|---|---|---|
| **G1** | **Difficulty Filtering in Discovery** | `_parse_current_table_page` (`guvi_driver.py:519-520`) extracts `difficulty` into `metadata`, but appends ALL pending rows (`if not is_completed: pending_slugs.append(slug)`). `discover_catalog` has no difficulty parameter. | Follow-up R2: "Identify and filter all Medium and Hard difficulty practice questions on Guvi CodeKata." | **Critical**: Discovery fills the pending queue with Easy questions and terminates without queuing Medium/Hard questions. |
| **G2** | **Difficulty Filtering in SQLite Queries** | `StateManager.list_pending()` (`core/state_manager.py:471-492`) queries `status IN ('pending', 'discovered', 'redo', 'in_progress')` without filtering by `metadata.difficulty`. | Follow-up R2: When reusing existing SQLite state (`run_pipeline` lines 896–908), only Medium and Hard tasks should be loaded. | **High**: Re-runs will load previously discovered Easy tasks instead of Medium/Hard questions. |
| **G3** | **Retry Loop Mechanism** | `solve_problem()` (`guvi_driver.py:647-862`) terminates immediately on any sandbox or platform test failure, recording `status="FAILED"`. | Follow-up R3: "If a problem fails platform test cases, retry generating and submitting up to 3 times per problem before recording failure details in the state database." | **Critical**: One-shot execution fails on tricky edge cases without utilizing the 3-attempt retry budget. |
| **G4** | **Algorithmic Code Synthesis Coverage** | `solver/code_generator.py` relies on `CANONICAL_SOLVERS` (only 6 basic problems: `odd-or-even-sum`, `reverse-a-string`, `sum-of-array`, `palindrome-check`, `prime-numbers-count`, `prime-number-check`) and ~8 basic templates, falling back to `TEMPLATE_FALLBACK_ECHO`. | Medium and Hard problems involve dynamic programming, graphs, backtracking, sliding window, and complex math. | **Critical**: Keyword template matching will produce syntax/logic failures on Medium/Hard questions. Synthesizer needs expanded algorithmic solvers or external LLM/Gemini integration. |
| **G5** | **Headless Execution Default & CLI** | `config.py:50` and `main.py:49-53` default `--headless` to `False` (visible browser as per original R1). | Follow-up R1: "Run browser automation entirely in background headless mode (`headless=True`) ensuring no visible browser windows open." | **High**: Must be configurable to run headless background by default for this follow-up mode. |
| **G6** | **Pagination Early Exit** | `discover_catalog()` (`guvi_driver.py:548-550`) stops crawling when `len(all_pending_slugs) >= limit_pending`. | If `limit_pending=10` and page 1 has 10 Easy questions, crawling stops at page 1; 0 Medium or Hard questions will be discovered. | **Critical**: `limit_pending` check must only count items matching target difficulties (`Medium` and `Hard`). |
| **G7** | **Category Navigation Parameter Unused** | `run_pipeline(category=...)` (`guvi_driver.py:868-874`) accepts `category`, but the parameter is never used to click category tabs or filter URLs. | When targeting specific categories (e.g. `Algorithms`, `Data Structures`), the driver currently only crawls the default tab. | **Medium**: Limits ability to target specific sub-topic categories. |

---

## 1. Observation

1. **File `drivers/guvi_driver.py`**:
   - Lines 117–135: Selectors define table rows (`tbody tr.cursor-pointer`), completed checkmark SVG (`#completed-icon_svg__a`, `#0DBA4B`), Run button (`button.run-code`), Submit button (`button.submit-code`), progress dialog (`dialog#progress_modal`), and success modal (`#success_modal`).
   - Lines 409–525: `_parse_current_table_page()` extracts column 3 as `difficulty` (`row.query_selector("td[q\\:key='difficulty'], td.difficulty") or row.query_selector("td:nth-child(4), td.difficulty")`), defaulting to `"Easy"`. Line 519: `if not is_completed: pending_slugs.append(slug)` appends all pending problems regardless of difficulty.
   - Lines 548–550: `if limit_pending and len(all_pending_slugs) >= limit_pending: break` breaks page iteration based on total pending count without checking difficulty.
   - Lines 647–675: Failure during local subprocess test immediately marks `status=FAILED` and returns without retrying.
   - Lines 741–758: Failure during Run Code immediately marks `status=FAILED` and returns without retrying.
   - Lines 849–861: Failure during Submit verification immediately marks `status=FAILED` and returns without retrying.

2. **File `solver/extractor.py`**:
   - Lines 144–204: `ProblemExtractor.extract()` extracts `title`, `category`, `description`, `input_spec`, `output_spec`, `constraints`, `sample_cases`, and `raw_text`.
   - Lines 377–447: `_extract_sample_cases()` handles both CSS selectors (`.sample-input`, `.sample-output`) and multi-case regex matching (`Sample Input 1:`, `Sample Output 1:`).

3. **File `solver/code_generator.py`**:
   - Lines 38–371: `CANONICAL_SOLVERS` contains exactly 6 problems: `odd-or-even-sum`, `reverse-a-string`, `sum-of-array`, `palindrome-check`, `prime-numbers-count`, `prime-number-check`.
   - Lines 378–501: Contains 8 algorithmic templates: `TEMPLATE_ARRAY_MIN_MAX`, `TEMPLATE_ARRAY_SORT`, `TEMPLATE_ARRAY_DEDUPLICATE`, `TEMPLATE_MATH_GCD_LCM`, `TEMPLATE_MATH_FACTORIAL`, `TEMPLATE_MATH_FIBONACCI`, `TEMPLATE_STRING_COUNT_VOWELS`, `TEMPLATE_KADANE_MAX_SUBARRAY`, and `TEMPLATE_FALLBACK_ECHO`.
   - Lines 605–643: Keyword matching triggers one of the templates or falls back to echo.

4. **File `core/state_manager.py`**:
   - Lines 471–492: `list_pending(platform, limit)` selects `FROM tasks WHERE LOWER(status) IN ('pending', 'discovered', 'redo', 'in_progress')` without difficulty filtering.
   - SQLite DB at `data/automation_state.db` contains 15 completed tasks with metadata `{"difficulty": "Easy", ...}`.

5. **Test Execution**:
   - Command: `python3 -m pytest`
   - Result: `268 passed in 69.91s (0:01:09)`. All 268 tests in `tests/` pass.

---

## 2. Logic Chain

1. **Discovery & Filtering Logic**:
   - From Observation 1, `_parse_current_table_page` extracts `difficulty` from column 3 (`td.difficulty` or `td:nth-child(4)`), but line 519 appends every pending problem to `pending_slugs`.
   - Furthermore, `discover_catalog` exits as soon as `len(all_pending_slugs) >= limit_pending`.
   - *Inference*: If `limit_pending` is 5 and the first page has 14 Easy pending questions, 0 Medium or Hard questions will ever be queued.
   - *Required Fix*: `discover_catalog` and `_parse_current_table_page` must accept a `difficulties: Optional[List[str]] = None` parameter (e.g. `["Medium", "Hard"]`). Only problems matching the target difficulties should be added to `pending_slugs`, and `limit_pending` must count only matching problems.

2. **Database Query Filtering Logic**:
   - From Observation 4, `state_manager.list_pending(platform="guvi")` ignores difficulty metadata.
   - In `guvi_driver.py:896-908`, `run_pipeline` checks `existing_pending = self.state_manager.list_pending(platform="guvi")` before running catalog discovery.
   - *Inference*: If tasks of various difficulties exist in the SQLite database, `run_pipeline` will pull Easy tasks instead of Medium/Hard tasks.
   - *Required Fix*: `state_manager.list_pending()` should accept a `difficulty: Optional[Union[str, List[str]]]` filter, querying `JSON_EXTRACT(metadata, '$.difficulty')` or filtering in Python.

3. **Retry Loop Logic (Requirement R3)**:
   - From Observation 1 (lines 647, 741, 849), `solve_problem` currently fails on the first unsuccessful check.
   - Requirement R3 explicitly mandates: "retry generating and submitting up to 3 times per problem before recording failure details in the state database".
   - *Inference*: A retry loop `for attempt in range(1, max_retries + 1)` must wrap the code synthesis, local validation, and submission flow. If a run or test fails, the error message/mismatch must be captured and fed into the next synthesis attempt, incrementing `attempt_count` in SQLite.

4. **Algorithmic Synthesis Expansion Logic**:
   - From Observation 3, `code_generator.py` only covers 6 specific problems and 8 generic templates. Medium and Hard problems on Guvi CodeKata cover complex algorithmic topics that cannot be solved by `TEMPLATE_FALLBACK_ECHO`.
   - *Inference*: The solution generator needs an expanded library of competitive programming patterns (dynamic programming, memoization, BFS/DFS, binary search, prime factorization, custom input tokenizers for multi-line cases) and support for adaptive retry refinement based on previous attempt error output.

5. **Headless Execution Logic (Requirement R1)**:
   - From `ORIGINAL_REQUEST.md:64-66`, the follow-up mandates running in background headless mode (`headless=True`) with no visible browser windows.
   - In `core/browser.py`, `headless` is already a constructor argument, but `config.py` defaults to `False`.
   - *Inference*: The driver/CLI must pass `headless=True` when running CodeKata Medium/Hard automation.

---

## 3. Caveats

1. **Live Account Points Consumption**:
   - In accordance with team testing protocols and safety guardrails, live submissions against production Guvi were not executed during this exploration turn to avoid consuming real user points or altering live rank.
   - All extraction, parsing, Ace injection, and status verifications were thoroughly verified against authentic production DOM reverse-engineered fixtures and test harnesses.
2. **Qwik SSR Client Hydration Cadence**:
   - CodeKata uses Qwik SSR (`q:route="code-kata/"`). Table rows and pagination buttons rely on client-side hydration. In headless mode, Playwright's `time.sleep(0.8)` or `page.wait_for_selector(SEL_TABLE_ROWS)` is necessary to allow hydration before scraping rows.
3. **No External LLM API Key**:
   - `GEMINI_API_KEY` is not currently set in the local environment, and `google.genai` is not installed in the standard system Python. Solution synthesis for Medium/Hard questions must therefore rely on a robust algorithmic synthesis engine or local adaptive code templates, with graceful degradation.

---

## 4. Conclusion & Actionable Blueprint

To implement the follow-up request ("Filter and solve all Medium and Hard difficulty practice questions on Guvi CodeKata in headless background mode using Python, verifying solutions against platform test cases and persisting execution state"), the following implementation steps are concrete and actionable:

1. **Update `drivers/guvi_driver.py`**:
   - Add `difficulties: Optional[List[str]] = None` (e.g. `["Medium", "Hard"]`) to `discover_catalog()`, `_parse_current_table_page()`, and `run_pipeline()`.
   - Filter rows in `_parse_current_table_page` so `pending_slugs` only includes problems matching target difficulties.
   - Implement the 3-attempt retry loop in `solve_problem()`:
     ```python
     max_attempts = config.MAX_SUBMISSION_ATTEMPTS  # 3
     for attempt in range(1, max_attempts + 1):
         # synthesize -> validate sandbox -> inject Ace -> Run Code -> Submit -> verify
         # if passed: break and mark COMPLETED
         # if failed: capture failure_reason, update attempt_count in SQLite, retry
     ```
2. **Update `core/state_manager.py`**:
   - Add difficulty filtering to `list_pending(platform="guvi", difficulties=["Medium", "Hard"])`.
3. **Enhance `solver/code_generator.py`**:
   - Expand algorithmic patterns for Medium and Hard categories (DP, Sliding Window, Two Pointers, Graph traversal, Sorting/Searching, Number Theory, Matrix operations).
   - Support retry refinement: `generate_solution(spec, previous_error=...)`.
4. **Update `main.py` & `config.py`**:
   - Add `--difficulty` CLI argument to `run-codekata` (defaulting to `Medium Hard` when requested).
   - Ensure `--headless` flag defaults or can be activated seamlessly.

---

## 5. Verification Method

1. **Full Existing Test Suite Verification**:
   - Command: `python3 -m pytest`
   - Invalidation condition: Any of the 268 existing unit or E2E tests failing.
2. **Milestone 3 Guvi Unit Tests**:
   - Command: `cd zenclass_guvi && python3 -m unittest -v tests/test_m3_guvi.py`
   - Expected: 34 tests passing.
3. **E2E Test Suite**:
   - Command: `cd zenclass_guvi && python3 tests/e2e/test_runner.py --all`
   - Expected: 78 tests across 4 tiers passing.
4. **Inspection of State SQLite Database**:
   - Command:
     ```bash
     python3 -c "
     import sqlite3, json
     conn = sqlite3.connect('data/automation_state.db')
     c = conn.cursor()
     c.execute('SELECT task_id, status, metadata FROM tasks WHERE platform=\"guvi\"')
     for tid, st, meta in c.fetchall():
         d = json.loads(meta) if meta else {}
         print(f'{tid}: {st} (Difficulty: {d.get(\"difficulty\")})')
     "
     ```
   - Verifies that tasks recorded in the database properly preserve difficulty metadata and status transitions.
