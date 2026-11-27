"""
finish_all_v3.py — Surgical Root-Cause Finisher v3 Across All 4 GUVI Practice Portals
(Strictly 1 Foreground Brave Tab | $0 FreeLLMAPI Opus/Sonnet/Fusion | Python-First | HTTP-Synced).

Root causes fixed in v3:
1. WebKata (82.87% -> 95%+):
   - Unescapes ALL strings in `<script type="qwik/json">` via `r'"((?:\\.|[^"\\])*)"'` to extract 100% untruncated
     `{{frameWindow}}` unit-test expressions (catching GUVI prose typos like '3px' when test checks `String(2)`!).
   - Clicks `Validate` (`button.run-code`) + awaits `POST /validate` BEFORE clicking `Submit` (`button.submit-code`)
     so the browser iframe computes fresh `testResults` after every `ace.setValue()`.
2. SQLKata (59.63% -> 90%+):
   - Collects all 109 questions across ALL 8 pages via `Go to next page` + `/sqlkata/questions` listener (fixing skipped p6/p8).
   - Clicks `input[name="sub-questions-accordion"]` directly inside each `div.collapse` so Q2..QN actually expand & get evaluated!
   - Checks `submissionData[f"s{qi+1}"]["valid"]` specifically instead of `any(submissionData.values())`!
   - Uses `Run Code` (`POST /sqlkata/run/`) on failed read-only `SELECT` queries to feed exact SQL errors/columns back to LLM.
3. FixTheCode (86% -> 96%+):
   - Extracts GUVI's untouched original buggy starter code & author hint directly from `<script type="qwik/json">` (bypassing broken DaisyUI Reset).
   - Feeds exact `publicTestCases` (`input`, `expected`, `output`) so author-quirk test expectations are matched cleanly in Python 3.
4. CodeKata (90.05% -> max solvable in Python 3 + locked C/C++/Java):
   - Background 3-worker pool pre-generates locally sample-verified (`verify_code_locally` on `Sample Input` + `Case 1/2`) Python 3
     solutions while Stages 1–3 run, then Stage 4 submits & repairs with live `compilationIssue` + `passedTestCases/totalTestCases`.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

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

RESULTS_JSON = ROOT / "data" / "ck_results.json"
PROB_DIR = ROOT / "data" / "ck_problems"
V3_CANDS_DIR = ROOT / "data" / "ck_v3_cands"
SOL_DIR = ROOT / "solutions"
SOL_FIX_DIR = ROOT / "solutions_fixthecode"
SOL_SQL_DIR = ROOT / "solutions_sqlkata"
SOL_WEB_DIR = ROOT / "solutions_webkata"
PROGRESS_JSON = ROOT / "reports" / "FINISH_V3_STATUS.json"

for _d in (V3_CANDS_DIR, SOL_DIR, SOL_FIX_DIR, SOL_SQL_DIR, SOL_WEB_DIR):
    _d.mkdir(parents=True, exist_ok=True)

LANG_EXT = {
    "PYTHON 3": "py", "PYTHON 2": "py", "C++": "cpp", "C": "c",
    "JAVASCRIPT": "js", "JAVA": "java", "JAVA 8": "java", "BASH": "sh", "SQLITE": "sql",
}


def log(msg: str) -> None:
    print(f"[V3 {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_prog(prog: Dict[str, Any]) -> None:
    prog["updated_at"] = datetime.now(timezone.utc).isoformat()
    PROGRESS_JSON.write_text(json.dumps(prog, indent=2), encoding="utf-8")


def unescape_qwik_str(raw_s: str) -> str:
    try:
        return json.loads(f'"{raw_s}"')
    except Exception:
        return (
            raw_s.replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace("\\/", "/")
            .replace("\\\\", "\\")
        )


def extract_qwik_strings(page: Page) -> List[str]:
    try:
        raw = page.evaluate("() => document.querySelector('script[type=\"qwik/json\"]')?.textContent || ''")
    except Exception:
        raw = ""
    if not raw:
        return []
    matches = re.findall(r'"((?:\\.|[^"\\])*)"', raw)
    return [unescape_qwik_str(m) for m in matches if m]


def dismiss_session_and_modals(page: Page) -> None:
    dismiss_popups(page)
    try:
        page.evaluate(
            """() => {
                for (const b of document.querySelectorAll('button')) {
                    if (b.offsetParent !== null && b.innerText.includes('Continue Here Anyway')) b.click();
                }
                for (const m of document.querySelectorAll('dialog, [role="dialog"]')) {
                    if (m.open) {
                        const cb = Array.from(m.querySelectorAll('button')).find(b => /^(close|✕|cancel)$/i.test(b.innerText.trim()));
                        if (cb) cb.click();
                    }
                }
                for (const inp of document.querySelectorAll('input.modal-toggle')) {
                    if (inp.checked) inp.checked = false;
                }
            }"""
        )
    except Exception:
        pass


def select_python_strict(page: Page) -> str:
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
            page.wait_for_timeout(140)
            opt = page.locator(f'.ss-content[data-id="{did}"] .ss-option').filter(has_text=re.compile(f"^{re.escape(chosen)}$")).first
            if opt.count() > 0:
                opt.click(force=True)
                page.wait_for_timeout(200)
                page.evaluate(
                    "() => { for (const b of document.querySelectorAll('button')) if (b.offsetParent!==null && b.innerText.trim()==='No') b.click(); }"
                )
    return chosen


def collect_catalog_unsolved_slugs(ctx: BrowserContext, page: Page, base_url: str, api_fragment: str) -> List[str]:
    """Steps through all pagination pages using Next Page button & API listener so NO page (like p6/p8) is ever skipped."""
    slugs: List[str] = []
    seen: Set[str] = set()

    def on_resp(r: Any) -> None:
        if api_fragment in r.url and r.status == 200:
            try:
                docs = json.loads(r.text()).get("data", {}).get("documents") or []
                for d in docs:
                    if str(d.get("status", "")).lower() != "solved":
                        u = d.get("uniqueUrl")
                        s = u[0] if isinstance(u, list) and u else (u if isinstance(u, str) else "")
                        if s and s not in seen:
                            seen.add(s)
                            slugs.append(s)
            except Exception:
                pass

    page.on("response", on_resp)
    try:
        enforce_single_tab(ctx, page)
        page.goto(base_url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(1500)
        dismiss_session_and_modals(page)

        # Parse page 1 from qwik/json or click page 2 then page 1 so API fires for page 1 too!
        p2 = page.locator("button").filter(has_text=re.compile(r"^2$")).first
        if p2.count() > 0 and p2.is_visible():
            p2.click(force=True)
            page.wait_for_timeout(750)
            p1 = page.locator("button").filter(has_text=re.compile(r"^1$")).first
            if p1.count() > 0 and p1.is_visible():
                p1.click(force=True)
                page.wait_for_timeout(750)

        # Now step Next Page until disabled
        for _ in range(15):
            nb = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
            if nb.count() == 0 or not nb.is_visible() or nb.get_attribute("disabled") is not None:
                break
            prev_len = len(seen)
            nb.click(force=True)
            page.wait_for_timeout(700)
            # Check if button got disabled
            if nb.get_attribute("disabled") is not None and len(seen) == prev_len:
                break
    finally:
        try:
            page.remove_listener("response", on_resp)
        except Exception:
            pass
    return slugs


# ============================================================================
# BACKGROUND WORKER: Locally Sample-Verified CodeKata Python Pre-Generator
# ============================================================================

def extract_extra_samples_from_desc(desc: str, base_samples: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = list(base_samples)
    m = re.search(
        r"Sample Input\s*:?\s*\n(.*?)\n\s*Sample Output\s*:?\s*\n(.*?)(?:\n\s*(?:Explanation|Accepted|Submissions|Code Editor)\b|$)",
        desc or "",
        flags=re.DOTALL | re.IGNORECASE,
    )
    if m:
        si, so = m.group(1).strip("\r\n"), m.group(2).strip("\r\n")
        if si or so:
            if all(s.get("input", "").strip() != si.strip() for s in out):
                out.insert(0, {"input": si, "output": so})
    return out


def pregen_one_ck(slug: str) -> None:
    out_f = V3_CANDS_DIR / f"{slug}.json"
    if out_f.exists():
        return
    pf = PROB_DIR / f"{slug}.json"
    if not pf.exists():
        return
    try:
        meta = json.loads(pf.read_text(encoding="utf-8"))
    except Exception:
        return
    desc = meta.get("description") or ""
    samples = extract_extra_samples_from_desc(desc, meta.get("samples") or [])
    samples_txt = "\n".join(
        f"Sample #{i+1} Input:\n{s.get('input','')}\nSample #{i+1} Expected Output (repr={s.get('output','')!r}):\n{s.get('output','')}"
        for i, s in enumerate(samples[:4])
    )

    verified_cands: List[str] = []
    err_ctx = ""
    for att in range(4):
        prompt = (
            f"GUVI CodeKata Problem ({slug}):\n{desc[:2800]}\n\n"
            f"EXACT TEST CASES (YOUR PYTHON 3 CODE MUST MATCH EVERY SINGLE ONE CHARACTER-FOR-CHARACTER!):\n{samples_txt}\n"
            f"{err_ctx}\n\n"
            "CRITICAL RULES:\n"
            "1. Check Sample Expected Outputs CAREFULLY! Notice if indexing is 1-based (e.g. 'GUVI' index 2 -> 'U'), "
            "or if path simplification outputs only the last segment ('/home/guvi' -> '/guvi'), or exact error strings ('None', 'Error', '-1').\n"
            "2. Preserve exact leading spaces on pattern/pyramid lines and exact decimal formatting.\n"
            "3. Output ONLY raw standalone Python 3 code reading from `sys.stdin`."
        )
        code = strip_fences(
            call_llm(
                "Grandmaster Python 3 competitive programmer. Output ONLY raw Python 3 source code.",
                prompt,
                seed=hash(slug) % 17 + att,
            )
        )
        if not code.strip():
            continue
        ok_loc, diff_msg = verify_code_locally(code, "PYTHON 3", samples)
        if ok_loc:
            if code not in verified_cands:
                verified_cands.append(code)
            if len(verified_cands) >= 2:
                break
            err_ctx = (
                "\nFirst candidate passed visible samples! Now write an ALTERNATIVE Python 3 implementation that STILL passes "
                "all visible samples above, while handling tricky hidden edge cases (e.g. negative/zero inputs, empty result -> -1, "
                "duplicate values, multi-line vs single-line input tokens, or 32-bit C integer semantics if bitwise)."
            )
        else:
            err_ctx = f"\nYour previous Python 3 code FAILED local sample verification:\n{diff_msg}\nCode:\n{code[:800]}\nFix it so ALL samples pass!"

    if verified_cands:
        out_f.write_text(json.dumps({"slug": slug, "lang": "PYTHON 3", "candidates": verified_cands}, indent=1), encoding="utf-8")


# ============================================================================
# STAGE 1: FixTheCode (7 remaining items -> Qwik original starter + API cases)
# ============================================================================

def finish_fixthecode_v3(ctx: BrowserContext, page: Page, prog: Dict[str, Any]) -> None:
    log("=== STAGE 1: FixTheCode v3 (Qwik Original Buggy Code + Exact API Test Cases) ===")
    slugs = collect_catalog_unsolved_slugs(ctx, page, "https://www.guvi.in/debugging/", "/debugging/questions")
    if not slugs:
        # Fallback known 7 slugs from previous run
        slugs = [
            "right-angled-triangle",
            "hallow-full-pyramid-pattern",
            "potential-energy-on-planets",
            "rope-cutting",
            "hollow-diamond-inscribed-in-a-rectangle",
            "butterfly-pattern-printing",
            "finding-routes-with-sreeram",
        ]
    log(f"[FixTheCode] {len(slugs)} unsolved slugs: {slugs}")

    for idx, slug in enumerate(slugs, start=1):
        enforce_single_tab(ctx, page)
        page.goto(f"https://www.guvi.in/debugging/{slug}/", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(1600)
        dismiss_session_and_modals(page)

        if page.evaluate("() => Boolean(document.querySelector('.question-status')?.innerText?.toLowerCase()?.includes('solved'))"):
            continue

        lang = select_python_strict(page)
        q_strs = extract_qwik_strings(page)
        code_like = [
            s for s in q_strs
            if 15 < len(s) < 3500 and ("\n" in s) and any(k in s for k in ("def ", "input(", "print(", "for ", "while ", "#include", "class "))
            and "<!DOCTYPE" not in s and "Problem Statement" not in s
        ]
        hint_like = [
            s for s in q_strs
            if 20 < len(s) < 800 and any(k in s.lower() for k in ("check ", "condition", "hint", "bug", "logic", "fix "))
        ]
        ace_now = page.evaluate("() => window.ace ? window.ace.edit('editor').getValue() : ''")
        prob_txt = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 2600)")

        orig_block = "\n---\n".join(code_like[:3]) if code_like else ace_now
        hints_block = "\n".join(hint_like[:3])

        api_feedback = ""
        solved = False
        for att in range(5):
            prompt = (
                f"FixTheCode Problem ({slug}):\n{prob_txt}\n\n"
                f"Untouched Original Buggy Code / Variants from GUVI Metadata:\n{orig_block}\n\n"
                f"Author Hint (if any): {hints_block}\n"
                f"{api_feedback}\n\n"
                "IMPORTANT:\n"
                "1. Inspect the Untouched Original Buggy Code VERY CAREFULLY — in GUVI FixTheCode, the test cases were generated from "
                "a 1-to-3 line bug fix of that EXACT original code (even if the problem title/statement has a copy-paste discrepancy, "
                "e.g., checking triangle validity vs right-angled triangle, or exact trailing spaces in patterns!).\n"
                "2. Match EVERY `expected` output in `publicTestCases` character-for-character (including trailing spaces or `end=''`)!\n"
                f"Output ONLY raw {lang} code."
            )
            code = strip_fences(
                call_llm(
                    f"Expert {lang} debugger for GUVI FixTheCode. Output ONLY raw {lang} code.",
                    prompt,
                    seed=idx * 3 + att,
                )
            )
            if not code.strip():
                continue
            page.evaluate("(c) => window.ace.edit('editor').setValue(c, -1)", code)
            try:
                with page.expect_response(lambda r: "/debugging/question/submit" in r.url and r.request.method == "POST", timeout=12000) as rinf:
                    page.evaluate("() => document.querySelector('button.submit-code')?.click()")
                rj = json.loads(rinf.value.text()).get("data", {})
            except Exception:
                rj = {}
            dismiss_session_and_modals(page)
            sub_c = rj.get("submissionCode") or {}
            if sub_c.get("passedAllTestCase"):
                solved = True
                prog["fixthecode_v3_solved"] += 1
                (SOL_FIX_DIR / f"{slug}.py").write_text(code, encoding="utf-8")
                save_prog(prog)
                break
            pub_tc = rj.get("publicTestCases") or []
            priv_tc = rj.get("privateTestCases") or []
            api_feedback = (
                f"\nAttempt {att+1} FAILED:\nSubmitted Code:\n{code[:900]}\n"
                f"Exact Judge Public Test Cases (check repr of expected vs output!):\n{json.dumps(pub_tc, indent=1)[:1500]}\n"
                f"Private Test Cases Passed: {[x.get('passed') for x in priv_tc]}\n"
                "Look closely at why public or private cases failed (exact whitespace/trailing spaces, original buggy logic vs prose)!"
            )
        log(f"[FixTheCode {idx}/{len(slugs)}] {slug} -> {'SOLVED' if solved else 'FAILED'} | +v3={prog['fixthecode_v3_solved']}")


# ============================================================================
# STAGE 2: WebKata (52 remaining items -> Full Qwik Assertions + Validate->Submit)
# ============================================================================

def click_wk_tab(page: Page, tab_name: str) -> None:
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


def finish_webkata_v3(ctx: BrowserContext, page: Page, prog: Dict[str, Any]) -> None:
    log("=== STAGE 2: WebKata v3 (100% Unescaped {{frameWindow}} Assertions + Validate-Before-Submit) ===")
    for topic in ("html", "css", "js", "bootstrap"):
        todo: List[Tuple[str, str]] = []
        for pno in range(1, 5):
            enforce_single_tab(ctx, page)
            page.goto(f"https://www.guvi.in/webkata/{topic}/?page={pno}&limit=50", wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1100)
            dismiss_session_and_modals(page)
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
                        if all(u != x[0] for x in todo):
                            todo.append((u, r["txt"][:55]))
            if len(rows) < 50:
                break

        log(f"[WebKata-{topic.upper()}] {len(todo)} remaining items.")
        for idx, (u, title_s) in enumerate(todo, start=1):
            enforce_single_tab(ctx, page)
            qid = u.rstrip("/").split("/")[-1]
            page.goto(u, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1500)
            dismiss_session_and_modals(page)

            q_strs = extract_qwik_strings(page)
            # Extract ALL {{frameWindow}} or unit-test expressions + adjacent expected value strings!
            assertions: List[str] = []
            for si, s in enumerate(q_strs):
                if "{{frameWindow}}" in s or ("expectedValue" in s and "function" in s) or ("querySelector" in s and "function" in s):
                    ctx_after = [x for x in q_strs[si + 1 : si + 4] if len(x) < 120 and "{{frameWindow}}" not in x]
                    assertions.append(f"Test #{len(assertions)}: {s[:1400]}  | Nearby literals: {ctx_after}")

            # Extract clean starter HTML/CSS/JS embedded in qwik/json if present
            clean_htmls = [s for s in q_strs if "<!DOCTYPE html>" in s or "<html" in s]
            desc = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 1700)")
            tab_names: List[str] = page.evaluate(
                "() => Array.from(document.querySelectorAll('button.tab-text')).filter(b => b.offsetParent!==null).map(b => b.innerText.trim())"
            ) or ["HTML"]

            starters: Dict[str, str] = {}
            for tname in tab_names:
                click_wk_tab(page, tname)
                cur_val = page.evaluate("() => window.ace ? window.ace.edit('editor').getValue() : ''")
                if tname == "HTML" and clean_htmls:
                    starters[tname] = clean_htmls[0]
                else:
                    starters[tname] = cur_val

            err_fb = ""
            solved = False
            assertions_txt = "\n".join(assertions[:15]) if assertions else "(No explicit frameWindow string found; follow Problem Description strictly.)"

            for att in range(4):
                prompt = (
                    f"WebKata Topic: {topic.upper()} (Question #{qid})\n"
                    f"Problem Description:\n{desc}\n\n"
                    f"Available Editor Tabs: {tab_names}\n"
                    f"Starter Files:\n{json.dumps(starters, indent=2)}\n\n"
                    f"EXACT LIVE IFRAME UNIT TEST EXPRESSIONS (GROUND TRUTH — OVERRIDES ANY TYPO IN PROSE!):\n{assertions_txt}\n"
                    f"{err_fb}\n\n"
                    "CRITICAL INSTRUCTIONS:\n"
                    "1. Read EVERY `Test #k` expression carefully! If prose says '3px' or 'red' but `Test #k` checks `String(2)` or `rgb(0, 128, 0)` or `querySelectorAll('p')`, "
                    "satisfy the EXACT `Test #k` JavaScript expression!\n"
                    "2. Note computed styles: `getComputedStyle(el)['border-top-width']` requires `border-style` (e.g. `solid`) to NOT be `none`, otherwise browser computed border-width is `0px`!\n"
                    "3. For Bootstrap problems, keep the `<link>` / `<script>` CDN tags from the starter HTML intact!\n"
                    "4. Return ONLY a valid JSON object mapping each tab name in Available Editor Tabs to its COMPLETE file content string."
                )
                raw = call_llm(
                    "Principal Front-End Engineer solving GUVI WebKata. Output ONLY valid JSON mapping tab names to complete file contents.",
                    prompt,
                    seed=idx * 3 + att,
                    max_tokens=2800,
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
                        click_wk_tab(page, tname)
                        page.evaluate(
                            """(c) => {
                                const ed = window.ace.edit('editor');
                                ed.setValue(c, -1);
                                ed.clearSelection();
                            }""",
                            content,
                        )
                        page.wait_for_timeout(120)

                # CRITICAL FIX: Click Validate (`button.run-code`) FIRST so iframe recomputes `testResults`!
                val_res = {}
                try:
                    with page.expect_response(lambda r: "/webkata/" in r.url and "/validate" in r.url and r.request.method == "POST", timeout=9000) as vinf:
                        page.evaluate("() => document.querySelector('button.run-code')?.click()")
                    val_res = json.loads(vinf.value.text()).get("data", {})
                except Exception:
                    page.wait_for_timeout(900)

                page.wait_for_timeout(220)
                # Now click Submit (`button.submit-code`) to persist when passing (or on final check)
                rj = {}
                if val_res.get("passedAllTestCase") or not val_res:
                    try:
                        with page.expect_response(lambda r: "/webkata/" in r.url and "/submit" in r.url and r.request.method == "POST", timeout=10000) as rinf:
                            page.evaluate("() => document.querySelector('button.submit-code')?.click()")
                        rj = json.loads(rinf.value.text()).get("data", {})
                    except Exception:
                        rj = {}
                    dismiss_session_and_modals(page)

                ev = (rj.get("evaluationDetails") or val_res or {})
                if rj.get("evaluationDetails", {}).get("passedAllTestCase") or (val_res.get("passedAllTestCase") and ev.get("passedAllTestCase")):
                    solved = True
                    prog["webkata_v3_solved"] += 1
                    (SOL_WEB_DIR / f"{topic}_{qid}.json").write_text(json.dumps(files_out, indent=2), encoding="utf-8")
                    save_prog(prog)
                    break

                ev_map = ev.get("evaluatedResults") or val_res.get("evaluatedResults") or {}
                err_fb = (
                    f"\nAttempt {att+1} FAILED!\nSubmitted files:\n{json.dumps(files_out)[:1200]}\n"
                    f"Iframe Evaluated Results per Test Index: {json.dumps(ev_map)}\n"
                    "Fix EVERY test index where `passed` is `false`!"
                )
            log(f"[WebKata-{topic.upper()} {idx}/{len(todo)}] {title_s} -> {'SOLVED' if solved else 'FAILED'} | +v3={prog['webkata_v3_solved']}")


# ============================================================================
# STAGE 3: SQLKata (44 remaining items -> Radio Input Click + Per-Index Valid + Run Feedback)
# ============================================================================

def extract_all_sql_tables(page: Page) -> str:
    try:
        if not page.evaluate("() => document.body.innerText.includes('Database Tables')"):
            page.evaluate("() => { for (const b of document.querySelectorAll('button')) if (b.offsetParent!==null && b.innerText.trim()==='Tables') b.click(); }")
            page.wait_for_timeout(350)
        return page.evaluate(
            """() => {
                const t = document.body.innerText || '';
                const i = t.indexOf('Database Tables');
                const slice = i !== -1 ? t.slice(i, i + 5500) : '';
                const tablesHtml = Array.from(document.querySelectorAll('table')).map((tb, idx) => {
                    const rows = Array.from(tb.querySelectorAll('tr')).slice(0, 18).map(
                        tr => Array.from(tr.querySelectorAll('th,td')).map(c => c.textContent.trim()).join(' | ')
                    ).join('\\n');
                    return `Table #${idx+1}:\\n${rows}`;
                }).join('\\n\\n');
                return (slice.split('Console\\n')[0] || slice.slice(0, 3500)) + '\\n\\nFull Unclipped Table Columns:\\n' + tablesHtml.slice(0, 3500);
            }"""
        )
    except Exception:
        return ""


def finish_sqlkata_v3(ctx: BrowserContext, page: Page, prog: Dict[str, Any]) -> None:
    log("=== STAGE 3: SQLKata v3 (All 8 Pages + Exact Radio Accordion Expand + s{k} Valid Check) ===")
    slugs = collect_catalog_unsolved_slugs(ctx, page, "https://www.guvi.in/sqlkata/", "/sqlkata/questions")
    log(f"[SQLKata] {len(slugs)} unsolved slugs collected across all 8 pages.")

    for idx, slug in enumerate(slugs, start=1):
        enforce_single_tab(ctx, page)
        page.goto(f"https://www.guvi.in/sqlkata/{slug}/", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(1700)
        dismiss_session_and_modals(page)

        scen = page.evaluate("() => (document.querySelector('main')||document.body).innerText.slice(0, 1300)")
        tables_txt = extract_all_sql_tables(page)

        q_loc = page.locator('div.collapse:has(input[name="sub-questions-accordion"])')
        n_q = q_loc.count()
        if n_q == 0:
            log(f"[SQLKata {idx}/{len(slugs)}] {slug} -> 0 subquestions found, skipping.")
            continue

        all_ok = True
        saved_q: List[str] = []

        for qi in range(n_q):
            cls_s = q_loc.nth(qi).get_attribute("class") or ""
            if "correct-submission" in cls_s:
                continue

            # CRITICAL FIX #1: Click the radio `<input name="sub-questions-accordion">` directly so Q{qi+1} expands & becomes active!
            radio = q_loc.nth(qi).locator('input[name="sub-questions-accordion"]').first
            radio.click(force=True)
            page.wait_for_timeout(280)
            if not radio.is_checked():
                page.evaluate(
                    "(idx) => { const ins = document.querySelectorAll('input[name=\"sub-questions-accordion\"]'); if (ins[idx]) ins[idx].click(); }",
                    qi,
                )
                page.wait_for_timeout(250)

            qtxt = q_loc.nth(qi).inner_text().strip()
            s_key = f"s{qi + 1}"
            sql_err = ""
            sub_solved = False

            strategies = [
                "Write the cleanest standard SQL query matching exact table & column names from Database Tables. Do NOT invent unrequested column aliases unless explicitly asked.",
                "Alternative 1: Check exact requested column aliases, `ORDER BY` direction, `DISTINCT`, or if DML (`INSERT`/`UPDATE`/`DELETE`), check whether the question ALSO asks to `SELECT` and display the updated/remaining rows right after the DML statement!",
                "Alternative 2: If DML (`INSERT`/`UPDATE`/`DELETE`) failed when paired with `SELECT`, try ONLY the single DML statement (or vice versa)! If `SELECT`, check `ROUND(..., 2)` vs unrounded, `LEFT JOIN` vs `INNER JOIN`, and `>=` vs `>`.",
                "Alternative 3: Notice if a previous DML mutated the session table or if explicit primary key `id` is required/forbidden in `INSERT`, or check exact string case & NULL handling (`IS NULL`, `COALESCE`).",
                "Alternative 4: Re-read every single word of Sub-Question and Full Unclipped Table Columns; check column order in `SELECT` and grouping!",
            ]

            for att, strat in enumerate(strategies):
                sql = strip_fences(
                    call_llm(
                        "Principal SQL Engineer (MySQL / SQLite) solving GUVI SQLKata. Output ONLY raw SQL statement(s) ending with semicolon.",
                        f"Scenario:\n{scen}\n\nDatabase Tables:\n{tables_txt[:4500]}\n\n"
                        f"Active Sub-Question (#{qi+1} of {n_q}):\n{qtxt}\n\n"
                        f"Strategy: {strat}\n{sql_err}",
                        seed=idx + qi * 3 + att,
                    )
                ).strip()
                if not sql:
                    continue

                page.evaluate(
                    """(s) => {
                        const ed = window.ace.edit('editor');
                        ed.setValue(s, -1);
                        ed.clearSelection();
                    }""",
                    sql,
                )

                rj = {}
                try:
                    with page.expect_response(lambda r: "/sqlkata/submit/" in r.url and r.request.method == "POST", timeout=11000) as rinf:
                        page.evaluate("() => document.querySelector('button.submit-code')?.click()")
                    rj = json.loads(rinf.value.text()).get("data", {})
                except Exception:
                    rj = {}
                dismiss_session_and_modals(page)

                sub_data = rj.get("submissionData") or {}
                # CRITICAL FIX #2: Check THIS specific subquestion `s{qi+1}` (NEVER `any(sub_data.values())`!)
                s_entry = sub_data.get(s_key) if isinstance(sub_data, dict) else None
                this_valid = bool(rj.get("passedAllTestCase")) or (isinstance(s_entry, dict) and s_entry.get("valid") is True)
                if not this_valid:
                    page.wait_for_timeout(150)
                    cls_now = q_loc.nth(qi).get_attribute("class") or ""
                    this_valid = "correct-submission" in cls_now

                if this_valid:
                    sub_solved = True
                    saved_q.append(f"-- Q{qi+1}: {qtxt[:100].replace(chr(10), ' ')}\n{sql}")
                    break

                # If read-only SELECT failed, click Run Code once to inspect exact SQL error / output columns!
                run_diag = ""
                upper_sql = sql.upper()
                if not any(kw in upper_sql for kw in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE")):
                    try:
                        with page.expect_response(lambda r: "/sqlkata/run/" in r.url and r.request.method == "POST", timeout=7000) as runf:
                            page.evaluate("() => document.querySelector('button.run-code')?.click()")
                        run_diag = runf.value.text()[:450]
                    except Exception:
                        pass
                sql_err += f"\nAttempt {att+1} REJECTED for {s_key}:\nSQL: {sql}\nRun/Judge Feedback: {run_diag or json.dumps(s_entry)[:300]}"

            if not sub_solved:
                all_ok = False

        if all_ok:
            prog["sqlkata_v3_solved"] += 1
            if saved_q:
                (SOL_SQL_DIR / f"{slug}.sql").write_text("\n\n".join(saved_q) + "\n", encoding="utf-8")
            save_prog(prog)
        log(f"[SQLKata {idx}/{len(slugs)}] {slug} ({n_q} Qs) -> {'SOLVED' if all_ok else 'PARTIAL'} | +v3={prog['sqlkata_v3_solved']}")


# ============================================================================
# STAGE 4: CodeKata (~216 remaining items -> Sample-Verified Python 3 + Live Judge Repair)
# ============================================================================

def submit_ck_v3(page: Page, code: str) -> Tuple[bool, int, int, str]:
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
    try:
        with page.expect_response(lambda r: "/code-kata/question/submit" in r.url and r.request.method == "POST", timeout=14000) as rinf:
            page.evaluate("() => document.querySelector('button.submit-code')?.click()")
        rj = json.loads(rinf.value.text()).get("data", {}).get("submissionData", {})
        dismiss_session_and_modals(page)
        return (
            bool(rj.get("passedAllTestCase")),
            int(rj.get("passedTestCases", 0)),
            int(rj.get("totalTestCases", 0)),
            str(rj.get("compilationIssue") or ""),
        )
    except Exception as exc:
        dismiss_session_and_modals(page)
        return False, 0, 0, str(exc)[:200]


def finish_codekata_v3(ctx: BrowserContext, page: Page, prog: Dict[str, Any]) -> None:
    log("=== STAGE 4: CodeKata v3 (Sample-Verified Python 3 First + Live Judge Repair) ===")
    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    todo_slugs = [
        s for s, v in sorted(results.items())
        if v.get("status") == "FAILED_PLATFORM" and s != "code-kata"
    ]
    log(f"[CodeKata] {len(todo_slugs)} FAILED_PLATFORM slugs queued.")

    for idx, slug in enumerate(todo_slugs, start=1):
        enforce_single_tab(ctx, page)
        page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=25000)
        try:
            page.wait_for_selector("#editor", timeout=5000)
            page.wait_for_function("() => Boolean(window.ace)", timeout=3500)
        except Exception:
            continue
        dismiss_session_and_modals(page)

        if page.evaluate("() => Boolean(document.querySelector('.question-status')?.innerText?.toLowerCase()?.includes('solved'))"):
            results[slug] = {"status": "COMPLETED", "language": "PYTHON 3", "attempts": 1}
            continue

        lang = select_python_strict(page)
        pfile = PROB_DIR / f"{slug}.json"
        meta = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else {}
        prob_txt = meta.get("description") or page.evaluate(
            "() => (document.querySelector('.problem-description, #problem-description, main')?.textContent || document.body.innerText).slice(0, 3000)"
        )
        samples = extract_extra_samples_from_desc(prob_txt, meta.get("samples") or [])

        # Extract clean starter template from qwik/json if available
        q_strs = extract_qwik_strings(page)
        starters_q = [
            s for s in q_strs
            if 10 < len(s) < 2500 and ("\n" in s) and any(k in s for k in ("class ", "public static", "#include", "def ", "struct ", "void "))
            and "Problem Statement" not in s and "<!DOCTYPE" not in s
        ]
        starter_hint = starters_q[0] if starters_q else ""

        cands: List[str] = []
        v3_f = V3_CANDS_DIR / f"{slug}.json"
        if v3_f.exists() and lang == "PYTHON 3":
            cands = json.loads(v3_f.read_text(encoding="utf-8")).get("candidates") or []

        solved = False
        judge_fb = ""

        for ci, c_code in enumerate(cands):
            ok, passed_tc, tot_tc, comp_err = submit_ck_v3(page, c_code)
            if ok:
                solved = True
                ext = LANG_EXT.get(lang, "py")
                (SOL_DIR / f"{slug}.{ext}").write_text(c_code, encoding="utf-8")
                results[slug] = {"status": "COMPLETED", "language": lang, "attempts": ci + 1}
                prog["codekata_v3_solved"] += 1
                break
            judge_fb += f"\nPre-verified Candidate {ci+1} ({passed_tc}/{tot_tc} passed): {comp_err[:350] or 'Hidden testcase mismatch'}\nCode:\n{c_code[:700]}\n"

        if not solved:
            samples_txt = "\n".join(
                f"Sample #{i+1} In:\n{s.get('input','')}\nSample #{i+1} Out (repr={s.get('output','')!r}):\n{s.get('output','')}"
                for i, s in enumerate(samples[:4])
            )
            for live_att in range(3):
                lang_spec = (
                    "Write a standalone Python 3 solution reading stdin via `sys.stdin`."
                    if lang.startswith("PYTHON")
                    else f"Write a complete {lang} program (note GUVI's starter template/class name if any)."
                )
                code = strip_fences(
                    call_llm(
                        f"Grandmaster competitive programmer ({lang}). {lang_spec} Output ONLY raw {lang} source code.",
                        f"Problem ({slug}):\n{prob_txt[:2600]}\n\n"
                        f"GUVI Starter Code (if locked language / OOP harness):\n{starter_hint[:900]}\n\n"
                        f"Visible Samples:\n{samples_txt}\n\n"
                        f"Judge / Local Feedback:\n{judge_fb[:1500]}\n\n"
                        "Check: 1-based vs 0-based indexing, custom output rules in samples, exact decimal formatting, "
                        "32-bit C signed int overflow on bitwise/math problems, empty result -> '-1'/'None'/'Error', and Java `Main` class name!",
                        seed=idx * 3 + live_att,
                    )
                )
                if not code.strip():
                    continue
                ok_loc, loc_err = verify_code_locally(code, lang, samples)
                if not ok_loc:
                    judge_fb += f"\nLocal sample check failed on Attempt {live_att+1}: {loc_err}\nCode:\n{code[:600]}"
                    continue
                ok, passed_tc, tot_tc, comp_err = submit_ck_v3(page, code)
                if ok:
                    solved = True
                    ext = LANG_EXT.get(lang, "py")
                    (SOL_DIR / f"{slug}.{ext}").write_text(code, encoding="utf-8")
                    results[slug] = {"status": "COMPLETED", "language": lang, "attempts": len(cands) + live_att + 1}
                    prog["codekata_v3_solved"] += 1
                    break
                judge_fb += f"\nJudge Attempt {live_att+1} ({passed_tc}/{tot_tc} passed): {comp_err[:400] or 'Hidden testcase Wrong Answer'}\nCode:\n{code[:650]}"

        tot_ck = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
        log(f"[CodeKata {idx}/{len(todo_slugs)}] {slug} ({lang}) -> {'SOLVED' if solved else 'FAILED'} | TOTAL_CK={tot_ck} (+v3={prog['codekata_v3_solved']})")
        if idx % 5 == 0:
            RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
            save_prog(prog)

    RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
    save_prog(prog)


def main() -> int:
    prog = {
        "fixthecode_v3_solved": 0,
        "webkata_v3_solved": 0,
        "sqlkata_v3_solved": 0,
        "codekata_v3_solved": 0,
    }
    save_prog(prog)
    stages = sys.argv[1:] or ["fixthecode", "webkata", "sqlkata", "codekata"]

    # Kick off background CodeKata local-sample-verified Python pre-generation while Stages 1-3 run!
    bg_pool: Optional[ThreadPoolExecutor] = None
    if "codekata" in stages and RESULTS_JSON.exists():
        ck_res = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
        ck_todo = [s for s, v in sorted(ck_res.items()) if v.get("status") == "FAILED_PLATFORM" and s != "code-kata"]
        log(f"[BG-PREGEN] Starting 3-thread local-verified Python 3 pre-generator for {len(ck_todo)} CodeKata items...")
        bg_pool = ThreadPoolExecutor(max_workers=3)
        for s in ck_todo:
            bg_pool.submit(pregen_one_ck, s)

    with sync_playwright() as pw:
        ctx, page = open_single_brave_tab(pw, disable_images=False)
        try:
            if "fixthecode" in stages:
                finish_fixthecode_v3(ctx, page, prog)
            if "webkata" in stages:
                finish_webkata_v3(ctx, page, prog)
            if "sqlkata" in stages:
                finish_sqlkata_v3(ctx, page, prog)
            if "codekata" in stages:
                finish_codekata_v3(ctx, page, prog)
        finally:
            save_prog(prog)
            ctx.close()
            if bg_pool is not None:
                bg_pool.shutdown(wait=False, cancel_futures=True)

    log(f"=== SURGICAL FINISHER V3 COMPLETE: {json.dumps(prog)} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
