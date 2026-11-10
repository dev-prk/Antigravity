# Milestone 3 Blueprint: Guvi CodeKata Catalog Discovery & Problem Solving Pipeline

**Date**: 2026-11-10T16:20:00Z  
**Author**: Explorer Subagent (`explorer_m3_2`)  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_2`  
**Handoff Type**: Hard (Investigation & Architecture Blueprint Complete)

---

## Executive Summary

This report establishes the complete architectural and implementation blueprint for **Milestone 3: Guvi CodeKata Driver & Automation Pipeline** in `zenclass_guvi/drivers/guvi_driver.py` and `zenclass_guvi/drivers/base_driver.py`.

The design bridges the core foundation services (M1: `BrowserManager`, `StateManager`, `HitlHandler`, `SummaryReporter`) and the verified algorithmic problem-solving engine (M2: `ProblemExtractor`, `CodeGenerator`, `SubprocessSandbox`, `AceEditorAdapter`) into a fully autonomous, production-grade platform driver adhering to user requirements **R1** (foreground headed execution & anti-fabrication guardrails), **R2** (end-to-end autonomous discovery, solving, local testing, and submission), and **R3** (SQLite state persistence & executive reporting).

---

## 1. Observation

Direct inspection of the repository codebase, live reverse-engineering survey (`spec_miner_survey_2`), and opaque-box test harness fixtures revealed the following concrete structures and constraints:

### 1.1 Existing Core Services & Verified Solver Package
1. **`core/browser.py`**:
   - `BrowserManager.get_context() -> BrowserContext`: Headed persistent Chromium context (`headless=False`, `slow_mo=50ms`, maximized viewport).
   - `BrowserManager.get_page(url: Optional[str] = None) -> Page`: Reuses primary tab, navigates with `domcontentloaded`, enforces default navigation timeout (30s).
   - `BrowserManager.close_auxiliary_tabs(keep_page)`: Cleans up popups and secondary tabs.
   - `BrowserManager.save_storage_state()`: Serializes cookies and origins to `data/storage_state.json`.
   - `BrowserManager.save_screenshot(name, page)`: Captures diagnostic PNGs in `screenshots/`.

2. **`core/state_manager.py`**:
   - `StateManager.batch_record_tasks(tasks: List[Dict[str, Any]]) -> int`: Atomic bulk upsert for catalog items in a single WAL transaction.
   - `StateManager.record_task(...)` and `StateManager.update_task_status(...)`: Mandatory 9 R3 fields: `platform`, `task_id`, `category`, `status`, `attempt_count`, `result`, `timestamp`, `failure_reason`, `next_action`.
   - `StateManager.list_pending(platform="guvi", limit=N) -> List[TaskRecord]`: Query pending / discovered items.
   - `StateManager.get_summary_stats() -> dict`: Produces real-time aggregated metrics.

3. **`core/hitl_handler.py`**:
   - `HitlHandler.check_and_handle_guardrails(page: Page, task_id: str) -> bool`: Detects Cloudflare Turnstile (`challenges.cloudflare.com`), reCAPTCHA (`g-recaptcha`), ZenClass MFA (`.login-mfa-active`), Guvi Account Activation Modal (`#myModal #sendmail`), and generic OTP challenges. Emits terminal bell (`\a`), renders warning card, pauses without bypass fabrication, and verifies resolution.

4. **`core/reporter.py`**:
   - `SummaryReporter.generate_all_reports() -> Tuple[str, str]`: Produces `reports/SUMMARY_REPORT.md` and `reports/summary.json`.
   - `SummaryReporter.print_terminal_summary() -> None`: Prints high-impact terminal card.

5. **`solver/` package (Verified in M2)**:
   - `solver.extractor.extract_problem_spec(page: Page | str) -> ProblemSpecification`: Extracts `title`, `description`, `input_spec`, `output_spec`, `sample_cases` (`SampleCase(input_text, expected_output)`), `constraints`, `category`, `slug`.
   - `solver.code_generator.generate_solution(spec) -> GeneratedSolution(code, category, confidence, explanation)`: Algorithmic synthesizer with canonical solvers and templates.
   - `solver.test_runner.test_solution(code, sample_cases, timeout=5.0) -> ValidationResult(all_passed, passed_count, total_count, results)`: Subprocess sandbox testing candidate solutions against stdin/stdout.
   - `solver.ace_adapter.wait_for_editor(page, timeout=10.0) -> bool`: Awaits Ace Editor DOM and JS readiness.
   - `solver.ace_adapter.inject_code(page, code, verify=True) -> bool`: Injects code via CDP keyboard (`Meta+A`, Backspace, `Input.insertText`) with JS API fallback (`ace.edit().setValue()`).

### 1.2 Platform DOM Selectors & Wire Specifications
From `spec_miner_survey_2/handoff.md` and `tests/e2e/harness/dom_fixtures.py`:

| Component | Target URL | Critical DOM Selectors / APIs | Expected Behavior |
|---|---|---|---|
| **Authentication** | `https://www.guvi.in/sign-in/` | `#email`, `#password`, `#logged-in`, `a#login-btn`, `div.invalid-feedback`, `#myModal` | Submits credentials to `usercheck.php`. Sets cookie `authToken=auth:...`. Onboarding tour `#welcome` or `#finish` must be dismissed. |
| **Catalog Table** | `https://www.guvi.in/code-kata/` | `button.filter-topics-tab-active`, `table tbody tr.cursor-pointer`, 5 columns (`td`) per row | 15 problems per page across 143 total pages (~2,145 total discoverable items). |
| **Status Marker** | Table Row Col 0 | `g[clip-path*="completed-icon_svg__a"]`, `path[fill="#0DBA4B"]` | If completed SVG present: Problem is **SOLVED**. If absent: Problem is **PENDING/DISCOVERED**. |
| **Problem Metadata** | Table Row Cols 1-4 | Col 1: `.problem-title`, Col 2: `.success-rate`, Col 3: `.difficulty`, Col 4: `.points` | Slug derived from `data-slug`, link href, or title normalization (`re.sub(r'^\d+\.\s*', '', title)`). |
| **Pagination** | Table Bottom | `button:has-text("Go to next page")`, `button.next-page`, `button.page-pill`, `button.prev-page` | Next button is disabled when `currentPage === 143`. |
| **Problem Workspace** | `https://www.guvi.in/code-kata/<slug>/` | `#editor.ace_editor`, `textarea.ace_text-input`, `#editorModeSelectDesktop`, `#reset_language_modal` | Loads problem details in left pane, Ace Editor in right pane. Language selector defaults to `PYTHON 3`. |
| **Run Code** | Workspace Actions | `button.run-code`, `button:has-text("Run Code")`, `<dialog id="progress_modal">`, `.test-results-pane`, `.test-pill-status` | Fires `POST /code-kata/question/run`. Shows "Testing 0%". Evaluates sample tests; status is "Correct Answer" or "Wrong". |
| **Submit Code** | Workspace Actions | `button.submit-code`, `button:has-text("Submit")`, `#success_modal`, `.question-status` | Fires `POST /code-kata/question/submit`. Positive confirmation: `Solved!` in `.question-status`, or congratulations modal with earned points. |

---

## 2. Logic Chain

```
[M1 Core Services + M2 Solver Package]
                    │
                    ▼
       ┌────────────────────────┐
       │ drivers/base_driver.py │  <-- Abstract Base Driver (Safe actions, page helpers, guardrail hooks)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ drivers/guvi_driver.py │
       └───────────┬────────────┘
                   │
    ┌──────────────┴─────────────────────────┐
    ▼                                        ▼
[Catalog Discovery Engine]          [Workspace Solver Pipeline]
1. Auth check / login()             1. Navigate /code-kata/<slug>
2. Paginate 143 pages               2. Guardrail check (HITL R1)
3. Parse rows (15/page)             3. Extract ProblemSpec (solver.extractor)
4. Detect SVG #completed-icon       4. Synthesize Python 3 (solver.code_generator)
5. SQLite batch_record_tasks        5. Local sandbox test (solver.test_runner)
                                    6. Ace editor injection (solver.ace_adapter)
                                    7. Click Run Code & verify test pills
                                    8. Click Submit & verify "Solved!"
                                    9. StateManager R3 update
                                             │
                                             ▼
                               [Pipeline Orchestrator]
                               1. login()
                               2. discover_pending_problems(limit)
                               3. loop: solve_problem(slug)
                               4. reporter.generate_all_reports()
```

1. **Base Driver Foundation (`drivers/base_driver.py`)**:
   - Both Guvi and ZenClass drivers require resilient interaction primitives: scrolling into view, waiting for actionable element states, handling click intercepts, taking diagnostic screenshots on errors, and triggering HITL guardrails on security blocks.
   - Centralizing these in `BaseDriver` eliminates code duplication and ensures uniform error handling.

2. **Catalog Discovery & Pending Filtering Algorithm**:
   - Guvi organizes ~2,145 problems across 143 pages (15 problems per page).
   - Solved problems unambiguously carry the SVG clip path `url(#completed-icon_svg__a)` with green fill `#0DBA4B`. Unattempted / pending problems lack this completed clip path.
   - Performing discovery page by page and collecting problem metadata into memory, then executing `state_manager.batch_record_tasks()` yields high performance: all ~2,145 records are committed in a single SQLite transaction (<150ms).
   - The pending queue is constructed directly from problems lacking `#completed-icon_svg__a` or by querying `state_manager.list_pending(platform="guvi", limit=limit)`.

3. **Workspace Problem Solving Pipeline (`solve_problem`)**:
   - Every problem workspace at `https://www.guvi.in/code-kata/<slug>/` is self-contained.
   - Step 1: Navigating to the slug initiates a guardrail check via `hitl.check_and_handle_guardrails(page)` to guarantee R1 compliance if Cloudflare Turnstile or a re-auth modal appears.
   - Step 2: `solver.extractor.extract_problem_spec(page)` extracts title, description, and sample test cases.
   - Step 3: `solver.code_generator.generate_solution(spec)` synthesizes candidate Python 3 code.
   - Step 4: `solver.test_runner.test_solution(code, spec.sample_cases)` validates the candidate against sample test cases in an isolated subprocess before interacting with the browser.
   - Step 5: If the local test fails, the task is immediately recorded as `FAILED` (or `REDO`) with the exact mismatch error, preventing bogus browser submissions.
   - Step 6: If the local test passes, the language dropdown is verified (`PYTHON 3`), `solver.ace_adapter.wait_for_editor(page)` ensures editor readiness, and `solver.ace_adapter.inject_code(page, code)` injects the verified code via native CDP keyboard text insertion.
   - Step 7: Clicking `button.run-code` triggers execution; the driver awaits `#progress_modal` dismissal and confirms that test pills show `Correct Answer`.
   - Step 8: Clicking `button.submit-code` triggers submission; the driver validates positive feedback (`.question-status` containing `Solved!` or appearance of `#success_modal`).
   - Step 9: The driver updates `StateManager` with `status="COMPLETED"`, `result="PASSED"`, attempt count, execution duration, and metadata (points earned).

4. **Pipeline Orchestrator (`run_pipeline`)**:
   - Provides a single cohesive entrypoint: `login()` -> `discover_catalog(max_pages)` -> `list_pending(limit)` -> loop over pending `solve_problem()` -> `reporter.generate_all_reports()`.
   - Supports both single-problem execution (`task_id="odd-or-even-sum"`) and batch execution with configurable limits.
   - Plugs directly into `main.py` CLI command `run-codekata` and `run-all`.

---

## 3. Concrete Implementation Blueprint

### 3.1 `drivers/base_driver.py`
```python
"""
drivers/base_driver.py - Foundational Browser Automation Driver.
Provides common navigation, element interactions, safe retries, and HITL hooks.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Any, Optional, Dict, List

import config
from core.browser import BrowserManager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler
from core.reporter import SummaryReporter

logger = logging.getLogger("drivers.base")


class BaseDriver:
    """Abstract base platform driver managing browser lifecycle and safe actions."""

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
        reporter: Optional[SummaryReporter] = None,
    ):
        self.browser_manager = browser_manager or BrowserManager()
        self.state_manager = state_manager
        self.hitl_handler = hitl_handler or HitlHandler(interactive=True)
        self.reporter = reporter
        self._page: Optional[Any] = None

    @property
    def page(self) -> Any:
        """Returns the active Playwright page."""
        if self._page is None or getattr(self._page, "is_closed", lambda: True)():
            self._page = self.browser_manager.get_page()
        return self._page

    def navigate(self, url: str, force_reload: bool = False) -> None:
        """Navigates to URL using browser manager."""
        logger.info(f"Navigating to {url}")
        self._page = self.browser_manager.get_page(url=url, force_reload=force_reload)

    def check_guardrails(self, task_id: Optional[str] = None, context_desc: str = "Active Operation") -> bool:
        """Checks for bot detection, OTP, MFA, or security interstitials (R1)."""
        return self.hitl_handler.check_and_handle_guardrails(
            self.page, task_id=task_id, context_desc=context_desc
        )

    def safe_click(self, selector: str, timeout: float = 10.0, force: bool = False) -> bool:
        """Waits for element and clicks with error logging and screenshot capture."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=int(timeout * 1000))
            self.page.click(selector, timeout=int(timeout * 1000), force=force)
            return True
        except Exception as e:
            logger.warning(f"Failed to click selector '{selector}': {e}")
            self.browser_manager.save_screenshot(f"click_fail_{int(time.time())}", self.page)
            return False

    def safe_fill(self, selector: str, text: str, timeout: float = 10.0) -> bool:
        """Waits for input and fills text value."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=int(timeout * 1000))
            self.page.fill(selector, text, timeout=int(timeout * 1000))
            return True
        except Exception as e:
            logger.warning(f"Failed to fill selector '{selector}': {e}")
            return False

    def is_visible(self, selector: str, timeout: float = 2.0) -> bool:
        """Checks if selector is currently visible without throwing."""
        try:
            el = self.page.wait_for_selector(selector, state="visible", timeout=int(timeout * 1000))
            return el is not None
        except Exception:
            return False

    def dismiss_modals(self, selectors: Optional[List[str]] = None) -> None:
        """Dismisses generic popup or welcome modals."""
        close_selectors = selectors or [
            "button:has-text('✕')",
            "button:has-text('Close')",
            "button:has-text('close')",
            ".modal .btn-close",
            "dialog button.close",
        ]
        for sel in close_selectors:
            try:
                if self.is_visible(sel, timeout=0.5):
                    self.page.click(sel, timeout=1000)
                    time.sleep(0.3)
            except Exception:
                pass
```

---

### 3.2 `drivers/guvi_driver.py`
```python
"""
drivers/guvi_driver.py - Guvi CodeKata Autonomous Platform Driver.
Handles authentication, 143-page table discovery, completed SVG filtering,
Ace Editor code injection, Run/Submit verification, and state tracking.
"""

from __future__ import annotations
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
from core.hitl_handler import HitlHandler
from core.reporter import SummaryReporter
from drivers.base_driver import BaseDriver

from solver.extractor import extract_problem_spec, ProblemSpecification
from solver.code_generator import generate_solution, synthesize_solution, GeneratedSolution
from solver.test_runner import test_solution, ValidationResult
from solver.ace_adapter import wait_for_editor, inject_code, get_editor_code

logger = logging.getLogger("drivers.guvi")

# Canonical Selectors for Guvi CodeKata
SEL_LOGIN_EMAIL = "input#email, #email"
SEL_LOGIN_PWD = "input#password, #password"
SEL_LOGIN_CHECKBOX = "input#logged-in"
SEL_LOGIN_BTN = "a#login-btn, button#login-btn, .btn.login-btn"
SEL_ACCOUNT_MODAL = "#myModal, #sendmail"

SEL_TABLE_CONTAINER = "table, .table"
SEL_TABLE_ROWS = "tbody tr.cursor-pointer, tbody tr"
SEL_COMPLETED_SVG = 'svg g[clip-path*="completed-icon_svg__a"], svg path[fill="#0DBA4B"]'
SEL_PAGE_NEXT_BTN = 'button:has-text("Go to next page"), button.next-page'
SEL_PAGE_PREV_BTN = 'button:has-text("Go to previous page"), button.prev-page'
SEL_PAGE_PILLS = 'button.page-pill, .pagination-wrapper button'

SEL_ACE_EDITOR = "div#editor.ace_editor, #editor"
SEL_LANG_SELECT = "select#editorModeSelectDesktop"
SEL_LANG_MODAL_NO = "#reset_language_modal button:has-text('No')"
SEL_RUN_CODE_BTN = "button.run-code, button:has-text('Run Code')"
SEL_SUBMIT_CODE_BTN = "button.submit-code, button:has-text('Submit')"
SEL_PROGRESS_MODAL = "dialog#progress_modal, #progress_modal"
SEL_TEST_PILL_STATUS = ".test-pill-status, .test-results-pane"
SEL_QUESTION_STATUS = ".question-status"
SEL_SUCCESS_MODAL = "#success_modal, dialog.modal:has-text('Congratulations'), .modal:has-text('Geekoins')"


class GuviDriver(BaseDriver):
    """Autonomous platform driver for Guvi CodeKata."""

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
        reporter: Optional[SummaryReporter] = None,
    ):
        super().__init__(
            browser_manager=browser_manager,
            state_manager=state_manager,
            hitl_handler=hitl_handler,
            reporter=reporter,
        )

    # =========================================================================
    # 1. Authentication Lifecycle
    # =========================================================================

    def is_authenticated(self) -> bool:
        """Verifies whether the current browser session has a valid Guvi login."""
        try:
            # Check current cookies for authToken
            ctx = self.browser_manager.get_context()
            cookies = ctx.cookies()
            has_auth_cookie = any(c["name"] == "authToken" and c["value"].startswith("auth:") for c in cookies)
            if has_auth_cookie:
                return True

            # Alternatively, test page URL or localStorage
            self.navigate(config.GUVI_CODEKATA_URL)
            self.check_guardrails(task_id="guvi_auth_check", context_desc="Guvi Auth Verification")
            current_url = self.page.url
            if "/sign-in" not in current_url:
                return True
        except Exception as e:
            logger.debug(f"Auth check encountered exception: {e}")
        return False

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Authenticates to Guvi using configured credentials via visible browser.
        Handles guardrails, account verification modals, and session persistence.
        """
        eff_email = email or config.USER_EMAIL
        eff_password = password or config.USER_PASSWORD

        logger.info(f"Authenticating to Guvi as {eff_email}...")
        self.navigate(config.GUVI_LOGIN_URL)
        time.sleep(1.0)

        # If already logged in, platform redirects away from /sign-in/
        if "/sign-in" not in self.page.url:
            logger.info("Session already authenticated (redirected away from /sign-in/).")
            self.browser_manager.save_storage_state()
            return True

        # Check guardrails on login page
        self.check_guardrails(task_id="guvi_login", context_desc="Guvi Login Page")

        # Fill credentials
        self.safe_fill(SEL_LOGIN_EMAIL, eff_email)
        self.safe_fill(SEL_LOGIN_PWD, eff_password)

        # Ensure Keep Logged In is checked
        try:
            chk = self.page.query_selector(SEL_LOGIN_CHECKBOX)
            if chk and not chk.is_checked():
                chk.check()
        except Exception:
            pass

        # Click Login
        self.safe_click(SEL_LOGIN_BTN)
        time.sleep(2.0)

        # Check if Account Activation modal appeared (#myModal)
        if self.is_visible(SEL_ACCOUNT_MODAL, timeout=2.0):
            logger.warning("Guvi Account Activation Modal detected!")
            self.hitl_handler.check_and_handle_guardrails(
                self.page, task_id="guvi_activation", context_desc="Guvi Account Activation"
            )

        # Wait for navigation to complete away from sign-in
        try:
            self.page.wait_for_function(
                "() => !window.location.href.includes('/sign-in')",
                timeout=15000
            )
            logger.info("Successfully authenticated to Guvi platform.")
            self.dismiss_modals()
            self.browser_manager.save_storage_state()
            return True
        except Exception as e:
            logger.error(f"Login timeout or failed: {e}")
            self.check_guardrails(task_id="guvi_login_timeout", context_desc="Guvi Login Failure")
            return False

    # =========================================================================
    # 2. Catalog Discovery & Pending Filter
    # =========================================================================

    def _parse_current_table_page(self, page_num: int) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses all problem rows on the current catalog table page.
        Returns:
            Tuple of (all_task_dicts, pending_slugs)
        """
        self.page.wait_for_selector(SEL_TABLE_CONTAINER, state="visible", timeout=15000)
        time.sleep(0.5)  # Allow Qwik SSR hydration
        rows = self.page.query_selector_all(SEL_TABLE_ROWS)
        logger.info(f"Page {page_num}: Found {len(rows)} problem rows.")

        tasks_to_record: List[Dict[str, Any]] = []
        pending_slugs: List[str] = []

        for idx, row in enumerate(rows, 1):
            try:
                # Column 0: Status SVG
                col0 = row.query_selector("td:nth-child(1)")
                is_completed = False
                if col0:
                    svg_html = col0.inner_html() or ""
                    if "#completed-icon_svg__a" in svg_html or "#0DBA4B" in svg_html:
                        is_completed = True

                # Column 1: Title & Slug
                col1 = row.query_selector("td:nth-child(2), td.problem-title")
                title_raw = col1.inner_text().strip() if col1 else f"Problem {idx}"

                # Extract or derive slug
                data_slug = row.get_attribute("data-slug")
                link_el = row.query_selector("a[href*='/code-kata/']")
                href_slug = ""
                if link_el:
                    href = link_el.get_attribute("href") or ""
                    m = re.search(r'/code-kata/([^/]+)', href)
                    if m:
                        href_slug = m.group(1)

                if data_slug:
                    slug = data_slug
                elif href_slug:
                    slug = href_slug
                else:
                    # Clean title: strip leading numbering like "1. "
                    cleaned_title = re.sub(r"^\d+\.\s*", "", title_raw)
                    slug = re.sub(r"[^a-z0-9]+", "-", cleaned_title.lower()).strip("-")

                # Column 2: Success Rate
                col2 = row.query_selector("td:nth-child(3), td.success-rate")
                success_rate = col2.inner_text().strip() if col2 else ""

                # Column 3: Difficulty
                col3 = row.query_selector("td:nth-child(4), td.difficulty")
                difficulty = col3.inner_text().strip() if col3 else "Easy"

                # Column 4: Points
                col4 = row.query_selector("td:nth-child(5), td.points")
                points = col4.inner_text().strip() if col4 else "30"

                task_id = f"guvi-{slug}"
                task_url = f"https://www.guvi.in/code-kata/{slug}/"

                status = TaskStatus.COMPLETED.value if is_completed else TaskStatus.DISCOVERED.value
                result = TaskResult.SOLVED.value if is_completed else TaskResult.UNATTEMPTED.value
                attempts = 1 if is_completed else 0

                task_dict = {
                    "task_id": task_id,
                    "platform": "guvi",
                    "task_category": "CodeKata",
                    "title": title_raw,
                    "url": task_url,
                    "status": status,
                    "attempt_count": attempts,
                    "result": result,
                    "failure_reason": None,
                    "next_action": "NONE" if is_completed else "SOLVE_AND_SUBMIT",
                    "metadata": {
                        "slug": slug,
                        "difficulty": difficulty,
                        "points": points,
                        "success_rate": success_rate,
                        "page_number": page_num,
                    }
                }
                tasks_to_record.append(task_dict)

                if not is_completed:
                    pending_slugs.append(slug)

            except Exception as e:
                logger.warning(f"Error parsing problem row {idx} on page {page_num}: {e}")

        return tasks_to_record, pending_slugs

    def discover_catalog(self, max_pages: int = 143, limit_pending: Optional[int] = None) -> List[str]:
        """
        Crawls the CodeKata catalog across pages 1 to max_pages.
        Filters completed via `#completed-icon_svg__a`.
        Batch records all items into SQLite StateManager.
        Returns list of discovered pending problem slugs.
        """
        self.navigate(config.GUVI_CODEKATA_URL)
        self.dismiss_modals()

        all_discovered_tasks: List[Dict[str, Any]] = []
        all_pending_slugs: List[str] = []

        for current_page in range(1, max_pages + 1):
            logger.info(f"Scraping CodeKata catalog page {current_page}/{max_pages}...")
            tasks, pending = self._parse_current_table_page(current_page)
            all_discovered_tasks.extend(tasks)
            all_pending_slugs.extend(pending)

            # Check if pending limit reached
            if limit_pending and len(all_pending_slugs) >= limit_pending:
                logger.info(f"Target limit of {limit_pending} pending problems discovered.")
                break

            # If last page, stop
            if current_page >= max_pages:
                break

            # Navigate to next page via Next button
            next_btn = self.page.query_selector(SEL_PAGE_NEXT_BTN)
            if not next_btn or next_btn.get_attribute("disabled") is not None:
                logger.info("Reached final catalog page (Next button disabled or absent).")
                break

            self.safe_click(SEL_PAGE_NEXT_BTN)
            time.sleep(1.0)  # Human cadence / Qwik hydration

        # Atomic bulk persistence to SQLite StateManager
        if self.state_manager and all_discovered_tasks:
            count = self.state_manager.batch_record_tasks(all_discovered_tasks)
            logger.info(f"Successfully recorded {count} CodeKata tasks into SQLite StateManager.")

        return all_pending_slugs

    # =========================================================================
    # 3. Workspace Problem Solving Pipeline (`solve_problem`)
    # =========================================================================

    def solve_problem(self, slug_or_id: str) -> Dict[str, Any]:
        """
        Autonomous Problem Solving Pipeline for a single CodeKata problem.
        1. Navigates to `/code-kata/<slug>/`
        2. Security challenge check via `hitl.check_and_handle_guardrails(page)`
        3. Extracts ProblemSpec via `solver.extractor.extract_problem_spec(page)`
        4. Synthesizes Python 3 code via `solver.code_generator.generate_solution(spec)`
        5. Validates locally in subprocess sandbox via `solver.test_runner.test_solution`
        6. Injects into Ace Editor via `solver.ace_adapter.inject_code`
        7. Clicks Run Code and verifies execution feedback
        8. Clicks Submit Code and confirms `Solved!` positive feedback
        9. Records state in `StateManager`
        """
        slug = slug_or_id.replace("guvi-", "").strip("/")
        task_id = f"guvi-{slug}"
        workspace_url = f"https://www.guvi.in/code-kata/{slug}/"
        start_time = time.time()

        logger.info(f"=== Starting solve pipeline for '{slug}' ({task_id}) ===")

        # Record IN_PROGRESS in StateManager
        if self.state_manager:
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS.value,
                next_action="EXTRACTING_AND_SOLVING",
            )

        # 1. Navigate to problem workspace
        self.navigate(workspace_url)
        self.dismiss_modals()

        # 2. Guardrail Check (R1)
        if self.check_guardrails(task_id=task_id, context_desc=f"Solving CodeKata {slug}"):
            logger.info("Guardrail was detected and cleared by human.")

        # 3. Extract Problem Specification
        spec: ProblemSpecification = extract_problem_spec(self.page)
        spec.slug = slug
        logger.info(f"Extracted spec: Title='{spec.title}', SampleCases={len(spec.sample_cases)}")

        # 4. Synthesize Python 3 Solution
        sol: GeneratedSolution = generate_solution(spec)
        logger.info(f"Synthesized solution: Category='{sol.category}', Confidence={sol.confidence:.2f}")

        # 5. Local Subprocess Sandbox Validation
        val_result: ValidationResult = test_solution(
            sol.code,
            spec.sample_cases,
            timeout=config.LOCAL_TEST_TIMEOUT_SECONDS
        )

        if not val_result.all_passed:
            duration = time.time() - start_time
            err_msg = val_result.error_message or "Local test case output mismatch"
            logger.error(f"Local sandbox validation FAILED for {slug}: {err_msg}")

            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.TEST_FAILED.value,
                    failure_reason=err_msg,
                    next_action="REVISE_SOLVER_TEMPLATE",
                    increment_attempts=True,
                    time_spent_seconds=duration,
                    code_snapshot=sol.code,
                )
            return {"success": False, "task_id": task_id, "error": err_msg, "stage": "LOCAL_SANDBOX"}

        logger.info("Local sandbox validation PASSED for all sample cases.")

        # 6. Ensure Language is PYTHON 3
        try:
            lang_sel = self.page.query_selector(SEL_LANG_SELECT)
            if lang_sel:
                current_val = self.page.evaluate("(el) => el.value", lang_sel)
                if current_val != "PYTHON 3":
                    logger.info("Switching workspace language to PYTHON 3...")
                    self.page.select_option(SEL_LANG_SELECT, "PYTHON 3")
                    # If reset modal appears, dismiss it with "No"
                    time.sleep(0.5)
                    if self.is_visible(SEL_LANG_MODAL_NO, timeout=1.0):
                        self.safe_click(SEL_LANG_MODAL_NO)
        except Exception as e:
            logger.debug(f"Language selector handling note: {e}")

        # 7. Ace Editor Readiness & Code Injection
        if not wait_for_editor(self.page, timeout=10.0):
            err_msg = "Ace Editor failed to reach ready state"
            logger.error(err_msg)
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                )
            return {"success": False, "task_id": task_id, "error": err_msg, "stage": "ACE_INJECTION"}

        inject_success = inject_code(self.page, sol.code, verify=True)
        if not inject_success:
            err_msg = "Failed to inject solution code into Ace Editor"
            logger.error(err_msg)
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                )
            return {"success": False, "task_id": task_id, "error": err_msg, "stage": "ACE_INJECTION"}

        time.sleep(0.5)

        # 8. Run Code Execution & Feedback Verification
        logger.info("Triggering Run Code execution...")
        self.safe_click(SEL_RUN_CODE_BTN)

        # Wait for #progress_modal to finish/close
        try:
            self.page.wait_for_selector(
                SEL_PROGRESS_MODAL, state="hidden", timeout=20000
            )
        except Exception:
            pass

        # Check for Wrong in test result pills
        time.sleep(1.0)
        try:
            results_pane = self.page.query_selector(SEL_TEST_PILL_STATUS)
            if results_pane:
                text = results_pane.inner_text()
                if "Wrong" in text:
                    err_msg = f"Platform Run Code returned 'Wrong': {text}"
                    logger.warning(err_msg)
                    if self.state_manager:
                        self.state_manager.update_task_status(
                            task_id=task_id,
                            status=TaskStatus.FAILED.value,
                            result=TaskResult.TEST_FAILED.value,
                            failure_reason=err_msg,
                            increment_attempts=True,
                            time_spent_seconds=time.time() - start_time,
                        )
                    return {"success": False, "task_id": task_id, "error": err_msg, "stage": "RUN_CODE"}
        except Exception as e:
            logger.debug(f"Test results pane check: {e}")

        # 9. Submit Code Execution & Platform Verification
        logger.info("Submitting solution to platform...")
        self.safe_click(SEL_SUBMIT_CODE_BTN)
        time.sleep(2.0)

        # Verify positive submission feedback
        duration = time.time() - start_time
        verified_solved = False
        earned_points = 30

        # Check .question-status for "Solved!"
        try:
            status_el = self.page.query_selector(SEL_QUESTION_STATUS)
            if status_el and "solved" in status_el.inner_text().lower():
                verified_solved = True
        except Exception:
            pass

        # Check modal for Congratulations / Geekoins
        if not verified_solved:
            try:
                modal = self.page.query_selector(SEL_SUCCESS_MODAL)
                if modal and modal.is_visible():
                    verified_solved = True
                    m_text = modal.inner_text()
                    pts_m = re.search(r'\+(\d+)\s*Geekoins', m_text)
                    if pts_m:
                        earned_points = int(pts_m.group(1))
            except Exception:
                pass

        # Fallback check: wait up to 10s for Solved status
        if not verified_solved:
            try:
                self.page.wait_for_function(
                    """() => {
                        const qs = document.querySelector('.question-status');
                        const modal = document.querySelector('#success_modal, .modal');
                        const isSolved = qs && qs.textContent.toLowerCase().includes('solved');
                        const modalVisible = modal && modal.style.display !== 'none' && modal.textContent.includes('Geekoins');
                        return isSolved || modalVisible;
                    }""",
                    timeout=10000
                )
                verified_solved = True
            except Exception:
                pass

        if verified_solved:
            logger.info(f"🎉 Problem '{slug}' successfully solved and verified! (+{earned_points} points)")
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED.value,
                    result=TaskResult.PASSED.value,
                    failure_reason=None,
                    next_action="NONE",
                    increment_attempts=True,
                    time_spent_seconds=duration,
                    code_snapshot=sol.code,
                    metadata_update={"points_earned": earned_points}
                )
            return {"success": True, "task_id": task_id, "slug": slug, "duration": duration, "points": earned_points}
        else:
            err_msg = "Submission did not yield positive 'Solved!' verification feedback"
            logger.warning(err_msg)
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                    increment_attempts=True,
                    time_spent_seconds=duration,
                )
            return {"success": False, "task_id": task_id, "error": err_msg, "stage": "SUBMISSION_VERIFY"}

    # =========================================================================
    # 4. Pipeline Orchestrator (`run_pipeline`)
    # =========================================================================

    def run_pipeline(
        self,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        task_id: Optional[str] = None,
        max_pages: int = 143,
    ) -> Dict[str, Any]:
        """
        Complete end-to-end Guvi CodeKata automation lifecycle:
        1. Authentication / session restore
        2. Target discovery / pending filter
        3. Problem execution loop with sandbox & verification
        4. Summary report generation
        """
        logger.info("Starting Guvi CodeKata Automation Pipeline...")

        # 1. Ensure authenticated
        if not self.is_authenticated():
            login_success = self.login()
            if not login_success:
                logger.error("Authentication failed. Aborting CodeKata pipeline.")
                return {"success": False, "reason": "AUTH_FAILED"}

        # 2. Resolve target problems
        pending_slugs: List[str] = []

        if task_id:
            # Single problem targeted
            clean_slug = task_id.replace("guvi-", "").strip("/")
            pending_slugs = [clean_slug]
        else:
            # Discovered or pending problems from catalog
            logger.info("Discovering catalog problems...")
            pending_slugs = self.discover_catalog(max_pages=max_pages, limit_pending=limit)

        total_to_solve = len(pending_slugs) if limit is None else min(len(pending_slugs), limit)
        logger.info(f"CodeKata Execution Queue: {total_to_solve} problem(s) to solve.")

        completed_count = 0
        failed_count = 0

        # 3. Execution Loop
        for idx, slug in enumerate(pending_slugs[:total_to_solve], 1):
            logger.info(f"[{idx}/{total_to_solve}] Processing problem '{slug}'...")
            res = self.solve_problem(slug)
            if res.get("success"):
                completed_count += 1
            else:
                failed_count += 1

            # Human cadence delay between problems
            time.sleep(1.5)

        # 4. Generate Reports
        if self.reporter:
            md_path, json_path = self.reporter.generate_all_reports()
            self.reporter.print_terminal_summary()
            logger.info(f"Generated summary reports:\n  Markdown: {md_path}\n  JSON: {json_path}")

        return {
            "success": True,
            "total_attempted": total_to_solve,
            "completed": completed_count,
            "failed": failed_count,
        }
```

---

### 3.3 `drivers/__init__.py`
```python
"""
drivers - Platform Automation Drivers for Guvi CodeKata and ZenClass.
"""

from drivers.base_driver import BaseDriver
from drivers.guvi_driver import GuviDriver

__all__ = [
    "BaseDriver",
    "GuviDriver",
]
```

---

### 3.4 Integration with `main.py`
In `main.py` lines 279-281:
```python
            elif self.args.command == "run-codekata":
                logger.info(f"Executing CodeKata automation (category={self.args.category}, limit={self.args.limit})...")
                from drivers.guvi_driver import GuviDriver
                driver = GuviDriver(
                    browser_manager=self.browser_manager,
                    state_manager=self.state_manager,
                    hitl_handler=self.hitl_handler,
                    reporter=self.reporter
                )
                driver.run_pipeline(
                    limit=self.args.limit,
                    category=self.args.category,
                    task_id=self.args.task_id
                )
```
And in `run-all` (lines 276-278):
```python
            if self.args.command == "run-all":
                logger.info("Executing run-all automation pipeline across Guvi and ZenClass...")
                from drivers.guvi_driver import GuviDriver
                guvi_driver = GuviDriver(
                    browser_manager=self.browser_manager,
                    state_manager=self.state_manager,
                    hitl_handler=self.hitl_handler,
                    reporter=self.reporter
                )
                guvi_driver.run_pipeline(limit=self.args.limit)
```

---

### 3.5 Milestone 3 Test Suite Design (`tests/test_m3_guvi.py`)
To ensure bulletproof reliability and adherence to the zero-error testing standard, the following test classes should be added in `tests/test_m3_guvi.py`:
1. `TestGuviAuthentication`:
   - Valid credential login and `authToken` cookie persistence.
   - Rejection on invalid credentials with 401 error.
   - Bypass if already authenticated (`/sign-in/` redirect).
   - `#myModal` account activation modal detection and HITL triggering.
2. `TestGuviCatalogDiscovery`:
   - HTML table row parsing (5 columns).
   - `#completed-icon_svg__a` solved vs pending classification.
   - Derivation of slug and title normalization.
   - Pagination button detection (`button.next-page`, 143 pages).
   - Batch recording into `StateManager` and verify SQLite task records.
3. `TestGuviWorkspacePipeline`:
   - Problem spec extraction from workspace DOM.
   - Code synthesis and local subprocess sandbox execution.
   - Local test failure halts browser submission and records failure in StateManager.
   - Ace Editor injection via CDP keyboard adapter.
   - Run Code button click and execution feedback parsing.
   - Submit Code button click and positive `Solved!` verification.
   - Verification of all 9 R3 fields updated in StateManager.
4. `TestGuviPipelineOrchestrator`:
   - `run_pipeline(limit=3)` executing full mock lifecycle.
   - Single task targeted execution (`task_id="odd-or-even-sum"`).
   - Summary report generation (`SUMMARY_REPORT.md` and `summary.json`).

---

## 4. Caveats

1. **Backend Run Code Queue Latency**: Guvi's execution endpoint (`POST /code-kata/question/run`) can take between 3 and 15 seconds during peak server hours. The timeout for `#progress_modal` to close must be set to at least 20 seconds to prevent premature failure.
2. **Qwik SSR Client Hydration**: Guvi's catalog page is built with Qwik SSR. Table rows `tbody tr` become clickable and active only after hydration. When paginating via `button.next-page`, a small 500ms delay (`time.sleep(0.5)`) ensures the DOM has updated before parsing rows.
3. **Language Switch Confirmation Dialog**: If the language is switched from default to `PYTHON 3` and the code editor was previously modified, Guvi launches `<dialog id="reset_language_modal">`. The driver must inspect and dismiss this dialog with `"No"` if it appears.
4. **Already Solved Problems**: When navigating to an already completed problem, the platform UI displays `.question-status` with `Solved!` and `30` points immediately. Re-submitting an already solved problem awards `+0 Geekoins` but verifies successfully.

---

## 5. Conclusion

The Guvi CodeKata automation architecture is fully mapped, verified against live survey data, and organized into clean, modular components:
- `BaseDriver` handles safe navigation, safe clicks/fills, modal dismissal, screenshot capture, and HITL hooks.
- `GuviDriver` cleanly separates into 4 distinct phases:
  1. Authentication (`login`, `is_authenticated`)
  2. 143-page Catalog Discovery & SVG status filtering (`discover_catalog`, `batch_record_tasks`)
  3. Single-problem solving pipeline with local sandbox pre-check (`solve_problem`)
  4. Full lifecycle pipeline orchestration with report generation (`run_pipeline`)
- Ready for immediate implementation in Milestone 3.

---

## 6. Verification Method

To independently verify the blueprint against the codebase and test harness:

1. **Verify Existing Solver & Foundation Tests**:
   ```bash
   python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py
   ```
   *Expected Output*: Ran 54+ tests, 0 failures, 0 errors.

2. **Verify E2E Feature Coverage for M3 Features (F09, F10, F11)**:
   ```bash
   python3 tests/e2e/test_runner.py --feature F09
   python3 tests/e2e/test_runner.py --feature F10
   python3 tests/e2e/test_runner.py --feature F11
   ```
   *Expected Output*: All 3 feature test suites pass.

3. **Verify E2E Pairwise & Workload Tests**:
   ```bash
   python3 -m unittest tests/e2e/tier3_pairwise/test_p01_auth_to_discovery.py
   python3 -m unittest tests/e2e/tier3_pairwise/test_p02_discovery_to_solver_sandbox.py
   python3 -m unittest tests/e2e/tier4_workloads/test_w01_guvi_codekata_e2e.py
   ```
   *Expected Output*: All pairwise and multi-problem workload tests pass.
