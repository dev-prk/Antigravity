"""
stress_m3_auth.py - Standalone Empirical Stress & Adversarial Test Harness
Milestone 3: Guvi Authentication & Session Management Subsystem
Target modules: drivers/base_driver.py, drivers/guvi_driver.py, core/browser.py

Executed by challenger_m3_1 (Empirical Challenger: Critic & Specialist).
Tests hostile edge cases, malformed credentials, credential rejections,
account activation modals, session probe idempotency, broken storage state,
and network/interstitial resilience.
"""

from __future__ import annotations
import json
import logging
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Ensure project root is in sys.path
PROJECT_ROOT = "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from core.browser import BrowserManager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler, GuardrailEvent, GuardrailType
from core.reporter import SummaryReporter

from drivers.base_driver import (
    BaseDriver,
    DriverError,
    AuthenticationError,
    GuardrailBlockedError,
    ElementNotFoundError,
)
from drivers.guvi_driver import (
    GuviDriver,
    GuviAuthenticationError,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("stress_m3_auth")


# =============================================================================
# Suite 1: Malformed and Boundary Credentials
# =============================================================================

class TestMalformedAndBoundaryCredentials(unittest.TestCase):
    """Stress tests boundary, malformed, empty, and non-string credentials."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            hitl_handler=self.mock_hitl,
            reporter=self.mock_rep,
        )

    def test_01_empty_email_and_empty_password(self):
        """Rejects empty string credentials immediately with GuviAuthenticationError."""
        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="", password="")
        self.assertIn("must not be empty", str(ctx.exception))

    def test_02_whitespace_only_credentials(self):
        """Rejects whitespace-only credentials (spaces, tabs, newlines)."""
        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="   \t  ", password="  \n ")
        self.assertIn("must not be empty", str(ctx.exception))

    def test_03_none_credentials_with_empty_config(self):
        """When config credentials are blank and arguments are None, raises GuviAuthenticationError."""
        with patch.object(config, "USER_EMAIL", ""), patch.object(config, "USER_PASSWORD", ""):
            with self.assertRaises(GuviAuthenticationError) as ctx:
                self.driver.login(email=None, password=None)
            self.assertIn("must not be empty", str(ctx.exception))

    def test_04_unusual_unicode_and_special_characters(self):
        """Ensures driver handles SQL injection strings, emojis, and symbols safely without unhandled error."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        adversarial_email = "test' OR '1'='1'--🚀@guvi.in"
        adversarial_pwd = "P@$$w0rd\u2603\u00A0'\"<script>"

        res = self.driver.login(email=adversarial_email, password=adversarial_pwd, timeout=2000)
        self.assertTrue(res)
        # Verify page.fill or page.type was invoked with adversarial strings
        self.mock_page.type.assert_any_call("input#email", adversarial_email, delay=20)
        self.mock_page.type.assert_any_call("input#password", adversarial_pwd, delay=20)

    def test_05_non_string_credentials_coercion(self):
        """Passes non-string types (integer, boolean) to verify str().strip() safety."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        # Should convert to strings and type them without TypeError
        res = self.driver.login(email=1234567, password=9876543, timeout=2000)
        self.assertTrue(res)


# =============================================================================
# Suite 2: Platform Credential Rejection & Error Feedback
# =============================================================================

class TestPlatformCredentialRejection(unittest.TestCase):
    """Stress tests UI error feedback (.invalid-feedback, alert-danger, etc.)."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            hitl_handler=self.mock_hitl,
        )

    def test_06_invalid_feedback_standard_selector(self):
        """Catches standard .invalid-feedback rejection and takes screenshot."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"

        def fake_wait(sel, **kw):
            if any(k in sel for k in ["email", "password", "login"]):
                return MagicMock()
            raise Exception("Not found")

        self.mock_page.wait_for_selector.side_effect = fake_wait

        err_elem = MagicMock()
        err_elem.is_visible.return_value = True
        err_elem.inner_text.return_value = "Incorrect Email or Password"

        def fake_qs(sel):
            if sel == ".invalid-feedback":
                return err_elem
            return None

        self.mock_page.query_selector.side_effect = fake_qs

        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="devsh.pareek@gmail.com", password="wrong_password")
        self.assertIn("Incorrect Email or Password", str(ctx.exception))
        self.mock_bm.save_screenshot.assert_called_with(name="guvi_auth_invalid_credentials", page=self.mock_page)

    def test_07_all_error_feedback_selectors(self):
        """Verifies each fallback selector in ERROR_FEEDBACK_SELECTORS triggers rejection."""
        selectors_to_test = [
            ".invalid-feedback",
            "#emailgroup .invalid-feedback",
            "#passwordGroup .invalid-feedback",
            ".alert-danger",
            "div:has-text('Incorrect Email or Password')",
        ]

        def fake_wait(sel, **kw):
            if any(k in sel for k in ["email", "password", "login"]):
                return MagicMock()
            raise Exception("Not found")

        for target_sel in selectors_to_test:
            with self.subTest(target_selector=target_sel):
                self.mock_bm.reset_mock()
                self.mock_page.url = "https://www.guvi.in/sign-in/"
                self.mock_page.wait_for_selector.side_effect = fake_wait

                err_elem = MagicMock()
                err_elem.is_visible.return_value = True
                err_elem.inner_text.return_value = f"Failed via {target_sel}"

                def fake_qs(sel, expected=target_sel):
                    if sel == expected:
                        return err_elem
                    return None

                self.mock_page.query_selector.side_effect = fake_qs

                with self.assertRaises(GuviAuthenticationError) as ctx:
                    self.driver.login(email="user@test.com", password="bad_password")
                self.assertIn(f"Failed via {target_sel}", str(ctx.exception))

    def test_08_hidden_invalid_feedback_does_not_falsely_abort(self):
        """Hidden .invalid-feedback (display:none, is_visible=False) must NOT abort valid login."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"

        def fake_wait(sel, **kw):
            if any(k in sel for k in ["email", "password", "login"]):
                return MagicMock()
            raise Exception("Not found")

        self.mock_page.wait_for_selector.side_effect = fake_wait
        self.mock_page.is_checked.return_value = True

        hidden_err = MagicMock()
        hidden_err.is_visible.return_value = False
        hidden_err.inner_text.return_value = "Stale error message"

        def fake_qs(sel):
            if ".invalid-feedback" in sel:
                return hidden_err
            return None

        self.mock_page.query_selector.side_effect = fake_qs

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        res = self.driver.login(email="user@test.com", password="valid_password", timeout=2000)
        self.assertTrue(res)

    def test_09_empty_text_invalid_feedback_ignored(self):
        """Visible .invalid-feedback with whitespace-only text does not cause false rejection."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"

        def fake_wait(sel, **kw):
            if any(k in sel for k in ["email", "password", "login"]):
                return MagicMock()
            raise Exception("Not found")

        self.mock_page.wait_for_selector.side_effect = fake_wait
        self.mock_page.is_checked.return_value = True

        blank_err = MagicMock()
        blank_err.is_visible.return_value = True
        blank_err.inner_text.return_value = "   "

        def fake_qs(sel):
            if ".invalid-feedback" in sel:
                return blank_err
            return None

        self.mock_page.query_selector.side_effect = fake_qs

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        res = self.driver.login(email="user@test.com", password="valid_password", timeout=2000)
        self.assertTrue(res)

    def test_10_multiple_errors_selects_first(self):
        """When both email and password errors are visible, first matching is raised cleanly."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"

        def fake_wait(sel, **kw):
            if any(k in sel for k in ["email", "password", "login"]):
                return MagicMock()
            raise Exception("Not found")

        self.mock_page.wait_for_selector.side_effect = fake_wait

        err1 = MagicMock()
        err1.is_visible.return_value = True
        err1.inner_text.return_value = "Email is invalid"

        err2 = MagicMock()
        err2.is_visible.return_value = True
        err2.inner_text.return_value = "Password is required"

        def fake_qs(sel):
            if sel == ".invalid-feedback":
                return err1
            if sel == "#passwordGroup .invalid-feedback":
                return err2
            return None

        self.mock_page.query_selector.side_effect = fake_qs

        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="bad_email", password="bad_password")
        self.assertIn("Email is invalid", str(ctx.exception))



# =============================================================================
# Suite 3: Account Activation Modal Interception (#myModal, #sendmail)
# =============================================================================

class TestAccountActivationModal(unittest.TestCase):
    """Stress tests account activation modal detection and HITL routing."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            hitl_handler=self.mock_hitl,
        )

    def test_11_mymodal_visible_triggers_hitl_activation(self):
        """Appearance of #myModal triggers HITL handler with task_id='guvi-activation'."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        def fake_is_visible(sel, **kw):
            if "#myModal" in sel or "#sendmail" in sel:
                return True
            return False

        with patch.object(self.driver, "is_visible", side_effect=fake_is_visible):
            self.mock_hitl.check_and_handle_guardrails.return_value = True
            res = self.driver.login(email="devsh.pareek@gmail.com", password="password")
            self.assertTrue(res)
            self.mock_hitl.check_and_handle_guardrails.assert_any_call(
                self.mock_page,
                task_id="guvi-activation",
                context_desc="Guvi Account Activation",
            )

    def test_12_sendmail_standalone_triggers_hitl_activation(self):
        """Even if #myModal wrapper ID is altered, #sendmail triggers HITL guardrail."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        def fake_is_visible(sel, **kw):
            if "#sendmail" in sel:
                return True
            return False

        with patch.object(self.driver, "is_visible", side_effect=fake_is_visible):
            self.mock_hitl.check_and_handle_guardrails.return_value = True
            res = self.driver.login(email="devsh.pareek@gmail.com", password="password")
            self.assertTrue(res)
            self.mock_hitl.check_and_handle_guardrails.assert_any_call(
                self.mock_page,
                task_id="guvi-activation",
                context_desc="Guvi Account Activation",
            )

    def test_13_hitl_guardrail_blocking_propagates(self):
        """If HITL raises GuardrailBlockedError on activation modal, driver does not swallow it."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_is_visible(sel, **kw):
            if "#myModal" in sel or "#sendmail" in sel:
                return True
            return False

        self.mock_hitl.check_and_handle_guardrails.side_effect = GuardrailBlockedError("User halted activation")

        with patch.object(self.driver, "is_visible", side_effect=fake_is_visible):
            with self.assertRaises(GuardrailBlockedError):
                self.driver.login(email="devsh.pareek@gmail.com", password="password")


# =============================================================================
# Suite 4: Idempotent Session Probing & Verification
# =============================================================================

class TestIdempotentSessionProbing(unittest.TestCase):
    """Stress tests cookie-based fast path, URL probe fallback, and idempotency."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_ctx = MagicMock()
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_context.return_value = self.mock_ctx
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = GuviDriver(browser_manager=self.mock_bm)

    def test_14_cookie_fast_path_avoids_navigation(self):
        """Valid 'authToken' starting with 'auth:' immediately succeeds without goto()."""
        self.mock_ctx.cookies.return_value = [
            {"name": "session_id", "value": "1234"},
            {"name": "authToken", "value": "auth:9f8e7d6c5b4a3210", "domain": ".guvi.in"},
        ]
        self.assertTrue(self.driver.is_authenticated())
        self.mock_page.goto.assert_not_called()

    def test_15_cookie_expired_or_corrupt_falls_back(self):
        """Cookie 'authToken' lacking 'auth:' prefix does NOT pass fast-path and triggers fallback probe."""
        self.mock_ctx.cookies.return_value = [
            {"name": "authToken", "value": "expired_or_invalid_format", "domain": ".guvi.in"},
        ]
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.side_effect = Exception("Not found")

        self.assertFalse(self.driver.is_authenticated())
        self.mock_page.goto.assert_called_with(
            self.driver.codekata_url,
            wait_until="domcontentloaded",
            timeout=config.NAVIGATION_TIMEOUT
        )

    def test_16_cookie_empty_value_falls_back(self):
        """Cookie 'authToken' with empty string value falls back to active probe."""
        self.mock_ctx.cookies.return_value = [
            {"name": "authToken", "value": "", "domain": ".guvi.in"},
        ]
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.side_effect = Exception("Not found")

        self.assertFalse(self.driver.is_authenticated())

    def test_17_probe_lands_on_codekata_indicators(self):
        """When cookies are empty, probe navigation to CodeKata with visible post-login indicators succeeds."""
        self.mock_ctx.cookies.return_value = []
        self.mock_page.url = ""  # blank initially

        def fake_goto(url, **kw):
            self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.goto.side_effect = fake_goto

        def fake_is_visible(sel, **kw):
            if sel in self.driver.POST_LOGIN_INDICATORS:
                return True
            return False

        with patch.object(self.driver, "is_visible", side_effect=fake_is_visible):
            self.assertTrue(self.driver.is_authenticated())

    def test_18_probe_localstorage_fallback(self):
        """When DOM indicators not yet hydrated, localStorage 'authToken' starting with 'auth:' verifies session."""
        self.mock_ctx.cookies.return_value = []
        self.mock_page.url = ""

        def fake_goto(url, **kw):
            self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.goto.side_effect = fake_goto
        self.mock_page.evaluate.return_value = "auth:local_storage_valid_token"

        with patch.object(self.driver, "is_visible", return_value=False):
            self.assertTrue(self.driver.is_authenticated())
            self.mock_page.evaluate.assert_called_with("() => localStorage.getItem('authToken')")

    def test_19_ensure_authenticated_consecutive_idempotence(self):
        """Repeated calls to ensure_authenticated() do NOT re-login when session is valid."""
        self.mock_ctx.cookies.return_value = [{"name": "authToken", "value": "auth:token123"}]

        with patch.object(self.driver, "login") as mock_login, patch.object(self.driver, "dismiss_popups") as mock_popups:
            for i in range(5):
                res = self.driver.ensure_authenticated()
                self.assertTrue(res)

            mock_login.assert_not_called()
            self.assertEqual(mock_popups.call_count, 5)

    def test_20_ensure_authenticated_force_relogin_bypasses_cache(self):
        """force_relogin=True bypasses is_authenticated() check and triggers login()."""
        self.mock_ctx.cookies.return_value = [{"name": "authToken", "value": "auth:token123"}]

        with patch.object(self.driver, "login", return_value=True) as mock_login:
            res = self.driver.ensure_authenticated(force_relogin=True)
            self.assertTrue(res)
            mock_login.assert_called_once()


# =============================================================================
# Suite 5: Storage State & Cookie Persistence
# =============================================================================

class TestBrokenStorageStateAndCookiePersistence(unittest.TestCase):
    """Stress tests storage state edge cases: corrupt files, missing dirs, missing keys."""

    def test_21_storage_state_file_missing_handled_gracefully(self):
        """Non-existent storage state file does not raise an exception during restore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_file = Path(tmpdir) / "does_not_exist.json"
            bm = BrowserManager(storage_state_path=missing_file)
            bm._context = MagicMock()
            bm._restore_storage_state()
            bm._context.add_cookies.assert_not_called()

    def test_22_storage_state_corrupt_json_handled_gracefully(self):
        """Corrupt JSON in storage state file logs a warning and does not raise an exception."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad_state.json"
            bad_file.write_text("{corrupt: [json, unquoted")

            bm = BrowserManager(storage_state_path=bad_file)
            bm._context = MagicMock()
            bm._restore_storage_state()
            bm._context.add_cookies.assert_not_called()

    def test_23_storage_state_malformed_cookies_structure(self):
        """JSON with 'cookies' as a non-list string or integer does not crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "non_list.json"
            bad_file.write_text(json.dumps({"cookies": "not_a_list"}))

            bm = BrowserManager(storage_state_path=bad_file)
            bm._context = MagicMock()
            bm._restore_storage_state()

    def test_24_storage_state_valid_cookies_injected(self):
        """Valid cookies list in storage_state.json is passed to context.add_cookies()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            good_file = Path(tmpdir) / "good_state.json"
            cookies_data = [
                {"name": "authToken", "value": "auth:sample", "domain": ".guvi.in", "path": "/"}
            ]
            good_file.write_text(json.dumps({"cookies": cookies_data}))

            bm = BrowserManager(storage_state_path=good_file)
            bm._context = MagicMock()
            bm._restore_storage_state()
            bm._context.add_cookies.assert_called_once_with(cookies_data)

    def test_25_persist_session_disk_failure_handled(self):
        """If save_storage_state() fails due to disk error, persist_session() does not crash."""
        mock_bm = MagicMock(spec=BrowserManager)
        mock_bm.save_storage_state.side_effect = PermissionError("Read-only filesystem")

        driver = GuviDriver(browser_manager=mock_bm)
        # Should not raise exception
        driver.persist_session()
        mock_bm.save_storage_state.assert_called_once()


# =============================================================================
# Suite 6: Interstitials, Timeouts & Error Recovery
# =============================================================================

class TestInterstitialsTimeoutsAndErrorRecovery(unittest.TestCase):
    """Stress tests Cloudflare Turnstile, reCAPTCHA, login timeouts, and DOM alterations."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            hitl_handler=self.mock_hitl,
        )

    def test_26_pre_login_guardrail_check(self):
        """Guardrails are actively checked immediately upon sign-in page load."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        res = self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertTrue(res)

        # Assert check_and_handle_guardrails was called for page load
        self.mock_hitl.check_and_handle_guardrails.assert_any_call(
            self.mock_page,
            task_id="guvi-auth",
            context_desc="Guvi Sign-In Page Load",
        )

    def test_27_post_submit_guardrail_check(self):
        """Guardrails are actively checked immediately after credential submission."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        res = self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertTrue(res)

        self.mock_hitl.check_and_handle_guardrails.assert_any_call(
            self.mock_page,
            task_id="guvi-auth",
            context_desc="Guvi Credential Post-Submission",
        )

    def test_28_login_timeout_raises_authentication_error(self):
        """When page remains stuck on /sign-in/ beyond timeout, raises GuviAuthenticationError and saves screenshot."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        with patch.object(self.driver, "is_visible", return_value=False):
            with self.assertRaises(GuviAuthenticationError) as ctx:
                # 300ms timeout for rapid test execution
                self.driver.login(email="devsh.pareek@gmail.com", password="password", timeout=300)
            self.assertIn("Timed out waiting for Guvi login completion", str(ctx.exception))
            self.mock_bm.save_screenshot.assert_called_with(name="guvi_auth_timeout", page=self.mock_page)

    def test_29_missing_login_form_fields_raises_element_not_found(self):
        """When email or password field is missing from DOM, raises ElementNotFoundError."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        # wait_for_selector fails for all selectors
        self.mock_page.wait_for_selector.side_effect = Exception("Not found")

        with self.assertRaises(ElementNotFoundError) as ctx:
            self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertIn("Could not locate login form fields", str(ctx.exception))
        self.mock_bm.save_screenshot.assert_called_with(name="guvi_login_form_missing", page=self.mock_page)

    def test_30_missing_submit_button_raises_element_not_found(self):
        """When form inputs exist but submit button is missing, raises ElementNotFoundError."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"

        def fake_wait(sel, **kw):
            if "email" in sel or "password" in sel:
                return MagicMock()
            raise Exception("Submit button missing")

        self.mock_page.wait_for_selector.side_effect = fake_wait

        with self.assertRaises(ElementNotFoundError) as ctx:
            self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertIn("Could not locate submit button", str(ctx.exception))
        self.mock_bm.save_screenshot.assert_called_with(name="guvi_submit_button_missing", page=self.mock_page)

    def test_31_navigation_network_error_handled_gracefully(self):
        """Network error on page.goto does not cause unhandled crash in navigate()."""
        self.mock_page.url = "about:blank"
        self.mock_page.goto.side_effect = Exception("net::ERR_INTERNET_DISCONNECTED")

        # Calling navigate should log warning and return page without raising unhandled exception
        page = self.driver.navigate("https://www.guvi.in/sign-in/")
        self.assertEqual(page, self.mock_page)
        self.mock_page.bring_to_front.assert_called()


# =============================================================================
# Main Test Execution
# =============================================================================

def run_stress_suite() -> unittest.TestResult:
    """Executes the full stress test suite and prints formatted results."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestMalformedAndBoundaryCredentials))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformCredentialRejection))
    suite.addTests(loader.loadTestsFromTestCase(TestAccountActivationModal))
    suite.addTests(loader.loadTestsFromTestCase(TestIdempotentSessionProbing))
    suite.addTests(loader.loadTestsFromTestCase(TestBrokenStorageStateAndCookiePersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestInterstitialsTimeoutsAndErrorRecovery))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    result = run_stress_suite()
    sys.exit(0 if result.wasSuccessful() else 1)
