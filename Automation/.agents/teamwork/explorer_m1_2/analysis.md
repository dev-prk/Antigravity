# Milestone 1: Persistent State Manager & Reporting Engine Architecture Design

**Agent ID**: `explorer_m1_2`  
**Date**: 2026-11-10T15:10:00Z  
**Target Milestone**: Milestone 1 (Core Foundation & Infrastructure)  
**Modules in Scope**: `core/state_manager.py`, `core/reporter.py`, `data/automation_state.db`, `data/state_summary.json`, `reports/SUMMARY_REPORT.md`, `reports/summary.json`  

---

## 1. Executive Summary & Requirement R3 Compliance Matrix

Requirement R3 of `ORIGINAL_REQUEST.md` mandates:
> **R3. Persistent State Management and Progress Reporting**
> - Maintain a persistent state tracking file across executions recording:
>   1. `platform`
>   2. `task identifier`
>   3. `task category`
>   4. `status`
>   5. `attempt count`
>   6. `result`
>   7. `timestamp`
>   8. `failure reason`
>   9. `next action`
> - Produce a summary report providing:
>   1. Total discovered
>   2. Total completed
>   3. Total pending
>   4. Total blocked
>   5. Success rate
>   6. Time spent
>   7. Errors / issues requiring human intervention

### R3 Compliance Verification Matrix

| Requirement Field | SQLite Column (`tasks`) | JSON State Export Key | TaskRecord Dataclass Attribute | Allowed Values / Format | Description |
|---|---|---|---|---|---|
| **Platform** | `platform` | `"platform"` | `platform: str` | `guvi_codekata`, `zenclass_tasks`, `zenclass_projects` | The source portal/system hosting the task |
| **Task Identifier** | `task_id` (PK) | `"task_id"` | `task_id: str` | e.g. `odd-or-even-sum`, `task_18152`, `proj_mern_capstone` | Unique canonical identifier across runs |
| **Task Category** | `task_category` | `"task_category"` | `task_category: str` | e.g. `Easy`, `Basics`, `JavaScript`, `Capstone`, `Fullstack` | Domain category or difficulty tier |
| **Status** | `status` | `"status"` | `status: str` | `DISCOVERED`, `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`, `FAILED` | Current execution state machine position |
| **Attempt Count** | `attempt_count` | `"attempt_count"` | `attempt_count: int` | Integer $\ge 0$ | Total number of execution/submission attempts |
| **Result** | `result` | `"result"` | `result: str` | e.g. `SOLVED`, `SUBMITTED`, `TEST_FAILED`, `CAPTCHA_TRIGGERED` | Execution outcome from platform or sandbox |
| **Timestamp** | `updated_at` | `"timestamp"` | `updated_at: str` | ISO-8601 UTC string (e.g. `2026-11-10T15:30:00Z`) | Exact time of last state mutation |
| **Failure Reason** | `failure_reason` | `"failure_reason"` | `failure_reason: Optional[str]` | e.g. `Test 2 failed: expected 5 got 4`, `Cloudflare challenge`, `None` | Verbatim reason if status is BLOCKED or FAILED |
| **Next Action** | `next_action` | `"next_action"` | `next_action: str` | e.g. `RETRY_WITH_ALTERNATIVE_SOLVER`, `PROMPT_USER_FOR_LINKS`, `SOLVE_AND_SUBMIT`, `NONE_COMPLETED` | Prescribed remediation or subsequent step |

---

## 2. Storage Architecture: SQLite Database & Atomic JSON Export

To guarantee **zero state loss**, **crash resilience**, and **seamless external observability**, the storage layer utilizes a dual-layer strategy:

```
┌────────────────────────────────────────────────────────┐
│                   Python Automation                    │
│     (main.py / guvi_driver / zenclass_driver)          │
└──────────────────────────┬─────────────────────────────┘
                           │
             Reads / Writes via StateManager
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌───────────────────┐       ┌───────────────────┐
   │ SQLite 3 Database │       │ Atomic JSON Sync  │
   │ data/             │       │ data/             │
   │ automation_state  │       │ state_summary     │
   │ .db               │       │ .json             │
   │ (WAL mode, ACID)  │       │ (os.replace swap) │
   └───────────────────┘       └───────────────────┘
```

### 2.1 SQLite Database Schema (`data/automation_state.db`)

SQLite is embedded in Python's standard library (`import sqlite3`), requires no background daemons, and provides full ACID transactions.

#### PRAGMA Configuration
Upon opening connection:
```sql
PRAGMA journal_mode = WAL;         -- Write-Ahead Logging for high concurrency & non-blocking reads
PRAGMA synchronous = NORMAL;       -- Fast disk sync while preventing DB corruption on crash
PRAGMA foreign_keys = ON;          -- Maintain relational integrity for attempt logs
PRAGMA busy_timeout = 5000;        -- Wait up to 5000ms if another process holds a brief lock
PRAGMA cache_size = -64000;        -- 64MB memory cache for fast indexing across 2,000+ items
```

#### Table 1: `tasks` (Primary State Table)
Stores the authoritative current state of every discovered task across platforms.
```sql
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    task_category TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK(status IN ('DISCOVERED', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED', 'FAILED')),
    attempt_count INTEGER NOT NULL DEFAULT 0,
    result TEXT NOT NULL DEFAULT '',
    failure_reason TEXT,
    next_action TEXT NOT NULL DEFAULT '',
    time_spent_seconds REAL NOT NULL DEFAULT 0.0,
    metadata JSON,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_platform_status ON tasks(platform, status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(task_category);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
```

#### Table 2: `task_attempts` (Historical Audit Log)
Stores every historical attempt, test failure, and intermediate result for each task.
```sql
CREATE TABLE IF NOT EXISTS task_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT NOT NULL DEFAULT '',
    failure_reason TEXT,
    time_spent_seconds REAL NOT NULL DEFAULT 0.0,
    code_snapshot TEXT,
    details JSON,
    FOREIGN KEY(task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_attempts_task_id ON task_attempts(task_id);
```

#### Table 3: `execution_runs` (Session-Level Tracker)
Stores top-level metrics for each execution run of `main.py`.
```sql
CREATE TABLE IF NOT EXISTS execution_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    command TEXT NOT NULL,
    platform_filter TEXT,
    total_discovered INTEGER NOT NULL DEFAULT 0,
    total_completed INTEGER NOT NULL DEFAULT 0,
    total_pending INTEGER NOT NULL DEFAULT 0,
    total_blocked INTEGER NOT NULL DEFAULT 0,
    total_failed INTEGER NOT NULL DEFAULT 0,
    duration_seconds REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL CHECK(status IN ('RUNNING', 'COMPLETED', 'FAILED', 'INTERRUPTED'))
);
```

### 2.2 Atomic JSON Export Mechanism (`data/state_summary.json`)

To satisfy Requirement R3's specification of a persistent tracking file and ensure external inspection tools or dashboard viewers can read task state at any moment without locking the database:

1. **Problem**: Writing directly to `data/state_summary.json` via standard file handles leaves a window where a crash, kill signal (`SIGINT`), or power loss produces a truncated, corrupted, or invalid JSON file.
2. **Solution**: Use atomic filesystem rename via `os.replace`:
   ```python
   def export_state_json(self, export_path: Optional[str] = None) -> str:
       target_path = Path(export_path or self.json_export_path).resolve()
       target_path.parent.mkdir(parents=True, exist_ok=True)
       
       # Write to unique temp file in the SAME directory/filesystem
       temp_path = target_path.with_name(f"{target_path.name}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}")
       
       data = {
           "schema_version": "1.0",
           "exported_at": datetime.now(timezone.utc).isoformat(),
           "summary_metrics": self.get_summary_stats(),
           "tasks": [task.to_dict() for task in self.list_tasks()]
       }
       
       with open(temp_path, "w", encoding="utf-8") as f:
           json.dump(data, f, indent=2, ensure_ascii=False)
           f.flush()
           os.fsync(f.fileno())  # Flush OS buffers to physical disk
           
       os.replace(temp_path, target_path)  # Atomic POSIX replacement
       return str(target_path)
   ```

---

## 3. Persistent State Manager (`core/state_manager.py`) Design

### 3.1 Dataclasses & Type Hierarchy

```python
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class TaskStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

class TaskPlatform(str, Enum):
    GUVI_CODEKATA = "guvi_codekata"
    ZENCLASS_TASKS = "zenclass_tasks"
    ZENCLASS_PROJECTS = "zenclass_projects"

class TaskResult(str, Enum):
    SOLVED = "SOLVED"
    PASSED = "PASSED"
    SUBMITTED = "SUBMITTED"
    TEST_FAILED = "TEST_FAILED"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    CAPTCHA_TRIGGERED = "CAPTCHA_TRIGGERED"
    MFA_TRIGGERED = "MFA_TRIGGERED"
    AWAITING_INPUT = "AWAITING_INPUT"
    UNATTEMPTED = "UNATTEMPTED"

@dataclass
class TaskRecord:
    task_id: str
    platform: str
    task_category: str
    title: str
    url: str = ""
    status: str = TaskStatus.PENDING.value
    attempt_count: int = 0
    result: str = TaskResult.UNATTEMPTED.value
    failure_reason: Optional[str] = None
    next_action: str = ""
    time_spent_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.updated_at  # R3 alias
        return d

@dataclass
class AttemptRecord:
    id: Optional[int]
    task_id: str
    attempt_number: int
    timestamp: str
    status: str
    result: str
    failure_reason: Optional[str]
    time_spent_seconds: float
    code_snapshot: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
```

### 3.2 StateManager Interface & Method Signatures

```python
class StateManager:
    """
    Authoritative state coordinator adhering to Requirement R3.
    Manages SQLite database persistence, WAL locking, transaction atomicity,
    and concurrent JSON state file exports.
    """
    
    def __init__(
        self,
        db_path: str = "data/automation_state.db",
        json_export_path: str = "data/state_summary.json"
    ) -> None:
        """Initializes database connection, applies PRAGMAs, and creates schema."""
        ...

    def close(self) -> None:
        """Closes the underlying SQLite database connection gracefully."""
        ...

    def __enter__(self) -> "StateManager":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    # -------------------------------------------------------------------------
    # Core Task Mutation APIs
    # -------------------------------------------------------------------------

    def record_task(
        self,
        task_id: str,
        platform: str,
        title: str,
        category: str,
        url: str = "",
        status: str = TaskStatus.PENDING.value,
        attempts: int = 0,
        result: str = TaskResult.UNATTEMPTED.value,
        failure_reason: Optional[str] = None,
        next_action: str = "",
        time_spent_seconds: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
        auto_export_json: bool = True
    ) -> TaskRecord:
        """
        Idempotent task registration (UPSERT).
        If task exists, updates fields without wiping existing attempt counters
        unless explicitly provided.
        """
        ...

    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[str] = None,
        failure_reason: Optional[str] = None,
        next_action: Optional[str] = None,
        time_spent_seconds: Optional[float] = None,
        metadata_update: Optional[Dict[str, Any]] = None,
        increment_attempts: bool = False,
        code_snapshot: Optional[str] = None,
        auto_export_json: bool = True
    ) -> Optional[TaskRecord]:
        """
        Updates task status, failure reason, and next action.
        Optionally increments attempt count and records an entry into `task_attempts`.
        """
        ...

    def batch_record_tasks(
        self,
        tasks: List[Dict[str, Any]],
        auto_export_json: bool = True
    ) -> int:
        """
        Optimized batch insertion for catalog discovery (e.g. 2,145 CodeKata problems)
        using a single database transaction. Returns count of inserted/updated tasks.
        """
        ...

    # -------------------------------------------------------------------------
    # Query & Retrieval APIs
    # -------------------------------------------------------------------------

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Retrieves a single task record by ID, or None if not found."""
        ...

    def list_pending(
        self,
        platform: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TaskRecord]:
        """
        Returns all uncompleted tasks with status IN ('PENDING', 'DISCOVERED').
        Ordered by created_at ascending.
        """
        ...

    def get_pending_tasks(
        self,
        platform: Optional[str] = None
    ) -> List[TaskRecord]:
        """Alias for list_pending to satisfy PROJECT.md interface contract."""
        return self.list_pending(platform=platform)

    def list_tasks(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[TaskRecord]:
        """Flexible query API for filtered task retrieval."""
        ...

    def list_blocked(
        self,
        platform: Optional[str] = None
    ) -> List[TaskRecord]:
        """Returns all tasks flagged with status = 'BLOCKED'."""
        ...

    def get_task_attempts(self, task_id: str) -> List[AttemptRecord]:
        """Returns chronological list of attempt logs for a given task."""
        ...

    # -------------------------------------------------------------------------
    # Metrics & Reporting Data APIs
    # -------------------------------------------------------------------------

    def get_summary_stats(
        self,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregates system-wide or platform-specific execution statistics:
        - total_discovered
        - total_completed
        - total_pending
        - total_in_progress
        - total_blocked
        - total_failed
        - success_rate (percentage)
        - total_time_spent_seconds
        - by_platform breakdown
        - human_intervention_issues (list of blocked/critical items)
        """
        ...

    def export_state_json(
        self,
        export_path: Optional[str] = None
    ) -> str:
        """Atomically serializes current database state to JSON file."""
        ...

    # -------------------------------------------------------------------------
    # Session / Execution Run Tracking APIs
    # -------------------------------------------------------------------------

    def start_execution_run(
        self,
        command: str,
        platform_filter: Optional[str] = None
    ) -> str:
        """Creates a new execution run record and returns run_id."""
        ...

    def end_execution_run(
        self,
        run_id: str,
        status: str = "COMPLETED"
    ) -> None:
        """Finalizes execution run record with duration and summary counts."""
        ...
```

---

## 4. Reporting Engine (`core/reporter.py`) Design

The Reporting Engine reads from `StateManager` and generates two required output artifacts:
1. **Executive Markdown Report**: `reports/SUMMARY_REPORT.md` (Rich formatting, tables, action items).
2. **Machine-Readable JSON Report**: `reports/summary.json` (Structured metrics for CI/CD and programmatic consumers).
3. **CLI Terminal Dashboard**: ANSI-colorized formatted summary box printed to stdout upon run completion.

### 4.1 Executive Markdown Report Format (`reports/SUMMARY_REPORT.md`)

```markdown
# 📊 ZenClass & Guvi Automation Execution Summary Report

**Generated At**: 2026-11-10T16:00:00Z  
**Execution Host**: macOS Apple Silicon (Darwin 24.x)  
**Overall Status**: 🟡 INTERVENTION REQUIRED (3 Blocked Items)

---

## 1. Executive Summary

| Metric | Count | Percentage |
|---|---|---|
| **Total Tasks Discovered** | **150** | 100.0% |
| **Total Tasks Completed** | **135** | 90.0% |
| **Total Tasks Pending** | **12** | 8.0% |
| **Total Tasks Blocked** | **3** | 2.0% |
| **Total Tasks Failed** | **0** | 0.0% |
| **Overall Success Rate** | **90.0%** | (Completed / Discovered) |
| **Total Execution Time** | **01:42:18** | (6,138.4 seconds) |
| **Average Time Per Task** | **45.4s** | |

---

## 2. Platform Breakdown Matrix

| Platform | Discovered | Completed | Pending | Blocked | Failed | Success Rate | Time Spent |
|---|---|---|---|---|---|---|---|
| **Guvi CodeKata** | 120 | 115 | 4 | 1 | 0 | 95.8% | 00:54:12 |
| **ZenClass Tasks** | 25 | 18 | 6 | 1 | 0 | 72.0% | 00:28:06 |
| **ZenClass Projects** | 5 | 2 | 2 | 1 | 0 | 40.0% | 00:20:00 |
| **TOTAL** | **150** | **135** | **12** | **3** | **0** | **90.0%** | **01:42:18** |

---

## 3. 🚨 Human Intervention Required (Requirement R3)

The following items are paused or blocked due to security, CAPTCHA, or external credential/URL requirements:

| # | Platform | Task ID / Title | Status | Attempts | Failure Reason | Prescribed Next Action |
|---|---|---|---|---|---|---|
| 1 | `guvi_codekata` | `odd-or-even-sum` | `BLOCKED` | 2 | Cloudflare Turnstile challenge detected | Solve Cloudflare challenge in visible foreground browser |
| 2 | `zenclass_tasks` | `task_41486_react` | `BLOCKED` | 1 | Form requires external API token | Provide API authorization token via CLI prompt |
| 3 | `zenclass_projects` | `proj_mern_capstone` | `BLOCKED` | 1 | Awaiting GitHub and Netlify deployment URLs | User to deploy local code in `projects/mern_capstone/` and provide URLs |

---

## 4. Category Breakdown

| Category | Total | Completed | Pending | Blocked | Success Rate |
|---|---|---|---|---|---|
| `Easy (CodeKata)` | 80 | 78 | 2 | 0 | 97.5% |
| `Medium (CodeKata)` | 40 | 37 | 2 | 1 | 92.5% |
| `JavaScript (Tasks)` | 15 | 12 | 3 | 0 | 80.0% |
| `React (Tasks)` | 10 | 6 | 3 | 1 | 60.0% |
| `Fullstack (Projects)`| 5 | 2 | 2 | 1 | 40.0% |

---

## 5. Recent Execution History (Last 10 Completed Items)

| Timestamp | Platform | Task Title | Result | Duration | Attempts |
|---|---|---|---|---|---|
| 2026-11-10T15:58:12Z | Guvi CodeKata | Array Min Max | `SOLVED` | 4.2s | 1 |
| 2026-11-10T15:57:40Z | Guvi CodeKata | String Reversal | `SOLVED` | 3.8s | 1 |
| ... | ... | ... | ... | ... | ... |

---
*Report automatically generated by ZenClass & Guvi Automation Reporter.*
```

### 4.2 Machine-Readable JSON Report Format (`reports/summary.json`)

```json
{
  "generated_at": "2026-11-10T16:00:00Z",
  "summary_metrics": {
    "total_discovered": 150,
    "total_completed": 135,
    "total_pending": 12,
    "total_blocked": 3,
    "total_failed": 0,
    "success_rate_percent": 90.0,
    "total_time_spent_seconds": 6138.4,
    "formatted_time_spent": "01:42:18"
  },
  "by_platform": {
    "guvi_codekata": {
      "total_discovered": 120,
      "total_completed": 115,
      "total_pending": 4,
      "total_blocked": 1,
      "total_failed": 0,
      "success_rate_percent": 95.83,
      "time_spent_seconds": 3252.0
    },
    "zenclass_tasks": {
      "total_discovered": 25,
      "total_completed": 18,
      "total_pending": 6,
      "total_blocked": 1,
      "total_failed": 0,
      "success_rate_percent": 72.0,
      "time_spent_seconds": 1686.4
    },
    "zenclass_projects": {
      "total_discovered": 5,
      "total_completed": 2,
      "total_pending": 2,
      "total_blocked": 1,
      "total_failed": 0,
      "success_rate_percent": 40.0,
      "time_spent_seconds": 1200.0
    }
  },
  "human_intervention_issues": [
    {
      "task_id": "odd-or-even-sum",
      "platform": "guvi_codekata",
      "title": "Odd or Even Sum",
      "status": "BLOCKED",
      "attempts": 2,
      "failure_reason": "Cloudflare Turnstile challenge detected",
      "next_action": "Solve Cloudflare challenge in visible foreground browser",
      "url": "https://www.guvi.in/code-kata/odd-or-even-sum/"
    },
    {
      "task_id": "task_41486_react",
      "platform": "zenclass_tasks",
      "title": "React Lifecycle Assignment",
      "status": "BLOCKED",
      "attempts": 1,
      "failure_reason": "Form requires external API token",
      "next_action": "Provide API authorization token via CLI prompt",
      "url": "https://v2.zenclass.in/tasks"
    },
    {
      "task_id": "proj_mern_capstone",
      "platform": "zenclass_projects",
      "title": "MERN Stack E-Commerce Capstone",
      "status": "BLOCKED",
      "attempts": 1,
      "failure_reason": "Awaiting GitHub and Netlify deployment URLs",
      "next_action": "User to deploy local code in projects/mern_capstone/ and provide URLs",
      "url": "https://v2.zenclass.in/projects"
    }
  ]
}
```

### 4.3 Reporter Class Interface (`core/reporter.py`)

```python
class SummaryReporter:
    """
    Produces executive Markdown reports and structured JSON summaries
    based on authoritative data from StateManager.
    """

    def __init__(
        self,
        state_manager: StateManager,
        report_dir: str = "reports"
    ) -> None:
        self.state_manager = state_manager
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown_report(
        self,
        output_file: Optional[str] = None
    ) -> str:
        """
        Compiles and writes reports/SUMMARY_REPORT.md.
        Returns the absolute path to the generated file.
        """
        ...

    def generate_json_report(
        self,
        output_file: Optional[str] = None
    ) -> str:
        """
        Compiles and writes reports/summary.json atomically.
        Returns the absolute path to the generated file.
        """
        ...

    def generate_all_reports(self) -> Tuple[str, str]:
        """Generates both Markdown and JSON reports, returning (md_path, json_path)."""
        md_path = self.generate_markdown_report()
        json_path = self.generate_json_report()
        return md_path, json_path

    def print_terminal_summary(self) -> None:
        """
        Renders a clean, high-impact ASCII box summary to stdout
        with colored status pills for quick CLI feedback.
        """
        ...
```

---

## 5. Failure Modes, Edge Cases & Resilience Engineering

| Edge Case / Failure Scenario | Risk | Mitigation Strategy in Design |
|---|---|---|
| **Process crash or SIGKILL mid-write** | Corrupted state file or truncated JSON | SQLite WAL mode provides ACID rollback. JSON export uses unique temp files + atomic `os.replace` + `os.fsync`. No corrupted half-files can ever exist on disk. |
| **Catalog discovery with 2,000+ problems** | High I/O latency with 2,000 separate DB commits | Provide `batch_record_tasks()` utilizing `cursor.executemany` wrapped in a single explicit transaction (`BEGIN TRANSACTION` ... `COMMIT`). Execution takes < 100ms for 2,145 rows. |
| **Concurrent CLI commands or multi-threading** | `sqlite3.OperationalError: database is locked` | Enable WAL mode (`PRAGMA journal_mode = WAL`), set `busy_timeout = 5000` (wait 5s for lock), and set `check_same_thread = False` with thread-safe connection handling. |
| **Special characters in titles or code (UTF-8)** | Text encoding errors or SQL injection | Use parameterized queries exclusively (`?` placeholders). Enforce `encoding="utf-8"` on all file I/O and JSON serializers. |
| **Task Re-run / Resume Lifecycle** | Completed tasks overwritten or attempt history wiped | Task UPSERT preserves existing `COMPLETED` status unless explicit force flag is set. `update_task_status` only mutates specified fields and appends to `task_attempts`. |
| **Zero tasks discovered (Empty DB)** | ZeroDivisionError when calculating success rate | Helper calculates `success_rate = (completed / total * 100.0) if total > 0 else 0.0`. Handled gracefully in all report templates. |
| **Corrupted database recovery** | Unreadable SQLite file | Add automatic integrity check on connection (`PRAGMA integrity_check`). If fatal corruption detected, rotate corrupted DB to `data/automation_state.db.bak.<timestamp>` and reinitialize schema from `data/state_summary.json` if available. |

---

## 6. Implementation Blueprint for Worker Agents

When implementing `core/state_manager.py` and `core/reporter.py` in Milestone 1:

1. **File Locations**:
   - `zenclass_guvi/core/state_manager.py`
   - `zenclass_guvi/core/reporter.py`
   - `zenclass_guvi/data/automation_state.db` (auto-created on init)
   - `zenclass_guvi/data/state_summary.json` (auto-exported on mutation)
   - `zenclass_guvi/reports/SUMMARY_REPORT.md` (generated by reporter)
   - `zenclass_guvi/reports/summary.json` (generated by reporter)
2. **Standard Library Only**:
   - Rely solely on Python standard libraries: `sqlite3`, `json`, `dataclasses`, `datetime`, `enum`, `pathlib`, `typing`, `os`, `uuid`, `shutil`.
   - Zero external pip requirements for the state and reporting layer.
3. **Integration with Drivers**:
   - `guvi_driver.py` and `zenclass_driver.py` will import `StateManager` and instantiate a single shared instance or accept it via constructor dependency injection.
   - On problem discovery: call `batch_record_tasks(...)`.
   - On problem processing: call `update_task_status(task_id, status=TaskStatus.IN_PROGRESS)`.
   - On success verification: call `update_task_status(task_id, status=TaskStatus.COMPLETED, result=TaskResult.SOLVED, increment_attempts=True)`.
   - On blocker/CAPTCHA: call `update_task_status(task_id, status=TaskStatus.BLOCKED, failure_reason=..., next_action=...)`.
   - On exit: call `SummaryReporter(state_manager).generate_all_reports()`.
