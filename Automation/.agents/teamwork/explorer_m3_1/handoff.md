# Handoff Report: Blueprint for Guvi Authentication & Session Management (`drivers/guvi_driver.py`)

**Date**: 2026-11-10T16:10:00Z  
**Agent ID**: `explorer_m3_1`  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_1`  
**Subject**: Architectural blueprint and production-ready implementation plan for Guvi Authentication and Session Management in Milestone 3 (`drivers/guvi_driver.py` & `drivers/base_driver.py`).  
**Handoff Type**: Hard (Task Complete)

---

## 1. Observation

Direct inspection of the repository, reverse-engineering survey findings, existing Milestone 1 & 2 infrastructure, and test suites revealed the following concrete facts:

### 1.1 Platform Endpoints & Credential Specifications
- **Login URL**: `https://www.guvi.in/sign-in/` (`config.GUVI_LOGIN_URL`, `config.py:37`).
- **CodeKata URL**: `https://www.guvi.in/code-kata/` (`config.GUVI_CODEKATA_URL`, `config.py:38`).
- **User Credentials**: 
  - Email: `devsh.pareek@gmail.com` (`config.USER_EMAIL`, `config.py:32`, derived from `ORIGINAL_REQUEST.md:14`).
  - Password: `Dev@99#$%esh` (`config.USER_PASSWORD`, `config.py:33`, derived from `ORIGINAL_REQUEST.md:14`).
- **Backend Authentication Endpoint**: `POST /usercheck.php` (observed in `new-sign-in.js` and `spec_miner_survey_2/handoff.md:58`, mocked in `tests/e2e/harness/mock_server.py:68`).
  - Payload: `{"emails": "devsh.pareek@gmail.com", "password": "...", "loggedInType": "loggedInUser"}`.
  - Successful response: `{"status": "success", "authToken": "auth:<hash>", "cusername": "Devesh Pareek", "userpoints": 2195}`.
  - Invalid credentials response: HTTP 401 with `{"status": "fail", "message": "Incorrect Email or Password"}`.

### 1.2 Form Selectors (Live Production DOM & Fixtures)
From live DOM reverse engineering (`spec_miner_survey_2/handoff.md:67-73`) and test harness (`dom_fixtures.py:11-38`):
- **Email Field**:
  - Live DOM: `input#email` (enclosed within `#emailgroup`).
  - Semantic / alternative selectors: `#login_email`, `input[type="email"]`, `input[name="email"]`.
- **Password Field**:
  - Live DOM: `input#password` (enclosed within `#passwordGroup`).
  - Semantic / alternative selectors: `#login_password`, `input[type="password"]`, `input[name="password"]`.
- **Keep Logged In Checkbox**:
  - Live DOM: `input#logged-in` (class `form-check-input`).
- **Submit Button**:
  - Live DOM: `a#login-btn.btn.login-btn` (desktop) and `a#mobile-login.login-btn` (mobile).
  - Semantic / alternative selectors: `#login_button`, `button[type="submit"]`, `button:has-text("Login")`, `a:has-text("Login")`.
- **Error Feedback**:
  - `#emailgroup > .invalid-feedback` and `#passwordGroup > .invalid-feedback` containing `"Incorrect Email or Password"`.
  - Input field marked with class `.is-invalid`.

### 1.3 Post-Login Indicators & Session Markers
- **URL Redirection**: Navigation moves away from `/sign-in/` to `https://www.guvi.in/`, `/courses`, `/code-kata/`, or `/dashboard`.
- **DOM Indicators**:
  - User avatar: `.user-avatar`, `div.profile-icon`, `a[href*="profile"]`.
  - User wallet / points: `#user_wallet_points`, `.user-points-badge`.
  - Sign-out trigger: `a[href*="sign-out"]`, `button:has-text("Sign Out")`.
  - Sign-in buttons (`#login-btn`, `a[href*="/sign-in/"]`) are removed or hidden.
- **Cookies**:
  - `authToken`: Formatted as `auth:<128-hex-chars>`.
  - `mail`: `devsh.pareek@gmail.com`.
  - `cusername`: `Devesh Pareek`.
  - `userpoints`: integer string (e.g., `"2195"`).
  - `isZenUser`: `"true"`.
- **LocalStorage**:
  - Keys: `authToken`, `loginSuccess` (`"true"`), `mail`, `userpoints`, `rank`.

### 1.4 Guardrails & HITL Infrastructure (`core/hitl_handler.py`)
`core/hitl_handler.py:54-103` defines registered `GUARDRAIL_RULES`:
1. `CLOUDFLARE_TURNSTILE`: `iframe[src*='challenges.cloudflare.com'], div.cf-turnstile, #cf-stage, #challenge-stage, div[id*='cf-turnstile']` and page title containing `"Just a moment..."` or `"Attention Required!"`.
2. `RECAPTCHA`: `iframe[src*='google.com/recaptcha'], iframe[src*='recaptcha/api2/anchor'], div.g-recaptcha, script[src*='recaptcha/api.js']`.
3. `GUVI_ACTIVATION_MODAL`: `#myModal, #myModal #sendmail, div.modal:has(#sendmail)` (Account activation gate).
4. `OTP_CHALLENGE`: `input[name*='otp' i], input[placeholder*='OTP' i], #otp, input[autocomplete='one-time-code']`.
5. `ACCOUNT_RESTRICTION`: `div:has-text('Account disabled'), div:has-text('Contact Coordinator')`.

When `hitl.check_and_handle_guardrails(page)` triggers:
- Emits 3 audible terminal bells (`\a` with 150ms delay).
- Renders an ANSI yellow boxed message on `sys.stderr`.
- Enters interactive loop waiting for the user to solve the challenge in the visible browser.
- Automatically re-verifies that the guardrail selector is cleared before resuming execution.
- Updates `state_manager` status to `BLOCKED` with reason, then resets to `IN_PROGRESS` upon resolution.

### 1.5 Browser Lifecycle & Persistence (`core/browser.py`)
`core/browser.py` provides:
- Persistent headed context via `launch_persistent_context(user_data_dir=str(self.profile_dir), headless=False, ...)` using `.browser_profile/`.
- Dual-layer cookie persistence:
  - Layer 1: Native Chromium SQLite cookie storage inside `.browser_profile/Default/Cookies`.
  - Layer 2: Explicit serialization via `browser_manager.save_storage_state()` dumping active cookies and localStorage to `data/storage_state.json`.
  - Layer 2 injection on startup via `browser_manager._restore_storage_state()` (`core/browser.py:125-137`).

---

## 2. Logic Chain

1. **Need for Idempotent Session Verification Before Login**:
   - *Observation*: Guvi immediately 302-redirects away from `/sign-in/` if valid session cookies exist (`spec_miner_survey_2/handoff.md:44`). Submitting credentials when already authenticated is redundant, adds latency, and risks triggering anti-bot heuristics.
   - *Logic*: `GuviDriver` must implement `is_authenticated()` and `ensure_authenticated()`. Before attempting credential input, it must probe the browser context cookies for `authToken` and navigate to a protected page (e.g., `GUVI_CODEKATA_URL`). If the page loads without redirecting to `/sign-in/`, the driver recognizes the active session immediately.

2. **Cascade Selector Resolution Strategy**:
   - *Observation*: Live production DOM uses `input#email`, `input#password`, `a#login-btn`, whereas dispatch prompts and standard web specs also anticipate `#login_email`, `input[type="email"]`, `#login_password`, `input[type="password"]`, `#login_button`, `button[type="submit"]`.
   - *Logic*: The driver must utilize cascade lists of selectors:
     ```python
     EMAIL_SELECTORS = ["#email", "#login_email", "input[type='email']", "input[name='email']"]
     PASSWORD_SELECTORS = ["#password", "#login_password", "input[type='password']", "input[name='password']"]
     SUBMIT_SELECTORS = ["#login-btn", "#login_button", "button[type='submit']", "a.login-btn", "#mobile-login"]
     ```
     By iterating through the candidate selectors with `page.wait_for_selector(sel, timeout=...)` or query checks, the driver works seamlessly across both live production DOM and mock/staging environments.

3. **Strict Compliance with Requirement R1 (Zero Automated Bypass)**:
   - *Observation*: Cloudflare Turnstile, reCAPTCHA v3, OTP challenges, and `#myModal #sendmail` activation gates exist on Guvi.
   - *Logic*: Any detection of these elements must immediately invoke `hitl_handler.check_and_handle_guardrails(page)`. The automated driver must never inject synthetic bypasses, OCR, or third-party solver tokens. It must pause, beep (`\a`), display clear terminal instructions, and wait for human resolution in the visible foreground browser window.

4. **Handling Post-Login Popups and Guided Tours**:
   - *Observation*: Guvi periodically presents guided onboarding dialogs (`#welcome`, `#liveClass`, `That's It! You Are Ready!` dialogs with close buttons) upon fresh login (`spec_miner_survey_2/handoff.md:48`).
   - *Logic*: After authentication succeeds, the driver should run a lightweight popup dismissal helper (`dismiss_popups()`) to close onboarding overlays before problem discovery or workspace navigation begins.

5. **Post-Authentication Storage State Serialization**:
   - *Observation*: `browser_manager.save_storage_state()` exports all cookies and localStorage origins to `data/storage_state.json`.
   - *Logic*: Immediately following a successful login (and post-login indicator confirmation), `GuviDriver` must call `browser_manager.save_storage_state()`. This ensures that subsequent runs or separate CLI processes can bootstrap using saved session state without requiring credential re-entry.

---

## 3. Caveats

1. **Dual Storage vs Profile Locks**: Chromium persistent contexts (`.browser_profile/`) lock their directory with `SingletonLock`. When running test suites concurrently, separate temporary profile directories must be used, which makes `data/storage_state.json` essential for cross-process session transfer.
2. **Dynamic Qwik Framework Reactivity**: Guvi CodeKata uses Qwik SSR (`q:route="code-kata/"`). Navigation often occurs via client-side router without a full page reload. DOM verification must wait for specific elements (`table tbody tr`, `.question-status`) rather than relying solely on `networkidle`.
3. **Account Activation Modal Gate**: If Guvi responds with `{access: "activate"}` from `usercheck.php`, the modal `#myModal` will open with button `#sendmail`. This is handled as an R1 guardrail by `HitlHandler`, requiring human verification.

---

## 4. Conclusion: Production-Ready Architectural Blueprint

### 4.1 Class Hierarchy and Layout

```
zenclass_guvi/
├── drivers/
│   ├── __init__.py               # Exports BaseDriver, GuviDriver, exceptions
│   ├── base_driver.py            # Common navigation, wait, HITL, and screenshot helpers
│   ├── guvi_driver.py            # Guvi CodeKata driver (Auth, Catalog, Execution, Submit)
│   └── zenclass_driver.py        # ZenClass driver (Milestone 4 & 5)
```

---

### 4.2 Blueprint: `drivers/base_driver.py`

```python
"""
drivers/base_driver.py - Common Platform Driver Base Class
Provides shared navigation, element interactions, HITL guardrail checks,
diagnostic screenshots, and session lifecycle management for Guvi and ZenClass.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Optional, List, Any, Dict

import config
from core.browser import BrowserManager, get_browser_manager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler

logger = logging.getLogger("drivers.base")


class DriverError(Exception):
    """Base exception for platform driver operations."""
    pass


class AuthenticationError(DriverError):
    """Raised when platform authentication fails."""
    pass


class GuardrailBlockedError(DriverError):
    """Raised when a security guardrail halts execution."""
    pass


class BaseDriver:
    """
    Abstract base driver encapsulating common Playwright interactions,
    HITL guardrail interception, and session persistence.
    """

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
    ):
        self.browser_manager = browser_manager or get_browser_manager()
        self.state_manager = state_manager
        self.hitl_handler = hitl_handler or HitlHandler(interactive=True, state_manager=self.state_manager)
        self._current_page: Optional[Any] = None

    @property
    def page(self) -> Any:
        """Returns the active Playwright page, initializing if needed."""
        if self._current_page is None or self._current_page.is_closed():
            self._current_page = self.browser_manager.get_page()
        return self._current_page

    def navigate(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[float] = None,
    ) -> Any:
        """Navigates to URL and brings the page to foreground."""
        timeout_ms = timeout or config.NAVIGATION_TIMEOUT
        logger.info(f"Navigating to {url} (wait_until={wait_until})")
        self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        self.page.bring_to_front()
        return self.page

    def check_guardrails(self, task_id: Optional[str] = None, context_desc: str = "Active Page") -> bool:
        """
        Inspects current page for Cloudflare, reCAPTCHA, OTP, or activation gates.
        Halts for human intervention if detected. Returns True if resolved, False if none.
        """
        return self.hitl_handler.check_and_handle_guardrails(
            self.page,
            task_id=task_id,
            context_desc=context_desc
        )

    def find_first_selector(self, selectors: List[str], timeout: float = 3000.0) -> Optional[str]:
        """Returns the first selector in the list that exists and is visible on page."""
        for sel in selectors:
            try:
                el = self.page.wait_for_selector(sel, state="visible", timeout=timeout)
                if el:
                    return sel
            except Exception:
                continue
        return None

    def safe_fill(self, selectors: List[str], value: str, timeout: float = 5000.0) -> str:
        """Fills the first matching selector from the list."""
        matched = self.find_first_selector(selectors, timeout=timeout)
        if not matched:
            raise DriverError(f"None of the target selectors {selectors} were found on {self.page.url}")
        self.page.fill(matched, value)
        return matched

    def safe_click(self, selectors: List[str], timeout: float = 5000.0) -> str:
        """Clicks the first matching selector from the list."""
        matched = self.find_first_selector(selectors, timeout=timeout)
        if not matched:
            raise DriverError(f"None of the target click selectors {selectors} were found on {self.page.url}")
        self.page.click(matched)
        return matched

    def save_screenshot(self, name: str = "error") -> Optional[Path]:
        """Captures diagnostic PNG screenshot."""
        return self.browser_manager.save_screenshot(name=name, page=self.page)

    def persist_session(self) -> None:
        """Exports active browser cookies and localStorage to storage_state.json."""
        self.browser_manager.save_storage_state()
```

---

### 4.3 Blueprint: `drivers/guvi_driver.py` (Authentication & Session Layer)

```python
"""
drivers/guvi_driver.py - Autonomous Guvi CodeKata Driver
Implements Guvi Authentication, Session Management, Problem Discovery,
and CodeKata Execution & Submission lifecycles.
Strictly adheres to Requirements R1, R2, R3.
"""

from __future__ import annotations
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import config
from drivers.base_driver import BaseDriver, AuthenticationError, DriverError
from core.browser import BrowserManager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler

logger = logging.getLogger("drivers.guvi")


class GuviAuthenticationError(AuthenticationError):
    """Raised when Guvi credential login is rejected or invalid."""
    pass


class GuviDriver(BaseDriver):
    """
    Automated driver for the Guvi platform (https://www.guvi.in).
    Coordinates authentication, session persistence, CodeKata catalog discovery,
    Ace editor code injection, and submission verification.
    """

    # Form Selector Fallback Arrays
    EMAIL_SELECTORS = [
        "#email",
        "#login_email",
        "input[type='email']",
        "input#email",
        "#emailgroup input",
    ]

    PASSWORD_SELECTORS = [
        "#password",
        "#login_password",
        "input[type='password']",
        "input#password",
        "#passwordGroup input",
    ]

    REMEMBER_ME_SELECTORS = [
        "#logged-in",
        "input#logged-in",
        "input[name='logged-in']",
        "input[type='checkbox']#logged-in",
    ]

    SUBMIT_SELECTORS = [
        "#login-btn",
        "#login_button",
        "button[type='submit']",
        "a.login-btn",
        "#mobile-login",
        "a#login-btn",
        "button:has-text('Login')",
        "a:has-text('Login')",
    ]

    ERROR_FEEDBACK_SELECTORS = [
        ".invalid-feedback",
        "#emailgroup .invalid-feedback",
        "#passwordGroup .invalid-feedback",
        ".alert-danger",
        "div:has-text('Incorrect Email or Password')",
    ]

    POST_LOGIN_INDICATORS = [
        ".user-avatar",
        "#user_wallet_points",
        "div.profile-icon",
        "a[href*='profile']",
        "button:has-text('Sign Out')",
        "a[href*='sign-out']",
        ".filter-topics-tab",
        "table tbody tr.cursor-pointer",
    ]

    POPUP_DISMISS_SELECTORS = [
        "button:has-text('✕')",
        "button:has-text('close')",
        "button:has-text('Close')",
        "#welcome button.close",
        ".modal button.close",
    ]

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
        base_url: Optional[str] = None,
        login_url: Optional[str] = None,
        codekata_url: Optional[str] = None,
    ):
        super().__init__(
            browser_manager=browser_manager,
            state_manager=state_manager,
            hitl_handler=hitl_handler,
        )
        self.base_url = base_url or config.GUVI_BASE_URL
        self.login_url = login_url or config.GUVI_LOGIN_URL
        self.codekata_url = codekata_url or config.GUVI_CODEKATA_URL

    # =========================================================================
    # 1. Session Detection & Verification
    # =========================================================================

    def is_authenticated(self) -> bool:
        """
        Determines whether the browser currently holds an active, valid Guvi session.
        Checks:
          1. Context cookies for valid 'authToken' (starts with 'auth:').
          2. Current URL / page DOM if already on Guvi.
          3. Probe navigation to CodeKata catalog without redirecting to /sign-in/.
        Returns True if session is valid; False otherwise.
        """
        logger.debug("Checking Guvi session validity...")

        # 1. In-memory cookie inspection
        try:
            cookies = self.page.context.cookies()
            auth_token = next((c["value"] for c in cookies if c["name"] == "authToken"), None)
            if not auth_token or not auth_token.startswith("auth:"):
                logger.debug("No valid 'authToken' cookie found in browser context.")
                return False
        except Exception as e:
            logger.debug(f"Cookie check error: {e}")
            return False

        # 2. Check current page state if already loaded
        current_url = self.page.url or ""
        if "/sign-in/" in current_url:
            return False

        for indicator in self.POST_LOGIN_INDICATORS:
            try:
                el = self.page.query_selector(indicator)
                if el and el.is_visible():
                    logger.info(f"Authenticated session verified via DOM indicator: {indicator}")
                    return True
            except Exception:
                pass

        # 3. Active probe: navigate to CodeKata and verify no redirect to sign-in
        try:
            logger.info("Probing session by navigating to CodeKata URL...")
            self.page.goto(self.codekata_url, wait_until="domcontentloaded", timeout=config.NAVIGATION_TIMEOUT)
            time.sleep(1.0)

            # Check for guardrails on target page
            self.check_guardrails(context_desc="Session Validation Probe")

            probe_url = self.page.url or ""
            if "/sign-in/" in probe_url:
                logger.info("Session invalid: Redirected to /sign-in/")
                return False

            # Confirm presence of CodeKata table or avatar
            for indicator in self.POST_LOGIN_INDICATORS:
                el = self.page.query_selector(indicator)
                if el:
                    logger.info("Session valid: CodeKata catalog accessed successfully.")
                    return True

            # Check localStorage as final fallback
            token_in_ls = self.page.evaluate("() => localStorage.getItem('authToken')")
            if token_in_ls and token_in_ls.startswith("auth:"):
                logger.info("Session valid: Confirmed via localStorage 'authToken'.")
                return True

        except Exception as e:
            logger.warning(f"Session probe encountered exception: {e}")

        return False

    def ensure_authenticated(self, force_relogin: bool = False) -> bool:
        """
        Idempotent entrypoint ensuring the driver is authenticated.
        If a valid session exists and force_relogin is False, avoids redundant login.
        Otherwise executes full login sequence.
        """
        if not force_relogin and self.is_authenticated():
            logger.info("Reusing existing authenticated Guvi session.")
            self.dismiss_popups()
            return True

        logger.info("Initiating fresh Guvi authentication sequence...")
        return self.login()

    # =========================================================================
    # 2. Guvi Authentication Workflow
    # =========================================================================

    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Executes credential authentication on https://www.guvi.in/sign-in/.
        Steps:
          1. Navigates to sign-in page.
          2. Inspects for early redirection (already logged in).
          3. Checks pre-login guardrails (Cloudflare Turnstile, reCAPTCHA).
          4. Types email & password into matching form fields.
          5. Ensures 'keep me logged in' checkbox is set.
          6. Submits credentials and monitors response / navigation.
          7. Checks for errors (.invalid-feedback) or account activation gates (#myModal).
          8. Awaits post-login URL or DOM indicator.
          9. Persists session state to storage_state.json.
        """
        user_email = email or config.USER_EMAIL
        user_password = password or config.USER_PASSWORD
        op_timeout = timeout or config.NAVIGATION_TIMEOUT

        if not user_email or not user_password:
            raise GuviAuthenticationError("User credentials (email/password) must not be empty.")

        logger.info(f"Navigating to Guvi sign-in page: {self.login_url}")
        self.navigate(self.login_url, wait_until="domcontentloaded", timeout=op_timeout)
        time.sleep(1.0)

        # Edge Case 3: Already authenticated redirect
        if "/sign-in/" not in self.page.url:
            logger.info(f"Auto-redirected away from sign-in to {self.page.url}. Session is already active.")
            self.persist_session()
            self.dismiss_popups()
            return True

        # Check for pre-fill guardrails (e.g. Cloudflare Turnstile challenge)
        self.check_guardrails(task_id="guvi-auth", context_desc="Guvi Sign-In Page Load")

        # Locate email and password inputs
        logger.info("Locating login form elements...")
        email_sel = self.find_first_selector(self.EMAIL_SELECTORS, timeout=5000.0)
        pwd_sel = self.find_first_selector(self.PASSWORD_SELECTORS, timeout=5000.0)

        if not email_sel or not pwd_sel:
            self.save_screenshot("guvi_login_form_missing")
            raise GuviAuthenticationError(
                f"Could not locate login form fields on {self.page.url}. "
                f"Searched email={self.EMAIL_SELECTORS}, pwd={self.PASSWORD_SELECTORS}"
            )

        # Fill credentials with natural cadence
        logger.info(f"Entering credentials for '{user_email}'...")
        self.page.fill(email_sel, "")
        self.page.type(email_sel, user_email, delay=20)

        self.page.fill(pwd_sel, "")
        self.page.type(pwd_sel, user_password, delay=20)

        # Ensure 'Keep me logged in' checkbox is checked
        rem_sel = self.find_first_selector(self.REMEMBER_ME_SELECTORS, timeout=1000.0)
        if rem_sel:
            try:
                if not self.page.is_checked(rem_sel):
                    self.page.check(rem_sel)
                    logger.debug(f"Checked 'Keep me logged in' via {rem_sel}")
            except Exception as e:
                logger.debug(f"Could not toggle remember me checkbox: {e}")

        # Locate submit button
        submit_sel = self.find_first_selector(self.SUBMIT_SELECTORS, timeout=3000.0)
        if not submit_sel:
            self.save_screenshot("guvi_submit_button_missing")
            raise GuviAuthenticationError(f"Could not locate submit button from {self.SUBMIT_SELECTORS}")

        logger.info(f"Submitting credentials via '{submit_sel}'...")
        self.page.click(submit_sel)

        # Wait briefly for server evaluation
        time.sleep(2.0)

        # Intercept immediate guardrails (e.g. Turnstile, reCAPTCHA, #myModal #sendmail)
        self.check_guardrails(task_id="guvi-auth", context_desc="Guvi Credential Post-Submission")

        # Check for rejection feedback (.invalid-feedback)
        for err_sel in self.ERROR_FEEDBACK_SELECTORS:
            try:
                err_el = self.page.query_selector(err_sel)
                if err_el and err_el.is_visible():
                    err_text = err_el.inner_text().strip()
                    if err_text:
                        self.save_screenshot("guvi_auth_invalid_credentials")
                        logger.error(f"Authentication failed: {err_text}")
                        raise GuviAuthenticationError(f"Guvi rejected credentials: {err_text}")
            except GuviAuthenticationError:
                raise
            except Exception:
                pass

        # Wait for navigation or post-login indicator
        logger.info("Awaiting post-login confirmation...")
        start_wait = time.time()
        authenticated = False

        while time.time() - start_wait < (op_timeout / 1000.0):
            # Check URL change
            current_url = self.page.url or ""
            if "/sign-in/" not in current_url:
                authenticated = True
                break

            # Check DOM indicators
            for ind in self.POST_LOGIN_INDICATORS:
                el = self.page.query_selector(ind)
                if el and el.is_visible():
                    authenticated = True
                    break

            if authenticated:
                break

            # Check guardrails in each poll iteration
            self.check_guardrails(task_id="guvi-auth", context_desc="Guvi Auth Wait Loop")
            time.sleep(1.0)

        if not authenticated:
            self.save_screenshot("guvi_auth_timeout")
            raise GuviAuthenticationError(
                f"Timed out waiting for Guvi login completion. Page URL remains: {self.page.url}"
            )

        logger.info(f"Guvi authentication successful! Landed on: {self.page.url}")

        # Clean up any guided onboarding modals
        self.dismiss_popups()

        # Persist session cookies & localStorage to storage_state.json
        self.persist_session()
        logger.info("Session state serialized and preserved for subsequent runs.")

        return True

    # =========================================================================
    # 3. Popup & Overlay Cleanup
    # =========================================================================

    def dismiss_popups(self) -> None:
        """Closes guided onboarding tours or welcome overlays if present."""
        for sel in self.POPUP_DISMISS_SELECTORS:
            try:
                btn = self.page.query_selector(sel)
                if btn and btn.is_visible():
                    logger.info(f"Dismissing modal popup via '{sel}'")
                    btn.click()
                    time.sleep(0.5)
            except Exception:
                pass
```

---

### 4.4 Blueprint: Security Challenges & HITL Integration Details

The blueprint achieves 100% compliance with Requirement R1:
1. **Cloudflare Turnstile Detection**:
   - Inspects `title` for `"Just a moment..."` and selector `iframe[src*='challenges.cloudflare.com'], div.cf-turnstile, #cf-stage`.
   - Action: Zero automated bypass. Emits 3 audible bells (`\a`), prints ANSI alert box, halts until human completes checkbox in the foreground browser.
2. **Google reCAPTCHA**:
   - Inspects `iframe[src*='google.com/recaptcha']`, `div.g-recaptcha`.
   - Action: Halts execution, alerts user, waits for foreground completion.
3. **Guvi Account Activation Gate (`#myModal #sendmail`)**:
   - Inspects `#myModal, #myModal #sendmail, div.modal:has(#sendmail)`.
   - Action: Alerts user that Guvi requires account activation / verification email, prompts user to handle it in browser.
4. **OTP / MFA Challenges**:
   - Inspects `input[name*='otp' i], input[placeholder*='OTP' i]`.
   - Action: Prompts user to enter OTP received on mobile/email into the browser form.

---

### 4.5 Blueprint: Session Persistence Architecture

```
Dual-Layer Session Persistence Architecture
===========================================

1. Primary Layer (On-Disk Browser Profile):
   BrowserManager launches Chromium with user_data_dir:
     zenclass_guvi/.browser_profile/
   Chromium automatically saves cookies, HTTP cache, localStorage, and IndexedDB
   in native SQLite databases (Default/Cookies).

2. Secondary Layer (Serialized JSON State):
   BrowserManager.save_storage_state() exports:
     zenclass_guvi/data/storage_state.json
   Format:
     {
       "cookies": [
         {"name": "authToken", "value": "auth:...", "domain": ".guvi.in", "path": "/"},
         {"name": "mail", "value": "devsh.pareek@gmail.com", "domain": ".guvi.in", "path": "/"},
         {"name": "cusername", "value": "Devesh Pareek", "domain": ".guvi.in", "path": "/"}
       ],
       "origins": [
         {
           "origin": "https://www.guvi.in",
           "localStorage": [
             {"name": "authToken", "value": "auth:..."},
             {"name": "loginSuccess", "value": "true"},
             {"name": "userpoints", "value": "2195"}
           ]
         }
       ]
     }

3. Startup Injection:
   On start(), BrowserManager checks if storage_state.json exists and injects cookies:
     context.add_cookies(cookies)
   Ensuring session portability across isolated test environments and fresh profiles.
```

---

## 5. Verification Method

To independently verify the architecture and implementation blueprint:

1. **Verify Mock Platform Auth Test Suite**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m unittest tests/e2e/tier1_features/test_f09_guvi_auth.py
   ```
   *Expected Result*: Ran 3 tests in ~1.0s, OK. Verifies login selectors, `usercheck.php` payload, and 401 error rejection.

2. **Verify Pairwise Auth-to-Discovery Transition**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m unittest tests/e2e/tier3_pairwise/test_p01_auth_to_discovery.py
   ```
   *Expected Result*: Tests pass, verifying that session cookie `authToken=auth:...` grants access to `/code-kata/` catalog and discovers pending problems.

3. **Verify Milestone 1 & 2 Infrastructure Compatibility**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py
   ```
   *Expected Result*: Ran 57 tests, OK.

4. **Verify Live Browser Cookie & Session Inspection via macOS AppleScript**:
   ```bash
   osascript -e '
   tell application "Brave Browser"
       set w to window 1
       set t to make new tab at end of tabs of w with properties {URL:"https://www.guvi.in/code-kata/"}
       delay 3
       set res to execute t javascript "JSON.stringify({hasAuthToken: document.cookie.includes(\"authToken=auth:\"), points: localStorage.getItem(\"userpoints\")})"
       close t
       return res
   end tell
   '
   ```
   *Expected Result*: `{"hasAuthToken":true,"points":"2195"}`.
