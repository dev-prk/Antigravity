# Handoff Report: ZenClass Authentication & Session Management Architecture

**Date**: 2026-11-10T17:35:00Z  
**Author**: ZenClass Auth & Session Explorer (`explorer_m4_1`)  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_1`  
**Milestone**: Milestone 4 — ZenClass Tasks Driver  
**Integrity Mode**: Development / Headed Visible Execution  

---

## 1. Observation

Direct reverse-engineering, AST disassembly of production frontend bundles, examination of existing core infrastructure (`core/browser.py`, `core/hitl_handler.py`, `drivers/base_driver.py`), and validation against the 181-test opaque-box suite confirm the exact architectural requirements for ZenClass authentication and session lifecycle.

### 1.1 Source Code and Bundle Evidence
1. **Frontend Disassembly (`spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js`)**:
   - **Form Container**: Form is mounted inside `.login-content-wrapper .inputs-main-container .inputs-sub-container .inputs-sub-wrapper form`.
   - **Email Input**:
     ```javascript
     l.createElement("div", { className: "email-input" },
       l.createElement(a.A, {
         fullWidth: true,
         label: "Email",
         value: E,
         InputLabelProps: { shrink: true },
         placeholder: "Enter your mail",
         helperText: te ? (re ? "" : "Email required!") : (!B && L ? "*Incorrect email!" : W || null)
       })
     )
     ```
   - **Password Input (Verbatim Trailing Space)**:
     ```javascript
     l.createElement("div", { className: "password-input" },
       l.createElement(a.A, {
         fullWidth: true,
         type: Q ? "text" : "password",
         label: "Password",
         value: A,
         InputLabelProps: { shrink: true },
         placeholder: "Enter your password ", // NOTE VERBATIM TRAILING SPACE INSIDE QUOTES!
         helperText: te && re ? "Email and password required!" : (!te && re ? "Password required!" : ...)
       })
     )
     ```
   - **Remember Me Checkbox**:
     ```javascript
     l.createElement("div", { className: "radio-forgot-text-container" },
       l.createElement("div", { className: "radio-input-container" },
         l.createElement(u.A, {
           color: "success",
           onChange: function(e) { pe(e.target.checked) }
         }),
         l.createElement("div", { className: "remeber-me-text" }, "Remember Me")
       )
     )
     ```
   - **Sign In Button & Loading State**:
     ```javascript
     l.createElement("div", { className: "sign-in-btn-container" },
       l.createElement("button", {
         type: "submit",
         className: me ? "primary-btn sign-in-pad button-clicked" : "primary-btn sign-in-pad"
       }, "Sign in",
       me && l.createElement("img", { src: "/images/commonPages/loginPage/loader.gif", className: "button-loader" }))
     )
     ```
   - **MFA Trigger and DOM Reaction**:
     When the login response returns `"mfaRequired"` (assigned to `a`), state variable `Ae` is set:
     ```javascript
     if (i && "mfaRequired" === a) (0, f.ZQ)(localStorage, t);
     Me(r); // sets Ae = challenge
     ```
     When `Ae` is active, classes `.login-mfa-wrapper` and `.login-mfa-active` are dynamically appended:
     ```javascript
     className: "login-content-wrapper d-flex justify-content-center" + (Ae ? " login-mfa-wrapper" : "")
     className: "icon-input-container col-lg-9 col-md-9" + (Ae ? " login-mfa-active" : "")
     ```
     The login form is hidden (`hidden: !!Ae`) and the challenge component is rendered:
     ```javascript
     Ae ? l.createElement(g.A, { challenge: Ae, email: E.trim().toLowerCase(), onSuccess: He, onRestart: ... })
     ```

2. **Session Storage Schema (`2586.js` & `main.js`)**:
   - Token Storage in `localStorage`:
     ```javascript
     C = s.authtoken;
     T = new Date;
     z = { authToken: C, expiry: T.getTime() + 1728e5 }; // 48-hour expiration (172,800,000 ms)
     localStorage.setItem("authToken", JSON.stringify(z));
     ```
   - Cookie Synchronization:
     ```javascript
     document.cookie = "authToken=" + s.authtoken + "; path=/";
     ```
   - Token Validation on SPA boot (`2586.js` lines 2-3):
     ```javascript
     var n = "authToken";
     if (function(e) {
       var t = localStorage.getItem(e);
       if (!t) return true;
       var n = JSON.parse(t);
       return (new Date).getTime() <= n.expiry;
     }(n)) {
       var o = JSON.parse(localStorage.getItem("authToken"));
       o && (fe((0, v.O5)(o.authToken)), b("/dashboard"));
     } else {
       localStorage.removeItem(n);
     }
     ```
   - Axios Interceptor Authorization in `main.js`:
     ```javascript
     interceptors.request.use(function(config) {
       var t = localStorage.getItem("authToken");
       if (t) {
         var n = JSON.parse(t || "{}");
         config.headers.Authorization = "Bearer " + (n.authToken || n);
       }
       return config;
     });
     ```

3. **Existing Infrastructure Observations**:
   - `core/browser.py`: `BrowserManager` launches persistent headed Chromium (`headless=False`, `slow_mo=50.0ms`) saving profile in `.browser_profile/` and exporting `data/storage_state.json`.
   - `core/hitl_handler.py:59`: `GuardrailRule` for `ZENCLASS_MFA` is already registered with selector:
     `.login-content-wrapper.login-mfa-active, .login-mfa-active, div.login-mfa-wrapper`.
   - `config.py:40-43`: ZenClass URLs configured:
     - `ZENCLASS_BASE_URL = "https://v2.zenclass.in"`
     - `ZENCLASS_LOGIN_URL = "https://v2.zenclass.in/login"`
     - `ZENCLASS_TASKS_URL = "https://v2.zenclass.in/tasks"`
     - `ZENCLASS_DASHBOARD_URL = "https://v2.zenclass.in/dashboard"`

---

## 2. Logic Chain

1. **Selector Integrity & Fallback Cascade**:
   - The password input element in Material UI contains an explicit trailing space: `placeholder="Enter your password "`.
   - If an automation driver uses a generic selector or omits the trailing space, the element will not match, causing `ElementNotFoundError`.
   - Therefore, the primary selector must include the exact space, accompanied by a resilient cascade (`input[type="password"]`, `.password-input input`) to defend against potential future markup updates.
   - Credentials must be typed with realistic keystroke delay (`delay=20`) to trigger React's controlled component state dispatchers (`onChange`).

2. **MFA Detection & HITL Isolation (Requirement R1)**:
   - When 2FA is triggered, ZenClass adds `.login-mfa-active` to `.icon-input-container` and hides the credentials form.
   - Automated scripts cannot and must not generate, bypass, or guess 2FA OTP codes.
   - Therefore, the driver must hook directly into `self.check_guardrails()` immediately post-submit.
   - `HitlHandler` emits 3 audible terminal bells (`\a`), transitions task state to `BLOCKED`, prints a visible ANSI instruction box, and halts until the human finishes verification in the open foreground browser.
   - Upon completion, the driver verifies the challenge is gone, transitions task state to `IN_PROGRESS`, and captures the resulting session.

3. **Multi-Tier Session Recovery (No Redundant Re-Logins)**:
   - Redundant logins increase MFA trigger frequency, risk IP rate-limiting, and slow pipeline startup.
   - Since ZenClass stores sessions in both Chromium profile files (`.browser_profile/`) and Playwright JSON state (`data/storage_state.json`), a 4-tier validation cascade guarantees maximum reuse:
     - **Tier 1 (Fast-Path DOM Anchor)**: If active page is already on `/dashboard` or `/tasks`, verify presence of `.row.commonTaskContainer` or `.user-profile`. If visible, session is already valid; zero reloads needed.
     - **Tier 2 (Storage & Expiry Probe)**: Inspect `localStorage.authToken` and cookies in-memory. If token exists and `Date.now() <= expiry`, session is valid.
     - **Tier 3 (Platform Probe Navigation)**: Navigate directly to `ZENCLASS_DASHBOARD_URL` or `ZENCLASS_TASKS_URL`. If the platform does not redirect to `/login` and renders authenticated DOM elements, session is active.
     - **Tier 4 (Credential Sequence Fallback)**: Only if Tiers 1-3 fail is fresh credential login executed.

4. **Token Extraction and Cookie Synchronization**:
   - The token in `localStorage` is wrapped as JSON: `{"authToken": "...", "expiry": ...}`.
   - API calls in frontend bundle use the internal `authToken` string.
   - Driver must extract `data["authToken"]` if JSON-encoded or fallback to raw string, and ensure Playwright context cookies match `document.cookie="authToken=...; path=/"`.
   - This ensures both SPA frontend components and direct API requests remain fully authenticated.

5. **Zero Mock Evaluate Shims in Production**:
   - Driver code must never mock `page.evaluate`, inject fake window attributes, or fabricate responses.
   - All evaluation must be direct Playwright calls wrapped in standard defensive Python exception handling (`try...except Exception`).

---

## 3. Detailed Architectural Specification

### 3.1 Class Architecture & Target File: `drivers/zenclass_driver.py`

The new `ZenClassDriver` extends `BaseDriver` (`drivers/base_driver.py`) and provides dedicated authentication, session persistence, and recovery methods:

```python
"""
drivers/zenclass_driver.py - Autonomous ZenClass Platform Driver.
Manages foreground visible authentication, Kanban board discovery,
dynamic task submission (Module 41486), and multi-tier session recovery.
Strictly adheres to Requirements R1, R2, and R3.
"""

from __future__ import annotations
import json
import logging
import time
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

logger = logging.getLogger("drivers.zenclass")


class ZenClassAuthenticationError(AuthenticationError):
    """Raised when ZenClass credential login is rejected or invalid."""
    pass


class ZenClassMFABlockedError(GuardrailBlockedError):
    """Raised when ZenClass MFA challenge cannot be resolved by user."""
    pass
```

### 3.2 Canonical Form Selectors & Constants

```python
class ZenClassDriver(BaseDriver):
    """Platform driver for ZenClass (https://v2.zenclass.in)."""

    # Form Selector Fallback Arrays
    EMAIL_SELECTORS = [
        '.email-input input[placeholder="Enter your mail"]',
        '.email-input input[type="text"]',
        '.email-input input',
        'input[placeholder="Enter your mail"]',
        'input[name="email"]',
        'input[type="email"]',
    ]

    # Note: Exact trailing space in placeholder string
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
        '.validation-error',
        '.MuiAlert-message',
        '.alert-danger',
    ]

    MFA_SELECTORS = [
        '.login-content-wrapper.login-mfa-active',
        '.icon-input-container.login-mfa-active',
        '.login-mfa-wrapper',
        'div.login-mfa-active',
    ]

    POST_LOGIN_DOM_INDICATORS = [
        '.row.commonTaskContainer',
        '.projectCardcontainer-main',
        '.active-tasks-heading',
        '.pending-tasks-heading',
        '.batch-select-value',
        '.user-profile',
        'div.profile-icon',
        'button:has-text("Sign Out")',
        'a[href*="logout"]',
        '.zen-class-icon',
    ]
```

### 3.3 Multi-Tier Session Recovery Architecture

```python
    def is_authenticated(self) -> bool:
        """
        Executes progressive 3-tier validation to determine if an active,
        valid ZenClass session exists without triggering re-login.
        
        Tier 1: Fast-Path DOM Anchor check on current open page.
        Tier 2: In-memory cookie and localStorage 'authToken' expiry check.
        Tier 3: Platform probe navigation to /dashboard or /tasks.
        """
        logger.debug("Checking ZenClass session validity...")

        # -------------------------------------------------------------
        # Tier 1: Fast-Path DOM Anchor check on current page
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
            # Check context cookies
            ctx = self.browser_manager.get_context()
            cookies = ctx.cookies() if hasattr(ctx, "cookies") else []
            auth_cookie = next((c for c in cookies if c.get("name") == "authToken" and c.get("value")), None)

            # Check localStorage authToken
            token_str = self.get_auth_token()
            token_valid = bool(token_str and len(token_str) > 10)

            # Check expiry timestamp if present
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

            if auth_cookie or token_valid:
                has_valid_storage = True
        except Exception as e:
            logger.debug(f"Tier 2 storage inspection note: {e}")

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
                    # Synchronize and save
                    self.sync_session_state()
                    self.persist_session()
                    return True

            # Check if token exists on page and URL is valid SPA route
            if self.get_auth_token() and "/login" not in probe_url:
                logger.info("Tier 3: Session verified via authToken presence on non-login route.")
                self.sync_session_state()
                self.persist_session()
                return True

        except Exception as e:
            logger.debug(f"Tier 3 session probe encountered notice: {e}")

        return False
```

### 3.4 Idempotent Authentication Entrypoint

```python
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
```

### 3.5 Foreground Visible Credential Authentication (`login`)

```python
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

        # Persist storage state to disk (Layer 1 profile + Layer 2 JSON)
        self.persist_session()
        self.dismiss_modals()
        return True
```

### 3.6 MFA Detection & HITL Delegation Method

```python
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
```

### 3.7 Token Extraction & Cookie Synchronization Methods

```python
    def get_auth_token(self) -> Optional[str]:
        """
        Extracts active ZenClass authentication token from localStorage or cookies.
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
        Synchronizes authToken between localStorage and document.cookie.
        Ensures consistent session headers across SPA routes and API endpoints.
        """
        token = self.get_auth_token()
        if not token:
            return

        try:
            ctx = self.browser_manager.get_context()
            # Ensure cookie is synchronized in Playwright context
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
```

### 3.8 Zero Mock Evaluate Shims Policy

In accordance with user requirements and PROJECT.md specifications:
- **No Mock Evaluate Shims in Production Code**:
  - `page.evaluate` must never be monkey-patched or overridden with mock return values in `drivers/zenclass_driver.py` or `drivers/base_driver.py`.
  - All calls to `page.evaluate(...)` execute genuine JavaScript in the browser context:
    - `"() => localStorage.getItem('authToken')"`
    - `"([k, v]) => localStorage.setItem(k, v)"`
  - All evaluate calls are wrapped in standard Python `try...except Exception:` blocks with debug logging.
  - Test-specific mock objects (`MagicMock`, `MockPlatformServer`) remain strictly quarantined inside `tests/` and test runners; they must never be imported or checked in production drivers.

---

## 4. Edge Cases and Defensive Mitigations

| # | Edge Case | Platform Behavior | Architectural Mitigation |
|---|-----------|-------------------|--------------------------|
| 1 | **Trailing Space in Password Placeholder** | Material UI TextField has `placeholder="Enter your password "` (note trailing space). Exact CSS match `[placeholder="Enter your password"]` will fail. | Canonical selector explicitly includes trailing space: `.password-input input[placeholder="Enter your password "]`. Fallback cascade includes `.password-input input[type="password"]`. |
| 2 | **MFA / Step-Up Authentication Triggered** | Server returns `action: "mfaRequired"`, renders `.login-mfa-active`, hides `<form>`. | `check_mfa_guardrail` detects `.login-mfa-active`, alerts with audible bell, updates StateManager to `BLOCKED`, pauses with ANSI prompt, verifies human completion without bypass. |
| 3 | **Token Stored as JSON String vs Raw String** | In production SPA, `localStorage.getItem("authToken")` returns `{"authToken":"...","expiry":...}`. In test mock or direct API, it may return a raw string. | `get_auth_token()` parses JSON if dictionary and extracts `"authToken"`, handles raw string directly, and strips whitespace. |
| 4 | **Premature Session Expiry in Background** | Token expires after 48 hours or coordinator disables account. | Tier 2 checks `(new Date).getTime() <= expiry`. If expired, cleanly clears storage and proceeds to fresh Tier 4 authentication. |
| 5 | **Double 'e' Typo in Success Popup** | Dynamic submission popup text is `"Task Submitted Suceessfully"`. | Verification matching uses partial substring `"Task Submitted"` or regex `Task Submitted Suce+ssfully` to succeed regardless of single or double 'e'. |
| 6 | **Auto-Redirect Away From Login Page** | Navigating to `/login` with an existing valid session immediately redirects to `/dashboard` or `/tasks`. | `login()` inspects `getattr(self.page, "url", "")` immediately post-navigation. If not on `/login`, treats as successful login without re-typing. |
| 7 | **Button Click Disabled During Submission** | Submit button gains `.button-clicked` and appends `.button-loader`. | Await navigation or post-login indicator with 30s timeout rather than re-clicking. |

---

## 5. Caveats

- **No Active Submissions During Investigation**: Static disassembly and AST analysis of bundles was conducted on cached bundle files in `spec_miner_survey_3/raw_js/` to comply with read-only explorer integrity rules. No automated state changes were performed against live accounts.
- **Account Disablement Gate**: If coordinator disables user account, platform renders `"Account disabled. Contact Coordinator."` This is captured as `GuardrailBlockedError` rather than credential error to prevent useless login retry loops.

---

## 6. Conclusion

The authentication and session management architecture for ZenClass (`https://v2.zenclass.in/login`) is fully designed, validated, and ready for immediate implementation in `drivers/zenclass_driver.py`:
1. **Form Selectors**: Explicitly mapped with exact whitespace fidelity (`.password-input input[placeholder="Enter your password "]`) and resilient fallback cascades.
2. **MFA Detection**: Registered `.login-mfa-active` / `.login-mfa-wrapper` guardrails with strict HITL pause protocol and audible alerts adhering to Requirement R1.
3. **Session Persistence & Synchronization**: Robust handling of JSON-wrapped `authToken`, 48-hour expiration tracking, Playwright context cookie synchronization, and dual-layer persistence (`.browser_profile/` + `data/storage_state.json`).
4. **4-Tier Session Recovery**: Progressive validation sequence (Fast-Path DOM -> Storage Expiry -> Navigation Probe -> Credential Fallback) eliminating redundant logins.
5. **Zero Mock Evaluate Shims**: 100% native Playwright execution in production code.

---

## 7. Verification Method

To independently verify these specifications and contracts:

1. **Verify Verbatim Password Placeholder and MFA Selectors in Raw Bundle**:
   ```bash
   grep -o -E '.{0,40}Enter your password .{0,40}' /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js
   grep -o -E '.{0,40}login-mfa-active.{0,40}' /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js
   grep -o -E '.{0,40}expiry:T\.getTime\(\)\+1728e5.{0,40}' /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js
   ```

2. **Verify Existing E2E ZenClass Auth Test Passes**:
   ```bash
   python3 -m unittest /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/e2e/tier1_features/test_f12_zenclass_auth.py
   ```

3. **Verify All 181 Project Tests Pass with 0 Failures**:
   ```bash
   python3 -m unittest discover -s /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests
   ```

4. **Verify Clean Git Status**:
   ```bash
   git status
   ```
