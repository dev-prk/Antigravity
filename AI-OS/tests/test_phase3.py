import json, os, subprocess, sys, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from aios.db import Ledger, TABLES
from aios.budget import Budget, OK, WARN, STOP
from aios import handoff
from aios.policy import PolicyEngine, Decision

BENCH = os.path.join(os.path.dirname(ROOT), "Random Ask", "tests", "evaluation", "benchmarks.jsonl")


def bench_ids(n):
    with open(BENCH) as f:
        return [json.loads(l)["id"] for l in f if l.strip()][:n]


class TestDB(unittest.TestCase):
    def test_tables_and_crud(self):
        l = Ledger()
        names = {r[0] for r in l.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for t in TABLES:
            self.assertIn(t, names)
        tid = l.create_task("g", 100, ["a", "b"])
        l.add_evidence(tid, "test", "ok"); l.add_decision(tid, "d", "why"); l.add_fact(tid, "f", "verified", "src")
        l.checkpoint(tid, "r"); l.audit(tid, "t", "x"); Budget(l, tid, 100).record(5)
        for t in TABLES:
            self.assertGreaterEqual(len(l.rows(t, tid)), 1, t)
        l.set_step(tid, 1, "done", "r1")
        self.assertEqual(l.next_step(tid)["seq"], 2)
        with self.assertRaises(Exception):
            l.add_fact(tid, "bad", "nonsense")


class TestBudget(unittest.TestCase):
    def test_thresholds(self):
        l = Ledger(); tid = l.create_task("g", 100)
        b = Budget(l, tid, 100)
        self.assertEqual(b.record(50), OK)
        self.assertEqual(b.record(30), WARN)
        self.assertEqual(len(l.rows("checkpoints", tid)), 1)
        self.assertEqual(b.record(5), OK)          # warn fires only once
        self.assertEqual(b.record(15), STOP)
        self.assertEqual(b.used_task(), 100)
        self.assertFalse(b.can_afford(1))
        self.assertEqual(l.get_task(tid)["status"], "paused")

    def test_session_limit(self):
        l = Ledger(); tid = l.create_task("g", 1000)
        b = Budget(l, tid, 1000, session_limit=10)
        self.assertEqual(b.record(10), STOP)


class TestHandoff(unittest.TestCase):
    def test_sections_and_size(self):
        l = Ledger(); tid = l.create_task("Goal " * 200, 100, ["step %d " % i * 20 for i in range(300)])
        for i in range(1, 201):
            l.set_step(tid, i, "done", "r" * 500)
        for i in range(30):
            l.add_decision(tid, "d%d" % i, "x" * 500)
        l.set_task(tid, blockers="b" * 2000)
        text = handoff.generate(l, tid)
        self.assertLessEqual(handoff.est_tokens(text), handoff.MAX_TOKENS)
        for h in ("## Goal", "## Done", "## Next action", "## Blockers"):
            self.assertIn(h, text)
        p = handoff.parse(text)
        self.assertEqual(p["task_id"], tid); self.assertEqual(p["next_seq"], 201)


class TestPolicy(unittest.TestCase):
    def test_redaction_not_disableable(self):
        pe = PolicyEngine(enable_redaction=False)
        out = pe.redact_secrets("key sk-abcdefghijklmnopqrstuvwx1234 and password=hunter2hunter2")
        self.assertNotIn("hunter2hunter2", out); self.assertNotIn("abcdefghijklmnopqrstuvwx1234", out)

    def test_external_delete_never_allowed(self):
        pe = PolicyEngine()
        d = pe.check_action("delete", "/Users/devesh/Desktop/x.txt")
        self.assertNotEqual(d.decision, Decision.ALLOW)
        d2 = pe.check_action("delete", "/Users/devesh/Desktop/x.txt", profile_override="SANDBOX_AUTONOMOUS")
        self.assertNotEqual(d2.decision, Decision.ALLOW)


WORKER = """
import sys; sys.path.insert(0, %r)
from aios.db import Ledger; from aios.budget import Budget; from aios.runner import run
db, hp, tid, die = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
l = Ledger(db); b = Budget(l, tid, 1000, session="%s")
print(run(l, tid, b, hp, lambda s: 100, die_after=None if die == "no" else int(die)))
"""


class TestKillResume(unittest.TestCase):
    def test_kill_then_resume(self):
        ids = bench_ids(6)                      # steps come from the existing benchmark suite
        self.assertEqual(len(ids), 6)
        d = tempfile.mkdtemp(); db = os.path.join(d, "s.db"); hp = os.path.join(d, "HANDOFF.md")
        l = Ledger(db); tid = l.create_task("run benchmark cases", 1000, ids); l.close()
        r1 = subprocess.run([sys.executable, "-c", WORKER % (ROOT, "s1"), db, hp, str(tid), "3"], capture_output=True, text=True)
        self.assertEqual(r1.returncode, 137)    # killed hard mid-task
        with open(hp) as f:
            text = f.read()
        self.assertEqual(handoff.parse(text)["next_seq"], 4)
        l = Ledger(db)
        self.assertEqual([s["status"] for s in l.steps(tid)], ["done"] * 3 + ["pending"] * 3)
        l.close()
        r2 = subprocess.run([sys.executable, "-c", WORKER % (ROOT, "s2"), db, hp, str(tid), "no"], capture_output=True, text=True)
        self.assertEqual(r2.stdout.strip(), "done", r2.stderr)
        l = Ledger(db)
        self.assertTrue(all(s["status"] == "done" for s in l.steps(tid)))
        self.assertEqual(Budget(l, tid, 1000).used_task(), 600)   # no step re-run / double-counted


if __name__ == "__main__":
    unittest.main()
