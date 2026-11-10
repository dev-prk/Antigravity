"""Token budget tracker. Hard limits per task and per session; checkpoints at thresholds."""
import time
from typing import Optional, Tuple

from .db import Ledger

OK, WARN, STOP = "ok", "checkpoint", "stop"


class BudgetExhausted(Exception):
    pass


class Budget:
    def __init__(self, ledger: Ledger, task_id: int, task_limit: int,
                 session_limit: Optional[int] = None, session: str = "s1",
                 warn_at: float = 0.8):
        self.l, self.tid, self.task_limit = ledger, task_id, task_limit
        self.session_limit, self.session, self.warn_at = session_limit, session, warn_at
        self._warned = self.used_task() >= warn_at * task_limit

    def _sum(self, where: str, args: tuple) -> int:
        r = self.l.conn.execute("SELECT COALESCE(SUM(tokens),0) FROM budget_usage WHERE " + where, args).fetchone()
        return int(r[0])

    def used_task(self) -> int:
        return self._sum("task_id=?", (self.tid,))

    def used_session(self) -> int:
        return self._sum("task_id=? AND session=?", (self.tid, self.session))

    def remaining(self) -> int:
        rem = self.task_limit - self.used_task()
        if self.session_limit is not None:
            rem = min(rem, self.session_limit - self.used_session())
        return max(rem, 0)

    def can_afford(self, estimate: int) -> bool:
        return estimate <= self.remaining()

    def record(self, tokens: int, note: str = "") -> str:
        """Record usage. Returns OK / WARN (checkpoint written once at warn_at) / STOP (hard limit hit)."""
        self.l._ins("INSERT INTO budget_usage(task_id,session,tokens,note,created) VALUES(?,?,?,?,?)",
                    (self.tid, self.session, tokens, note, time.time()))
        if self.remaining() == 0:
            self.l.checkpoint(self.tid, "budget_exhausted")
            self.l.set_task(self.tid, status="paused", blockers="token budget exhausted")
            return STOP
        if not self._warned and self.used_task() >= self.warn_at * self.task_limit:
            self._warned = True
            self.l.checkpoint(self.tid, "budget_%d%%" % int(self.warn_at * 100))
            return WARN
        return OK
