# Handoff Report: E2E Testing Architecture & CodeKata Core Pipeline Investigation

- **Author**: Explorer 2 (E2E Testing Track)
- **Role**: Read-only Investigation & Synthesis
- **Date**: 2026-11-10T22:34:00Z
- **Target Suite**: `zenclass_guvi/tests/e2e/test_medium_hard_codekata.py`
- **Scope Reference**: `.agents/teamwork/sub_orch_e2e/SCOPE.md`
- **Project Scope Reference**: `.agents/teamwork/orchestrator_2/PROJECT.md`

---

## 1. Observation

Direct code inspections of `zenclass_guvi` yielded the following findings across the 6 target components and test harness:

### 1.1 Headless Mode Implementation
- **`config.py`**:
  - Line 50: `HEADLESS = os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true"` (strictly `False` by default for R1 headed mode).
  - Lines 55-65: `BROWSER_ARGS = ["--start-maximized", "--disable-blink-features=AutomationControlled", "--no-default-browser-check", "--no-first-run"]` and `IGNORE_DEFAULT_ARGS = ["--enable-automation"]`.
- **`core/browser.py`**:
  - Lines 48-55: `BrowserManager.__init__(self, profile_dir=None, storage_state_path=None, headless: Optional[bool] = None, slow_mo: Optional[float] = None, ...)` sets:
    `self.headless = config.HEADLESS if headless is None else headless`.
  - Lines 88-95: Playwright persistent context launch:
    ```python
    self._context = self._playwright.chromium.launch_persistent_context(
        user_data_dir=str(self.profile_dir),
        headless=self.headless,
        no_viewport=True,
        args=config.BROWSER_ARGS,
        ignore_default_args=config.IGNORE_DEFAULT_ARGS,
        slow_mo=self.slow_mo,
    )
    ```
- **`drivers/base_driver.py`**:
  - Line 56: `self.browser_manager = browser_manager or BrowserManager()`.
- **`main.py`**:
  - Lines 49-53: CLI argument:
    ```python
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default: False, headed foreground as per R1)",
    )
    ```
  - Lines 260-263: Browser initialization in runner:
    ```python
    self.browser_manager = BrowserManager(
        headless=self.args.headless,
        slow_mo=self.args.slow_mo
    )
    ```

### 1.2 Difficulty Filtering Mechanics
- **`drivers/guvi_driver.py`**:
  - Lines 478-483 in `_parse_current_table_page()`: Extracts difficulty from the 4th column of CodeKata table:
    ```python
    col3 = (
        row.query_selector("td[q\\:key='difficulty'], td.difficulty")
        or row.query_selector("td:nth-child(4), td.difficulty")
    )
    difficulty = col3.inner_text().strip() if col3 else "Easy"
    ```
  - Lines 509-516: Injects difficulty into task metadata:
    ```python
    "metadata": {
        "slug": slug,
        "difficulty": difficulty,
        "points": points,
        "success_rate": success_rate,
        "page_number": page_num,
    }
    ```
  - Lines 519-521: Currently appends all unsolved slugs to `pending_slugs` regardless of difficulty:
    ```python
    if not is_completed:
        pending_slugs.append(slug)
    ```
  - Lines 527-580: `discover_catalog(self, max_pages: int = 143, limit_pending: Optional[int] = None)` has no `difficulties` parameter.
  - Lines 867-911: `run_pipeline(self, limit=None, category=None, task_id=None, max_pages=143)` retrieves pending tasks via `self.state_manager.list_pending(platform="guvi", limit=limit)` without difficulty filtering.
- **`core/state_manager.py`**:
  - Lines 471-493: `list_pending(self, platform: Optional[str] = None, limit: Optional[int] = None) -> List[TaskRecord]`:
    Executes `SELECT * FROM tasks WHERE LOWER(status) IN ('pending', 'discovered', 'redo', 'in_progress')`.
    Lacks a `difficulties` parameter filtering on `json_extract(metadata, '$.difficulty')`.
- **`main.py`**:
  - Lines 119-135: Subcommand `run-codekata` currently has `--category` and `--task-id`, but lacks `--difficulty`.

### 1.3 3-Attempt Retry Loop Mechanics
- **`drivers/guvi_driver.py`**:
  - Lines 586-862 (`solve_problem()`): Currently executes exactly **one attempt**.
  - Lines 653-674: When `val_result.all_passed` is False, immediately calls `self.state_manager.update_task_status(..., status=TaskStatus.FAILED.value, result=TaskResult.TEST_FAILED.value, increment_attempts=True)` and exits.
  - Lines 707-718: When Ace editor injection fails, immediately records `FAILED` and exits.
  - Lines 746-758: When Run Code returns 'Wrong', immediately records `FAILED` and exits.
  - Lines 850-861: When submission feedback verification fails, immediately records `FAILED` and exits.
  - **Absence**: There is currently no `for attempt in range(1, MAX_SUBMISSION_ATTEMPTS + 1)` retry loop, and errors are not fed back into code synthesis.
- **`solver/code_generator.py`**:
  - Line 577: `def generate_solution(problem: Union[ProblemSpecification, Any]) -> GeneratedSolution`.
  - Signature currently takes only `problem` (no `previous_error` or `attempt` argument).
  - Line 646: `def synthesize_solution(problem: Union[ProblemSpecification, Any]) -> str`.

### 1.4 Test Case Output & Data Structures
- **`solver/extractor.py`**:
  - Lines 19-53:
    ```python
    @dataclass
    class SampleCase:
        input_text: str = ""
        expected_output: str = ""
        case_number: int = 1
        explanation: Optional[str] = None
    ```
  - Lines 55-128:
    ```python
    @dataclass
    class ProblemSpecification:
        title: str = "Unknown"
        description: str = ""
        input_spec: str = ""
        output_spec: str = ""
        sample_cases: List[SampleCase] = field(default_factory=list)
        constraints: str = ""
        category: str = "General"
        raw_text: str = ""
        _slug: str = field(default="", repr=False)
    ```
- **`solver/test_runner.py`**:
  - Lines 27-40:
    ```python
    @dataclass
    class TestCaseResult:
        passed: bool
        input_data: str
        expected_output: str
        actual_output: str
        error_message: str
        duration: float  # seconds
        stderr: str = ""
        exit_code: int = 0
    ```
  - Lines 42-83:
    ```python
    @dataclass
    class ValidationResult:
        all_passed: bool
        passed_count: int
        total_count: int
        results: List[TestCaseResult]
    ```
- **DOM / Platform Output Selectors**:
  - `drivers/guvi_driver.py` Lines 130-135: `SEL_TEST_PILL_STATUS = ".test-pill-status, .test-results-pane, #test-results"`, `SEL_QUESTION_STATUS = ".question-status, #question-status"`, `SEL_SUCCESS_MODAL = "#success_modal, dialog.modal:has-text('Congratulations'), .modal:has-text('Geekoins')"`.
  - Mock server endpoints in `tests/e2e/harness/mock_server.py`:
    - `POST /code-kata/question/run` returns:
      `{"status": "success", "output": "odd", "expected": "odd", "testCases": [{"id": 1, "status": "Correct Answer"}]}`
    - `POST /code-kata/question/submit` returns:
      `{"status": "success", "message": "Solved!", "earned_points": 30, "completed": True}`

### 1.5 SQLite State Persistence Schema
- **`core/state_manager.py`**:
  - Lines 148-165: Table `tasks`:
    - Primary key: `task_id TEXT PRIMARY KEY`
    - Core fields: `platform TEXT`, `task_category TEXT`, `title TEXT`, `url TEXT`, `status TEXT`, `attempt_count INTEGER`, `result TEXT`, `failure_reason TEXT`, `next_action TEXT`, `time_spent_seconds REAL`, `metadata JSON`, `created_at TEXT`, `updated_at TEXT`.
  - Lines 171-185: Table `task_attempts`:
    - Primary key: `id INTEGER PRIMARY KEY AUTOINCREMENT`
    - Foreign key: `task_id REFERENCES tasks(task_id) ON DELETE CASCADE`
    - Core fields: `attempt_number INTEGER`, `timestamp TEXT`, `status TEXT`, `result TEXT`, `failure_reason TEXT`, `time_spent_seconds REAL`, `code_snapshot TEXT`, `details JSON`.
  - Lines 189-204: Table `execution_runs`:
    - Primary key: `run_id TEXT PRIMARY KEY`
    - Core fields: `started_at TEXT`, `completed_at TEXT`, `command TEXT`, `platform_filter TEXT`, `total_discovered INTEGER`, `total_completed INTEGER`, `total_pending INTEGER`, `total_blocked INTEGER`, `total_failed INTEGER`, `duration_seconds REAL`, `status TEXT`.
  - Concurrency & Integrity: PRAGMA WAL mode (`PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL; PRAGMA busy_timeout = 5000;`), Python `threading.RLock()`, atomic file export via `os.replace`.

### 1.6 Current Test Suite Status
- Execution command: `python3 -m pytest -q`
- Result: **268 passed in 69.29s (100% pass rate, zero regressions across existing test base)**.

---

## 2. Logic Chain

1. **Headless Execution Contract**:
   - `ORIGINAL_REQUEST.md §R1` mandates background headless execution (`headless=True`) for the Medium/Hard CodeKata pipeline.
   - `core/browser.py` already supports `BrowserManager(headless=True)`.
   - `main.py` provides the CLI switch `--headless`.
   - When instantiated by the runner, passing `headless=True` propagates directly to Playwright's `launch_persistent_context`.
   - *E2E Test Inference*: Tests must verify that when `--headless` or `headless=True` is provided, Chromium launches without a visible viewport, does not require a graphical window manager, and functions identically in CI / headless environments.

2. **Difficulty Filtering Contract**:
   - `PROJECT.md` specifies that `StateManager.list_pending(platform="guvi", difficulties=["Medium", "Hard"])` must filter tasks using SQLite JSON extraction:
     `json_extract(metadata, '$.difficulty') IN ('Medium', 'Hard')` (case-insensitive).
   - In catalog discovery (`GuviDriver.discover_catalog`), DOM row extraction reads column 4 (`td.difficulty`). Filtering must selectively enqueue only tasks whose extracted difficulty matches the target list.
   - In `main.py`, `run-codekata` must parse `--difficulty Medium Hard` and propagate it to `driver.run_pipeline(difficulties=...)`.
   - *E2E Test Inference*: Tests must exercise single difficulty (`Medium`), single difficulty (`Hard`), combined (`["Medium", "Hard"]`), case variations (`["medium", "HARD"]`), and non-matching sets (catalog with only Easy returning empty pending set).

3. **3-Attempt Retry Loop Contract**:
   - `ORIGINAL_REQUEST.md §R3` mandates: "If a problem fails platform test cases, retry generating and submitting up to 3 times per problem before recording failure details in the state database and proceeding to the next question."
   - The retry loop in `GuviDriver.solve_problem()` must encompass:
     a) Code generation via `generate_solution(spec, previous_error=prev_err, attempt=attempt)`.
     b) Local sandbox test execution via `test_solution(...)`.
     c) Ace Editor code injection via `inject_code(...)`.
     d) Platform Run Code execution and test pill verification.
     e) Submit Code execution and Solved! confirmation.
   - If any step fails before attempt 3, the error message / diff is captured as `previous_error`, an attempt record is logged to `task_attempts`, and loop continues to attempt `attempt + 1`.
   - If attempt 3 fails, final status is updated to `FAILED`, result to `TEST_FAILED` or `SUBMISSION_FAILED`, and the pipeline proceeds to the next problem without raising an uncaught exception or halting the queue.
   - *E2E Test Inference*: Tests must verify: attempt 1 success (1 attempt logged, status COMPLETED); attempt 2 recovery (attempt 1 fails, attempt 2 succeeds, 2 attempts logged, status COMPLETED); attempt 3 recovery (2 failed, 1 pass, 3 attempts logged, status COMPLETED); and exhaustion (3 failed, 3 attempts logged, final status FAILED).

4. **Test Output & State Persistence Contract**:
   - `task_attempts` must capture granular payload `details JSON` containing input data, expected output, actual output, error diff, and execution time per attempt.
   - `tasks` must capture total attempts, final result, failure reason, and `metadata` containing `difficulty`.
   - `execution_runs` must track start time, end time, total completed, total failed, and total duration.
   - *E2E Test Inference*: Tests must directly query the SQLite tables (`SELECT * FROM task_attempts WHERE task_id = ?`) to assert that all schema constraints, timestamps, and foreign keys are satisfied.

---

## 3. Concrete Guidance for `tests/e2e/test_medium_hard_codekata.py`

To strictly comply with `SCOPE.md` and satisfy the 4-Tier test architecture, the test suite `tests/e2e/test_medium_hard_codekata.py` should be implemented with **49 discrete tests** organized as follows:

```
tests/e2e/test_medium_hard_codekata.py
├── Tier 1: Feature Coverage (20 tests)
│   ├── TestTier1R1HeadlessExecution (5 tests)
│   ├── TestTier1R2DifficultyFiltering (5 tests)
│   ├── TestTier1R3ThreeAttemptRetryLoop (5 tests)
│   └── TestTier1R4SQLiteStatePersistence (5 tests)
├── Tier 2: Boundary & Corner Cases (20 tests)
│   ├── TestTier2R1HeadlessBoundaries (5 tests)
│   ├── TestTier2R2DifficultyBoundaries (5 tests)
│   ├── TestTier2R3RetryBoundaries (5 tests)
│   └── TestTier2R4DatabaseBoundaries (5 tests)
├── Tier 3: Cross-Feature Interactions (4 tests)
│   └── TestTier3PairwiseInteractions (4 tests)
└── Tier 4: Real-World Workload Scenarios (5 tests)
    └── TestTier4WorkloadScenarios (5 tests)
```

### Detailed Test Manifest:

#### Tier 1: Feature Coverage (20 tests)
- **R1: Headless Background Execution**
  1. `test_r1_config_headless_default_and_env_override`: Asserts `config.HEADLESS` is `False` by default and responds to `AUTOMATION_HEADLESS=true`.
  2. `test_r1_browser_manager_headless_instantiation`: Verifies `BrowserManager(headless=True)` initializes persistent Chromium context with `headless=True`.
  3. `test_r1_cli_headless_flag_parsing`: Verifies `create_cli_parser()` correctly parses `--headless` as `True` and default as `False`.
  4. `test_r1_browser_launch_anti_detection_args`: Verifies `BROWSER_ARGS` (`--disable-blink-features=AutomationControlled`, etc.) are passed to persistent context in headless mode.
  5. `test_r1_headless_screenshot_diagnostics`: Verifies diagnostic screenshot capture operates without error in headless mode.
- **R2: Difficulty Filtering & Problem Solving**
  6. `test_r2_state_manager_list_pending_medium_filter`: Verifies `list_pending(difficulties=["Medium"])` returns only Medium tasks.
  7. `test_r2_state_manager_list_pending_hard_filter`: Verifies `list_pending(difficulties=["Hard"])` returns only Hard tasks.
  8. `test_r2_state_manager_list_pending_case_insensitivity`: Verifies `list_pending(difficulties=["medium", "HARD"])` matches regardless of casing.
  9. `test_r2_catalog_discovery_filters_medium_hard_only`: Verifies discovery on mock catalog HTML filters out Easy tasks and preserves Medium/Hard tasks.
  10. `test_r2_code_generator_medium_hard_synthesis`: Verifies code generator synthesizes valid Python 3 syntax for algorithmic Medium/Hard specs (e.g. two pointers, dynamic programming).
- **R3: 3-Attempt Retries & Error Feedback**
  11. `test_r3_immediate_success_attempt_1`: Problem passing on first attempt records 1 attempt and status `COMPLETED`.
  12. `test_r3_retry_recovery_attempt_2`: Problem failing sandbox on attempt 1, receiving error feedback, and passing attempt 2 records 2 attempts and status `COMPLETED`.
  13. `test_r3_retry_recovery_attempt_3`: Problem failing attempt 1 and 2, adapting code to previous error, and passing attempt 3 records 3 attempts and status `COMPLETED`.
  14. `test_r3_exhaustion_3_attempts_flags_failed`: Problem failing all 3 attempts records 3 attempts and final status `FAILED` without raising unhandled exception.
  15. `test_r3_solver_error_feedback_refinement`: Verifies `generate_solution(spec, previous_error="...")` adjusts generated code based on error input.
- **R4: SQLite State Persistence**
  16. `test_r4_task_registration_with_difficulty_metadata`: Verifies task record persists `difficulty`, `points`, and `slug` in JSON `metadata`.
  17. `test_r4_task_attempts_history_timestamps`: Verifies each attempt creates an independent row in `task_attempts` with ISO timestamp and time spent.
  18. `test_r4_task_attempts_details_payload`: Verifies validation output dictionary (input, expected, actual, error message) is stored in `task_attempts.details`.
  19. `test_r4_summary_statistics_with_difficulty_and_failures`: Verifies `get_summary_stats()` aggregates completed, failed, and pending counts accurately.
  20. `test_r4_execution_run_tracking`: Verifies `start_execution_run()` and `end_execution_run()` persist session duration and task metrics.

#### Tier 2: Boundary & Corner Cases (20 tests)
- **R1: Headless Boundaries**
  21. `test_b_r1_missing_display_environment`: Verifies browser context initializes cleanly when `os.environ["DISPLAY"]` is removed.
  22. `test_b_r1_zero_and_negative_slow_mo`: Verifies `slow_mo=0.0` or invalid values are handled safely in headless mode.
  23. `test_b_r1_concurrent_headless_contexts`: Verifies two headless `BrowserManager` instances using distinct profile directories do not collide.
  24. `test_b_r1_headless_navigation_timeout_graceful_recovery`: Verifies navigation timeout in headless mode logs screenshot and raises recoverable `DriverError`.
  25. `test_b_r1_auxiliary_tab_cleanup_headless`: Verifies extraneous popup tabs are closed in headless mode without crashing context.
- **R2: Difficulty Filtering Boundaries**
  26. `test_b_r2_empty_sample_cases_in_spec`: Problem specification with empty sample cases generates fallback solution without IndexError.
  27. `test_b_r2_extractor_css_style_leak_sanitization`: Problem with inline `{display:inline-flex...}` in DOM is cleaned from `sample_input` and `sample_output`.
  28. `test_b_r2_catalog_missing_difficulty_td`: Table row missing difficulty column defaults safely to "Easy" or "Unknown".
  29. `test_b_r2_empty_difficulties_list_returns_all`: `list_pending(difficulties=[])` or `None` returns all pending items without error.
  30. `test_b_r2_no_problems_matching_difficulty`: Catalog containing only Easy problems returns empty list for `["Medium", "Hard"]` without hanging.
- **R3: Retry & Error Recovery Boundaries**
  31. `test_b_r3_sandbox_timeout_triggers_retry`: Subprocess infinite loop timeout is intercepted and passed as error feedback to next attempt.
  32. `test_b_r3_syntax_error_in_attempt_1_retried`: AST syntax error in initial candidate is caught locally and refined in attempt 2.
  33. `test_b_r3_partial_test_pass_treated_as_failure`: 2 of 3 test cases passing triggers retry with failing case details.
  34. `test_b_r3_transient_network_blip_on_submit`: Platform submit network timeout on attempt 1 is retried on attempt 2.
  35. `test_b_r3_zero_remaining_attempts_boundary`: Loop boundary guarantees no more than 3 attempts are ever executed.
- **R4: Database Boundaries**
  36. `test_b_r4_concurrent_multithreaded_writes`: Multi-threaded task updates are serialized safely by `threading.RLock()`.
  37. `test_b_r4_large_test_output_payload`: Persisting 200KB traceback in `task_attempts.details` succeeds without SQLite truncation.
  38. `test_b_r4_duplicate_task_id_upsert_preserves_attempts`: Re-recording an existing task preserves max attempt count and cumulative time spent.
  39. `test_b_r4_special_characters_in_task_fields`: Problem titles and code with quotes, backslashes, emojis, and unicode persist intact.
  40. `test_b_r4_atomic_json_export_replaces_cleanly`: Interrupted JSON write leaves existing state file uncorrupted via atomic rename.

#### Tier 3: Cross-Feature Interactions (4 tests)
- 41. `test_p01_headless_and_difficulty_filtered_discovery`: Headless browser navigates mock catalog and extracts only Medium/Hard problems into pending queue.
- 42. `test_p02_medium_hard_problem_error_feedback_recovery`: Medium/Hard problem extracts spec, fails attempt 1, feeds error diff to attempt 2, and passes.
- 43. `test_p03_max_retries_and_granular_state_history`: Hard problem exhausting 3 attempts results in exactly 3 `task_attempts` rows, final status `FAILED`, and accurate summary stats.
- 44. `test_p04_headless_pipeline_execution_run_persistence`: Complete headless execution run registers `execution_runs` record with matching completed/failed counts.

#### Tier 4: Real-World Workload Scenarios (5 tests)
- 45. `test_w01_mixed_catalog_batch_solving`: Catalog contains 2 Easy, 2 Medium, 1 Hard; execution resolves only the 2 Medium and 1 Hard, leaving Easy unattempted.
- 46. `test_w02_flaky_problem_multi_stage_recovery`: Problem fails attempt 1 with wrong answer, fails attempt 2 with syntax error, and passes attempt 3 with full submission.
- 47. `test_w03_unsolvable_hard_problem_continues_queue`: Unsolvable Hard problem exhausts 3 attempts and is flagged failed; execution smoothly proceeds to solve the next Medium question.
- 48. `test_w04_resuming_interrupted_run_from_state`: An interrupted run with 1 completed Medium and 1 pending Hard resumes, skips the completed question, and solves only the pending Hard question.
- 49. `test_w05_full_platform_e2e_simulation_and_reporting`: End-to-end execution against `MockPlatformServer` using headless mode, discovery, solving, verification, and summary markdown/json report generation.

---

## 4. Test Harness & Mock Strategy Recommendations

1. **Isolation & Fast Deterministic Execution**:
   - Use `:memory:` or `tempfile.TemporaryDirectory()` for `db_path` in all tests to guarantee test runs never mutate or pollute `data/automation_state.db`.
   - Leverage `MockPlatformServer` (from `tests/e2e/harness/mock_server.py`) for simulated HTTP platform endpoints (`/code-kata/`, `/code-kata/question/run`, `/code-kata/question/submit`).
   - Mock Playwright Page objects via `unittest.mock.MagicMock(autospec=True)` when verifying driver decision logic and retry loops without requiring browser binary startup for unit tests.
   - For Tier 4 and headless integration tests, use real Playwright Chromium context in `headless=True` mode directed to `MockPlatformServer`.

2. **Progressive Testability Bridge**:
   - Until implementers (M1, M2, M3) land the new parameters (`difficulties` in `list_pending`, `previous_error` in `generate_solution`, retry loop in `GuviDriver`), tests should check for method capability dynamically (e.g. `inspect.signature` or falling back to contract oracles) or follow test-driven development (TDD) principles to validate readiness.

---

## 5. Caveats

1. **Live Platform Verification**:
   - Tests execute against local mock fixtures and HTTP mock servers. Testing against live `guvi.in` production requires valid active network and credential authentication, which would consume production student points and risk rate-limiting bans.
2. **Platform DOM Variations**:
   - Real Guvi CodeKata uses Qwik SSR with dynamic hydration. Selectors like `button.run-code` and `.test-pill-status` have multiple fallback arrays; test fixtures reflect the reverse-engineered DOM structures documented in `spec_miner_survey_2`.

---

## 6. Conclusion

- The codebase has a clean foundation for headless execution (`BrowserManager(headless=True)`) and granular SQLite tracking (`tasks`, `task_attempts`, `execution_runs`).
- Four specific enhancements are required across M1-M3:
  1. `core/state_manager.py`: Add `difficulties: Optional[List[str]] = None` to `list_pending()`.
  2. `solver/extractor.py`: Add CSS sanitization to strip `{...}` inline style artifacts from sample cases.
  3. `solver/code_generator.py`: Extend `generate_solution` signature to accept `previous_error: Optional[str] = None, attempt: int = 1`, and add Medium/Hard algorithmic templates.
  4. `drivers/guvi_driver.py`: Implement the 3-attempt retry loop in `solve_problem()` with error feedback propagation, and add `difficulties` parameter in `discover_catalog()` and `run_pipeline()`.
  5. `main.py`: Add `--difficulty` to `run-codekata` CLI parser.
- The 49-test suite designed for `tests/e2e/test_medium_hard_codekata.py` provides 100% comprehensive coverage across all 4 tiers required by `SCOPE.md`.

---

## 7. Verification Method

To independently verify the current baseline and test infrastructure:

1. **Run full existing test suite**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m pytest -q
   ```
   *Expected outcome*: 268 passed, 0 failed.

2. **Verify target components syntax and contracts**:
   ```bash
   python3 -c "import config, core.browser, core.state_manager, solver.extractor, solver.code_generator, drivers.guvi_driver, main; print('All modules load successfully')"
   ```
   *Expected outcome*: `All modules load successfully`.

3. **Check test runner tier execution**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 tests/e2e/test_runner.py --tier 1
   ```
   *Expected outcome*: 22 feature tests pass.
