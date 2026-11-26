"""
kata_common.py — Shared Single-Tab Brave + $0 FreeLLMAPI + Exact-Whitespace Verification Helpers
for GUVI CodeKata (Python-first -> 100%), FixTheCode (Python-first), SQLKata (SQL), and WebKata (HTML/CSS/JS).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple
import urllib.request

from playwright.sync_api import BrowserContext, Page, Playwright

ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
PROFILE_DIR = ROOT / ".browser_profile"
NODE_BIN = "/Users/devesh/.local/node/bin/node"
FREELLM_BASE = os.environ.get("FREELLM_BASE", "http://127.0.0.1:31415")
FREEAPI_DB = os.path.expanduser("~/Library/Application Support/FreeLLMAPI/freeapi.db")

FAST_BRAVE_ARGS = list(config.BROWSER_ARGS) + [
    "--host-resolver-rules=MAP *.doubleclick.net 127.0.0.1, MAP *.googleadservices.com 127.0.0.1, "
    "MAP *.googletagmanager.com 127.0.0.1, MAP *.google-analytics.com 127.0.0.1, MAP *.clarity.ms 127.0.0.1, "
    "MAP bat.bing.com 127.0.0.1, MAP px.ads.linkedin.com 127.0.0.1, MAP web-in21.mxradon.com 127.0.0.1, "
    "MAP *.taboola.com 127.0.0.1, MAP *.tapad.com 127.0.0.1",
]

# Strongest reasoning & coding models in FreeLLMAPI ($0 free pool)
STRONG_MODELS = [
    "gpt-oss-120b",
    "qwen3.8-27b",
    "auto",
    "gemma-4-26b-a4b-it",
    "glm-5.3-flash",
    "minimax-m3.1-flash",
]

# Strict Python-first preference per user requirement ("Use python to solve all the code question")
PYTHON_FIRST_LANGS = ["PYTHON 3", "PYTHON 2", "C++", "C", "JAVASCRIPT", "JAVA", "JAVA 8", "BASH", "SQLITE"]


def _load_key() -> Optional[str]:
    if os.environ.get("FREELLM_KEY"):
        return os.environ["FREELLM_KEY"]
    if not os.path.exists(FREEAPI_DB):
        return None
    con = sqlite3.connect(f"file:{FREEAPI_DB}?mode=ro", uri=True)
    row = con.execute("SELECT value FROM settings WHERE key='unified_api_key'").fetchone()
    con.close()
    return row[0] if row else None


FREELLM_KEY = _load_key()


def call_llm(system_prompt: str, user_prompt: str, seed: int = 0, max_tokens: int = 2000) -> str:
    if not FREELLM_KEY:
        return ""
    n = len(STRONG_MODELS)
    for i in range(4):
        model_id = STRONG_MODELS[(seed + i) % n]
        try:
            body = {
                "model": model_id,
                "max_tokens": max_tokens,
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
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
            if txt and len(txt) > 4 and not txt.startswith("Safety:"):
                return txt
        except Exception:
            time.sleep(0.25)
    return ""


def strip_fences(raw: str) -> str:
    txt = re.sub(r"<think>.*?</think>", "", (raw or ""), flags=re.DOTALL).strip()
    m = re.search(r"```(?:[a-zA-Z0-9_+-]+)?\s*\n(.*?)```", txt, flags=re.DOTALL)
    if m:
        return m.group(1).rstrip() + "\n"
    txt = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", txt)
    txt = re.sub(r"\s*```$", "", txt)
    return txt.rstrip() + "\n"


def norm_lines_preserve_indent(s: str) -> str:
    """Preserves leading spaces on EVERY line (critical for star/number/alphabet pyramids!)."""
    lines = str(s).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(ln.rstrip() for ln in lines)


def verify_code_locally(code: str, lang: str, samples: List[Dict[str, str]]) -> Tuple[bool, str]:
    valid = [s for s in samples if s.get("input") or s.get("output")]
    if lang == "PYTHON 3":
        try:
            compile(code, "<sol>", "exec")
        except SyntaxError as exc:
            return False, f"SyntaxError: {exc}"
    if not valid or lang in ("JAVA", "JAVA 8"):
        return True, ""

    with tempfile.TemporaryDirectory() as td:
        tp = Path(td)
        if lang in ("PYTHON 3", "PYTHON 2"):
            src = tp / "sol.py"
            src.write_text(code, encoding="utf-8")
            cmd = [sys.executable, str(src)]
        elif lang in ("C", "CLANG C"):
            src, exe = tp / "sol.c", tp / "sol"
            src.write_text(code, encoding="utf-8")
            cr = subprocess.run(["/usr/bin/clang", "-O2", str(src), "-lm", "-o", str(exe)], capture_output=True, text=True, timeout=8)
            if cr.returncode != 0:
                return False, f"C compile error:\n{cr.stderr[:350]}"
            cmd = [str(exe)]
        elif lang == "C++":
            src, exe = tp / "sol.cpp", tp / "sol"
            src.write_text(code, encoding="utf-8")
            cr = subprocess.run(["/usr/bin/clang++", "-std=c++17", "-O2", str(src), "-o", str(exe)], capture_output=True, text=True, timeout=10)
            if cr.returncode != 0:
                return False, f"C++ compile error:\n{cr.stderr[:350]}"
            cmd = [str(exe)]
        elif lang == "JAVASCRIPT" and os.path.exists(NODE_BIN):
            src = tp / "sol.js"
            src.write_text(code, encoding="utf-8")
            cmd = [NODE_BIN, str(src)]
        else:
            return True, ""

        for idx, sc in enumerate(valid, start=1):
            inp, exp = str(sc.get("input", "")), str(sc.get("output", ""))
            try:
                pr = subprocess.run(cmd, input=inp if inp.endswith("\n") else inp + "\n", capture_output=True, text=True, timeout=3.0)
            except subprocess.TimeoutExpired:
                return False, f"Timeout (>3s) on sample #{idx}"
            if pr.returncode != 0:
                return False, f"Runtime error #{idx}: {pr.stderr[:240]}"
            if norm_lines_preserve_indent(pr.stdout) != norm_lines_preserve_indent(exp):
                return False, f"Output mismatch #{idx}:\nInput:\n{inp[:140]}\nExpected (exact spaces):\n{exp[:180]!r}\nGot:\n{pr.stdout[:180]!r}"
    return True, ""


def open_single_brave_tab(pw: Playwright, disable_images: bool = False) -> Tuple[BrowserContext, Page]:
    subprocess.run(["pkill", "-f", str(PROFILE_DIR)], check=False)
    time.sleep(0.6)
    for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        p = PROFILE_DIR / lk
        if p.exists() or p.is_symlink():
            try:
                p.unlink()
            except Exception:
                pass
    args = list(FAST_BRAVE_ARGS) + (["--blink-settings=imagesEnabled=false"] if disable_images else [])
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        executable_path=BRAVE_BINARY,
        headless=False,
        no_viewport=True,
        args=args,
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
    page.set_default_timeout(8000)
    return ctx, page


def enforce_single_tab(ctx: BrowserContext, page: Page) -> None:
    for ep in list(ctx.pages):
        if ep != page and not ep.is_closed():
            try:
                ep.close()
            except Exception:
                pass


def dismiss_popups(page: Page) -> None:
    try:
        page.evaluate(
            """() => {
                for (const b of document.querySelectorAll('button')) {
                    const t = (b.innerText || '').trim();
                    if ((t === '✕' || t === 'Finish' || t === 'Continue Here Anyway') && b.offsetParent !== null) {
                        b.click();
                    }
                }
            }"""
        )
    except Exception:
        pass
