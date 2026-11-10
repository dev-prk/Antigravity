"""CLI: python3 -m aios status | new GOAL LIMIT STEP... | done SEQ [EVIDENCE] | tokens N"""
import os
import sys

from . import handoff
from .budget import Budget
from .db import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB, HP = os.path.join(ROOT, "state", "aios.db"), os.path.join(ROOT, "HANDOFF.md")


def active(l):
    r = l.conn.execute("SELECT id FROM tasks WHERE status!='done' ORDER BY id DESC LIMIT 1").fetchone()
    return r[0] if r else None


def main(a):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    l = Ledger(DB)
    cmd = a[0] if a else "status"
    if cmd == "new" and len(a) >= 4:
        tid = l.create_task(a[1], int(a[2]), a[3:])
        handoff.write(l, tid, HP, "new task")
        print("task", tid)
        return 0
    tid = active(l)
    if tid is None:
        print("No active task.")
        return 0
    if cmd == "done" and len(a) >= 2:
        l.set_step(tid, int(a[1]), "done", a[2] if len(a) > 2 else "ok")
        if len(a) > 2:
            l.add_evidence(tid, "step", a[2])
        if l.next_step(tid) is None:
            l.set_task(tid, status="done")
        handoff.write(l, tid, HP, "step boundary")
    elif cmd == "tokens" and len(a) >= 2:
        s = Budget(l, tid, l.get_task(tid)["token_limit"]).record(int(a[1]), "manual")
        handoff.write(l, tid, HP, "budget " + s)
        print("budget:", s)
    print(handoff.generate(l, tid))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
