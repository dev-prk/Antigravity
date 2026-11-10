# Project: AI-OS Phase 3a & Phase 3b

## Architecture
The AI-OS (Artificial Intelligence Operating System) is a model-agnostic, token-disciplined execution environment designed for production workspace use without paid API keys or external service dependencies (Docker, Postgres, Ollama). It runs cleanly on Python 3.9.6 standard library and SQLite3.

```text
~/Documents/Antigravity/AI-OS/
├── AGENTS.md                         # Layer A: System constitution (< 100 lines)
├── .agents/
│   ├── rules/
│   │   ├── security.md               # Secret redaction, destructive command guards
│   │   ├── coding.md                 # Python 3.9.6 stdlib only, type annotations
│   │   └── verification.md           # Independent verification, evidence standards
│   └── skills/                       # Zero-duplication reuse via symlinks
│       ├── claude -> ../../../.agents/skills/claude
│       ├── orchestration -> ../../../.agents/skills/orchestration
│       ├── loop-engineering -> ../../../.agents/skills/loop-engineering
│       └── chain-of-mindset -> ../../../.agents/skills/chain-of-mindset
├── aios/
│   ├── __init__.py
│   ├── models.py                     # Stdlib @dataclass schemas for Task, Step, Evidence, etc.
│   ├── policy.py                     # 5 governance profiles & immutable kernel guardrails
│   ├── db.py                         # SQLite 8-table persistence, WAL, FTS5 facts, append-only triggers
│   ├── ledger.py                     # Task lifecycle state machine & atomic step execution
│   ├── budget.py                     # Token tracking, 80% checkpoint trigger, 95% clean stop
│   └── handoff.py                    # Automated HANDOFF.md generator (<=1.5k tokens) & resumer
├── config/
│   └── policies.json                 # User-configurable governance profiles
├── tests/
│   ├── __init__.py
│   ├── test_layer_a.py               # Invariants, rules, symlinks, policy & guardrails
│   ├── test_db.py                    # SQLite 8 tables, indexes, triggers, FTS5, CRUD
│   ├── test_ledger.py                # Task lifecycle state transitions & step logging
│   ├── test_budget.py                # Token budgeting, 80% checkpoint & 95% stop triggers
│   ├── test_handoff.py               # HANDOFF.md generator (<=1.5k tokens) & resumer
│   ├── test_kill_resume.py           # Automated kill/resume process continuity test
│   └── evaluation/                   # Evaluation benchmark harness adapted from Random Ask
│       ├── aios_runner.py            # Benchmark runner & metric calculator
│       ├── benchmarks.jsonl          # Benchmark scenarios
│       └── test_benchmark_suite.py   # Benchmark test execution
└── README.md                         # System documentation and usage guide
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | AGENTS.md Constitution | Invariant root directives strictly under 100 lines | M1 | R1, Survey |
| 2 | Governance Rules | `.agents/rules/` (`security.md`, `coding.md`, `verification.md`) | M1 | R1, Survey |
| 3 | Skill Reuse Symlinks | Reuse `claude`, `orchestration`, `loop-engineering`, `chain-of-mindset` without duplication | M1 | R1, Survey |
| 4 | Policy Engine | 5 profiles (`READ_ONLY`, `SANDBOX_AUTONOMOUS`, `WORKSPACE_AUTONOMOUS`, `APPROVAL_REQUIRED`, `RESTRICTED`) | M1 | R1, Survey |
| 5 | Immutable Kernel Guardrails | Non-configurable secret redaction and prohibition of external destructive commands | M1 | R1, Survey |
| 6 | SQLite Schema & Tables | 8 tables (`tasks`, `steps`, `evidence`, `decisions`, `facts`, `checkpoints`, `budget_usage`, `audit_log`) | M2 | R2, Survey |
| 7 | Append-Only DB Triggers | Engine-level triggers preventing update/delete on `decisions`, `budget_usage`, `audit_log` | M2 | R2, Survey |
| 8 | FTS5 Facts Search | Full-text search virtual table and sync triggers on `facts` | M2 | R2, Survey |
| 9 | SQLite CRUD Operations | Full create, read, update, list APIs for all entities | M2 | R2, Survey |
| 10 | Task Ledger Engine | Lifecycle state machine (`PENDING`, `PLANNING`, `RUNNING`, `PAUSED`, `AWAITING_APPROVAL`, `COMPLETED`, `FAILED`, `STOPPED_BUDGET_REACHED`) | M3 | R2, Survey |
| 11 | Step Progression & Evidence | Step execution tracking with stdout/stderr recording and content hashing | M3 | R2, Survey |
| 12 | Token Budget Tracker | Accurate token counting with 1.33 words/token heuristic fallback | M3 | R3, Survey |
| 13 | 80% Budget Threshold Trigger | Proactive checkpoint & handoff generation at 80% of budget | M3 | R3, Survey |
| 14 | 95% Clean Stop Boundary | Clean task pause and termination at 95% limit avoiding mid-phase crash | M3 | R3, Survey |
| 15 | HANDOFF.md Generator | Structured markdown generator (Goal, Done, Next Action, Blockers) <= 1.5k tokens | M4 | R2, R3, Survey |
| 16 | HANDOFF.md Resumer | Automated task resumption from `HANDOFF.md` + SQLite checkpoint | M4 | R2, R4, Survey |
| 17 | Zero-Duplicate Step Resume | Resuming execution skips already completed steps and continues from next pending | M4 | R4, Survey |
| 18 | Automated Kill/Resume Test | Automated process kill & seamless resume verification harness | M5 | R4, Survey |
| 19 | Benchmark Evaluation Harness | Adapted offline benchmark runner in `tests/evaluation/` | M5 | R4, Survey |
| 20 | E2E Regression & Tier 5 Hardening | Complete E2E test pass across all tiers with adversarial verification | M5 | R4, Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Design & implement opaque-box test infrastructure and Tiers 1-4 tests, publish `TEST_READY.md` | none | IN_PROGRESS |
| 1 | Layer A Scaffolding & Policy | `AGENTS.md`, `.agents/rules/`, `.agents/skills/` symlinks, `config/policies.json`, `aios/policy.py`, `tests/test_layer_a.py` | none | PLANNED |
| 2 | SQLite State Database Engine | `aios/models.py`, `aios/db.py` (8 tables, triggers, FTS5, CRUD), `tests/test_db.py` | none | PLANNED |
| 3 | Task Ledger & Token Budget | `aios/ledger.py`, `aios/budget.py` (lifecycle states, 80%/95% tripwires), `tests/test_ledger.py`, `tests/test_budget.py` | M2 | PLANNED |
| 4 | Automated HANDOFF Generator & Resumer | `aios/handoff.py` (<= 1.5k tokens constraint, resumption reconciliation), `tests/test_handoff.py` | M2, M3 | PLANNED |
| 5 | Final Milestone: 100% E2E Pass + Kill/Resume + Tier 5 Hardening | Phase 1: 100% E2E tests pass + automated kill/resume test verification; Phase 2: Tier 5 adversarial coverage hardening | E2E, M1, M2, M3, M4 | PLANNED |

## Interface Contracts

### `aios.policy` ↔ `aios.ledger` / `aios.tool`
```python
class PolicyEngine:
    def __init__(self, config_path: Optional[str] = None, workspace_root: Optional[str] = None): ...
    def check_action(self, action_type: str, target_resource: str, profile_override: Optional[str] = None) -> PolicyDecision: ...
    def redact_secrets(self, text: str) -> str: ...
    def execute_safe_command(self, command: str, working_dir: Optional[str] = None) -> CommandResult: ...
```

### `aios.db` ↔ `aios.ledger` / `aios.budget` / `aios.handoff`
```python
class DatabaseManager:
    def __init__(self, db_path: str): ...
    def initialize_schema(self) -> None: ...
    # Tasks CRUD
    def create_task(self, task: Task) -> str: ...
    def get_task(self, task_id: str) -> Optional[Task]: ...
    def update_task_status(self, task_id: str, new_status: str) -> None: ...
    def update_task_budget(self, task_id: str, token_delta: int) -> None: ...
    # Steps CRUD
    def create_step(self, step: Step) -> str: ...
    def get_step(self, step_id: str) -> Optional[Step]: ...
    def update_step_status(self, step_id: str, status: str, result_summary: Optional[str] = None) -> None: ...
    def list_steps(self, task_id: str) -> List[Step]: ...
    # Evidence CRUD
    def record_evidence(self, evidence: Evidence) -> str: ...
    def list_evidence(self, task_id: str) -> List[Evidence]: ...
    # Decisions (Append-only)
    def record_decision(self, decision: Decision) -> str: ...
    def list_decisions(self, task_id: str) -> List[Decision]: ...
    # Facts & FTS5
    def record_fact(self, fact: Fact) -> str: ...
    def search_facts(self, query: str) -> List[Fact]: ...
    # Checkpoints
    def create_checkpoint(self, checkpoint: Checkpoint) -> str: ...
    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]: ...
    # Budget Usage (Append-only)
    def record_budget_usage(self, usage: BudgetUsage) -> str: ...
    def get_total_task_tokens(self, task_id: str) -> int: ...
    # Audit Log (Append-only)
    def record_audit(self, audit: AuditEvent) -> str: ...
    def query_audit_log(self, task_id: Optional[str] = None) -> List[AuditEvent]: ...
```

### `aios.budget` ↔ `aios.ledger`
```python
class BudgetTracker:
    def __init__(self, db: DatabaseManager, task_id: str, token_budget: int): ...
    def track_usage(self, prompt_tokens: int, completion_tokens: int, step_id: Optional[str] = None) -> BudgetStatus: ...
    def check_threshold(self) -> ThresholdStatus: # NORMAL, WARNING_80, HALT_95
    def estimate_tokens(self, text: str) -> int: ...
```

### `aios.handoff` ↔ `aios.db` / `aios.ledger`
```python
class HandoffManager:
    def __init__(self, db: DatabaseManager, workspace_root: str): ...
    def generate_handoff(self, task_id: str, trigger_reason: str) -> str: # Writes HANDOFF.md, <= 1.5k tokens
    def resume_task(self, handoff_path: str) -> ResumeContext: # Reconciles state, returns next pending step
```

## Code Layout
All production code strictly under `/Users/devesh/Documents/Antigravity/AI-OS/`:
- `AGENTS.md`: Root invariants (< 100 lines)
- `.agents/rules/`: Security, coding, and verification rules
- `.agents/skills/`: Symlinks to root skills
- `aios/`: Core runtime modules (`__init__.py`, `models.py`, `policy.py`, `db.py`, `ledger.py`, `budget.py`, `handoff.py`)
- `config/`: Configuration files (`policies.json`)
- `tests/`: Automated unit & integration tests (`test_layer_a.py`, `test_db.py`, `test_ledger.py`, `test_budget.py`, `test_handoff.py`, `test_kill_resume.py`)
- `tests/evaluation/`: Benchmark evaluation runner and datasets
