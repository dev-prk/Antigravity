"""
submit_final_ck_repairs.py — Fast Single-Tab Submitter for Opus/Sonnet 2-Candidate CodeKata Repairs + Final Live Sweep.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time
from typing import Any, Dict

from playwright.sync_api import sync_playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT / "scripts"))
from kata_common import enforce_single_tab, open_single_brave_tab  # noqa: E402
from solve_codekata_100_python import (  # noqa: E402
    LANG_EXT,
    RESULTS_JSON,
    SOL_DIR,
    save_ck_status,
    select_python_or_locked,
    submit_and_check,
    sweep_live_status_filter,
    synthesize_or_repair,
    PROB_DIR,
)

FINAL_DIR = ROOT / "data" / "ck_final_repairs_v2"


def log(msg: str) -> None:
    print(f"[FINAL-CK {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> int:
    start_ts = time.time()
    results: Dict[str, Any] = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    rfiles = sorted(FINAL_DIR.glob("*.json"))
    log(f"Submitting {len(rfiles)} deep-repaired CodeKata items in 1 foreground Brave tab...")

    with sync_playwright() as pw:
        ctx, page = open_single_brave_tab(pw, disable_images=True)
        try:
            for idx, rf in enumerate(rfiles, start=1):
                enforce_single_tab(ctx, page)
                data = json.loads(rf.read_text(encoding="utf-8"))
                slug = data["slug"]
                if results.get(slug, {}).get("status") == "COMPLETED":
                    continue
                t0 = time.time()
                page.goto(f"https://www.guvi.in/code-kata/{slug}/", wait_until="domcontentloaded", timeout=25000)
                try:
                    page.wait_for_selector("#editor", timeout=5500)
                    page.wait_for_function("() => Boolean(window.ace)", timeout=4000)
                except Exception:
                    continue

                if page.evaluate("() => Boolean(document.querySelector('.question-status')?.innerText?.toLowerCase()?.includes('solved'))"):
                    results[slug] = {"status": "COMPLETED", "language": "PYTHON 3", "attempts": 1}
                    continue

                lang, starter = select_python_or_locked(page)
                cands = data.get("candidates") or []
                if lang != data.get("lang"):
                    pfile = PROB_DIR / f"{slug}.json"
                    meta = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else {}
                    prob_t = meta.get("description") or page.evaluate("() => (document.querySelector('main')?.textContent || document.body.innerText).slice(0, 2800)")
                    cands = [synthesize_or_repair(lang, prob_t, starter, meta.get("samples") or [], "", idx)]

                solved = False
                last_msg = ""
                for c_idx, code in enumerate(cands):
                    if not code.strip():
                        continue
                    ok, msg = submit_and_check(page, code)
                    last_msg = msg
                    if ok:
                        solved = True
                        ext = LANG_EXT.get(lang, "py")
                        (SOL_DIR / f"{slug}.{ext}").write_text(code, encoding="utf-8")
                        results[slug] = {"status": "COMPLETED", "language": lang, "attempts": c_idx + 1, "reason": msg, "duration_s": round(time.time() - t0, 2)}
                        break

                if not solved:
                    results[slug] = {"status": "FAILED_PLATFORM", "language": lang, "attempts": len(cands), "reason": last_msg[:220], "duration_s": round(time.time() - t0, 2)}

                tot = sum(1 for v in results.values() if v.get("status") == "COMPLETED")
                log(f"[{idx}/{len(rfiles)}] {slug} ({lang}) -> {'SOLVED' if solved else 'FAILED'} | SOLVED={tot}")
                if idx % 8 == 0:
                    save_ck_status(results, start_ts)

            # Final check for any remaining `Yet to start` items
            seq_ref = [len(rfiles)]
            sweep_live_status_filter(ctx, page, "Yet to start", results, start_ts, seq_ref)
        finally:
            final_tot = save_ck_status(results, start_ts)
            ctx.close()

    log(f"=== FINAL CODEKATA REPAIR SWEEP COMPLETE: {final_tot} SOLVED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
