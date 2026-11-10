"""
tests/test_m4_zenclass_tasks.py - Comprehensive Unit and Integration Test Suite for Milestone 4.

Validates:
- Module 41486 13-field dynamic mapping table & regex URL validation
- Verbatim trailing space in password placeholder & DOM selectors
- ZenClass credential login lifecycle, auto-redirect, error feedback, and MFA detection
- 4-tier session recovery cascade (DOM anchor, storage expiry, navigation probe, login fallback)
- Kanban board task discovery across Active, Pending, Completed columns & "Attend" quiz classification
- Task detail modal extraction & clean dismissal
- Dynamic 13-field submission modal mapping, validation, and filling
- Ephemeral 2.0s UI confirmation popup verification with spelling resilience
- SQLite StateManager persistence and 9 R3 fields
- Full pipeline orchestrator (run_task_pipeline) with limit and task_id targeting
- CLI integration (run-zenclass-tasks and run-zenclass)
- Zero mock evaluate shims static verification
- Mandatory autospec=True on all @patch calls
"""

from __future__ import annotations
import inspect
import json
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult, TaskRecord
from core.hitl_handler import HitlHandler, GuardrailEvent, GuardrailType
from core.reporter import SummaryReporter

from drivers.base_driver import (
    BaseDriver,
    DriverError,
    AuthenticationError,
    GuardrailBlockedError,
    ElementNotFoundError,
)
from drivers.zenclass_tasks_driver import (
    ZenClassTasksDriver,
    ZenClassDriver,
    ZenClassAuthenticationError,
    ZenClassMFABlockedError,
    DiscoveredTask,
    ZENCLASS_TASK_FIELD_MAP,
    LABEL_TO_FIELD_KEY,
    ZENCLASS_URL_REGEX,
    ZENCLASS_CONFIRMATION_REGEX,
)
from drivers import (
    ZenClassTasksDriver as ExportedZenClassTasksDriver,
    ZenClassDriver as ExportedZenClassDriver,
    ZenClassAuthenticationError as ExportedZenClassAuthError,
    ZenClassMFABlockedError as ExportedZenClassMFABlockedError,
)

from tests.e2e.harness.dom_fixtures import (
    ZENCLASS_LOGIN_HTML,
    ZENCLASS_TASKS_HTML,
    ZENCLASS_SUBMISSION_MODAL_HTML,
)
from main import create_cli_parser, AutomationRunner


# =============================================================================
# 1. Module 41486 Field Map & URL Regex Unit Tests
# =============================================================================

class TestModule41486FieldMappingAndRegex(unittest.TestCase):
    """Verifies Module 41486 dynamic field map and URL validation specifications."""

    def test_canonical_13_fields_present(self):
        """Verifies exactly 13 canonical fields exported by Module 41486."""
        self.assertEqual(len(ZENCLASS_TASK_FIELD_MAP), 13)
        expected_keys = [
            "frontEnd_Deployed_Url",
            "backEnd_Deployed_Url",
            "frontEnd_SourceCode",
            "backEnd_SourceCode",
            "github_Url",
            "g-drive_Url",
            "submission_Url",
            "linkedin_post_Url",
            "document_Url",
            "figma_Url",
            "figma_prototype_Url",
            "dribble_Url",
            "behance_Url",
        ]
        for k in expected_keys:
            self.assertIn(k, ZENCLASS_TASK_FIELD_MAP)
            self.assertTrue(len(ZENCLASS_TASK_FIELD_MAP[k]) > 0)

    def test_bidirectional_and_normalized_label_lookup(self):
        """Verifies human label normalization to canonical keys."""
        # Exact match
        self.assertEqual(LABEL_TO_FIELD_KEY["frontend deployed url"], "frontEnd_Deployed_Url")
        self.assertEqual(LABEL_TO_FIELD_KEY["github url"], "github_Url")
        self.assertEqual(LABEL_TO_FIELD_KEY["frontend source code"], "frontEnd_SourceCode")
        self.assertEqual(LABEL_TO_FIELD_KEY["backend source code"], "backEnd_SourceCode")
        self.assertEqual(LABEL_TO_FIELD_KEY["submission url"], "submission_Url")

        # Hyphenated and common alias variants
        self.assertEqual(LABEL_TO_FIELD_KEY.get("front-end deployed url"), "frontEnd_Deployed_Url")
        self.assertEqual(LABEL_TO_FIELD_KEY.get("gdrive url"), "g-drive_Url")
        self.assertEqual(LABEL_TO_FIELD_KEY.get("google drive url"), "g-drive_Url")
        self.assertEqual(LABEL_TO_FIELD_KEY.get("dribbble url"), "dribble_Url")

    def test_url_validation_regex_valid_cases(self):
        """Verifies platform regex matches valid URLs (http, https, ftp)."""
        valid_urls = [
            "https://github.com/testuser/repo",
            "http://localhost:3000",
            "https://zenclass.in/tasks?batch=12",
            "https://project.vercel.app/demo#section",
            "ftp://files.example.org/submission.zip",
            "https://sub.domain.co.in/app?v=1&t=2",
            "http://127.0.0.1:8080/path",
        ]
        for url in valid_urls:
            self.assertTrue(
                bool(ZENCLASS_URL_REGEX.match(url)),
                f"Valid URL was rejected by regex: {url}"
            )

    def test_url_validation_regex_invalid_cases(self):
        """Verifies platform regex rejects malformed or unauthorized protocol URLs."""
        invalid_urls = [
            "",
            "   ",
            "github.com/no-protocol",
            "www.example.com",
            "https://has space.com",
            "https://repo.com/path with spaces",
            "javascript:alert(1)",
            "file:///etc/passwd",
            'https://example.com/quote"',
            "data:text/html;base64,PHNjcmlwdD4=",
        ]
        for url in invalid_urls:
            self.assertFalse(
                bool(ZENCLASS_URL_REGEX.match(url)),
                f"Invalid URL was unexpectedly matched by regex: {url}"
            )

    def test_confirmation_regex_spelling_resilience(self):
        """Verifies confirmation regex handles both platform typo ('Suceessfully') and standard ('Successfully')."""
        self.assertTrue(bool(ZENCLASS_CONFIRMATION_REGEX.search("Task Submitted Suceessfully")))
        self.assertTrue(bool(ZENCLASS_CONFIRMATION_REGEX.search("Task Submitted Successfully")))
        self.assertTrue(bool(ZENCLASS_CONFIRMATION_REGEX.search("task submitted sucessfully")))
        self.assertTrue(bool(ZENCLASS_CONFIRMATION_REGEX.search("Task Submitted Suceeessfully")))
        self.assertFalse(bool(ZENCLASS_CONFIRMATION_REGEX.search("Task Submission Failed")))


# =============================================================================
# 2. DOM Selectors & Material UI Trailing Space Integrity
# =============================================================================

class TestZenClassDOMSelectors(unittest.TestCase):
    """Verifies selector definitions and whitespace fidelity against production markup."""

    def test_password_selector_verbatim_trailing_space(self):
        """Authoritative source: spec_miner_survey_3 §1.1 - exact trailing space in password placeholder."""
        trailing_space_found = False
        for sel in ZenClassTasksDriver.PASSWORD_SELECTORS:
            if 'placeholder="Enter your password "' in sel:
                trailing_space_found = True
                break
        self.assertTrue(trailing_space_found, "Primary password selector must include exact trailing space")

    def test_email_selectors_contain_material_ui_classes(self):
        """Verifies presence of Material UI .email-input in selector cascade."""
        self.assertTrue(any(".email-input" in sel for sel in ZenClassTasksDriver.EMAIL_SELECTORS))

    def test_submit_button_selectors_contain_primary_btn(self):
        """Verifies sign-in submit button selectors match production CSS classes."""
        self.assertTrue(any(".sign-in-btn-container" in sel or "sign-in-pad" in sel for sel in ZenClassTasksDriver.SUBMIT_SELECTORS))

    def test_mfa_selectors_contain_active_classes(self):
        """Verifies MFA selectors include .login-mfa-active and .login-mfa-wrapper."""
        self.assertIn(".login-mfa-active", ZenClassTasksDriver.MFA_SELECTORS)
        self.assertIn(".login-mfa-wrapper", ZenClassTasksDriver.MFA_SELECTORS)

    def test_kanban_board_selectors_match_spec(self):
        """Verifies Kanban columns and card class selectors match specification."""
        self.assertIn(".column.active-tasks", ZenClassTasksDriver.SEL_COLUMN_ACTIVE)
        self.assertIn(".column.pending-tasks", ZenClassTasksDriver.SEL_COLUMN_PENDING)
        self.assertIn(".column.completed-tasks", ZenClassTasksDriver.SEL_COLUMN_COMPLETED)
        self.assertIn(".itemactive-tasks", ZenClassTasksDriver.SEL_CARD_ACTIVE)
        self.assertIn(".itempending-tasks", ZenClassTasksDriver.SEL_CARD_PENDING)
        self.assertIn(".itemcompleted-tasks", ZenClassTasksDriver.SEL_CARD_COMPLETED)


# =============================================================================
# 3. Authentication & Session Recovery Cascade Tests
# =============================================================================

class TestZenClassAuthentication(unittest.TestCase):
    """Verifies foreground visible login, MFA handling, and 4-tier recovery cascade."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_page.url = "https://v2.zenclass.in/login"
        self.mock_bm.get_page.return_value = self.mock_page
        self.mock_ctx = MagicMock()
        self.mock_bm.get_context.return_value = self.mock_ctx

        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            hitl_handler=self.mock_hitl,
            reporter=self.mock_rep,
        )

    def test_empty_credentials_raises_authentication_error(self):
        """Verifies login raises ZenClassAuthenticationError when email/password are empty."""
        with self.assertRaises(ZenClassAuthenticationError):
            self.driver.login(email="", password="secret")

        with self.assertRaises(ZenClassAuthenticationError):
            self.driver.login(email="user@test.com", password="  ")

    def test_login_auto_redirect_detects_active_session(self):
        """Verifies navigating to /login when already logged in detects redirect away."""
        self.mock_page.url = "https://v2.zenclass.in/dashboard"
        with patch.object(self.driver, "sync_session_state", autospec=True) as mock_sync, \
             patch.object(self.driver, "persist_session", autospec=True) as mock_persist, \
             patch.object(self.driver, "dismiss_modals", autospec=True) as mock_dismiss:
            res = self.driver.login(email="user@zenclass.in", password="Password@123")
            self.assertTrue(res)
            mock_sync.assert_called_once()
            mock_persist.assert_called_once()
            mock_dismiss.assert_called_once()

    def test_successful_login_sequence(self):
        """Verifies standard successful login sequence with typing and post-login verification."""
        self.mock_page.url = "https://v2.zenclass.in/login"

        def mock_wait_for_selector(sel, state="visible", timeout=3000):
            if "mail" in sel or "email" in sel or "password" in sel or "sign-in" in sel or "Sign in" in sel:
                return MagicMock()
            if "commonTaskContainer" in sel or "active-tasks" in sel:
                return MagicMock()
            return None

        self.mock_page.wait_for_selector.side_effect = mock_wait_for_selector
        self.mock_page.query_selector.return_value = None  # no error message

        # Simulate navigation to /tasks post submit
        def after_click(sel, force=False):
            self.mock_page.url = "https://v2.zenclass.in/tasks"

        self.mock_page.click.side_effect = after_click

        with patch.object(self.driver, "sync_session_state", autospec=True) as mock_sync, \
             patch.object(self.driver, "persist_session", autospec=True) as mock_persist, \
             patch.object(self.driver, "dismiss_modals", autospec=True):
            res = self.driver.login(email="student@zenclass.in", password="Password@123", timeout=2000.0)
            self.assertTrue(res)
            mock_sync.assert_called_once()
            mock_persist.assert_called_once()

    def test_login_credential_rejection_raises_error(self):
        """Verifies inline error feedback raises ZenClassAuthenticationError."""
        self.mock_page.url = "https://v2.zenclass.in/login"

        mock_err_el = MagicMock()
        mock_err_el.is_visible.return_value = True
        mock_err_el.inner_text.return_value = "*Incorrect email or password!"

        def mock_qs(sel):
            if "MuiFormHelperText-root" in sel or "invalid-feedback" in sel or "error" in sel:
                return mock_err_el
            return None

        self.mock_page.query_selector.side_effect = mock_qs

        with patch.object(self.driver, "find_first_selector", autospec=True) as mock_find, \
             patch.object(self.driver, "save_screenshot", autospec=True):
            mock_find.return_value = "input#test"
            with self.assertRaises(ZenClassAuthenticationError) as ctx:
                self.driver.login(email="bad@zenclass.in", password="WrongPassword", timeout=2000.0)
            self.assertIn("rejected credentials", str(ctx.exception))

    def test_login_account_disabled_raises_guardrail_blocked(self):
        """Verifies 'Account disabled' feedback raises GuardrailBlockedError (not retryable auth error)."""
        self.mock_page.url = "https://v2.zenclass.in/login"

        mock_err_el = MagicMock()
        mock_err_el.is_visible.return_value = True
        mock_err_el.inner_text.return_value = "Account disabled. Contact Coordinator."

        def mock_qs(sel):
            if "MuiFormHelperText-root" in sel or "error" in sel:
                return mock_err_el
            return None

        self.mock_page.query_selector.side_effect = mock_qs

        with patch.object(self.driver, "find_first_selector", autospec=True) as mock_find, \
             patch.object(self.driver, "save_screenshot", autospec=True):
            mock_find.return_value = "input#test"
            with self.assertRaises(GuardrailBlockedError) as ctx:
                self.driver.login(email="disabled@zenclass.in", password="Password@123", timeout=2000.0)
            self.assertIn("Account restricted", str(ctx.exception))

    def test_mfa_challenge_triggers_hitl_guardrail(self):
        """Verifies MFA challenge (.login-mfa-active) delegates to HitlHandler."""
        self.mock_page.url = "https://v2.zenclass.in/login"
        self.mock_hitl.check_and_handle_guardrails.return_value = True

        with patch.object(self.driver, "find_first_selector", autospec=True) as mock_find:
            mock_find.return_value = ".login-mfa-active"
            triggered = self.driver.check_mfa_guardrail(task_id="test-mfa")
            self.assertTrue(triggered)
            self.mock_hitl.check_and_handle_guardrails.assert_called_once_with(
                self.mock_page,
                task_id="test-mfa",
                context_desc="ZenClass MFA Two-Factor Verification"
            )

    # 4-Tier Session Recovery Tests
    def test_tier_1_fast_path_dom_anchor_recovery(self):
        """Tier 1: Current open page on /tasks with visible DOM indicator succeeds without navigation."""
        self.mock_page.url = "https://v2.zenclass.in/tasks"
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True) as mock_nav:
            mock_vis.return_value = True
            is_auth = self.driver.is_authenticated()
            self.assertTrue(is_auth)
            mock_nav.assert_not_called()  # Zero reloads needed

    def test_tier_2_storage_unexpired_token_recovery(self):
        """Tier 2: Valid unexpired authToken in localStorage verifies session."""
        self.mock_page.url = "https://v2.zenclass.in/dashboard"
        expiry_future = (time.time() + 3600) * 1000
        token_payload = json.dumps({"authToken": "valid_jwt_token_12345", "expiry": expiry_future})
        self.mock_page.evaluate.return_value = token_payload

        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis:
            mock_vis.return_value = False  # Tier 1 anchor not matched
            is_auth = self.driver.is_authenticated()
            self.assertTrue(is_auth)

    def test_tier_2_storage_expired_token_rejected(self):
        """Tier 2: Expired authToken in localStorage is rejected and falls back."""
        self.mock_page.url = "https://v2.zenclass.in/login"
        expiry_past = (time.time() - 3600) * 1000
        token_payload = json.dumps({"authToken": "expired_jwt_token", "expiry": expiry_past})
        self.mock_page.evaluate.return_value = token_payload

        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True):
            mock_vis.return_value = False
            # Probe navigation redirects to /login
            self.mock_page.url = "https://v2.zenclass.in/login"
            is_auth = self.driver.is_authenticated()
            self.assertFalse(is_auth)

    def test_tier_3_navigation_probe_recovery(self):
        """Tier 3: Platform probe navigation to /tasks validates active session."""
        self.mock_page.url = "about:blank"
        self.mock_page.evaluate.return_value = None

        def probe_nav(url, wait_until="domcontentloaded", timeout=None):
            self.mock_page.url = "https://v2.zenclass.in/tasks"

        with patch.object(self.driver, "navigate", autospec=True) as mock_nav, \
             patch.object(self.driver, "check_guardrails", autospec=True), \
             patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "sync_session_state", autospec=True), \
             patch.object(self.driver, "persist_session", autospec=True):
            mock_nav.side_effect = probe_nav
            # Post-login indicator visible after navigation
            mock_vis.side_effect = lambda sel, timeout=0.5: sel in ZenClassTasksDriver.POST_LOGIN_DOM_INDICATORS

            is_auth = self.driver.is_authenticated()
            self.assertTrue(is_auth)

    def test_tier_4_probe_redirected_to_login_fails(self):
        """Tier 4: Probe navigation redirects to /login -> returns False (triggers credential fallback)."""
        self.mock_page.url = "about:blank"
        self.mock_page.evaluate.return_value = None

        def probe_nav(url, wait_until="domcontentloaded", timeout=None):
            self.mock_page.url = "https://v2.zenclass.in/login"

        with patch.object(self.driver, "navigate", autospec=True) as mock_nav, \
             patch.object(self.driver, "check_guardrails", autospec=True), \
             patch.object(self.driver, "is_visible", autospec=True) as mock_vis:
            mock_nav.side_effect = probe_nav
            mock_vis.return_value = False
            is_auth = self.driver.is_authenticated()
            self.assertFalse(is_auth)

    def test_ensure_authenticated_avoids_redundant_login(self):
        """Verifies ensure_authenticated reuses active session without calling login."""
        with patch.object(self.driver, "is_authenticated", autospec=True) as mock_is_auth, \
             patch.object(self.driver, "login", autospec=True) as mock_login, \
             patch.object(self.driver, "dismiss_modals", autospec=True):
            mock_is_auth.return_value = True
            res = self.driver.ensure_authenticated(force_relogin=False)
            self.assertTrue(res)
            mock_login.assert_not_called()

    def test_ensure_authenticated_with_force_relogin(self):
        """Verifies ensure_authenticated with force_relogin=True executes login."""
        with patch.object(self.driver, "is_authenticated", autospec=True) as mock_is_auth, \
             patch.object(self.driver, "login", autospec=True) as mock_login:
            mock_is_auth.return_value = True
            mock_login.return_value = True
            res = self.driver.ensure_authenticated(force_relogin=True)
            self.assertTrue(res)
            mock_login.assert_called_once()


# =============================================================================
# 4. Kanban Board Discovery & Classification Unit Tests
# =============================================================================

class TestZenClassTasksDiscovery(unittest.TestCase):
    """Verifies parsing of Kanban columns, card metadata, redo tags, and action buttons."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            hitl_handler=self.mock_hitl,
        )

    def test_classify_task_state_action_attend_marked_blocked(self):
        """Verifies card with 'Attend' button (external quiz) is classified as BLOCKED (Requirement R1/R2)."""
        task = DiscoveredTask(
            task_id="quiz-101",
            title="Module 1 Evaluation Quiz",
            column="active",
            action_type="ATTEND",
        )
        status, result, next_act, reason = self.driver._classify_task_state(task)
        self.assertEqual(status, TaskStatus.BLOCKED.value)
        self.assertEqual(result, TaskResult.AWAITING_INPUT.value)
        self.assertEqual(next_act, "REQUIRES_HUMAN_INTERACTIVE_ASSESSMENT")
        self.assertIn("interactive test session", reason or "")

    def test_classify_task_state_redo_task(self):
        """Verifies card with Redo tag or Re-submit button is classified as REDO."""
        task = DiscoveredTask(
            task_id="task-102",
            title="Async Await Refactoring",
            column="pending",
            is_redo=True,
            action_type="RESUBMIT",
        )
        status, result, next_act, reason = self.driver._classify_task_state(task)
        self.assertEqual(status, TaskStatus.REDO.value)
        self.assertEqual(result, TaskResult.UNATTEMPTED.value)
        self.assertEqual(next_act, "SOLVE_AND_SUBMIT")
        self.assertIsNone(reason)

    def test_classify_task_state_completed_column(self):
        """Verifies card in completed column is classified as COMPLETED / PASSED."""
        task = DiscoveredTask(
            task_id="task-100",
            title="HTML Fundamentals",
            column="completed",
            score="10/10",
            action_type="EDIT",
        )
        status, result, next_act, reason = self.driver._classify_task_state(task)
        self.assertEqual(status, TaskStatus.COMPLETED.value)
        self.assertEqual(result, TaskResult.PASSED.value)
        self.assertEqual(next_act, "NONE")

    def test_discover_tasks_parses_board_and_persists_state(self):
        """Verifies discover_tasks parses cards across all 3 columns and records 9 R3 fields."""
        # Create mock elements representing the 3 cards in ZENCLASS_TASKS_HTML
        card_active = MagicMock()
        card_active.get_attribute.side_effect = lambda attr: "task-101" if attr == "data-task-id" else "itemactive-tasks"
        card_active.inner_text.return_value = "Day 1: Basic JavaScript Functions\nJavaScript\nSubmit"
        title_el1 = MagicMock()
        title_el1.inner_text.return_value = "Day 1: Basic JavaScript Functions"
        submit_btn1 = MagicMock()
        submit_btn1.inner_text.return_value = "Submit"
        tag_el1 = MagicMock()
        tag_el1.inner_text.return_value = "JavaScript"

        def qs1(sel):
            if "task-name" in sel:
                return title_el1
            if "submit" in sel:
                return submit_btn1
            return None

        card_active.query_selector.side_effect = qs1
        card_active.query_selector_all.side_effect = lambda sel: [tag_el1] if "common-tags" in sel else []

        card_pending = MagicMock()
        card_pending.get_attribute.side_effect = lambda attr: "task-102" if attr == "data-task-id" else "itempending-tasks"
        title_el2 = MagicMock()
        title_el2.inner_text.return_value = "Day 2: Async Await & Fetch API"
        redo_el = MagicMock()
        redo_el.inner_text.return_value = "Redo"
        submit_btn2 = MagicMock()
        submit_btn2.inner_text.return_value = "Re-submit"

        def qs2(sel):
            if "task-name" in sel:
                return title_el2
            if "redo" in sel:
                return redo_el
            if "submit" in sel:
                return submit_btn2
            return None

        card_pending.query_selector.side_effect = qs2
        card_pending.query_selector_all.return_value = []

        card_completed = MagicMock()
        card_completed.get_attribute.side_effect = lambda attr: "task-100" if attr == "data-task-id" else "itemcompleted-tasks"
        title_el3 = MagicMock()
        title_el3.inner_text.return_value = "Day 0: HTML & CSS Introduction"
        score_el = MagicMock()
        score_el.inner_text.return_value = "10/10"
        edit_btn = MagicMock()
        edit_btn.inner_text.return_value = "Edit"

        def qs3(sel):
            if "task-name" in sel:
                return title_el3
            if "score" in sel:
                return score_el
            if "edit" in sel:
                return edit_btn
            return None

        card_completed.query_selector.side_effect = qs3
        card_completed.query_selector_all.return_value = []

        # Mock page query for column elements
        col_active = MagicMock()
        col_active.query_selector_all.return_value = [card_active]

        col_pending = MagicMock()
        col_pending.query_selector_all.return_value = [card_pending]

        col_completed = MagicMock()
        col_completed.query_selector_all.return_value = [card_completed]

        def page_qs(sel):
            if "active-tasks" in sel:
                return col_active
            if "pending-tasks" in sel:
                return col_pending
            if "completed-tasks" in sel:
                return col_completed
            return None

        self.mock_page.query_selector.side_effect = page_qs
        self.mock_page.query_selector_all.return_value = []

        with patch.object(self.driver, "navigate", autospec=True), \
             patch.object(self.driver, "check_guardrails", autospec=True):
            tasks = self.driver.discover_tasks()

            self.assertEqual(len(tasks), 3)
            t_map = {t.task_id: t for t in tasks}

            self.assertIn("task-101", t_map)
            self.assertEqual(t_map["task-101"].action_type, "SUBMIT")
            self.assertEqual(t_map["task-101"].column, "active")

            self.assertIn("task-102", t_map)
            self.assertTrue(t_map["task-102"].is_redo)
            self.assertEqual(t_map["task-102"].action_type, "RESUBMIT")

            self.assertIn("task-100", t_map)
            self.assertEqual(t_map["task-100"].score, "10/10")

            # Verify SQLite StateManager batch persistence
            self.mock_sm.batch_record_tasks.assert_called_once()
            persisted_list = self.mock_sm.batch_record_tasks.call_args[0][0]
            self.assertEqual(len(persisted_list), 3)


# =============================================================================
# 5. Task Detail Modal Extraction Unit Tests
# =============================================================================

class TestZenClassTaskDetailExtraction(unittest.TestCase):
    """Verifies problem statement HTML extraction and clean dismissal."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
        )

    def test_extract_task_details_success(self):
        """Verifies extracting title, HTML problem content, tags, attachment link, and closing modal."""
        mock_title = MagicMock()
        mock_title.inner_text.return_value = "Day 1: Basic JavaScript Functions"

        mock_content = MagicMock()
        mock_content.inner_html.return_value = "<p>Write a function that calculates factorial.</p>"
        mock_content.inner_text.return_value = "Write a function that calculates factorial."

        mock_tag = MagicMock()
        mock_tag.inner_text.return_value = "JavaScript"

        mock_att = MagicMock()
        mock_att.get_attribute.return_value = "https://zenclass.in/instructions/day1.pdf"

        mock_close = MagicMock()
        mock_close.is_visible.return_value = True

        def modal_qs(sel):
            if "title" in sel or "name" in sel:
                return mock_title
            if "content" in sel or "text-editor" in sel:
                return mock_content
            if "instruction" in sel:
                return mock_att
            if "close" in sel or "✕" in sel or "back" in sel:
                return mock_close
            return None

        self.mock_page.query_selector.side_effect = modal_qs
        self.mock_page.query_selector_all.side_effect = lambda sel: [mock_tag] if "tags" in sel or "common-tags" in sel else []

        with patch.object(self.driver, "safe_click", autospec=True):
            details = self.driver.get_task_details("task-101")

            self.assertEqual(details["title"], "Day 1: Basic JavaScript Functions")
            self.assertIn("factorial", details["html_content"])
            self.assertEqual(details["tags"], ["JavaScript"])
            self.assertEqual(details["attachment_url"], "https://zenclass.in/instructions/day1.pdf")
            mock_close.click.assert_called_once()


# =============================================================================
# 6. Dynamic 13-Field Submission & Confirmation Unit Tests
# =============================================================================

class TestZenClassDynamicSubmission(unittest.TestCase):
    """Verifies dynamic field discovery, URL regex checking, and confirmation handling."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
        )

    def test_submit_task_missing_required_url_fails(self):
        """Verifies submission halts and records FAILED status when required field URL is not provided."""
        # Create wrapper demanding 'frontEnd_Deployed_Url'
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Frontend Deployed URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = "frontEnd_Deployed_Url"

        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            # Only provide github_Url, missing frontEnd_Deployed_Url
            res = self.driver.submit_task("task-101", deliverable_urls={"github_Url": "https://github.com/u/repo"})
            self.assertFalse(res["success"])
            self.assertIn("Missing required submission URL", res["error"])
            self.mock_sm.update_task_status.assert_called()

    def test_submit_task_malformed_url_fails_regex(self):
        """Verifies submission halts and records FAILED status when candidate URL violates regex."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Github URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = "github_Url"

        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            # Invalid URL without protocol
            res = self.driver.submit_task("task-101", deliverable_urls={"github_Url": "not-a-valid-url"})
            self.assertFalse(res["success"])
            self.assertIn("failed regex validation", res["error"])

    def test_submit_task_success_with_spelling_resilient_confirmation(self):
        """Verifies full successful submission matching platform 'Task Submitted Suceessfully'."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Github URL"
        input_el = MagicMock()

        def wrapper_qs(sel):
            if "label" in sel:
                return label_el
            if "input" in sel:
                return input_el
            return None

        wrapper.query_selector.side_effect = wrapper_qs
        wrapper.get_attribute.return_value = "github_Url"

        self.mock_page.query_selector_all.return_value = [wrapper]

        # Modal submit button
        modal_submit_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_submit_btn

        # Confirmation popup mock
        mock_popup = MagicMock()
        mock_text = MagicMock()
        mock_text.inner_text.return_value = "Task Submitted Suceessfully"  # note platform spelling

        def page_qs(sel):
            if "sucess-popup-text" in sel or "modal-message" in sel:
                return mock_text
            return None

        self.mock_page.query_selector.side_effect = page_qs

        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task(
                "task-101",
                deliverable_urls={"github_Url": "https://github.com/student/day1-repo"}
            )
            self.assertTrue(res["success"])
            input_el.fill.assert_called_with("https://github.com/student/day1-repo")
            modal_submit_btn.click.assert_called_once()
            self.mock_sm.update_task_status.assert_called()

    def test_verify_submission_confirmation_detects_error_popup(self):
        """Verifies platform error popup is detected and task is marked FAILED."""
        mock_popup = MagicMock()
        mock_text = MagicMock()
        mock_text.inner_text.return_value = "Platform Error: Submission deadline has passed."

        self.mock_page.wait_for_selector.return_value = mock_popup
        self.mock_page.query_selector.side_effect = lambda sel: mock_text if "text" in sel or "modal" in sel else None

        res = self.driver.verify_submission_confirmation(
            task_id="task-105",
            start_time=time.time(),
            filled_fields={"github_Url": "https://github.com/u/repo"}
        )
        self.assertFalse(res["success"])
        self.assertIn("submission error", res["error"].lower())


# =============================================================================
# 7. Pipeline Orchestrator & CLI Integration Tests
# =============================================================================

class TestZenClassPipelineAndCLI(unittest.TestCase):
    """Verifies run_task_pipeline orchestration and main.py CLI integration."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            reporter=self.mock_rep,
        )

    def test_run_task_pipeline_auth_failure_aborts(self):
        """Verifies pipeline aborts immediately if authentication fails."""
        with patch.object(self.driver, "ensure_authenticated", autospec=True) as mock_auth:
            mock_auth.return_value = False
            summary = self.driver.run_task_pipeline()
            self.assertFalse(summary["success"])
            self.assertEqual(summary["error"], "Authentication failed")

    def test_run_task_pipeline_limit_and_attend_handling(self):
        """Verifies pipeline processes queue up to limit and handles 'Attend' quizzes cleanly."""
        t1 = DiscoveredTask(task_id="t1", title="Task 1", column="active", action_type="SUBMIT")
        t2 = DiscoveredTask(task_id="t2", title="Task 2 Quiz", column="active", action_type="ATTEND")
        t3 = DiscoveredTask(task_id="t3", title="Task 3", column="pending", is_redo=True, action_type="RESUBMIT")

        with patch.object(self.driver, "ensure_authenticated", autospec=True) as mock_auth, \
             patch.object(self.driver, "discover_tasks", autospec=True) as mock_disc, \
             patch.object(self.driver, "submit_task", autospec=True) as mock_submit:
            mock_auth.return_value = True
            mock_disc.return_value = [t1, t2, t3]
            mock_submit.return_value = {"success": True, "task_id": "t1"}

            # Limit = 2
            summary = self.driver.run_task_pipeline(limit=2)

            self.assertEqual(summary["total_discovered"], 3)
            self.assertEqual(summary["queue_size"], 2)
            self.assertEqual(summary["completed"], 2)
            self.mock_rep.generate_all_reports.assert_called_once()

    def test_cli_parser_contains_run_zenclass_tasks(self):
        """Verifies create_cli_parser exposes run-zenclass-tasks and run-zenclass."""
        parser = create_cli_parser()
        args1 = parser.parse_args(["run-zenclass-tasks", "--task-id", "task-101"])
        self.assertEqual(args1.command, "run-zenclass-tasks")
        self.assertEqual(args1.task_id, "task-101")

        args2 = parser.parse_args(["run-zenclass", "--type", "tasks", "--task-id", "task-102"])
        self.assertEqual(args2.command, "run-zenclass")
        self.assertEqual(args2.type, "tasks")

    def test_drivers_package_exports_zenclass_tasks_driver(self):
        """Verifies drivers/__init__.py exports ZenClassTasksDriver and ZenClassDriver."""
        self.assertEqual(ExportedZenClassTasksDriver, ZenClassTasksDriver)
        self.assertEqual(ExportedZenClassDriver, ZenClassTasksDriver)
        self.assertEqual(ExportedZenClassAuthError, ZenClassAuthenticationError)
        self.assertEqual(ExportedZenClassMFABlockedError, ZenClassMFABlockedError)


# =============================================================================
# 8. Zero Mock Evaluate Shims Static Verification
# =============================================================================

class TestZeroMockEvaluateShims(unittest.TestCase):
    """Static analysis test verifying zero mock evaluate shims in production drivers."""

    def test_no_mock_evaluate_shims_in_zenclass_tasks_driver(self):
        """Ensures drivers/zenclass_tasks_driver.py contains zero mock evaluate branching or shims."""
        driver_path = Path(PROJECT_ROOT) / "drivers" / "zenclass_tasks_driver.py"
        self.assertTrue(driver_path.exists(), f"File {driver_path} does not exist.")

        content = driver_path.read_text(encoding="utf-8")

        # Forbidden patterns in production code
        forbidden_patterns = [
            r"isinstance\([^,]+evaluate,\s*(?:MagicMock|Mock)\)",
            r"mock_evaluate",
            r"mockEvaluate",
            r"__mock__",
            r"unittest\.mock",
            r"from unittest\.mock import",
        ]
        for pattern in forbidden_patterns:
            matches = re.findall(pattern, content)
            self.assertEqual(
                len(matches),
                0,
                f"Forbidden mock evaluate shim pattern '{pattern}' detected in {driver_path}!"
            )


if __name__ == "__main__":
    unittest.main()
