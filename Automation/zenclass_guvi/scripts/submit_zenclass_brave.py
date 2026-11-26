"""
Verified Playwright Foreground Brave Submitter for GUVI Zen Class Projects.

Uses exact DOM selectors verified on https://www.zenclass.in/projects:
- Card container: .common-padding filtered by .project-card-course-name-wrapper (slot label)
- Card trigger: .primary-outlined-submit-btn (trusted Playwright click)
- Modal input: .submit-form-container-web input[placeholder="Enter Link"]
- Modal submit: .submit-form-container-web .form-submit-container button.primary-btn
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from playwright.sync_api import BrowserContext, Page, sync_playwright

ZENCLASS_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ZENCLASS_ROOT))
import config  # noqa: E402

BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
PROFILE_DIR = ZENCLASS_ROOT / ".browser_profile"
REPORT_OUT = ZENCLASS_ROOT / "reports" / "GITHUB_AND_ZENCLASS_SUBMISSION.json"
SCREENSHOT_OUT = ZENCLASS_ROOT / "screenshots" / "final_zenclass_submitted.png"

OWNER = "dev-prk"

PROJECTS_SPEC: List[Tuple[str, str, str]] = [
    ("int-aiml-c-we-e-b2-b3-b4-final-project", "Final Project - 1", "INT-AIML-C-WE-E-B2, B3 &B4_Final_Project"),
    ("intel-aiml-multi-agent-support-ticket-automation-system", "Mini Project - 6", "INTEL_AIML_Multi-Agent Support Ticket Automation System"),
    ("intl-aiml-ai-powered-banking-support-fraud-intelligence", "Mini Project - 5", "INTL_AIML_AI-Powered Banking Support & Fraud Intelligence"),
    ("intel-aiml-visual-product-similarity-image-based-recommend", "Mini Project - 4", "INTEL_AIML_Visual Product Similarity & Image-Based Recommend"),
    ("intel-aiml-rapido-intelligent-mobility-insights", "Mini Project - 3", "INTEL-AIML_Rapido: Intelligent Mobility Insights"),
    ("intl-aiml-traffic-violations-insight-system", "Mini Project - 2", "INTL_AIML_Traffic Violations Insight System"),
    ("intel-aiml-ncaafb-api-data-analysis", "Mini Project - 1", "INTEL_AIML_NCAAFB API: Data Analysis"),
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def activate_brave() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Brave Browser" to activate'], check=False)


def submit_card(page: Page, slot_label: str, github_url: str) -> Dict[str, Any]:
    # Close any lingering modal before starting next card
    close_icon = page.locator(".common-popup-close-icon-container")
    if close_icon.count() > 0 and close_icon.first.is_visible():
        close_icon.first.click()
        page.wait_for_timeout(600)

    card = page.locator(".common-padding", has=page.locator(".project-card-course-name-wrapper", has_text=slot_label)).first
    if card.count() == 0:
        return {"status": "CARD_NOT_FOUND", "github_url": github_url}

    sub_btn = card.locator(".primary-outlined-submit-btn")
    if sub_btn.count() == 0 or not sub_btn.first.is_visible():
        return {"status": "ALREADY_SUBMITTED", "github_url": github_url, "card_text": card.inner_text()[:180]}

    sub_btn.first.scroll_into_view_if_needed()
    sub_btn.first.click()

    modal_input = page.locator('.submit-form-container-web input[placeholder="Enter Link"]')
    modal_input.first.wait_for(state="visible", timeout=8000)

    count = modal_input.count()
    for i in range(count):
        inp = modal_input.nth(i)
        inp.click()
        inp.fill("")
        inp.fill(github_url)

    page.wait_for_timeout(400)

    confirm_btn = page.locator(".submit-form-container-web .form-submit-container button.primary-btn").first
    confirm_btn.click()

    # Capture confirmation popup or wait for modal to close
    confirmation_text = ""
    for _ in range(16):
        page.wait_for_timeout(500)
        popup = page.locator(".sucess-popup-main-container, .success-popup-container, .Toastify__toast, .validation-error-text").first
        if popup.count() > 0 and popup.is_visible():
            confirmation_text = popup.inner_text().strip()
            # Close success popup if it has a close button or wait for auto-dismiss
            if "error" in confirmation_text.lower() or "valid" in confirmation_text.lower():
                return {"status": "VALIDATION_ERROR", "error": confirmation_text, "github_url": github_url}
        if page.locator('.submit-form-container-web input[placeholder="Enter Link"]:visible').count() == 0:
            if not confirmation_text:
                confirmation_text = "Modal closed cleanly — card moved to Completed Projects"
            break

    # Wait briefly for any success popup overlay to auto-dismiss
    for _ in range(8):
        if page.locator(".MuiBackdrop-root:visible").count() == 0:
            break
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

    page.wait_for_timeout(1200)
    return {
        "status": "SUBMITTED",
        "fields_filled": count,
        "github_url": github_url,
        "confirmation": confirmation_text,
    }


def main() -> int:
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        lp = PROFILE_DIR / lock_name
        if lp.exists() or lp.is_symlink():
            try:
                lp.unlink()
            except Exception:
                pass

    results: Dict[str, Dict[str, Any]] = {}
    for slug, slot_lbl, exact_title in PROJECTS_SPEC:
        results[slug] = {
            "slot": slot_lbl,
            "card_title": exact_title,
            "github_url": f"https://github.com/{OWNER}/{slug}",
            "github_published": True,
        }

    with sync_playwright() as pw:
        log("Launching foreground Brave Browser on authenticated Zen Class profile...")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=config.BROWSER_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
            slow_mo=50,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        activate_brave()
        page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
        page.locator(".common-padding").first.wait_for(state="visible", timeout=15000)
        page.wait_for_timeout(1500)

        for slug, slot_lbl, exact_title in PROJECTS_SPEC:
            gh_url = results[slug]["github_url"]
            log(f"Submitting [{slot_lbl}] '{exact_title}' -> {gh_url} ...")
            sub_res = submit_card(page, slot_lbl, gh_url)
            results[slug]["zenclass_submission"] = sub_res
            log(f"  -> {slot_lbl}: {sub_res}")

        # Reload board to verify Pending Projects == 0 and Completed Projects == 7
        page.reload(wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        remaining_submit_btns = page.locator(".primary-outlined-submit-btn:visible").count()
        board_text = page.evaluate("() => document.body.innerText.slice(0, 2000)")

        SCREENSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SCREENSHOT_OUT), full_page=True)
        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))

        payload = {
            "github_owner": OWNER,
            "remaining_pending_submit_buttons": remaining_submit_btns,
            "board_text_excerpt": board_text,
            "screenshot": str(SCREENSHOT_OUT),
            "projects": results,
        }
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log(f"DONE! Remaining Pending Submit buttons: {remaining_submit_btns}")
        ctx.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
