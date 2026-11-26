"""Structured SQLite Store for Short-Term, Long-Term & Feedback Memory Layers."""

from __future__ import annotations

import datetime
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "support_multiagent.db"


class SupportMemoryDB:
    """Persists tickets, 6-agent execution logs, session chat memory, and continuous learning feedback."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    session_id TEXT,
                    ticket_text TEXT NOT NULL,
                    cleaned_text TEXT,
                    order_id TEXT,
                    product_name TEXT,
                    category TEXT,
                    priority TEXT,
                    sentiment TEXT,
                    confidence_score REAL,
                    escalated INTEGER DEFAULT 0,
                    auto_resolved INTEGER DEFAULT 0,
                    escalation_reason TEXT,
                    response_text TEXT,
                    status TEXT NOT NULL DEFAULT 'NEW'
                );

                CREATE TABLE IF NOT EXISTS agent_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT NOT NULL,
                    step_order INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS feedback_memory (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT NOT NULL,
                    ticket_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    approved_resolution TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_logs_ticket ON agent_logs(ticket_id, step_order);
                CREATE INDEX IF NOT EXISTS idx_tickets_session ON tickets(session_id);
                """
            )
            conn.commit()

    def create_raw_ticket(self, ticket_text: str, session_id: str = "default", ticket_id: Optional[str] = None) -> str:
        tid = ticket_id or f"TKT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tickets (ticket_id, created_at, session_id, ticket_text, status) VALUES (?, ?, ?, ?, 'NEW')",
                (tid, now, session_id, ticket_text),
            )
            conn.commit()
        return tid

    def save_processed_ticket(self, record: Dict[str, Any], logs: List[Dict[str, Any]]) -> None:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tickets (
                    ticket_id, created_at, session_id, ticket_text, cleaned_text, order_id,
                    product_name, category, priority, sentiment, confidence_score,
                    escalated, auto_resolved, escalation_reason, response_text, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["ticket_id"],
                    record.get("created_at", now),
                    record.get("session_id", "default"),
                    record["ticket_text"],
                    record.get("cleaned_text", ""),
                    record.get("order_id"),
                    record.get("product_name"),
                    record.get("category"),
                    record.get("priority"),
                    record.get("sentiment"),
                    float(record.get("confidence_score", 0.0)),
                    int(bool(record.get("escalated", False))),
                    int(bool(record.get("auto_resolved", False))),
                    record.get("escalation_reason", ""),
                    record.get("response_text", ""),
                    "ESCALATED" if record.get("escalated") else "AUTO_RESOLVED",
                ),
            )
            conn.execute("DELETE FROM agent_logs WHERE ticket_id = ?", (record["ticket_id"],))
            for step_idx, log_item in enumerate(logs, start=1):
                conn.execute(
                    """
                    INSERT INTO agent_logs (ticket_id, step_order, agent_name, latency_ms, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["ticket_id"],
                        step_idx,
                        log_item["agent_name"],
                        float(log_item["latency_ms"]),
                        json.dumps(log_item["output"]),
                        now,
                    ),
                )
            conn.commit()

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
            return dict(row) if row else None

    def get_logs(self, ticket_id: str) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT step_order, agent_name, latency_ms, payload_json, created_at FROM agent_logs WHERE ticket_id = ? ORDER BY step_order ASC",
                (ticket_id,),
            ).fetchall()
        return [
            {
                "step_order": r["step_order"],
                "agent_name": r["agent_name"],
                "latency_ms": r["latency_ms"],
                "output": json.loads(r["payload_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def record_feedback(self, ticket_id: str, rating: int, approved_resolution: str) -> Dict[str, Any]:
        tkt = self.get_ticket(ticket_id)
        if not tkt:
            raise KeyError(f"Ticket {ticket_id} not found.")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO feedback_memory (ticket_id, ticket_text, category, rating, approved_resolution, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ticket_id, tkt["ticket_text"], tkt.get("category") or "General", int(rating), approved_resolution, now),
            )
            conn.commit()
        return {"ticket_id": ticket_id, "rating": int(rating), "learned": True}

    def get_learned_feedback(self) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM feedback_memory WHERE rating >= 4 ORDER BY feedback_id DESC").fetchall()
        return [dict(r) for r in rows]

    def recent_tickets_df(self, limit: int = 50) -> pd.DataFrame:
        with self.connect() as conn:
            return pd.read_sql_query(f"SELECT * FROM tickets ORDER BY created_at DESC LIMIT {int(limit)}", conn)
