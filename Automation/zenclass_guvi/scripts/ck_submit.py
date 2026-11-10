"""
ck_submit.py - Headless (background) submitter for Guvi CodeKata solutions.

For every solutions/<slug>.py that is not yet verified solved:
  1. Local sandbox check against scraped sample cases (data/ck_problems/<slug>.json)
  2. Headless: open workspace, select PYTHON 3, inject code, Submit
  3. Verify 'Solved!' / 'Congratulations ... Geekoins' platform feedback
  4. Persist status / attempts / failure reason in data/automation_state.db
     and data/ck_results.json (max 3 attempts per problem, then FAILED)

Usage: python3 scripts/ck_submit.py [slug ...]
"""
import sys, os, re, time, json, subprocess
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from playwright.sync_api import sync_playwright
from solver.ace_adapter import inject_code, wait_for_editor
from core.state_manager import StateManager, TaskStatus

STATE = os.path.join(ROOT, "data", "storage_state.json")
PROB_DIR = os.path.join(ROOT, "data", "ck_problems")
SOL_DIR = os.path.join(ROOT, "solutions")
RESULTS = os.path.join(ROOT, "data", "ck_results.json")
MAX_ATTEMPTS = 3


def norm(s):
    return "\n".join(l.rstrip() for l in str(s).strip().splitlines())


def local_check(code, samples):
    for s in samples:
        if not s.get("input") and not s.get("output"):
            continue
        try:
            r = subprocess.run([sys.executable, "-c", code], input=s["input"] + "\n",
                               capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            return False, "local timeout"
        if norm(r.stdout) != norm(s["output"]):
            return False, f"local mismatch: in={s['input']!r} exp={s['output']!r} got={r.stdout.strip()!r} err={r.stderr[-200:]}"
    return True, ""


def main():
    results = json.load(open(RESULTS)) if os.path.exists(RESULTS) else {}
    only = set(sys.argv[1:])
    sm = StateManager()
    slugs = sorted(f[:-3] for f in os.listdir(SOL_DIR) if f.endswith(".py"))
    if only:
        slugs = [s for s in slugs if s in only]
    queue = []
    for s in slugs:
        r = results.get(s, {})
        if r.get("status") == "COMPLETED":
            continue
        code = open(os.path.join(SOL_DIR, s + ".py")).read()
        if r.get("code") == code and r.get("status") == "FAILED_PLATFORM":
            continue  # unchanged code already failed on platform; needs a revised solution
        if r.get("attempts", 0) >= MAX_ATTEMPTS and r.get("code") == code:
            continue
        queue.append((s, code))
    print(f"Queue: {len(queue)} solution(s)", flush=True)
    if not queue:
        return

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(storage_state=STATE, viewport={"width": 1400, "height": 900})
        pg = ctx.new_page()
        for i, (slug, code) in enumerate(queue, 1):
            meta = {}
            fp = os.path.join(PROB_DIR, slug + ".json")
            if os.path.exists(fp):
                meta = json.load(open(fp))
            r = results.setdefault(slug, {"attempts": 0})
            t0 = time.time()
            ok, why = local_check(code, meta.get("samples", []))
            status, reason = None, ""
            if not ok:
                status, reason = "FAILED_LOCAL", why
            else:
                try:
                    pg.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=45000)
                    time.sleep(2.5)
                    if pg.query_selector(".question-status") and "solved" in (pg.inner_text(".question-status") or "").lower():
                        status = "COMPLETED"
                        reason = "already solved on platform"
                    else:
                        try:
                            sel = pg.query_selector("select#editorModeSelectDesktop")
                            if sel and pg.evaluate("(e)=>e.value", sel) != "PYTHON 3":
                                pg.select_option("select#editorModeSelectDesktop", "PYTHON 3")
                                time.sleep(0.5)
                                no = pg.query_selector("#reset_language_modal button:has-text('No')")
                                if no and no.is_visible():
                                    no.click()
                        except Exception:
                            pass
                        if not wait_for_editor(pg, timeout=15.0) or not inject_code(pg, code, verify=True):
                            status, reason = "ERROR", "editor injection failed"
                        else:
                            time.sleep(0.5)
                            pg.click("button.submit-code, button:has-text('Submit'):not(.submit-button)", timeout=8000)
                            solved = False
                            try:
                                pg.wait_for_function("""() => {
                                    const qs = document.querySelector('.question-status');
                                    if (qs && qs.textContent.toLowerCase().includes('solved')) return true;
                                    return Array.from(document.querySelectorAll('dialog, .modal, [role="dialog"]')).some(m => {
                                        const t = m.textContent || '';
                                        if (!t.includes('Geekoins') && !t.includes('Congratulations')) return false;
                                        const st = getComputedStyle(m);
                                        return m.open || (st.display !== 'none' && st.visibility !== 'hidden' && m.offsetParent !== null);
                                    });
                                }""", timeout=30000)
                                solved = True
                            except Exception:
                                pass
                            if solved:
                                status = "COMPLETED"
                            else:
                                pane = ""
                                for s2 in [".test-pill-status", ".test-results-pane", "#test-results", ".output-container"]:
                                    el = pg.query_selector(s2)
                                    if el:
                                        pane += el.inner_text()[:400]
                                status, reason = "FAILED_PLATFORM", ("platform rejected: " + pane.strip().replace("\n", " "))[:500]
                except Exception as e:
                    status, reason = "ERROR", str(e)[:300]
            r["attempts"] = r.get("attempts", 0) + 1
            r.update({"status": status, "reason": reason, "code": code,
                      "ts": datetime.now(timezone.utc).isoformat(), "difficulty": meta.get("difficulty")})
            dur = round(time.time() - t0, 2)
            final_fail = status != "COMPLETED" and r["attempts"] >= MAX_ATTEMPTS
            try:
                sm.batch_record_tasks([{
                    "task_id": f"guvi-{slug}", "platform": "guvi", "task_category": "CodeKata",
                    "title": meta.get("title", slug), "url": f"https://www.guvi.in/code-kata/{slug}/",
                    "status": TaskStatus.COMPLETED.value if status == "COMPLETED" else (TaskStatus.FAILED.value if final_fail else TaskStatus.PENDING.value),
                    "attempt_count": r["attempts"],
                    "result": "PASSED" if status == "COMPLETED" else status,
                    "failure_reason": None if status == "COMPLETED" else reason,
                    "next_action": "NONE" if status == "COMPLETED" else ("HUMAN_REVIEW" if final_fail else "REVISE_SOLUTION"),
                    "time_spent_seconds": dur,
                    "metadata": {"slug": slug, "difficulty": meta.get("difficulty"), "checked_at": r["ts"]},
                }])
            except Exception as e:
                print("state db note:", e)
            json.dump(results, open(RESULTS, "w"), indent=1)
            print(f"[{i}/{len(queue)}] {slug}: {status} {reason[:160]}", flush=True)
            time.sleep(1.0)
        try:
            ctx.storage_state(path=STATE)
        except Exception:
            pass
        b.close()
    done = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    print(f"TOTAL COMPLETED: {done} / {len(results)} attempted", flush=True)


if __name__ == "__main__":
    main()
