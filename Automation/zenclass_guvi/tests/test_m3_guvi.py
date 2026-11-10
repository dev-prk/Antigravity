"""
tests/test_m3_guvi.py - Comprehensive Unit and Integration Test Suite for Milestone 3.

Validates:
- Foundational BaseDriver (drivers/base_driver.py):
  - Page property initialization, navigation, and foreground focus
  - HITL guardrail hooks and delegation
  - Resilient selector cascade (find_first_selector, safe_fill, safe_click)
  - ElementNotFoundError on missing selectors
  - Visibility checks and modal dismissals
  - Diagnostic screenshot capture and session persistence
- GuviDriver Authentication Lifecycle (drivers/guvi_driver.py):
  - Cookie authToken check with 'auth:' prefix
  - Probe navigation to CodeKata catalog without /sign-in/ redirect
  - Ensure authenticated avoids redundant login
  - Empty credential validation
  - Full login sequence: natural typing, remember me, submission, and post-login detection
  - Auto-redirect handling when already authenticated
  - Credential rejection handling (.invalid-feedback)
  - Account activation modal (#myModal) HITL interception
  - Timeout enforcement
- GuviDriver Catalog Discovery & Pending Filtering:
  - 5-column table row parsing from live DOM fixtures
  - #completed-icon_svg__a solved vs pending classification
  - Metadata extraction (title, success rate, difficulty, points)
  - Slug derivation from data-slug, link href, or title normalization
  - 9 R3 fields on every task record
  - 143-page pagination and disabled next button detection
  - Atomic bulk persistence into SQLite StateManager
- GuviDriver Problem Solving Pipeline (solve_problem):
  - Problem specification extraction (solver.extractor)
  - Algorithmic code synthesis (solver.code_generator)
  - Local subprocess sandbox pre-check (solver.test_runner)
  - Anti-cheating guardrail: local test failure halts browser submission
  - Ace Editor readiness and CDP keyboard text injection (solver.ace_adapter)
  - Run Code execution and test pill verification
  - Submit Code execution and positive 'Solved!' verification
  - StateManager 9 R3 fields update and duration recording
- GuviDriver Pipeline Orchestrator (run_pipeline):
  - End-to-end batch execution with limit enforcement
  - Single task targeting via task_id
  - Authentication failure abort
  - Summary report generation (core.reporter)
- CLI Integration & Driver Package Exports:
  - drivers/__init__.py public exports
  - main.py CLI integration for run-codekata and run-all
"""

from __future__ import annotations
import json
import os
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
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
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
from drivers import (
    BaseDriver as ExportedBaseDriver,
    GuviDriver as ExportedGuviDriver,
)

from solver.extractor import SampleCase, ProblemSpecification
from solver.code_generator import GeneratedSolution
from solver.test_runner import ValidationResult, TestCaseResult
from tests.e2e.harness.dom_fixtures import (
    GUVI_LOGIN_HTML,
    GUVI_CODEKATA_TABLE_HTML,
    GUVI_WORKSPACE_HTML,
)
from main import create_cli_parser, AutomationRunner


# =============================================================================
# 1. BaseDriver Unit Tests
# =============================================================================

class TestBaseDriver(unittest.TestCase):
    """Verifies foundational base driver methods, error handling, and helpers."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.driver = BaseDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            hitl_handler=self.mock_hitl,
            reporter=self.mock_rep,
        )

    def test_page_property_caching_and_init(self):
        """Verifies lazy retrieval and caching of active Playwright page."""
        page1 = self.driver.page
        self.assertEqual(page1, self.mock_page)
        self.mock_bm.get_page.assert_called_once()

        # Accessing second time should return cached reference without re-calling get_page
        page2 = self.driver.page
        self.assertEqual(page2, page1)
        self.assertEqual(self.mock_bm.get_page.call_count, 1)

    def test_navigate_calls_goto_and_bring_to_front(self):
        """Verifies navigation calls goto and brings page to foreground (R1)."""
        self.mock_page.url = "about:blank"
        self.driver.navigate("https://www.guvi.in/code-kata/", wait_until="domcontentloaded")

        self.mock_page.goto.assert_called_once_with(
            "https://www.guvi.in/code-kata/",
            wait_until="domcontentloaded",
            timeout=config.NAVIGATION_TIMEOUT
        )
        self.mock_page.bring_to_front.assert_called()

    def test_check_guardrails_delegates_to_hitl_handler(self):
        """Verifies guardrail inspection delegates to HitlHandler."""
        self.mock_hitl.check_and_handle_guardrails.return_value = True
        result = self.driver.check_guardrails(task_id="test-1", context_desc="Testing Context")

        self.assertTrue(result)
        self.mock_hitl.check_and_handle_guardrails.assert_called_once_with(
            self.mock_page, task_id="test-1", context_desc="Testing Context"
        )

    def test_find_first_selector_returns_first_visible(self):
        """Iterates through candidates and returns the first visible match."""
        def fake_wait(sel, state="visible", timeout=3000):
            if sel == "#candidate_two":
                return MagicMock()
            raise Exception("Not visible")

        self.mock_page.wait_for_selector.side_effect = fake_wait
        matched = self.driver.find_first_selector(["#candidate_one", "#candidate_two", "#candidate_three"])
        self.assertEqual(matched, "#candidate_two")

    def test_find_first_selector_none_found(self):
        """Returns None when no candidates match."""
        self.mock_page.wait_for_selector.side_effect = Exception("Not visible")
        matched = self.driver.find_first_selector(["#nonexistent_1", "#nonexistent_2"])
        self.assertIsNone(matched)

    def test_safe_fill_success(self):
        """Fills matching input selector and returns selector name."""
        self.mock_page.wait_for_selector.return_value = MagicMock()
        res = self.driver.safe_fill(["#email", "input#email"], "test@example.com")
        self.assertEqual(res, "#email")
        self.mock_page.fill.assert_called_once_with("#email", "test@example.com")

    def test_safe_fill_raises_element_not_found(self):
        """Raises ElementNotFoundError when none of the input selectors exist."""
        self.mock_page.wait_for_selector.side_effect = Exception("Missing")
        with self.assertRaises(ElementNotFoundError):
            self.driver.safe_fill(["#missing1", "#missing2"], "value")

    def test_safe_click_success(self):
        """Clicks matching selector and returns selector name."""
        self.mock_page.wait_for_selector.return_value = MagicMock()
        res = self.driver.safe_click(["#login-btn", "button[type='submit']"])
        self.assertEqual(res, "#login-btn")
        self.mock_page.click.assert_called_once_with("#login-btn", force=False)

    def test_safe_click_raises_element_not_found(self):
        """Raises ElementNotFoundError when target click selector is missing."""
        self.mock_page.wait_for_selector.side_effect = Exception("Missing")
        with self.assertRaises(ElementNotFoundError):
            self.driver.safe_click(["#missing-btn"])

    def test_is_visible_returns_boolean(self):
        """Returns True if visible, False on timeout without throwing."""
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.assertTrue(self.driver.is_visible("#present"))

        self.mock_page.wait_for_selector.side_effect = Exception("Timeout")
        self.assertFalse(self.driver.is_visible("#absent"))

    def test_dismiss_modals_clicks_close_buttons(self):
        """Dismisses matching popup modals and returns count dismissed."""
        btn_mock = MagicMock()
        btn_mock.is_visible.return_value = True

        def fake_qs(sel):
            if sel == "button:has-text('✕')":
                return btn_mock
            return None

        self.mock_page.query_selector.side_effect = fake_qs
        dismissed = self.driver.dismiss_modals()
        self.assertGreaterEqual(dismissed, 1)
        btn_mock.click.assert_called()

    def test_persist_session_calls_browser_manager(self):
        """Exports browser session state to disk."""
        self.driver.persist_session()
        self.mock_bm.save_storage_state.assert_called_once()

    def test_save_screenshot_calls_browser_manager(self):
        """Saves diagnostic PNG via browser manager."""
        self.driver.save_screenshot("test_diag")
        self.mock_bm.save_screenshot.assert_called_once_with(name="test_diag", page=self.mock_page)


# =============================================================================
# 2. GuviDriver Authentication Lifecycle Tests
# =============================================================================

class TestGuviAuthentication(unittest.TestCase):
    """Verifies Guvi authentication, session probing, and guardrail handling."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_page.query_selector.return_value = None
        self.mock_bm.get_page.return_value = self.mock_page

        self.mock_ctx = MagicMock()
        self.mock_bm.get_context.return_value = self.mock_ctx

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
            hitl_handler=self.mock_hitl,
            reporter=self.mock_rep,
        )

    def test_is_authenticated_with_valid_auth_cookie(self):
        """Returns True when authToken starting with 'auth:' exists in browser cookies."""
        self.mock_ctx.cookies.return_value = [
            {"name": "authToken", "value": "auth:a1b2c3d4e5f6g7h8", "domain": ".guvi.in"}
        ]
        self.assertTrue(self.driver.is_authenticated())

    def test_is_authenticated_probe_navigation_success(self):
        """Probes CodeKata URL when no cookies exist; returns True when indicators match."""
        self.mock_ctx.cookies.return_value = []
        self.mock_page.url = ""  # Initial blank state triggers probe
        self.mock_page.wait_for_selector.return_value = MagicMock()

        with patch.object(self.driver, "is_visible", return_value=True):
            self.assertTrue(self.driver.is_authenticated())
            self.mock_page.goto.assert_called()

    def test_is_authenticated_probe_redirect_to_signin_returns_false(self):
        """Returns False when probing CodeKata URL redirects to /sign-in/."""
        self.mock_ctx.cookies.return_value = []
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.side_effect = Exception("Timeout")

        self.assertFalse(self.driver.is_authenticated())

    def test_ensure_authenticated_skips_login_when_valid(self):
        """Avoids redundant login if valid session exists."""
        self.mock_ctx.cookies.return_value = [{"name": "authToken", "value": "auth:valid_token"}]
        with patch.object(self.driver, "login") as mock_login:
            result = self.driver.ensure_authenticated()
            self.assertTrue(result)
            mock_login.assert_not_called()

    def test_ensure_authenticated_triggers_login_when_invalid(self):
        """Triggers full login sequence when session is invalid."""
        self.mock_ctx.cookies.return_value = []
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.side_effect = Exception("Not found")

        with patch.object(self.driver, "login", return_value=True) as mock_login:
            result = self.driver.ensure_authenticated()
            self.assertTrue(result)
            mock_login.assert_called_once()

    def test_login_empty_credentials_raises_error(self):
        """Empty email or password raises GuviAuthenticationError."""
        with self.assertRaises(GuviAuthenticationError):
            self.driver.login(email="", password="password")

        with self.assertRaises(GuviAuthenticationError):
            self.driver.login(email="user@test.com", password="")

    def test_login_auto_redirect_when_already_authenticated(self):
        """If navigating to /sign-in/ auto-redirects away, marks session active."""
        # Initial navigation lands on dashboard instead of /sign-in/
        self.mock_page.url = "https://www.guvi.in/courses"
        result = self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertTrue(result)
        self.mock_bm.save_storage_state.assert_called()

    def test_login_success_flow(self):
        """Simulates full login sequence with form filling and post-login confirmation."""
        # Step 1: on /sign-in/
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True

        # After submission, page navigates to /code-kata/
        def fake_click(sel, **kw):
            if "login" in sel:
                self.mock_page.url = "https://www.guvi.in/code-kata/"

        self.mock_page.click.side_effect = fake_click

        result = self.driver.login(email="devsh.pareek@gmail.com", password="password")
        self.assertTrue(result)
        self.mock_page.fill.assert_called()
        self.mock_bm.save_storage_state.assert_called()

    def test_login_credential_rejection_raises_error(self):
        """Visible .invalid-feedback with error text raises GuviAuthenticationError."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()

        err_element = MagicMock()
        err_element.is_visible.return_value = True
        err_element.inner_text.return_value = "Incorrect Email or Password"

        def fake_qs(sel):
            if ".invalid-feedback" in sel:
                return err_element
            return None

        self.mock_page.query_selector.side_effect = fake_qs

        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="devsh.pareek@gmail.com", password="wrong_password")
        self.assertIn("Incorrect Email or Password", str(ctx.exception))

    def test_login_activation_modal_triggers_guardrail(self):
        """Detection of #myModal triggers HITL handler."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.mock_page.wait_for_selector.return_value = MagicMock()
        self.mock_page.is_checked.return_value = True
        self.mock_page.click.side_effect = lambda sel, **kw: setattr(self.mock_page, "url", "https://www.guvi.in/code-kata/")

        def fake_is_visible(sel, **kw):
            if "#myModal" in sel or "sendmail" in sel:
                return True
            if ".user-avatar" in sel or "table" in sel:
                return True
            return False

        with patch.object(self.driver, "is_visible", side_effect=fake_is_visible):
            self.mock_hitl.check_and_handle_guardrails.return_value = True
            res = self.driver.login(email="devsh.pareek@gmail.com", password="password")
            self.assertTrue(res)
            self.mock_hitl.check_and_handle_guardrails.assert_called()


# =============================================================================
# 3. GuviDriver Catalog Discovery & Filtering Tests
# =============================================================================

class MockRowElement:
    """Simulates Playwright ElementHandle for a single table row."""

    def __init__(self, col0_svg: str, title: str, rate: str, diff: str, pts: str, slug: str = ""):
        self.col0_svg = col0_svg
        self.title_text = title
        self.rate_text = rate
        self.diff_text = diff
        self.pts_text = pts
        self.slug = slug

    def get_attribute(self, attr: str):
        if attr == "data-slug":
            return self.slug
        return None

    def query_selector(self, sel: str):
        if "nth-child(1)" in sel:
            m = MagicMock()
            m.inner_html.return_value = self.col0_svg
            return m
        elif "nth-child(2)" in sel or "problem-title" in sel:
            m = MagicMock()
            m.inner_text.return_value = self.title_text
            return m
        elif "nth-child(3)" in sel or "success-rate" in sel:
            m = MagicMock()
            m.inner_text.return_value = self.rate_text
            return m
        elif "nth-child(4)" in sel or "difficulty" in sel:
            m = MagicMock()
            m.inner_text.return_value = self.diff_text
            return m
        elif "nth-child(5)" in sel or "points" in sel:
            m = MagicMock()
            m.inner_text.return_value = self.pts_text
            return m
        elif "a[href*='/code-kata/']" in sel:
            m = MagicMock()
            m.get_attribute.return_value = f"/code-kata/{self.slug}/"
            return m
        return None


class TestGuviCatalogDiscovery(unittest.TestCase):
    """Verifies 143-page table discovery, SVG completed status, and SQLite batch recording."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        # Use in-memory SQLite StateManager for genuine atomic transactions
        self.state_manager = StateManager(":memory:")

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.state_manager,
        )

    def tearDown(self):
        self.state_manager.close()

    def test_parse_current_table_page_classifies_solved_and_pending(self):
        """Parses rows and verifies #completed-icon_svg__a filtering."""
        # 5 simulated problem rows matching GUVI_CODEKATA_TABLE_HTML fixture
        rows = [
            MockRowElement(
                col0_svg='<svg><g clip-path="url(#completed-icon_svg__a)"><path fill="#0DBA4B"/></g></svg>',
                title="1. Odd or Even Sum",
                rate="73.97%",
                diff="Easy",
                pts="30",
                slug="odd-or-even-sum"
            ),
            MockRowElement(
                col0_svg='<svg><g></g></svg>',
                title="2. Reverse a String",
                rate="68.20%",
                diff="Easy",
                pts="30",
                slug="reverse-a-string"
            ),
            MockRowElement(
                col0_svg='<svg><g></g></svg>',
                title="3. Sum of Array Elements",
                rate="81.12%",
                diff="Easy",
                pts="20",
                slug="sum-of-array"
            ),
            MockRowElement(
                col0_svg='<svg><g></g></svg>',
                title="4. Palindrome Checker",
                rate="55.40%",
                diff="Medium",
                pts="40",
                slug="palindrome-check"
            ),
            MockRowElement(
                col0_svg='<svg><g clip-path="url(#completed-icon_svg__a)"><path fill="#0DBA4B"/></g></svg>',
                title="5. Count Prime Numbers",
                rate="42.80%",
                diff="Hard",
                pts="50",
                slug="prime-numbers-count"
            ),
        ]
        self.mock_page.query_selector_all.return_value = rows

        tasks, pending = self.driver._parse_current_table_page(page_num=1)

        self.assertEqual(len(tasks), 5)
        self.assertEqual(len(pending), 3)

        # Check pending slugs
        self.assertIn("reverse-a-string", pending)
        self.assertIn("sum-of-array", pending)
        self.assertIn("palindrome-check", pending)
        self.assertNotIn("odd-or-even-sum", pending)
        self.assertNotIn("prime-numbers-count", pending)

        # Check 9 R3 fields on solved problem
        solved_task = next(t for t in tasks if t["task_id"] == "guvi-odd-or-even-sum")
        self.assertEqual(solved_task["platform"], "guvi")
        self.assertEqual(solved_task["task_category"], "CodeKata")
        self.assertEqual(solved_task["status"], TaskStatus.COMPLETED.value)
        self.assertEqual(solved_task["result"], TaskResult.SOLVED.value)
        self.assertEqual(solved_task["attempt_count"], 1)
        self.assertEqual(solved_task["next_action"], "NONE")
        self.assertEqual(solved_task["metadata"]["points"], "30")
        self.assertEqual(solved_task["metadata"]["difficulty"], "Easy")

        # Check 9 R3 fields on pending problem
        pending_task = next(t for t in tasks if t["task_id"] == "guvi-reverse-a-string")
        self.assertEqual(pending_task["status"], TaskStatus.DISCOVERED.value)
        self.assertEqual(pending_task["result"], TaskResult.UNATTEMPTED.value)
        self.assertEqual(pending_task["attempt_count"], 0)
        self.assertEqual(pending_task["next_action"], "SOLVE_AND_SUBMIT")

    def test_discover_catalog_persists_to_sqlite(self):
        """Crawls catalog and verifies atomic batch recording into SQLite database."""
        rows_page_1 = [
            MockRowElement(
                col0_svg='<svg><g></g></svg>',
                title="1. Reverse a String",
                rate="68.20%",
                diff="Easy",
                pts="30",
                slug="reverse-a-string"
            ),
            MockRowElement(
                col0_svg='<svg><g clip-path="url(#completed-icon_svg__a)"><path fill="#0DBA4B"/></g></svg>',
                title="2. Odd or Even Sum",
                rate="73.97%",
                diff="Easy",
                pts="30",
                slug="odd-or-even-sum"
            ),
        ]
        self.mock_page.query_selector_all.return_value = rows_page_1

        # Simulate last page (next button disabled)
        next_btn = MagicMock()
        next_btn.get_attribute.return_value = "disabled"
        self.mock_page.query_selector.return_value = next_btn

        pending = self.driver.discover_catalog(max_pages=1)
        self.assertEqual(pending, ["reverse-a-string"])

        # Verify SQLite persistent state
        rec_pending = self.state_manager.get_task("guvi-reverse-a-string")
        self.assertIsNotNone(rec_pending)
        self.assertEqual(rec_pending.status, TaskStatus.DISCOVERED.value)
        self.assertEqual(rec_pending.platform, "guvi")

        rec_solved = self.state_manager.get_task("guvi-odd-or-even-sum")
        self.assertIsNotNone(rec_solved)
        self.assertEqual(rec_solved.status, TaskStatus.COMPLETED.value)
        self.assertEqual(rec_solved.result, TaskResult.SOLVED.value)


# =============================================================================
# 4. GuviDriver Problem Solving Pipeline Tests (`solve_problem`)
# =============================================================================

class TestGuviWorkspacePipeline(unittest.TestCase):
    """Verifies single problem solving, sandbox pre-checks, Ace injection, Run, and Submit."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.state_manager = StateManager(":memory:")
        self.mock_hitl = MagicMock(spec=HitlHandler)

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.state_manager,
            hitl_handler=self.mock_hitl,
        )

    def tearDown(self):
        self.state_manager.close()

    @patch("drivers.guvi_driver.extract_problem_spec")
    @patch("drivers.guvi_driver.generate_solution")
    @patch("drivers.guvi_driver.test_solution")
    @patch("drivers.guvi_driver.wait_for_editor")
    @patch("drivers.guvi_driver.inject_code")
    def test_solve_problem_successful_pipeline(
        self,
        mock_inject,
        mock_wait_editor,
        mock_test_sol,
        mock_gen_sol,
        mock_extract_spec,
    ):
        """End-to-end solve pipeline: extract -> synthesize -> sandbox -> inject -> run -> submit -> verify."""
        spec = ProblemSpecification(
            title="Odd or Even Sum",
            description="Add two numbers and print even or odd",
            sample_cases=[SampleCase(input_text="9 2\n", expected_output="odd\n")]
        )
        mock_extract_spec.return_value = spec

        sol = GeneratedSolution(
            code="n, m = map(int, input().split())\nprint('odd' if (n + m) % 2 else 'even')\n",
            category="Math",
            confidence=1.0,
            explanation="Odd/Even sum"
        )
        mock_gen_sol.return_value = sol

        # Sandbox passes
        mock_test_sol.return_value = ValidationResult(
            all_passed=True,
            passed_count=1,
            total_count=1,
            results=[TestCaseResult(
                passed=True,
                input_data="9 2\n",
                expected_output="odd\n",
                actual_output="odd\n",
                error_message="",
                duration=0.01,
            )]
        )

        # Ace Editor ready & injected
        mock_wait_editor.return_value = True
        mock_inject.return_value = True

        # DOM: Solved! status and success modal
        qs_status = MagicMock()
        qs_status.inner_text.return_value = "Solved!"

        modal_elem = MagicMock()
        modal_elem.is_visible.return_value = True
        modal_elem.inner_text.return_value = "Congratulations! You have earned +30 Geekoins"

        def fake_qs(sel):
            if "question-status" in sel:
                return qs_status
            if "success_modal" in sel or "Geekoins" in sel:
                return modal_elem
            return MagicMock()

        self.mock_page.query_selector.side_effect = fake_qs
        self.mock_page.wait_for_selector.return_value = MagicMock()

        result = self.driver.solve_problem("odd-or-even-sum")

        self.assertTrue(result["success"])
        self.assertEqual(result["task_id"], "guvi-odd-or-even-sum")
        self.assertEqual(result["points"], 30)

        # Verify SQLite StateManager updated with 9 R3 fields
        task = self.state_manager.get_task("guvi-odd-or-even-sum")
        self.assertIsNotNone(task)
        self.assertEqual(task.status, TaskStatus.COMPLETED.value)
        self.assertEqual(task.result, TaskResult.PASSED.value)
        self.assertIsNone(task.failure_reason)
        self.assertEqual(task.next_action, "NONE")
        self.assertEqual(task.attempt_count, 1)
        self.assertEqual(task.metadata["points_earned"], 30)

    @patch("drivers.guvi_driver.extract_problem_spec")
    @patch("drivers.guvi_driver.generate_solution")
    @patch("drivers.guvi_driver.test_solution")
    @patch("drivers.guvi_driver.inject_code")
    def test_solve_problem_local_sandbox_failure_halts_submission(
        self,
        mock_inject,
        mock_test_sol,
        mock_gen_sol,
        mock_extract_spec,
    ):
        """Requirement R2 Anti-Cheating: Subprocess sandbox failure immediately halts platform submission."""
        spec = ProblemSpecification(
            title="Complex Algorithmic Task",
            description="Hard problem",
            sample_cases=[SampleCase(input_text="100\n", expected_output="42\n")]
        )
        mock_extract_spec.return_value = spec
        mock_gen_sol.return_value = GeneratedSolution(
            code="print(0)", category="Math", confidence=0.5, explanation="Stub"
        )

        # Sandbox fails!
        mock_test_sol.return_value = ValidationResult(
            all_passed=False,
            passed_count=0,
            total_count=1,
            results=[TestCaseResult(
                passed=False,
                input_data="100\n",
                expected_output="42\n",
                actual_output="0",
                error_message="Output mismatch: expected '42', got '0'",
                duration=0.01,
            )]
        )

        result = self.driver.solve_problem("complex-task")

        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "LOCAL_SANDBOX")
        self.assertIn("Output mismatch", result["error"])

        # Editor injection and click submit MUST NOT be executed
        mock_inject.assert_not_called()
        self.mock_page.click.assert_not_called()

        # StateManager updated to FAILED / TEST_FAILED
        task = self.state_manager.get_task("guvi-complex-task")
        self.assertIsNotNone(task)
        self.assertEqual(task.status, TaskStatus.FAILED.value)
        self.assertEqual(task.result, TaskResult.TEST_FAILED.value)
        self.assertIn("Output mismatch", task.failure_reason)
        self.assertEqual(task.next_action, "REVISE_SOLVER_TEMPLATE")

    @patch("drivers.guvi_driver.extract_problem_spec")
    @patch("drivers.guvi_driver.generate_solution")
    @patch("drivers.guvi_driver.test_solution")
    @patch("drivers.guvi_driver.wait_for_editor")
    def test_solve_problem_ace_editor_failure(
        self,
        mock_wait_editor,
        mock_test_sol,
        mock_gen_sol,
        mock_extract_spec,
    ):
        """Ace Editor readiness failure records error and halts execution."""
        mock_extract_spec.return_value = ProblemSpecification(title="P", description="D")
        mock_gen_sol.return_value = GeneratedSolution(
            code="pass", category="General", confidence=1.0, explanation="No-op"
        )
        mock_test_sol.return_value = ValidationResult(all_passed=True, passed_count=1, total_count=1, results=[])

        # Ace Editor fails to reach ready state
        mock_wait_editor.return_value = False

        res = self.driver.solve_problem("failing-editor")
        self.assertFalse(res["success"])
        self.assertEqual(res["stage"], "ACE_INJECTION")

        task = self.state_manager.get_task("guvi-failing-editor")
        self.assertEqual(task.status, TaskStatus.FAILED.value)
        self.assertEqual(task.result, TaskResult.SUBMISSION_FAILED.value)


# =============================================================================
# 5. GuviDriver Pipeline Orchestrator Tests (`run_pipeline`)
# =============================================================================

class TestGuviPipelineOrchestrator(unittest.TestCase):
    """Verifies end-to-end orchestration, single task targeting, and report generation."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_page.is_closed.return_value = False
        self.mock_bm.get_page.return_value = self.mock_page

        self.state_manager = StateManager(":memory:")
        self.mock_rep = MagicMock(spec=SummaryReporter)
        self.mock_rep.generate_all_reports.return_value = ("/reports/SUMMARY_REPORT.md", "/reports/summary.json")

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.state_manager,
            reporter=self.mock_rep,
        )

    def tearDown(self):
        self.state_manager.close()

    @patch.object(GuviDriver, "ensure_authenticated", return_value=True)
    @patch.object(GuviDriver, "solve_problem")
    def test_run_pipeline_single_task_targeting(self, mock_solve, mock_auth):
        """Single problem targeting via task_id parameter."""
        mock_solve.return_value = {"success": True, "task_id": "guvi-target-slug"}

        res = self.driver.run_pipeline(task_id="guvi-target-slug")

        self.assertTrue(res["success"])
        self.assertEqual(res["total_attempted"], 1)
        self.assertEqual(res["completed"], 1)
        mock_solve.assert_called_once_with("target-slug")
        self.mock_rep.generate_all_reports.assert_called_once()

    @patch.object(GuviDriver, "ensure_authenticated", return_value=True)
    @patch.object(GuviDriver, "discover_catalog")
    @patch.object(GuviDriver, "solve_problem")
    def test_run_pipeline_batch_with_limit(self, mock_solve, mock_discover, mock_auth):
        """Batch execution discovering catalog and solving up to limit."""
        mock_discover.return_value = ["slug-1", "slug-2", "slug-3", "slug-4"]
        mock_solve.side_effect = [
            {"success": True, "slug": "slug-1"},
            {"success": True, "slug": "slug-2"},
        ]

        res = self.driver.run_pipeline(limit=2)

        self.assertTrue(res["success"])
        self.assertEqual(res["total_attempted"], 2)
        self.assertEqual(res["completed"], 2)
        self.assertEqual(mock_solve.call_count, 2)
        self.mock_rep.generate_all_reports.assert_called()

    @patch.object(GuviDriver, "ensure_authenticated", return_value=False)
    def test_run_pipeline_aborts_on_auth_failure(self, mock_auth):
        """Pipeline immediately aborts if authentication cannot be established."""
        res = self.driver.run_pipeline(limit=5)
        self.assertFalse(res["success"])
        self.assertEqual(res["reason"], "AUTH_FAILED")


# =============================================================================
# 6. Package Exports & CLI Integration Tests
# =============================================================================

class TestGuviPackageExportsAndCLI(unittest.TestCase):
    """Verifies clean package exports and CLI subcommand integration."""

    def test_drivers_init_exports(self):
        """Verifies drivers/__init__.py exports BaseDriver, GuviDriver, and exceptions."""
        import drivers
        self.assertTrue(hasattr(drivers, "BaseDriver"))
        self.assertTrue(hasattr(drivers, "GuviDriver"))
        self.assertTrue(hasattr(drivers, "DriverError"))
        self.assertTrue(hasattr(drivers, "AuthenticationError"))
        self.assertTrue(hasattr(drivers, "GuviAuthenticationError"))
        self.assertIs(drivers.BaseDriver, BaseDriver)
        self.assertIs(drivers.GuviDriver, GuviDriver)

    @patch("drivers.guvi_driver.GuviDriver.run_pipeline")
    def test_main_cli_wires_run_codekata(self, mock_run_pipeline):
        """Verifies 'run-codekata' command properly invokes GuviDriver.run_pipeline()."""
        parser = create_cli_parser()
        args = parser.parse_args(["--limit", "3", "run-codekata", "--category", "Basics"])

        runner = AutomationRunner(args)
        runner.initialize_services = MagicMock()
        runner.initialize_browser = MagicMock()
        runner.cleanup = MagicMock()
        runner.state_manager = MagicMock(spec=StateManager)
        runner.reporter = MagicMock(spec=SummaryReporter)

        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)
        mock_run_pipeline.assert_called_once_with(limit=3, category="Basics", task_id=None)

    @patch("drivers.guvi_driver.GuviDriver.run_pipeline")
    def test_main_cli_wires_run_all(self, mock_run_pipeline):
        """Verifies 'run-all' command properly invokes GuviDriver.run_pipeline()."""
        parser = create_cli_parser()
        args = parser.parse_args(["--limit", "5", "run-all"])

        runner = AutomationRunner(args)
        runner.initialize_services = MagicMock()
        runner.initialize_browser = MagicMock()
        runner.cleanup = MagicMock()
        runner.state_manager = MagicMock(spec=StateManager)
        runner.reporter = MagicMock(spec=SummaryReporter)

        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)
        mock_run_pipeline.assert_called_once_with(limit=5)


if __name__ == "__main__":
    unittest.main()
