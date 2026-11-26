"""
scrape_easy_and_testcases.py — Fast Parallel HTTP SSR Scraper for Easy Catalog + Public Test Cases.

Uses zero browser tabs (pure urllib HTTP GET against GUVI's Qwik SSR HTML) to:
1. Scrape all ~810 unsolved Easy problem specs from data/ck_easy_catalog.json into data/ck_problems/<slug>.json.
2. Extract BOTH Sample Input/Output AND the extra public Case 1 / Case 2 / Case 3 test cases embedded in SSR HTML,
   dramatically increasing local compiler verification accuracy (especially on pattern & formatting problems).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import html as html_lib
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List
import urllib.request

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
EASY_CATALOG = ROOT / "data" / "ck_easy_catalog.json"
PROB_DIR = ROOT / "data" / "ck_problems"
PROB_DIR.mkdir(parents=True, exist_ok=True)


def parse_ssr_problem(slug: str, title: str, difficulty: str, raw_html: str) -> Dict[str, Any]:
    cleaned = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw_html, flags=re.DOTALL | re.IGNORECASE)
    txt = html_lib.unescape(re.sub(r"<[^>]+>", "\n", cleaned))
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt).strip()

    ps_idx = txt.find("Problem Statement")
    if ps_idx == -1:
        ps_idx = txt.find("Input Description")
    con_idx = txt.find("Accepted\n", ps_idx if ps_idx != -1 else 0)
    desc_block = txt[max(0, ps_idx - 80):(con_idx if con_idx != -1 else ps_idx + 2800)] if ps_idx != -1 else txt[:2800]

    in_m = re.search(r"Input Description\s*:?\s*\n(.*?)(?:\nOutput Description|\nSample Input|\Z)", desc_block, flags=re.DOTALL | re.IGNORECASE)
    out_m = re.search(r"Output Description\s*:?\s*\n(.*?)(?:\nSample Input|\nConstraints|\Z)", desc_block, flags=re.DOTALL | re.IGNORECASE)
    si_m = re.search(r"Sample Input\s*:?\s*\n(.*?)(?:\nSample Output|\Z)", desc_block, flags=re.DOTALL | re.IGNORECASE)
    so_m = re.search(r"Sample Output\s*:?\s*\n(.*?)(?:\n(?:Explanation|Note|Constraints|Hint|Accepted)|\Z)", desc_block, flags=re.DOTALL | re.IGNORECASE)

    samples: List[Dict[str, str]] = []
    seen_pairs = set()
    if si_m and so_m:
        inp0 = si_m.group(1).strip()
        out0 = so_m.group(1).strip()
        if inp0 or out0:
            samples.append({"input": inp0, "output": out0})
            seen_pairs.add((inp0, out0))

    # Extract extra public Case 1 / Case 2 / Case 3 blocks from SSR "Test Case ... Console" section
    tc_m = re.search(r"Test Case\s*\nTest Result\s*\n(.*?)\nConsole", txt, flags=re.DOTALL)
    if tc_m:
        tc_body = tc_m.group(1)
        pairs = re.findall(r"(?:^|\n)Input\n(.*?)\nOutput\n(.*?)(?=\nInput\n|\Z)", tc_body, flags=re.DOTALL)
        for p_in, p_out in pairs:
            p_in_s, p_out_s = p_in.strip(), p_out.strip()
            if (p_in_s, p_out_s) not in seen_pairs and (p_in_s or p_out_s):
                samples.append({"input": p_in_s, "output": p_out_s})
                seen_pairs.add((p_in_s, p_out_s))

    return {
        "title": title,
        "slug": slug,
        "difficulty": difficulty,
        "completed": False,
        "description": desc_block,
        "input_spec": in_m.group(1).strip() if in_m else "",
        "output_spec": out_m.group(1).strip() if out_m else "",
        "constraints": "",
        "samples": samples[:5],
        "raw": "",
    }


def fetch_and_save(item: Dict[str, Any], force_enrich: bool = False) -> bool:
    slug = item["slug"]
    out_p = PROB_DIR / f"{slug}.json"
    if out_p.exists() and not force_enrich:
        try:
            cur = json.loads(out_p.read_text(encoding="utf-8"))
            if cur.get("description") and len(cur.get("samples") or []) >= 2:
                return True
        except Exception:
            pass

    url = f"https://www.guvi.in/code-kata/{slug}/"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw_html = resp.read().decode("utf-8", errors="ignore")
            parsed = parse_ssr_problem(slug, item.get("title", slug), item.get("difficulty", "Easy"), raw_html)
            if parsed["description"]:
                tmp = out_p.with_suffix(".stmp")
                tmp.write_text(json.dumps(parsed, indent=1), encoding="utf-8")
                tmp.replace(out_p)
                return True
        except Exception:
            time.sleep(0.3 * (attempt + 1))
    return False


def main() -> int:
    t0 = time.time()
    easy_items = json.loads(EASY_CATALOG.read_text(encoding="utf-8")) if EASY_CATALOG.exists() else []
    todo_easy = [x for x in easy_items if not x.get("completed")]
    print(f"[SSR-SCRAPE] Scraping {len(todo_easy)} Easy problem specs + multi-case tests across 24 threads...", flush=True)

    ok_cnt = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = [ex.submit(fetch_and_save, it, False) for it in todo_easy]
        for idx, f in enumerate(as_completed(futs), start=1):
            if f.result():
                ok_cnt += 1
            if idx % 200 == 0 or idx == len(todo_easy):
                print(f"[SSR-SCRAPE] Easy progress: {idx}/{len(todo_easy)} (ok={ok_cnt}, {time.time()-t0:.1f}s)", flush=True)

    # Also enrich pattern / single-sample Medium problems so they have >=2 test cases
    med_candidates = []
    for pf in sorted(PROB_DIR.glob("*.json")):
        try:
            d = json.loads(pf.read_text(encoding="utf-8"))
            if len(d.get("samples") or []) < 2 and d.get("difficulty") != "Easy":
                med_candidates.append({"slug": d.get("slug") or pf.stem, "title": d.get("title", pf.stem), "difficulty": d.get("difficulty", "Medium")})
        except Exception:
            pass

    print(f"[SSR-SCRAPE] Enriching {len(med_candidates)} single-sample Medium/Hard problems with extra SSR test cases...", flush=True)
    enr_ok = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = [ex.submit(fetch_and_save, it, True) for it in med_candidates]
        for idx, f in enumerate(as_completed(futs), start=1):
            if f.result():
                enr_ok += 1
            if idx % 300 == 0 or idx == len(med_candidates):
                print(f"[SSR-SCRAPE] Enrich progress: {idx}/{len(med_candidates)} (ok={enr_ok}, {time.time()-t0:.1f}s)", flush=True)

    print(f"[SSR-SCRAPE] DONE in {time.time()-t0:.1f}s! Total problem specs on disk: {len(list(PROB_DIR.glob('*.json')))}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
