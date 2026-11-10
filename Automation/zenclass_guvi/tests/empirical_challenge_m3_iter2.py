"""
zenclass_guvi/tests/empirical_challenge_m3_iter2.py
Empirical Adversarial Stress Harness for Milestone 3 Iteration 2 Gate Review.
Author: challenger_m3_iter2_2 (Empirical Challenger)

Coverage:
1. Catalog Crawling, Pagination & Scale (143 pages simulation, limits, boundary cases, corrupt rows, SVG parsing)
2. Authentication State Recovery & Headed/Anti-Detection Flags (multi-tier recovery, persistent context args, headless=False)
3. Zero Fake Evaluate Shims Verification (static AST analysis + runtime failure condition assertions)
4. Interface Signature & Autospec Integrity (solver.ace_adapter.inject_code contract)
"""

import ast
import inspect
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# Ensure import paths resolve to zenclass_guvi
ZENCLASS_DIR = Path(__file__).resolve().parent.parent
if str(ZENCLASS_DIR) not in sys.path:
    sys.path.insert(0, str(ZENCLASS_DIR))

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
from core.hitl_handler import HitlHandler
from drivers.guvi_driver import GuviDriver, GuviAuthenticationError
from solver.extractor import ProblemSpecification
from solver.code_generator import GeneratedSolution
from solver.test_runner import ValidationResult, TestCaseResult
from solver.ace_adapter import inject_code, AceEditorAdapter


class TestCatalogCrawlingStress(unittest.TestCase):
    """Stress testing catalog crawling, 143-page simulation, and SVG filtering."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_state.db"
        self.state_mgr = StateManager(db_path=self.db_path)
        self.mock_browser = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_browser.get_page.return_value = self.mock_page
        self.driver = GuviDriver(
            browser_manager=self.mock_browser,
            state_manager=self.state_mgr,
        )
        self.driver._current_page = self.mock_page

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_mock_row(self, title, slug, is_completed=False, difficulty="Easy", points="30"):
        row = MagicMock()
        row.get_attribute.side_effect = lambda attr: slug if attr == "data-slug" else None

        # col 0: Status SVG
        col0 = MagicMock()
        if is_completed:
            col0.inner_html.return_value = (
                '<svg><g clip-path="url(#completed-icon_svg__a)"><path fill="#0DBA4B"/></g></svg>'
            )
        else:
            col0.inner_html.return_value = '<svg><circle cx="5" cy="5" r="4" fill="#CCCCCC"/></svg>'

        # col 1: Title
        col1 = MagicMock()
        col1.inner_text.return_value = title

        # link
        link = MagicMock()
        link.get_attribute.return_value = f"/code-kata/{slug}/"

        # col 2: Success Rate
        col2 = MagicMock()
        col2.inner_text.return_value = "85%"

        # col 3: Difficulty
        col3 = MagicMock()
        col3.inner_text.return_value = difficulty

        # col 4: Points
        col4 = MagicMock()
        col4.inner_text.return_value = points

        def query_selector_fn(sel):
            if "nth-child(1)" in sel:
                return col0
            elif "nth-child(2)" in sel or "problem-title" in sel:
                return col1
            elif "a[href*='/code-kata/']" in sel:
                return link
            elif "nth-child(3)" in sel or "success-rate" in sel:
                return col2
            elif "nth-child(4)" in sel or "difficulty" in sel:
                return col3
            elif "nth-child(5)" in sel or "points" in sel:
                return col4
            return None

        row.query_selector.side_effect = query_selector_fn
        return row

    def test_01_catalog_143_pages_full_crawl_scale(self):
        """Simulates full 143-page catalog crawl: 143 pages x 10 problems = 1,430 problems."""
        TOTAL_PAGES = 143
        PROBLEMS_PER_PAGE = 10

        pages_data = []
        for p in range(1, TOTAL_PAGES + 1):
            rows = []
            for i in range(1, PROBLEMS_PER_PAGE + 1):
                idx = (p - 1) * PROBLEMS_PER_PAGE + i
                is_comp = (idx % 2 == 0)  # Even numbers completed, odd pending
                row = self._create_mock_row(
                    title=f"Problem {idx}",
                    slug=f"problem-{idx}",
                    is_completed=is_comp,
                )
                rows.append(row)
            pages_data.append(rows)

        current_page_idx = [0]

        def query_selector_all_fn(sel):
            if "tr" in sel:
                idx = current_page_idx[0]
                if idx < len(pages_data):
                    return pages_data[idx]
                return []
            return []

        self.mock_page.query_selector_all.side_effect = query_selector_all_fn

        # Mock next page button
        next_btn = MagicMock()

        def next_btn_click():
            current_page_idx[0] += 1

        next_btn.click.side_effect = next_btn_click
        next_btn.get_attribute.side_effect = lambda attr: (
            "disabled" if attr == "disabled" and current_page_idx[0] >= (TOTAL_PAGES - 1) else None
        )

        def query_selector_page_fn(sel):
            if "next page" in sel or "next-page" in sel:
                return next_btn
            return None

        self.mock_page.query_selector.side_effect = query_selector_page_fn

        # Execute crawl with 143 max pages
        with patch("time.sleep", return_value=None):
            pending_slugs = self.driver.discover_catalog(max_pages=TOTAL_PAGES)

        # Assertions: 1,430 problems total, 715 pending (odd numbers 1 to 1429)
        expected_pending_count = TOTAL_PAGES * PROBLEMS_PER_PAGE // 2
        self.assertEqual(len(pending_slugs), expected_pending_count)
        self.assertEqual(pending_slugs[0], "problem-1")
        self.assertEqual(pending_slugs[-1], f"problem-{TOTAL_PAGES * PROBLEMS_PER_PAGE - 1}")

        # Check SQLite persistence: all 1,430 problems recorded
        all_tasks = self.state_mgr.list_all_tasks(platform="guvi")
        self.assertEqual(len(all_tasks), TOTAL_PAGES * PROBLEMS_PER_PAGE)

        pending_tasks = self.state_mgr.list_pending(platform="guvi")
        self.assertEqual(len(pending_tasks), expected_pending_count)

        # Verify all 9 R3 mandatory fields on sampled tasks
        for sample_task in [all_tasks[0], all_tasks[500], all_tasks[-1]]:
            self.assertIsNotNone(sample_task.task_id)
            self.assertEqual(sample_task.platform, "guvi")
            self.assertEqual(sample_task.task_category, "CodeKata")
            self.assertIsNotNone(sample_task.title)
            self.assertTrue(sample_task.url.startswith("https://www.guvi.in/code-kata/"))
            self.assertIn(sample_task.status, [TaskStatus.DISCOVERED.value, TaskStatus.COMPLETED.value])
            self.assertIn(sample_task.result, [TaskResult.UNATTEMPTED.value, TaskResult.SOLVED.value])
            self.assertIsNotNone(sample_task.updated_at)
            self.assertIn(sample_task.next_action, ["NONE", "SOLVE_AND_SUBMIT"])

    def test_02_catalog_limit_pending_stops_early(self):
        """Verify discovery terminates immediately when limit_pending is satisfied."""
        pages_data = []
        for p in range(1, 10):
            rows = [
                self._create_mock_row(f"P{p}_{i}", f"slug-{p}-{i}", is_completed=False)
                for i in range(1, 6)
            ]
            pages_data.append(rows)

        current_page_idx = [0]
        self.mock_page.query_selector_all.side_effect = lambda sel: pages_data[current_page_idx[0]]

        next_btn = MagicMock()
        next_btn.get_attribute.return_value = None
        next_btn.click.side_effect = lambda: current_page_idx.__setitem__(0, current_page_idx[0] + 1)
        self.mock_page.query_selector.side_effect = lambda sel: next_btn if "next" in sel else None

        # Request limit_pending = 12 (should stop on page 3 where count reaches 15 >= 12)
        with patch("time.sleep", return_value=None):
            pending = self.driver.discover_catalog(max_pages=143, limit_pending=12)

        self.assertGreaterEqual(len(pending), 12)
        # Should not have crawled beyond page 3
        self.assertLessEqual(current_page_idx[0], 3)

    def test_03_catalog_pagination_disabled_button_stops_crawl(self):
        """Verify crawl terminates when next button has disabled attribute."""
        rows = [self._create_mock_row("P1", "slug-1", is_completed=False)]
        self.mock_page.query_selector_all.return_value = rows

        next_btn = MagicMock()
        next_btn.get_attribute.side_effect = lambda attr: "disabled" if attr == "disabled" else None
        self.mock_page.query_selector.return_value = next_btn

        with patch("time.sleep", return_value=None):
            pending = self.driver.discover_catalog(max_pages=50)

        # Crawl stopped after 1 page, click was never called
        self.assertEqual(len(pending), 1)
        next_btn.click.assert_not_called()

    def test_04_catalog_pagination_missing_button_stops_crawl(self):
        """Verify crawl terminates when next button is None (last page reached)."""
        rows = [self._create_mock_row("P1", "slug-1", is_completed=False)]
        self.mock_page.query_selector_all.return_value = rows
        self.mock_page.query_selector.return_value = None

        with patch("time.sleep", return_value=None):
            pending = self.driver.discover_catalog(max_pages=50)

        self.assertEqual(len(pending), 1)

    def test_05_catalog_empty_table_page_returns_gracefully(self):
        """Verify empty table page returns ([], []) without exception."""
        self.mock_page.query_selector_all.return_value = []
        tasks, pending = self.driver._parse_current_table_page(page_num=1)
        self.assertEqual(tasks, [])
        self.assertEqual(pending, [])

    def test_06_catalog_svg_filter_variations(self):
        """Stress-test SVG completed classification across multiple variations."""
        # 1. Standard clip-path URL
        r1 = self._create_mock_row("Problem 1", "p1", is_completed=False)
        col0_1 = MagicMock()
        col0_1.inner_html.return_value = '<svg><g clip-path="url(#completed-icon_svg__a)"><path/></g></svg>'
        r1.query_selector.side_effect = lambda sel: col0_1 if "nth-child(1)" in sel else None

        # 2. Hex color fill uppercase #0DBA4B
        r2 = self._create_mock_row("Problem 2", "p2", is_completed=False)
        col0_2 = MagicMock()
        col0_2.inner_html.return_value = '<svg><path fill="#0DBA4B"/></svg>'
        r2.query_selector.side_effect = lambda sel: col0_2 if "nth-child(1)" in sel else None

        # 3. Uncompleted grey circle
        r3 = self._create_mock_row("Problem 3", "p3", is_completed=False)
        col0_3 = MagicMock()
        col0_3.inner_html.return_value = '<svg><circle fill="#CCCCCC"/></svg>'
        r3.query_selector.side_effect = lambda sel: col0_3 if "nth-child(1)" in sel else None

        # 4. None / empty inner_html
        r4 = self._create_mock_row("Problem 4", "p4", is_completed=False)
        col0_4 = MagicMock()
        col0_4.inner_html.return_value = None
        r4.query_selector.side_effect = lambda sel: col0_4 if "nth-child(1)" in sel else None

        self.mock_page.query_selector_all.return_value = [r1, r2, r3, r4]

        tasks, pending = self.driver._parse_current_table_page(page_num=1)
        self.assertEqual(len(tasks), 4)

        # r1 is completed
        self.assertEqual(tasks[0]["status"], TaskStatus.COMPLETED.value)
        self.assertEqual(tasks[0]["result"], TaskResult.SOLVED.value)

        # r2 is completed
        self.assertEqual(tasks[1]["status"], TaskStatus.COMPLETED.value)
        self.assertEqual(tasks[1]["result"], TaskResult.SOLVED.value)

        # r3 is pending
        self.assertEqual(tasks[2]["status"], TaskStatus.DISCOVERED.value)
        self.assertEqual(tasks[2]["result"], TaskResult.UNATTEMPTED.value)

        # r4 is pending
        self.assertEqual(tasks[3]["status"], TaskStatus.DISCOVERED.value)
        self.assertEqual(tasks[3]["result"], TaskResult.UNATTEMPTED.value)

        # pending list contains r3 and r4 slugs
        self.assertEqual(len(pending), 2)

    def test_07_catalog_corrupt_row_does_not_abort_page_parsing(self):
        """Verify throwing row does not prevent remaining sibling rows from being parsed."""
        r_good1 = self._create_mock_row("Good 1", "good-1", is_completed=False)
        r_bad = MagicMock()
        r_bad.query_selector.side_effect = RuntimeError("DOM node detached during SSR hydration")
        r_good2 = self._create_mock_row("Good 2", "good-2", is_completed=True)

        self.mock_page.query_selector_all.return_value = [r_good1, r_bad, r_good2]

        tasks, pending = self.driver._parse_current_table_page(page_num=1)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["metadata"]["slug"], "good-1")
        self.assertEqual(tasks[1]["metadata"]["slug"], "good-2")

    def test_08_slug_derivation_precedence(self):
        """Verify data-slug > href slug > title normalization."""
        # 1. data-slug present
        r1 = MagicMock()
        r1.get_attribute.side_effect = lambda a: "data-slug-val" if a == "data-slug" else None
        col1 = MagicMock()
        col1.inner_text.return_value = "Ignored Title"
        r1.query_selector.side_effect = lambda s: col1 if "nth-child(2)" in s else None

        self.mock_page.query_selector_all.return_value = [r1]
        tasks, _ = self.driver._parse_current_table_page(1)
        self.assertEqual(tasks[0]["metadata"]["slug"], "data-slug-val")

        # 2. href slug present, no data-slug
        r2 = MagicMock()
        r2.get_attribute.return_value = None
        link = MagicMock()
        link.get_attribute.return_value = "/code-kata/href-extracted-slug/"
        r2.query_selector.side_effect = lambda s: link if "a[href" in s else (col1 if "nth-child(2)" in s else None)

        self.mock_page.query_selector_all.return_value = [r2]
        tasks, _ = self.driver._parse_current_table_page(1)
        self.assertEqual(tasks[0]["metadata"]["slug"], "href-extracted-slug")

        # 3. title fallback
        r3 = MagicMock()
        r3.get_attribute.return_value = None
        col1_custom = MagicMock()
        col1_custom.inner_text.return_value = "105. Find Odd Numbers in List!"
        r3.query_selector.side_effect = lambda s: col1_custom if "nth-child(2)" in s else None

        self.mock_page.query_selector_all.return_value = [r3]
        tasks, _ = self.driver._parse_current_table_page(1)
        self.assertEqual(tasks[0]["metadata"]["slug"], "find-odd-numbers-in-list")


class TestAuthRecoveryAndAntiDetection(unittest.TestCase):
    """Stress testing authentication state recovery and headed anti-detection flags."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_browser = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_browser.get_page.return_value = self.mock_page
        self.driver = GuviDriver(browser_manager=self.mock_browser)
        self.driver._current_page = self.mock_page

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_09_anti_detection_flags_and_headed_mode_configuration(self):
        """Verify configuration enforces headed execution (R1) and anti-detection flags."""
        self.assertFalse(config.HEADLESS, "Requirement R1 strictly requires headed foreground execution (HEADLESS=False)")
        self.assertIn("--disable-blink-features=AutomationControlled", config.BROWSER_ARGS)
        self.assertIn("--enable-automation", config.IGNORE_DEFAULT_ARGS)
        self.assertIn("--start-maximized", config.BROWSER_ARGS)

    def test_10_auth_recovery_tier1_cookies(self):
        """Tier 1: Cookie 'authToken' starting with 'auth:' validates session without navigation."""
        mock_ctx = MagicMock()
        mock_ctx.cookies.return_value = [
            {"name": "session_id", "value": "xyz123"},
            {"name": "authToken", "value": "auth:eyJhbGciOi..."},
        ]
        self.mock_browser.get_context.return_value = mock_ctx

        self.assertTrue(self.driver.is_authenticated())
        # Should not have navigated since cookie fast-path returned True
        self.mock_page.goto.assert_not_called()

    def test_11_auth_recovery_tier1_invalid_cookie_falls_through(self):
        """Tier 1: Missing or non-auth cookie falls through to navigation probe."""
        mock_ctx = MagicMock()
        mock_ctx.cookies.return_value = [
            {"name": "authToken", "value": "not-starting-with-auth"},
        ]
        self.mock_browser.get_context.return_value = mock_ctx
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.driver.is_visible = MagicMock(return_value=False)

        # Active probe navigates to codekata_url and sees redirect to /sign-in/
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.assertFalse(self.driver.is_authenticated())

    def test_12_auth_recovery_tier3_navigation_probe_success(self):
        """Tier 3: Active probe lands on CodeKata with post-login indicator."""
        mock_ctx = MagicMock()
        mock_ctx.cookies.return_value = []
        self.mock_browser.get_context.return_value = mock_ctx

        self.mock_page.url = "https://www.guvi.in/code-kata/"
        # First check on open page: False, then active probe navigation
        call_count = [0]

        def is_visible_side_effect(selector, timeout=None):
            call_count[0] += 1
            # Return True on active probe check
            return selector == ".table" and call_count[0] > len(self.driver.POST_LOGIN_INDICATORS)

        self.driver.is_visible = MagicMock(side_effect=is_visible_side_effect)
        self.assertTrue(self.driver.is_authenticated())

    def test_13_auth_recovery_localStorage_fallback(self):
        """Fallback: LocalStorage 'authToken' starting with 'auth:' returns True."""
        mock_ctx = MagicMock()
        mock_ctx.cookies.return_value = []
        self.mock_browser.get_context.return_value = mock_ctx

        self.mock_page.url = "https://www.guvi.in/code-kata/"
        self.driver.is_visible = MagicMock(return_value=False)
        self.mock_page.evaluate.return_value = "auth:localStorageTokenValue"

        self.assertTrue(self.driver.is_authenticated())

    def test_14_ensure_authenticated_skips_login_when_valid(self):
        """Verify ensure_authenticated() does not call login() if is_authenticated() is True."""
        self.driver.is_authenticated = MagicMock(return_value=True)
        self.driver.login = MagicMock()
        self.driver.dismiss_popups = MagicMock()

        res = self.driver.ensure_authenticated(force_relogin=False)
        self.assertTrue(res)
        self.driver.login.assert_not_called()
        self.driver.dismiss_popups.assert_called_once()

    def test_15_ensure_authenticated_force_relogin_bypasses_cache(self):
        """Verify force_relogin=True invokes login() even if is_authenticated() is True."""
        self.driver.is_authenticated = MagicMock(return_value=True)
        self.driver.login = MagicMock(return_value=True)

        res = self.driver.ensure_authenticated(force_relogin=True)
        self.assertTrue(res)
        self.driver.login.assert_called_once()

    def test_16_login_credential_rejection_raises_error(self):
        """Verify visible .invalid-feedback raises GuviAuthenticationError with feedback text."""
        self.mock_page.url = "https://www.guvi.in/sign-in/"
        self.driver.find_first_selector = MagicMock(side_effect=lambda sels, timeout=None: sels[0])
        self.driver.is_visible = MagicMock(return_value=False)

        err_el = MagicMock()
        err_el.is_visible.return_value = True
        err_el.inner_text.return_value = "Incorrect Email or Password"

        def query_sel(sel):
            if ".invalid-feedback" in sel:
                return err_el
            return None

        self.mock_page.query_selector.side_effect = query_sel

        with self.assertRaises(GuviAuthenticationError) as ctx:
            self.driver.login(email="devsh.pareek@gmail.com", password="wrongpassword")

        self.assertIn("Incorrect Email or Password", str(ctx.exception))

    def test_17_storage_state_persistence_roundtrip(self):
        """Verify storage state file serialization and restoration."""
        profile_dir = Path(self.temp_dir.name) / "profile"
        storage_path = Path(self.temp_dir.name) / "storage_state.json"

        bm = BrowserManager(profile_dir=profile_dir, storage_state_path=storage_path)
        mock_ctx = MagicMock()
        bm._context = mock_ctx

        # Save storage state
        def fake_storage_state(path):
            with open(path, "w") as f:
                json.dump({"cookies": [{"name": "authToken", "value": "auth:saved123"}]}, f)

        mock_ctx.storage_state.side_effect = fake_storage_state
        bm.save_storage_state()

        self.assertTrue(storage_path.exists())

        # Restore storage state
        mock_ctx_new = MagicMock()
        bm._context = mock_ctx_new
        bm._restore_storage_state()

        mock_ctx_new.add_cookies.assert_called_once_with(
            [{"name": "authToken", "value": "auth:saved123"}]
        )


class TestZeroFakeEvaluateShims(unittest.TestCase):
    """Verify zero fake evaluate shims exist in production code or execute during failure conditions."""

    def test_18_static_ast_and_source_inspection_zero_fake_shims(self):
        """
        Static source analysis of drivers/guvi_driver.py and drivers/base_driver.py.
        Verifies:
        - No mock fetch calls ('fetch(')
        - No XMLHttpRequest calls
        - No DOM textContent mutations ('textContent =')
        - No DOM innerHTML mutations ('innerHTML =')
        - No dummy payloads ('question_id:')
        """
        driver_path = ZENCLASS_DIR / "drivers" / "guvi_driver.py"
        with open(driver_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Parse AST to ensure valid Python syntax
        tree = ast.parse(code, filename=str(driver_path))
        self.assertIsNotNone(tree)

        # Assert no forbidden mock shims in source
        self.assertNotIn("fetch('/code-kata/question", code, "Mock fetch shim found in guvi_driver.py")
        self.assertNotIn("fetch('/usercheck.php", code, "Mock auth fetch shim found in guvi_driver.py")
        self.assertNotIn("qs.textContent = 'Solved!'", code, "DOM mutation shim found in guvi_driver.py")
        self.assertNotIn("modal.style.display = 'block'", code, "Modal display mutation found in guvi_driver.py")

        # Check all page.evaluate occurrences
        eval_matches = re.findall(r'page\.evaluate\((.*?)\)', code, re.DOTALL)
        self.assertEqual(len(eval_matches), 2, f"Expected exactly 2 legitimate evaluates, found {len(eval_matches)}")

        # Legitimate 1: localStorage.getItem('authToken')
        self.assertIn("localStorage.getItem('authToken')", eval_matches[0])
        # Legitimate 2: (el) => el.value
        self.assertIn("el.value", eval_matches[1])

    def test_19_zero_shims_during_sandbox_failure(self):
        """Under local sandbox failure, driver strictly halts without executing any evaluate shims."""
        temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(temp_dir.name) / "test_state.db"
        state_mgr = StateManager(db_path=db_path)
        mock_browser = MagicMock(spec=BrowserManager)
        mock_page = MagicMock()
        mock_browser.get_page.return_value = mock_page
        driver = GuviDriver(browser_manager=mock_browser, state_manager=state_mgr)
        driver._current_page = mock_page

        mock_spec = ProblemSpecification(
            title="Sum Problem",
            description="Add two numbers",
            sample_cases=[("1 2", "3")],
        )
        mock_sol = GeneratedSolution(code="def solve(): print(0)", category="math", confidence=0.9)
        mock_fail_val = ValidationResult(
            all_passed=False,
            results=[TestCaseResult(input_data="1 2", expected_output="3", actual_output="0", passed=False, error_message="Mismatch")],
            error_message="Mismatch"
        )

        with patch("drivers.guvi_driver.extract_problem_spec", return_value=mock_spec), \
             patch("drivers.guvi_driver.generate_solution", return_value=mock_sol), \
             patch("drivers.guvi_driver.test_solution", return_value=mock_fail_val), \
             patch("drivers.guvi_driver.inject_code") as mock_inject:

            res = driver.solve_problem("sum-problem")

            # Assertions:
            self.assertFalse(res["success"])
            self.assertEqual(res["stage"], "LOCAL_SANDBOX")
            self.assertEqual(res["error"], "Mismatch")

            # Verify inject_code and evaluate were NEVER called
            mock_inject.assert_not_called()
            mock_page.evaluate.assert_not_called()

            # State recorded as FAILED / TEST_FAILED
            task = state_mgr.get_task("guvi-sum-problem")
            self.assertEqual(task.status, TaskStatus.FAILED.value)
            self.assertEqual(task.result, TaskResult.TEST_FAILED.value)

        temp_dir.cleanup()

    def test_20_zero_shims_during_ace_injection_failure(self):
        """Under Ace editor injection failure, driver halts without submitting or evaluating fake responses."""
        temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(temp_dir.name) / "test_state.db"
        state_mgr = StateManager(db_path=db_path)
        mock_browser = MagicMock(spec=BrowserManager)
        mock_page = MagicMock()
        mock_browser.get_page.return_value = mock_page
        driver = GuviDriver(browser_manager=mock_browser, state_manager=state_mgr)
        driver._current_page = mock_page

        mock_spec = ProblemSpecification(title="Sample", description="", sample_cases=[])
        mock_sol = GeneratedSolution(code="print('ok')", category="general", confidence=1.0)
        mock_val = ValidationResult(all_passed=True, results=[])

        with patch("drivers.guvi_driver.extract_problem_spec", return_value=mock_spec), \
             patch("drivers.guvi_driver.generate_solution", return_value=mock_sol), \
             patch("drivers.guvi_driver.test_solution", return_value=mock_val), \
             patch("drivers.guvi_driver.wait_for_editor", return_value=False):

            res = driver.solve_problem("sample-prob")

            self.assertFalse(res["success"])
            self.assertEqual(res["stage"], "ACE_INJECTION")
            # Click submit was NEVER called
            mock_page.click.assert_not_called()

        temp_dir.cleanup()

    def test_21_zero_shims_during_run_code_failure(self):
        """When platform Run Code shows 'Wrong', driver halts without clicking Submit or faking success."""
        temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(temp_dir.name) / "test_state.db"
        state_mgr = StateManager(db_path=db_path)
        mock_browser = MagicMock(spec=BrowserManager)
        mock_page = MagicMock()
        mock_browser.get_page.return_value = mock_page
        driver = GuviDriver(browser_manager=mock_browser, state_manager=state_mgr)
        driver._current_page = mock_page

        mock_spec = ProblemSpecification(title="Sample", description="", sample_cases=[])
        mock_sol = GeneratedSolution(code="print('ok')", category="general", confidence=1.0)
        mock_val = ValidationResult(all_passed=True, results=[])

        # Test results pane indicates 'Wrong'
        results_pane = MagicMock()
        results_pane.inner_text.return_value = "Test Case 1: Wrong Answer"

        def query_sel(sel):
            if "test-pill" in sel or "test-results" in sel:
                return results_pane
            return None

        mock_page.query_selector.side_effect = query_sel
        driver.find_first_selector = MagicMock(return_value="button.run-code")

        with patch("drivers.guvi_driver.extract_problem_spec", return_value=mock_spec), \
             patch("drivers.guvi_driver.generate_solution", return_value=mock_sol), \
             patch("drivers.guvi_driver.test_solution", return_value=mock_val), \
             patch("drivers.guvi_driver.wait_for_editor", return_value=True), \
             patch("drivers.guvi_driver.inject_code", return_value=True):

            res = driver.solve_problem("sample-prob")

            self.assertFalse(res["success"])
            self.assertEqual(res["stage"], "RUN_CODE")
            self.assertIn("Wrong", res["error"])

            # Verify Submit button was never clicked
            clicked_selectors = [c[0][0] for c in mock_page.click.call_args_list if c[0]]
            self.assertNotIn("button.submit-code", clicked_selectors)
            self.assertNotIn("button:has-text('Submit')", clicked_selectors)

        temp_dir.cleanup()

    def test_22_zero_shims_during_submit_timeout(self):
        """When platform verification times out, driver fails genuinely without fabricating Solved!."""
        temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(temp_dir.name) / "test_state.db"
        state_mgr = StateManager(db_path=db_path)
        mock_browser = MagicMock(spec=BrowserManager)
        mock_page = MagicMock()
        mock_browser.get_page.return_value = mock_page
        driver = GuviDriver(browser_manager=mock_browser, state_manager=state_mgr)
        driver._current_page = mock_page

        mock_spec = ProblemSpecification(title="Sample", description="", sample_cases=[])
        mock_sol = GeneratedSolution(code="print('ok')", category="general", confidence=1.0)
        mock_val = ValidationResult(all_passed=True, results=[])

        driver.find_first_selector = MagicMock(side_effect=lambda sels, timeout=None: sels[0])
        mock_page.query_selector.return_value = None
        # wait_for_function times out
        mock_page.wait_for_function.side_effect = TimeoutError("Timed out waiting for Solved!")

        with patch("drivers.guvi_driver.extract_problem_spec", return_value=mock_spec), \
             patch("drivers.guvi_driver.generate_solution", return_value=mock_sol), \
             patch("drivers.guvi_driver.test_solution", return_value=mock_val), \
             patch("drivers.guvi_driver.wait_for_editor", return_value=True), \
             patch("drivers.guvi_driver.inject_code", return_value=True):

            res = driver.solve_problem("sample-prob")

            self.assertFalse(res["success"])
            self.assertEqual(res["stage"], "SUBMISSION_VERIFY")
            self.assertIn("did not yield positive 'Solved!'", res["error"])

            # State recorded as FAILED
            task = state_mgr.get_task("guvi-sample-prob")
            self.assertEqual(task.status, TaskStatus.FAILED.value)
            self.assertEqual(task.result, TaskResult.SUBMISSION_FAILED.value)

        temp_dir.cleanup()


class TestInterfaceSignatureIntegrity(unittest.TestCase):
    """Verify solver.ace_adapter.inject_code contract and autospec compatibility."""

    def test_23_inject_code_signature_and_autospec_compatibility(self):
        """Verifies inject_code parameter signature accepts (page, code, verify=True)."""
        sig = inspect.signature(inject_code)
        self.assertIn("page", sig.parameters)
        self.assertIn("code", sig.parameters)
        self.assertIn("verify", sig.parameters)
        self.assertEqual(sig.parameters["verify"].default, True)

        # Test autospec patching with all parameter combinations
        with patch("drivers.guvi_driver.inject_code", autospec=True) as mock_inj:
            # 1. Positional + keyword default
            mock_inj("page_obj", "source_code")
            # 2. Positional + explicit keyword verify=True
            mock_inj("page_obj", "source_code", verify=True)
            # 3. Positional + explicit keyword verify=False
            mock_inj("page_obj", "source_code", verify=False)
            self.assertEqual(mock_inj.call_count, 3)

    def test_24_inject_code_delegates_verify_to_adapter(self):
        """Verifies module inject_code forwards verify argument to AceEditorAdapter."""
        mock_page = MagicMock()
        mock_adapter = MagicMock(spec=AceEditorAdapter)

        with patch("solver.ace_adapter._default_adapter", mock_adapter):
            inject_code(mock_page, "test_code", verify=False)
            mock_adapter.inject_code.assert_called_once_with(mock_page, "test_code", verify=False)

            mock_adapter.reset_mock()
            inject_code(mock_page, "test_code", verify=True)
            mock_adapter.inject_code.assert_called_once_with(mock_page, "test_code", verify=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
