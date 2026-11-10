"""HANDOFF.md generator/resumer. Target <= 1500 tokens (estimated chars/4)."""
import re
from typing import Any, Dict, List

from .db import Ledger

MAX_TOKENS = 1500


def est_tokens(text: str) -> int:
    return (len(text) + 3) // 4


def _clip(s: str, n: int) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def generate(ledger: Ledger, task_id: int, reason: str = "") -> str:
    t = ledger.get_task(task_id)
    steps = ledger.steps(task_id)
    done = [s for s in steps if s["status"] == "done"]
    nxt = ledger.next_step(task_id)
    used = ledger.conn.execute("SELECT COALESCE(SUM(tokens),0) FROM budget_usage WHERE task_id=?", (task_id,)).fetchone()[0]
    decisions = ledger.rows("decisions", task_id)[-5:]

    def build(done_n: int) -> str:
        shown = done[-done_n:] if done_n else []
        out = ["# HANDOFF", "Task: %d | Status: %s | Tokens: %d/%d%s" % (
            task_id, t["status"], used, t["token_limit"], (" | Reason: " + reason) if reason else ""),
            "", "## Goal", _clip(t["goal"], 400), "", "## Done (%d/%d)" % (len(done), len(steps))]
        out += ["- [%d] %s: %s" % (s["seq"], _clip(s["title"], 80), _clip(s["result"], 100)) for s in shown]
        out += ["", "## Next action",
                ("[%d] %s" % (nxt["seq"], _clip(nxt["title"], 200))) if nxt else "None - all steps done",
                "", "## Blockers", _clip(t["blockers"], 300) or "None", "", "## Decisions"]
        out += ["- %s: %s" % (_clip(d["title"], 60), _clip(d["rationale"], 120)) for d in decisions] or ["- none"]
        return "\n".join(out) + "\n"

    n = len(done)
    text = build(n)
    while est_tokens(text) > MAX_TOKENS and n > 0:  # drop oldest done-steps first
        n -= 1
        text = build(n)
    return text


def write(ledger: Ledger, task_id: int, path: str, reason: str = "") -> str:
    text = generate(ledger, task_id, reason)
    with open(path, "w") as f:
        f.write(text)
    return text


def parse(text: str) -> Dict[str, Any]:
    """Extract goal, next-step seq and blockers from a HANDOFF.md."""
    def sec(name: str) -> str:
        m = re.search(r"## %s[^\n]*\n(.*?)(?=\n## |\Z)" % name, text, re.S)
        return m.group(1).strip() if m else ""
    m = re.search(r"Task: (\d+)", text)
    ns = re.match(r"\[(\d+)\]", sec("Next action"))
    return {"task_id": int(m.group(1)) if m else None, "goal": sec("Goal"),
            "next_seq": int(ns.group(1)) if ns else None, "blockers": sec("Blockers")}
