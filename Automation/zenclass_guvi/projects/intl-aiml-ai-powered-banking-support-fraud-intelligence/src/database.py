"""Normalized & Indexed SQLite Database Layer with Pagination for Banking Support & Fraud Intelligence."""

from __future__ import annotations

import datetime
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "banking_intelligence.db"


class BankingDatabase:
    """Manages normalized SQLite tables, indexes, audit logging, and paginated queries."""

    def __init__(self, db_path: Optional[Path] = None, data_dir: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS copilot_audit_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        query_text TEXT NOT NULL,
                        predicted_intent TEXT NOT NULL,
                        sentiment TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        suggested_action TEXT NOT NULL,
                        top_policy_source TEXT
                    );
                    """
                )
                # Populate tickets and transactions if missing
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
                if cur.fetchone() is None:
                    tickets = pd.read_csv(self.data_dir / "01_support_tickets.csv")
                    txns = pd.read_csv(self.data_dir / "02_transactions.csv")
                    tickets.to_sql("support_tickets", conn, if_exists="replace", index=False)
                    txns.to_sql("transactions", conn, if_exists="replace", index=False)
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_tkt_cat ON support_tickets(category);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_tkt_risk ON support_tickets(risk_level);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_fraud ON transactions(fraud_label);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_acct ON transactions(account_id);")
                conn.commit()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Database initialization failed: {exc}") from exc

    def log_interaction(
        self,
        query_text: str,
        predicted_intent: str,
        sentiment: str,
        risk_level: str,
        suggested_action: str,
        top_policy_source: str,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO copilot_audit_logs
                (created_at, query_text, predicted_intent, sentiment, risk_level, suggested_action, top_policy_source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    query_text,
                    predicted_intent,
                    sentiment,
                    risk_level,
                    suggested_action,
                    top_policy_source,
                ),
            )
            conn.commit()

    def get_paginated_table(
        self,
        table: str,
        page: int = 1,
        page_size: int = 25,
        filter_col: Optional[str] = None,
        filter_val: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, int]:
        """Returns a single page of records and total matching row count."""
        allowed_tables = {"support_tickets": {"category", "risk_level", "sentiment"}, "transactions": {"city", "transaction_type", "fraud_label"}, "copilot_audit_logs": {"risk_level"}}
        if table not in allowed_tables:
            raise ValueError(f"Unsupported table: {table}")

        offset = max(0, (page - 1) * page_size)
        where_clause = ""
        params: tuple = ()
        if filter_col and filter_val is not None and filter_val != "All":
            if filter_col not in allowed_tables[table]:
                raise ValueError(f"Unsupported filter column: {filter_col}")
            where_clause = f"WHERE {filter_col} = ?"
            params = (filter_val,)

        with self.connect() as conn:
            total = int(conn.execute(f"SELECT COUNT(*) FROM {table} {where_clause}", params).fetchone()[0])
            df = pd.read_sql_query(
                f"SELECT * FROM {table} {where_clause} LIMIT ? OFFSET ?",
                conn,
                params=params + (page_size, offset),
            )
        return df, total

    def summary_counts(self) -> Dict[str, int]:
        with self.connect() as conn:
            return {
                "support_tickets": int(conn.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]),
                "transactions": int(conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]),
                "fraud_transactions": int(conn.execute("SELECT COUNT(*) FROM transactions WHERE fraud_label = 1").fetchone()[0]),
                "audit_logs": int(conn.execute("SELECT COUNT(*) FROM copilot_audit_logs").fetchone()[0]),
            }
