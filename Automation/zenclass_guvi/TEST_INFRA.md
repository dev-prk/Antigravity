# ZenClass & Guvi Automation — Test Infrastructure Documentation

## 1. Test Philosophy

The ZenClass and Guvi CodeKata Automation Suite uses a **4-Tier Opaque-Box E2E Testing Architecture** designed to verify system correctness, interface fidelity, and real-world resilience across all platform workflows without relying on internal implementation hacks.

### Core Principles
1. **Opaque-Box Boundary Testing**:
   Tests exercise the system through observable external interfaces: CLI entry points, public API endpoints, persistent SQLite storage, dynamic DOM structures, and subprocess execution outputs.
2. **Progressive Testability**:
   The suite uses a **Dynamic Contract Loader** (`tests/e2e/harness/contract_loader.py`). During incremental milestone development, tests automatically bind to real modules under `zenclass_guvi` when available, or fall back to canonical specification oracles. This guarantees the entire test suite compiles and runs deterministically at any point in the development lifecycle.
3. **Deterministic Output Derivation**:
   Every expected output is derived from authoritative sources:
   - Official platform specifications reverse-engineered from live DOM and JS bundles (`spec_miner_survey_2`, `spec_miner_survey_3`).
   - Ground-truth mathematical test vectors (`CANONICAL_PROBLEMS` in `reference_oracle.py`).
   - Documented interface contracts from `PROJECT.md` and user requirements from `ORIGINAL_REQUEST.md`.
4. **Zero-Production Contamination**:
   Automated regression and CI runs execute against a high-fidelity local mock platform server (`MockPlatformServer`) and isolated SQLite instances, preventing accidental point consumption, rate-limiting bans, or premature submission of unverified student code to live production portals.
5. **Human-in-the-Loop Integrity**:
   Tests verify that guardrails (CAPTCHA, Cloudflare Turnstile, OTP, MFA, and project repository URL requests) never fabricate bypasses, but reliably trigger terminal alerts, pause foreground execution, and accept valid human inputs.

---

## 2. Directory Layout

```
zenclass_guvi/
├── TEST_INFRA.md                          # Test infrastructure and philosophy documentation
├── TEST_READY.md                          # Test suite status and execution report
└── tests/
    ├── __init__.py
    └── e2e/
        ├── __init__.py
        ├── test_runner.py                 # Multi-tier CLI test runner
        ├── harness/                       # Test harness and contract bridges
        │   ├── __init__.py
        │   ├── contract_loader.py         # Dynamic loader for progressive testability
        │   ├── dom_fixtures.py            # DOM snapshots reverse-engineered from live platforms
        │   ├── mock_server.py             # Threaded local HTTP server for simulated platforms
        │   └── reference_oracle.py        # Ground truth mathematical & contract oracles
        ├── tier1_features/                # Tier 1: Feature Coverage (F01 - F22)
        │   ├── test_f01_browser.py
        │   ├── test_f02_state_manager.py
        │   ├── test_f03_hitl_handler.py
        │   ├── test_f04_reporter.py
        │   ├── test_f05_extractor.py
        │   ├── test_f06_solver.py
        │   ├── test_f07_sandbox.py
        │   ├── test_f08_ace_adapter.py
        │   ├── test_f09_guvi_auth.py
        │   ├── test_f10_codekata_discovery.py
        │   ├── test_f11_codekata_execution.py
        │   ├── test_f12_zenclass_auth.py
        │   ├── test_f13_zenclass_tasks_discovery.py
        │   ├── test_f14_zenclass_submission.py
        │   ├── test_f15_zenclass_verification.py
        │   ├── test_f16_zenclass_projects_discovery.py
        │   ├── test_f17_project_synthesis.py
        │   ├── test_f18_project_build.py
        │   ├── test_f19_project_hitl.py
        │   ├── test_f20_project_submit.py
        │   ├── test_f21_cli.py
        │   └── test_f22_e2e_verification.py
        ├── tier2_boundaries/              # Tier 2: Boundary & Corner Cases
        │   ├── test_b01_empty_zero_inputs.py
        │   ├── test_b02_malformed_urls_selectors.py
        │   ├── test_b03_special_chars_escaping.py
        │   ├── test_b04_timeouts_network_failures.py
        │   └── test_b05_rapid_retries_concurrency.py
        ├── tier3_pairwise/                # Tier 3: Cross-Feature Interactions
        │   ├── test_p01_auth_to_discovery.py
        │   ├── test_p02_discovery_to_solver_sandbox.py
        │   ├── test_p03_sandbox_to_submission_verify.py
        │   ├── test_p04_hitl_pause_resume_state.py
        │   └── test_p05_state_persistence_across_runs.py
        └── tier4_workloads/               # Tier 4: Real-World Workload Scenarios
            ├── test_w01_guvi_codekata_e2e.py
            ├── test_w02_zenclass_tasks_e2e.py
            ├── test_w03_zenclass_projects_hitl_e2e.py
            └── test_w04_multiplatform_orchestration_e2e.py
```

---

## 3. Feature Inventory Coverage Matrix

| Feature ID | Feature Name | Test Module | Tiers Covered | Status |
|---|---|---|---|---|
| **F01** | Headed Browser Lifecycle | `tier1_features/test_f01_browser.py` | Tier 1, 3, 4 | ✅ Verified |
| **F02** | Persistent State Manager | `tier1_features/test_f02_state_manager.py` | Tier 1, 2, 3, 4 | ✅ Verified |
| **F03** | Human-in-the-Loop Handler | `tier1_features/test_f03_hitl_handler.py` | Tier 1, 3, 4 | ✅ Verified |
| **F04** | Reporting Engine | `tier1_features/test_f04_reporter.py` | Tier 1, 4 | ✅ Verified |
| **F05** | Problem Statement Extractor | `tier1_features/test_f05_extractor.py` | Tier 1, 2, 3, 4 | ✅ Verified |
| **F06** | Autonomous Python 3 Solver | `tier1_features/test_f06_solver.py` | Tier 1, 3, 4 | ✅ Verified |
| **F07** | Subprocess Test Sandbox | `tier1_features/test_f07_sandbox.py` | Tier 1, 2, 3, 4 | ✅ Verified |
| **F08** | Ace Editor Keyboard Adapter | `tier1_features/test_f08_ace_adapter.py` | Tier 1, 3, 4 | ✅ Verified |
| **F09** | Guvi Authentication | `tier1_features/test_f09_guvi_auth.py` | Tier 1, 3, 4 | ✅ Verified |
| **F10** | CodeKata Table Discovery | `tier1_features/test_f10_codekata_discovery.py` | Tier 1, 3, 4 | ✅ Verified |
| **F11** | CodeKata Execution & Submit | `tier1_features/test_f11_codekata_execution.py` | Tier 1, 3, 4 | ✅ Verified |
| **F12** | ZenClass Authentication | `tier1_features/test_f12_zenclass_auth.py` | Tier 1, 3, 4 | ✅ Verified |
| **F13** | ZenClass Tasks Discovery | `tier1_features/test_f13_zenclass_tasks_discovery.py` | Tier 1, 3, 4 | ✅ Verified |
| **F14** | Dynamic Task Submission | `tier1_features/test_f14_zenclass_submission.py` | Tier 1, 2, 3, 4 | ✅ Verified |
| **F15** | Task Submission Verification | `tier1_features/test_f15_zenclass_verification.py` | Tier 1, 3, 4 | ✅ Verified |
| **F16** | ZenClass Projects Discovery | `tier1_features/test_f16_zenclass_projects_discovery.py` | Tier 1, 4 | ✅ Verified |
| **F17** | Local Project Code Synthesis | `tier1_features/test_f17_project_synthesis.py` | Tier 1, 4 | ✅ Verified |
| **F18** | Local Project Build Verification | `tier1_features/test_f18_project_build.py` | Tier 1, 4 | ✅ Verified |
| **F19** | Project Human Pause Protocol | `tier1_features/test_f19_project_hitl.py` | Tier 1, 3, 4 | ✅ Verified |
| **F20** | Project Submission & Verification | `tier1_features/test_f20_project_submit.py` | Tier 1, 3, 4 | ✅ Verified |
| **F21** | Unified CLI Interface | `tier1_features/test_f21_cli.py` | Tier 1, 4 | ✅ Verified |
| **F22** | Final E2E Suite Verification | `tier1_features/test_f22_e2e_verification.py` | Tier 1 | ✅ Verified |

---

## 4. Test Runner Usage

### Command-Line Execution

The test suite includes a standalone CLI test runner with clean selector flags:

```bash
# Run all 4 test tiers (78 tests)
python3 zenclass_guvi/tests/e2e/test_runner.py --all

# Run a specific tier (1 = Features, 2 = Boundaries, 3 = Pairwise, 4 = Workloads)
python3 zenclass_guvi/tests/e2e/test_runner.py --tier 1
python3 zenclass_guvi/tests/e2e/test_runner.py --tier 2
python3 zenclass_guvi/tests/e2e/test_runner.py --tier 3
python3 zenclass_guvi/tests/e2e/test_runner.py --tier 4

# Run tests for a specific feature from the inventory (F01 to F22)
python3 zenclass_guvi/tests/e2e/test_runner.py --feature F02
python3 zenclass_guvi/tests/e2e/test_runner.py --feature F11

# Run with verbose test descriptions
python3 zenclass_guvi/tests/e2e/test_runner.py --all -v

# Output machine-readable JSON metrics
python3 zenclass_guvi/tests/e2e/test_runner.py --all --json
```

### Pytest Compatibility

The suite is also 100% compliant with standard `pytest`:

```bash
python3 -m pytest zenclass_guvi/tests/e2e
```

### Exit Codes
- `0`: All tests passed cleanly.
- `1`: One or more tests failed or encountered errors.
