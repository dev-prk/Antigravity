"""
solve_codekata_100_python.py — Drive GUVI CodeKata Solved -> 100% in Strictly 1 Foreground Brave Tab (Python-First).

Two-Stage Precision Sweep:
- Stage A (Fast Precomputed Sweep): Submits all unsolved problems pre-computed in data/ck_py_precomputed/
  at ~1.6s/question, ALWAYS selecting PYTHON 3 (or PYTHON 2) whenever Python is in select#editorModeSelectDesktop,
  and running up to 2 instant self-debugging repairs using GUVI's `Run Code` Expected-vs-Actual test output!
- Stage B (Live Catalog Sweep of Yet-to-Start & In-Progress): Filters `https://www.guvi.in/code-kata/` by
  `Yet to start` and `In progress` (50/page) and clicks every remaining unsolved row directly in-place
  (catching all ~66 special/apostrophe slugs!) to push Solved % as close to 100.00% as GUVI's judge allows.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Set, Tuple

from playwright.sync_api import BrowserContext, Page, sync_playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT / "scripts"))
from kata_common import (  # noqa: E402
    PYTHON_FIRST_LANGS,
    call_llm,
    dismiss_popups,
    enforce_single_tab,
    open_single_brave_tab,
    strip_fences,
    verify_code_locally,
)

PY_PRE_DIR = ROOT / "data" / "ck_py_precomputed"
OLD_PRE_DIR = ROOT / "data" / "ck_precomputed"
REPAIR_QUEUE_DIR = ROOT / "data" / "ck_repair_queue"
PROB_DIR = ROOT / "data" / "ck_problems"
REPAIR_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_JSON = ROOT / "data" / "ck_results.json"
LIVE_STATUS_JSON = ROOT / "reports" / "CODEKATA_LIVE_STATUS.json"
SOL_DIR = ROOT / "solutions"

LANG_EXT = {
    "PYTHON 3": "py", "PYTHON 2": "py", "C++": "cpp", "C": "c",
    "JAVASCRIPT": "js", "JAVA": "java", "JAVA 8": "java", "BASH": "sh", "SQLITE": "sql",
}


def log(msg: str) -> None:
    print(f"[CK100 {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_ck_status(results: Dict[str, Any], start_ts: float) -> int:
    RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
    solved_cnt = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    other_cnt = sum(1 for v in results.values() if v.get("status") != "COMPLETED")
    LIVE_STATUS_JSON.write_text(
        json.dumps(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "verified_solved_total": solved_cnt,
                "other_attempted": other_cnt,
                "elapsed_minutes": round((time.time() - start_ts) / 60.0, 1),
                "py_precomputed_ready": len(list(PY_PRE_DIR.glob("*.json"))),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return solved_cnt


def select_python_or_locked(page: Page) -> Tuple[str, str]:
    try:
        page.wait_for_function(
            "() => (document.querySelector('select#editorModeSelectDesktop')?.options?.length || 0) > 0",
            timeout=2000,
        )
    except Exception:
        pass
    info = page.evaluate(
        """() => {
            const s = document.querySelector('select#editorModeSelectDesktop');
            const opts = s && s.options.length ? Array.from(s.options).map(o => o.value) : ['PYTHON 3'];
            return { cur: s?.value || 'PYTHON 3', opts, did: s?.getAttribute('data-id') || '' };
        }"""
    )
    chosen = next((lp for lp in PYTHON_FIRST_LANGS if lp in info["opts"]), info["opts"][0])
    if info["cur"] != chosen and info["did"]:
        did = info["did"]
        ss = page.locator(f'.ss-main[data-id="{did}"]').first
        if ss.count() > 0 and ss.is_visible():
            ss.click(force=True)
            page.wait_for_timeout(120)
            opt = page.locator(f'.ss-content[data-id="{did}"] .ss-option').filter(has_text=re.compile(f"^{re.escape(chosen)}$")).first
            if opt.count() > 0:
                opt.click(force=True)
                page.wait_for_timeout(180)
                page.evaluate("() => { const n = Array.from(document.querySelectorAll('button')).find(b => b.offsetParent!==null && b.innerText.trim()==='No'); if (n) n.click(); }")
    starter = page.evaluate("() => { try { return window.ace ? (window.ace.edit('editor').getValue() || '') : ''; } catch(e) { return ''; } }")
    return chosen, starter


def submit_and_check(page: Page, code: str) -> Tuple[bool, str]:
    page.evaluate(
        """(src) => {
            if (window.ace) {
                const ed = window.ace.edit('editor');
                ed.setValue(src, -1);
                ed.clearSelection();
            }
        }""",
        code,
    )
    page.evaluate("() => document.querySelector('button.submit-code')?.click()")
    page.wait_for_timeout(340)
    for _ in range(95):
        page.wait_for_timeout(125)
        v = page.evaluate(
            """() => {
                const qs = document.querySelector('.question-status');
                if (qs && qs.innerText.toLowerCase().includes('solved')) return { ok: true, done: true, msg: 'SOLVED_STATUS' };
                for (const m of document.querySelectorAll('dialog, .modal, [role="dialog"]')) {
                    const t = m.innerText || '';
                    if ((m.open || m.offsetParent !== null) && (t.includes('Geekoins') || t.includes('Congratulations'))) {
                        return { ok: true, done: true, msg: 'SOLVED_MODAL' };
                    }
                }
                const b = document.body.innerText || '';
                if (b.includes('Answer\\nCorrect Answer')) return { ok: true, done: true, msg: 'CORRECT_ANSWER' };
                for (const tag of ['Wrong Answer', 'Compiler Error', 'Compilation Error', 'Runtime Error', 'Time Limit Exceeded']) {
                    if (b.includes('Answer\\n' + tag)) {
                        const i = b.indexOf('Answer\\n' + tag);
                        return { ok: false, done: true, msg: b.slice(i, i + 400) };
                    }
                }
                return { ok: false, done: false, msg: '' };
            }"""
        )
        if v["done"]:
            return bool(v["ok"]), str(v["msg"])
    return False, "VERDICT_TIMEOUT"


def synthesize_or_repair(lang: str, prob_text: str, starter: str, samples: List[Dict[str, str]], err_ctx: str, seed: int) -> str:
    lang_rule = (
        "Write a complete standalone Python 3 program reading from sys.stdin and printing exact output to sys.stdout."
        if lang.startswith("PYTHON")
        else f"Write a complete standalone {lang} program reading stdin and printing exact stdout."
    )
    if lang in ("JAVA", "JAVA 8"):
        lang_rule += " Use `public class Main` with `public static void main(String[] args)` unless Starter Code defines a specific class name."

    samples_txt = "\n".join(
        f"Case {i+1} Input:\n{s.get('input','')}\nCase {i+1} Exact Expected Output (repr={s.get('output','')!r}):\n{s.get('output','')}"
        for i, s in enumerate(samples[:4])
    )
    sys_p = (
        f"Expert {lang} competitive programmer. {lang_rule}\n"
        "Output ONLY raw code (no markdown prose). Match exact leading spaces on pyramid/pattern rows, "
        "no extra trailing spaces at line ends, exact '-1' / 'yes' / 'no' casing, and optimal time complexity."
    )
    user_p = f"Problem:\n{prob_text[:2800]}\n\n{samples_txt}\n"
    if starter.strip():
        user_p += f"\nStarter / Template Code:\n{starter[:700]}\n"
    if err_ctx:
        user_p += f"\nPREVIOUS ATTEMPT FAILED:\n{err_ctx[:900]}\nFix all edge cases & exact output formatting!\n"

    best = ""
    for tr in range(2):
        raw = call_llm(sys_p, user_p, seed + tr * 3)
        if not raw:
            continue
        code = strip_fences(raw)
        best = code
        ok, lerr = verify_code_locally(code, lang, samples)
        if ok:
            return code
        user_p += f"\nLocal sample check failed:\n{lerr}\nReturn ONLY fixed {lang} code."
    return best


def solve_current_codekata_page(
    page: Page,
    pre_code: str,
    pre_lang: str,
    results: Dict[str, Any],
    seq: int,
    non_blocking: bool = True,
) -> bool:
    slug = page.url.split("?")[0].rstrip("/").split("/")[-1]
    t0 = time.time()
    try:
        page.wait_for_selector("#editor", timeout=5500)
        page.wait_for_function("() => Boolean(window.ace)", timeout=4000)
    except Exception:
        results[slug] = {"status": "SKIPPED_NO_EDITOR", "attempts": 1}
        return False

    if page.evaluate("() => Boolean(document.querySelector('.question-status')?.innerText?.toLowerCase()?.includes('solved'))"):
        results[slug] = {"status": "COMPLETED", "language": "PYTHON 3", "attempts": 1, "duration_s": round(time.time() - t0, 2)}
        return True

    lang, starter = select_python_or_locked(page)
    pfile = PROB_DIR / f"{slug}.json"
    meta = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else {}
    samples = meta.get("samples") or []
    prob_text = meta.get("description") or page.evaluate(
        "() => (document.querySelector('.problem-description, #problem-description, main')?.textContent || document.body.innerText).slice(0, 3000)"
    )

    # Fast non-blocking path: if language differs from precomputed or code missing, queue to background worker in 0ms!
    if non_blocking and (not pre_code.strip() or lang != pre_lang):
        prev_rep = results.get(slug, {}).get("queued_repair", False)
        if not prev_rep:
            (REPAIR_QUEUE_DIR / f"{slug}.json").write_text(
                json.dumps({"slug": slug, "lang": lang, "prob_text": prob_text, "starter": starter, "samples": samples, "err_ctx": f"Required locked language: {lang}"}),
                encoding="utf-8",
            )
            results[slug] = {"status": "QUEUED_REPAIR", "language": lang, "queued_repair": True, "attempts": 1}
            return False

    max_atts = 1 if non_blocking else 2
    code = pre_code if (pre_code.strip() and lang == pre_lang) else ""
    err_ctx = ""

    for att in range(max_atts):
        if not code.strip() or att > 0:
            code = synthesize_or_repair(lang, prob_text, starter, samples, err_ctx, seq + att * 5)
        if not code.strip():
            continue
        ok, msg = submit_and_check(page, code)
        if ok:
            ext = LANG_EXT.get(lang, "py")
            (SOL_DIR / f"{slug}.{ext}").write_text(code, encoding="utf-8")
            results[slug] = {"status": "COMPLETED", "language": lang, "attempts": att + 1, "reason": msg, "duration_s": round(time.time() - t0, 2)}
            return True

        # Non-blocking repair queue: capture Run Code diff in 0.9s and hand off to background worker!
        page.evaluate("() => document.querySelector('button.run-code')?.click()")
        page.wait_for_timeout(900)
        run_diff = page.evaluate(
            """() => {
                const t = document.body.innerText || '';
                const i = t.indexOf('Test Result');
                return i !== -1 ? t.slice(i, i + 900) : t.slice(-800);
            }"""
        )
        err_ctx = f"Verdict: {msg[:250]}\nRun Code Test Result:\n{run_diff}"
        if non_blocking and not results.get(slug, {}).get("queued_repair"):
            (REPAIR_QUEUE_DIR / f"{slug}.json").write_text(
                json.dumps({"slug": slug, "lang": lang, "prob_text": prob_text, "starter": starter, "samples": samples, "err_ctx": err_ctx}),
                encoding="utf-8",
            )
            results[slug] = {"status": "FAILED_PLATFORM", "language": lang, "queued_repair": True, "attempts": 1, "reason": err_ctx[:240], "duration_s": round(time.time() - t0, 2)}
            return False

    results[slug] = {"status": "FAILED_PLATFORM", "language": lang, "queued_repair": True, "attempts": max_atts, "reason": err_ctx[:240], "duration_s": round(time.time() - t0, 2)}
    return False


def sweep_live_status_filter(ctx: BrowserContext, page: Page, filter_label: str, results: Dict[str, Any], start_ts: float, seq_ref: List[int]) -> None:
    """Filters https://www.guvi.in/code-kata/ by `Yet to start` or `In progress` and clicks every unsolved row in place."""
    seen_titles: Set[str] = set()
    for pno in range(1, 25):
        while True:
            enforce_single_tab(ctx, page)
            page.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1500)
            dismiss_popups(page)
            try:
                did = page.evaluate("() => document.querySelector('select#itemsPerPage')?.getAttribute('data-id') || ''")
                if did:
                    page.locator(f'.ss-main[data-id="{did}"]').first.click(force=True)
                    page.wait_for_timeout(120)
                    page.locator(f'.ss-content[data-id="{did}"] .ss-option', has_text="50").first.click(force=True)
                    page.wait_for_timeout(700)
                page.locator("#status-filter-id").first.click(force=True)
                page.wait_for_timeout(200)
                page.locator(f"li:has-text('{filter_label}')").first.click(force=True)
                page.wait_for_timeout(1000)
                if pno > 1:
                    for _ in range(pno - 1):
                        nb = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
                        if nb.count() == 0 or nb.get_attribute("disabled") is not None:
                            return
                        nb.click(force=True)
                        page.wait_for_timeout(450)
            except Exception:
                return

            rows = page.evaluate(
                """() => Array.from(document.querySelectorAll('tbody tr')).map((r, i) => ({
                    i,
                    done: r.innerHTML.includes('completed-icon_svg__a') || r.innerHTML.includes('#0DBA4B'),
                    title: (r.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 90)
                }))"""
            )
            if not rows:
                return
            cand = next((r for r in rows if not r["done"] and r["title"] and r["title"] not in seen_titles), None)
            if cand is None:
                break

            seen_titles.add(cand["title"])
            seq_ref[0] += 1
            page.locator("tbody tr").nth(cand["i"]).click(force=True)
            page.wait_for_timeout(1500)
            dismiss_popups(page)
            slug = page.url.split("?")[0].rstrip("/").split("/")[-1]
            pre_f = PY_PRE_DIR / f"{slug}.json"
            pre_code = json.loads(pre_f.read_text(encoding="utf-8")).get("code", "") if pre_f.exists() else ""
            ok = solve_current_codekata_page(page, pre_code, "PYTHON 3", results, seq_ref[0], non_blocking=False)
            solved_tot = save_ck_status(results, start_ts) if seq_ref[0] % 5 == 0 else sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            log(f"[LIVE-{filter_label} #{seq_ref[0]}] {slug} -> {'SOLVED' if ok else 'FAILED'} | TOTAL_SOLVED={solved_tot}")


def main() -> int:
    start_ts = time.time()
    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    tried_pre: Set[str] = set()
    seq_ref = [0]

    with sync_playwright() as pw:
        ctx, page = open_single_brave_tab(pw, disable_images=True)
        try:
            # Stage A0: Immediately consume the ~510 unvisited PYTHON 3 solutions already in data/ck_precomputed/
            unvisited_old = [
                p for p in sorted(OLD_PRE_DIR.glob("*__PYTHON_3.json"))
                if "__retry" not in p.name and p.name.split("__")[0] not in results
            ]
            log(f"Stage A0: Sweeping {len(unvisited_old)} unvisited precomputed Python-3 CodeKata solutions...")
            for pf in unvisited_old:
                enforce_single_tab(ctx, page)
                slug = pf.name.split("__")[0]
                tried_pre.add(slug)
                seq_ref[0] += 1
                pdata = json.loads(pf.read_text(encoding="utf-8"))
                page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=25000)
                ok = solve_current_codekata_page(page, pdata.get("code", ""), "PYTHON 3", results, seq_ref[0])
                solved_tot = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
                log(f"[UNVIS #{seq_ref[0]}] {slug} ({results.get(slug,{}).get('language','PY3')}) -> {'SOLVED' if ok else 'FAILED'} | SOLVED={solved_tot}")
                if seq_ref[0] % 8 == 0:
                    save_ck_status(results, start_ts)

            # Stage A1: Fast exact-whitespace Python-3 precomputed sweep
            log("Stage A1: Sweeping exact-whitespace Python-3 precomputed CodeKata solutions...")
            while True:
                ready = [
                    p for p in sorted(PY_PRE_DIR.glob("*.json"), key=lambda x: (0 if "__repaired" in x.name else 1, x.name))
                    if p.name not in tried_pre and results.get(p.stem.split("__")[0], {}).get("status") not in ("COMPLETED", "SKIPPED_NO_EDITOR")
                ]
                if not ready:
                    break
                for pf in ready:
                    enforce_single_tab(ctx, page)
                    tried_pre.add(pf.name)
                    pdata = json.loads(pf.read_text(encoding="utf-8"))
                    slug = pdata.get("slug") or pf.stem.split("__")[0]
                    seq_ref[0] += 1
                    page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=25000)
                    ok = solve_current_codekata_page(page, pdata.get("code", ""), pdata.get("lang", "PYTHON 3"), results, seq_ref[0], non_blocking=True)
                    solved_tot = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
                    log(f"[PRE #{seq_ref[0]}] {slug} ({results.get(slug,{}).get('language','PY3')}) -> {'SOLVED' if ok else 'QUEUED/FAILED'} | SOLVED={solved_tot}")
                    if seq_ref[0] % 8 == 0:
                        save_ck_status(results, start_ts)

            # Stage B: Live table sweep of `Yet to start` & `In progress` (catches all non-standard slugs!)
            log("Stage B: Sweeping live `Yet to start` and `In progress` tables on CodeKata...")
            sweep_live_status_filter(ctx, page, "Yet to start", results, start_ts, seq_ref)
            sweep_live_status_filter(ctx, page, "In progress", results, start_ts, seq_ref)
        finally:
            final_cnt = save_ck_status(results, start_ts)
            ctx.close()

    log(f"=== CODEKATA 100% SWEEP COMPLETE: {final_cnt} VERIFIED SOLVED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
