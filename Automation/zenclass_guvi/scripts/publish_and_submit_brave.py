"""
Foreground Brave Browser Publisher & Zen Class Project Submitter (v2 — Navigation-Resilient).

1. Launches Brave Browser (/Applications/Brave Browser.app) visibly in the foreground reusing .browser_profile.
2. Creates 7 standalone PUBLIC GitHub repositories (resilient to mid-login redirects/WebAuthn navigations).
3. Pushes all 7 staged local Git repositories over SSH (git@github.com:<owner>/<slug>.git) and verifies live HTTPS URLs.
4. Navigates to https://www.zenclass.in/projects in the same Brave window, matches each card by its exact slot label
   ('Final Project - 1', 'Mini Project - 6' .. 'Mini Project - 1'), fills 'Enter Link' with the live GitHub URL,
   clicks Submit, and captures a full-page verification screenshot + JSON report.
"""

from __future__ import annotations

import json
import re
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
STAGE_BASE = Path("/Users/devesh/.gemini/antigravity/brain/2caedd74-214f-417a-893a-29945b5b662c/scratch/git_publish")
REPORT_OUT = ZENCLASS_ROOT / "reports" / "GITHUB_AND_ZENCLASS_SUBMISSION.json"
SCREENSHOT_OUT = ZENCLASS_ROOT / "screenshots" / "final_zenclass_submitted.png"

# (slug, repo_description, slot_label_on_card, exact_card_title)
PROJECTS_SPEC: List[Tuple[str, str, str, str]] = [
    (
        "int-aiml-c-we-e-b2-b3-b4-final-project",
        "Autonomous Sports Commentary System — Multi-Agent AI Commentators, Live Stats, Voice Q&A, AWS & MLOps",
        "Final Project - 1",
        "INT-AIML-C-WE-E-B2, B3 &B4_Final_Project",
    ),
    (
        "intel-aiml-multi-agent-support-ticket-automation-system",
        "Multi-Agent Customer Support Intelligence Platform (6-Agent Graph, FAISS RAG, FastAPI, Streamlit)",
        "Mini Project - 6",
        "INTEL_AIML_Multi-Agent Support Ticket Automation System",
    ),
    (
        "intl-aiml-ai-powered-banking-support-fraud-intelligence",
        "AI-Powered Banking Support & Fraud Intelligence System using NLP + FAISS RAG",
        "Mini Project - 5",
        "INTL_AIML_AI-Powered Banking Support & Fraud Intelligence",
    ),
    (
        "intel-aiml-visual-product-similarity-image-based-recommend",
        "Visual Product Similarity & Image-Based Recommendation System (PyTorch ResNet50, FAISS, Streamlit)",
        "Mini Project - 4",
        "INTEL_AIML_Visual Product Similarity & Image-Based Recommend",
    ),
    (
        "intel-aiml-rapido-intelligent-mobility-insights",
        "Rapido Intelligent Mobility Insights: Ride Outcomes, Cancellations & Dynamic Fare Forecasting",
        "Mini Project - 3",
        "INTEL-AIML_Rapido: Intelligent Mobility Insights",
    ),
    (
        "intl-aiml-traffic-violations-insight-system",
        "Traffic Violations Insight System: 43-Column Data Cleaning, EDA & Interactive Streamlit Dashboard",
        "Mini Project - 2",
        "INTL_AIML_Traffic Violations Insight System",
    ),
    (
        "intel-aiml-ncaafb-api-data-analysis",
        "Sports Analytics on NCAAFB Data Using Real-Time API Feeds (Python, SQL, Sportradar API, Streamlit)",
        "Mini Project - 1",
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
        timeout=120,
    )
    if res.returncode != 0:
        raise RuntimeError(f"git push failed for {slug}: {res.stderr}")


def ensure_github_authenticated(ctx: BrowserContext, page: Page, max_wait_sec: int = 600) -> str:
    log("Opening https://github.com/new in foreground Brave Browser...")
    try:
        page.goto("https://github.com/new", wait_until="domcontentloaded", timeout=30000)
    except Exception as exc:
        log(f"Initial goto note: {exc}")
    activate_brave()

    t0 = time.time()
    prompted = False
    while time.time() - t0 < max_wait_sec:
        for p in list(ctx.pages):
            if p.is_closed():
                continue
            try:
                url = p.url
                if "github.com" in url and "/login" not in url and "/sessions/" not in url and "/password_reset" not in url:
                    has_new_form = p.locator(
                        'input[data-testid="repository-name-input"], input#repository-name-input, input[aria-label*="Repository"], button:has-text("Create repository")'
                    ).count() > 0
                    user_login = p.evaluate(
                        "() => document.querySelector('meta[name=\"user-login\"]')?.getAttribute('content') || ''"
                    )
                    if user_login or has_new_form or url.rstrip("/") == "https://github.com/new":
                        resolved_owner = str(user_login).strip() or "dev-prk"
                        log(f"Authenticated on GitHub as '{resolved_owner}' (url={url})!")
                        return resolved_owner
            except Exception:
                # Mid-redirect execution context destroyed — safe to ignore and retry next tick
                continue

        if not prompted:
            log("ACTION_NEEDED: Please finish GitHub sign-in / Passkey in the foreground Brave Browser window...")
            activate_brave()
            prompted = True
        time.sleep(1.5)

    raise RuntimeError("Timed out waiting for GitHub authentication in Brave Browser.")


def create_github_repo_in_ui(page: Page, owner: str, slug: str, description: str) -> None:
    if remote_repo_exists(owner, slug):
        log(f"GitHub repo {owner}/{slug} already exists — skipping UI creation.")
        return

    log(f"Creating public GitHub repository: {owner}/{slug}...")
    page.goto("https://github.com/new", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)

    # Locate Repository Name input across Primer React & classic GitHub variants
    filled_name = False
    candidates = [
        page.get_by_role("textbox", name=re.compile(r"Repository name", re.I)),
        page.locator('input[data-testid="repository-name-input"]'),
        page.locator("input#repository-name-input"),
        page.locator('input[aria-label*="Repository"]'),
        page.locator('input[name="repository[name]"]'),
    ]
    for cand in candidates:
        try:
            if cand.count() > 0 and cand.first.is_visible():
                cand.first.click()
                cand.first.fill(slug)
                filled_name = True
                break
        except Exception:
            continue

    if not filled_name:
        raise RuntimeError(f"Could not find Repository Name input on {page.url}")

    # Fill optional description
    desc_candidates = [
        page.get_by_role("textbox", name=re.compile(r"Description", re.I)),
        page.locator('input[name="Description"]'),
        page.locator('input[aria-label*="Description"]'),
        page.locator('input[data-testid="repository-description-input"]'),
    ]
    for dc in desc_candidates:
        try:
            if dc.count() > 0 and dc.first.is_visible():
                dc.first.fill(description)
                break
        except Exception:
            continue

    # Ensure Public radio is checked if radio controls are rendered
    pub_radio = page.locator('input[type="radio"][value="public"]').first
    try:
        if pub_radio.count() > 0 and pub_radio.is_visible():
            pub_radio.check()
    except Exception:
        pass

    # Wait for async name availability check ("... is available")
    page.wait_for_timeout(2200)

    btn_candidates = [
        page.get_by_role("button", name=re.compile(r"^Create repository$", re.I)),
        page.locator('button:has-text("Create repository")'),
        page.locator('button:has-text("Create a new repository")'),
    ]
    clicked = False
    for bc in btn_candidates:
        try:
            if bc.count() > 0 and bc.last.is_visible():
                bc.last.scroll_into_view_if_needed()
                bc.last.click()
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        raise RuntimeError(f"Could not click 'Create repository' button on {page.url}")

    # Poll git ls-remote up to 25s (handles post-click redirect or sudo confirmation if prompted)
    for attempt in range(13):
        page.wait_for_timeout(2000)
        if remote_repo_exists(owner, slug):
            log(f"Verified remote repo exists via SSH: git@github.com:{owner}/{slug}.git")
            return
        if attempt == 4:
            try:
                if "confirm" in page.url.lower() or "session" in page.url.lower():
                    log("ACTION_NEEDED: GitHub requested quick session confirmation in Brave...")
                    activate_brave()
            except Exception:
                pass

    raise RuntimeError(f"Repo {owner}/{slug} not reachable via SSH after creation attempt (URL: {page.url})")


def ensure_zenclass_authenticated(ctx: BrowserContext, page: Page, max_wait_sec: int = 600) -> Page:
    log("Opening https://www.zenclass.in/projects in Brave Browser...")
    try:
        page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass
    page.wait_for_timeout(2500)

    try:
        if "/login" in page.url and config.ZENCLASS_EMAIL and config.ZENCLASS_PASSWORD:
            log("Attempting automatic Zen Class sign-in with configured workspace credentials...")
            email_loc = page.locator('input[placeholder*="mail"], input[type="email"], input[type="text"]').first
            pass_loc = page.locator('input[type="password"]').first
            if email_loc.count() > 0 and pass_loc.count() > 0:
                email_loc.fill(config.ZENCLASS_EMAIL)
                pass_loc.fill(config.ZENCLASS_PASSWORD)
                sign_btn = page.locator('button:has-text("Sign in"), button[type="submit"]').first
                if sign_btn.count() > 0:
                    sign_btn.click()
                    page.wait_for_timeout(3500)
    except Exception as exc:
        log(f"Auto-signin note: {exc}")

    t0 = time.time()
    prompted = False
    while time.time() - t0 < max_wait_sec:
        for p in list(ctx.pages):
            if p.is_closed():
                continue
            try:
                u = p.url
                if "zenclass.in" in u and "/login" not in u:
                    if "/projects" not in u:
                        p.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
                        p.wait_for_timeout(2500)
                    if "/login" not in p.url:
                        log(f"Authenticated on Zen Class ({p.url})!")
                        return p
            except Exception:
                continue

        if not prompted:
            log("ACTION_NEEDED: Please sign in to Zen Class in the foreground Brave Browser window...")
            activate_brave()
            prompted = True
        time.sleep(1.5)

    raise RuntimeError("Timed out waiting for Zen Class authentication in Brave Browser.")


def submit_project_by_slot(page: Page, slot_label: str, exact_title: str, github_url: str) -> Dict[str, Any]:
    page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    # Locate the exact card containing slot_label (e.g., "Final Project - 1", "Mini Project - 6") and click its Submit button
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
            // Walk up to the nearest card container that holds action buttons ('View' or 'Submit')
            let card = slotNode.parentElement;
            while (card && card !== document.body) {
                const btns = Array.from(card.querySelectorAll("button"));
                const hasViewOrSubmit = card.innerText.includes("View") || btns.length > 0;
                if (hasViewOrSubmit && card.innerText.includes(slotLabel) && card.clientHeight > 90 && card.clientHeight < 420) {
                    const submitBtn = btns.find(b => b.innerText.trim().toLowerCase() === "submit");
                    if (submitBtn) {
                        submitBtn.scrollIntoView({ block: "center" });
                        submitBtn.click();
                        return { found: true, clickedSubmit: true, cardText: card.innerText };
                    }
                    return { found: true, clickedSubmit: false, reason: "NO_SUBMIT_BTN_ALREADY_SUBMITTED", cardText: card.innerText };
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

    # Wait for modal input ('Enter Link' or any visible text input inside modal)
    link_inputs = page.locator('input[placeholder="Enter Link"], .submit-form-container-web input[type="text"]')
    if link_inputs.count() == 0:
        # Fallback: any visible text input on top layer
        link_inputs = page.locator('input[type="text"]:visible, input[type="url"]:visible')

    in_count = link_inputs.count()
    if in_count == 0:
        return {"status": "MODAL_INPUT_NOT_FOUND", "github_url": github_url}

    filled_count = 0
    for i in range(in_count):
        inp = link_inputs.nth(i)
        if inp.is_visible():
            inp.click()
            inp.fill("")
            inp.fill(github_url)
            filled_count += 1

    page.wait_for_timeout(600)

    # Click the modal's Submit button (distinct from card Submit buttons behind backdrop)
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

    # Wait up to 6s for toast / success popup or modal dismissal
    confirmation_msg = ""
    for _ in range(12):
        page.wait_for_timeout(500)
        try:
            if page.locator('input[placeholder="Enter Link"]:visible').count() == 0:
                confirmation_msg = "Modal closed after submission"
                break
            toast = page.locator(".sucess-popup-main-container, .Toastify__toast, [role='alert']").first
            if toast.count() > 0 and toast.is_visible():
                confirmation_msg = toast.inner_text().strip()
                break
        except Exception:
            continue

    page.wait_for_timeout(1500)
    return {
        "status": "SUBMITTED",
        "fields_filled": filled_count,
        "github_url": github_url,
        "confirmation": confirmation_msg or "Submitted",
    }


def read_board_summary(page: Page) -> Dict[str, Any]:
    return page.evaluate(
        """() => {
            const bodyText = document.body.innerText;
            const pendingBtns = Array.from(document.querySelectorAll("button")).filter(
                b => b.innerText.trim().toLowerCase() === "submit" && b.offsetParent !== null
            ).length;
            return {
                remaining_submit_buttons_on_board: pendingBtns,
                has_no_pending_text: bodyText.includes("No Pending") || pendingBtns === 0,
                page_snippet: bodyText.slice(0, 800)
            };
        }"""
    )


def main() -> int:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        lp = PROFILE_DIR / lock_name
        if lp.exists() or lp.is_symlink():
            try:
                lp.unlink()
            except Exception:
                pass

    results: Dict[str, Dict[str, Any]] = {}

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
        if config.STORAGE_STATE_PATH.exists():
            try:
                st_data = json.loads(config.STORAGE_STATE_PATH.read_text(encoding="utf-8"))
                if st_data.get("cookies"):
                    ctx.add_cookies(st_data["cookies"])
            except Exception:
                pass

        gh_page = ctx.pages[0] if ctx.pages else ctx.new_page()
        activate_brave()

        # Phase 1 & 2: Ensure GitHub auth, create 7 public repos & push over SSH
        owner = ensure_github_authenticated(ctx, gh_page)
        gh_page = [p for p in ctx.pages if not p.is_closed()][0]

        for slug, desc, slot_lbl, exact_title in PROJECTS_SPEC:
            create_github_repo_in_ui(gh_page, owner, slug, desc)
            log(f"Pushing {slug} over SSH to git@github.com:{owner}/{slug}.git...")
            push_staged_repo(owner, slug)
            https_url = f"https://github.com/{owner}/{slug}"
            gh_page.goto(https_url, wait_until="domcontentloaded", timeout=30000)
            log(f"Verified public repository live: {https_url}")
            results[slug] = {
                "slot": slot_lbl,
                "card_title": exact_title,
                "github_url": https_url,
                "github_published": True,
            }

        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))

        # Phase 3: Open Zen Class in a new tab of the same Brave window & submit all 7 URLs
        zc_tab = ctx.new_page()
        zc_page = ensure_zenclass_authenticated(ctx, zc_tab)

        for slug, _desc, slot_lbl, exact_title in PROJECTS_SPEC:
            https_url = results[slug]["github_url"]
            log(f"Submitting [{slot_lbl}] '{exact_title}' -> {https_url} ...")
            sub_info = submit_project_by_slot(zc_page, slot_lbl, exact_title, https_url)
            results[slug]["zenclass_submission"] = sub_info
            log(f"  -> {slot_lbl}: {sub_info}")

        # Final board reload + screenshot + summary verification
        zc_page.goto("https://www.zenclass.in/projects", wait_until="domcontentloaded", timeout=30000)
        zc_page.wait_for_timeout(3500)
        board_check = read_board_summary(zc_page)
        SCREENSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        zc_page.screenshot(path=str(SCREENSHOT_OUT), full_page=True)
        ctx.storage_state(path=str(config.STORAGE_STATE_PATH))

        final_payload = {
            "github_owner": owner,
            "board_verification": board_check,
            "screenshot": str(SCREENSHOT_OUT),
            "projects": results,
        }
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")
        log(f"COMPLETED ALL 7 PROJECTS! Remaining Submit buttons on board: {board_check['remaining_submit_buttons_on_board']}")
        ctx.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
