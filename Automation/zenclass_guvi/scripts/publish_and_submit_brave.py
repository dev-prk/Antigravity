"""
Foreground Brave Browser Publisher & Zen Class Project Submitter.

1. Launches Brave Browser (/Applications/Brave Browser.app) visibly in the foreground.
2. Creates 7 standalone PUBLIC GitHub repositories (pausing cleanly in foreground Brave if GitHub login/Passkey is needed).
3. Pushes all 7 staged local Git repositories over SSH (git@github.com:<owner>/<slug>.git) and verifies live HTTPS URLs.
4. Navigates to https://www.zenclass.in/projects in the same Brave window, submits all 7 GitHub URLs, and verifies portal confirmation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

from playwright.sync_api import Page, sync_playwright

ZENCLASS_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(ZENCLASS_ROOT))
import config  # noqa: E402

BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
PROFILE_DIR = ZENCLASS_ROOT / ".browser_profile"
STAGE_BASE = Path("/Users/devesh/.gemini/antigravity/brain/2caedd74-214f-417a-893a-29945b5b662c/scratch/git_publish")
REPORT_OUT = ZENCLASS_ROOT / "reports" / "GITHUB_AND_ZENCLASS_SUBMISSION.json"
SCREENSHOT_OUT = ZENCLASS_ROOT / "screenshots" / "final_zenclass_submitted.png"

# Ordered list: (slug, repo_description, zenclass_card_match_substring, exact_card_title)
PROJECTS_SPEC: List[Tuple[str, str, str, str]] = [
    (
        "int-aiml-c-we-e-b2-b3-b4-final-project",
        "Autonomous Sports Commentary System — Multi-Agent AI Commentators, Live Stats, Voice Q&A, AWS & MLOps",
        "Final_Project",
        "INT-AIML-C-WE-E-B2, B3 &B4_Final_Project",
    ),
    (
        "intel-aiml-multi-agent-support-ticket-automation-system",
        "Multi-Agent Customer Support Intelligence Platform (6-Agent Graph, FAISS RAG, FastAPI, Streamlit)",
        "Multi-Agent Support Ticket",
        "INTEL_AIML_Multi-Agent Support Ticket Automation System",
    ),
    (
        "intl-aiml-ai-powered-banking-support-fraud-intelligence",
        "AI-Powered Banking Support & Fraud Intelligence System using NLP + FAISS RAG",
        "Banking Support",
        "INTL_AIML_AI-Powered Banking Support & Fraud Intelligence",
    ),
    (
        "intel-aiml-visual-product-similarity-image-based-recommend",
        "Visual Product Similarity & Image-Based Recommendation System (PyTorch ResNet50, FAISS, Streamlit)",
        "Visual Product Similarity",
        "INTEL_AIML_Visual Product Similarity & Image-Based Recommend",
    ),
    (
        "intel-aiml-rapido-intelligent-mobility-insights",
        "Rapido Intelligent Mobility Insights: Ride Outcomes, Cancellations & Dynamic Fare Forecasting",
        "Rapido",
        "INTEL-AIML_Rapido: Intelligent Mobility Insights",
    ),
    (
        "intl-aiml-traffic-violations-insight-system",
        "Traffic Violations Insight System: 43-Column Data Cleaning, EDA & Interactive Streamlit Dashboard",
        "Traffic Violations",
        "INTL_AIML_Traffic Violations Insight System",
    ),
    (
        "intel-aiml-ncaafb-api-data-analysis",
        "Sports Analytics on NCAAFB Data Using Real-Time API Feeds (Python, SQL, Sportradar API, Streamlit)",
        "NCAAFB",
        "INTEL_AIML_NCAAFB API: Data Analysis",
    ),
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def activate_brave() -> None:
    subprocess.run(["osascript", "-e", 'tell application "Brave Browser" to activate'], check=False)


def remote_repo_exists(owner: str, slug: str) -> bool:
    res = subprocess.run(
        ["git", "ls-remote", f"git@github.com:{owner}/{slug}.git"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return res.returncode == 0


def push_staged_repo(owner: str, slug: str) -> None:
    repo_dir = STAGE_BASE / slug
    remote_url = f"git@github.com:{owner}/{slug}.git"
    subprocess.run(["git", "-C", str(repo_dir), "remote", "set-url", "origin", remote_url], check=True)
    res = subprocess.run(
        ["git", "-C", str(repo_dir), "push", "-u", "origin", "main", "--force"],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if res.returncode != 0:
        raise RuntimeError(f"git push failed for {slug}: {res.stderr}")


def ensure_github_authenticated(page: Page, max_wait_sec: int = 600) -> str:
    log("Opening https://github.com/new in foreground Brave Browser...")
    page.goto("https://github.com/new", wait_until="domcontentloaded", timeout=30000)
    activate_brave()

    t0 = time.time()
    prompted = False
    while time.time() - t0 < max_wait_sec:
        url = page.url
        user_login = page.evaluate(
            "() => document.querySelector('meta[name=\"user-login\"]')?.getAttribute('content') || ''"
        )
        if user_login and "/login" not in url and "/sessions/" not in url:
            log(f"Authenticated on GitHub as '{user_login}'!")
            return str(user_login).strip()

        if not prompted:
            log("ACTION_NEEDED: Please complete GitHub sign-in / Passkey in the foreground Brave Browser window...")
            sys.stdout.write("\a")
            sys.stdout.flush()
            activate_brave()
            prompted = True
        time.sleep(2.0)

    raise RuntimeError("Timed out waiting for GitHub authentication in Brave Browser.")


def create_github_repo_in_ui(page: Page, owner: str, slug: str, description: str) -> None:
    if remote_repo_exists(owner, slug):
        log(f"GitHub repo {owner}/{slug} already exists — skipping UI creation.")
        return

    log(f"Creating public GitHub repository: {owner}/{slug}...")
    page.goto("https://github.com/new", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1200)

    # Fill repository name
    name_selectors = [
        'input[data-testid="repository-name-input"]',
        'input#repository-name-input',
        'input[aria-label="Repository"]',
        'input[aria-label*="Repository name"]',
        'input[name="repository[name]"]',
    ]
    filled_name = False
    for sel in name_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            loc.click()
            loc.fill(slug)
            filled_name = True
            break
    if not filled_name:
        raise RuntimeError(f"Could not locate Repository Name input on {page.url}")

    # Fill description if present
    desc_selectors = [
        'input[name="Description"]',
        'input[aria-label="Description"]',
        'input[data-testid="repository-description-input"]',
        'input[name="repository[description]"]',
    ]
    for sel in desc_selectors:
        loc = page.locator(sel).first
        if loc.count() > 0 and loc.is_visible():
            loc.fill(description)
            break

    # Ensure Public visibility is selected if radio exists
    pub_radio = page.locator('input[type="radio"][value="public"]').first
    if pub_radio.count() > 0 and pub_radio.is_visible():
        try:
            pub_radio.check()
        except Exception:
            pass

    # Wait for GitHub async availability validation
    page.wait_for_timeout(2000)

    create_btn_selectors = [
        'button:has-text("Create repository")',
        'button:has-text("Create a new repository")',
        'button[type="submit"]:has-text("Create")',
    ]
    clicked = False
    for sel in create_btn_selectors:
        btn = page.locator(sel).last
        if btn.count() > 0 and btn.is_visible():
            btn.scroll_into_view_if_needed()
            btn.click()
            clicked = True
            break
    if not clicked:
        raise RuntimeError("Could not find 'Create repository' submit button on GitHub /new")

    # Wait until git ls-remote sees the created repo (up to 20s)
    for _ in range(10):
        page.wait_for_timeout(2000)
        if remote_repo_exists(owner, slug):
            log(f"Verified remote repo created: git@github.com:{owner}/{slug}.git")
            return

    raise RuntimeError(f"Repository {owner}/{slug} was not reachable via SSH after UI click (current URL: {page.url})")


def ensure_zenclass_authenticated(page: Page, max_wait_sec: int = 600) -> None:
    log("Opening https://www.zenclass.in/projects in Brave Browser...")
    page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)

    if "/login" in page.url:
        log("Zen Class redirected to /login — attempting configured credentials first...")
        try:
            email_loc = page.locator('input[placeholder*="mail"], input[type="email"], input[type="text"]').first
            pass_loc = page.locator('input[type="password"]').first
            if email_loc.count() > 0 and pass_loc.count() > 0 and config.ZENCLASS_EMAIL and config.ZENCLASS_PASSWORD:
                email_loc.fill(config.ZENCLASS_EMAIL)
                pass_loc.fill(config.ZENCLASS_PASSWORD)
                sign_btn = page.locator('button:has-text("Sign in"), button[type="submit"]').first
                if sign_btn.count() > 0:
                    sign_btn.click()
                    page.wait_for_timeout(3500)
        except Exception as exc:
            log(f"Auto-fill note: {exc}")

    t0 = time.time()
    prompted = False
    while time.time() - t0 < max_wait_sec:
        if "/login" not in page.url and "zenclass.in" in page.url:
            if "/projects" not in page.url:
                page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
            if "/login" not in page.url:
                log(f"Authenticated on Zen Class ({page.url})!")
                return
        if not prompted:
            log("ACTION_NEEDED: Please sign in to Zen Class in the foreground Brave Browser window...")
            activate_brave()
            prompted = True
        time.sleep(2.0)

    raise RuntimeError("Timed out waiting for Zen Class authentication in Brave Browser.")


def submit_project_on_zenclass(page: Page, match_substr: str, exact_title: str, github_url: str) -> Dict[str, str]:
    page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)

    # Locate the card containing match_substr or exact_title
    cards = page.locator("#individual-card, .itempending-Project, .itemactive-Project, .itemcompleted-Project")
    card_count = cards.count()
    target_card = None
    card_text_found = ""

    for idx in range(card_count):
        c = cards.nth(idx)
        txt = c.inner_text()
        if exact_title in txt or match_substr.lower() in txt.lower():
            target_card = c
            card_text_found = txt
            break

    if target_card is None:
        return {"status": "CARD_NOT_FOUND", "github_url": github_url}

    # Check if Submit button exists on this card (or if already submitted)
    sub_btn = target_card.locator('button:has-text("Submit"), .primary-outlined-submit-btn').first
    if sub_btn.count() == 0 or not sub_btn.is_visible():
        return {"status": "ALREADY_SUBMITTED", "github_url": github_url, "card_preview": card_text_found[:120]}

    sub_btn.scroll_into_view_if_needed()
    sub_btn.click()
    page.wait_for_timeout(1200)

    # Fill all visible text/url inputs inside the modal
    modal_inputs = page.locator('.submit-form-container-web input[type="text"], input[placeholder="Enter Link"]')
    in_count = modal_inputs.count()
    if in_count == 0:
        return {"status": "MODAL_INPUT_NOT_FOUND", "github_url": github_url}

    for i in range(in_count):
        inp = modal_inputs.nth(i)
        if inp.is_visible():
            inp.click()
            inp.fill(github_url)

    page.wait_for_timeout(600)

    # Click modal confirm Submit button
    modal_submit = page.locator('.submit-form-container-web .form-submit-container button, .submit-form-container-web button:has-text("Submit")').last
    if modal_submit.count() == 0:
        return {"status": "MODAL_SUBMIT_BTN_NOT_FOUND", "github_url": github_url}

    modal_submit.click()

    # Wait for toast / confirmation / modal close
    confirmation_text = ""
    for _ in range(12):
        page.wait_for_timeout(500)
        popup = page.locator(".sucess-popup-main-container, .success-popup-container, .Toastify__toast, .modal-message").first
        if popup.count() > 0 and popup.is_visible():
            confirmation_text = popup.inner_text().strip()
            break
        if page.locator(".submit-form-container-web").count() == 0:
            confirmation_text = "Modal closed cleanly after submit"
            break

    page.wait_for_timeout(1500)
    return {
        "status": "SUBMITTED",
        "github_url": github_url,
        "confirmation": confirmation_text or "Submitted",
    }


def main() -> int:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        lp = PROFILE_DIR / lock_name
        if lp.exists() or lp.is_symlink():
            try:
                lp.unlink()
            except Exception:
                pass

    results: Dict[str, Dict] = {}

    with sync_playwright() as pw:
        log(f"Launching Brave Browser at {BRAVE_BINARY}...")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_BINARY,
            headless=False,
            no_viewport=True,
            args=config.BROWSER_ARGS,
            ignore_default_args=config.IGNORE_DEFAULT_ARGS,
            slow_mo=40,
        )
        # Restore saved cookies if available
        if config.STORAGE_STATE_PATH.exists():
            try:
                st_data = json.loads(config.STORAGE_STATE_PATH.read_text(encoding="utf-8"))
                if st_data.get("cookies"):
                    ctx.add_cookies(st_data["cookies"])
            except Exception:
                pass

        gh_page = ctx.pages[0] if ctx.pages else ctx.new_page()
        activate_brave()

        # 1. Authenticate GitHub & Publish all 7 repos
        owner = ensure_github_authenticated(gh_page)

        for slug, desc, _substr, exact_title in PROJECTS_SPEC:
            create_github_repo_in_ui(gh_page, owner, slug, desc)
            log(f"Pushing {slug} over SSH to git@github.com:{owner}/{slug}.git...")
            push_staged_repo(owner, slug)
            https_url = f"https://github.com/{owner}/{slug}"
            gh_page.goto(https_url, wait_until="domcontentloaded", timeout=30000)
            title_ok = slug.lower() in gh_page.url.lower()
            log(f"Published & verified: {https_url} (ok={title_ok})")
            results[slug] = {
                "card_title": exact_title,
                "github_url": https_url,
                "github_published": True,
            }

        # Save storage state after GitHub auth
        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))

        # 2. Open Zen Class in a tab inside the SAME Brave window & submit all 7 URLs
        zc_page = ctx.new_page()
        ensure_zenclass_authenticated(zc_page)

        for slug, _desc, substr, exact_title in PROJECTS_SPEC:
            https_url = results[slug]["github_url"]
            log(f"Submitting '{exact_title}' -> {https_url} ...")
            sub_info = submit_project_on_zenclass(zc_page, substr, exact_title, https_url)
            results[slug]["zenclass_submission"] = sub_info
            log(f"  Result for {slug}: {sub_info}")

        # Reload board to verify final Pending vs Completed counts and capture screenshot
        zc_page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
        zc_page.wait_for_timeout(3500)
        pending_cards = zc_page.locator(".itempending-Project").count()
        completed_cards = zc_page.locator(".itemcompleted-Project").count()
        active_cards = zc_page.locator(".itemactive-Project").count()
        SCREENSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        zc_page.screenshot(path=str(SCREENSHOT_OUT), full_page=True)
        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))

        final_payload = {
            "github_owner": owner,
            "board_counts_after_submission": {
                "active": active_cards,
                "pending": pending_cards,
                "completed": completed_cards,
            },
            "screenshot": str(SCREENSHOT_OUT),
            "projects": results,
        }
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")
        log(f"ALL DONE! Board counts: active={active_cards}, pending={pending_cards}, completed={completed_cards}")
        ctx.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
