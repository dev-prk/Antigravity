"""
precompute_python_remaining.py — Background $0 FreeLLMAPI Pre-Solver for Remaining CodeKata Problems (Strictly PYTHON 3).

1. Re-fetches exact whitespace-preserved <pre>/test-case blocks from SSR HTML for unsolved CodeKata problems
   (fixing the leading-space pyramid bug where earlier scraping stripped leading spaces!).
2. Synthesizes & locally verifies PYTHON 3 solutions across 4 gentle worker threads (zero 429 contention),
   writing to data/ck_py_precomputed/<slug>.json.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait
import html as html_lib
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List
import urllib.request

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT / "scripts"))
from kata_common import call_llm, strip_fences, verify_code_locally  # noqa: E402

PROB_DIR = ROOT / "data" / "ck_problems"
RESULTS_JSON = ROOT / "data" / "ck_results.json"
PY_PRE_DIR = ROOT / "data" / "ck_py_precomputed"
REPAIR_QUEUE_DIR = ROOT / "data" / "ck_repair_queue"
PY_PRE_DIR.mkdir(parents=True, exist_ok=True)
REPAIR_QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"[PY-PRE {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch_exact_ssr_samples(slug: str) -> List[Dict[str, str]]:
    """Extracts Case 1/2/3 Input/Output from SSR HTML WITHOUT collapsing or stripping leading spaces."""
    try:
        req = urllib.request.Request(f"https://www.guvi.in/code-kata/{slug}/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    cleaned = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
    # Replace block tags with newlines but NEVER collapse horizontal spaces!
    txt = html_lib.unescape(re.sub(r"<[^>]+>", "\n", cleaned)).replace("\r\n", "\n").replace("\r", "\n")

    samples: List[Dict[str, str]] = []
    tc_m = re.search(r"Test Case\s*\n+Test Result\s*\n+(.*?)\n+Console", txt, flags=re.DOTALL)
    if tc_m:
        tc_body = tc_m.group(1)
        pairs = re.findall(r"(?:^|\n)\s*Input\s*\n(.*?)\n\s*Output\s*\n(.*?)(?=\n\s*Input\s*\n|\Z)", tc_body, flags=re.DOTALL)
        for p_in, p_out in pairs:
            in_lines = p_in.strip("\n").split("\n")
            out_lines = p_out.strip("\n").split("\n")
            in_s = "\n".join(ln.rstrip() for ln in in_lines)
            out_s = "\n".join(ln.rstrip() for ln in out_lines)
            if in_s or out_s:
                samples.append({"input": in_s, "output": out_s})
    return samples[:4]


def solve_one_python(meta: Dict[str, Any], prev_reason: str, seed: int) -> bool:
    slug = meta["slug"]
    out_file = PY_PRE_DIR / f"{slug}.json"
    if out_file.exists():
        return True

    exact_samples = fetch_exact_ssr_samples(slug)
    samples = exact_samples if exact_samples else (meta.get("samples") or [])
    if exact_samples:
        meta["samples"] = exact_samples
        try:
            (PROB_DIR / f"{slug}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        except Exception:
            pass

    samples_repr = "\n".join(
        f"Test Case {i+1}:\nInput:\n{s.get('input','')}\nExact Expected Output (repr={s.get('output','')!r}):\n{s.get('output','')}"
        for i, s in enumerate(samples[:4])
    )
    prev_hint = f"\nNOTE: Previous attempt failed on GUVI with: {prev_reason[:260]}\nCheck boundary cases, exact leading/trailing spaces, '-1' when not found, and float formatting!\n" if prev_reason else ""

    sys_p = (
        "Expert Python 3 competitive programmer for GUVI CodeKata.\n"
        "Write a complete standalone Python 3 program reading from sys.stdin and writing exact output to sys.stdout.\n"
        "CRITICAL RULES:\n"
        "1. Output ONLY raw Python 3 code (no markdown prose, no input() prompts).\n"
        "2. Pay strict attention to repr(...) of Expected Output: match exact leading spaces on pyramid/pattern rows, "
        "no extra trailing spaces at line ends, exact capitalization, and exact float precision.\n"
        "3. Use optimal O(N) / O(N log N) algorithms; handle N=0, negative numbers, duplicates, and multi-line vs single-line input."
    )
    base_u = (
        f"Problem: {meta.get('title', slug)} ({meta.get('difficulty', '')})\n\n"
        f"{(meta.get('description') or meta.get('raw') or '')[:2600]}\n\n"
        f"Input Spec: {meta.get('input_spec', '')}\nOutput Spec: {meta.get('output_spec', '')}\n\n"
        f"{samples_repr}\n{prev_hint}"
    )

    u_prompt = base_u
    best_code = ""
    for tr in range(3):
        raw = call_llm(sys_p, u_prompt, seed + tr * 2)
        if not raw:
            continue
        code = strip_fences(raw)
        best_code = code
        ok, err = verify_code_locally(code, "PYTHON 3", samples)
        if ok:
            tmp = out_file.with_suffix(".tmp")
            tmp.write_text(json.dumps({"slug": slug, "lang": "PYTHON 3", "code": code, "local_ok": True}), encoding="utf-8")
            tmp.replace(out_file)
            return True
        u_prompt = f"{base_u}\n\nYour previous Python 3 code failed local check:\n{code[:1200]}\nError:\n{err}\nReturn ONLY corrected Python 3 code."

    if best_code:
        tmp = out_file.with_suffix(".tmp")
        tmp.write_text(json.dumps({"slug": slug, "lang": "PYTHON 3", "code": best_code, "local_ok": False}), encoding="utf-8")
        tmp.replace(out_file)
        return True
    return False


def drain_repair_queue(ex: ThreadPoolExecutor) -> int:
    rfiles = sorted(REPAIR_QUEUE_DIR.glob("*.json"))[:16]
    if not rfiles:
        return 0

    def _repair_one(rf: Path) -> bool:
        try:
            payload = json.loads(rf.read_text(encoding="utf-8"))
            rf.unlink()
        except Exception:
            return False
        slug = payload["slug"]
        lang = payload.get("lang", "PYTHON 3")
        prob_text = payload.get("prob_text", "")
        starter = payload.get("starter", "")
        samples = payload.get("samples") or []
        err_ctx = payload.get("err_ctx", "")

        lang_rule = (
            "Write a complete standalone Python 3 program reading from sys.stdin and printing exact output to sys.stdout."
            if lang.startswith("PYTHON")
            else f"Write a complete standalone {lang} program reading stdin and printing exact stdout."
        )
        if lang in ("JAVA", "JAVA 8"):
            lang_rule += " Use `public class Main` unless Starter Code specifies another class name."
        sys_p = f"Expert {lang} competitive programmer. {lang_rule} Output ONLY raw code."
        u_p = f"Problem:\n{prob_text[:2500]}\n\nStarter:\n{starter[:600]}\n\nPREVIOUS SUBMISSION FAILED:\n{err_ctx[:900]}\nFix all edge cases & exact formatting!"

        for tr in range(2):
            raw = call_llm(sys_p, u_p, int(time.time()) + tr * 3)
            if not raw:
                continue
            code = strip_fences(raw)
            ok, lerr = verify_code_locally(code, lang, samples)
            if ok or tr == 1:
                out_f = PY_PRE_DIR / f"{slug}__repaired.json"
                tmp = out_f.with_suffix(".tmp")
                tmp.write_text(json.dumps({"slug": slug, "lang": lang, "code": code, "repaired": True}), encoding="utf-8")
                tmp.replace(out_f)
                return True
            u_p += f"\nLocal check error:\n{lerr}"
        return False

    futs = [ex.submit(_repair_one, rf) for rf in rfiles]
    wait(futs, timeout=75)
    return len(rfiles)


def main() -> int:
    workers = 6
    log(f"Starting Python-3 exact-whitespace pre-solver + repair worker ({workers} threads)...")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for pass_no in range(30):
            drain_repair_queue(ex)
            res = json.loads(RESULTS_JSON.read_text(encoding="utf-8")) if RESULTS_JSON.exists() else {}
            todo = []
            for pf in sorted(PROB_DIR.glob("*.json")):
                try:
                    d = json.loads(pf.read_text(encoding="utf-8"))
                    slug = d.get("slug") or pf.stem
                    d["slug"] = slug
                    if res.get(slug, {}).get("status") == "COMPLETED":
                        continue
                    if (PY_PRE_DIR / f"{slug}.json").exists():
                        continue
                    todo.append((d, res.get(slug, {}).get("reason", "")))
                except Exception:
                    continue

            if not todo:
                log("All known unsolved CodeKata problems pre-solved in Python 3!")
                time.sleep(8.0)
                continue

            todo.sort(key=lambda pair: (0 if pair[0].get("difficulty") == "Easy" else (1 if pair[0].get("difficulty") == "Medium" else 2), pair[0]["slug"]))
            log(f"Pass {pass_no+1}: {len(todo)} unsolved CodeKata problems queued for Python 3 pre-solve...")
            batch_sz = 8
            for b in range(0, len(todo), batch_sz):
                drain_repair_queue(ex)
                chunk = todo[b:b + batch_sz]
                futs = [ex.submit(solve_one_python, m, rsn, b + i) for i, (m, rsn) in enumerate(chunk)]
                done_f, _ = wait(futs, timeout=95)
                ok_c = sum(1 for f in done_f if f.result())
                log(f"Batch +{ok_c}/{len(chunk)} ready | Total Python precomputed: {len(list(PY_PRE_DIR.glob('*.json')))}")
                time.sleep(0.8)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
