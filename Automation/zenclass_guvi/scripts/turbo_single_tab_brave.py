"""
turbo_single_tab_brave.py — Ultra-Fast SINGLE-TAB Foreground Brave CodeKata Autopilot (Target: 1,000+ Solved).

Design:
- STRICTLY ONE TAB in foreground Brave Browser (closes any extra tabs; zero multi-tab clutter).
- Blocks 3rd-party ad/tracker pixels & heavy images/fonts via Playwright route interception -> ~0.4s page loads.
- 20-thread background FreeLLMAPI + local compiler producer pool pre-solves & sample-tests problems AHEAD of the browser tab
  so the single Brave tab NEVER waits on LLM calls!
- Non-blocking self-debugging retries: if Guvi rejects a submission on hidden tests, the browser tab immediately moves to the
  next pre-solved problem while the background pool repairs the failed code using Guvi's exact error output and re-queues it!
- Starts immediately on the 1,316 pre-scraped problems on disk, then harvests & solves Easy catalog problems in the same tab.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Page, Route, async_playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
AUTO_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation")
sys.path.insert(0, str(ROOT))
import config  # noqa: E402
from core.state_manager import StateManager, TaskStatus  # noqa: E402

BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
PROFILE_DIR = ROOT / ".browser_profile"
PROB_DIR = ROOT / "data" / "ck_problems"
PRECOMP_DIR = ROOT / "data" / "ck_precomputed"
SOL_DIR = ROOT / "solutions"
RESULTS_JSON = ROOT / "data" / "ck_results.json"
LIVE_STATUS_JSON = ROOT / "reports" / "CODEKATA_LIVE_STATUS.json"
EASY_CATALOG_CACHE = ROOT / "data" / "ck_easy_catalog.json"
NODE_BIN = "/Users/devesh/.local/node/bin/node"

PROB_DIR.mkdir(parents=True, exist_ok=True)
PRECOMP_DIR.mkdir(parents=True, exist_ok=True)
SOL_DIR.mkdir(parents=True, exist_ok=True)
LIVE_STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)

FREELLM_BASE = os.environ.get("FREELLM_BASE", "http://127.0.0.1:31415")
KILO_URL = "https://api.kilo.ai/api/gateway/v1/chat/completions"
FREEAPI_DB = os.path.expanduser("~/Library/Application Support/FreeLLMAPI/freeapi.db")

LANG_PREFERENCE = ["PYTHON 3", "C++", "C", "JAVASCRIPT", "JAVA", "JAVA 8", "PYTHON 2", "BASH", "SQLITE"]
LANG_EXT = {
    "PYTHON 3": "py", "PYTHON 2": "py", "C++": "cpp", "C": "c",
    "CLANG C": "c", "JAVASCRIPT": "js", "JAVA": "java", "JAVA 8": "java",
    "SQLITE": "sql", "BASH": "sh",
}

BLOCKED_TRACKER_DOMAINS = (
    "googleadservices.com", "doubleclick.net", "google-analytics.com",
    "googletagmanager.com", "bat.bing.com", "clarity.ms", "linkedin.com",
    "mxradon.com", "facebook.net", "facebook.com", "snapchat.com",
    "taboola.com", "tapad.com", "hotjar.com",
)

MODEL_ROTATION = [
    "auto",
    "qwen3.8-27b",
    "gpt-oss-120b",
    "glm-5.3-flash",
    "gemma-4-26b-a4b-it",
    "minimax-m3.1-flash",
    "glm-4.7-flash",
    "gpt-oss-20b",
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def get_freellm_key() -> Optional[str]:
    if os.environ.get("FREELLM_KEY"):
        return os.environ["FREELLM_KEY"]
    if not os.path.exists(FREEAPI_DB):
        return None
    con = sqlite3.connect(f"file:{FREEAPI_DB}?mode=ro", uri=True)
    row = con.execute("SELECT value FROM settings WHERE key='unified_api_key'").fetchone()
    con.close()
    return row[0] if row else None


FREELLM_KEY = get_freellm_key()


def guess_initial_language(meta: Dict[str, Any]) -> str:
    txt = f"{meta.get('slug', '')} {meta.get('title', '')}".lower()
    if any(k in txt for k in ("stringbuffer", "stringbuilder", "method-overriding", "constructor-chaining", "final-variables", "interface-in-java", "java-program")):
        return "JAVA"
    if any(k in txt for k in ("using-namespaces", "operator-overloading", "friend-function", "stl-", "cpp-program")):
        return "C++"
    if any(k in txt for k in ("using-realloc", "using-malloc", "using-calloc", "pointer-arithmetic", "c-program")):
        return "C"
    return "PYTHON 3"


def strip_code_fences(raw: str) -> str:
    txt = (raw or "").strip()
    txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.DOTALL).strip()
    m = re.search(r"```(?:[a-zA-Z0-9_+]+)?\s*\n(.*?)```", txt, flags=re.DOTALL)
    if m:
        return m.group(1).strip() + "\n"
    txt = re.sub(r"^```[a-zA-Z0-9_+]*\s*", "", txt)
    txt = re.sub(r"\s*```$", "", txt)
    return txt.strip() + "\n"


def norm_out(s: str) -> str:
    return "\n".join(line.rstrip() for line in str(s).strip().splitlines())


def call_free_llm_sync(system_prompt: str, user_prompt: str, seed: int = 0) -> str:
    n = len(MODEL_ROTATION)
    ordered = [MODEL_ROTATION[(seed + i) % n] for i in range(4)]
    if FREELLM_KEY:
        for model_name in ordered:
            try:
                body = {
                    "model": model_name,
                    "max_tokens": 1600,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                }
                req = urllib.request.Request(
                    f"{FREELLM_BASE}/v1/messages",
                    data=json.dumps(body).encode("utf-8"),
                    headers={
                        "x-api-key": FREELLM_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=14) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
                if txt and len(txt) > 8 and not txt.startswith("Safety:"):
                    return txt
            except Exception:
                continue

    for km in ("openrouter/free",):
        try:
            body = {
                "model": km,
                "max_tokens": 1600,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            req = urllib.request.Request(
                KILO_URL,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "FreeLLMAPI"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            msg = (data.get("choices") or [{}])[0].get("message") or {}
            txt = (msg.get("content") or "").strip()
            if txt and len(txt) > 8:
                return txt
        except Exception:
            continue

    return ""


def verify_locally_sync(code: str, lang: str, samples: List[Dict[str, str]]) -> Tuple[bool, str]:
    valid_samples = [s for s in samples if s.get("input") or s.get("output")]
    if lang == "PYTHON 3":
        try:
            compile(code, "<sol>", "exec")
        except SyntaxError as exc:
            return False, f"SyntaxError: {exc}"

    if not valid_samples or lang in ("JAVA", "JAVA 8"):
        return True, ""

    with tempfile.TemporaryDirectory() as tmpd:
        tp = Path(tmpd)
        if lang == "PYTHON 3":
            src = tp / "sol.py"
            src.write_text(code, encoding="utf-8")
            cmd = [sys.executable, str(src)]
        elif lang in ("C", "CLANG C"):
            src, exe = tp / "sol.c", tp / "sol_bin"
            src.write_text(code, encoding="utf-8")
            c_res = subprocess.run(["/usr/bin/clang", "-O2", str(src), "-lm", "-o", str(exe)], capture_output=True, text=True, timeout=8)
            if c_res.returncode != 0:
                return False, f"C compile error:\n{c_res.stderr[:400]}"
            cmd = [str(exe)]
        elif lang == "C++":
            src, exe = tp / "sol.cpp", tp / "sol_bin"
            src.write_text(code, encoding="utf-8")
            c_res = subprocess.run(["/usr/bin/clang++", "-std=c++17", "-O2", str(src), "-o", str(exe)], capture_output=True, text=True, timeout=10)
            if c_res.returncode != 0:
                return False, f"C++ compile error:\n{c_res.stderr[:400]}"
            cmd = [str(exe)]
        elif lang == "JAVASCRIPT" and os.path.exists(NODE_BIN):
            src = tp / "sol.js"
            src.write_text(code, encoding="utf-8")
            cmd = [NODE_BIN, str(src)]
        else:
            return True, ""

        for idx, sc in enumerate(valid_samples, start=1):
            inp = str(sc.get("input", ""))
            exp = str(sc.get("output", ""))
            try:
                proc = subprocess.run(
                    cmd,
                    input=inp if inp.endswith("\n") else inp + "\n",
                    capture_output=True,
                    text=True,
                    timeout=3.0,
                )
            except subprocess.TimeoutExpired:
                return False, f"Timeout (>3s) on sample #{idx}"
            if proc.returncode != 0:
                return False, f"Runtime error on sample #{idx}: {proc.stderr[:250]}"
            if norm_out(proc.stdout) != norm_out(exp):
                return False, f"Mismatch #{idx}: in={inp[:140]!r} exp={exp[:140]!r} got={proc.stdout.strip()[:140]!r}"

    return True, ""


def solve_problem_offline_sync(
    meta: Dict[str, Any],
    lang: str,
    starter_code: str = "",
    platform_error: str = "",
    seed: int = 0,
) -> Tuple[str, bool, str]:
    """Synthesizes & locally validates a solution in a background worker thread."""
    slug = meta["slug"]
    cache_path = PRECOMP_DIR / f"{slug}__{lang.replace(' ', '_')}.json"
    if not platform_error and not starter_code and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if cached.get("code") and cached.get("local_ok"):
                return cached["code"], True, ""
        except Exception:
            pass

    lang_spec = {
        "PYTHON 3": "Write a complete Python 3 program reading from sys.stdin and printing exact output to stdout.",
        "C": "Write a complete C11 program (#include <stdio.h>, <stdlib.h>, <string.h>, <math.h>) reading stdin and printing exact stdout.",
        "C++": "Write a complete C++17 program (#include <iostream>, <vector>, <string>, <algorithm>, etc.) reading cin/stdin and printing exact cout.",
        "JAVASCRIPT": "Write a complete Node.js program reading stdin via fs.readFileSync(0, 'utf8') and printing via console.log.",
        "JAVA": "Write a complete Java program with `public class Main` and `public static void main(String[] args)` reading System.in.",
        "JAVA 8": "Write a complete Java 8 program with `public class Main` and `public static void main(String[] args)` reading System.in.",
    }.get(lang, f"Write a complete {lang} program reading stdin and printing exact stdout.")

    sys_prompt = (
        f"Expert competitive programmer ({lang}). {lang_spec}\n"
        "RULES: Output ONLY raw code (no prose, no input prompts). Match exact case/spacing/'-1' rules. "
        "Use optimal O(N) / O(N log N) algorithms and handle N=0, negative numbers, duplicates, and trailing spaces."
    )

    samples = meta.get("samples") or []
    samples_txt = "\n".join(
        f"Sample {i+1} Input:\n{s.get('input','')}\nSample {i+1} Output:\n{s.get('output','')}"
        for i, s in enumerate(samples[:4])
    )
    starter_txt = f"\nEditor Template:\n{starter_code[:500]}\n" if starter_code.strip() else ""
    err_txt = f"\nPREVIOUS SUBMISSION FAILED ON HIDDEN TESTS:\n{platform_error[:500]}\nFix all edge cases & formatting!\n" if platform_error else ""

    base_prompt = (
        f"Problem: {meta.get('title', slug)}\nLanguage: {lang}\n\n"
        f"{(meta.get('description') or meta.get('raw') or '')[:2600]}\n\n"
        f"Input: {meta.get('input_spec', '')}\nOutput: {meta.get('output_spec', '')}\n"
        f"Constraints: {meta.get('constraints', '')}\n\n{samples_txt}\n{starter_txt}{err_txt}"
    )

    prompt = base_prompt
    last_code, last_err = "", ""
    max_tries = 2 if platform_error else 3

    for tr in range(max_tries):
        raw = call_free_llm_sync(sys_prompt, prompt, seed + tr * 3)
        if not raw:
            last_err = "empty_llm"
            continue
        code = strip_code_fences(raw)
        last_code = code
        ok, err = verify_locally_sync(code, lang, samples)
        if ok:
            if not platform_error:
                try:
                    tmp_c = cache_path.with_suffix(".ctmp")
                    tmp_c.write_text(
                        json.dumps({"slug": slug, "lang": lang, "code": code, "local_ok": True}),
                        encoding="utf-8",
                    )
                    tmp_c.replace(cache_path)
                except Exception:
                    pass
            return code, True, ""
        last_err = err
        prompt = f"{base_prompt}\n\nPrevious {lang} attempt failed local check:\n{code[:1200]}\nError:\n{err}\nOutput ONLY corrected {lang} code."

    return last_code, False, last_err


async def fast_route_filter(route: Route) -> None:
    req = route.request
    url = req.url
    if req.resource_type in ("image", "media", "font"):
        await route.abort()
        return
    if any(dom in url for dom in BLOCKED_TRACKER_DOMAINS):
        await route.abort()
        return
    await route.continue_()


async def switch_lang_fast(page: Page, target_lang: str) -> Tuple[str, str]:
    info = await page.evaluate(
        """() => {
            const sel = document.querySelector('select#editorModeSelectDesktop');
            const opts = sel ? Array.from(sel.options).map(o => o.value) : ['PYTHON 3'];
            const current = sel ? sel.value : 'PYTHON 3';
            let starter = '';
            try { if (window.ace) starter = window.ace.edit('editor').getValue() || ''; } catch (e) {}
            return { current, opts, dataId: sel?.getAttribute('data-id') || '', starter };
        }"""
    )
    opts = info["opts"] or ["PYTHON 3"]
    chosen = target_lang if target_lang in opts else next((lp for lp in LANG_PREFERENCE if lp in opts), opts[0])

    if info["current"] != chosen and info["dataId"]:
        did = info["dataId"]
        ss_main = page.locator(f'.ss-main[data-id="{did}"]').first
        if await ss_main.count() > 0 and await ss_main.is_visible():
            await ss_main.click(force=True)
            await page.wait_for_timeout(150)
            opt_loc = page.locator(f'.ss-content[data-id="{did}"] .ss-option').filter(
                has_text=re.compile(f"^{re.escape(chosen)}$")
            ).first
            if await opt_loc.count() > 0:
                await opt_loc.click(force=True)
                await page.wait_for_timeout(200)
                await page.evaluate(
                    """() => {
                        const noBtn = Array.from(document.querySelectorAll('dialog button, .modal button')).find(
                            b => b.textContent.trim() === 'No' && b.offsetParent !== null
                        );
                        if (noBtn) noBtn.click();
                    }"""
                )
    starter = await page.evaluate(
        "() => { try { return window.ace ? (window.ace.edit('editor').getValue() || '') : ''; } catch (e) { return ''; } }"
    )
    return chosen, starter


async def inject_and_submit_fast(page: Page, code: str) -> Tuple[bool, str]:
    await page.evaluate(
        """(src) => {
            if (window.ace) {
                const ed = window.ace.edit('editor');
                ed.setValue(src, -1);
                ed.clearSelection();
            } else {
                const el = document.querySelector('#editor');
                if (el && el.env && el.env.editor) el.env.editor.setValue(src, -1);
            }
        }""",
        code,
    )
    sub_btn = page.locator("button.submit-code, button:has-text('Submit'):not(.submit-button)").first
    await sub_btn.click(force=True)

    # Ultra-fast 140ms polling up to 16 seconds
    for _ in range(115):
        await page.wait_for_timeout(140)
        verdict = await page.evaluate(
            """() => {
                const qs = document.querySelector('.question-status');
                if (qs && qs.textContent.toLowerCase().includes('solved')) return { ok: true, msg: 'SOLVED_STATUS' };

                const modals = document.querySelectorAll('dialog, .modal, [role="dialog"]');
                for (const m of modals) {
                    const t = m.innerText || '';
                    if ((t.includes('Geekoins') || t.includes('Congratulations')) && (m.open || m.offsetParent !== null)) {
                        return { ok: true, msg: 'SOLVED_MODAL' };
                    }
                }

                const body = document.body.innerText || '';
                if (body.includes('Answer\\nCorrect Answer') || body.includes('Correct Answer\\nTest Cases')) {
                    return { ok: true, msg: 'CORRECT_ANSWER' };
                }
                for (const errTag of ['Wrong Answer', 'Compiler Error', 'Compilation Error', 'Runtime Error', 'Time Limit Exceeded']) {
                    if (body.includes('Answer\\n' + errTag)) {
                        const idx = body.indexOf('Answer\\n' + errTag);
                        return { ok: false, done: true, msg: body.slice(idx, idx + 420) };
                    }
                }
                return { ok: false, done: false, msg: '' };
            }"""
        )
        if verdict["ok"]:
            return True, verdict["msg"]
        if verdict.get("done"):
            return False, verdict["msg"]

    return False, "VERDICT_TIMEOUT"


async def harvest_easy_catalog_single_tab(page: Page) -> List[Dict[str, Any]]:
    if EASY_CATALOG_CACHE.exists():
        return json.loads(EASY_CATALOG_CACHE.read_text(encoding="utf-8"))

    log("Harvesting Easy problems in the single tab to expand pool beyond 1,316...")
    await page.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=45000)
    await page.wait_for_timeout(2000)
    await page.evaluate(
        "() => { for (const b of document.querySelectorAll('button')) if (b.innerText.trim() === '✕' || b.innerText.trim() === 'Finish') b.click(); }"
    )
    try:
        did = await page.evaluate("() => document.querySelector('select#itemsPerPage')?.getAttribute('data-id') || ''")
        if did:
            await page.locator(f'.ss-main[data-id="{did}"]').first.click(force=True)
            await page.wait_for_timeout(200)
            await page.locator(f'.ss-content[data-id="{did}"] .ss-option', has_text="50").first.click(force=True)
            await page.wait_for_timeout(1200)
        await page.locator("#difficulty-filter-id").first.click(force=True)
        await page.wait_for_timeout(250)
        await page.locator("li.difficulty-filter-option:has-text('Easy')").first.click(force=True)
        await page.wait_for_timeout(1500)
    except Exception:
        pass

    easy_items: Dict[str, Dict[str, Any]] = {}
    seen_fp = set()
    for _ in range(65):
        rows = await page.evaluate(
            """() => Array.from(document.querySelectorAll('tbody tr')).map(r => {
                const tds = Array.from(r.querySelectorAll('td'));
                if (tds.length < 4) return null;
                const html0 = tds[0].innerHTML || '';
                const done = html0.includes('completed-icon_svg__a') || html0.includes('#0DBA4B');
                const cells = tds.map(c => c.innerText.trim());
                const title = cells.find(c => /^\\d+\\.\\s/.test(c)) || cells[1] || cells[0];
                return { title, completed: done };
            }).filter(Boolean)"""
        )
        if not rows:
            break
        fp = rows[0]["title"] + str(len(rows))
        if fp in seen_fp:
            break
        seen_fp.add(fp)
        for r in rows:
            clean = re.sub(r"^\d+\.\s*", "", r["title"].strip())
            sl = re.sub(r"[^a-z0-9]+", "-", clean.lower()).strip("-")
            easy_items[sl] = {"slug": sl, "title": r["title"], "difficulty": "Easy", "completed": bool(r["completed"])}
        nxt = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
        if await nxt.count() == 0 or (await nxt.get_attribute("disabled")) is not None:
            break
        await nxt.click(force=True)
        await page.wait_for_timeout(550)

    out = list(easy_items.values())
    EASY_CATALOG_CACHE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    log(f"Harvested {len(out)} Easy problems in single tab!")
    return out


def save_checkpoint(results: Dict[str, Any], start_ts: float) -> int:
    RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
    solved_cnt = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    failed_cnt = sum(1 for v in results.values() if v.get("status") not in ("COMPLETED", None))
    rate_pm = round(solved_cnt / max((time.time() - start_ts) / 60.0, 0.1), 1)
    status_obj = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "verified_solved_total": solved_cnt,
        "attempted_other": failed_cnt,
        "solve_rate_per_min": rate_pm,
        "elapsed_minutes": round((time.time() - start_ts) / 60.0, 1),
    }
    LIVE_STATUS_JSON.write_text(json.dumps(status_obj, indent=2), encoding="utf-8")
    return solved_cnt


async def main() -> int:
    start_ts = time.time()
    target_solved = int(os.environ.get("CK_TARGET", "1250"))
    producer_workers = int(os.environ.get("CK_PRODUCERS", "20"))

    for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        p = PROFILE_DIR / lk
        if p.exists() or p.is_symlink():
            try:
                p.unlink()
            except Exception:
                pass

    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    sm = StateManager()

    # Load all 1,316 pre-scraped problems immediately (Medium before Hard, shorter descriptions first for fastest wins!)
    scraped_metas: List[Dict[str, Any]] = []
    for pf in sorted(PROB_DIR.glob("*.json")):
        try:
            d = json.loads(pf.read_text(encoding="utf-8"))
            d["slug"] = d.get("slug") or pf.stem
            if d.get("completed"):
                results.setdefault(d["slug"], {"status": "COMPLETED", "language": "EXISTING", "attempts": 1})
                continue
            if results.get(d["slug"], {}).get("status") in ("COMPLETED", "SKIPPED_NO_EDITOR"):
                continue
            if results.get(d["slug"], {}).get("attempts", 0) >= 3:
                continue
            scraped_metas.append(d)
        except Exception:
            continue

    scraped_metas.sort(
        key=lambda m: (
            0 if m.get("difficulty") == "Easy" else (1 if m.get("difficulty") == "Medium" else 2),
            0 if m.get("samples") else 1,
            len(m.get("description") or ""),
        )
    )
    log(f"Immediate pre-scraped problem queue ready: {len(scraped_metas)} problems | Already solved: {sum(1 for v in results.values() if v.get('status')=='COMPLETED')}")

    ready_q: "asyncio.Queue[Optional[Dict[str, Any]]]" = asyncio.Queue(maxsize=300)
    executor = ThreadPoolExecutor(max_workers=producer_workers)
    loop = asyncio.get_running_loop()
    in_flight_tasks: set = set()

    def schedule_precompute(meta: Dict[str, Any], lang: str, plat_err: str = "", retry_num: int = 0, seed: int = 0) -> None:
        async def _job():
            code, local_ok, local_err = await loop.run_in_executor(
                executor, solve_problem_offline_sync, meta, lang, "", plat_err, seed
            )
            await ready_q.put({
                "meta": meta,
                "lang": lang,
                "code": code,
                "local_ok": local_ok,
                "local_err": local_err,
                "retry_num": retry_num,
            })

        t = asyncio.create_task(_job())
        in_flight_tasks.add(t)
        t.add_done_callback(in_flight_tasks.discard)

    async def feed_initial_pool():
        for idx, m in enumerate(scraped_metas):
            while ready_q.qsize() > 180:
                await asyncio.sleep(0.2)
            schedule_precompute(m, guess_initial_language(m), seed=idx)
            if idx < 25:
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.05)

    feeder_task = asyncio.create_task(feed_initial_pool())

    async with async_playwright() as pw:
        log("Launching foreground Brave Browser (STRICT SINGLE-TAB TURBO MODE)...")
        ctx = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=config.BROWSER_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
        )
        subprocess.run(["osascript", "-e", 'tell application "Brave Browser" to activate'], check=False)

        # Enforce strictly ONE tab!
        open_pages = list(ctx.pages)
        page = open_pages[0] if open_pages else await ctx.new_page()
        for extra in open_pages[1:]:
            try:
                await extra.close()
            except Exception:
                pass

        await page.route("**/*", fast_route_filter)

        easy_harvested = False
        processed_session = 0

        while True:
            solved_total = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            if solved_total >= target_solved and ready_q.empty() and feeder_task.done() and not in_flight_tasks:
                break

            # If pre-scraped queue is drained and we still want more solved, harvest Easy problems in the SAME tab!
            if ready_q.empty() and feeder_task.done() and not in_flight_tasks:
                if not easy_harvested:
                    easy_harvested = True
                    easy_list = await harvest_easy_catalog_single_tab(page)
                    new_easy = 0
                    for e_idx, e_item in enumerate(easy_list):
                        sl = e_item["slug"]
                        if e_item.get("completed"):
                            results.setdefault(sl, {"status": "COMPLETED", "language": "EXISTING", "attempts": 1})
                            continue
                        if results.get(sl, {}).get("status") in ("COMPLETED", "SKIPPED_NO_EDITOR"):
                            continue
                        # Put lightweight shell item; single tab will extract live description on visit if uncached
                        pfile = PROB_DIR / f"{sl}.json"
                        if pfile.exists():
                            emeta = json.loads(pfile.read_text(encoding="utf-8"))
                            schedule_precompute(emeta, guess_initial_language(emeta), seed=2000 + e_idx)
                        else:
                            await ready_q.put({
                                "meta": e_item,
                                "lang": "PYTHON 3",
                                "code": "",
                                "local_ok": False,
                                "local_err": "NEEDS_LIVE_EXTRACT",
                                "retry_num": 0,
                            })
                        new_easy += 1
                    log(f"Queued {new_easy} Easy problems into single-tab pipeline!")
                    if new_easy == 0:
                        break
                    continue
                else:
                    break

            try:
                bundle = await asyncio.wait_for(ready_q.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue

            if bundle is None:
                break

            meta = bundle["meta"]
            slug = meta["slug"]
            if results.get(slug, {}).get("status") == "COMPLETED":
                ready_q.task_done()
                continue

            t0 = time.time()
            status = "FAILED"
            reason = ""
            chosen_lang = bundle["lang"]
            code = bundle["code"]
            retry_num = bundle["retry_num"]

            try:
                # Close any stray popup tabs if website ever opened one
                for extra_p in list(ctx.pages):
                    if extra_p != page and not extra_p.is_closed():
                        try:
                            await extra_p.close()
                        except Exception:
                            pass

                await page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=30000)
                try:
                    await page.wait_for_selector("#editor", timeout=8000)
                except Exception:
                    results[slug] = {"status": "SKIPPED_NO_EDITOR", "attempts": 1, "ts": datetime.now(timezone.utc).isoformat()}
                    ready_q.task_done()
                    continue

                # Wait briefly for Ace JS binding (`window.ace`)
                await page.wait_for_function("() => Boolean(window.ace || document.querySelector('#editor')?.env?.editor)", timeout=6000)

                already = await page.evaluate(
                    "() => Boolean(document.querySelector('.question-status')?.textContent?.toLowerCase()?.includes('solved'))"
                )
                if already:
                    status, reason = "COMPLETED", "Already solved"
                else:
                    chosen_lang, starter_code = await switch_lang_fast(page, bundle["lang"])

                    # Extract live description if this was an uncached Easy problem, OR re-synthesize if language was locked differently
                    if bundle["local_err"] == "NEEDS_LIVE_EXTRACT" or not meta.get("description"):
                        raw_dom = await page.evaluate(
                            "() => (document.querySelector('.problem-description, #problem-description, .question-content, main')?.innerText || document.body.innerText).slice(0, 3500)"
                        )
                        samples = []
                        si_m = re.search(r"Sample Input\s*:?\s*\n(.*?)(?:\n\s*Sample Output|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
                        so_m = re.search(r"Sample Output\s*:?\s*\n(.*?)(?:\n\s*(?:Explanation|Note|Constraints|Hint)|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
                        if si_m and so_m:
                            samples.append({"input": si_m.group(1).strip(), "output": so_m.group(1).strip().split("\n\n")[0].strip()})
                        meta = {**meta, "description": raw_dom, "samples": samples, "raw": raw_dom}
                        (PROB_DIR / f"{slug}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
                        code, _, _ = await loop.run_in_executor(
                            executor, solve_problem_offline_sync, meta, chosen_lang, starter_code, "", processed_session
                        )
                    elif chosen_lang != bundle["lang"] or not code.strip():
                        code, _, _ = await loop.run_in_executor(
                            executor, solve_problem_offline_sync, meta, chosen_lang, starter_code, "", processed_session + 7
                        )

                    if code.strip():
                        plat_ok, plat_msg = await inject_and_submit_fast(page, code)
                        if plat_ok:
                            status, reason = "COMPLETED", plat_msg
                        else:
                            status, reason = "FAILED_PLATFORM", plat_msg[:240]
                            # Non-blocking background self-debug retry: tab moves on immediately while pool repairs!
                            if retry_num < 1:
                                schedule_precompute(meta, chosen_lang, plat_err=plat_msg, retry_num=retry_num + 1, seed=processed_session + 13)
                    else:
                        status, reason = "FAILED_SYNTHESIS", "Empty code"

            except Exception as exc:
                err_str = str(exc)
                if "Target page, context or browser has been closed" in err_str:
                    log("Foreground Brave tab closed — saving checkpoint and exiting cleanly.")
                    save_checkpoint(results, start_ts)
                    return 1
                status, reason = "ERROR", err_str[:220]

            dur = round(time.time() - t0, 2)
            processed_session += 1
            prev_att = results.get(slug, {}).get("attempts", 0)
            results[slug] = {
                "status": status,
                "language": chosen_lang,
                "attempts": prev_att + 1,
                "reason": reason,
                "duration_s": dur,
                "difficulty": meta.get("difficulty", "Medium"),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if status == "COMPLETED" and code.strip():
                ext = LANG_EXT.get(chosen_lang, "txt")
                (SOL_DIR / f"{slug}.{ext}").write_text(code, encoding="utf-8")

            solved_now = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            if processed_session % 5 == 0 or status == "COMPLETED":
                log(
                    f"[#{processed_session}] {slug} ({chosen_lang}, {dur}s) -> {status} | "
                    f"SOLVED={solved_now} | ReadyBuf={ready_q.qsize()} | InFlightLLM={len(in_flight_tasks)}"
                )

            if processed_session % 15 == 0:
                save_checkpoint(results, start_ts)
                try:
                    sm.batch_record_tasks([{
                        "task_id": f"guvi-{slug}",
                        "platform": "guvi",
                        "task_category": "CodeKata",
                        "title": meta.get("title", slug),
                        "url": f"https://www.guvi.in/code-kata/{slug}/",
                        "status": TaskStatus.COMPLETED.value if status == "COMPLETED" else TaskStatus.FAILED.value,
                        "attempt_count": prev_att + 1,
                        "result": "PASSED" if status == "COMPLETED" else status,
                        "failure_reason": None if status == "COMPLETED" else reason,
                        "next_action": "NONE",
                        "time_spent_seconds": dur,
                    }])
                except Exception:
                    pass

            ready_q.task_done()

        solved_final = save_checkpoint(results, start_ts)
        await ctx.storage_state(path=str(config.STORAGE_STATE_PATH))
        await ctx.close()

    executor.shutdown(wait=False)
    log(f"=== TURBO SINGLE-TAB COMPLETE: {solved_final} VERIFIED SOLVED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
