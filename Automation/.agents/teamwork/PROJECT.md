# Project: ZenClass & Guvi CodeKata Automation Suite

## Architecture
- **Runtime Environment**: Python 3.9 + Playwright 1.60.0 on macOS Apple Silicon.
- **Browser Execution**: Headed foreground Chromium (`headless=False`) using persistent browser context (`.browser_profile/`) ensuring continuous real-time visual monitoring on macOS Aqua desktop.
- **State & Data Layer**: SQLite database (`data/automation_state.db`) tracking all task entities across runs with atomic JSON export (`data/state_summary.json`).
- **Problem Solving Engine**: Local autonomous code synthesizer with subprocess test sandbox (`solver/`) verifying candidate solutions against sample inputs/outputs before submission.
- **Platform Drivers**:
  - Guvi CodeKata driver: Ace editor injection, 143-page table discovery, `#completed-icon_svg__a` filtering, Run/Submit API verification.
  - ZenClass driver: Kanban board discovery, dynamic 13-field submission modal, positive confirmation verification (`Task Submitted Suceessfully`).
  - ZenClass projects module: Autonomous local solution generation in `projects/<slug>/`, local build testing, interactive human pause protocol for repository & deployment URLs.
- **Human-in-the-Loop Protocol**: Automatic detection of CAPTCHA, Cloudflare Turnstile, OTP, MFA (`.login-mfa-active`), pausing with audible terminal alert (`\a`) and interactive prompt without fabricating bypass.
- **Reporting Engine**: Generates comprehensive executive Markdown report (`reports/SUMMARY_REPORT.md`) and JSON summary metrics.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Headed Browser Lifecycle | Headed foreground Chromium launch with persistent context & session reuse | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Persistent State Manager | SQLite tracking database & atomic JSON state export across executions | M1 | ORIGINAL_REQUEST §R3 |
| 3 | Human-in-the-Loop Handler | Pause & interactive prompt for CAPTCHA, OTP, MFA, and link prompts | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Reporting Engine | Markdown & JSON summary report generation with counts, success rate, time spent | M1 | ORIGINAL_REQUEST §R3 |
| 5 | Problem Statement Extractor | Parse CodeKata problem title, description, constraints, and sample I/O | M2 | Survey (spec_miner_2) |
| 6 | Autonomous Python 3 Solver | Algorithmic code synthesis engine for common programming patterns | M2 | ORIGINAL_REQUEST §R2 |
| 7 | Subprocess Test Sandbox | Sandboxed execution of candidate solutions against sample I/O | M2 | ORIGINAL_REQUEST §R2 |
| 8 | Ace Editor Keyboard Adapter | Reliable Playwright CDP keyboard text insertion into Ace Editor | M2 | Survey (spec_miner_2) |
| 9 | Guvi Authentication | Direct login & session verification via cookies/localStorage | M3 | ORIGINAL_REQUEST §R1 |
| 10 | CodeKata Table Discovery | Paginate 143 pages, parse metadata, filter solved via `#completed-icon_svg__a` | M3 | Survey (spec_miner_2) |
| 11 | CodeKata Execution & Submit | Run Code (`button.run-code`), parse test pills, Submit (`button.submit-code`), verify `Solved!` | M3 | ORIGINAL_REQUEST §R2 |
| 12 | ZenClass Authentication | Direct SPA login at `/login`, credential submission, token storage in localStorage | M4 | ORIGINAL_REQUEST §R1 |
| 13 | ZenClass Tasks Discovery | Kanban board inspection (Active, Pending, Completed), task detail modal extraction | M4 | Survey (spec_miner_3) |
| 14 | Dynamic Task Submission | Dynamic 13-field modal mapping (Module 41486), URL validation, submit action | M4 | Survey (spec_miner_3) |
| 15 | Task Submission Verification | Verify positive UI confirmation popup (`Task Submitted Suceessfully`) | M4 | ORIGINAL_REQUEST §R3 |
| 16 | ZenClass Projects Discovery | Capstone/project catalog parsing across Active, Pending, Completed | M5 | Survey (spec_miner_3) |
| 17 | Local Project Code Synthesis | Generate complete frontend/backend code, tests, README in `projects/<slug>/` | M5 | ORIGINAL_REQUEST §R2 |
| 18 | Local Project Build Verification | Run local build/lint/test commands to verify generated project health | M5 | ORIGINAL_REQUEST §R2 |
| 19 | Project Human Pause Protocol | Pause execution, emit audio alert, prompt user for repository & deployment URLs | M5 | ORIGINAL_REQUEST §R2 |
| 20 | Project Submission & Verification | Submit project form with user links, verify platform submission confirmation | M5 | ORIGINAL_REQUEST §R2 |
| 21 | Unified CLI Interface | Scaffolding `main.py` with commands (`run-all`, `run-codekata`, `run-zenclass`, `resume`, `report`) | M1 | Architecture Survey |
| 22 | Final E2E Suite Verification | Pass 100% of E2E test suite (Tiers 1-4) and verify live completion | M6 | Dual Track Final Milestone |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Core Foundation & Infrastructure | Headed browser manager, SQLite persistent state manager, HITL handler, reporter, CLI scaffolding | none | DONE |
| 2 | M2: Problem Solver Engine & Sandbox | Problem extractor, Python 3 algorithmic synthesizer, sandboxed test runner, Ace editor adapter | M1 | DONE |
| 3 | M3: Guvi CodeKata Driver & Automation | Authentication, 143-page table discovery, `#completed-icon_svg__a` filtering, Run/Submit lifecycle | M1, M2 | DONE |
| 4 | M4: ZenClass Tasks Driver | Authentication, Kanban discovery, task detail extraction, dynamic 13-field submission, UI confirmation | M1 | DONE |
| 5 | M5: ZenClass Projects Driver & R2 HITL | Project discovery, local solution synthesis in `projects/<slug>/`, local build test, human pause protocol, submission | M1, M4 | IN_PROGRESS |
| 6 | M6: Dual Track Final Milestone | Pass 100% of E2E test suite, live platform verification, final persistent state and summary report | M1, M2, M3, M4, M5, E2E_READY | PLANNED |

## Interface Contracts

### `core/browser.py` ↔ Drivers
- `get_browser_context() -> BrowserContext`: Returns active persistent headed context (`headless=False`).
- `get_page(url: str = None) -> Page`: Returns active page or navigates to specified URL.
- `close_context() -> None`: Gracefully saves cookies and closes browser.

### `core/state_manager.py` ↔ Drivers & Reporter
- `record_task(task_id: str, platform: str, title: str, category: str, url: str, status: str, attempts: int, result: str, failure_reason: str, next_action: str, metadata: dict = None) -> None`
- `get_task(task_id: str) -> Optional[TaskRecord]`
- `get_pending_tasks(platform: Optional[str] = None) -> List[TaskRecord]`
- `get_summary_stats() -> dict`
- `export_state_json() -> str`: Saves and returns path to `data/state_summary.json`.

### `core/hitl_handler.py` ↔ Drivers
- `check_and_handle_guardrails(page: Page) -> bool`: Checks for Cloudflare Turnstile, OTP, MFA (`.login-mfa-active`), `#myModal`. If detected, triggers terminal alert and pauses for human completion.
- `request_project_links(project_title: str, project_id: str, local_code_dir: str, required_fields: List[str]) -> Dict[str, str]`: Pauses with formatted CLI prompt and returns user-supplied URLs.

### `solver/` ↔ `drivers/guvi_driver.py`
- `extract_problem_spec(page: Page) -> ProblemSpec`
- `synthesize_solution(spec: ProblemSpec) -> str`: Returns candidate Python 3 source code.
- `validate_solution(code: str, sample_input: str, sample_output: str) -> ValidationResult`
- `inject_code_into_ace(page: Page, code: str) -> bool`

## Code Layout
```
/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/
├── .browser_profile/                   # Persistent Chrome profile & cookies
├── requirements.txt                    # Dependencies (playwright, etc.)
├── config.py                           # URLs, credentials, paths, timeouts
├── main.py                             # CLI entry point
├── core/
│   ├── __init__.py
│   ├── browser.py                      # Headed browser manager
│   ├── state_manager.py                # SQLite & JSON persistence
│   ├── hitl_handler.py                 # Human-in-the-loop pause manager
│   └── reporter.py                     # Markdown & JSON report generator
├── solver/
│   ├── __init__.py
│   ├── extractor.py                    # Problem description & sample I/O parser
│   ├── code_generator.py               # Python 3 algorithmic synthesizer
│   ├── test_runner.py                  # Sandboxed local subprocess runner
│   └── ace_adapter.py                  # Ace editor keyboard text injection
├── drivers/
│   ├── __init__.py
│   ├── base_driver.py                  # Common navigation & wait helpers
│   ├── guvi_driver.py                  # Guvi CodeKata automation driver
│   └── zenclass_driver.py              # ZenClass tasks & projects driver
├── projects/                           # Local solution code for ZenClass projects
│   └── README.md
├── data/
│   ├── automation_state.db             # SQLite database
│   └── state_summary.json              # State JSON export
├── reports/
│   ├── SUMMARY_REPORT.md               # Executive summary report
│   └── summary.json                    # Machine-readable report
└── tests/
    ├── e2e/                            # Opaque-box E2E test suite (Tiers 1-4)
    │   ├── test_runner.py              # Test runner
    │   ├── tier1_features/             # Tier 1: Feature coverage tests
    │   ├── tier2_boundaries/           # Tier 2: Boundary & corner tests
    │   ├── tier3_pairwise/             # Tier 3: Cross-feature combinations
    │   └── tier4_workloads/            # Tier 4: Real-world end-to-end scenarios
    └── TEST_INFRA.md                   # Test architecture documentation
```
