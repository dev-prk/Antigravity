# ZenClass & Guvi Automation — Test Infrastructure Documentation

## 1. Test Philosophy & Design Principles

The ZenClass and Guvi CodeKata Automation Suite uses a **4-Tier Opaque-Box E2E Testing Architecture** designed to verify system correctness, interface fidelity, and real-world resilience across all platform workflows without relying on internal implementation hacks.

### Core Principles
1. **Opaque-Box Boundary Testing**:
   Tests exercise the system strictly through observable external interfaces: CLI entry points, public API endpoints, persistent SQLite storage, dynamic DOM structures, and subprocess execution outputs.
2. **Progressive Testability**:
   The suite uses a **Dynamic Contract Loader** (`tests/e2e/harness/contract_loader.py`) and standard interface abstractions. During incremental milestone development, tests automatically bind to live modules under `zenclass_guvi` when available, or fall back to canonical specification oracles. This guarantees the entire test suite compiles and runs deterministically at any point in the development lifecycle.
3. **Deterministic Output Derivation**:
   Every expected output is derived from authoritative sources:
   - Official platform specifications reverse-engineered from live DOM and JS bundles (`spec_miner_survey_2`, `spec_miner_survey_3`).
   - Ground-truth mathematical test vectors (`CANONICAL_PROBLEMS` in `reference_oracle.py`).
   - Documented interface contracts from `PROJECT.md` and user requirements from `ORIGINAL_REQUEST.md` (Initial and Follow-up).
4. **Zero-Production Contamination**:
   Automated regression and CI runs execute against a high-fidelity local mock platform server (`MockPlatformServer`) and isolated SQLite instances (`:memory:` or temporary disk files), preventing accidental student point consumption, rate-limiting bans, or premature submission of unverified student code to live production portals.
5. **Headless Background Integrity & Human-in-the-Loop Safeguards**:
   Tests verify that headless mode (`headless=True`) executes quietly in the background without UI popups or desktop session disruption, while security guardrails (CAPTCHA, Cloudflare Turnstile, OTP, MFA, and project repository URL requests) never fabricate bypasses, but reliably trigger alerts, pause execution, and accept valid human inputs.

---

## 2. Directory Layout & Module Organization

```
zenclass_guvi/
├── TEST_INFRA.md                                  # Test infrastructure and architecture documentation
├── TEST_READY.md                                  # Test suite status and execution report
└── tests/
    ├── __init__.py
    ├── test_m1_core.py                            # Milestone 1 Core unit & integration tests
    ├── test_m2_solver.py                          # Milestone 2 Solver unit tests
    ├── test_m3_guvi.py                            # Milestone 3 GuviDriver tests
    ├── test_m4_zenclass_tasks.py                  # Milestone 4 ZenClass tasks tests
    ├── test_m5_zenclass_projects.py               # Milestone 5 ZenClass projects tests
    └── e2e/
        ├── __init__.py
        ├── test_medium_hard_codekata.py           # Unified 4-Tier E2E Suite (Medium/Hard Headless, 52 tests)
        ├── test_runner.py                         # Standalone multi-tier CLI test runner
        ├── harness/                               # Test harness and contract bridges
        │   ├── __init__.py
        │   ├── contract_loader.py                 # Dynamic loader for progressive testability
        │   ├── dom_fixtures.py                    # DOM snapshots reverse-engineered from live platforms
        │   ├── mock_server.py                     # Threaded local HTTP server for simulated platforms
        │   └── reference_oracle.py                # Ground truth mathematical & contract oracles
        ├── tier1_features/                        # Tier 1: Feature Coverage (F01 - F22, 54 tests)
        ├── tier2_boundaries/                      # Tier 2: Boundary & Corner Cases (14 tests)
        ├── tier3_pairwise/                        # Tier 3: Cross-Feature Interactions (6 tests)
        └── tier4_workloads/                       # Tier 4: Real-World Workload Scenarios (4 tests)
```

---

## 3. Four-Tier Test Hierarchy & Requirements Mapping

The E2E test suite partitions verification into four distinct, escalating tiers:

### Tier 1: Feature Coverage (22 Tests)
Verifies discrete requirements in isolation to ensure each capability works according to specification:
- **R1: Headless Background Execution** (5 tests): Configuration defaults, persistent Chromium launch with `headless=True`, anti-automation stealth flags (`--disable-blink-features=AutomationControlled`), cookie session restoration without auth UI, and graceful context teardown.
- **R2: Difficulty Filtering & Problem Solving** (7 tests): Catalog discovery filtering Medium (`palindrome-check`) and Hard (`prime-numbers-count`) questions, SQLite `list_pending` filtering with case insensitivity (`medium`, `HARD`), problem extractor CSS sanitization stripping inline stylesheet artifacts, and Python 3 algorithmic solution synthesis for Medium and Hard problems.
- **R3: 3-Attempt Retries & Error Feedback** (5 tests): Immediate success on Attempt 1, recovery on Attempt 2 via error feedback, recovery on Attempt 3, max attempts exhaustion flagging `FAILED` without crashing the pipeline, and `generate_solution` error adaptation.
- **R4: Persistent State Management** (5 tests): Task difficulty metadata persistence via SQLite JSON extraction, multi-row attempt history logging in `task_attempts`, granular test output payload serialization in `details` JSON, execution run tracking lifecycle in `execution_runs`, and summary metrics aggregation by difficulty.

### Tier 2: Boundary & Corner Cases (20 Tests)
Stress tests extreme inputs, resource limits, and transient error scenarios:
- **R1 Boundaries** (5 tests): Headless operation in CI environments with unset `DISPLAY` and `WAYLAND_DISPLAY`, profile lock recovery from crashed background processes, rapid consecutive launches without resource leaks, off-screen DOM element interaction, and concurrent headless session isolation.
- **R2 Boundaries** (5 tests): Catalog page with zero matching Medium/Hard problems returning empty list, table rows missing difficulty cells defaulting safely, problem specifications with zero sample cases generating defensive fallbacks, Unicode math symbols and escape sequences in problem I/O, and unknown difficulty queries returning empty sets without SQL errors.
- **R3 Boundaries** (5 tests): Subprocess infinite loop timeout interception (0.2s) with error adaptation, `SyntaxError` recovery in candidate solutions, partial test pass isolation (extracting failing cases), transient network timeouts triggering retry, and resiliency when `previous_error` is None or empty.
- **R4 Boundaries** (5 tests): SQLite `busy_timeout=5000` handling database contention, persisting massive 150KB traceback payloads without truncation, duplicate task ID upsert merging metadata while preserving `created_at`, SQLite WAL mode recovery passing `PRAGMA integrity_check`, and multi-threaded concurrent writes serialized safely via `threading.RLock`.

### Tier 3: Cross-Feature Pairwise Interactions (5 Tests)
Validates integration contracts between pairs of system components:
- **R1 + R2**: Headless browser discovering catalog from `MockPlatformServer` and isolating only Medium and Hard problems.
- **R2 + R3**: Hard algorithmic problem failing Attempt 1, passing error feedback to solver, and recovering on Attempt 2.
- **R3 + R4**: 3-attempt failure logging exactly 3 attempt rows in `task_attempts` and setting final task status `FAILED` in `tasks`.
- **R1 + R4**: Complete headless execution persisting `execution_runs` session records and updating task states.
- **R2 + R4**: Catalog batch with mixed difficulties querying `list_pending(difficulties=["Medium", "Hard"])` accurately from SQLite.

### Tier 4: Real-World Workload Scenarios (5 Tests)
Simulates end-to-end operational flows mimicking actual student workloads:
- **Scenario 1**: Mixed catalog batch containing 5 problems (Easy, Medium, Hard); strictly partitions and solves only Medium and Hard questions.
- **Scenario 2**: Flaky problem batch exhibiting diverse retry dynamics (P1: 1 attempt, P2: 2 attempts, P3: 3 attempts); all reach `COMPLETED` with 6 total attempts logged.
- **Scenario 3**: Unsolvable Hard problem exhausts 3 attempts and marks `FAILED`; pipeline does NOT crash and smoothly continues to solve subsequent Medium questions.
- **Scenario 4**: Resuming an interrupted headless run from SQLite state; completed and failed tasks are skipped, solving only pending tasks.
- **Scenario 5**: Full end-to-end simulated run against `MockPlatformServer` in headless mode, solving problems, persisting SQLite state, and generating executive Markdown (`SUMMARY_REPORT.md`) and JSON (`summary.json`) summary reports.

---

## 4. Requirement Verification Matrix

| Requirement | Scope Description | Tier 1 Tests | Tier 2 Tests | Tier 3 Tests | Tier 4 Tests | Total Tests |
|---|---|---|---|---|---|---|
| **§R1: Headless Execution** | Browser automation runs entirely headlessly without UI popups or desktop interference | `test_t1_r1_01` to `test_t1_r1_05` (5) | `test_t2_r1_01` to `test_t2_r1_05` (5) | `test_t3_p01`, `test_t3_p04` (2) | `test_t4_w01`, `test_t4_w05` (2) | **14** |
| **§R2: Difficulty Filtering & Solving** | Filter Medium and Hard questions, extract problem specs, sanitize CSS, synthesize Python 3 | `test_t1_r2_01` to `test_t1_r2_07` (7) | `test_t2_r2_01` to `test_t2_r2_05` (5) | `test_t3_p01`, `test_t3_p02`, `test_t3_p05` (3) | `test_t4_w01` (1) | **16** |
| **§R3: 3-Attempt Retries & Feedback** | Retry up to 3 times with error feedback before marking task failed | `test_t1_r3_01` to `test_t1_r3_05` (5) | `test_t2_r3_01` to `test_t2_r3_05` (5) | `test_t3_p02`, `test_t3_p03` (2) | `test_t4_w02`, `test_t4_w03` (2) | **14** |
| **§R4: SQLite State Persistence** | Record status, attempt count, test outputs, timestamps in `data/automation_state.db` | `test_t1_r4_01` to `test_t1_r4_05` (5) | `test_t2_r4_01` to `test_t2_r4_05` (5) | `test_t3_p03`, `test_t3_p04`, `test_t3_p05` (3) | `test_t4_w02`, `test_t4_w04`, `test_t4_w05` (3) | **16** |
| **TOTAL** | **Comprehensive E2E Coverage** | **22** | **20** | **5** | **5** | **52** |

---

## 5. Mocking Architecture & Test Isolation

1. **`MockPlatformServer` (`tests/e2e/harness/mock_server.py`)**:
   - Lightweight `socketserver.TCPServer` bound dynamically to `127.0.0.1` on port 0.
   - Runs in a background daemon thread with automatic startup and teardown via context manager.
   - Emulates endpoints:
     - `GET /sign-in/`: Returns `GUVI_LOGIN_HTML`
     - `GET /code-kata/`: Returns `GUVI_CODEKATA_TABLE_HTML` with 5 difficulty-tagged rows
     - `GET /code-kata/<slug>/`: Returns `GUVI_WORKSPACE_HTML` with Ace Editor
     - `POST /usercheck.php`: Emulates authentication API
     - `POST /code-kata/question/run`: Emulates platform test run API
     - `POST /code-kata/question/submit`: Emulates submission API returning `Solved!`
     - `GET /health`: Health check endpoint returning `{"status": "healthy"}`
2. **Playwright Mocking vs Real Contexts**:
   - Unit tests use `unittest.mock.patch("core.browser.sync_playwright")` to verify launch arguments, viewport flags, and cookie injection without starting browser binaries.
   - Integration tests leverage headless Chromium persistent contexts directed to `MockPlatformServer`.
3. **Database Isolation**:
   - Tests instantiate `StateManager(":memory:")` or `StateManager(tempfile.mkdtemp() / "state.db")`.
   - Never mutates or accesses production `data/automation_state.db`.
   - Fully tests SQLite WAL journaling, busy timeouts, and `json_extract` filters.

---

## 6. Execution Guide & CLI Options

### Pytest Execution

```bash
# Run the complete Headless Medium/Hard CodeKata E2E test suite (52 tests)
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -v

# Run by Tier
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "TestTier1" -v
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "TestTier2" -v
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "TestTier3" -v
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "TestTier4" -v

# Run by Requirement
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "r1" -v  # Headless Execution
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "r2" -v  # Difficulty Filtering
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "r3" -v  # 3-Attempt Retries
python3 -m pytest zenclass_guvi/tests/e2e/test_medium_hard_codekata.py -k "r4" -v  # SQLite State Persistence

# Run all E2E tests (130 tests across all modules)
python3 -m pytest zenclass_guvi/tests/e2e -v
```

### Standalone CLI Runner

```bash
# Run all 4 legacy E2E tiers (78 tests)
python3 zenclass_guvi/tests/e2e/test_runner.py --all

# Run specific tier or feature
python3 zenclass_guvi/tests/e2e/test_runner.py --tier 1
python3 zenclass_guvi/tests/e2e/test_runner.py --feature F10
```

---

## 7. Quality Gates & Regression Verification

- **Baseline Regression Gate**: All 268 baseline unit and integration tests must pass with 0 regressions.
- **E2E Acceptance Gate**: All 52 tests in `test_medium_hard_codekata.py` must pass with 100% pass rate.
- **Combined E2E Gate**: All 130 E2E tests in `tests/e2e/` must pass in under 15 seconds.
- **Exit Code**: Clean exit code `0` for successful test runs.
