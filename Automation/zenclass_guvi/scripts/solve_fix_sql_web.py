"""
solve_fix_sql_web.py — Fast In-Place Single-Tab Foreground Brave Solver for:
1. FixTheCode (https://www.guvi.in/debugging/) — Strictly PYTHON 3 first (all code questions in Python)
2. SQLKata (https://www.guvi.in/sqlkata/) — Multi-subquestion SQL with live Database Tables + Run Code self-debugging
3. WebKata (https://www.guvi.in/webkata/) — HTML, CSS, JavaScript, and Bootstrap multi-tab solver + test-case retries
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable, Dict, List, Set, Tuple

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
)

MULTI_REPORT = ROOT / "reports" / "MULTI_KATA_LIVE_STATUS.json"
SOL_FIX_DIR = ROOT / "solutions_fixthecode"
SOL_SQL_DIR = ROOT / "solutions_sqlkata"
SOL_WEB_DIR = ROOT / "solutions_webkata"
for _d in (SOL_FIX_DIR, SOL_SQL_DIR, SOL_WEB_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[MULTI {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_multi_checkpoint(state: Dict[str, Any]) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    MULTI_REPORT.write_text(json.dumps(state, indent=2), encoding="utf-8")


def set_50_per_page(page: Page) -> None:
    try:
        did = page.evaluate("() => document.querySelector('select#itemsPerPage')?.getAttribute('data-id') || ''")
        if did:
            page.locator(f'.ss-main[data-id="{did}"]').first.click(force=True)
            page.wait_for_timeout(150)
            page.locator(f'.ss-content[data-id="{did}"] .ss-option', has_text="50").first.click(force=True)
            page.wait_for_timeout(800)
    except Exception:
        pass


def select_python_first(page: Page) -> str:
    try:
        page.wait_for_function(
            "() => (document.querySelector('select#editorModeSelectDesktop')?.options?.length || 0) > 0",
            timeout=1800,
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
    return chosen


def poll_code_verdict(page: Page) -> Tuple[bool, str]:
    page.evaluate("() => document.querySelector('button.submit-code')?.click()")
    page.wait_for_timeout(350)
    for _ in range(85):
        page.wait_for_timeout(130)
        res = page.evaluate(
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
                if (b.includes('Answer\\nCorrect Answer') || b.includes('Solved!')) return { ok: true, done: true, msg: 'CORRECT' };
                for (const tag of ['Wrong Answer', 'Compiler Error', 'Compilation Error', 'Runtime Error', 'Time Limit Exceeded']) {
                    if (b.includes('Answer\\n' + tag)) {
                        const i = b.indexOf('Answer\\n' + tag);
                        return { ok: false, done: true, msg: b.slice(i, i + 380) };
                    }
                }
                return { ok: false, done: false, msg: '' };
            }"""
        )
        if res["done"]:
            return bool(res["ok"]), str(res["msg"])
    return False, "TIMEOUT"


def sweep_table_inplace(
    ctx: BrowserContext,
    page: Page,
    base_url: str,
    label: str,
    solve_fn: Callable[[Page, int], bool],
) -> None:
    """Iterates every page of a GUVI table catalog in 1 tab and solves each uncompleted row in place (zero double-navigation)."""
    page.goto(base_url, wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(1800)
    dismiss_popups(page)

    max_p = page.evaluate(
        """() => {
            const nums = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => /^\\d+$/.test(t)).map(Number);
            return nums.length ? Math.max(...nums) : 1;
        }"""
    )
    seen_titles: Set[str] = set()
    seq = 0

    for pno in range(1, max_p + 1):
        while True:
            enforce_single_tab(ctx, page)
            if "limit=" in base_url:
                p_url = re.sub(r"page=\d+", f"page={pno}", base_url)
                page.goto(p_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(1100)
                dismiss_popups(page)
            else:
                page.goto(base_url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(1300)
                dismiss_popups(page)
                if pno > 1:
                    num_btn = page.locator("button").filter(has_text=re.compile(f"^{pno}$")).first
                    if num_btn.count() > 0 and num_btn.is_visible():
                        num_btn.click(force=True)
                        page.wait_for_timeout(600)
                    else:
                        for _ in range(pno - 1):
                            nb = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
                            if nb.count() == 0 or nb.get_attribute("disabled") is not None:
                                return
                            nb.click(force=True)
                            page.wait_for_timeout(500)

            rows = page.evaluate(
                """() => Array.from(document.querySelectorAll('tbody tr')).map((r, i) => ({
                    i,
                    done: r.innerHTML.includes('completed-icon_svg__a') || r.innerHTML.includes('#0DBA4B'),
                    title: (r.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 90)
                }))"""
            )
            nxt = next((r for r in rows if not r["done"] and r["title"] and r["title"] not in seen_titles), None)
            if nxt is None:
                break

            seen_titles.add(nxt["title"])
            seq += 1
            trs = page.locator("tbody tr")
            if nxt["i"] >= trs.count():
                break
            trs.nth(nxt["i"]).click(force=True)
            page.wait_for_timeout(1700)
            dismiss_popups(page)
            try:
                ok = solve_fn(page, seq)
            except Exception as exc:
                log(f"[{label} #{seq}] Error on {nxt['title'][:45]}: {str(exc)[:120]}")
                ok = False
            log(f"[{label} #{seq} p{pno}] {nxt['title'][:50]} -> {'SOLVED' if ok else 'FAILED'}")


def solve_one_fixthecode(page: Page, seq: int, state: Dict[str, Any]) -> bool:
    slug = page.url.split("?")[0].rstrip("/").split("/")[-1]
    if page.evaluate("() => document.body.innerText.includes('Solved!')"):
        state["fixthecode_solved"] += 1
        return True
    lang = select_python_first(page)
    starter = page.evaluate("() => window.ace ? window.ace.edit('editor').getValue() : ''")
    prob_txt = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 2600)")
    err_fb = ""
    for att in range(3):
        code = strip_fences(
            call_llm(
                f"Expert {lang} competitive programmer & debugger. Fix the bug or write a clean {lang} solution reading stdin and printing exact stdout. Output ONLY raw {lang} code.",
                f"Problem:\n{prob_txt}\n\nBuggy Starter Code:\n{starter}\n{err_fb}",
                seq + att * 3,
            )
        )
        if not code.strip():
            continue
        page.evaluate("(c) => window.ace.edit('editor').setValue(c, -1)", code)
        ok, msg = poll_code_verdict(page)
        if ok:
            (SOL_FIX_DIR / f"{slug}.py").write_text(code, encoding="utf-8")
            state["fixthecode_solved"] += 1
            save_multi_checkpoint(state)
            return True
        page.evaluate("() => document.querySelector('button.run-code')?.click()")
        page.wait_for_timeout(1300)
        run_diff = page.evaluate("() => (document.body.innerText || '').slice(-900)")
        err_fb = f"\nPrevious attempt failed ({msg[:180]}).\nTest Case Output:\n{run_diff}\nFix every edge case & exact spacing!"
    save_multi_checkpoint(state)
    return False


def solve_one_sqlkata(page: Page, seq: int, state: Dict[str, Any]) -> bool:
    slug = page.url.split("?")[0].rstrip("/").split("/")[-1]
    if page.evaluate("() => document.body.innerText.includes('Solved!')"):
        state["sqlkata_solved"] += 1
        return True
    scen = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 1000)")
    # Ensure Database Tables pane is open and cache initial schema so it is never lost
    if not page.evaluate("() => document.body.innerText.includes('Database Tables')"):
        page.evaluate("() => { for (const b of document.querySelectorAll('button')) if (b.offsetParent!==null && b.innerText.trim()==='Tables') b.click(); }")
        page.wait_for_timeout(400)
    base_tbl = page.evaluate("() => { const t = document.body.innerText; const i = t.indexOf('Database Tables'); return i!==-1 ? t.slice(i, i+2600) : ''; }")

    n_q = page.locator("div.collapse").count()
    saved_queries: List[str] = []

    for qi in range(n_q):
        if page.evaluate(f"() => document.querySelectorAll('div.collapse')[{qi}]?.className?.includes('correct-submission')"):
            continue
        page.locator("div.collapse").nth(qi).click(force=True)
        page.wait_for_timeout(400)
        if not page.evaluate("() => document.body.innerText.includes('Database Tables')"):
            page.evaluate("() => { for (const b of document.querySelectorAll('button')) if (b.offsetParent!==null && b.innerText.trim()==='Tables') b.click(); }")
            page.wait_for_timeout(300)
        cur_tbl = page.evaluate("() => { const t = document.body.innerText; const i = t.indexOf('Database Tables'); return i!==-1 ? t.slice(i, i+2600) : ''; }") or base_tbl
        qtxt = page.evaluate(f"() => document.querySelectorAll('div.collapse')[{qi}]?.innerText || ''")
        sql_err = ""

        for att in range(3):
            sql = strip_fences(
                call_llm(
                    "Expert SQL developer (MySQL / SQLite) for GUVI SQLKata. "
                    "Write ONLY the exact SQL query/statement(s) requested ending with semicolon. "
                    "Match exact table/column names & exact string spellings in Database Tables. No prose.",
                    f"Scenario:\n{scen}\n\n{cur_tbl}\n\nActive Sub-Question:\n{qtxt}\n{sql_err}",
                    seq + qi * 3 + att * 2,
                )
            ).strip()
            if not sql:
                continue
            # Directly Submit (NEVER click Run Code first, which double-executes INSERT/UPDATE/DELETE and disables Submit!)
            page.evaluate("(s) => window.ace.edit('editor').setValue(s, -1)", sql)
            page.evaluate("() => document.querySelector('button.submit-code')?.click()")

            sub_ok = False
            for _ in range(22):
                page.wait_for_timeout(160)
                sub_ok = page.evaluate(
                    f"() => Boolean(document.querySelectorAll('div.collapse')[{qi}]?.className?.includes('correct-submission') || document.body.innerText.includes('Solved!'))"
                )
                if sub_ok:
                    break

            dismiss_popups(page)
            page.evaluate(
                """() => {
                    for (const m of document.querySelectorAll('dialog, .modal')) {
                        if (m.open || m.offsetParent !== null) {
                            const cb = Array.from(m.querySelectorAll('button')).find(b => /close|✕/i.test(b.innerText));
                            if (cb) cb.click();
                        }
                    }
                }"""
            )
            if sub_ok:
                saved_queries.append(f"-- Q{qi+1}\n{sql}")
                break
            page.evaluate("() => { for (const b of document.querySelectorAll('button')) if (b.offsetParent!==null && b.innerText.trim()==='Output') b.click(); }")
            page.wait_for_timeout(220)
            out_msg = page.evaluate("() => { const t = document.body.innerText; const i = t.indexOf('Tables\\nOutput'); return i!==-1 ? t.slice(i, i+600) : t.slice(-500); }")
            sql_err = (
                f"\nPrevious SQL was rejected by judge:\n{sql}\nJudge / Console Output:\n{out_msg}\n"
                "Fix exact column names/order, aliases (try WITHOUT alias if exact column name matches, or exact alias requested), "
                "ROUND(..., 2) vs unrounded, or single statement vs multi-statement!"
            )

    prob_ok = page.evaluate(
        "() => document.body.innerText.includes('Solved!') || (document.querySelectorAll('div.collapse').length > 0 && Array.from(document.querySelectorAll('div.collapse')).every(c => c.className.includes('correct-submission')))"
    )
    if prob_ok:
        state["sqlkata_solved"] += 1
        if saved_queries:
            (SOL_SQL_DIR / f"{slug}.sql").write_text("\n\n".join(saved_queries) + "\n", encoding="utf-8")
    save_multi_checkpoint(state)
    return bool(prob_ok)


def click_visible_webkata_tab(page: Page, tab_name: str) -> None:
    page.evaluate(
        """(tn) => {
            const btn = Array.from(document.querySelectorAll('button.tab-text')).find(
                b => b.offsetParent !== null && b.innerText.trim() === tn
            );
            if (btn) btn.click();
        }""",
        tab_name,
    )
    page.wait_for_timeout(160)


def solve_one_webkata(page: Page, seq: int, topic: str, state: Dict[str, Any]) -> bool:
    qid = page.url.split("?")[0].rstrip("/").split("/")[-1]
    if page.evaluate("() => document.body.innerText.includes('Solved!')"):
        state["webkata_solved"] += 1
        return True
    desc = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 1700)")
    tab_names: List[str] = page.evaluate(
        "() => Array.from(document.querySelectorAll('button.tab-text')).filter(b => b.offsetParent!==null).map(b => b.innerText.trim())"
    ) or ["HTML"]

    starters: Dict[str, str] = {}
    for tname in tab_names:
        click_visible_webkata_tab(page, tname)
        starters[tname] = page.evaluate("() => window.ace ? window.ace.edit('editor').getValue() : ''")

    err_note = ""
    for att in range(3):
        prompt = (
            f"WebKata Topic: {topic.upper()}\nProblem Description:\n{desc}\n\n"
            f"Available Editor Tabs: {tab_names}\nStarter Files:\n{json.dumps(starters, indent=2)}\n{err_note}\n\n"
            "Return ONLY a valid JSON object mapping each modified tab name (from Available Editor Tabs) to its COMPLETE file content string."
        )
        raw = call_llm(
            "Expert Front-End developer for GUVI WebKata (HTML5, CSS3, Vanilla JS, Bootstrap). "
            "Preserve starter IDs/classes/structure, satisfy every DOM & computed-style assertion, "
            "and output ONLY valid JSON mapping tab names to full code strings.",
            prompt,
            seq + att * 4,
            max_tokens=2600,
        )
        cleaned = strip_fences(raw).strip()
        files_out: Dict[str, str] = {}
        try:
            files_out = json.loads(cleaned)
        except Exception:
            m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if m:
                try:
                    files_out = json.loads(m.group(0))
                except Exception:
                    pass
            if not files_out and len(tab_names) == 1 and cleaned:
                files_out = {tab_names[0]: cleaned}

        if not files_out:
            continue

        for tname, content in files_out.items():
            if tname in tab_names and isinstance(content, str) and content.strip():
                click_visible_webkata_tab(page, tname)
                page.evaluate("(c) => window.ace.edit('editor').setValue(c, -1)", content)

        page.evaluate("() => document.querySelector('button.submit-code')?.click()")
        page.wait_for_timeout(2000)
        verdict = page.evaluate(
            """() => {
                const modals = Array.from(document.querySelectorAll('dialog, .modal, [role="dialog"]')).filter(m => m.open || m.offsetParent !== null).map(m => m.innerText.trim());
                const joined = modals.join('\\n');
                const ok = joined.includes('Congratulations') || joined.includes('Geekoins') || document.body.innerText.includes('Solved!') || (joined.includes('Passed') && !joined.includes('Failed'));
                return { ok, modalText: joined.slice(0, 420) };
            }"""
        )
        page.evaluate(
            """() => {
                for (const m of document.querySelectorAll('dialog, .modal, [role="dialog"]')) {
                    if (m.open || m.offsetParent !== null) {
                        const cb = Array.from(m.querySelectorAll('button')).find(b => /close|✕/i.test(b.innerText));
                        if (cb) cb.click();
                    }
                }
            }"""
        )
        if verdict["ok"]:
            state["webkata_solved"] += 1
            (SOL_WEB_DIR / f"{topic}_{qid}.json").write_text(json.dumps(files_out, indent=2), encoding="utf-8")
            save_multi_checkpoint(state)
            return True
        err_note = f"\nPrevious test results:\n{verdict['modalText']}\nCheck exact HTML semantic tags (<mark>, <b>/<strong>, <input> attributes), exact CSS properties/units, and JS DOM event handlers!"

    save_multi_checkpoint(state)
    return False


def run_webkata_fast(ctx: BrowserContext, page: Page, state: Dict[str, Any]) -> None:
    """Harvests all unsolved WebKata numeric IDs across html/css/js/bootstrap in seconds, then solves directly without table reloads."""
    for topic in ("html", "css", "js", "bootstrap"):
        todo_urls: List[Tuple[str, str]] = []
        for pno in range(1, 5):
            enforce_single_tab(ctx, page)
            list_url = f"https://www.guvi.in/webkata/{topic}/?page={pno}&limit=50"
            page.goto(list_url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1200)
            dismiss_popups(page)
            rows = page.evaluate(
                """() => Array.from(document.querySelectorAll('tbody tr')).map(r => ({
                    done: r.innerHTML.includes('completed-icon_svg__a') || r.innerHTML.includes('#0DBA4B'),
                    txt: (r.innerText || '').trim().replace(/\\s+/g, ' ')
                }))"""
            )
            if not rows:
                break
            for r in rows:
                if not r["done"]:
                    m = re.match(r"^(\d+)\.", r["txt"])
                    if m:
                        u = f"https://www.guvi.in/webkata/{topic}/{m.group(1)}/"
                        if all(u != x[0] for x in todo_urls):
                            todo_urls.append((u, r["txt"][:55]))
            if len(rows) < 50:
                break

        log(f"[WebKata-{topic.upper()}] {len(todo_urls)} unsolved problems queued.")
        for idx, (u, title_s) in enumerate(todo_urls, start=1):
            enforce_single_tab(ctx, page)
            page.goto(u, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1400)
            dismiss_popups(page)
            try:
                ok = solve_one_webkata(page, idx, topic, state)
            except Exception as exc:
                log(f"[WebKata-{topic.upper()} #{idx}] Error: {str(exc)[:110]}")
                ok = False
            log(f"[WebKata-{topic.upper()} {idx}/{len(todo_urls)}] {title_s} -> {'SOLVED' if ok else 'FAILED'} | total={state['webkata_solved']}")


def main() -> int:
    state = json.loads(MULTI_REPORT.read_text(encoding="utf-8")) if MULTI_REPORT.exists() else {
        "fixthecode_solved": 0,
        "sqlkata_solved": 0,
        "webkata_solved": 0,
    }
    stages = sys.argv[1:] or ["fixthecode", "sqlkata", "webkata"]
    with sync_playwright() as pw:
        ctx, page = open_single_brave_tab(pw, disable_images=False)
        try:
            if "fixthecode" in stages:
                sweep_table_inplace(ctx, page, "https://www.guvi.in/debugging/", "FixTheCode", lambda p, s: solve_one_fixthecode(p, s, state))
            if "webkata" in stages:
                run_webkata_fast(ctx, page, state)
            if "sqlkata" in stages:
                sweep_table_inplace(ctx, page, "https://www.guvi.in/sqlkata/", "SQLKata", lambda p, s: solve_one_sqlkata(p, s, state))
        finally:
            save_multi_checkpoint(state)
            ctx.close()
    log(f"=== MULTI-PLATFORM COMPLETE: {json.dumps(state)} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
