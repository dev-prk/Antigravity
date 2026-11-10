# Scope: E2E Testing Track - Headless Medium/Hard CodeKata Test Suite

## Architecture
- Target project: `zenclass_guvi`
- Test framework: `pytest`
- Test suite target file: `tests/e2e/test_medium_hard_codekata.py`
- Test documentation: `TEST_INFRA.md`, `TEST_READY.md`

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| R1 | Headless Background Execution | Browser automation runs entirely headlessly (`headless=True`) without visible UI windows or desktop interference | E2E | ORIGINAL_REQUEST §R1 |
| R2 | Difficulty Filtering & Solving | Filter Medium and Hard questions, extract problem spec, generate Python 3 solution, submit | E2E | ORIGINAL_REQUEST §R2 |
| R3 | 3-Attempt Retries & Error Feedback | Retry up to 3 times per problem with test feedback before flagging final failure | E2E | ORIGINAL_REQUEST §R3 |
| R4 | SQLite State Persistence | Granular tracking of status, attempt count, test outputs, timestamps in `data/automation_state.db` | E2E | ORIGINAL_REQUEST §R4 |

## Test Methodology (4 Tiers)
- **Tier 1: Feature Coverage** (≥5 tests per feature = 20 tests min)
  - R1: Headless defaults in config, browser launcher flags, stealth arguments, CLI overrides, no-window confirmation
  - R2: Difficulty filtering ('Medium', 'Hard', mixed, case-insensitivity), catalog extraction, Python 3 solution synthesis
  - R3: Immediate success (1 attempt), retry recovery on attempt 2, retry recovery on attempt 3, max attempts exhaustion (failed status after 3), feedback propagation across retries
  - R4: Task insertion with difficulty metadata, attempt history logging with timestamps, test output payload persistence, summary metrics query, execution run tracking
- **Tier 2: Boundary & Corner Cases** (≥5 tests per feature = 20 tests min)
  - R1: Missing display environment variables (CI/headless servers), concurrent session headless isolation
  - R2: Problems with empty sample cases, special character inputs, malformed DOM/CSS leak in spec, no problems found for filter, unknown difficulty tags
  - R3: Network timeout during attempt, syntax error recovery, partial test pass recovery, zero attempts allowed edge, transient platform error
  - R4: Corrupt/locked SQLite database, large test output payloads, concurrent state writes, duplicate task insertions, schema evolution
- **Tier 3: Cross-Feature Interactions** (Pairwise combinations ≥ 4 tests)
  - R1 + R2: Headless end-to-end difficulty filtered discovery and extraction
  - R2 + R3: Hard problem failing attempt 1 with syntax error, recovering on attempt 2
  - R3 + R4: Multi-attempt failure accurately recorded in database with 3 distinct attempt rows and final task status 'failed'
  - R1 + R4: Complete headless run persists execution_runs and tasks cleanly
- **Tier 4: Real-World Workload Scenarios** (≥ 5 scenarios)
  - Scenario 1: Mixed catalog batch containing Easy, Medium, and Hard; only Medium and Hard solved
  - Scenario 2: Flaky problem scenario with 1st attempt wrong answer, 2nd attempt compile error, 3rd attempt passing
  - Scenario 3: Hard problem exhausting all 3 attempts, continuing gracefully to next problem
  - Scenario 4: Resuming an interrupted headless run from SQLite state (skipping already completed Medium/Hard tasks)
  - Scenario 5: End-to-end simulated platform run with multiple problems and final progress report generation

## Milestones / Iteration Status
- Phase: Iteration Loop 2B
- Current step: Survey / Exploration (Spawn 3 Explorers)
