"""Relational SQLite database layer for NCAAFB Sports Analytics Platform."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "ncaafb_analytics.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


class NCAAFBDatabase:
    """Manages normalized 8-table + schedule relational storage and SQL analytics."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        with self.connect() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def upsert_many(self, table: str, columns: List[str], rows: Iterable[tuple]) -> int:
        rows_list = list(rows)
        if not rows_list:
            return 0
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"
        with self.connect() as conn:
            conn.executemany(sql, rows_list)
            conn.commit()
        return len(rows_list)

    def query_df(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        cleaned = sql.strip()
        if not cleaned.upper().startswith(("SELECT", "WITH", "PRAGMA")):
            raise ValueError("Only read-only SELECT / WITH queries are permitted.")
        with self.connect() as conn:
            return pd.read_sql_query(cleaned, conn, params=params)

    def table_counts(self) -> Dict[str, int]:
        tables = [
            "Conferences",
            "Venues",
            "Teams",
            "Seasons",
            "Players",
            "Player_Statistics",
            "Rankings",
            "Coaches",
            "Schedules",
        ]
        counts: Dict[str, int] = {}
        with self.connect() as conn:
            for tbl in tables:
                cur = conn.execute(f"SELECT COUNT(*) AS cnt FROM {tbl}")
                counts[tbl] = int(cur.fetchone()["cnt"])
        return counts
