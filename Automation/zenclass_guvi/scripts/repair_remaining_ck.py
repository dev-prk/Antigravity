"""
repair_remaining_ck.py — Deep 2-Candidate Background Pre-Solver for the Final ~321 Unsolved CodeKata Items.

Uses FreeLLMAPI's top reasoning models (claude-sonnet-4-5, claude-opus-4-5, fusion, gpt-oss-120b — $0 free pool)
to generate up to 2 locally-verified candidate solutions per remaining CodeKata problem while the foreground
Brave tab completes FixTheCode, SQLKata, and WebKata.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT / "scripts"))
from kata_common import call_llm, strip_fences, verify_code_locally  # noqa: E402
from precompute_python_remaining import fetch_exact_ssr_samples  # noqa: E402

PROB_DIR = ROOT / "data" / "ck_problems"
RESULTS_JSON = ROOT / "data" / "ck_results.json"
FINAL_DIR = ROOT / "data" / "ck_final_repairs"
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[DEEP-CK {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def repair_one(slug: str, prev_info: Dict[str, Any], seed: int) -> bool:
    out_f = FINAL_DIR / f"{slug}.json"
    if out_f.exists():
        return True

    # Prefer PYTHON 3 unless previous live run proved this problem locked out Python
    prev_lang = prev_info.get("language", "PYTHON 3")
    target_lang = prev_lang if prev_lang not in ("PYTHON 3", "PY3", "EXISTING", "", None) else "PYTHON 3"

    pfile = PROB_DIR / f"{slug}.json"
    meta = json.loads(pfile.read_text(encoding="utf-8")) if pfile.exists() else {"slug": slug, "title": slug}
    exact_s = fetch_exact_ssr_samples(slug)
    samples = exact_s if exact_s else (meta.get("samples") or [])
    prev_reason = str(prev_info.get("reason", ""))

    samples_txt = "\n".join(
        f"Test Case {i+1}:\nInput:\n{s.get('input','')}\nExact Expected Output (repr={s.get('output','')!r}):\n{s.get('output','')}"
        for i, s in enumerate(samples[:4])
    )
    lang_rule = (
        "Write a complete standalone Python 3 program reading from sys.stdin and printing exact output to sys.stdout."
        if target_lang.startswith("PYTHON")
        else f"Write a complete standalone {target_lang} program reading stdin and printing exact stdout."
    )
    if target_lang in ("JAVA", "JAVA 8"):
        lang_rule += " Use `public class Main` with `public static void main(String[] args)`."

    sys_1 = (
        f"Senior ICPC / GUVI CodeKata problem setter ({target_lang}). {lang_rule}\n"
        "Output ONLY raw code. Carefully analyze why a naive solution fails hidden GUVI test cases:\n"
        "- Empty output when nothing matches -> GUVI almost always expects `-1`!\n"
        "- Exact pyramid/pattern leading spaces vs single spaces between tokens (check repr of Expected Output!).\n"
        "- Duplicate elements, negative integers, N=0/N=1, 0-based vs 1-based indexing, float formatting/truncation."
    )
    user_p = (
        f"Problem: {meta.get('title', slug)} ({meta.get('difficulty', '')})\n\n"
        f"{(meta.get('description') or meta.get('raw') or '')[:2800]}\n\n"
        f"Input Spec: {meta.get('input_spec', '')}\nOutput Spec: {meta.get('output_spec', '')}\n\n"
        f"{samples_txt}\n\n"
        f"PREVIOUS FAILED SUBMISSION DETAILS:\n{prev_reason[:600]}\n"
    )

    candidates: List[str] = []
    for variant_idx, extra_focus in enumerate([
        "Focus on exact problem definition, '-1' edge cases, and exact whitespace matching.",
        "Provide an alternative interpretation if the wording is ambiguous (e.g. strict vs non-strict comparison, truncation vs rounding, all occurrences vs consecutive duplicates) that STILL passes all provided Test Cases!",
    ]):
        p_txt = f"{user_p}\nStrategy hint: {extra_focus}"
        for tr in range(2):
            raw = call_llm(sys_1, p_txt, seed + variant_idx * 2 + tr)
            if not raw:
                continue
            code = strip_fences(raw)
            ok, lerr = verify_code_locally(code, target_lang, samples)
            if ok:
                if code not in candidates:
                    candidates.append(code)
                break
            p_txt = f"{user_p}\nLocal check failed:\n{lerr}\nFix and output ONLY {target_lang} code."

    if candidates:
        tmp = out_f.with_suffix(".tmp")
        tmp.write_text(json.dumps({"slug": slug, "lang": target_lang, "candidates": candidates}), encoding="utf-8")
        tmp.replace(out_f)
        return True
    return False


def main() -> int:
    res = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
    todo = [
        (slug, info)
        for slug, info in sorted(res.items())
        if info.get("status") not in ("COMPLETED", "SKIPPED_NO_EDITOR") and slug != "code-kata"
    ]
    log(f"Deep-solving {len(todo)} remaining CodeKata problems with Opus/Sonnet/Fusion (3 workers)...")
    with ThreadPoolExecutor(max_workers=3) as ex:
        for b in range(0, len(todo), 9):
            chunk = todo[b:b + 9]
            futs = [ex.submit(repair_one, s, inf, b + i) for i, (s, inf) in enumerate(chunk)]
            done_f, _ = wait(futs, timeout=90)
            ok_c = sum(1 for f in done_f if f.result())
            log(f"Progress {min(b+9, len(todo))}/{len(todo)} (+{ok_c}) | Ready in ck_final_repairs: {len(list(FINAL_DIR.glob('*.json')))}")
            time.sleep(0.5)
    log("All remaining CodeKata deep repairs finished!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
