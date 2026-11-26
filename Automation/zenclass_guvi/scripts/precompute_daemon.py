"""
precompute_daemon.py — High-Throughput Separate OS Process Pre-Computing CodeKata Solutions.

Runs with 24 worker threads on FreeLLMAPI ($0 free pool) + local python3/clang/clang++/node verification,
continuously feeding data/ck_precomputed/ (Easy -> Medium -> Hard + background retries) with zero GIL impact
on the single foreground Brave tab.
"""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT / "scripts"))
from turbo_single_tab_brave import (  # noqa: E402
    PRECOMP_DIR,
    PROB_DIR,
    RESULTS_JSON,
    guess_initial_language,
    solve_problem_offline_sync,
)

RETRY_DIR = ROOT / "data" / "ck_retry_queue"
RETRY_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[PRECOMPUTE {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def process_one(meta: Dict[str, Any], seed: int) -> bool:
    slug = meta["slug"]
    lang = guess_initial_language(meta)
    out_file = PRECOMP_DIR / f"{slug}__{lang.replace(' ', '_')}.json"
    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            if existing.get("slug") and existing.get("code") and existing.get("local_ok"):
                return True
        except Exception:
            pass

    code, local_ok, err = solve_problem_offline_sync(meta, lang, "", "", seed)
    if code.strip():
        tmp = out_file.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"slug": slug, "lang": lang, "code": code, "local_ok": local_ok, "err": err[:200]}),
            encoding="utf-8",
        )
        tmp.replace(out_file)
        return True
    return False


def drain_retries(executor: ThreadPoolExecutor) -> int:
    retry_files = sorted(RETRY_DIR.glob("*.json"))
    if not retry_files:
        return 0
    futs = []
    for rf in retry_files[:32]:
        try:
            payload = json.loads(rf.read_text(encoding="utf-8"))
            rf.unlink()
        except Exception:
            continue

        def _do_retry(p=payload):
            meta = p["meta"]
            lang = p["lang"]
            err = p.get("plat_err", "")
            code, local_ok, _ = solve_problem_offline_sync(meta, lang, p.get("starter_code", ""), err, int(time.time()) % 97)
            if code.strip():
                out = PRECOMP_DIR / f"{meta['slug']}__{lang.replace(' ', '_')}__retry.json"
                tmp = out.with_suffix(".tmp")
                tmp.write_text(
                    json.dumps({"slug": meta["slug"], "lang": lang, "code": code, "local_ok": local_ok, "retry": True}),
                    encoding="utf-8",
                )
                tmp.replace(out)

        futs.append(executor.submit(_do_retry))
    if futs:
        wait(futs, timeout=45)
    return len(futs)


def load_results() -> Dict[str, Any]:
    if not RESULTS_JSON.exists():
        return {}
    try:
        return json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    workers = int(os.environ.get("CK_PRE_WORKERS", "24"))
    log(f"Starting upgraded precompute_daemon with {workers} threads...")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for pass_no in range(12):
            drain_retries(ex)
            results = load_results()
            metas = []
            for pf in PROB_DIR.glob("*.json"):
                try:
                    d = json.loads(pf.read_text(encoding="utf-8"))
                    slug = d.get("slug") or pf.stem
                    d["slug"] = slug
                    if results.get(slug, {}).get("status") in ("COMPLETED", "SKIPPED_NO_EDITOR"):
                        continue
                    lang = guess_initial_language(d)
                    out_f = PRECOMP_DIR / f"{slug}__{lang.replace(' ', '_')}.json"
                    if out_f.exists():
                        continue
                    metas.append(d)
                except Exception:
                    continue

            metas.sort(
                key=lambda m: (
                    0 if m.get("difficulty") == "Easy" else (1 if m.get("difficulty") == "Medium" else 2),
                    0 if len(m.get("samples") or []) >= 2 else (1 if m.get("samples") else 2),
                    len(m.get("description") or ""),
                )
            )
            if not metas and not list(RETRY_DIR.glob("*.json")):
                time.sleep(4.0)
                continue

            log(f"Pass {pass_no+1}: Pre-solving {len(metas)} problems (Easy first) across {workers} threads...")
            batch_size = 72
            for b_start in range(0, len(metas), batch_size):
                drain_retries(ex)
                # Re-check if newly scraped Easy problems arrived on disk!
                if pass_no == 0 and b_start > 0 and b_start % 144 == 0:
                    easy_ready_specs = sum(1 for p in PROB_DIR.glob("*.json") if p.stat().st_mtime > time.time() - 40)
                    if easy_ready_specs > 30:
                        log(f"Detected {easy_ready_specs} freshly scraped Easy specs — re-sorting queue to prioritize Easy!")
                        break

                chunk = metas[b_start:b_start + batch_size]
                futs = {ex.submit(process_one, m, b_start + i): m["slug"] for i, m in enumerate(chunk)}
                done_futs, pending_futs = wait(futs.keys(), timeout=42)
                done_b = 0
                for f in done_futs:
                    try:
                        if f.result():
                            done_b += 1
                    except Exception:
                        pass
                total_ready = len(list(PRECOMP_DIR.glob("*.json")))
                log(f"Batch +{done_b}/{len(chunk)} ready (pending={len(pending_futs)}) | Total precomputed on disk: {total_ready}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
