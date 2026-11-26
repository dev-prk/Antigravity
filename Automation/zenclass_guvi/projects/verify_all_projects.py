"""End-to-end deliverable structure, pytest, and headless Streamlit UI verification across all 7 Zen Class projects."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

PROJECTS_ROOT = Path(__file__).resolve().parent

PROJECT_SLUGS = [
    "intel-aiml-ncaafb-api-data-analysis",
    "intl-aiml-traffic-violations-insight-system",
    "intel-aiml-rapido-intelligent-mobility-insights",
    "intel-aiml-visual-product-similarity-image-based-recommend",
    "intl-aiml-ai-powered-banking-support-fraud-intelligence",
    "intel-aiml-multi-agent-support-ticket-automation-system",
    "int-aiml-c-we-e-b2-b3-b4-final-project",
]


def verify_all() -> int:
    results = []
    all_ok = True

    for slug in PROJECT_SLUGS:
        pdir = PROJECTS_ROOT / slug
        req_files = ["README.md", "requirements.txt", "app.py"]
        missing = [f for f in req_files if not (pdir / f).exists()]

        # 1. Run pytest
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(pdir),
            capture_output=True,
            text=True,
            env={**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE", "OMP_NUM_THREADS": "1"},
        )
        pytest_ok = proc.returncode == 0

        # 2. Run headless Streamlit AppTest smoke render in isolated subprocess
        ui_code = (
            "import os; os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'; os.environ['OMP_NUM_THREADS']='1'; "
            "from streamlit.testing.v1 import AppTest; "
            "at = AppTest.from_file('app.py', default_timeout=60); at.run(); "
            "assert not at.exception, f'Streamlit exception: {at.exception}'; "
            "print('STREAMLIT_RENDER_OK', len(at.metric), 'metrics')"
        )
        ui_proc = subprocess.run(
            [sys.executable, "-c", ui_code],
            cwd=str(pdir),
            capture_output=True,
            text=True,
        )
        ui_ok = ui_proc.returncode == 0

        ok = (not missing) and pytest_ok and ui_ok
        if not ok:
            all_ok = False

        results.append({
            "project": slug,
            "files_ok": len(missing) == 0,
            "pytest_ok": pytest_ok,
            "pytest_summary": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr.strip()[-200:],
            "streamlit_ui_ok": ui_ok,
            "streamlit_summary": ui_proc.stdout.strip().splitlines()[-1] if ui_proc.stdout.strip() else ui_proc.stderr.strip()[-300:],
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {slug} | pytest={pytest_ok} | streamlit_ui={ui_ok}")
        if not ok:
            print("  pytest out:", proc.stdout, proc.stderr)
            print("  ui out:", ui_proc.stdout, ui_proc.stderr)

    (PROJECTS_ROOT / "VERIFICATION_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(verify_all())
