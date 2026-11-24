"""Deterministic grader. No LLM. Usage: python3 check.py <path-to-SkillTest>"""
import sys, pathlib, importlib
app = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../../SkillTest").resolve()
sys.path.insert(0, str(app))
ea = importlib.import_module("explain_analyzer")
here = pathlib.Path(__file__).parent

def flat(n, out):
    out.append(n); [flat(c, out) for c in n["children"]]; return out

def nodes(text):
    r = ea.analyze_explain_and_query(text)
    tree = r.get("plan_tree") or r.get("tree") or r.get("nodes")
    trees = tree if isinstance(tree, list) else [tree]
    out = []
    for t in trees: flat(t, out)
    return {(n["node_type"] + (" " + n["relation"] if n.get("relation") else "")): n for n in out}

# Expected self (exclusive) ms, worked by hand: per-worker loop avg is already wall-clock.
EXPECT = {"Gather": 20.0, "Parallel Hash Join": 76.5, "Parallel Seq Scan orders": 600.0,
          "Parallel Hash": 1.5, "Parallel Seq Scan customers": 2.0}
ok = True
got = nodes((here / "parallel_plan.txt").read_text())
for k, want in EXPECT.items():
    n = got.get(k)
    v = n and n["exclusive_ms"]
    good = n is not None and abs(v - want) <= 1.0
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {k:28} self={v}  want={want}")
pcts = sum(n["pct_of_total"] for n in got.values())
good = pcts <= 101.0; ok &= good
print(f"{'PASS' if good else 'FAIL'}  sum of % of total = {pcts:.1f} (must be <= 100)")
# Regression: non-parallel nested loop must stay exact (from test 2 audit)
nl = """Nested Loop  (cost=0.29..900.00 rows=5000 width=8) (actual time=0.020..245.000 rows=5000 loops=1)
  ->  Seq Scan on a  (cost=0.00..80.00 rows=5000 width=4) (actual time=0.005..5.000 rows=5000 loops=1)
  ->  Index Scan using b_pkey on b  (cost=0.29..0.30 rows=1 width=4) (actual time=0.040..0.048 rows=1 loops=5000)
        Index Cond: (id = a.id)
Planning Time: 0.1 ms
Execution Time: 246.0 ms"""
g2 = nodes(nl)
for k, want in {"Index Scan b": 240.0, "Seq Scan a": 5.0, "Nested Loop": 0.0}.items():
    v = g2.get(k, {}).get("exclusive_ms"); good = v is not None and abs(v - want) <= 1.0; ok &= good
    print(f"{'PASS' if good else 'FAIL'}  regression {k:17} self={v}  want={want}")
print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
