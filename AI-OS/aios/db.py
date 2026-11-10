"""SQLite state + task ledger. Python 3.9, stdlib only."""
import json
import sqlite3
import time
from typing import Any, Dict, List, Optional

TABLES = ["tasks", "steps", "evidence", "decisions", "facts",
          "checkpoints", "budget_usage", "audit_log"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, goal TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', token_limit INTEGER NOT NULL DEFAULT 0,
  blockers TEXT NOT NULL DEFAULT '', created REAL, updated REAL);
CREATE TABLE IF NOT EXISTS steps(id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL REFERENCES tasks(id),
  seq INTEGER NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
  result TEXT, updated REAL, UNIQUE(task_id, seq));
CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL,
  step_id INTEGER, kind TEXT, content TEXT, created REAL);
CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY, task_id INTEGER, title TEXT,
  rationale TEXT, created REAL);
CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY, task_id INTEGER, statement TEXT,
  status TEXT NOT NULL DEFAULT 'assumed' CHECK(status IN ('verified','assumed','stale')),
  source TEXT, created REAL);
CREATE TABLE IF NOT EXISTS checkpoints(id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL,
  reason TEXT, state_json TEXT, created REAL);
CREATE TABLE IF NOT EXISTS budget_usage(id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL,
  session TEXT, tokens INTEGER NOT NULL, note TEXT, created REAL);
CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY, task_id INTEGER, actor TEXT,
  action TEXT, detail TEXT, created REAL);
"""


class Ledger:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)

    def close(self):
        self.conn.close()

    def _ins(self, sql: str, args: tuple) -> int:
        cur = self.conn.execute(sql, args)
        self.conn.commit()
        return cur.lastrowid

    # tasks / steps
    def create_task(self, goal: str, token_limit: int = 0, steps: Optional[List[str]] = None) -> int:
        now = time.time()
        tid = self._ins("INSERT INTO tasks(goal,token_limit,created,updated) VALUES(?,?,?,?)",
                        (goal, token_limit, now, now))
        for i, t in enumerate(steps or [], 1):
            self.add_step(tid, i, t)
        self.audit(tid, "ledger", "create_task", goal)
        return tid

    def add_step(self, task_id: int, seq: int, title: str) -> int:
        return self._ins("INSERT INTO steps(task_id,seq,title,updated) VALUES(?,?,?,?)",
                         (task_id, seq, title, time.time()))

    def set_step(self, task_id: int, seq: int, status: str, result: str = ""):
        self.conn.execute("UPDATE steps SET status=?,result=?,updated=? WHERE task_id=? AND seq=?",
                          (status, result, time.time(), task_id, seq))
        self.conn.commit()
        self.audit(task_id, "ledger", "step_" + status, "seq=%d" % seq)

    def set_task(self, task_id: int, status: Optional[str] = None, blockers: Optional[str] = None):
        if status is not None:
            self.conn.execute("UPDATE tasks SET status=?,updated=? WHERE id=?", (status, time.time(), task_id))
        if blockers is not None:
            self.conn.execute("UPDATE tasks SET blockers=?,updated=? WHERE id=?", (blockers, time.time(), task_id))
        self.conn.commit()

    def get_task(self, task_id: int) -> Dict[str, Any]:
        r = self.conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return dict(r) if r else {}

    def steps(self, task_id: int) -> List[Dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM steps WHERE task_id=? ORDER BY seq", (task_id,))]

    def next_step(self, task_id: int) -> Optional[Dict[str, Any]]:
        r = self.conn.execute("SELECT * FROM steps WHERE task_id=? AND status!='done' ORDER BY seq LIMIT 1",
                              (task_id,)).fetchone()
        return dict(r) if r else None

    # evidence / decisions / facts
    def add_evidence(self, task_id: int, kind: str, content: str, step_id: Optional[int] = None) -> int:
        return self._ins("INSERT INTO evidence(task_id,step_id,kind,content,created) VALUES(?,?,?,?,?)",
                         (task_id, step_id, kind, content, time.time()))

    def add_decision(self, task_id: int, title: str, rationale: str) -> int:
        return self._ins("INSERT INTO decisions(task_id,title,rationale,created) VALUES(?,?,?,?)",
                         (task_id, title, rationale, time.time()))

    def add_fact(self, task_id: int, statement: str, status: str = "assumed", source: str = "") -> int:
        return self._ins("INSERT INTO facts(task_id,statement,status,source,created) VALUES(?,?,?,?,?)",
                         (task_id, statement, status, source, time.time()))

    def rows(self, table: str, task_id: int) -> List[Dict[str, Any]]:
        assert table in TABLES
        col = "id" if table == "tasks" else "task_id"
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM %s WHERE %s=? ORDER BY id" % (table, col), (task_id,))]

    # checkpoints / audit
    def checkpoint(self, task_id: int, reason: str) -> int:
        state = {"task": self.get_task(task_id), "steps": self.steps(task_id)}
        return self._ins("INSERT INTO checkpoints(task_id,reason,state_json,created) VALUES(?,?,?,?)",
                         (task_id, reason, json.dumps(state), time.time()))

    def latest_checkpoint(self, task_id: int) -> Optional[Dict[str, Any]]:
        r = self.conn.execute("SELECT * FROM checkpoints WHERE task_id=? ORDER BY id DESC LIMIT 1",
                              (task_id,)).fetchone()
        return dict(r) if r else None

    def audit(self, task_id: Optional[int], actor: str, action: str, detail: str = ""):
        self._ins("INSERT INTO audit_log(task_id,actor,action,detail,created) VALUES(?,?,?,?,?)",
                  (task_id, actor, action, detail, time.time()))
