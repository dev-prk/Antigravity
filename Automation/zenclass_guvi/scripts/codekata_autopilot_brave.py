"""
codekata_autopilot_brave.py — Autonomous Foreground Brave Browser CodeKata Solver & Submitter.

Architecture:
1. Launches ONE visible foreground Brave Browser window reusing zenclass_guvi/.browser_profile.
2. Crawls all CodeKata pages (50 rows/page) across Easy, Medium, and Hard, capturing Qwik XHR
   `uniqueUrl` slugs + `status` ("solved" vs unsolved) into data/ck_full_catalog.json.
3. Runs an async multi-language solver + multi-tab Brave submitter (5 tabs in the single window):
   - Reads allowed languages from `select#editorModeSelectDesktop` (prefers PYTHON 3 -> C++ -> C -> JAVASCRIPT -> JAVA).
   - Synthesizes solutions strictly via FreeLLMAPI (http://127.0.0.1:31415 `auto` + Kilo keyless free fallback — $0 paid quota).
   - Validates locally against extracted sample test cases using python3 / clang++ / clang / node (with up to 3 repair turns).
   - Injects code via focus-free `window.ace.edit('editor').setValue(code, -1)` and clicks Submit.
   - Verifies positive platform confirmation ('Solved' / 'Correct Answer' / 'Geekoins'); retries once on hidden-test rejection.
   - Checkpoints every result to data/ck_results.json, data/automation_state.db, solutions/, and PROGRESS.md.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import BrowserContext, Page, async_playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
AUTO_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation")
sys.path.insert(0, str(ROOT))
import config  # noqa: E402
from core.state_manager import StateManager, TaskStatus  # noqa: E402
from solver.extractor import extract_problem_spec  # noqa: E402

BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
PROFILE_DIR = ROOT / ".browser_profile"
FULL_CATALOG_JSON = ROOT / "data" / "ck_full_catalog.json"
PROB_DIR = ROOT / "data" / "ck_problems"
SOL_DIR = ROOT / "solutions"
RESULTS_JSON = ROOT / "data" / "ck_results.json"
LIVE_STATUS_JSON = ROOT / "reports" / "CODEKATA_LIVE_STATUS.json"
NODE_BIN = "/Users/devesh/.local/node/bin/node"

PROB_DIR.mkdir(parents=True, exist_ok=True)
SOL_DIR.mkdir(parents=True, exist_ok=True)
LIVE_STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)

FREELLM_BASE = os.environ.get("FREELLM_BASE", "http://127.0.0.1:31415")
KILO_URL = "https://api.kilo.ai/api/gateway/v1/chat/completions"
FREEAPI_DB = os.path.expanduser("~/Library/Application Support/FreeLLMAPI/freeapi.db")

LANG_PREFERENCE = ["PYTHON 3", "C++", "C", "JAVASCRIPT", "JAVA", "JAVA 8", "PYTHON 2", "BASH", "SQLITE"]
LANG_EXT = {
    "PYTHON 3": "py",
    "PYTHON 2": "py",
    "C++": "cpp",
    "C": "c",
    "CLANG C": "c",
    "JAVASCRIPT": "js",
    "JAVA": "java",
    "JAVA 8": "java",
    "SQLITE": "sql",
    "BASH": "sh",
}


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

# Rotate across strong free models via FreeLLMAPI + Kilo free gateway (never touches paid `agy`)
MODEL_ROTATION = [
    "auto",
    "groq:llama-3.3-70b-versatile",
    "nvidia:meta/llama-3.1-70b-instruct",
    "qwen3.8-27b",
    "gpt-oss-120b",
    "openrouter:meta-llama/llama-3.1-70b-instruct:free",
]


def _sync_llm_call(system_prompt: str, user_prompt: str, attempt_seed: int = 0) -> str:
    models_to_try = MODEL_ROTATION[attempt_seed % len(MODEL_ROTATION):] + MODEL_ROTATION[:attempt_seed % len(MODEL_ROTATION)]
    if FREELLM_KEY:
        for model_name in models_to_try[:3]:
            try:
                body = {
                    "model": model_name,
                    "max_tokens": 1800,
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
                with urllib.request.urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
                if txt and len(txt) > 10 and not txt.startswith("Safety:"):
                    return txt
            except Exception:
                continue

    # Tier 2 keyless free pool fallback
    for km in ("kilo-auto/free", "openrouter/free"):
        try:
            body = {
                "model": km,
                "max_tokens": 2048,
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
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            msg = (data.get("choices") or [{}])[0].get("message") or {}
            txt = (msg.get("content") or "").strip()
            if txt and len(txt) > 10:
                return txt
        except Exception:
            continue

    return ""


def strip_code_fences(raw: str) -> str:
    txt = (raw or "").strip()
    # Strip <think>...</think> reasoning blocks if emitted by reasoning models
    txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.DOTALL).strip()
    m = re.search(r"```(?:[a-zA-Z0-9_+]+)?\s*\n(.*?)```", txt, flags=re.DOTALL)
    if m:
        return m.group(1).strip() + "\n"
    # Remove stray leading/trailing backticks
    txt = re.sub(r"^```[a-zA-Z0-9_+]*\s*", "", txt)
    txt = re.sub(r"\s*```$", "", txt)
    return txt.strip() + "\n"


def norm_out(s: str) -> str:
    return "\n".join(line.rstrip() for line in str(s).strip().splitlines())


def _sync_local_verify(code: str, lang: str, samples: List[Dict[str, str]]) -> Tuple[bool, str]:
    valid_samples = [s for s in samples if s.get("input") or s.get("output")]
    if not valid_samples:
        # Syntax check at minimum for Python 3
        if lang == "PYTHON 3":
            try:
                compile(code, "<solution>", "exec")
            except SyntaxError as exc:
                return False, f"Python SyntaxError: {exc}"
        return True, ""

    if lang in ("JAVA", "JAVA 8"):
        # No local JDK on this machine; defer to Guvi online judge
        return True, ""

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_path = Path(tmpd)
        run_cmd: List[str] = []

        if lang == "PYTHON 3":
            src = tmp_path / "sol.py"
            src.write_text(code, encoding="utf-8")
            run_cmd = [sys.executable, str(src)]
        elif lang in ("C", "CLANG C"):
            src = tmp_path / "sol.c"
            exe = tmp_path / "sol_bin"
            src.write_text(code, encoding="utf-8")
            comp = subprocess.run(["/usr/bin/clang", "-O2", str(src), "-lm", "-o", str(exe)], capture_output=True, text=True, timeout=10)
            if comp.returncode != 0:
                return False, f"C compile error:\n{comp.stderr[:500]}"
            run_cmd = [str(exe)]
        elif lang == "C++":
            src = tmp_path / "sol.cpp"
            exe = tmp_path / "sol_bin"
            src.write_text(code, encoding="utf-8")
            comp = subprocess.run(["/usr/bin/clang++", "-std=c++17", "-O2", str(src), "-o", str(exe)], capture_output=True, text=True, timeout=12)
            if comp.returncode != 0:
                return False, f"C++ compile error:\n{comp.stderr[:500]}"
            run_cmd = [str(exe)]
        elif lang == "JAVASCRIPT" and os.path.exists(NODE_BIN):
            src = tmp_path / "sol.js"
            src.write_text(code, encoding="utf-8")
            run_cmd = [NODE_BIN, str(src)]
        else:
            return True, ""

        for idx, sc in enumerate(valid_samples, start=1):
            inp = str(sc.get("input", ""))
            exp = str(sc.get("output", ""))
            try:
                proc = subprocess.run(
                    run_cmd,
                    input=inp if inp.endswith("\n") else inp + "\n",
                    capture_output=True,
                    text=True,
                    timeout=4.0,
                )
            except subprocess.TimeoutExpired:
                return False, f"Sample #{idx} timed out (>4s) on input={inp[:120]!r}"

            if proc.returncode != 0:
                return False, f"Sample #{idx} runtime error (exit {proc.returncode}) on input={inp[:120]!r}: {proc.stderr[:300]}"

            if norm_out(proc.stdout) != norm_out(exp):
                return (
                    False,
                    f"Sample #{idx} output mismatch:\nInput:\n{inp[:200]}\nExpected:\n{exp[:200]}\nActual:\n{proc.stdout.strip()[:200]}",
                )

    return True, ""


async def synthesize_verified_solution(
    meta: Dict[str, Any],
    lang: str,
    starter_code: str = "",
    platform_error: str = "",
    seed_offset: int = 0,
) -> Tuple[str, bool, str]:
    """Generates and locally validates a solution in `lang` with up to 3 self-debugging turns."""
    lang_hint = {
        "PYTHON 3": "Write a standalone Python 3 program reading from sys.stdin and printing exact required output to stdout.",
        "C": "Write a complete standard C11 program (#include <stdio.h>, <stdlib.h>, <string.h>, <math.h>) reading from stdin and printing exact output to stdout.",
        "C++": "Write a complete C++17 program (#include <bits/stdc++.h> or standard headers) reading from cin/stdin and printing exact output to cout.",
        "JAVASCRIPT": "Write a complete Node.js program reading all stdin via fs.readFileSync(0, 'utf8') and printing exact output via console.log.",
        "JAVA": "Write a complete Java program with `public class Main` and `public static void main(String[] args)` reading from Scanner/BufferedReader(System.in).",
        "JAVA 8": "Write a complete Java 8 program with `public class Main` and `public static void main(String[] args)` reading from System.in.",
    }.get(lang, f"Write a complete {lang} program reading from stdin and writing exact output to stdout.")

    sys_prompt = (
        f"You are an expert competitive programmer solving a GUVI CodeKata problem in {lang}. "
        f"{lang_hint} "
        "CRITICAL RULES:\n"
        "1. Output ONLY raw source code — NO markdown prose, NO explanations, NO input prompts like input('Enter:').\n"
        "2. Match output capitalization, spacing, and '-1' / edge-case rules in the problem statement & samples EXACTLY.\n"
        "3. Handle edge cases (empty lines, trailing spaces, N=0/1, negative integers, large N with optimal time complexity)."
    )

    samples_list = meta.get("samples") or []
    samples_txt = "\n".join(
        f"Sample {i+1} Input:\n{s.get('input','')}\nSample {i+1} Expected Output:\n{s.get('output','')}"
        for i, s in enumerate(samples_list[:4])
    )
    starter_block = f"\nStarter Editor Template (if relevant):\n{starter_code[:600]}\n" if starter_code.strip() else ""
    plat_block = f"\nPREVIOUS SUBMISSION FAILED ON HIDDEN TESTS WITH:\n{platform_error[:600]}\nFix all edge cases, formatting, and complexity!\n" if platform_error else ""

    base_prompt = (
        f"Title: {meta.get('title', meta.get('slug'))}\n"
        f"Language Required: {lang}\n\n"
        f"Problem Statement:\n{meta.get('description') or meta.get('raw', '')[:2500]}\n\n"
        f"Input Specification:\n{meta.get('input_spec', '')}\n"
        f"Output Specification:\n{meta.get('output_spec', '')}\n"
        f"Constraints:\n{meta.get('constraints', '')}\n\n"
        f"{samples_txt}\n"
        f"{starter_block}{plat_block}"
    )

    last_code = ""
    last_err = ""
    prompt = base_prompt

    for attempt in range(3):
        raw_reply = await asyncio.to_thread(_sync_llm_call, sys_prompt, prompt, seed_offset + attempt)
        if not raw_reply:
            last_err = "Empty LLM reply"
            continue
        code = strip_code_fences(raw_reply)
        last_code = code
        ok, err = await asyncio.to_thread(_sync_local_verify, code, lang, samples_list)
        if ok:
            return code, True, ""
        last_err = err
        prompt = (
            f"{base_prompt}\n\n"
            f"Your previous {lang} code failed local verification:\n"
            f"--- CODE ---\n{code[:1500]}\n--- ERROR ---\n{err}\n\n"
            f"Return ONLY the corrected {lang} code."
        )

    return last_code, False, last_err


def slugify(title: str) -> str:
    t = re.sub(r"^\d+\.\s*", "", title.strip())
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


async def crawl_full_catalog(page: Page) -> List[Dict[str, Any]]:
    """Crawls all CodeKata pages at 50 rows/page (~44 pages) to discover all Easy, Medium, and Hard problems."""
    captured_docs: Dict[str, Dict[str, Any]] = {}

    async def handle_response(resp):
        try:
            if "guvi.in" in resp.url and resp.status == 200:
                ct = resp.headers.get("content-type", "")
                if "json" in ct:
                    body = await resp.json()
                    docs = None
                    if isinstance(body, dict):
                        docs = body.get("documents") or (body.get("data") or {}).get("documents")
                    if isinstance(docs, list):
                        for d in docs:
                            if isinstance(d, dict) and d.get("uniqueUrl"):
                                sl = str(d["uniqueUrl"]).strip("/")
                                captured_docs[sl] = {
                                    "slug": sl,
                                    "qid": d.get("qid"),
                                    "title": f"{d.get('qid', '')}. {d.get('questionName', sl)}".strip(". "),
                                    "completed": str(d.get("status", "")).lower() == "solved",
                                }
        except Exception:
            pass

    page.on("response", handle_response)
    log("Crawling full 2,182-problem CodeKata catalog (50 items/page) in foreground Brave...")
    await page.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3500)

    # Dismiss welcome tour if visible
    await page.evaluate(
        """() => {
            for (const b of document.querySelectorAll('button')) {
                if (b.innerText.trim() === '✕' || b.innerText.trim() === 'Finish') b.click();
            }
        }"""
    )

    # Switch itemsPerPage to 50 via JS + SlimSelect / native select
    try:
        await page.select_option("select#itemsPerPage", value="50", force=True)
        await page.wait_for_timeout(2200)
    except Exception:
        pass

    catalog_by_slug: Dict[str, Dict[str, Any]] = {}
    seen_page_fingerprints = set()

    for page_no in range(1, 160):
        rows_data = await page.evaluate(
            """() => {
                return Array.from(document.querySelectorAll('tbody tr')).map(r => {
                    const tds = Array.from(r.querySelectorAll('td'));
                    if (tds.length < 4) return null;
                    const html0 = tds[0].innerHTML || '';
                    const done = html0.includes('completed-icon_svg__a') || html0.includes('#0DBA4B');
                    const cells = tds.map(c => c.innerText.trim());
                    const title = cells.find(c => /^\\d+\\.\\s/.test(c)) || cells[1] || cells[0];
                    const diff = cells.find(c => c === 'Easy' || c === 'Medium' || c === 'Hard') || 'Easy';
                    return { title, difficulty: diff, completed: done };
                }).filter(Boolean);
            }"""
        )
        if not rows_data:
            break
        fp = rows_data[0]["title"] + "|" + str(len(rows_data))
        if fp in seen_page_fingerprints:
            break
        seen_page_fingerprints.add(fp)

        for item in rows_data:
            sl = slugify(item["title"])
            catalog_by_slug[sl] = {
                "slug": sl,
                "title": item["title"],
                "difficulty": item["difficulty"],
                "completed": bool(item["completed"]),
            }

        if page_no % 5 == 0 or page_no == 1:
            log(f"Catalog crawl page {page_no}: {len(catalog_by_slug)} unique rows collected...")

        nxt = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
        if await nxt.count() == 0:
            break
        disabled = await nxt.get_attribute("disabled")
        if disabled is not None:
            break
        await nxt.click(force=True)
        await page.wait_for_timeout(1100)

    # Merge captured exact uniqueUrl slugs + existing ck_catalog.json (which has exact -2 slugs for Medium/Hard!)
    old_cat_path = ROOT / "data" / "ck_catalog.json"
    if old_cat_path.exists():
        for c in json.loads(old_cat_path.read_text(encoding="utf-8")):
            sl = c["slug"]
            if sl not in catalog_by_slug:
                catalog_by_slug[sl] = {
                    "slug": sl,
                    "title": c.get("title", sl),
                    "difficulty": c.get("difficulty", "Medium"),
                    "completed": bool(c.get("completed", False)),
                }

    for sl, doc in captured_docs.items():
        if sl in catalog_by_slug:
            catalog_by_slug[sl]["completed"] = catalog_by_slug[sl]["completed"] or doc["completed"]
        else:
            catalog_by_slug[sl] = {
                "slug": sl,
                "title": doc["title"],
                "difficulty": "Easy",
                "completed": doc["completed"],
            }

    # Also include any pre-scraped ck_problems/*.json slugs
    for pf in PROB_DIR.glob("*.json"):
        sl = pf.stem
        if sl not in catalog_by_slug:
            d = json.loads(pf.read_text(encoding="utf-8"))
            catalog_by_slug[sl] = {
                "slug": sl,
                "title": d.get("title", sl),
                "difficulty": d.get("difficulty", "Medium"),
                "completed": bool(d.get("completed", False)),
            }

    diff_rank = {"Easy": 0, "Medium": 1, "Hard": 2}
    final_list = sorted(
        catalog_by_slug.values(),
        key=lambda x: (diff_rank.get(x.get("difficulty", "Easy"), 1), x["slug"]),
    )
    FULL_CATALOG_JSON.write_text(json.dumps(final_list, indent=1), encoding="utf-8")
    log(
        f"Catalog crawl complete: {len(final_list)} total problems "
        f"({sum(1 for x in final_list if x['completed'])} already solved on portal)."
    )
    return final_list


async def switch_editor_language_if_needed(page: Page) -> Tuple[str, str]:
    """Reads allowed languages on current workspace, selects preferred language via SlimSelect, returns (lang, starter_code)."""
    info = await page.evaluate(
        """() => {
            const sel = document.querySelector('select#editorModeSelectDesktop');
            const opts = sel ? Array.from(sel.options).map(o => o.value) : ['PYTHON 3'];
            const current = sel ? sel.value : 'PYTHON 3';
            let starter = '';
            try {
                if (window.ace) starter = window.ace.edit('editor').getValue() || '';
            } catch (e) {}
            return { current, opts, dataId: sel?.getAttribute('data-id') || '', starter };
        }"""
    )
    opts = info["opts"] or ["PYTHON 3"]
    chosen = next((lp for lp in LANG_PREFERENCE if lp in opts), opts[0])

    if info["current"] != chosen and info["dataId"]:
        did = info["dataId"]
        ss_main = page.locator(f'.ss-main[data-id="{did}"]').first
        if await ss_main.count() > 0 and await ss_main.is_visible():
            await ss_main.click(force=True)
            await page.wait_for_timeout(300)
            opt_loc = page.locator(f'.ss-content[data-id="{did}"] .ss-option').filter(has_text=re.compile(f"^{re.escape(chosen)}$")).first
            if await opt_loc.count() > 0:
                await opt_loc.click(force=True)
                await page.wait_for_timeout(400)
                # Dismiss 'Keep the Code Changes?' modal if shown
                await page.evaluate(
                    """() => {
                        const btns = Array.from(document.querySelectorAll('dialog button, .modal button'));
                        const noBtn = btns.find(b => b.textContent.trim() === 'No' && b.offsetParent !== null);
                        if (noBtn) noBtn.click();
                    }"""
                )
                await page.wait_for_timeout(250)

    starter = await page.evaluate(
        """() => {
            try { return window.ace ? (window.ace.edit('editor').getValue() || '') : ''; }
            catch (e) { return ''; }
        }"""
    )
    return chosen, starter


async def extract_live_meta(page: Page, slug: str, fallback_item: Dict[str, Any]) -> Dict[str, Any]:
    """Loads cached problem spec from data/ck_problems/<slug>.json or extracts directly from the live DOM."""
    cache_file = PROB_DIR / f"{slug}.json"
    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        if cached.get("description") and len(cached.get("description", "")) > 40:
            return cached

    raw_dom = await page.evaluate(
        """() => {
            const pane = document.querySelector('.problem-description, #problem-description, .question-content, main');
            return pane ? pane.innerText : document.body.innerText.slice(0, 4000);
        }"""
    )
    # Parse sample input / sample output blocks from raw problem text
    samples = []
    si_match = re.search(r"Sample Input\s*:?\s*\n(.*?)(?:\n\s*Sample Output|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
    so_match = re.search(r"Sample Output\s*:?\s*\n(.*?)(?:\n\s*(?:Explanation|Note|Constraints|Hint)|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
    if si_match and so_match:
        si = si_match.group(1).strip()
        so = so_match.group(1).strip().split("\n\n")[0].strip()
        if si or so:
            samples.append({"input": si, "output": so})

    meta = {
        "title": fallback_item.get("title", slug),
        "slug": slug,
        "difficulty": fallback_item.get("difficulty", "Easy"),
        "completed": False,
        "description": raw_dom[:3500],
        "input_spec": "",
        "output_spec": "",
        "constraints": "",
        "samples": samples,
        "raw": raw_dom[:3500],
    }
    cache_file.write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


async def submit_code_and_check(page: Page, code: str) -> Tuple[bool, str]:
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

    for _ in range(32):
        await page.wait_for_timeout(650)
        verdict = await page.evaluate(
            """() => {
                const qs = document.querySelector('.question-status');
                if (qs && qs.textContent.toLowerCase().includes('solved')) return { ok: true, msg: 'SOLVED_STATUS' };

                const modals = Array.from(document.querySelectorAll('dialog, .modal, [role="dialog"]'));
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
                        return { ok: false, done: true, msg: body.slice(idx, idx + 450) };
                    }
                }
                return { ok: false, done: false, msg: '' };
            }"""
        )
        if verdict["ok"]:
            return True, verdict["msg"]
        if verdict.get("done"):
            return False, verdict["msg"]

    return False, "TIMEOUT_WAITING_FOR_VERDICT"


def write_checkpoint(results: Dict[str, Any], total_catalog: int, start_ts: float) -> None:
    RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
    solved_cnt = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    failed_cnt = sum(1 for v in results.values() if v.get("status") not in ("COMPLETED", None))
    elapsed_m = round((time.time() - start_ts) / 60.0, 1)
    summary = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_catalog_problems": total_catalog,
        "verified_solved": solved_cnt,
        "failed_or_needs_retry": failed_cnt,
        "remaining": max(0, total_catalog - solved_cnt - failed_cnt),
        "elapsed_minutes": elapsed_m,
    }
    LIVE_STATUS_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")


async def worker_loop(
    worker_id: int,
    page: Page,
    queue: "asyncio.Queue[Dict[str, Any]]",
    results: Dict[str, Any],
    sm: StateManager,
    lock: asyncio.Lock,
    total_catalog: int,
    start_ts: float,
) -> None:
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        slug = item["slug"]
        t0 = time.time()
        status = "FAILED"
        reason = ""
        chosen_lang = "PYTHON 3"
        final_code = ""

        try:
            await page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=45000)
            # Check if 404 or missing editor
            try:
                await page.wait_for_selector("#editor", timeout=12000)
            except Exception:
                status, reason = "SKIPPED_NO_EDITOR", f"No #editor found at /code-kata/{slug}/"
                async with lock:
                    results[slug] = {"status": status, "reason": reason, "ts": datetime.now(timezone.utc).isoformat()}
                queue.task_done()
                continue

            await page.wait_for_timeout(1200)

            # Fast-path if already solved on platform
            already = await page.evaluate(
                "() => Boolean(document.querySelector('.question-status')?.textContent?.toLowerCase()?.includes('solved'))"
            )
            if already:
                status, reason = "COMPLETED", "Already solved on platform"
            else:
                chosen_lang, starter_code = await switch_editor_language_if_needed(page)
                meta = await extract_live_meta(page, slug, item)

                # Synthesis + local check
                code, local_ok, local_err = await synthesize_verified_solution(
                    meta=meta,
                    lang=chosen_lang,
                    starter_code=starter_code,
                    seed_offset=worker_id,
                )
                final_code = code

                if code.strip():
                    plat_ok, plat_msg = await submit_code_and_check(page, code)
                    if plat_ok:
                        status, reason = "COMPLETED", plat_msg
                    else:
                        # 1 self-debugging retry using exact Guvi judge feedback!
                        code2, _, _ = await synthesize_verified_solution(
                            meta=meta,
                            lang=chosen_lang,
                            starter_code=starter_code,
                            platform_error=f"{plat_msg}\nLocal note: {local_err}",
                            seed_offset=worker_id + 2,
                        )
                        if code2.strip() and code2 != code:
                            final_code = code2
                            # Re-open problem tab cleanly before retry submit (since Submit switched to Submissions view)
                            await page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=45000)
                            await page.wait_for_selector("#editor", timeout=12000)
                            await page.wait_for_timeout(1000)
                            await switch_editor_language_if_needed(page)
                            plat_ok2, plat_msg2 = await submit_code_and_check(page, code2)
                            if plat_ok2:
                                status, reason = "COMPLETED", f"RETRY_{plat_msg2}"
                            else:
                                status, reason = "FAILED_PLATFORM", plat_msg2[:260]
                        else:
                            status, reason = "FAILED_PLATFORM", plat_msg[:260]
                else:
                    status, reason = "FAILED_SYNTHESIS", local_err[:260]

        except Exception as exc:
            status, reason = "ERROR", str(exc)[:260]

        dur = round(time.time() - t0, 2)
        async with lock:
            if status == "COMPLETED" and final_code.strip():
                ext = LANG_EXT.get(chosen_lang, "txt")
                (SOL_DIR / f"{slug}.{ext}").write_text(final_code, encoding="utf-8")

            prev_attempts = results.get(slug, {}).get("attempts", 0)
            results[slug] = {
                "status": status,
                "language": chosen_lang,
                "attempts": prev_attempts + 1,
                "reason": reason,
                "duration_s": dur,
                "difficulty": item.get("difficulty", "Easy"),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            try:
                sm.batch_record_tasks([{
                    "task_id": f"guvi-{slug}",
                    "platform": "guvi",
                    "task_category": "CodeKata",
                    "title": item.get("title", slug),
                    "url": f"https://www.guvi.in/code-kata/{slug}/",
                    "status": TaskStatus.COMPLETED.value if status == "COMPLETED" else TaskStatus.FAILED.value,
                    "attempt_count": prev_attempts + 1,
                    "result": "PASSED" if status == "COMPLETED" else status,
                    "failure_reason": None if status == "COMPLETED" else reason,
                    "next_action": "NONE" if status == "COMPLETED" else "RETRY",
                    "time_spent_seconds": dur,
                    "metadata": {"slug": slug, "language": chosen_lang, "difficulty": item.get("difficulty")},
                }])
            except Exception:
                pass

            done_now = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            processed_now = len(results)
            log(f"[W{worker_id}] {slug} ({chosen_lang}, {dur}s) -> {status} | Solved={done_now} | Processed={processed_now}/{total_catalog} | QueueLeft={queue.qsize()}")

            if processed_now % 10 == 0 or queue.qsize() == 0:
                write_checkpoint(results, total_catalog, start_ts)

        queue.task_done()


async def main() -> int:
    start_ts = time.time()
    num_tabs = int(os.environ.get("CK_TABS", "5"))
    limit = int(os.environ.get("CK_LIMIT", "0"))  # 0 = ALL problems

    for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        p = PROFILE_DIR / lk
        if p.exists() or p.is_symlink():
            try:
                p.unlink()
            except Exception:
                pass

    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    sm = StateManager()

    async with async_playwright() as pw:
        log(f"Launching foreground Brave Browser with {num_tabs} worker tabs...")
        ctx = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=config.BROWSER_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
        )
        subprocess.run(["osascript", "-e", 'tell application "Brave Browser" to activate'], check=False)

        first_tab = ctx.pages[0] if ctx.pages else await ctx.new_page()

        if FULL_CATALOG_JSON.exists() and "--recrawl" not in sys.argv:
            catalog = json.loads(FULL_CATALOG_JSON.read_text(encoding="utf-8"))
            log(f"Loaded cached full catalog ({len(catalog)} problems).")
        else:
            catalog = await crawl_full_catalog(first_tab)

        # Seed already-completed items from catalog into results
        for item in catalog:
            if item.get("completed") and results.get(item["slug"], {}).get("status") != "COMPLETED":
                results[item["slug"]] = {
                    "status": "COMPLETED",
                    "language": "EXISTING",
                    "attempts": 1,
                    "reason": "Completed in catalog",
                    "difficulty": item.get("difficulty", "Easy"),
                    "ts": datetime.now(timezone.utc).isoformat(),
                }

        write_checkpoint(results, len(catalog), start_ts)

        pending_items = [
            item for item in catalog
            if results.get(item["slug"], {}).get("status") != "COMPLETED"
            and results.get(item["slug"], {}).get("status") != "SKIPPED_NO_EDITOR"
        ]
        if limit > 0:
            pending_items = pending_items[:limit]

        log(f"Pending unsolved CodeKata problems queued: {len(pending_items)} (out of {len(catalog)} total)")

        q: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        for it in pending_items:
            q.put_nowait(it)

        tabs = [first_tab] + [await ctx.new_page() for _ in range(max(0, num_tabs - 1))]
        lock = asyncio.Lock()

        await asyncio.gather(
            *(
                worker_loop(idx + 1, tabs[idx], q, results, sm, lock, len(catalog), start_ts)
                for idx in range(len(tabs))
            )
        )

        write_checkpoint(results, len(catalog), start_ts)
        await ctx.storage_state(path=str(config.STORAGE_STATE_PATH))
        await ctx.close()

    solved_total = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    log(f"=== CODEKATA AUTOPILOT COMPLETE: {solved_total}/{len(catalog)} SOLVED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
