"""
single_tab_submitter_brave.py — Zero-GIL Pure Single-Tab Foreground Brave Submitter.

Strictly 1 tab in foreground Brave Browser:
- Uses Chromium C++ --host-resolver-rules to drop 3rd-party ad/analytics domains at 0ms overhead.
- Consumes precomputed solutions from data/ck_precomputed/ immediately (starting at t=0.0s!).
- Also harvests the ~857 Easy problems in the SAME single tab once initial precomputed items are underway,
  writing their specs to data/ck_problems/ for precompute_daemon.py!
- Non-blocking retries: failed platform submissions are written to data/ck_retry_queue/ for background repair.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import Page, sync_playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import config  # noqa: E402
from core.state_manager import StateManager, TaskStatus  # noqa: E402
from turbo_single_tab_brave import (  # noqa: E402
    BRAVE_BINARY,
    EASY_CATALOG_CACHE,
    LANG_EXT,
    LANG_PREFERENCE,
    LIVE_STATUS_JSON,
    PRECOMP_DIR,
    PROB_DIR,
    PROFILE_DIR,
    RESULTS_JSON,
    SOL_DIR,
    solve_problem_offline_sync,
)

RETRY_DIR = ROOT / "data" / "ck_retry_queue"
RETRY_DIR.mkdir(parents=True, exist_ok=True)

FAST_BRAVE_ARGS = list(config.BROWSER_ARGS) + [
    '--host-resolver-rules=MAP *.doubleclick.net 127.0.0.1, MAP *.googleadservices.com 127.0.0.1, MAP *.googletagmanager.com 127.0.0.1, MAP *.google-analytics.com 127.0.0.1, MAP *.clarity.ms 127.0.0.1, MAP bat.bing.com 127.0.0.1, MAP px.ads.linkedin.com 127.0.0.1, MAP web-in21.mxradon.com 127.0.0.1, MAP *.taboola.com 127.0.0.1, MAP *.tapad.com 127.0.0.1',
    '--blink-settings=imagesEnabled=false',
]


def log(msg: str) -> None:
    print(f"[TAB {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_status(results: Dict[str, Any], start_ts: float) -> int:
    RESULTS_JSON.write_text(json.dumps(results, indent=1), encoding="utf-8")
    solved_cnt = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
    other_cnt = sum(1 for v in results.values() if v.get("status") not in ("COMPLETED", None))
    elapsed_m = max((time.time() - start_ts) / 60.0, 0.05)
    LIVE_STATUS_JSON.write_text(
        json.dumps(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "verified_solved_total": solved_cnt,
                "other_attempted": other_cnt,
                "solve_rate_per_min": round(solved_cnt / elapsed_m, 1),
                "elapsed_minutes": round(elapsed_m, 1),
                "precomputed_ready_files": len(list(PRECOMP_DIR.glob("*.json"))),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return solved_cnt


def switch_lang_sync(page: Page, desired_lang: str) -> Tuple[str, str]:
    try:
        page.wait_for_function(
            "() => (document.querySelector('select#editorModeSelectDesktop')?.options?.length || 0) > 0",
            timeout=1800,
        )
    except Exception:
        pass
    info = page.evaluate(
        """() => {
            const sel = document.querySelector('select#editorModeSelectDesktop');
            const opts = sel && sel.options.length ? Array.from(sel.options).map(o => o.value) : ['PYTHON 3'];
            const current = sel && sel.value ? sel.value : 'PYTHON 3';
            let starter = '';
            try { if (window.ace) starter = window.ace.edit('editor').getValue() || ''; } catch (e) {}
            return { current, opts, dataId: sel?.getAttribute('data-id') || '', starter };
        }"""
    )
    opts = info["opts"] or ["PYTHON 3"]
    chosen = desired_lang if desired_lang in opts else next((lp for lp in LANG_PREFERENCE if lp in opts), opts[0])

    if info["current"] != chosen and info["dataId"]:
        did = info["dataId"]
        ss_main = page.locator(f'.ss-main[data-id="{did}"]').first
        if ss_main.count() > 0 and ss_main.is_visible():
            ss_main.click(force=True)
            page.wait_for_timeout(120)
            opt_loc = page.locator(f'.ss-content[data-id="{did}"] .ss-option').filter(
                has_text=re.compile(f"^{re.escape(chosen)}$")
            ).first
            if opt_loc.count() > 0:
                opt_loc.click(force=True)
                page.wait_for_timeout(180)
                page.evaluate(
                    """() => {
                        const noBtn = Array.from(document.querySelectorAll('dialog button, .modal button')).find(
                            b => b.textContent.trim() === 'No' && b.offsetParent !== null
                        );
                        if (noBtn) noBtn.click();
                    }"""
                )
    starter = page.evaluate(
        "() => { try { return window.ace ? (window.ace.edit('editor').getValue() || '') : ''; } catch (e) { return ''; } }"
    )
    return chosen, starter


def submit_and_poll_sync(page: Page, code: str) -> Tuple[bool, str]:
    page.evaluate(
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
    page.locator("button.submit-code, button:has-text('Submit'):not(.submit-button)").first.click(force=True)
    page.wait_for_timeout(320)

    for _ in range(115):
        page.wait_for_timeout(120)
        verdict = page.evaluate(
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


def harvest_easy_list_sync(page: Page) -> List[Dict[str, Any]]:
    if EASY_CATALOG_CACHE.exists():
        return json.loads(EASY_CATALOG_CACHE.read_text(encoding="utf-8"))

    log("Harvesting Easy catalog in the same single tab (~15s)...")
    page.goto("https://www.guvi.in/code-kata/", wait_until="domcontentloaded", timeout=35000)
    page.wait_for_timeout(1800)
    page.evaluate("() => { for (const b of document.querySelectorAll('button')) if (b.innerText.trim() === '✕' || b.innerText.trim() === 'Finish') b.click(); }")
    try:
        did = page.evaluate("() => document.querySelector('select#itemsPerPage')?.getAttribute('data-id') || ''")
        if did:
            page.locator(f'.ss-main[data-id="{did}"]').first.click(force=True)
            page.wait_for_timeout(150)
            page.locator(f'.ss-content[data-id="{did}"] .ss-option', has_text="50").first.click(force=True)
            page.wait_for_timeout(1000)
        page.locator("#difficulty-filter-id").first.click(force=True)
        page.wait_for_timeout(200)
        page.locator("li.difficulty-filter-option:has-text('Easy')").first.click(force=True)
        page.wait_for_timeout(1200)
    except Exception:
        pass

    easy_map: Dict[str, Dict[str, Any]] = {}
    seen_fp = set()
    for _ in range(65):
        rows = page.evaluate(
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
            easy_map[sl] = {"slug": sl, "title": r["title"], "difficulty": "Easy", "completed": bool(r["completed"])}
        nxt = page.locator('button[aria-label="Go to next page"], button:has-text("Go to next page")').first
        if nxt.count() == 0 or nxt.get_attribute("disabled") is not None:
            break
        nxt.click(force=True)
        page.wait_for_timeout(450)

    items = list(easy_map.values())
    EASY_CATALOG_CACHE.write_text(json.dumps(items, indent=1), encoding="utf-8")
    log(f"Harvested {len(items)} Easy items!")
    return items


EASY_SLUGS_SET: set = set()


def _get_easy_slugs() -> set:
    global EASY_SLUGS_SET
    if not EASY_SLUGS_SET and EASY_CATALOG_CACHE.exists():
        try:
            EASY_SLUGS_SET = {x["slug"] for x in json.loads(EASY_CATALOG_CACHE.read_text(encoding="utf-8"))}
        except Exception:
            pass
    return EASY_SLUGS_SET


def next_ready_candidate(results: Dict[str, Any], tried_files: set) -> Optional[Tuple[Path, Dict[str, Any]]]:
    easy_set = _get_easy_slugs()
    # Prefer Easy precomputed solutions & retry repairs first for maximum solve velocity!
    files = sorted(
        PRECOMP_DIR.glob("*.json"),
        key=lambda p: (
            0 if p.stem.split("__")[0] in easy_set else 1,
            0 if "__retry" in p.name else 1,
            p.name,
        ),
    )
    for fp in files:
        if fp.name in tried_files:
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        slug = data.get("slug") or (fp.stem.split("__")[0] if "__" in fp.stem else "")
        if not slug:
            tried_files.add(fp.name)
            continue
        if not data.get("lang") and "__" in fp.stem:
            data["lang"] = fp.stem.split("__")[1].replace("_", " ")
        if results.get(slug, {}).get("status") in ("COMPLETED", "SKIPPED_NO_EDITOR"):
            tried_files.add(fp.name)
            continue
        if results.get(slug, {}).get("attempts", 0) >= 2 and "__retry" not in fp.name:
            tried_files.add(fp.name)
            continue
        return fp, data
    return None


def main() -> int:
    start_ts = time.time()
    target_solved = int(os.environ.get("CK_TARGET", "1200"))

    # Cleanly terminate any stray Chromium still holding .browser_profile before starting
    subprocess.run(["pkill", "-f", str(PROFILE_DIR)], check=False)
    time.sleep(0.8)
    for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        p = PROFILE_DIR / lk
        if p.exists() or p.is_symlink():
            try:
                p.unlink()
            except Exception:
                pass

    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    sm = StateManager()
    tried_files: set = set()
    easy_queue: List[Dict[str, Any]] = []
    easy_harvested = False
    processed = 0

    with sync_playwright() as pw:
        log("Opening foreground Brave Browser (1 Window, STRICTLY 1 TAB, Zero-GIL C++ Tracker Block)...")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=FAST_BRAVE_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
        )
        subprocess.run(["osascript", "-e", 'tell application "Brave Browser" to activate'], check=False)

        pages = list(ctx.pages)
        page = pages[0] if pages else ctx.new_page()
        for ep in pages[1:]:
            try:
                ep.close()
            except Exception:
                pass

        while True:
            solved_cnt = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            if solved_cnt >= target_solved:
                log(f"TARGET REACHED: {solved_cnt} solved >= {target_solved}!")
                break

            cand = next_ready_candidate(results, tried_files)

            # If precomputed buffer is temporarily empty, either harvest Easy problems or solve 1 Easy item live
            if cand is None:
                if not easy_harvested:
                    easy_harvested = True
                    easy_list = harvest_easy_list_sync(page)
                    for e in easy_list:
                        if e.get("completed"):
                            results.setdefault(e["slug"], {"status": "COMPLETED", "language": "EXISTING", "attempts": 1})
                        elif results.get(e["slug"], {}).get("status") not in ("COMPLETED", "SKIPPED_NO_EDITOR"):
                            easy_queue.append(e)
                    save_status(results, start_ts)
                    continue

                if easy_queue:
                    e_item = easy_queue.pop(0)
                    slug = e_item["slug"]
                    if results.get(slug, {}).get("status") == "COMPLETED":
                        continue
                    cand_data = {"slug": slug, "lang": "PYTHON 3", "code": "", "live_easy": True, "meta_stub": e_item}
                    cand_fp = None
                else:
                    # Wait briefly for precompute_daemon to emit remaining items/retries
                    time.sleep(1.5)
                    cand2 = next_ready_candidate(results, tried_files)
                    if cand2 is None:
                        log("All precomputed & Easy items exhausted!")
                        break
                    cand_fp, cand_data = cand2
            else:
                cand_fp, cand_data = cand

            if cand_fp is not None:
                tried_files.add(cand_fp.name)

            slug = cand_data["slug"]
            code = cand_data.get("code", "")
            wanted_lang = cand_data.get("lang", "PYTHON 3")
            is_retry = bool(cand_data.get("retry"))
            t0 = time.time()
            status = "FAILED"
            reason = ""
            chosen_lang = wanted_lang

            # Keep strictly 1 tab!
            for ep in list(ctx.pages):
                if ep != page and not ep.is_closed():
                    try:
                        ep.close()
                    except Exception:
                        pass

            try:
                page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=25000)
                try:
                    page.wait_for_selector("#editor", timeout=6500)
                except Exception:
                    results[slug] = {"status": "SKIPPED_NO_EDITOR", "attempts": 1, "ts": datetime.now(timezone.utc).isoformat()}
                    continue

                page.wait_for_function("() => Boolean(window.ace || document.querySelector('#editor')?.env?.editor)", timeout=5000)

                already = page.evaluate(
                    "() => Boolean(document.querySelector('.question-status')?.textContent?.toLowerCase()?.includes('solved'))"
                )
                if already:
                    status, reason = "COMPLETED", "Already solved"
                else:
                    chosen_lang, starter_code = switch_lang_sync(page, wanted_lang)
                    pfile = PROB_DIR / f"{slug}.json"
                    meta = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else cand_data.get("meta_stub", {"slug": slug, "title": slug})

                    if not meta.get("description") or cand_data.get("live_easy"):
                        raw_dom = page.evaluate(
                            "() => (document.querySelector('.problem-description, #problem-description, .question-content, main')?.innerText || document.body.innerText).slice(0, 3500)"
                        )
                        samples = []
                        si_m = re.search(r"Sample Input\s*:?\s*\n(.*?)(?:\n\s*Sample Output|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
                        so_m = re.search(r"Sample Output\s*:?\s*\n(.*?)(?:\n\s*(?:Explanation|Note|Constraints|Hint)|\Z)", raw_dom, flags=re.DOTALL | re.IGNORECASE)
                        if si_m and so_m:
                            samples.append({"input": si_m.group(1).strip(), "output": so_m.group(1).strip().split("\n\n")[0].strip()})
                        meta = {**meta, "slug": slug, "description": raw_dom, "samples": samples, "raw": raw_dom}
                        pfile.write_text(json.dumps(meta, indent=1), encoding="utf-8")

                    if chosen_lang != wanted_lang or not code.strip():
                        code, _, _ = solve_problem_offline_sync(meta, chosen_lang, starter_code, "", processed + 3)

                    if code.strip():
                        ok, msg = submit_and_poll_sync(page, code)
                        if ok:
                            status, reason = "COMPLETED", msg
                        else:
                            status, reason = "FAILED_PLATFORM", msg[:240]
                            # Queue non-blocking background repair if first failure
                            if not is_retry and results.get(slug, {}).get("attempts", 0) < 2:
                                (RETRY_DIR / f"{slug}.json").write_text(
                                    json.dumps({"meta": meta, "lang": chosen_lang, "starter_code": starter_code, "plat_err": msg}),
                                    encoding="utf-8",
                                )
                    else:
                        status, reason = "FAILED_SYNTHESIS", "Empty code"

            except Exception as exc:
                es = str(exc)
                if "Target page, context or browser has been closed" in es:
                    log("Single Brave tab closed by user — saving checkpoint cleanly.")
                    save_status(results, start_ts)
                    return 1
                status, reason = "ERROR", es[:200]

            dur = round(time.time() - t0, 2)
            processed += 1
            prev_att = results.get(slug, {}).get("attempts", 0)
            results[slug] = {
                "status": status,
                "language": chosen_lang,
                "attempts": prev_att + 1,
                "reason": reason,
                "duration_s": dur,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if status == "COMPLETED" and code.strip():
                ext = LANG_EXT.get(chosen_lang, "txt")
                (SOL_DIR / f"{slug}.{ext}").write_text(code, encoding="utf-8")

            solved_now = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
            log(f"[#{processed}] {slug} ({chosen_lang}, {dur}s) -> {status} | SOLVED={solved_now}/{target_solved}")

            if processed % 10 == 0:
                save_status(results, start_ts)
                try:
                    sm.batch_record_tasks([{
                        "task_id": f"guvi-{slug}",
                        "platform": "guvi",
                        "task_category": "CodeKata",
                        "title": slug,
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

        final_solved = save_status(results, start_ts)
        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))
        ctx.close()

    log(f"=== SINGLE-TAB RUN COMPLETE: {final_solved} VERIFIED SOLVED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
