"""Minimal step runner used for resume demos/tests. A real executor plugs in via `work`."""
import os
import sys
from typing import Callable, Optional

from .budget import STOP, Budget
from .db import Ledger
from . import handoff


def run(ledger: Ledger, task_id: int, budget: Budget, handoff_path: str,
        work: Callable[[dict], int], die_after: Optional[int] = None) -> str:
    """Run pending steps. work(step)->tokens used. Writes HANDOFF.md at every boundary.
    die_after=N simulates a hard kill (os._exit) after N completed steps."""
    ledger.set_task(task_id, status="running")
    completed = 0
    while True:
        step = ledger.next_step(task_id)
        if step is None:
            ledger.set_task(task_id, status="done", blockers="")
            handoff.write(ledger, task_id, handoff_path, "complete")
            return "done"
        if not budget.can_afford(1):
            handoff.write(ledger, task_id, handoff_path, "budget")
            return "paused"
        tokens = work(step)
        ledger.set_step(task_id, step["seq"], "done", "ok")
        state = budget.record(tokens, "step %d" % step["seq"])
        handoff.write(ledger, task_id, handoff_path, "step boundary")
        completed += 1
        if state == STOP:
            return "paused"
        if die_after is not None and completed >= die_after:
            os._exit(137)  # simulated kill, no cleanup
