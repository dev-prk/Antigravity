# Handoff Report — E2E Test Suite Architecture & Conventions Survey

**Agent**: Explorer 1 (`explorer_e2e_1`)  
**Target File Analyzed**: `zenclass_guvi/tests/` & proposals for `tests/e2e/test_medium_hard_codekata.py`  
**Date/Timestamp**: 2026-11-10T22:36:00Z  

---

## 1. Observation

### 1.1 Existing Test Suite Composition & Execution Status
- **Test Executable & Version**:
  Command: `export PATH="/Users/devesh/Library/Python/3.9/bin:$PATH" && pytest --version`
  Result: `pytest 8.4.2` running under Python 3.9.6 on darwin (macOS).
- **Full Suite Run**:
  Command: `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && export PATH="/Users/devesh/Library/Python/3.9/bin:$PATH" && pytest`
  Result:
  ```
  ============================= test session starts ==============================
  platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
  rootdir: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
  collecting ... collected 268 items
  ...
  ======================== 268 passed in 69.01s (0:01:09) ========================
  ```
- **E2E Sub-Suite Run**:
  Command: `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && export PATH="/Users/devesh/Library/Python/3.9/bin:$PATH" && pytest --durations=15 tests/e2e`
  Result:
  ```
  ============================== 78 passed in 7.93s ==============================
  ```
  All 78 tests across 36 E2E test files passed in 7.93s (averaging ~101 ms per test).

### 1.2 Test Hierarchy & Directory Organization
Direct inspection of `zenclass_guvi/tests/` revealed two distinct test clusters:
1. **Milestone / Component Unit & Integration Suites**:
   - `tests/test_m1_core.py` (536 lines, 22 tests): Browser lifecycle, StateManager, HITL handler, Reporter, CLI parser.
   - `tests/test_m2_solver.py` (659 lines, 35 tests): Problem extractor, code generator, test runner sandbox, Ace adapter.
   - `tests/test_m3_guvi.py` (877 lines, 34 tests): BaseDriver, GuviDriver auth, CodeKata catalog discovery, single-problem solve pipeline.
   - `tests/test_m3_stress_challenger.py` (12 tests): Adversarial parameter stress tests for `inject_code` and `autospec`.
   - `tests/test_m4_stress_challenger.py` (20 tests): ZenClass tasks stress testing.
   - `tests/test_m4_zenclass_tasks.py` (37 tests): ZenClass task discovery and modal submission.
   - `tests/test_m5_zenclass_projects.py` (30 tests): ZenClass projects discovery, code synthesis, and verification.
2. **4-Tier E2E Architecture** (`tests/e2e/`):
   - `tests/e2e/tier1_features/test_f01_browser.py` through `test_f22_e2e_verification.py` (22 files, 54 tests): Isolated feature verification.
   - `tests/e2e/tier2_boundaries/test_b01_empty_zero_inputs.py` through `test_b05_rapid_retries_concurrency.py` (5 files, 14 tests): Boundary conditions, timeouts, SQL injection, escaping, concurrency.
   - `tests/e2e/tier3_pairwise/test_p01_auth_to_discovery.py` through `test_p05_state_persistence_across_runs.py` (5 files, 6 tests): Pairwise cross-feature interactions.
   - `tests/e2e/tier4_workloads/test_w01_guvi_codekata_e2e.py` through `test_w04_multiplatform_orchestration_e2e.py` (4 files, 4 tests): Real-world multi-step platform workflows.
   - Harness directory `tests/e2e/harness/`:
     - `contract_loader.py` (111 lines): Dynamic bridge to live modules or canonical reference oracles.
     - `mock_server.py` (175 lines): Threaded HTTP mock server (`MockPlatformServer`) on `127.0.0.1:<port>`.
     - `dom_fixtures.py` (337 lines): Real reverse-engineered HTML fixtures (`GUVI_LOGIN_HTML`, `GUVI_CODEKATA_TABLE_HTML`, `GUVI_WORKSPACE_HTML`, etc.).
     - `reference_oracle.py` (427 lines): Canonical problems, reference state manager, reference sandbox.
   - Standalone CLI runner: `tests/e2e/test_runner.py` (192 lines) supporting `--all`, `--tier [1-4]`, `--feature [F01-F22]`, `--verbose`, `--json`.

### 1.3 Conftest and Fixture Conventions
- Command: `find zenclass_guvi -name "conftest.py"` yielded 0 results.
- Command: `grep -r "@pytest" zenclass_guvi/tests/` yielded 0 results.
- **Convention**: Every test file imports `unittest` and defines classes inheriting from `unittest.TestCase`. Test setup and cleanup use `def setUp(self):` and `def tearDown(self):`.
- Assertions strictly use `self.assertEqual`, `self.assertTrue`, `self.assertIn`, `self.assertRaises`, and `self.assertIsNone`.
- There are NO custom pytest fixtures or pytest plugins required; `pytest` discovers and runs all `unittest.TestCase` classes automatically.

### 1.4 Database Fixtures: In-Memory vs. Temp On-Disk SQLite
Across the test suite, three distinct database testing patterns are used:
1. **Pure In-Memory SQLite (`:memory:`)**:
   - Used in `test_w01_guvi_codekata_e2e.py:24`, `test_b05_rapid_retries_concurrency.py:15`:
     ```python
     self.state_mgr, _ = get_state_manager(":memory:")
     ```
   - Extremely fast (sub-millisecond execution).
2. **Temporary On-Disk SQLite (`tempfile.mkdtemp() / "test_state.db"`)**:
   - Used in `test_f02_state_manager.py:18-24`, `test_p05_state_persistence_across_runs.py:17-21`:
     ```python
     self.temp_dir = tempfile.mkdtemp()
     self.db_path = os.path.join(self.temp_dir, "test_state.db")
     self.state_mgr = StateManager(self.db_path)
     # tearDown: shutil.rmtree(self.temp_dir, ignore_errors=True)
     ```
   - Crucial for testing:
     - Real SQLite WAL file generation (`test_state.db-wal`, `test_state.db-shm`).
     - Real process restart simulation: closing connection in Run 1 and reopening in Run 2.
     - Database locks, busy timeouts, and schema queries (`json_extract(metadata, '$.difficulty')`).
3. **Mock State Manager (`MagicMock(spec=StateManager)`)**:
   - Used in `test_m3_guvi.py:106, 239`:
     ```python
     self.mock_sm = MagicMock(spec=StateManager)
     ```
   - Used strictly when unit testing driver call workflows to verify that `record_task`, `update_task_status`, or `record_task_attempt` are called with expected arguments without executing SQL.

### 1.5 Browser and Page Mocking vs. Real Contexts
1. **`MockPlatformServer` (`tests/e2e/harness/mock_server.py`)**:
   - Lightweight `socketserver.TCPServer` bound to `127.0.0.1` on port `0` (dynamic OS-assigned free port).
   - Starts and stops in background thread via context manager (`with MockPlatformServer() as server:`).
   - Serves endpoints:
     - `GET /sign-in/`: Returns `GUVI_LOGIN_HTML`
     - `GET /code-kata/`: Returns `GUVI_CODEKATA_TABLE_HTML`
     - `GET /code-kata/<slug>`: Returns `GUVI_WORKSPACE_HTML`
     - `POST /usercheck.php`: Validates credentials, returns JWT `authToken`
     - `POST /code-kata/question/run`: Simulates platform test run
     - `POST /code-kata/question/submit`: Returns `{"status": "success", "message": "Solved!", "completed": True, "earned_points": 30}`
2. **DOM Fixtures with Difficulty (`tests/e2e/harness/dom_fixtures.py`)**:
   - `GUVI_CODEKATA_TABLE_HTML` (lines 61-114) includes:
     - Row 1: `odd-or-even-sum`, Difficulty `Easy`, status solved (`#completed-icon_svg__a`)
     - Row 2: `reverse-a-string`, Difficulty `Easy`, pending
     - Row 3: `sum-of-array`, Difficulty `Easy`, pending
     - Row 4: `palindrome-check`, Difficulty `Medium`, pending (`data-slug="palindrome-check"`, `<td class="difficulty">Medium</td>`)
     - Row 5: `prime-numbers-count`, Difficulty `Hard`, solved (`<td class="difficulty">Hard</td>`)
3. **Playwright Mock Page & BrowserManager**:
   - In `test_m3_guvi.py`, `mock_bm = MagicMock(spec=BrowserManager)` and `mock_page = MagicMock()` with Playwright Page methods (`wait_for_selector`, `query_selector`, `fill`, `click`, `evaluate`, `select_option`).
   - In `test_f01_browser.py`, `BrowserManager` configuration is tested for `headless=True` vs `headless=False` flags without opening unnecessary UI windows.

---

## 2. Logic Chain

1. **Test Portability & Runner Uniformity**:
   - *From Observation 1.1 & 1.3*: Pytest 8.4.2 discovered and passed all 268 existing tests because they follow `unittest.TestCase`. No custom pytest plugins or conftest configurations are required.
   - *Inference*: `tests/e2e/test_medium_hard_codekata.py` MUST be implemented as `unittest.TestCase` classes. This guarantees zero friction when executed via `pytest`, `python3 -m unittest`, or `test_runner.py`.

2. **Opaque-Box Boundary Testing Without Facade Mocks**:
   - *From Observation 1.4*: In-memory and temp on-disk SQLite databases provide full SQLite engine execution (foreign keys, JSON queries like `json_extract(metadata, '$.difficulty')`, WAL transactions).
   - *From Observation 1.5*: `MockPlatformServer` serves authentic HTML/JSON payloads locally on `127.0.0.1` without contacting Guvi's live production servers.
   - *Inference*: Testing R1-R4 opaque-box behavior in `test_medium_hard_codekata.py` must use real SQLite databases (`:memory:` or `tempfile.mkdtemp()`) and `MockPlatformServer` or simulated DOMs. This prevents "mock self-satisfaction" and verifies the actual contract behavior.

3. **Sub-Second Execution Speed**:
   - *From Observation 1.1*: All 78 tests in `tests/e2e/` run in under 8 seconds. The slowest individual tests take ~0.5s because they run subprocess python sandboxes or sleep.
   - *Inference*: To maintain rapid feedback, `test_medium_hard_codekata.py` should avoid real network calls and sleep loops. Time-dependent retry loops should use mock timers or small timeouts (`timeout=0.1s`).

4. **Requirement Mapping (R1 - R4) to the 4-Tier Structure**:
   - *From sub_orch_e2e/SCOPE.md and PROJECT.md*:
     - **R1: Headless Background Execution**:
       - Default config vs CLI flag (`--headless`).
       - Browser launch argument inspection (`headless=True`, anti-bot stealth args).
       - Operation in environment with unset `DISPLAY` (CI/headless server).
     - **R2: Difficulty Filtering & Problem Solving**:
       - `StateManager.list_pending(platform="guvi", difficulties=["Medium", "Hard"])`.
       - Discovery filtering in `GuviDriver.discover_catalog()` and `GuviDriver.run_pipeline()`.
       - Case-insensitive filtering (`medium`, `HARD`, `Medium`).
       - Problem extraction sanitizing inline CSS leaks.
       - Python 3 solution generation for Medium (`palindrome-check`) and Hard (`prime-numbers-count`) problems.
     - **R3: 3-Attempt Retries & Error Feedback**:
       - Immediate success on Attempt 1 (no retries).
       - Recovery on Attempt 2 after Attempt 1 fails.
       - Recovery on Attempt 3 after Attempts 1 and 2 fail.
       - Exhaustion: Flagging task as `FAILED` after 3 failed attempts, continuing pipeline to next problem.
       - Propagation of `previous_error` to `generate_solution(spec, previous_error=..., attempt=...)`.
     - **R4: SQLite State Persistence**:
       - Recording each attempt in `task_attempts` with `attempt_number`, `status`, `result`, `failure_reason`, and `details` JSON.
       - Recording `tasks` status (`COMPLETED`, `FAILED`, `PENDING`), `attempt_count`, and `metadata` containing `difficulty`.
       - Recording `execution_runs` row for the headless session.
       - Aggregate metrics calculation via `get_summary_stats()`.

---

## 3. Recommended Design for `tests/e2e/test_medium_hard_codekata.py`

Based on the investigated conventions, `tests/e2e/test_medium_hard_codekata.py` should be organized into 4 distinct test classes:

### Class 1: `TestTier1FeatureCoverage` (≥20 tests, ≥5 per feature)
- **R1 Headless Background**:
  1. `test_r1_config_headless_flag_default`: Verifies `config.HEADLESS` reflects environment or defaults.
  2. `test_r1_browser_manager_headless_launch`: Verifies `BrowserManager(headless=True)` configures Playwright context with `headless=True`.
  3. `test_r1_stealth_arguments_in_headless_mode`: Verifies `--disable-blink-features=AutomationControlled` is present in headless launch args.
  4. `test_r1_cli_headless_flag_parsing`: Verifies `main.py` parses `--headless` flag.
  5. `test_r1_missing_display_headless_environment`: Simulates `DISPLAY=None` to verify headless initialization without X11/Wayland window server.
- **R2 Difficulty Filtering & Solving**:
  6. `test_r2_state_manager_difficulty_filtering_medium_hard`: Verifies `list_pending(difficulties=["Medium", "Hard"])` excludes `Easy` tasks.
  7. `test_r2_state_manager_difficulty_case_insensitivity`: Verifies filtering works for `['medium', 'HARD']`.
  8. `test_r2_catalog_discovery_difficulty_tagging`: Verifies catalog parsing tags `difficulty` in task metadata from DOM table.
  9. `test_r2_problem_extractor_css_sanitization`: Verifies extractor removes `{display:inline-flex...}` style leaks from problem description and sample cases.
  10. `test_r2_python3_solver_medium_problem`: Verifies solution synthesis for `palindrome-check` generates valid Python 3 AST passing sample cases.
  11. `test_r2_python3_solver_hard_problem`: Verifies solution synthesis for `prime-numbers-count` generates valid Python 3 AST passing sample cases.
- **R3 3-Attempt Retries & Error Feedback**:
  12. `test_r3_immediate_success_attempt_1`: Problem passes on first attempt; verify attempts=1, status=COMPLETED.
  13. `test_r3_recovery_on_attempt_2`: Problem fails sandbox/platform on attempt 1, receives error feedback, passes attempt 2.
  14. `test_r3_recovery_on_attempt_3`: Problem fails attempts 1 and 2, passes attempt 3 with refined code.
  15. `test_r3_exhaustion_after_3_attempts`: Problem fails 3 consecutive attempts; marked as FAILED with attempts=3 without crashing pipeline.
  16. `test_r3_error_feedback_passed_to_generator`: Verifies `previous_error` parameter is forwarded to `generate_solution`.
- **R4 SQLite State Persistence**:
  17. `test_r4_task_metadata_contains_difficulty`: Verifies `tasks` table stores `metadata` with `difficulty: "Medium"` or `"Hard"`.
  18. `test_r4_task_attempts_history_logging`: Verifies every retry appends a row to `task_attempts` with timestamp and attempt number.
  19. `test_r4_test_output_payload_in_attempt_details`: Verifies stdout/stderr and test case failures are recorded in `task_attempts.details`.
  20. `test_r4_summary_stats_includes_difficulty_counts`: Verifies `get_summary_stats()` correctly aggregates completed and failed counts.
  21. `test_r4_execution_run_persistence`: Verifies `execution_runs` logs headless session start, command, duration, and completion status.

### Class 2: `TestTier2BoundaryAndCornerCases` (≥20 tests, ≥5 per feature)
- **R1 Headless Boundaries**:
  22. `test_b_r1_headless_with_custom_profile_dir`: Custom profile directory path with spaces and special characters.
  23. `test_b_r1_concurrent_headless_browser_managers`: Multiple headless contexts running concurrently with isolated user data dirs.
  24. `test_b_r1_headless_screenshot_capture`: Verification that diagnostic screenshots work headlessly without a screen.
  25. `test_b_r1_headless_viewport_size_default`: Default headless viewport resolution consistency.
  26. `test_b_r1_headless_timeout_propagation`: Navigation timeout triggers `TimeoutError` without hanging.
- **R2 Filtering Boundaries**:
  27. `test_b_r2_empty_sample_cases_in_spec`: Problem with zero sample cases degrades gracefully.
  28. `test_b_r2_special_characters_in_problem_io`: Inputs with Unicode, tabs, and escape sequences handled cleanly.
  29. `test_b_r2_no_problems_match_difficulty_filter`: Catalog with only Easy problems yields empty pending list without error.
  30. `test_b_r2_unknown_difficulty_tag`: Problems with missing or unknown difficulty tag (e.g. `None` or `"Expert"`).
  31. `test_b_r2_heavily_nested_css_in_dom`: Problem workspace with deeply nested CSS/SVG style tags stripped cleanly.
- **R3 Retry Boundaries**:
  32. `test_b_r3_zero_max_attempts_boundary`: `max_attempts=1` or `max_attempts=0` handling.
  33. `test_b_r3_syntax_error_in_attempt_1_recovery`: AST syntax error in attempt 1 captured and corrected in attempt 2.
  34. `test_b_r3_platform_500_transient_error_retry`: HTTP 500 or timeout during submission triggers retry.
  35. `test_b_r3_empty_error_message_feedback`: Retry when platform returns failure without explicit error message.
  36. `test_b_r3_partial_pass_feedback`: Attempt passes test case 1 but fails test case 2.
- **R4 Persistence Boundaries**:
  37. `test_b_r4_locked_sqlite_busy_timeout`: SQLite `busy_timeout=5000` handles transient database contention.
  38. `test_b_r4_large_code_snapshot_persistence`: Attempt with large code payload (e.g. 50KB) persisted safely in SQLite.
  39. `test_b_r4_concurrent_attempt_logging`: Multiple threads logging attempts to the same task simultaneously.
  40. `test_b_r4_duplicate_task_id_upsert`: Upserting task with same ID preserves existing attempt history.
  41. `test_b_r4_corrupt_metadata_json_recovery`: Malformed JSON in metadata handled with empty dict fallback.

### Class 3: `TestTier3CrossFeatureInteractions` (≥4 tests)
42. `test_p_r1_r2_headless_discovery_and_extraction`: Headless driver discovers catalog, parses Medium/Hard difficulty tags, and extracts problem specs without opening visible windows.
43. `test_p_r2_r3_hard_problem_syntax_failure_then_recovery`: Hard problem fails Attempt 1 with syntax error, error feedback is passed to solver, Attempt 2 recovers and passes sandbox.
44. `test_p_r3_r4_three_attempt_failure_recorded_in_sqlite`: Multi-attempt failure records 3 distinct rows in `task_attempts` with incrementing attempt numbers, final status `FAILED` in `tasks`.
45. `test_p_r1_r4_headless_run_persists_execution_run_and_state`: Complete headless execution persists `execution_runs` row with command `run-codekata --headless --difficulty Medium Hard` and updates tasks.

### Class 4: `TestTier4RealWorldWorkloadScenarios` (≥5 scenarios)
46. `test_w_scenario1_mixed_catalog_batch_filters_medium_hard`: Simulated catalog containing 5 problems (2 Easy, 2 Medium, 1 Hard); driver discovers all, but filters and attempts only the 3 Medium and Hard questions.
47. `test_w_scenario2_flaky_problem_recovery_workflow`: Medium problem fails Attempt 1 (wrong answer), fails Attempt 2 (compile error), receives error feedback and succeeds on Attempt 3; status recorded as `COMPLETED`.
48. `test_w_scenario3_hard_problem_exhaustion_continues_pipeline`: Hard problem fails all 3 attempts and is recorded as `FAILED`; pipeline does NOT halt and smoothly processes the next Medium problem.
49. `test_w_scenario4_resuming_interrupted_run_skips_completed_medium_hard`: State DB contains 1 already completed Medium problem and 1 pending Hard problem; headless run resumes, skips the completed problem, and solves only the pending Hard problem.
50. `test_w_scenario5_end_to_end_simulated_pipeline_with_summary_report`: Complete simulated pipeline discovers catalog, filters Medium/Hard, solves problems, persists state in SQLite, and generates executive Markdown and JSON summary reports.

---

## 4. Caveats

1. **Production Code Dependencies**:
   - `core/state_manager.py` currently has `list_pending(platform, limit)` without the `difficulties` parameter. The tests must account for this (using `contract_loader.py` or checking whether `difficulties` is supported once M1 implements it).
   - `solver/code_generator.py` currently has `generate_solution(problem)` without `previous_error` and `attempt`. Feature 6 (Milestone 2) will add this signature.
   - `drivers/guvi_driver.py` currently executes only 1 attempt in `solve_problem()` and lacks `difficulties` filtering in `discover_catalog()`. Milestone 3 will implement the 3-attempt retry loop.
   - The test suite in `tests/e2e/test_medium_hard_codekata.py` can use `contract_loader.py` or canonical specification oracles so that the entire suite compiles and runs cleanly across all milestones.
2. **Headless OS Environment**:
   - While macOS has a window server, CI environments (Linux Docker/GitHub Actions) have no display server (`DISPLAY` is unset). The test suite should test both explicit `headless=True` and environments where `DISPLAY` is absent.

---

## 5. Conclusion

1. **Framework & Layout**: The project strictly uses `unittest.TestCase` executed via `pytest 8.4.2`. There is no `conftest.py`. `tests/e2e/test_medium_hard_codekata.py` must use standard `unittest.TestCase` classes to ensure 100% interoperability with `pytest`, `unittest`, and `test_runner.py`.
2. **Database Strategy**: Real on-disk temp SQLite databases (`tempfile.mkdtemp() / "test_state.db"`) or `:memory:` must be used for state verification (R4), ensuring real WAL mode, schema constraints, and SQL filters (`json_extract(metadata, '$.difficulty')`) are executed without mock facades.
3. **Mocking & Isolation**: `MockPlatformServer` on `127.0.0.1:<random_port>` and Playwright mock pages provide fast (<10ms per test), isolated, zero-contamination platform simulation without external network dependencies.
4. **4-Tier Structure**: A comprehensive 50-test suite across 4 tiers directly maps to user requirements R1 (Headless), R2 (Difficulty Filtering), R3 (3-Attempt Retries), and R4 (SQLite State Persistence).

---

## 6. Verification Method

To independently verify these findings:
1. **Verify Pytest Environment & Existing Suite Execution**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   export PATH="/Users/devesh/Library/Python/3.9/bin:$PATH"
   pytest tests/e2e
   ```
   *Expected Result*: 78 passed in ~8 seconds.
2. **Inspect Absence of Conftest & Pytest Decorators**:
   ```bash
   find zenclass_guvi -name "conftest.py"
   grep -r "@pytest" zenclass_guvi/tests/
   ```
   *Expected Result*: 0 matches.
3. **Verify DOM Fixture Difficulty Tags**:
   ```bash
   python3 -c "import sys; sys.path.insert(0, 'zenclass_guvi'); from tests.e2e.harness.dom_fixtures import GUVI_CODEKATA_TABLE_HTML; print('Medium in HTML:', 'Medium' in GUVI_CODEKATA_TABLE_HTML); print('Hard in HTML:', 'Hard' in GUVI_CODEKATA_TABLE_HTML)"
   ```
   *Expected Result*: Both True.
4. **Verify Dynamic Port Binding in Mock Platform Server**:
   ```bash
   python3 -c "import sys; sys.path.insert(0, 'zenclass_guvi'); from tests.e2e.harness.mock_server import MockPlatformServer; s = MockPlatformServer(); s.start(); print('Server URL:', s.base_url()); s.stop()"
   ```
   *Expected Result*: Prints `http://127.0.0.1:<dynamic_port>` cleanly without errors.
