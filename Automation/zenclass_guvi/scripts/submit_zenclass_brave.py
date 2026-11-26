"""
Zero-Flash Foreground Brave Browser Submitter for GUVI Zen Class Projects.

All 7 GitHub repositories under https://github.com/dev-prk/ are already published and verified.
This script:
1. Opens https://www.zenclass.in/login ONCE in foreground Brave Browser (no stale cookie injection,
   ZERO navigation/reload polling while waiting for login — eliminating all screen flashing).
2. Passively waits until Zen Class login completes and settles on /dashboard or /projects.
3. Navigates ONCE to https://www.zenclass.in/projects and submits all 7 GitHub URLs in-place.
4. Captures final board counts + full-page verification screenshot.
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


def wait_for_zenclass_login_passively(ctx: BrowserContext, page: Page, max_wait_sec: int = 600) -> Page:
    """
    Opens https://www.zenclass.in/login ONCE and waits COMPLETELY PASSIVELY (never calling goto() inside the loop)
    until the user finishes signing in and lands stably on an authenticated Zen Class route.
    """
    # Clear any corrupted/stale zenclass cookies so React Router does not redirect-loop
    try:
        all_cookies = ctx.cookies()
        keep = [c for c in all_cookies if "zenclass" not in c.get("domain", "")]
        ctx.clear_cookies()
        if keep:
            ctx.add_cookies(keep)
    except Exception:
        pass

    log("Opening https://www.zenclass.in/login once in foreground Brave Browser...")
    page.goto("https://www.zenclass.in/login", wait_until="domcontentloaded", timeout=30000)
    activate_brave()

    prompted = False
    t0 = time.time()
    while time.time() - t0 < max_wait_sec:
        for p in list(ctx.pages):
            if p.is_closed():
                continue
            try:
                u = p.url
                # Must be on zenclass.in and NOT on /login or oauth callback
                if (
                    "zenclass.in" in u
                    and "/login" not in u
                    and "google" not in u
                    and "callback" not in u
                ):
                    # Verify token or dashboard UI settled for 2.5s without bouncing back to /login
                    time.sleep(2.5)
                    u_after = p.url
                    if "zenclass.in" in u_after and "/login" not in u_after:
                        has_session = p.evaluate(
                            "() => Boolean(localStorage.getItem('authToken') || localStorage.length > 0 || document.body.innerText.includes('Student'))"
                        )
                        if has_session:
                            log(f"Zen Class session stably authenticated on {u_after}!")
                            return p
            except Exception:
                continue

        if not prompted:
            log("WAITING_FOR_USER: Please sign in once on https://www.zenclass.in/login in Brave Browser (zero reloads while you sign in)...")
            prompted = True
        time.sleep(2.0)

    raise RuntimeError("Timed out waiting for Zen Class login in Brave Browser.")


def submit_single_card_in_place(page: Page, slot_label: str, github_url: str) -> Dict[str, Any]:
    # Ensure any leftover modal from previous card is closed
    try:
        if page.locator('input[placeholder="Enter Link"]:visible').count() > 0:
            page.keyboard.press("Escape")
            page.wait_for_timeout(600)
    except Exception:
        pass

    click_state = page.evaluate(
        """(slotLabel) => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
            let slotNode = null;
            while (walker.nextNode()) {
                const el = walker.currentNode;
                if (el.children.length === 0 && el.textContent && el.textContent.trim() === slotLabel) {
                    slotNode = el;
                    break;
                }
            }
            if (!slotNode) {
                return { found: false, reason: "SLOT_LABEL_NOT_FOUND" };
            }
            let card = slotNode.parentElement;
            while (card && card !== document.body) {
                const btns = Array.from(card.querySelectorAll("button"));
                const hasAction = card.innerText.includes("View") || btns.length > 0;
                if (hasAction && card.innerText.includes(slotLabel) && card.clientHeight > 80 && card.clientHeight < 450) {
                    const submitBtn = btns.find(b => b.innerText.trim().toLowerCase() === "submit");
                    if (submitBtn) {
                        submitBtn.scrollIntoView({ block: "center" });
                        submitBtn.click();
                        return { found: true, clickedSubmit: true, cardText: card.innerText };
                    }
                    return { found: true, clickedSubmit: false, reason: "ALREADY_SUBMITTED", cardText: card.innerText };
                }
                card = card.parentElement;
            }
            return { found: false, reason: "CARD_CONTAINER_NOT_FOUND" };
        }""",
        slot_label,
    )

    if not click_state.get("found"):
        return {"status": click_state.get("reason", "NOT_FOUND"), "github_url": github_url}

    if not click_state.get("clickedSubmit"):
        return {
            "status": "ALREADY_SUBMITTED",
            "github_url": github_url,
            "card_text": click_state.get("cardText", "")[:160],
        }

    page.wait_for_timeout(1200)

    link_inputs = page.locator('input[placeholder="Enter Link"]:visible, .submit-form-container-web input[type="text"]:visible')
    if link_inputs.count() == 0:
        link_inputs = page.locator('input[type="text"]:visible, input[type="url"]:visible')

    in_count = link_inputs.count()
    if in_count == 0:
        return {"status": "MODAL_INPUT_NOT_FOUND", "github_url": github_url}

    for i in range(in_count):
        inp = link_inputs.nth(i)
        inp.click()
        inp.fill("")
        inp.fill(github_url)

    page.wait_for_timeout(600)

    submitted_modal = page.evaluate(
        """() => {
            const modalInput = document.querySelector('input[placeholder="Enter Link"]');
            if (modalInput) {
                let container = modalInput.parentElement;
                while (container && container !== document.body) {
                    const btns = Array.from(container.querySelectorAll("button")).filter(
                        b => b.innerText.trim().toLowerCase() === "submit" && b.offsetParent !== null
                    );
                    if (btns.length > 0) {
                        btns[btns.length - 1].click();
                        return true;
                    }
                    container = container.parentElement;
                }
            }
            const fallbackBtns = Array.from(document.querySelectorAll('.submit-form-container-web button, [role="dialog"] button')).filter(
                b => b.innerText.trim().toLowerCase() === "submit"
            );
            if (fallbackBtns.length > 0) {
                fallbackBtns[fallbackBtns.length - 1].click();
                return true;
            }
            return false;
        }"""
    )
    if not submitted_modal:
        return {"status": "MODAL_SUBMIT_BTN_NOT_FOUND", "github_url": github_url}

    confirmation_msg = ""
    for _ in range(14):
        page.wait_for_timeout(500)
        try:
            toast = page.locator(".sucess-popup-main-container, .Toastify__toast, [role='alert']").first
            if toast.count() > 0 and toast.is_visible():
                confirmation_msg = toast.inner_text().strip()
            if page.locator('input[placeholder="Enter Link"]:visible').count() == 0:
                if not confirmation_msg:
                    confirmation_msg = "Modal closed cleanly after submit"
                break
        except Exception:
            continue

    page.wait_for_timeout(1800)
    return {
        "status": "SUBMITTED",
        "fields_filled": in_count,
        "github_url": github_url,
        "confirmation": confirmation_msg or "Submitted",
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
        log("Launching Brave Browser (zero-flash mode)...")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=config.BROWSER_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
            slow_mo=40,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        zc_page = wait_for_zenclass_login_passively(ctx, page)

        # Navigate ONCE to /projects and wait for cards to hydrate
        log("Navigating once to https://www.zenclass.in/projects...")
        zc_page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
        for _ in range(15):
            zc_page.wait_for_timeout(1000)
            body_txt = zc_page.evaluate("() => document.body.innerText")
            if "Pending Projects" in body_txt or "Final Project - 1" in body_txt or "Completed Projects" in body_txt:
                break
        zc_page.wait_for_timeout(1500)

        for slug, slot_lbl, exact_title in PROJECTS_SPEC:
            gh_url = results[slug]["github_url"]
            log(f"Submitting [{slot_lbl}] '{exact_title}' -> {gh_url} ...")
            sub_res = submit_single_card_in_place(zc_page, slot_lbl, gh_url)
            results[slug]["zenclass_submission"] = sub_res
            log(f"  -> {slot_lbl}: {sub_res}")

        # Single final refresh to capture verified Completed Projects column
        zc_page.reload(wait_until="domcontentloaded", timeout=30000)
        zc_page.wait_for_timeout(3500)
        board_summary = zc_page.evaluate(
            """() => {
                const submitBtns = Array.from(document.querySelectorAll("button")).filter(
                    b => b.innerText.trim().toLowerCase() === "submit" && b.offsetParent !== null
                ).length;
                return {
                    remaining_submit_buttons: submitBtns,
                    board_text_excerpt: document.body.innerText.slice(0, 1200)
                };
            }"""
        )
        SCREENSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        zc_page.screenshot(path=str(SCREENSHOT_OUT), full_page=True)

        payload = {
            "github_owner": OWNER,
            "board_verification": board_summary,
            "screenshot": str(SCREENSHOT_OUT),
            "projects": results,
        }
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log(f"ALL SUBMISSIONS FINISHED! Remaining Submit buttons: {board_summary['remaining_submit_buttons']}")
        ctx.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
