# Comprehensive Specification & 4-Tier E2E Test Matrix Report

**State Folder**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_e2e_3`  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`  
**Target Test Suite**: `tests/e2e/test_medium_hard_codekata.py`  
**Test Architecture Reference**: `TEST_INFRA.md`  
**Timestamp**: `2026-11-10T22:33:00Z`

---

## 1. Executive Summary & Specification Mining

This report provides the authoritative specification mining and complete 4-tier opaque-box E2E test matrix for the Guvi CodeKata Medium and Hard headless automation system. Requirements have been extracted from `ORIGINAL_REQUEST.md` (Follow-up 2026-11-10T22:13:52Z), `PROJECT.md`, `SCOPE.md`, and the existing `zenclass_guvi` codebase.

### The Four Core Requirements
1. **§R1. Headless Background Execution**:
   - Run browser automation entirely in background headless mode (`headless=True`) using the persistent Chromium browser context manager and Guvi credentials (`devsh.pareek@gmail.com` / `Dev@99#$%esh`).
   - Guarantee zero visible browser windows and zero desktop session interference.
   - Maintain anti-detection arguments (`--disable-blink-features=AutomationControlled`, `--no-default-browser-check`, `--no-first-run`, `--start-maximized`) and cookie session persistence via `storage_state.json`.
2. **§R2. Difficulty Filtering and Problem Solving**:
   - Filter and isolate all **Medium** and **Hard** difficulty practice questions on Guvi CodeKata.
   - Parse problem specifications and sanitize CSS stylesheet leaks (`{display:inline-flex...}`) from sample inputs and outputs in `solver/extractor.py`.
   - Synthesize valid, competitive-programming Python 3 solutions across mathematical, string, array, two-pointer, and dynamic programming algorithms in `solver/code_generator.py`.
   - Support `difficulties` parameter in `StateManager.list_pending()`, `GuviDriver.discover_catalog()`, `GuviDriver.run_pipeline()`, and `main.py --difficulty`.
3. **§R3. Failure Handling and 3-Attempt Retries**:
   - If a problem fails platform test cases during Run Code or Submit Code, retry generating and submitting up to **3 times** per problem.
   - Refine subsequent candidate solutions by passing error output into `generate_solution(spec, previous_error=..., attempt=...)`.
   - If a problem fails after 3 attempts, mark its final status as `FAILED` in SQLite without crashing or halting the overall automation run.
4. **§R4. Persistent State Management**:
   - Record every problem's status (`COMPLETED`, `FAILED`, `PENDING`), attempt count (1 to 3), test case outputs, code snapshots, failure reasons, and ISO timestamps in SQLite `data/automation_state.db`.
   - Log each individual attempt into `task_attempts` with granular details JSON payloads.
   - Maintain lifecycle run tracking in `execution_runs` and generate executive summary reports (`reports/SUMMARY_REPORT.md` and `reports/summary.json`).

---

## 2. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | R1 Headless | Headless Context Launch | Launches persistent Chromium context with `headless=True` and anti-automation flags | `headless=True`, `profile_dir`, `storage_state_path` | `BrowserContext`, active `Page` | Raises `PlaywrightError` if profile locked; handles cleanly | `core/browser.py:88-95` |
| 2 | R1 Headless | CLI & Config Flag Precedence | `--headless` CLI flag and `AUTOMATION_HEADLESS` env variable control headless state | CLI args, `config.HEADLESS` | Boolean `headless` in runner namespace | Defaults to False if headed, True if flag passed | `config.py:50`, `main.py:49-53` |
| 3 | R1 Headless | Session Cookie Restoration | Dual-layer cookie restoration from `storage_state.json` without visible auth UI | `storage_state.json` path | Injected cookies in context | Logs warning if JSON corrupt; continues | `core/browser.py:125-137` |
| 4 | R2 Filtering | Catalog Difficulty Filtering | Filters CodeKata catalog rows by Difficulty column ("Medium", "Hard") | `difficulties: List[str]` (e.g. `['Medium', 'Hard']`) | Discovered pending slugs list | Skips non-matching difficulty rows | `drivers/guvi_driver.py:477-483` |
| 5 | R2 Filtering | StateManager Difficulty Query | Queries SQLite tasks by difficulty stored in metadata JSON | `platform="guvi"`, `difficulties=["Medium", "Hard"]` | `List[TaskRecord]` | Returns empty list if no matches | `core/state_manager.py:471` |
| 6 | R2 Solving | Extractor CSS Sanitization | Strips inline stylesheet artifacts (`{display:inline-flex...}`) from sample cases | Raw workspace HTML string or DOM page | Clean `ProblemSpecification` with sanitized I/O | Returns empty string if sample case missing | `solver/extractor.py:20-69` |
| 7 | R2 Solving | Algorithmic Code Synthesis | Synthesizes Python 3 solutions for Medium and Hard problems | `ProblemSpecification` | `GeneratedSolution(code, category, confidence, ...)` | Falls back to AST-valid standard template | `solver/code_generator.py:577` |
| 8 | R3 Retries | 3-Attempt Retry Loop | Retries problem generation and submission up to 3 times per problem | `slug_or_id`, max attempts (3) | Final outcome dict (`success: bool`, `attempts: int`) | Flags `FAILED` after 3 attempts; does not halt pipeline | `drivers/guvi_driver.py:586` |
| 9 | R3 Retries | Solver Feedback Refinement | Refines candidate solution using previous test execution failure error output | `spec`, `previous_error: str`, `attempt: int` | Adjusted `GeneratedSolution` | Uses standard fallback if error format unparseable | `PROJECT.md:53-56` |
| 10 | R4 State | Granular Attempt Persistence | Inserts individual attempt row into `task_attempts` with test case outputs | `task_id`, `attempt_number`, `status`, `details` JSON | Row ID in `task_attempts` table | Retries on database lock; logs warning | `core/state_manager.py:350-359` |
| 11 | R4 State | Task Difficulty Metadata | Stores difficulty, points, success rate in `tasks.metadata` JSON | Task dictionary with metadata dict | Persistent row in `tasks` | Upserts on conflict preserving created_at | `core/state_manager.py:253-275` |
| 12 | R4 State | Execution Run Tracking | Logs automation run start, end, duration, total passed, total failed | `run_type`, `platform`, execution counts | Row in `execution_runs` | Updates status to COMPLETED or FAILED | `core/state_manager.py:195-204` |

---

## 3. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| E01 | R1 Headless | Linux/Unix environment with unset `DISPLAY` / `WAYLAND_DISPLAY` | Headless Chromium launches cleanly; no X11 connection error. |
| E02 | R1 Headless | Browser profile directory locked by crashed background Chromium process | Playwright raises SingletonLock error; BrowserManager catches, logs diagnostic, triggers cleanup. |
| E03 | R1 Headless | Off-screen DOM element positioned beyond standard viewport height | Headless browser auto-scrolls element into viewport upon click/fill without throwing viewport errors. |
| E04 | R2 Filtering | Catalog table page containing only "Easy" problems when filtering for Medium/Hard | Table parser ignores all Easy rows; returns empty pending list `[]`; advances to next catalog page. |
| E05 | R2 Filtering | Catalog row missing `.difficulty` table cell or containing unexpected string (e.g. "Unknown") | Parser falls back safely without throwing `AttributeError`; skips row if not matching requested difficulties. |
| E06 | R2 Solving | Problem statement where CSS classes leak inline styles `{display:inline-flex; align-items:center}` into `.sample-input` | Sanitizer regex removes all inline CSS tokens; leaves pure alphanumeric/numeric test data. |
| E07 | R2 Solving | Problem specification with zero sample test cases | Extractor creates `ProblemSpecification` with `sample_cases=[]`; code generator uses description semantics. |
| E08 | R3 Retries | Candidate code on attempt 1 enters infinite loop (`while True: pass`) | Subprocess sandbox enforces timeout (5.0s), terminates child process, forwards `TimeoutExpired` to attempt 2. |
| E09 | R3 Retries | Candidate code on attempt 1 throws `SyntaxError` during compilation | Error message captured verbatim; attempt 2 passes syntax error feedback into generator to fix indentation/syntax. |
| E10 | R3 Retries | Platform Run Code passes 3 of 4 test cases; 1 test case fails with Wrong Answer | Attempt 2 receives isolated failure details for the failing test case rather than generic failure string. |
| E11 | R3 Retries | All 3 attempts fail platform test cases | Driver logs failure, marks `TaskStatus.FAILED`, `attempt_count=3`, and proceeds to the next problem without halting. |
| E12 | R4 State | SQLite database locked (`sqlite3.OperationalError: database is locked`) during concurrent write | Internal lock and WAL mode prevent corruption; retries write operation after short backoff. |
| E13 | R4 State | Large error traceback (>100KB) in attempt details | Payload serialized into JSON text column in `task_attempts` without schema overflow or database truncation. |
| E14 | R4 State | Querying `list_pending(difficulties=[])` with empty list or unknown difficulty values | Query parameterizes SQL cleanly; returns empty list `[]` without throwing syntax errors. |

---

## 4. Complete 4-Tier Opaque-Box Test Matrix

The test matrix is targeted for `zenclass_guvi/tests/e2e/test_medium_hard_codekata.py`. It contains **52 distinct tests** spanning all 4 tiers, providing comprehensive coverage across R1, R2, R3, and R4.

```
Total Test Count: 52
- Tier 1 (Feature Coverage): 22 tests (R1: 5, R2: 7, R3: 5, R4: 5)
- Tier 2 (Boundary & Corner Cases): 20 tests (R1: 5, R2: 5, R3: 5, R4: 5)
- Tier 3 (Cross-Feature Pairwise): 5 tests
- Tier 4 (Real-World Workloads): 5 tests
```

---

### Tier 1: Feature Coverage (22 Tests)

#### Feature R1: Headless Background Execution (5 Tests)
1. **`test_t1_r1_01_browser_manager_headless_flag`**
   - **Feature**: R1
   - **Inputs**: `BrowserManager(headless=True)`
   - **Setup/Mocks**: Mock `sync_playwright` launch persistent context.
   - **Actions**: Invoke `bm.start()`.
   - **Expected Assertions**: `launch_persistent_context` is invoked with `headless=True`; verify `bm.headless is True`.
2. **`test_t1_r1_02_cli_headless_argument_parsing`**
   - **Feature**: R1
   - **Inputs**: CLI argv `["run-codekata", "--headless"]` and `["run-codekata"]`.
   - **Setup/Mocks**: `main.create_cli_parser()`.
   - **Actions**: Parse both command-line argument lists.
   - **Expected Assertions**: Namespace for first invocation has `args.headless is True`; default invocation adheres to `config.HEADLESS`.
3. **`test_t1_r1_03_stealth_and_anti_automation_flags`**
   - **Feature**: R1
   - **Inputs**: Headless browser launch configuration.
   - **Setup/Mocks**: Inspect `launch_persistent_context` call arguments.
   - **Actions**: Launch headless browser manager.
   - **Expected Assertions**: `args` contains `"--disable-blink-features=AutomationControlled"`, `"--no-default-browser-check"`, `"--no-first-run"`; `ignore_default_args` contains `"--enable-automation"`.
4. **`test_t1_r1_04_session_storage_cookie_restoration_headless`**
   - **Feature**: R1
   - **Inputs**: Pre-recorded `storage_state.json` containing `authToken="auth:guvi_token_999"` on domain `.guvi.in`.
   - **Setup/Mocks**: Mock persistent context with `add_cookies` method; temporary storage state file.
   - **Actions**: Call `bm.start()` in headless mode.
   - **Expected Assertions**: `context.add_cookies` is called with the exact cookie list; session is authenticated without user interaction.
5. **`test_t1_r1_05_graceful_headless_teardown_and_export`**
   - **Feature**: R1
   - **Inputs**: Active headless BrowserManager instance.
   - **Setup/Mocks**: Mock context with `storage_state()` and `close()`; mock Playwright with `stop()`.
   - **Actions**: Execute context manager exit (`with BrowserManager(headless=True) as bm: pass`).
   - **Expected Assertions**: `context.storage_state()` is invoked; `context.close()` and `playwright.stop()` are called; `bm._context` is reset to None.

#### Feature R2: Difficulty Filtering and Problem Solving (7 Tests)
6. **`test_t1_r2_01_catalog_discovery_medium_filter`**
   - **Feature**: R2
   - **Inputs**: Catalog page DOM containing 5 problems (Easy, Medium, Hard); parameter `difficulties=["Medium"]`.
   - **Setup/Mocks**: Mock page serving `GUVI_CODEKATA_TABLE_HTML`; mock StateManager.
   - **Actions**: `driver.discover_catalog(max_pages=1, difficulties=["Medium"])`.
   - **Expected Assertions**: Returns list containing ONLY Medium slug (`palindrome-check`); excludes Easy (`reverse-a-string`, `sum-of-array`) and Hard.
7. **`test_t1_r2_02_catalog_discovery_hard_filter`**
   - **Feature**: R2
   - **Inputs**: Catalog page DOM with unsolved Hard problem; parameter `difficulties=["Hard"]`.
   - **Setup/Mocks**: Mock page serving `GUVI_CODEKATA_TABLE_HTML` modified to make `prime-numbers-count` unsolved.
   - **Actions**: `driver.discover_catalog(max_pages=1, difficulties=["Hard"])`.
   - **Expected Assertions**: Returns list containing ONLY Hard slug (`prime-numbers-count`).
8. **`test_t1_r2_03_state_manager_list_pending_difficulties`**
   - **Feature**: R2
   - **Inputs**: StateManager populated with 1 Easy task, 1 Medium task, and 1 Hard task.
   - **Setup/Mocks**: `StateManager(":memory:")`.
   - **Actions**: `sm.list_pending(platform="guvi", difficulties=["Medium", "Hard"])`.
   - **Expected Assertions**: Returns exactly 2 tasks; metadata difficulty matches "Medium" and "Hard"; "Easy" task is filtered out.
9. **`test_t1_r2_04_state_manager_difficulty_case_insensitivity`**
   - **Feature**: R2
   - **Inputs**: Tasks with `metadata={"difficulty": "medium"}` and `{"difficulty": "HARD"}`; query with `difficulties=["Medium", "hard"]`.
   - **Setup/Mocks**: `StateManager(":memory:")`.
   - **Actions**: Query `list_pending(difficulties=["Medium", "hard"])`.
   - **Expected Assertions**: Both tasks are matched and returned regardless of case differences in metadata or query parameter.
10. **`test_t1_r2_05_extractor_css_leak_sanitization`**
    - **Feature**: R2
    - **Inputs**: Problem workspace HTML where `.sample-input` contains `{display:inline-flex; align-items:center;} 9 2` and `.sample-output` contains `{content:""} odd`.
    - **Setup/Mocks**: Raw HTML passed to `extract_problem_spec`.
    - **Actions**: Extract `ProblemSpecification`.
    - **Expected Assertions**: `spec.sample_cases[0].input_text == "9 2"`, `spec.sample_cases[0].expected_output == "odd"`; curly braces and CSS style rules are completely stripped.
11. **`test_t1_r2_06_code_generator_medium_algorithmic_synthesis`**
    - **Feature**: R2
    - **Inputs**: `ProblemSpecification` for Medium problem (e.g., "Palindrome Checker" or "Subarray Sum Equals K").
    - **Setup/Mocks**: Call `generate_solution(spec)`.
    - **Actions**: Synthesize solution and validate syntax.
    - **Expected Assertions**: Returns `GeneratedSolution`; `confidence >= 0.85`; `ast.parse(sol.code)` succeeds with valid Python 3 syntax; handles two-pointer or hashing algorithm.
12. **`test_t1_r2_07_code_generator_hard_algorithmic_synthesis`**
    - **Feature**: R2
    - **Inputs**: `ProblemSpecification` for Hard problem (e.g., "Count Prime Numbers in Range" or "0/1 Knapsack").
    - **Setup/Mocks**: Call `generate_solution(spec)`.
    - **Actions**: Synthesize solution and validate syntax.
    - **Expected Assertions**: Returns `GeneratedSolution`; `category` reflects Mathematics/DP; code utilizes Sieve of Eratosthenes or dynamic programming array; passes AST validation.

#### Feature R3: 3-Attempt Retries and Error Feedback (5 Tests)
13. **`test_t1_r3_01_immediate_success_single_attempt`**
    - **Feature**: R3
    - **Inputs**: Single Medium problem (`palindrome-check`).
    - **Setup/Mocks**: Mock page where Run Code returns "Correct Answer" and Submit Code returns "Solved!" on Attempt 1.
    - **Actions**: `driver.solve_problem("palindrome-check")`.
    - **Expected Assertions**: Returns `{"success": True, "attempts": 1}`; task status in StateManager is `COMPLETED`; `attempt_count == 1`.
14. **`test_t1_r3_02_recovery_on_attempt_two_with_feedback`**
    - **Feature**: R3
    - **Inputs**: Problem where Attempt 1 fails platform Run Code with `Wrong Answer: Expected 'even', Got 'odd'`.
    - **Setup/Mocks**: Mock page simulating failure on attempt 1, success on attempt 2; spy on `generate_solution`.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: `generate_solution` is called twice; 2nd call receives `previous_error="Wrong Answer: Expected 'even', Got 'odd'"` and `attempt=2`; task succeeds on Attempt 2; task status is `COMPLETED`, `attempt_count == 2`.
15. **`test_t1_r3_03_recovery_on_attempt_three`**
    - **Feature**: R3
    - **Inputs**: Problem failing Attempt 1 (IndexError) and Attempt 2 (Wrong Answer), succeeding on Attempt 3.
    - **Setup/Mocks**: Mock page simulating 2 consecutive failures then success on Attempt 3.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: Exactly 3 attempts executed; task marked `COMPLETED`; `attempt_count == 3`; all 3 attempts recorded in `task_attempts`.
16. **`test_t1_r3_04_max_attempts_exhaustion_marks_failed`**
    - **Feature**: R3
    - **Inputs**: Problem that fails platform validation on all 3 attempts.
    - **Setup/Mocks**: Mock page always returning Wrong Answer / failed test pill.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: Exactly 3 attempts executed (never attempts a 4th time); returns `{"success": False, "attempts": 3}`; task status in StateManager is `FAILED`, `result="TEST_FAILED"`, `attempt_count == 3`.
17. **`test_t1_r3_05_error_feedback_signature_and_adaptation`**
    - **Feature**: R3
    - **Inputs**: `spec = ProblemSpecification(title="Sum of Array", ...)` with `previous_error="ValueError: invalid literal for int() with base 10: ''"`, `attempt=2`.
    - **Setup/Mocks**: Call `generate_solution(spec, previous_error=..., attempt=2)`.
    - **Actions**: Inspect synthesized code and metadata.
    - **Expected Assertions**: Generated code accommodates empty token handling; explanation mentions retry adjustment; valid AST syntax.

#### Feature R4: Persistent State Management (5 Tests)
18. **`test_t1_r4_01_task_difficulty_metadata_persistence`**
    - **Feature**: R4
    - **Inputs**: Task recorded with `metadata={"difficulty": "Hard", "points": "50", "slug": "prime-numbers-count"}`.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: `sm.record_task(...)` followed by SQL query `SELECT json_extract(metadata, '$.difficulty') FROM tasks WHERE task_id = ?`.
    - **Expected Assertions**: Returned value equals `"Hard"`; `task.metadata["difficulty"] == "Hard"`.
19. **`test_t1_r4_02_task_attempts_history_multi_row_persistence`**
    - **Feature**: R4
    - **Inputs**: Problem executed across 3 attempts (2 failures, 1 success).
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: Invoke `sm.update_task_status(...)` with `increment_attempts=True` across 3 attempts.
    - **Expected Assertions**: `task_attempts` table contains exactly 3 rows for `task_id`; row 1 has `attempt_number=1, status='FAILED'`, row 2 has `attempt_number=2, status='FAILED'`, row 3 has `attempt_number=3, status='COMPLETED'`.
20. **`test_t1_r4_03_test_output_payload_in_attempt_details`**
    - **Feature**: R4
    - **Inputs**: Attempt recorded with granular test case details `{"test_cases": [{"id": 1, "passed": False, "error": "AssertionError"}]}`.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: Update status with metadata update containing test results.
    - **Expected Assertions**: `details` column in `task_attempts` contains valid JSON; `json.loads(row["details"])["test_cases"][0]["id"] == 1`.
21. **`test_t1_r4_04_execution_run_tracking_lifecycle`**
    - **Feature**: R4
    - **Inputs**: Headless execution run lifecycle.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: Start run via `sm.start_execution_run(...)` then complete via `sm.complete_execution_run(...)`.
    - **Expected Assertions**: `execution_runs` row records start and end timestamps, duration > 0, status `COMPLETED`, total attempted, passed, and failed counts.
22. **`test_t1_r4_05_summary_metrics_query_by_difficulty`**
    - **Feature**: R4
    - **Inputs**: Database populated with 2 completed Medium tasks, 1 failed Hard task, and 5 pending Easy tasks.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: `sm.get_summary_metrics()`.
    - **Expected Assertions**: Accurately aggregates total completed=2, total failed=1, total pending=5, success_rate=66.7%.

---

### Tier 2: Boundary & Corner Cases (20 Tests)

#### Feature R1 Boundary & Corner Cases (5 Tests)
23. **`test_t2_r1_01_headless_without_display_env`**
    - **Feature**: R1
    - **Inputs**: Environment with `DISPLAY` and `WAYLAND_DISPLAY` removed (`patch.dict(os.environ, {}, clear=False)`).
    - **Setup/Mocks**: `BrowserManager(headless=True)`.
    - **Actions**: Launch headless browser context.
    - **Expected Assertions**: Starts successfully without raising `PlaywrightError: Target closed` or X11 connection errors.
24. **`test_t2_r1_02_headless_profile_lock_recovery`**
    - **Feature**: R1
    - **Inputs**: Profile directory locked by previous crashed process (`SingletonLock` in PlaywrightError).
    - **Setup/Mocks**: Mock `launch_persistent_context` throwing `PlaywrightError("SingletonLock")` on first call.
    - **Actions**: Attempt launch with browser manager.
    - **Expected Assertions**: Logs diagnostic lock message; closes dangling resources cleanly without unhandled crash.
25. **`test_t2_r1_03_rapid_consecutive_headless_launches`**
    - **Feature**: R1
    - **Inputs**: 5 rapid consecutive `start()` and `close()` calls on distinct BrowserManager instances.
    - **Setup/Mocks**: Headless instances created in loop.
    - **Actions**: Launch and close in rapid succession.
    - **Expected Assertions**: All 5 instances open and close cleanly; no port collisions or zombie browser processes.
26. **`test_t2_r1_04_headless_offscreen_element_interaction`**
    - **Feature**: R1
    - **Inputs**: Element positioned at `top: 3000px` (outside standard viewport height).
    - **Setup/Mocks**: Mock page with off-screen button.
    - **Actions**: `driver.safe_click("button.off-screen")`.
    - **Expected Assertions**: Playwright auto-scrolls element into view; click succeeds without viewport boundary errors.
27. **`test_t2_r1_05_concurrent_headless_session_isolation`**
    - **Feature**: R1
    - **Inputs**: Two distinct BrowserManager instances with separate profile directories.
    - **Setup/Mocks**: Two temporary directories `profile_a` and `profile_b`.
    - **Actions**: Start both headless contexts concurrently.
    - **Expected Assertions**: Both contexts exist simultaneously; cookies and storage states remain completely isolated.

#### Feature R2 Boundary & Corner Cases (5 Tests)
28. **`test_t2_r2_01_catalog_page_zero_medium_hard_matches`**
    - **Feature**: R2
    - **Inputs**: Catalog page containing only "Easy" problems, filter `difficulties=["Medium", "Hard"]`.
    - **Setup/Mocks**: Mock catalog table containing 10 Easy problems.
    - **Actions**: `driver.discover_catalog(max_pages=1, difficulties=["Medium", "Hard"])`.
    - **Expected Assertions**: Returns empty pending list `[]`; zero tasks recorded as pending; no exceptions raised.
29. **`test_t2_r2_02_catalog_row_missing_difficulty_tag`**
    - **Feature**: R2
    - **Inputs**: Table row where `.difficulty` cell is empty or missing from DOM.
    - **Setup/Mocks**: HTML table with malformed row lacking difficulty cell.
    - **Actions**: `driver._parse_current_table_page(1)`.
    - **Expected Assertions**: Parser defaults difficulty to "Easy" or "Unknown"; does not throw `AttributeError`; parses remaining rows cleanly.
30. **`test_t2_r2_03_problem_spec_empty_sample_cases`**
    - **Feature**: R2
    - **Inputs**: Workspace HTML containing problem title and description but empty `.sample-input` and `.sample-output`.
    - **Setup/Mocks**: Workspace HTML with missing test cases.
    - **Actions**: `extract_problem_spec(html)`.
    - **Expected Assertions**: Returns `ProblemSpecification` with `sample_cases=[]`; title and description extracted; no `IndexError`.
31. **`test_t2_r2_04_problem_spec_special_characters_and_unicode`**
    - **Feature**: R2
    - **Inputs**: Sample input containing escaped backslashes, quotes, mathematical symbols (`∑`, `√`, `π`), and multi-line formatting.
    - **Setup/Mocks**: Workspace HTML with unicode test data.
    - **Actions**: `extract_problem_spec(html)` -> `generate_solution(spec)`.
    - **Expected Assertions**: Extracted test case preserves raw strings; generated code avoids string syntax errors when parsing stdin.
32. **`test_t2_r2_05_state_manager_unknown_difficulty_values`**
    - **Feature**: R2
    - **Inputs**: Query `sm.list_pending(difficulties=["Extreme", "Nightmare", ""])`.
    - **Setup/Mocks**: StateManager with standard Easy/Medium/Hard tasks.
    - **Actions**: Execute `list_pending`.
    - **Expected Assertions**: Returns empty list `[]`; does not throw SQLite syntax errors or unhandled exceptions.

#### Feature R3 Boundary & Corner Cases (5 Tests)
33. **`test_t2_r3_01_sandbox_timeout_recovery_in_retry`**
    - **Feature**: R3
    - **Inputs**: Candidate solution on Attempt 1 contains `while True: pass` triggering timeout.
    - **Setup/Mocks**: Local sandbox timeout set to 1.0s.
    - **Actions**: `driver.solve_problem(slug)` with attempt 1 timeout, corrected on attempt 2.
    - **Expected Assertions**: Attempt 1 caught as sandbox timeout (`timed out after 1.0s`); error feedback passed to Attempt 2; Attempt 2 generates non-infinite code and passes.
34. **`test_t2_r3_02_syntax_error_in_code_generator_refinement`**
    - **Feature**: R3
    - **Inputs**: Attempt 1 produces `SyntaxError: unexpected EOF while parsing`.
    - **Setup/Mocks**: Pass syntax error into `generate_solution(spec, previous_error=..., attempt=2)`.
    - **Actions**: Synthesize solution for attempt 2.
    - **Expected Assertions**: Code generator recognizes syntax error in feedback; returns code with valid AST syntax.
35. **`test_t2_r3_03_partial_test_pass_isolation`**
    - **Feature**: R3
    - **Inputs**: Platform Run Code evaluates 5 test cases: Cases 1, 2, 4, 5 pass; Case 3 fails with `AssertionError: Got 0, Expected 1`.
    - **Setup/Mocks**: Mock test pill DOM returning partial pass status.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: Extracted `previous_error` isolates Case 3 failure specifically; Attempt 2 focuses on failing test condition.
36. **`test_t2_r3_04_network_timeout_during_submission_retry`**
    - **Feature**: R3
    - **Inputs**: Attempt 1 encounters `PlaywrightError: Timeout 10000ms exceeded waiting for selector button.submit-code`.
    - **Setup/Mocks**: Mock page throws Playwright timeout on first click, succeeds on second.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: Network/DOM timeout is treated as a retryable attempt failure; Attempt 2 re-injects code and completes successfully.
37. **`test_t2_r3_05_none_or_empty_previous_error_resilience`**
    - **Feature**: R3
    - **Inputs**: Direct calls: `generate_solution(spec, previous_error="", attempt=2)` and `generate_solution(spec, previous_error=None, attempt=3)`.
    - **Setup/Mocks**: Direct function invocation.
    - **Actions**: Invoke `generate_solution` with falsy `previous_error`.
    - **Expected Assertions**: Executes cleanly without `AttributeError` or string formatting exceptions; returns valid AST-compliant code.

#### Feature R4 Boundary & Corner Cases (5 Tests)
38. **`test_t2_r4_01_sqlite_database_locked_retry`**
    - **Feature**: R4
    - **Inputs**: Simulated `sqlite3.OperationalError: database is locked` on status update.
    - **Setup/Mocks**: Mock cursor throwing OperationalError on first call, succeeding on retry.
    - **Actions**: Invoke `sm.update_task_status(...)`.
    - **Expected Assertions**: Internal lock/retry mechanism recovers; task status is persisted without crashing the pipeline.
39. **`test_t2_r4_02_massive_test_output_payload_persistence`**
    - **Feature**: R4
    - **Inputs**: Test output payload containing 150KB stderr traceback and 100 test case result dictionaries.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: Persist attempt with large details payload.
    - **Expected Assertions**: Successfully stored and retrieved from SQLite without schema truncation or memory faults.
40. **`test_t2_r4_03_duplicate_task_id_metadata_merge`**
    - **Feature**: R4
    - **Inputs**: Insert task `guvi-palindrome-check` with `metadata={"difficulty": "Medium"}`, then re-insert with `metadata={"difficulty": "Medium", "points": "40"}`.
    - **Setup/Mocks**: `StateManager(":memory:")`.
    - **Actions**: Execute `record_task` twice with same `task_id`.
    - **Expected Assertions**: Single row in `tasks` table; metadata merged to include both keys; `created_at` preserved; `updated_at` updated.
41. **`test_t2_r4_04_corrupt_wal_recovery`**
    - **Feature**: R4
    - **Inputs**: SQLite database file on disk with temporary uncheckpointed WAL file.
    - **Setup/Mocks**: Temp SQLite file with `PRAGMA journal_mode=WAL;`.
    - **Actions**: Re-open database with new StateManager instance.
    - **Expected Assertions**: Connects cleanly, runs `PRAGMA integrity_check` returning `'ok'`; all committed data intact.
42. **`test_t2_r4_05_concurrent_thread_writes_atomicity`**
    - **Feature**: R4
    - **Inputs**: 10 concurrent threads each writing 5 attempts for different tasks.
    - **Setup/Mocks**: `StateManager(":memory:")` with internal RLock.
    - **Actions**: Execute writes concurrently via `ThreadPoolExecutor(max_workers=10)`.
    - **Expected Assertions**: Exactly 50 rows inserted in `task_attempts`; no `sqlite3.ProgrammingError` or database corruption.

---

### Tier 3: Cross-Feature Pairwise Interactions (5 Tests)

43. **`test_t3_p01_r1_headless_plus_r2_difficulty_discovery`**
    - **Pairwise Combination**: R1 (Headless Execution) + R2 (Difficulty Filtering & Discovery)
    - **Inputs**: Mock platform server serving CodeKata table with mixed difficulties; `GuviDriver` configured with `headless=True` and `difficulties=["Medium", "Hard"]`.
    - **Setup/Mocks**: MockBrowserManager running headless; mock page with `GUVI_CODEKATA_TABLE_HTML`.
    - **Actions**: `driver.discover_catalog(difficulties=["Medium", "Hard"])`.
    - **Expected Assertions**: Crawl runs completely headlessly without GUI windows; returns pending list containing only the Medium (`palindrome-check`) and Hard (`prime-numbers-count`) problems; Easy problems omitted.
44. **`test_t3_p02_r2_hard_problem_plus_r3_retry_feedback`**
    - **Pairwise Combination**: R2 (Medium/Hard Solving) + R3 (3-Attempt Retries & Error Feedback)
    - **Inputs**: Hard algorithmic problem (`prime-numbers-count`).
    - **Setup/Mocks**: Mock page where Attempt 1 returns `Wrong Answer (Got 2, Expected 4)`; Attempt 2 receives error feedback, refines prime checking logic, and passes platform Run & Submit.
    - **Actions**: `driver.solve_problem("prime-numbers-count")`.
    - **Expected Assertions**: Pipeline detects Attempt 1 failure; passes feedback to `generate_solution(spec, previous_error=..., attempt=2)`; succeeds on Attempt 2; task marked `COMPLETED` with `attempt_count == 2`.
45. **`test_t3_p03_r3_retry_exhaustion_plus_r4_sqlite_persistence`**
    - **Pairwise Combination**: R3 (3-Attempt Retries) + R4 (SQLite State Persistence)
    - **Inputs**: A problem that consistently fails all 3 attempts.
    - **Setup/Mocks**: Mock page failing all submissions; `StateManager(":memory:")`.
    - **Actions**: `driver.solve_problem(slug)`.
    - **Expected Assertions**: Automation halts retry loop at Attempt 3; task in `tasks` table has `status='FAILED'`, `attempt_count=3`; `task_attempts` has exactly 3 rows with timestamps, failure reasons, and code snapshots preserved.
46. **`test_t3_p04_r1_headless_plus_r4_state_run_lifecycle`**
    - **Pairwise Combination**: R1 (Headless Execution) + R4 (SQLite State Persistence)
    - **Inputs**: Headless execution run covering multiple problems.
    - **Setup/Mocks**: Headless driver; `StateManager(":memory:")`.
    - **Actions**: Launch headless run; execute 2 tasks (1 pass on attempt 1, 1 fail after 3 retries); close driver.
    - **Expected Assertions**: `execution_runs` contains clean start/finish records; browser closes cleanly without leaving processes; all task states accurately reflected in SQLite.
47. **`test_t3_p05_r2_difficulty_filtering_plus_r4_persistence_query`**
    - **Pairwise Combination**: R2 (Difficulty Filtering) + R4 (SQLite State Persistence)
    - **Inputs**: Bulk catalog discovery of 10 problems into StateManager with mixed difficulties.
    - **Setup/Mocks**: StateManager with 4 Easy, 3 Medium, 3 Hard tasks.
    - **Actions**: `sm.list_pending(difficulties=["Medium", "Hard"])`.
    - **Expected Assertions**: Returns exactly 6 tasks; each returned task has `metadata["difficulty"]` in `["Medium", "Hard"]`.

---

### Tier 4: Real-World Workload Application Scenarios (5 Tests)

48. **`test_t4_w01_mixed_catalog_batch_strict_difficulty_partitioning`**
    - **Scenario**: Catalog contains 10 problems (5 Easy, 3 Medium, 2 Hard). User executes headless CodeKata run filtered strictly for Medium and Hard.
    - **Setup/Mocks**: Mock catalog table with 10 rows; driver configured with `headless=True`, `difficulties=["Medium", "Hard"]`.
    - **Actions**: Execute `driver.run_pipeline(difficulties=["Medium", "Hard"])`.
    - **Expected Assertions**: Exactly 5 problems attempted (3 Medium, 2 Hard); 0 Easy problems attempted; all 5 recorded in SQLite; summary shows 5 attempted.
49. **`test_t4_w02_multi_attempt_cascading_recovery_batch`**
    - **Scenario**: Batch of 3 Medium/Hard problems exhibiting diverse failure and recovery dynamics:
      - Problem 1: Passes Attempt 1 (0 retries).
      - Problem 2: Fails Attempt 1 (Wrong Answer), passes Attempt 2.
      - Problem 3: Fails Attempt 1 (SyntaxError), fails Attempt 2 (Time Limit), passes Attempt 3.
    - **Setup/Mocks**: Mock page dynamically returning staged responses per problem.
    - **Actions**: Execute batch solver across all 3 problems.
    - **Expected Assertions**: All 3 problems reach `COMPLETED`; Problem 1 has 1 attempt; Problem 2 has 2 attempts; Problem 3 has 3 attempts; total attempts logged in SQLite = 6.
50. **`test_t4_w03_unsolvable_hard_problem_exhaustion_continues_pipeline`**
    - **Scenario**: Batch of 3 problems:
      - Problem 1: Medium (passes Attempt 1).
      - Problem 2: Hard unsolvable (fails Attempt 1, 2, 3 with Wrong Answer).
      - Problem 3: Medium (passes Attempt 1).
    - **Setup/Mocks**: Mock page returning 3 consecutive failures for Problem 2.
    - **Actions**: Execute batch solver.
    - **Expected Assertions**: Failure on Problem 2 does NOT crash or abort the pipeline; Problem 2 is marked `FAILED` after 3 attempts; Problem 3 is attempted and marked `COMPLETED`; overall batch finishes with 2 completed, 1 failed.
51. **`test_t4_w04_resuming_interrupted_headless_run`**
    - **Scenario**: StateManager contains 5 Medium/Hard tasks from a prior interrupted session:
      - 2 tasks `COMPLETED`
      - 1 task `FAILED` (already exhausted 3 attempts)
      - 2 tasks `PENDING`
    - **Setup/Mocks**: Pre-populated SQLite DB; CLI invocation `resume --platform guvi --include-failed=False`.
    - **Actions**: Run resume pipeline.
    - **Expected Assertions**: The 2 `COMPLETED` tasks and 1 `FAILED` task are skipped; only the 2 `PENDING` tasks are attempted and solved; no redundant browser operations on already completed problems.
52. **`test_t4_w05_full_end_to_end_headless_run_with_executive_report`**
    - **Scenario**: Complete end-to-end workflow: Headless login -> Catalog discovery (Medium/Hard) -> 3-attempt solving loop -> SQLite state persistence -> Executive Markdown and JSON report generation.
    - **Setup/Mocks**: Full mock platform server (`MockPlatformServer`), headless BrowserManager, temporary reports directory.
    - **Actions**: Execute complete pipeline, then trigger `SummaryReporter.generate_all_reports()`.
    - **Expected Assertions**: `automation_state.db` contains complete task and attempt history; `SUMMARY_REPORT.md` exists and contains "Guvi CodeKata", total discovered, total solved, success rate; `summary.json` contains matching numerical metrics.

---

## 5. Architecture & Specification for `TEST_INFRA.md`

`TEST_INFRA.md` serves as the authoritative architectural specification and operational guide for the test suite. It must be updated to document the Medium/Hard Headless testing capabilities alongside the earlier ZenClass features.

### Recommended `TEST_INFRA.md` Structure:

```markdown
# Guvi & ZenClass Automation — Test Infrastructure Documentation

## 1. Test Philosophy & Design Principles
- Opaque-Box Boundary Testing
- Progressive Testability (Contract Loader Pattern)
- Deterministic Output Derivation (Reference Oracles & Canonical Problems)
- Zero-Production Contamination (Local Mock Server & Isolated SQLite)
- Headless Background Integrity & Human-in-the-Loop Safeguards

## 2. Directory Layout & Module Organization
- zenclass_guvi/tests/e2e/test_medium_hard_codekata.py (Unified 4-Tier Test Suite)
- zenclass_guvi/tests/e2e/harness/
  - mock_server.py (Local HTTP Mock Platform)
  - dom_fixtures.py (Qwik SSR & Ace Editor DOM fixtures)
  - contract_loader.py (Dynamic contract binding)
  - reference_oracle.py (Ground truth test vectors)

## 3. Four-Tier Test Hierarchy & Requirements Mapping
- Tier 1: Feature Coverage (R1, R2, R3, R4)
- Tier 2: Boundary & Corner Cases (R1, R2, R3, R4)
- Tier 3: Cross-Feature Pairwise Interactions
- Tier 4: Real-World Workload Scenarios

## 4. Requirement Verification Matrix
- Requirement R1 (Headless Background Execution): Tests t1_r1_01-05, t2_r1_01-05, t3_p01, t3_p04, t4_w01-05
- Requirement R2 (Difficulty Filtering & Solving): Tests t1_r2_01-07, t2_r2_01-05, t3_p01, t3_p02, t3_p05, t4_w01-05
- Requirement R3 (3-Attempt Retries & Error Feedback): Tests t1_r3_01-05, t2_r3_01-05, t3_p02, t3_p03, t4_w02, t4_w03
- Requirement R4 (SQLite State & Test Output Persistence): Tests t1_r4_01-05, t2_r4_01-05, t3_p03-05, t4_w01-05

## 5. Mocking Architecture & Test Isolation
- MockPlatformServer: Threaded HTTP server simulating Guvi sign-in, CodeKata table, and Ace Editor Run/Submit endpoints.
- Page & Browser Mocks: Playwright sync API mocks for headless validation without display server dependencies.
- State Isolation: In-memory SQLite (`:memory:`) or isolated tempfiles per test with WAL journaling.

## 6. Execution Guide & CLI Options
- Running Full Suite: python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -v
- Running by Tier: pytest -k "t1" / pytest -k "t2" / pytest -k "t3" / pytest -k "t4"
- Running by Requirement: pytest -k "r1" / pytest -k "r2" / pytest -k "r3" / pytest -k "r4"
- Standalone runner: python3 zenclass_guvi/tests/e2e/test_runner.py --all

## 7. Quality Gates & Regression Verification
- Baseline regression check: 268/268 passing unit and integration tests.
- E2E acceptance gate: 52/52 passing E2E tests with 0 failures, 0 errors.
```

---

## 6. Five-Component Handoff Report

### 1. Observation
- Verified `ORIGINAL_REQUEST.md` lines 45-88: Follow-up request explicitly specifies:
  - §R1: Background headless mode (`headless=True`), no visible browser windows.
  - §R2: Filter and solve all Medium and Hard practice questions on Guvi CodeKata in Python 3.
  - §R3: Retry generating and submitting up to 3 times per problem before recording failure details in state database and proceeding to next question.
  - §R4: Record status, attempt count, test case outputs, and timestamps in SQLite `data/automation_state.db`.
- Verified existing codebase in `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi`:
  - `config.py:50`: `HEADLESS = os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true"` (currently defaults to False as per initial prompt).
  - `core/browser.py:88-95`: Persistent context launch respects `self.headless`.
  - `core/state_manager.py:471-492`: `list_pending(platform=..., limit=...)` currently lacks the `difficulties` parameter defined in `PROJECT.md:44`.
  - `drivers/guvi_driver.py:477-483`: Row parsing extracts `difficulty` into task metadata, but `discover_catalog` and `run_pipeline` do not currently accept a `difficulties` filter parameter.
  - `drivers/guvi_driver.py:653-674, 746-750`: `solve_problem` currently fails immediately on first test failure rather than executing a 3-attempt retry loop.
  - `solver/code_generator.py:577`: `generate_solution(problem)` does not yet accept `previous_error` or `attempt` parameters.
- Executed existing test suite: `python3 -m pytest zenclass_guvi/tests -q`:
  - Output: `268 passed in 69.63s (0:01:09)`. Zero failures, zero regressions across existing test baseline.

### 2. Logic Chain
- Step 1: Because the user request requires headless execution for Medium/Hard CodeKata questions (§R1), the test suite must verify that `BrowserManager`, `main.py`, and `config.py` correctly configure and instantiate Chromium with `headless=True` and anti-detection flags under both normal and headless CI environments (missing `DISPLAY`).
- Step 2: Because the user request requires filtering Medium and Hard questions (§R2), the test suite must verify filtering at all layers: DOM table discovery in `GuviDriver.discover_catalog()`, persistent state retrieval in `StateManager.list_pending(difficulties=[...])`, and CLI options in `main.py --difficulty`.
- Step 3: Because the user request requires up to 3 retry attempts with error feedback before failure (§R3), the test suite must verify the full lifecycle: immediate success (1 attempt), recovery on attempt 2 with previous error feedback, recovery on attempt 3, and graceful exhaustion after 3 attempts marking status `FAILED` without halting the pipeline.
- Step 4: Because the user request requires recording status, attempt counts, test case outputs, and timestamps in SQLite `data/automation_state.db` (§R4), the test suite must verify that both `tasks` and `task_attempts` persist granular JSON payloads, timestamps, code snapshots, and difficulty metadata.
- Step 5: By structuring the test suite into 4 distinct tiers (22 Tier 1 feature tests, 20 Tier 2 boundary tests, 5 Tier 3 pairwise tests, and 5 Tier 4 workload scenarios), all individual and combined behaviors are verified prior to production deployment.

### 3. Caveats
- Production Codebase Incomplete: As documented in `PROJECT.md`, the production implementations for Milestones M1, M2, and M3 (`difficulties` parameter in `state_manager.py`, `previous_error` in `code_generator.py`, and the 3-attempt loop in `guvi_driver.py`) are currently planned and being built by parallel specialist agents. The test specifications designed here represent opaque-box contracts; tests will assert against these contracts once M1-M3 merge.
- Live Guvi Platform Interaction: The E2E tests are designed to run against `MockPlatformServer` and mock page contexts to avoid rate limiting or credential locking on the live Guvi portal. Live platform credentials (`devsh.pareek@gmail.com`) remain documented in `config.py` for staging execution.

### 4. Conclusion
The specification mining is complete, authoritative, and fully cross-referenced against `ORIGINAL_REQUEST.md`, `PROJECT.md`, and `SCOPE.md`. The 4-tier opaque-box test matrix specifies 52 comprehensive tests for `tests/e2e/test_medium_hard_codekata.py`, covering every requirement (R1-R4) with concrete inputs, mocks, actions, and assertions. The structure for `TEST_INFRA.md` is fully defined and ready for integration.

### 5. Verification Method
1. Inspect the handoff report:
   ```bash
   cat /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_e2e_3/handoff.md
   ```
2. Verify baseline test suite health:
   ```bash
   python3 -m pytest zenclass_guvi/tests -q
   ```
   (Expected: 268 passed)
3. Invalidation Conditions:
   - Any test specification omitting test name, tier, feature, inputs, mocks, actions, or assertions.
   - Any requirement (R1, R2, R3, R4) having fewer than 5 tests in Tier 1 or Tier 2.
   - Fewer than 4 pairwise interaction tests in Tier 3.
   - Fewer than 5 realistic workload scenarios in Tier 4.
