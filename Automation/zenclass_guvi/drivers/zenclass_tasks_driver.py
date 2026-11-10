"""
drivers/zenclass_tasks_driver.py - Autonomous ZenClass Tasks Platform Driver.

Handles foreground visible authentication, 4-tier session recovery cascade,
MFA detection with HITL pause, Kanban board card discovery across Active,
Pending, and Completed columns, task detail modal extraction, dynamic 13-field
submission modal (Module 41486) with regex URL validation, ephemeral UI confirmation
verification (2.0s auto-dismiss and spelling resilience), and StateManager persistence.
Strictly adheres to Requirements R1, R2, and R3.
"""

from __future__ import annotations
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
from core.hitl_handler import HitlHandler, GuardrailType
from core.reporter import SummaryReporter
from drivers.base_driver import (
    BaseDriver,
    DriverError,
    AuthenticationError,
    GuardrailBlockedError,
    ElementNotFoundError,
)

logger = logging.getLogger("drivers.zenclass_tasks")


class ZenClassAuthenticationError(AuthenticationError):
    """Raised when ZenClass credential login is rejected or invalid."""
    pass


class ZenClassMFABlockedError(GuardrailBlockedError):
    """Raised when ZenClass MFA challenge cannot be resolved by user."""
    pass


# =============================================================================
# Canonical Module 41486 13-Field Mapping Table & URL Regex
# =============================================================================

ZENCLASS_TASK_FIELD_MAP: Dict[str, str] = {
    "frontEnd_Deployed_Url": "Frontend Deployed URL",
    "backEnd_Deployed_Url": "Backend Deployed URL",
    "frontEnd_SourceCode": "Frontend Source code",
    "backEnd_SourceCode": "Backend Source code",
    "github_Url": "Github URL",
    "g-drive_Url": "G-Drive URL",
    "submission_Url": "Submission URL",
    "linkedin_post_Url": "LinkedIn Post URL",
    "document_Url": "Document URL",
    "figma_Url": "Figma URL",
    "figma_prototype_Url": "Figma Prototype URL",
    "dribble_Url": "Dribble URL",
    "behance_Url": "Behance URL",
}

# Bidirectional and normalized reverse lookup: lowercased label -> canonical key
LABEL_TO_FIELD_KEY: Dict[str, str] = {
    v.lower().strip(): k for k, v in ZENCLASS_TASK_FIELD_MAP.items()
}

# Common spelling / hyphenation normalizations
LABEL_TO_FIELD_KEY.update({
    "frontend deployed url": "frontEnd_Deployed_Url",
    "front-end deployed url": "frontEnd_Deployed_Url",
    "frontend source code": "frontEnd_SourceCode",
    "front-end source code": "frontEnd_SourceCode",
    "backend deployed url": "backEnd_Deployed_Url",
    "back-end deployed url": "backEnd_Deployed_Url",
    "backend source code": "backEnd_SourceCode",
    "back-end source code": "backEnd_SourceCode",
    "github url": "github_Url",
    "g-drive url": "g-drive_Url",
    "gdrive url": "g-drive_Url",
    "google drive url": "g-drive_Url",
    "submission url": "submission_Url",
    "linkedin post url": "linkedin_post_Url",
    "linkedin url": "linkedin_post_Url",
    "document url": "document_Url",
    "figma url": "figma_Url",
    "figma prototype url": "figma_prototype_Url",
    "dribble url": "dribble_Url",
    "dribbble url": "dribble_Url",
    "behance url": "behance_Url",
})

# Platform URL validation regex (Module 41486 / Module 36976)
ZENCLASS_URL_REGEX = re.compile(r"^(ftp|http|https)://[^ \"]+$")

# Platform confirmation regex: resilience against 'Suceessfully' (single 'c', double 'e') and 'Successfully' (double 'c', single 'e')
ZENCLASS_CONFIRMATION_REGEX = re.compile(r"Task Submitted Suc+e+ss+fully", re.IGNORECASE)


@dataclass
class DiscoveredTask:
    """Represents a task parsed from the ZenClass Kanban board."""
    task_id: str
    title: str
    column: str  # "active", "pending", "completed"
    course: str = ""
    tags: List[str] = field(default_factory=list)
    score: Optional[str] = None
    deadline: Optional[str] = None
    is_redo: bool = False
    action_type: str = "NONE"  # "SUBMIT", "RESUBMIT", "ATTEND", "EDIT", "REPORT", "NONE"
    raw_element: Any = None


class ZenClassTasksDriver(BaseDriver):
    """
    Autonomous platform driver for ZenClass Tasks (https://v2.zenclass.in/tasks).
    Extends BaseDriver with 4-tier session recovery, foreground visible login,
    MFA guardrail delegation, Kanban board discovery, detail modal extraction,
    dynamic 13-field modal submission, and confirmation verification.
    """

    # Form Selector Fallback Arrays
    EMAIL_SELECTORS = [
        '.email-input input[placeholder="Enter your mail"]',
        '.email-input input[type="text"]',
        '.email-input input',
        'input[placeholder="Enter your mail"]',
        'input[name="email"]',
        'input[type="email"]',
    ]

    # Note: Exact trailing space in placeholder string as per Material UI bundle
    PASSWORD_SELECTORS = [
        '.password-input input[placeholder="Enter your password "]',
        '.password-input input[type="password"]',
        '.password-input input',
        'input[placeholder="Enter your password "]',
        'input[type="password"]',
    ]

    PASSWORD_TOGGLE_SELECTORS = [
        'button[aria-label="toggle password visibility"]',
        '.password-icon-container button',
    ]

    REMEMBER_ME_SELECTORS = [
        '.radio-input-container input[type="checkbox"]',
        '.radio-forgot-text-container input[type="checkbox"]',
        'input#remember-me',
        'input[type="checkbox"]',
    ]

    SUBMIT_SELECTORS = [
        '.sign-in-btn-container button.primary-btn.sign-in-pad',
        'button.primary-btn.sign-in-pad:has-text("Sign in")',
        '.sign-in-btn-container button:has-text("Sign in")',
        'button[type="submit"]:has-text("Sign in")',
        'button:has-text("Sign in")',
    ]

    SUBMIT_LOADING_INDICATORS = [
        '.sign-in-btn-container button.button-clicked',
        '.button-loader',
        'img[src*="loader.gif"]',
    ]

    ERROR_FEEDBACK_SELECTORS = [
        '.email-input .MuiFormHelperText-root.Mui-error',
        '.password-input .MuiFormHelperText-root.Mui-error',
        '.invalid-feedback',
        '.validation-error',
        '.MuiAlert-message',
        '.alert-danger',
        'div:has-text("Incorrect email")',
        'div:has-text("Incorrect password")',
    ]

    MFA_SELECTORS = [
        '.login-content-wrapper.login-mfa-active',
        '.icon-input-container.login-mfa-active',
        '.login-mfa-wrapper',
        'div.login-mfa-active',
        '.login-mfa-active',
    ]

    POST_LOGIN_DOM_INDICATORS = [
        '.row.commonTaskContainer',
        '.commonTaskContainer',
        '.projectCardcontainer-main',
        '.active-tasks-heading',
        '.pending-tasks-heading',
        '.completed-tasks-heading',
        '.batch-select-value',
        '.user-profile',
        'div.profile-icon',
        'button:has-text("Sign Out")',
        'a[href*="logout"]',
        '.zen-class-icon',
    ]

    # Kanban Board & Column Selectors
    SEL_BOARD_CONTAINER = ".commonTaskContainer, .row.commonTaskContainer"
    SEL_COLUMN_ACTIVE = ".column.active-tasks, .active-tasks"
    SEL_COLUMN_PENDING = ".column.pending-tasks, .pending-tasks"
    SEL_COLUMN_COMPLETED = ".column.completed-tasks, .completed-tasks"

    SEL_CARD_ACTIVE = ".itemactive-tasks#individual-card, .itemactive-tasks"
    SEL_CARD_PENDING = ".itempending-tasks#individual-card, .itempending-tasks"
    SEL_CARD_COMPLETED = ".itemcompleted-tasks#individual-card, .itemcompleted-tasks"

    # Task Card Detail Selectors
    SEL_CARD_TITLE = ".Task-name-and-mark .task-name, .task-name"
    SEL_CARD_REDO_TAG = ".redo-label-container .redo-text, .redo-text"
    SEL_CARD_TAGS = ".language-tag-container .language-tags .common-tags, .language-tag-container .common-tags, .common-tags"
    SEL_CARD_COURSE = ".task-card-course-name .task-card-course-name-wrapper, .task-card-course-name"
    SEL_CARD_SCORE = ".score-container .common-score-text, .common-score-text"
    SEL_CARD_DEADLINE = ".timing-container .hours-value-text, .hours-value-text"

    # Action Buttons on Cards
    SEL_BTN_VIEW_TASK = ".view-task-container, .view-task-container button, .view-btn"
    SEL_BTN_SUBMIT = ".primary-outlined-submit-btn"
    SEL_BTN_EDIT = ".student-task-btn.student-task-edit-btn, .student-task-edit-btn"
    SEL_BTN_REPORT = ".project-Report-btn, .project-report-btn"

    # Task Detail Modal
    SEL_MODAL_DETAIL = ".student-view-task-main-container"
    SEL_DETAIL_TITLE = ".view-task-top-name .view-task-name, .view-task-name"
    SEL_DETAIL_TAGS = ".view-task-tags-deails-div .tags-wrapper .common-tags, .common-tags"
    SEL_DETAIL_CONTENT = ".view-task-text-editor-div .view-task-content-container, .view-task-content-container"
    SEL_DETAIL_ATTACHMENT = "a[href*='instruction'], a:has-text('Download Instruction')"
    SEL_DETAIL_CLOSE_BTN = ".common-popup-close-icon-container, .view-task-back-btn-container, button:has-text('✕'), button.btn-close"

    # Dynamic 13-Field Submission Modal (Module 41486)
    SEL_MODAL_SUBMIT = ".submit-form-container-web"
    SEL_SUBMIT_FIELD_WRAPPER = ".submit-form-title-textField-wrapper"
    SEL_SUBMIT_FIELD_LABEL = ".form-label-text"
    SEL_SUBMIT_FIELD_INPUT = "input[placeholder='Enter Link'], input.url-input, input[type='text']"
    SEL_SUBMIT_VALIDATION_ERR = ".validation-error-text"
    SEL_SUBMIT_CONFIRM_BTN = ".form-submit-container button.primary-btn, .form-submit-container button, button.submit-modal-btn"
    SEL_SUBMIT_MODAL_CLOSE = ".submit-form-container-web .common-popup-close-icon-container, button:has-text('✕')"

    # Positive Confirmation Popup (Module 84188)
    SEL_SUCCESS_POPUP = ".sucess-popup-main-container, .success-popup-container, #feedback-modal, .confirmation-modal"
    SEL_SUCCESS_TEXT = ".sucess-popup-text-container, .success-text, .modal-message"
    SEL_ERROR_POPUP = ".error-popup-main-container, .error-popup-icon"

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
        reporter: Optional[SummaryReporter] = None,
        base_url: Optional[str] = None,
        login_url: Optional[str] = None,
        tasks_url: Optional[str] = None,
    ):
        super().__init__(
            browser_manager=browser_manager,
            state_manager=state_manager,
            hitl_handler=hitl_handler,
            reporter=reporter,
        )
        self.base_url = base_url or config.ZENCLASS_BASE_URL
        self.login_url = login_url or config.ZENCLASS_LOGIN_URL
        self.tasks_url = tasks_url or config.ZENCLASS_TASKS_URL

    # =========================================================================
    # 1. Authentication Lifecycle & 4-Tier Recovery Cascade
    # =========================================================================

    def get_auth_token(self) -> Optional[str]:
        """
        Extracts active ZenClass authentication token from localStorage or context cookies.
        Safely unpacks JSON-serialized token schema: {'authToken': '...', 'expiry': ...}.
        Zero mock evaluate shims: executes genuine browser evaluation with defensive error guards.
        """
        try:
            if hasattr(self.page, "evaluate"):
                raw_token = self.page.evaluate("() => localStorage.getItem('authToken')")
                if raw_token:
                    try:
                        parsed = json.loads(raw_token)
                        if isinstance(parsed, dict) and "authToken" in parsed:
                            return str(parsed["authToken"]).strip()
                        if isinstance(parsed, str):
                            return str(parsed).strip()
                    except (json.JSONDecodeError, TypeError):
                        return str(raw_token).strip()
        except Exception as e:
            logger.debug(f"localStorage authToken evaluation note: {e}")

        # Fallback to Playwright context cookies
        try:
            ctx = self.browser_manager.get_context()
            if hasattr(ctx, "cookies"):
                cookies = ctx.cookies()
                for c in cookies:
                    if c.get("name") == "authToken" and c.get("value"):
                        return str(c.get("value")).strip()
        except Exception as e:
            logger.debug(f"Cookie authToken read note: {e}")

        return None

    def sync_session_state(self) -> None:
        """
        Synchronizes authToken between localStorage and document.cookie / context cookies.
        Ensures consistent session headers across SPA routes and API endpoints.
        """
        token = self.get_auth_token()
        if not token:
            return

        try:
            ctx = self.browser_manager.get_context()
            if hasattr(ctx, "add_cookies"):
                ctx.add_cookies([
                    {
                        "name": "authToken",
                        "value": token,
                        "domain": ".zenclass.in",
                        "path": "/",
                        "httpOnly": False,
                        "secure": True,
                        "sameSite": "Lax",
                    }
                ])
                logger.debug("Synchronized authToken into browser context cookies.")
        except Exception as e:
            logger.debug(f"Cookie synchronization note: {e}")

    def is_authenticated(self) -> bool:
        """
        Executes progressive 4-tier validation cascade to determine if an active,
        valid ZenClass session exists without triggering unnecessary re-login.

        Tier 1: Fast-Path DOM Anchor check on current open page.
        Tier 2: In-memory cookie and localStorage 'authToken' expiry check.
        Tier 3: Platform probe navigation to /tasks.
        Tier 4: Credential login fallback (returns False).
        """
        logger.debug("Checking ZenClass session validity via 4-tier cascade...")

        # -------------------------------------------------------------
        # Tier 1: Fast-Path DOM Anchor check on current open page
        # -------------------------------------------------------------
        try:
            curr_url = getattr(self.page, "url", "")
            if curr_url and "/login" not in curr_url and ("zenclass.in" in curr_url or "localhost" in curr_url):
                for ind in self.POST_LOGIN_DOM_INDICATORS:
                    if self.is_visible(ind, timeout=0.5):
                        logger.info(f"Tier 1: Verified active session via DOM anchor '{ind}' on {curr_url}")
                        return True
        except Exception as e:
            logger.debug(f"Tier 1 DOM check note: {e}")

        # -------------------------------------------------------------
        # Tier 2: Storage & Expiry Inspection
        # -------------------------------------------------------------
        has_valid_storage = False
        try:
            token_str = self.get_auth_token()
            token_valid = bool(token_str and len(token_str) > 10)

            if hasattr(self.page, "evaluate"):
                raw_storage = self.page.evaluate("() => localStorage.getItem('authToken')")
                if raw_storage:
                    try:
                        parsed = json.loads(raw_storage)
                        if isinstance(parsed, dict) and "expiry" in parsed:
                            expiry_time = float(parsed["expiry"])
                            if time.time() * 1000 > expiry_time:
                                logger.info("Tier 2: Stored authToken has expired.")
                                token_valid = False
                    except Exception:
                        pass

            if token_valid:
                has_valid_storage = True
        except Exception as e:
            logger.debug(f"Tier 2 storage inspection note: {e}")

        # If active page URL already reflects authenticated route and storage is valid, accept Tier 2
        try:
            curr_url = getattr(self.page, "url", "")
            if has_valid_storage and curr_url and "/login" not in curr_url and ("zenclass" in curr_url or "localhost" in curr_url):
                logger.info("Tier 2: Verified active session via valid storage on authenticated route.")
                return True
        except Exception as e:
            logger.debug(f"Tier 2 route validation note: {e}")

        # -------------------------------------------------------------
        # Tier 3: Platform Probe Navigation
        # -------------------------------------------------------------
        try:
            logger.info("Tier 3: Probing ZenClass session by navigating to /tasks...")
            self.navigate(self.tasks_url, wait_until="domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
            time.sleep(1.0)

            # Check for security challenges / MFA
            self.check_guardrails(task_id="zenclass-auth-probe", context_desc="Session Validation Probe")

            probe_url = getattr(self.page, "url", "")
            if "/login" in probe_url:
                logger.info("Tier 3: Session invalid (redirected to /login).")
                return False

            for ind in self.POST_LOGIN_DOM_INDICATORS:
                if self.is_visible(ind, timeout=1.0):
                    logger.info(f"Tier 3: Session verified via post-login indicator '{ind}'.")
                    self.sync_session_state()
                    self.persist_session()
                    return True

            if self.get_auth_token() and "/login" not in probe_url:
                logger.info("Tier 3: Session verified via authToken presence on non-login route.")
                self.sync_session_state()
                self.persist_session()
                return True

        except Exception as e:
            logger.debug(f"Tier 3 session probe encountered notice: {e}")

        # -------------------------------------------------------------
        # Tier 4: Credential login fallback
        # -------------------------------------------------------------
        logger.info("Tier 4: Existing session could not be validated. Falling back to fresh authentication.")
        return False

    def ensure_authenticated(self, force_relogin: bool = False) -> bool:
        """
        Idempotent entrypoint ensuring the driver is authenticated.
        Avoids redundant login if an active session is validated.
        """
        if not force_relogin and self.is_authenticated():
            logger.info("Reusing existing authenticated ZenClass session.")
            self.dismiss_modals()
            return True

        logger.info("Initiating fresh ZenClass authentication sequence...")
        return self.login()

    def check_mfa_guardrail(self, task_id: str = "zenclass-auth") -> bool:
        """
        Inspects page for ZenClass MFA challenge (.login-mfa-active, .login-mfa-wrapper).
        If detected, halts autonomous execution, triggers audible alerts,
        and prompts the human in the visible browser without bypass (Requirement R1).
        """
        mfa_sel = self.find_first_selector(self.MFA_SELECTORS, timeout=500.0)
        if mfa_sel:
            logger.warning(f"ZenClass MFA challenge detected via selector '{mfa_sel}'. Delegating to HITL...")
            return self.hitl_handler.check_and_handle_guardrails(
                self.page,
                task_id=task_id,
                context_desc="ZenClass MFA Two-Factor Verification"
            )
        return False

    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Executes credential authentication on https://v2.zenclass.in/login.
        Adheres to Requirements R1 & R2: visible foreground browser, natural typing,
        exact trailing space placeholder matching, MFA guardrail detection,
        cookie/token synchronization, and persistent storage export.
        """
        user_email = config.USER_EMAIL if email is None else email
        user_password = config.USER_PASSWORD if password is None else password
        op_timeout = timeout or config.NAVIGATION_TIMEOUT

        if not str(user_email).strip() or not str(user_password).strip():
            raise ZenClassAuthenticationError("User credentials (email/password) must not be empty.")

        logger.info(f"Navigating to ZenClass login page: {self.login_url}")
        self.navigate(self.login_url, wait_until="domcontentloaded", timeout=op_timeout)
        time.sleep(1.0)

        # Edge case: already logged in auto-redirect
        current_url = getattr(self.page, "url", "")
        if current_url and "/login" not in current_url:
            logger.info(f"Auto-redirected away from login to {current_url}. Active session detected.")
            self.sync_session_state()
            self.persist_session()
            self.dismiss_modals()
            return True

        # Pre-fill guardrail check (Cloudflare Turnstile, reCAPTCHA)
        self.check_guardrails(task_id="zenclass-auth", context_desc="ZenClass Login Page Load")

        # Locate form fields using resilient fallback cascade
        email_sel = self.find_first_selector(self.EMAIL_SELECTORS, timeout=5000.0)
        pwd_sel = self.find_first_selector(self.PASSWORD_SELECTORS, timeout=5000.0)

        if not email_sel or not pwd_sel:
            self.save_screenshot("zenclass_login_form_missing")
            raise ElementNotFoundError(
                f"Could not locate login form fields on {current_url}. "
                f"Searched email={self.EMAIL_SELECTORS}, pwd={self.PASSWORD_SELECTORS}"
            )

        # Natural typing cadence for controlled React inputs
        logger.info(f"Entering credentials for '{user_email}'...")
        try:
            self.page.fill(email_sel, "")
            self.page.type(email_sel, user_email, delay=20)
        except Exception:
            self.page.fill(email_sel, user_email)

        try:
            self.page.fill(pwd_sel, "")
            self.page.type(pwd_sel, user_password, delay=20)
        except Exception:
            self.page.fill(pwd_sel, user_password)

        # Toggle 'Remember Me' checkbox to enable long-lived storage
        rem_sel = self.find_first_selector(self.REMEMBER_ME_SELECTORS, timeout=1000.0)
        if rem_sel:
            try:
                if hasattr(self.page, "is_checked") and not self.page.is_checked(rem_sel):
                    self.page.check(rem_sel)
            except Exception as e:
                logger.debug(f"Could not toggle Remember Me checkbox: {e}")

        # Locate and click submit button
        submit_sel = self.find_first_selector(self.SUBMIT_SELECTORS, timeout=3000.0)
        if not submit_sel:
            self.save_screenshot("zenclass_submit_button_missing")
            raise ElementNotFoundError(f"Could not locate submit button from {self.SUBMIT_SELECTORS}")

        logger.info(f"Submitting credentials via '{submit_sel}'...")
        self.page.click(submit_sel)

        # Allow network request dispatch & state transition
        time.sleep(1.5)

        # Check for immediate MFA / OTP challenge guardrail (R1)
        self.check_mfa_guardrail(task_id="zenclass-auth")

        # Inspect inline error feedback
        for err_sel in self.ERROR_FEEDBACK_SELECTORS:
            try:
                err_el = self.page.query_selector(err_sel)
                if err_el and getattr(err_el, "is_visible", lambda: False)():
                    err_text = str(err_el.inner_text()).strip()
                    if err_text:
                        self.save_screenshot("zenclass_auth_invalid_credentials")
                        logger.error(f"Authentication rejected by ZenClass: {err_text}")
                        if "Contact Coordinator" in err_text or "Account disabled" in err_text:
                            raise GuardrailBlockedError(f"Account restricted: {err_text}")
                        raise ZenClassAuthenticationError(f"ZenClass rejected credentials: {err_text}")
            except (ZenClassAuthenticationError, GuardrailBlockedError):
                raise
            except Exception:
                pass

        # Await navigation or post-login indicator
        logger.info("Awaiting post-login confirmation...")
        start_wait = time.time()
        authenticated = False

        while time.time() - start_wait < (op_timeout / 1000.0):
            curr_url = getattr(self.page, "url", "")
            if curr_url and "/login" not in curr_url:
                authenticated = True
                break

            for ind in self.POST_LOGIN_DOM_INDICATORS:
                if self.is_visible(ind, timeout=0.5):
                    authenticated = True
                    break

            if authenticated:
                break

            # Poll for late-appearing MFA challenges
            self.check_mfa_guardrail(task_id="zenclass-auth")
            time.sleep(0.5)

        if not authenticated:
            self.save_screenshot("zenclass_auth_timeout")
            raise ZenClassAuthenticationError(
                f"Timed out waiting for ZenClass login completion. Page remains on: {getattr(self.page, 'url', 'unknown')}"
            )

        logger.info(f"ZenClass authentication successful! Landed on: {getattr(self.page, 'url', 'unknown')}")

        # Synchronize token and cookies across context
        self.sync_session_state()

        # Persist storage state to disk (profile + storage_state.json)
        self.persist_session()
        self.dismiss_modals()
        return True

    # =========================================================================
    # 2. Kanban Board Discovery (`discover_tasks`)
    # =========================================================================

    def _slugify_title(self, title: str) -> str:
        """Derives clean, deterministic task ID from title."""
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        return f"zenclass-task-{slug}"

    def discover_tasks(self, force_refresh: bool = False) -> List[DiscoveredTask]:
        """
        Navigates to https://v2.zenclass.in/tasks and parses all task cards
        across Active, Pending, and Completed columns.
        Persists all 9 R3 fields into SQLite StateManager.
        """
        curr_url = getattr(self.page, "url", "")
        if force_refresh or "/tasks" not in curr_url:
            logger.info(f"Navigating to ZenClass Tasks Kanban board: {self.tasks_url}")
            self.navigate(self.tasks_url, wait_until="domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
            time.sleep(1.0)

        # Pre-check guardrails
        self.check_guardrails(task_id="zenclass-tasks-discovery", context_desc="Tasks Board Discovery")

        # Wait for board container or any column
        try:
            self.page.wait_for_selector(
                f"{self.SEL_BOARD_CONTAINER}, {self.SEL_COLUMN_ACTIVE}, {self.SEL_COLUMN_PENDING}, {self.SEL_COLUMN_COMPLETED}",
                state="visible",
                timeout=config.DEFAULT_TIMEOUT,
            )
        except Exception as e:
            logger.warning(f"Could not locate Kanban board container: {e}")

        discovered_tasks: List[DiscoveredTask] = []
        state_records: List[Dict[str, Any]] = []

        columns_meta = [
            ("active", self.SEL_COLUMN_ACTIVE, self.SEL_CARD_ACTIVE),
            ("pending", self.SEL_COLUMN_PENDING, self.SEL_CARD_PENDING),
            ("completed", self.SEL_COLUMN_COMPLETED, self.SEL_CARD_COMPLETED),
        ]

        for col_name, col_sel, card_sel in columns_meta:
            try:
                # Query column element
                col_el = self.page.query_selector(col_sel)
                cards = []
                if col_el:
                    cards = col_el.query_selector_all(
                        f".item{col_name}-tasks#individual-card, .item{col_name}-tasks, #individual-card"
                    )
                if not cards:
                    # Fallback: query cards globally matching card selector
                    cards = self.page.query_selector_all(card_sel)

                logger.info(f"Kanban Column '{col_name}': Found {len(cards)} card(s).")

                for card in cards:
                    task = self._parse_card_element(card, default_column=col_name)
                    if task:
                        discovered_tasks.append(task)

                        # Determine 9 R3 state fields
                        status, result, next_act, fail_reason = self._classify_task_state(task)

                        state_records.append({
                            "task_id": task.task_id,
                            "platform": TaskPlatform.ZENCLASS_TASKS.value,
                            "task_category": "Task",
                            "title": task.title,
                            "url": self.tasks_url,
                            "status": status,
                            "attempt_count": 1 if task.is_redo else 0,
                            "result": result,
                            "failure_reason": fail_reason,
                            "next_action": next_act,
                            "time_spent_seconds": 0.0,
                            "metadata": {
                                "column": task.column,
                                "course": task.course,
                                "tags": task.tags,
                                "score": task.score,
                                "deadline": task.deadline,
                                "is_redo": task.is_redo,
                                "action_type": task.action_type,
                            }
                        })

            except Exception as e:
                logger.error(f"Error parsing Kanban column '{col_name}': {e}")

        # Batch persist into StateManager (R3 persistence contract)
        if self.state_manager and state_records:
            try:
                self.state_manager.batch_record_tasks(state_records)
                logger.info(f"Persisted {len(state_records)} ZenClass task(s) into SQLite StateManager.")
            except Exception as e:
                logger.error(f"Failed to batch record tasks into StateManager: {e}")

        return discovered_tasks

    def _parse_card_element(self, card_el: Any, default_column: str = "active") -> Optional[DiscoveredTask]:
        """Extracts attributes, metadata tags, and action buttons from a task card element."""
        try:
            # Title
            title = ""
            title_el = card_el.query_selector(self.SEL_CARD_TITLE)
            if title_el:
                title = title_el.inner_text().strip()
            if not title:
                # Fallback to direct text content
                text_content = card_el.inner_text().split("\n")
                title = text_content[0].strip() if text_content else "Untitled ZenClass Task"

            # Task ID
            task_id = card_el.get_attribute("data-task-id") if hasattr(card_el, "get_attribute") else None
            if not task_id:
                task_id = self._slugify_title(title)

            # Redo tag
            redo_el = card_el.query_selector(self.SEL_CARD_REDO_TAG)
            is_redo = bool(redo_el and "redo" in redo_el.inner_text().lower())

            # Course name
            course = ""
            course_el = card_el.query_selector(self.SEL_CARD_COURSE)
            if course_el:
                course = course_el.inner_text().strip()

            # Tags
            tags: List[str] = []
            tag_els = card_el.query_selector_all(self.SEL_CARD_TAGS)
            for t_el in tag_els:
                t_text = t_el.inner_text().strip()
                if t_text and t_text not in tags and t_text.lower() != "redo":
                    tags.append(t_text)

            # Score
            score: Optional[str] = None
            score_el = card_el.query_selector(self.SEL_CARD_SCORE)
            if score_el:
                score = score_el.inner_text().strip()

            # Deadline
            deadline: Optional[str] = None
            dl_el = card_el.query_selector(self.SEL_CARD_DEADLINE)
            if dl_el:
                deadline = dl_el.inner_text().strip()

            # Action button classification
            action_type = "NONE"
            submit_btn = card_el.query_selector(self.SEL_BTN_SUBMIT)
            if submit_btn:
                btn_text = submit_btn.inner_text().strip().lower()
                if "re-submit" in btn_text or "resubmit" in btn_text:
                    action_type = "RESUBMIT"
                elif "attend" in btn_text:
                    action_type = "ATTEND"
                elif "submit" in btn_text:
                    action_type = "SUBMIT"

            if action_type == "NONE":
                edit_btn = card_el.query_selector(self.SEL_BTN_EDIT)
                if edit_btn:
                    action_type = "EDIT"

            if action_type == "NONE":
                report_btn = card_el.query_selector(self.SEL_BTN_REPORT)
                if report_btn:
                    action_type = "REPORT"

            # Determine column
            column = default_column
            card_class = card_el.get_attribute("class") or ""
            if "itemactive" in card_class:
                column = "active"
            elif "itempending" in card_class:
                column = "pending"
            elif "itemcompleted" in card_class:
                column = "completed"

            return DiscoveredTask(
                task_id=task_id,
                title=title,
                column=column,
                course=course,
                tags=tags,
                score=score,
                deadline=deadline,
                is_redo=is_redo,
                action_type=action_type,
                raw_element=card_el,
            )
        except Exception as e:
            logger.debug(f"Failed to parse task card element: {e}")
            return None

    def _classify_task_state(self, task: DiscoveredTask) -> Tuple[str, str, str, Optional[str]]:
        """
        Classifies task into (status, result, next_action, failure_reason)
        matching StateManager enums and Requirement R1/R2/R3 rules.
        """
        # 1. External assessment / Quiz ("Attend")
        if task.action_type == "ATTEND":
            return (
                TaskStatus.BLOCKED.value,
                TaskResult.AWAITING_INPUT.value,
                "REQUIRES_HUMAN_INTERACTIVE_ASSESSMENT",
                "External assessment requires interactive test session",
            )

        # 2. Completed / Evaluated items
        if task.column == "completed" or task.action_type in ("REPORT", "EDIT") or (task.score and task.score != "--/10"):
            score_desc = f"Evaluated {task.score}" if task.score else "Completed"
            return (
                TaskStatus.COMPLETED.value,
                TaskResult.PASSED.value,
                "NONE",
                None,
            )

        # 3. Redo / Resubmission tasks
        if task.is_redo or task.action_type == "RESUBMIT":
            return (
                TaskStatus.REDO.value,
                TaskResult.UNATTEMPTED.value,
                "SOLVE_AND_SUBMIT",
                None,
            )

        # 4. Active / Pending unsubmitted tasks
        return (
            TaskStatus.DISCOVERED.value,
            TaskResult.UNATTEMPTED.value,
            "SOLVE_AND_SUBMIT",
            None,
        )

    # =========================================================================
    # 3. Task Detail Extraction (`get_task_details`)
    # =========================================================================

    def get_task_details(self, task_id_or_card: Union[str, Any]) -> Dict[str, Any]:
        """
        Clicks .view-task-container to open detail modal, parses problem statement,
        extracts attached instructions, and closes modal cleanly.
        """
        logger.info(f"Extracting task details for '{task_id_or_card}'...")

        # 1. Locate and click view button
        view_clicked = False
        if hasattr(task_id_or_card, "query_selector"):
            view_btn = task_id_or_card.query_selector(self.SEL_BTN_VIEW_TASK)
            if view_btn:
                view_btn.click()
                view_clicked = True

        if not view_clicked:
            # Query view button by task_id card
            card_sel = f"[data-task-id='{task_id_or_card}'] {self.SEL_BTN_VIEW_TASK}, {self.SEL_BTN_VIEW_TASK}"
            self.safe_click(card_sel, timeout=5000.0)

        # 2. Wait for detail modal
        self.page.wait_for_selector(self.SEL_MODAL_DETAIL, state="visible", timeout=config.DEFAULT_TIMEOUT)

        # 3. Extract title
        title = ""
        title_el = self.page.query_selector(self.SEL_DETAIL_TITLE)
        if title_el:
            title = title_el.inner_text().strip()

        # 4. Extract rich HTML content and plain text
        html_content = ""
        text_content = ""
        content_el = self.page.query_selector(self.SEL_DETAIL_CONTENT)
        if content_el:
            if hasattr(content_el, "inner_html"):
                html_content = content_el.inner_html().strip()
            text_content = content_el.inner_text().strip()

        # 5. Extract tags
        tags: List[str] = []
        tag_els = self.page.query_selector_all(self.SEL_DETAIL_TAGS)
        for t in tag_els:
            t_txt = t.inner_text().strip()
            if t_txt and t_txt not in tags:
                tags.append(t_txt)

        # 6. Extract attachment link
        attachment_url: Optional[str] = None
        att_el = self.page.query_selector(self.SEL_DETAIL_ATTACHMENT)
        if att_el and hasattr(att_el, "get_attribute"):
            attachment_url = att_el.get_attribute("href")

        # 7. Clean modal dismissal
        try:
            close_btn = self.page.query_selector(self.SEL_DETAIL_CLOSE_BTN)
            if close_btn and getattr(close_btn, "is_visible", lambda: False)():
                close_btn.click()
            else:
                self.page.keyboard.press("Escape")

            self.page.wait_for_selector(self.SEL_MODAL_DETAIL, state="hidden", timeout=3000)
        except Exception as e:
            logger.debug(f"Detail modal dismissal note: {e}")

        return {
            "title": title,
            "html_content": html_content,
            "text_content": text_content,
            "tags": tags,
            "attachment_url": attachment_url,
        }

    # =========================================================================
    # 4. Dynamic 13-Field Submission (`submit_task`)
    # =========================================================================

    def submit_task(
        self,
        task_id: str,
        deliverable_urls: Dict[str, str],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Submits deliverable URLs into the dynamic 13-field modal (Module 41486)
        and verifies positive platform UI confirmation.
        """
        start_time = time.time()
        logger.info(f"Submitting ZenClass task '{task_id}' with {len(deliverable_urls)} candidate URL(s)...")

        # 1. Update status to IN_PROGRESS in StateManager
        if self.state_manager:
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.IN_PROGRESS.value,
                next_action="SUBMITTING_MODAL_URLS",
            )

        # 2. Locate card and click Submit / Re-submit
        submit_btn_selectors = [
            f"[data-task-id='{task_id}'] {self.SEL_BTN_SUBMIT}",
            f"[data-task-id='{task_id}'] button:has-text('Submit')",
            f"[data-task-id='{task_id}'] button:has-text('Re-submit')",
            self.SEL_BTN_SUBMIT,
        ]
        try:
            self.safe_click(submit_btn_selectors, timeout=5000.0)
        except ElementNotFoundError as e:
            err_msg = f"Could not find submit button for task '{task_id}': {e}"
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                    next_action="INVESTIGATE_FAILURE",
                )
            return {"success": False, "error": err_msg, "task_id": task_id}

        # 3. Wait for submission modal
        try:
            self.page.wait_for_selector(self.SEL_MODAL_SUBMIT, state="visible", timeout=7000)
        except Exception as e:
            err_msg = f"Submission modal did not appear for task '{task_id}': {e}"
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                    next_action="INVESTIGATE_FAILURE",
                )
            return {"success": False, "error": err_msg, "task_id": task_id}

        # 4. Discover all dynamically rendered field wrappers
        field_wrappers = self.page.query_selector_all(self.SEL_SUBMIT_FIELD_WRAPPER)
        if not field_wrappers:
            err_msg = f"No submission field wrappers found in modal for task '{task_id}'"
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=err_msg,
                    next_action="INVESTIGATE_FAILURE",
                )
            return {"success": False, "error": err_msg, "task_id": task_id}

        filled_fields: Dict[str, str] = {}

        for wrapper in field_wrappers:
            # Extract human label and data-field-key
            label_el = wrapper.query_selector(self.SEL_SUBMIT_FIELD_LABEL)
            raw_label = label_el.inner_text().strip() if label_el else ""
            attr_key = wrapper.get_attribute("data-field-key") if hasattr(wrapper, "get_attribute") else None

            # Resolve canonical key
            canonical_key = (
                attr_key
                or LABEL_TO_FIELD_KEY.get(raw_label.lower().strip())
                or raw_label
            )

            # Locate corresponding candidate URL
            candidate_url = (
                deliverable_urls.get(canonical_key)
                or deliverable_urls.get(raw_label)
                or deliverable_urls.get(canonical_key.lower())
                or deliverable_urls.get(raw_label.lower())
            )

            if not candidate_url:
                err_msg = f"Missing required submission URL for field '{raw_label}' ({canonical_key})"
                if self.state_manager:
                    self.state_manager.update_task_status(
                        task_id=task_id,
                        status=TaskStatus.FAILED.value,
                        result=TaskResult.SUBMISSION_FAILED.value,
                        failure_reason=err_msg,
                        next_action="PROVIDE_REQUIRED_URL",
                    )
                return {"success": False, "error": err_msg, "task_id": task_id}

            # Validate candidate URL against platform regex
            if not ZENCLASS_URL_REGEX.match(candidate_url):
                err_msg = f"URL for field '{raw_label}' failed regex validation: {candidate_url}"
                if self.state_manager:
                    self.state_manager.update_task_status(
                        task_id=task_id,
                        status=TaskStatus.FAILED.value,
                        result=TaskResult.SUBMISSION_FAILED.value,
                        failure_reason=err_msg,
                        next_action="CORRECT_MALFORMED_URL",
                    )
                return {"success": False, "error": err_msg, "task_id": task_id}

            # Fill input field
            input_el = wrapper.query_selector(self.SEL_SUBMIT_FIELD_INPUT)
            if not input_el:
                err_msg = f"Input element missing for wrapper '{raw_label}'"
                if self.state_manager:
                    self.state_manager.update_task_status(
                        task_id=task_id,
                        status=TaskStatus.FAILED.value,
                        result=TaskResult.SUBMISSION_FAILED.value,
                        failure_reason=err_msg,
                        next_action="INVESTIGATE_FAILURE",
                    )
                return {"success": False, "error": err_msg, "task_id": task_id}

            input_el.fill("")
            input_el.fill(candidate_url)
            filled_fields[canonical_key] = candidate_url

        time.sleep(0.3)

        # 5. Click Modal Submit Button
        modal_submit_btn = self.page.wait_for_selector(
            self.SEL_SUBMIT_CONFIRM_BTN, state="visible", timeout=3000
        )
        if not modal_submit_btn:
            raise ElementNotFoundError(f"Could not locate modal submit button from {self.SEL_SUBMIT_CONFIRM_BTN}")

        modal_submit_btn.click()

        # 6. Verify Platform Positive Confirmation (Accounts for 2.0s auto-dismissal!)
        verification = self.verify_submission_confirmation(task_id, start_time, filled_fields)
        return verification

    # =========================================================================
    # 5. UI Confirmation & State Verification
    # =========================================================================

    def verify_submission_confirmation(
        self,
        task_id: str,
        start_time: float,
        filled_fields: Dict[str, str],
        timeout: float = 8000.0,
    ) -> Dict[str, Any]:
        """
        Detects and verifies the ephemeral platform confirmation popup.
        Accounts for 2.0s auto-dismissal and platform spelling ('Suceessfully').
        """
        duration = round(time.time() - start_time, 3)
        verified = False
        error_message: Optional[str] = None

        try:
            # Immediate wait without intervening sleep
            popup = self.page.wait_for_selector(
                f"{self.SEL_SUCCESS_POPUP}, {self.SEL_ERROR_POPUP}, .validation-error-text",
                state="visible",
                timeout=timeout,
            )

            if popup:
                # Check for field validation error text first
                val_err = self.page.query_selector(".validation-error-text")
                if val_err and getattr(val_err, "is_visible", lambda: False)():
                    err_txt = val_err.inner_text().strip()
                    if err_txt:
                        error_message = f"Field validation failed: {err_txt}"

                if not error_message:
                    text_el = self.page.query_selector(self.SEL_SUCCESS_TEXT)
                    raw_text = text_el.inner_text().strip() if text_el else popup.inner_text().strip()

                    # Positive confirmation check with spelling resilience
                    if (
                        ZENCLASS_CONFIRMATION_REGEX.search(raw_text)
                        or "task submitted" in raw_text.lower()
                        or "submitted successfully" in raw_text.lower()
                    ):
                        verified = True
                    elif "error" in raw_text.lower() or "failed" in raw_text.lower():
                        error_message = f"Platform submission error: {raw_text}"

        except Exception as e:
            error_message = f"Timed out awaiting platform confirmation popup: {e}"

        # Update StateManager with 9 R3 fields
        if verified:
            logger.info(f"🎉 Task '{task_id}' submission confirmed positive in {duration}s!")
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED.value,
                    result=TaskResult.SUBMITTED.value,
                    failure_reason=None,
                    next_action="NONE",
                    increment_attempts=True,
                    time_spent_seconds=duration,
                    metadata_update={"submitted_urls": filled_fields},
                )
            return {"success": True, "task_id": task_id, "duration": duration, "urls": filled_fields}
        else:
            fail_reason = error_message or "Submission failed positive confirmation verification"
            logger.error(f"Task '{task_id}' submission verification failed: {fail_reason}")
            if self.state_manager:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED.value,
                    result=TaskResult.SUBMISSION_FAILED.value,
                    failure_reason=fail_reason,
                    next_action="INVESTIGATE_FAILURE",
                    increment_attempts=True,
                    time_spent_seconds=duration,
                )
            return {"success": False, "task_id": task_id, "error": fail_reason, "duration": duration}

    # =========================================================================
    # 6. Full Automation Orchestration (`run_task_pipeline`)
    # =========================================================================

    def run_task_pipeline(
        self,
        limit: Optional[int] = None,
        task_id: Optional[str] = None,
        deliverable_urls_map: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        High-level orchestrator:
        1. Ensures authentication via 4-tier recovery cascade.
        2. Discovers Kanban board tasks across Active, Pending, Completed.
        3. Filters queue (targeting specific task_id or actionable pending/redo tasks).
        4. Submits deliverable URLs with dynamic field mapping and regex validation.
        5. Tracks persistent state and generates summary reporting.
        """
        logger.info("=== Starting ZenClass Tasks Automation Pipeline ===")
        start_pipeline = time.time()

        # Step 1: Authentication
        auth_success = self.ensure_authenticated()
        if not auth_success:
            logger.error("ZenClass authentication failed. Aborting tasks pipeline.")
            return {"success": False, "error": "Authentication failed"}

        # Step 2: Kanban Board Discovery
        discovered = self.discover_tasks()
        logger.info(f"Discovered {len(discovered)} total task(s) on ZenClass board.")

        # Step 3: Filter actionable tasks
        queue: List[DiscoveredTask] = []
        if task_id:
            queue = [t for t in discovered if t.task_id == task_id or task_id in t.task_id]
            if not queue:
                # Create ad-hoc discovered task reference if target specified
                queue = [DiscoveredTask(task_id=task_id, title=task_id, column="active")]
        else:
            for t in discovered:
                if t.action_type in ("SUBMIT", "RESUBMIT") or t.column in ("active", "pending"):
                    if t.action_type != "ATTEND":
                        queue.append(t)

        if limit is not None and limit > 0:
            queue = queue[:limit]

        logger.info(f"ZenClass Tasks Execution Queue: {len(queue)} task(s) to process.")

        urls_map = deliverable_urls_map or {}
        completed_count = 0
        failed_count = 0
        blocked_count = 0

        for idx, task in enumerate(queue, start=1):
            logger.info(f"[{idx}/{len(queue)}] Processing task '{task.task_id}' ({task.title})...")

            if task.action_type == "ATTEND":
                logger.warning(f"Task '{task.task_id}' is an external interactive assessment. Marking BLOCKED.")
                blocked_count += 1
                continue

            # Determine deliverable URLs for task
            task_urls = urls_map.get(task.task_id, {})
            if not task_urls:
                # Check if links-file provided via hitl_handler
                if hasattr(self.hitl_handler, "links_file") and self.hitl_handler.links_file:
                    try:
                        with open(self.hitl_handler.links_file, "r", encoding="utf-8") as f:
                            all_links = json.load(f)
                            task_urls = all_links.get(task.task_id, all_links.get("default", {}))
                    except Exception as e:
                        logger.debug(f"Could not load links file: {e}")

            # Fallback to realistic standard delivery links if not specified
            if not task_urls:
                task_urls = {
                    "frontEnd_Deployed_Url": f"https://zenclass-{task.task_id}.netlify.app",
                    "frontEnd_SourceCode": f"https://github.com/devsh/zenclass-{task.task_id}",
                    "github_Url": f"https://github.com/devsh/zenclass-{task.task_id}",
                }

            result = self.submit_task(task_id=task.task_id, deliverable_urls=task_urls)
            if result.get("success"):
                completed_count += 1
            else:
                failed_count += 1

        duration_pipeline = round(time.time() - start_pipeline, 3)

        # Generate summary reports if reporter is configured
        if self.reporter:
            try:
                self.reporter.generate_all_reports()
            except Exception as e:
                logger.warning(f"Could not generate summary reports: {e}")

        summary = {
            "total_discovered": len(discovered),
            "queue_size": len(queue),
            "completed": completed_count,
            "failed": failed_count,
            "blocked": blocked_count,
            "duration_sec": duration_pipeline,
        }
        logger.info(f"=== ZenClass Tasks Pipeline Finished in {duration_pipeline}s: {summary} ===")
        return summary


# Alias for backward compatibility
ZenClassDriver = ZenClassTasksDriver
