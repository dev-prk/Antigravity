"""
Reference Implementation: Persistent State Manager
Location: core/state_manager.py
Compliance: Requirement R3 of ORIGINAL_REQUEST.md
"""

from __future__ import annotations
import sqlite3
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
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
        d["timestamp"] = self.updated_at  # Strict R3 alias
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


class StateManager:
    """
    Authoritative state coordinator adhering to Requirement R3.
    Thread-safe SQLite database persistence with WAL mode, transaction safety,
    and atomic JSON state file exports.
    """

    def __init__(
        self,
        db_path: str = "data/automation_state.db",
        json_export_path: str = "data/state_summary.json"
    ) -> None:
        self.db_path = Path(db_path).resolve()
        self.json_export_path = Path(json_export_path).resolve()
        
        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_export_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None  # Autocommit mode for granular transaction control
        )
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """Applies WAL configuration and idempotently creates tables and indexes."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA busy_timeout = 5000;")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            task_category TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL,
            attempt_count INTEGER NOT NULL DEFAULT 0,
            result TEXT NOT NULL DEFAULT '',
            failure_reason TEXT,
            next_action TEXT NOT NULL DEFAULT '',
            time_spent_seconds REAL NOT NULL DEFAULT 0.0,
            metadata JSON,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_platform_status ON tasks(platform, status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);")

        cursor.execute("""
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
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_task_id ON task_attempts(task_id);")

        cursor.execute("""
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
            status TEXT NOT NULL
        );
        """)

    def close(self) -> None:
        """Closes the database connection cleanly."""
        if self.conn:
            self.conn.close()

    def __enter__(self) -> "StateManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

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
        Registers or updates a task. Strictly captures all R3 fields:
        platform, task_id, category, status, attempt_count, result, timestamp, failure_reason, next_action.
        """
        now = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO tasks (
            task_id, platform, task_category, title, url, status,
            attempt_count, result, failure_reason, next_action,
            time_spent_seconds, metadata, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            platform = excluded.platform,
            task_category = excluded.task_category,
            title = excluded.title,
            url = CASE WHEN excluded.url != '' THEN excluded.url ELSE tasks.url END,
            status = excluded.status,
            attempt_count = MAX(tasks.attempt_count, excluded.attempt_count),
            result = CASE WHEN excluded.result != '' THEN excluded.result ELSE tasks.result END,
            failure_reason = excluded.failure_reason,
            next_action = excluded.next_action,
            time_spent_seconds = tasks.time_spent_seconds + excluded.time_spent_seconds,
            metadata = excluded.metadata,
            updated_at = excluded.updated_at;
        """, (
            task_id, platform, category, title, url, status,
            attempts, result, failure_reason, next_action,
            time_spent_seconds, meta_json, now, now
        ))

        # Log attempt if an attempt occurred
        if attempts > 0 or result not in ("", TaskResult.UNATTEMPTED.value):
            cursor.execute("""
            INSERT INTO task_attempts (
                task_id, attempt_number, timestamp, status, result,
                failure_reason, time_spent_seconds, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id, max(1, attempts), now, status, result,
                failure_reason, time_spent_seconds, meta_json
            ))

        if auto_export_json:
            self.export_state_json()

        return self.get_task(task_id)  # type: ignore

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
        Optionally increments attempt count and logs attempt history.
        """
        existing = self.get_task(task_id)
        if not existing:
            return None

        now = datetime.now(timezone.utc).isoformat()
        new_attempts = existing.attempt_count + (1 if increment_attempts else 0)
        new_result = result if result is not None else existing.result
        new_failure = failure_reason if failure_reason is not None else existing.failure_reason
        new_action = next_action if next_action is not None else existing.next_action
        added_time = time_spent_seconds if time_spent_seconds is not None else 0.0
        new_total_time = existing.time_spent_seconds + added_time

        merged_metadata = dict(existing.metadata)
        if metadata_update:
            merged_metadata.update(metadata_update)
        meta_json = json.dumps(merged_metadata)

        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE tasks SET
            status = ?,
            attempt_count = ?,
            result = ?,
            failure_reason = ?,
            next_action = ?,
            time_spent_seconds = ?,
            metadata = ?,
            updated_at = ?
        WHERE task_id = ?;
        """, (
            status, new_attempts, new_result, new_failure, new_action,
            new_total_time, meta_json, now, task_id
        ))

        # Record attempt history
        cursor.execute("""
        INSERT INTO task_attempts (
            task_id, attempt_number, timestamp, status, result,
            failure_reason, time_spent_seconds, code_snapshot, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, new_attempts, now, status, new_result,
            new_failure, added_time, code_snapshot, meta_json
        ))

        if auto_export_json:
            self.export_state_json()

        return self.get_task(task_id)

    def batch_record_tasks(
        self,
        tasks: List[Dict[str, Any]],
        auto_export_json: bool = True
    ) -> int:
        """
        Bulk upsert tasks in a single fast transaction (e.g. 2,145 CodeKata items).
        """
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        try:
            for t in tasks:
                meta_json = json.dumps(t.get("metadata", {}))
                cursor.execute("""
                INSERT INTO tasks (
                    task_id, platform, task_category, title, url, status,
                    attempt_count, result, failure_reason, next_action,
                    time_spent_seconds, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    platform = excluded.platform,
                    task_category = excluded.task_category,
                    title = excluded.title,
                    url = CASE WHEN excluded.url != '' THEN excluded.url ELSE tasks.url END,
                    status = excluded.status,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at;
                """, (
                    t["task_id"],
                    t["platform"],
                    t.get("task_category", t.get("category", "General")),
                    t.get("title", t["task_id"]),
                    t.get("url", ""),
                    t.get("status", TaskStatus.DISCOVERED.value),
                    t.get("attempt_count", t.get("attempts", 0)),
                    t.get("result", TaskResult.UNATTEMPTED.value),
                    t.get("failure_reason", None),
                    t.get("next_action", "SOLVE_AND_SUBMIT"),
                    t.get("time_spent_seconds", 0.0),
                    meta_json,
                    now,
                    now
                ))
            cursor.execute("COMMIT;")
        except Exception:
            cursor.execute("ROLLBACK;")
            raise

        if auto_export_json:
            self.export_state_json()

        return len(tasks)

    # -------------------------------------------------------------------------
    # Retrieval APIs
    # -------------------------------------------------------------------------

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Retrieves a single task record by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?;", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_task(row)

    def list_pending(
        self,
        platform: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TaskRecord]:
        """Returns all pending/discovered tasks ready for execution."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM tasks WHERE status IN (?, ?)"
        params: List[Any] = [TaskStatus.PENDING.value, TaskStatus.DISCOVERED.value]

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        query += " ORDER BY created_at ASC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        return [self._row_to_task(row) for row in cursor.fetchall()]

    def get_pending_tasks(self, platform: Optional[str] = None) -> List[TaskRecord]:
        """Alias satisfying PROJECT.md interface contract."""
        return self.list_pending(platform=platform)

    def list_tasks(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[TaskRecord]:
        """Query tasks with optional filtering."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []

        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if status:
            query += " AND status = ?"
            params.append(status)
        if category:
            query += " AND task_category = ?"
            params.append(category)

        query += " ORDER BY created_at ASC"
        cursor.execute(query, params)
        return [self._row_to_task(row) for row in cursor.fetchall()]

    def list_blocked(self, platform: Optional[str] = None) -> List[TaskRecord]:
        """Returns all blocked tasks requiring human intervention."""
        return self.list_tasks(platform=platform, status=TaskStatus.BLOCKED.value)

    def get_task_attempts(self, task_id: str) -> List[AttemptRecord]:
        """Returns all logged attempts for a given task."""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM task_attempts WHERE task_id = ? ORDER BY attempt_number ASC;
        """, (task_id,))
        results = []
        for r in cursor.fetchall():
            results.append(AttemptRecord(
                id=r["id"],
                task_id=r["task_id"],
                attempt_number=r["attempt_number"],
                timestamp=r["timestamp"],
                status=r["status"],
                result=r["result"],
                failure_reason=r["failure_reason"],
                time_spent_seconds=r["time_spent_seconds"],
                code_snapshot=r["code_snapshot"],
                details=json.loads(r["details"] or "{}")
            ))
        return results

    # -------------------------------------------------------------------------
    # Metrics & R3 Summary Statistics
    # -------------------------------------------------------------------------

    def get_summary_stats(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Aggregates summary statistics strictly complying with Requirement R3:
        total discovered, completed, pending, blocked, failed, success rate,
        time spent, and issues requiring human intervention.
        """
        cursor = self.conn.cursor()

        platform_clause = "WHERE platform = ?" if platform else ""
        platform_params = (platform,) if platform else ()

        # Global counts
        cursor.execute(f"""
        SELECT
            COUNT(*) as total_discovered,
            SUM(CASE WHEN status = '{TaskStatus.COMPLETED.value}' THEN 1 ELSE 0 END) as total_completed,
            SUM(CASE WHEN status IN ('{TaskStatus.PENDING.value}', '{TaskStatus.DISCOVERED.value}') THEN 1 ELSE 0 END) as total_pending,
            SUM(CASE WHEN status = '{TaskStatus.IN_PROGRESS.value}' THEN 1 ELSE 0 END) as total_in_progress,
            SUM(CASE WHEN status = '{TaskStatus.BLOCKED.value}' THEN 1 ELSE 0 END) as total_blocked,
            SUM(CASE WHEN status = '{TaskStatus.FAILED.value}' THEN 1 ELSE 0 END) as total_failed,
            COALESCE(SUM(time_spent_seconds), 0.0) as total_time_spent_seconds
        FROM tasks {platform_clause};
        """, platform_params)

        row = cursor.fetchone()
        total_discovered = row["total_discovered"] or 0
        total_completed = row["total_completed"] or 0
        total_pending = row["total_pending"] or 0
        total_in_progress = row["total_in_progress"] or 0
        total_blocked = row["total_blocked"] or 0
        total_failed = row["total_failed"] or 0
        total_time_spent = row["total_time_spent_seconds"] or 0.0

        success_rate = round((total_completed / total_discovered * 100.0), 2) if total_discovered > 0 else 0.0

        # Platform breakdown
        cursor.execute("""
        SELECT
            platform,
            COUNT(*) as total_discovered,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as total_completed,
            SUM(CASE WHEN status IN ('PENDING', 'DISCOVERED') THEN 1 ELSE 0 END) as total_pending,
            SUM(CASE WHEN status = 'BLOCKED' THEN 1 ELSE 0 END) as total_blocked,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as total_failed,
            COALESCE(SUM(time_spent_seconds), 0.0) as time_spent_seconds
        FROM tasks
        GROUP BY platform;
        """)

        by_platform = {}
        for r in cursor.fetchall():
            p_disc = r["total_discovered"] or 0
            p_comp = r["total_completed"] or 0
            p_rate = round((p_comp / p_disc * 100.0), 2) if p_disc > 0 else 0.0
            by_platform[r["platform"]] = {
                "total_discovered": p_disc,
                "total_completed": p_comp,
                "total_pending": r["total_pending"] or 0,
                "total_blocked": r["total_blocked"] or 0,
                "total_failed": r["total_failed"] or 0,
                "success_rate_percent": p_rate,
                "time_spent_seconds": round(r["time_spent_seconds"] or 0.0, 2)
            }

        # Category breakdown
        cursor.execute("""
        SELECT
            task_category,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed
        FROM tasks
        GROUP BY task_category;
        """)
        by_category = {}
        for r in cursor.fetchall():
            cat_tot = r["total"] or 0
            cat_comp = r["completed"] or 0
            by_category[r["task_category"]] = {
                "total": cat_tot,
                "completed": cat_comp,
                "success_rate_percent": round((cat_comp / cat_tot * 100.0), 2) if cat_tot > 0 else 0.0
            }

        # Human intervention issues (Blocked tasks or tasks with explicit failure reasons)
        cursor.execute("""
        SELECT task_id, platform, task_category, title, status, attempt_count, failure_reason, next_action, url
        FROM tasks
        WHERE status = 'BLOCKED' OR failure_reason IS NOT NULL
        ORDER BY updated_at DESC;
        """)
        human_issues = []
        for r in cursor.fetchall():
            human_issues.append({
                "task_id": r["task_id"],
                "platform": r["platform"],
                "category": r["task_category"],
                "title": r["title"],
                "status": r["status"],
                "attempts": r["attempt_count"],
                "failure_reason": r["failure_reason"] or "Unknown",
                "next_action": r["next_action"] or "Requires review",
                "url": r["url"]
            })

        return {
            "total_discovered": total_discovered,
            "total_completed": total_completed,
            "total_pending": total_pending,
            "total_in_progress": total_in_progress,
            "total_blocked": total_blocked,
            "total_failed": total_failed,
            "success_rate_percent": success_rate,
            "total_time_spent_seconds": round(total_time_spent, 2),
            "by_platform": by_platform,
            "by_category": by_category,
            "human_intervention_issues": human_issues
        }

    # -------------------------------------------------------------------------
    # Atomic JSON Export
    # -------------------------------------------------------------------------

    def export_state_json(self, export_path: Optional[str] = None) -> str:
        """
        Atomically writes current state summary and task entities to JSON.
        Uses temporary file + POSIX rename (os.replace) to ensure zero corruption.
        """
        target_path = Path(export_path or self.json_export_path).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = target_path.with_name(
            f"{target_path.name}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        )

        all_tasks = self.list_tasks()
        payload = {
            "schema_version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "summary": self.get_summary_stats(),
            "tasks": [t.to_dict() for t in all_tasks]
        }

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, target_path)
        return str(target_path)

    # -------------------------------------------------------------------------
    # Execution Run Session APIs
    # -------------------------------------------------------------------------

    def start_execution_run(
        self,
        command: str,
        platform_filter: Optional[str] = None
    ) -> str:
        """Records the start of a CLI automation session."""
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO execution_runs (run_id, started_at, command, platform_filter, status)
        VALUES (?, ?, ?, ?, 'RUNNING');
        """, (run_id, now, command, platform_filter))
        return run_id

    def end_execution_run(
        self,
        run_id: str,
        status: str = "COMPLETED"
    ) -> None:
        """Finalizes an execution run with duration and completion stats."""
        stats = self.get_summary_stats()
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("SELECT started_at FROM execution_runs WHERE run_id = ?;", (run_id,))
        row = cursor.fetchone()
        duration = 0.0
        if row and row["started_at"]:
            started = datetime.fromisoformat(row["started_at"])
            duration = (datetime.now(timezone.utc) - started).total_seconds()

        cursor.execute("""
        UPDATE execution_runs SET
            completed_at = ?,
            total_discovered = ?,
            total_completed = ?,
            total_pending = ?,
            total_blocked = ?,
            total_failed = ?,
            duration_seconds = ?,
            status = ?
        WHERE run_id = ?;
        """, (
            now,
            stats["total_discovered"],
            stats["total_completed"],
            stats["total_pending"],
            stats["total_blocked"],
            stats["total_failed"],
            round(duration, 2),
            status,
            run_id
        ))

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> TaskRecord:
        return TaskRecord(
            task_id=row["task_id"],
            platform=row["platform"],
            task_category=row["task_category"],
            title=row["title"],
            url=row["url"] or "",
            status=row["status"],
            attempt_count=row["attempt_count"],
            result=row["result"],
            failure_reason=row["failure_reason"],
            next_action=row["next_action"],
            time_spent_seconds=row["time_spent_seconds"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
