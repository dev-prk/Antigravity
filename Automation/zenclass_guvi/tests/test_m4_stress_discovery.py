"""
tests/test_m4_stress_discovery.py - Adversarial Stress Test Harness for Milestone 4.

Focus Areas:
1. Kanban Board Discovery under diverse and hostile mock DOMs:
   - Empty columns (0 active, 0 pending, 0 completed)
   - Completely missing column containers
   - High volume (60+ cards across columns)
   - Malformed/degraded cards (missing data-task-id, missing titles, empty text, missing tags, missing buttons, unicode edge-cases)
   - Diverse action buttons (Attend, Submit, Re-submit, Resubmit, Edit, Report, unknown)
2. Card Status Classification:
   - Attend cards mapped to TaskStatus.BLOCKED / TaskResult.AWAITING_INPUT
   - Re-submit cards mapped to TaskStatus.REDO / TaskResult.UNATTEMPTED (attempt_count=1)
   - Submit cards mapped to TaskStatus.DISCOVERED / TaskResult.UNATTEMPTED (attempt_count=0)
   - Completed cards mapped to TaskStatus.COMPLETED / TaskResult.PASSED
   - Evaluation score handling ('10/10' vs '--/10')
3. 4-Tier Session Recovery Cascade:
   - Tier 1: Fast-Path DOM Anchor (success on /tasks, rejection on /login or untrusted domain)
   - Tier 2: Storage & Expiry (unexpired token success, expired token rejection, short/corrupted token rejection)
   - Tier 3: Probe Navigation (/tasks probe success vs redirect to /login failure, network error resilience)
   - Tier 4: Credential fallback trigger
   - MFA Detection (.login-mfa-active, .login-mfa-wrapper) and terminal bell emission
4. Static AST Clean Code Verification:
   - Real Python ast parse of drivers/zenclass_tasks_driver.py
   - No mock evaluate shims, no fake DOM mutations, no test framework imports in production code
"""

import ast
import io
import json
import os
import re
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
from core.hitl_handler import HitlHandler, GuardrailType
from core.reporter import SummaryReporter

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


class TestAdversarialKanbanDiscovery(unittest.TestCase):
    """Stress-tests Kanban board parsing across extreme DOM topologies."""

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

    def test_empty_board_all_columns_empty(self):
        """Stress: Board with 3 present columns but 0 cards in any column."""
        col_active = MagicMock()
        col_active.query_selector_all.return_value = []
        col_pending = MagicMock()
        col_pending.query_selector_all.return_value = []
        col_completed = MagicMock()
        col_completed.query_selector_all.return_value = []

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
            self.assertEqual(tasks, [])
            # StateManager batch record should not fail or be called with empty list
            if self.mock_sm.batch_record_tasks.called:
                self.assertEqual(len(self.mock_sm.batch_record_tasks.call_args[0][0]), 0)

    def test_missing_column_containers_entirely(self):
        """Stress: DOM is stripped of all column containers entirely."""
        self.mock_page.query_selector.return_value = None
        self.mock_page.query_selector_all.return_value = []

        with patch.object(self.driver, "navigate", autospec=True), \
             patch.object(self.driver, "check_guardrails", autospec=True):
            tasks = self.driver.discover_tasks()
            self.assertEqual(tasks, [])

    def test_high_volume_cards_65_cards(self):
        """Stress: 65 cards across columns (25 active, 20 pending, 20 completed)."""
        def make_mock_card(task_id, title, col_class, action_type="SUBMIT", is_redo=False, score=None):
            card = MagicMock()
            card.get_attribute.side_effect = lambda attr: task_id if attr == "data-task-id" else col_class
            card.inner_text.return_value = f"{title}\nTag\n{action_type}"

            title_el = MagicMock()
            title_el.inner_text.return_value = title

            redo_el = MagicMock()
            redo_el.inner_text.return_value = "Redo" if is_redo else ""

            btn_el = MagicMock()
            btn_el.inner_text.return_value = action_type

            score_el = MagicMock()
            score_el.inner_text.return_value = score if score else ""

            def qs(sel):
                if "task-name" in sel:
                    return title_el
                if "redo" in sel and is_redo:
                    return redo_el
                if "primary-outlined-submit-btn" in sel and action_type in ("SUBMIT", "RESUBMIT", "ATTEND"):
                    return btn_el
                if "student-task-edit-btn" in sel and action_type == "EDIT":
                    return btn_el
                if "project-report-btn" in sel and action_type == "REPORT":
                    return btn_el
                if "common-score-text" in sel and score:
                    return score_el
                return None

            card.query_selector.side_effect = qs
            card.query_selector_all.return_value = []
            return card

        cards_active = [
            make_mock_card(f"act-{i}", f"Active Task {i}", "itemactive-tasks", "ATTEND" if i == 0 else "SUBMIT")
            for i in range(25)
        ]
        cards_pending = [
            make_mock_card(f"pen-{i}", f"Pending Task {i}", "itempending-tasks", "RESUBMIT", is_redo=True)
            for i in range(20)
        ]
        cards_completed = [
            make_mock_card(f"comp-{i}", f"Completed Task {i}", "itemcompleted-tasks", "EDIT", score="10/10")
            for i in range(20)
        ]

        col_active = MagicMock()
        col_active.query_selector_all.return_value = cards_active
        col_pending = MagicMock()
        col_pending.query_selector_all.return_value = cards_pending
        col_completed = MagicMock()
        col_completed.query_selector_all.return_value = cards_completed

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

        start_t = time.time()
        with patch.object(self.driver, "navigate", autospec=True), \
             patch.object(self.driver, "check_guardrails", autospec=True):
            tasks = self.driver.discover_tasks()
        duration = time.time() - start_t

        self.assertEqual(len(tasks), 65)
        # Verify deterministic parsing and performance (< 1.0 second)
        self.assertLess(duration, 1.0, f"Parsing 65 cards took too long: {duration}s")

        # Verify StateManager received all 65
        self.mock_sm.batch_record_tasks.assert_called_once()
        batch = self.mock_sm.batch_record_tasks.call_args[0][0]
        self.assertEqual(len(batch), 65)

        # Check distribution
        statuses = [b["status"] for b in batch]
        self.assertEqual(statuses.count(TaskStatus.BLOCKED.value), 1)  # act-0 is ATTEND
        self.assertEqual(statuses.count(TaskStatus.DISCOVERED.value), 24)
        self.assertEqual(statuses.count(TaskStatus.REDO.value), 20)
        self.assertEqual(statuses.count(TaskStatus.COMPLETED.value), 20)

    def test_malformed_and_degraded_cards(self):
        """Stress: Missing fields, empty texts, fallback titles, unicode symbols."""
        # 1. Missing data-task-id -> derives slug
        c1 = MagicMock()
        c1.get_attribute.return_value = None
        t1 = MagicMock()
        t1.inner_text.return_value = "React Component Architecture"
        c1.query_selector.side_effect = lambda sel: t1 if "task-name" in sel else None
        c1.query_selector_all.return_value = []

        # 2. Missing title element -> falls back to inner_text
        c2 = MagicMock()
        c2.get_attribute.return_value = "task-fallback-text"
        c2.inner_text.return_value = "Fallback Line Title\nSecond line\nSubmit"
        c2.query_selector.return_value = None
        c2.query_selector_all.return_value = []

        # 3. Completely empty card text -> falls back to "Untitled ZenClass Task"
        c3 = MagicMock()
        c3.get_attribute.return_value = None
        c3.inner_text.return_value = ""
        c3.query_selector.return_value = None
        c3.query_selector_all.return_value = []

        # 4. Special unicode / XSS-like title
        c4 = MagicMock()
        c4.get_attribute.return_value = "xss-test"
        t4 = MagicMock()
        t4.inner_text.return_value = "✨ Day 10: <script>alert('xss')</script> & 特殊字符"
        c4.query_selector.side_effect = lambda sel: t4 if "task-name" in sel else None
        c4.query_selector_all.return_value = []

        col_active = MagicMock()
        col_active.query_selector_all.return_value = [c1, c2, c3, c4]

        def page_qs(sel):
            if "active-tasks" in sel:
                return col_active
            return MagicMock(query_selector_all=MagicMock(return_value=[]))

        self.mock_page.query_selector.side_effect = page_qs
        self.mock_page.query_selector_all.return_value = []

        with patch.object(self.driver, "navigate", autospec=True), \
             patch.object(self.driver, "check_guardrails", autospec=True):
            tasks = self.driver.discover_tasks()

        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0].task_id, "zenclass-task-react-component-architecture")
        self.assertEqual(tasks[1].title, "Fallback Line Title")
        self.assertEqual(tasks[2].title, "Untitled ZenClass Task")
        self.assertEqual(tasks[2].task_id, "zenclass-task-untitled-zenclass-task")
        self.assertIn("alert", tasks[3].title)

    def test_diverse_action_buttons(self):
        """Stress: Attend, Submit, Re-submit, Resubmit, Edit, Report, unknown."""
        buttons = [
            ("ATTEND", "Attend", "primary-outlined-submit-btn"),
            ("SUBMIT", "Submit", "primary-outlined-submit-btn"),
            ("RESUBMIT", "Re-submit", "primary-outlined-submit-btn"),
            ("RESUBMIT", "Resubmit", "primary-outlined-submit-btn"),
            ("EDIT", "Edit", "student-task-edit-btn"),
            ("REPORT", "Report", "project-report-btn"),
            ("NONE", "Unknown Action", "some-other-btn"),
        ]

        cards = []
        for idx, (expected_act, label, btn_class) in enumerate(buttons):
            c = MagicMock()
            c.get_attribute.side_effect = lambda attr: f"card-{idx}" if attr == "data-task-id" else "itemactive-tasks"
            c.inner_text.return_value = f"Task {idx}\n{label}"

            title_el = MagicMock()
            title_el.inner_text.return_value = f"Task {idx}"

            btn_el = MagicMock()
            btn_el.inner_text.return_value = label

            def make_qs(b_class, b_el, t_el):
                def qs(sel):
                    if "task-name" in sel:
                        return t_el
                    if b_class in sel:
                        return b_el
                    return None
                return qs

            c.query_selector.side_effect = make_qs(btn_class, btn_el, title_el)
            c.query_selector_all.return_value = []
            cards.append(c)

        col_active = MagicMock()
        col_active.query_selector_all.return_value = cards

        self.mock_page.query_selector.side_effect = lambda sel: col_active if "active-tasks" in sel else MagicMock(query_selector_all=MagicMock(return_value=[]))
        self.mock_page.query_selector_all.return_value = []

        with patch.object(self.driver, "navigate", autospec=True), \
             patch.object(self.driver, "check_guardrails", autospec=True):
            tasks = self.driver.discover_tasks()

        self.assertEqual(len(tasks), len(buttons))
        for task, (expected_act, label, _) in zip(tasks, buttons):
            self.assertEqual(task.action_type, expected_act, f"Failed for label '{label}'")


class TestAdversarialCardClassification(unittest.TestCase):
    """Stress-tests the deterministic state mapping engine (_classify_task_state)."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.driver = ZenClassTasksDriver(browser_manager=self.mock_bm)

    def test_attend_cards_priority_over_all_other_signals(self):
        """Stress: Attend button (HYREX/PETs) MUST always map to BLOCKED / AWAITING_INPUT."""
        scenarios = [
            # Active column
            DiscoveredTask(task_id="t1", title="Quiz 1", column="active", action_type="ATTEND"),
            # Pending column
            DiscoveredTask(task_id="t2", title="Quiz 2", column="pending", action_type="ATTEND"),
            # Redo flag set + Attend
            DiscoveredTask(task_id="t3", title="Quiz 3", column="active", is_redo=True, action_type="ATTEND"),
            # Score present + Attend
            DiscoveredTask(task_id="t4", title="Quiz 4", column="completed", score="5/10", action_type="ATTEND"),
        ]
        for t in scenarios:
            status, result, next_act, reason = self.driver._classify_task_state(t)
            self.assertEqual(status, TaskStatus.BLOCKED.value, f"Failed on {t.title}")
            self.assertEqual(result, TaskResult.AWAITING_INPUT.value, f"Failed on {t.title}")
            self.assertEqual(next_act, "REQUIRES_HUMAN_INTERACTIVE_ASSESSMENT")
            self.assertIsNotNone(reason)

    def test_redo_classification_variants(self):
        """Stress: Re-submit button or is_redo=True maps to REDO / UNATTEMPTED."""
        t1 = DiscoveredTask(task_id="t1", title="Task 1", column="active", action_type="RESUBMIT", is_redo=False)
        t2 = DiscoveredTask(task_id="t2", title="Task 2", column="pending", action_type="SUBMIT", is_redo=True)

        for t in [t1, t2]:
            status, result, next_act, reason = self.driver._classify_task_state(t)
            self.assertEqual(status, TaskStatus.REDO.value)
            self.assertEqual(result, TaskResult.UNATTEMPTED.value)
            self.assertEqual(next_act, "SOLVE_AND_SUBMIT")
            self.assertIsNone(reason)

    def test_completed_classification_and_score_distinction(self):
        """Stress: Completed column, Edit/Report, score != '--/10' vs unattempted '--/10'."""
        # 1. Column completed
        t1 = DiscoveredTask(task_id="t1", title="T1", column="completed", action_type="NONE")
        self.assertEqual(self.driver._classify_task_state(t1)[0], TaskStatus.COMPLETED.value)

        # 2. Action EDIT
        t2 = DiscoveredTask(task_id="t2", title="T2", column="active", action_type="EDIT")
        self.assertEqual(self.driver._classify_task_state(t2)[0], TaskStatus.COMPLETED.value)

        # 3. Action REPORT
        t3 = DiscoveredTask(task_id="t3", title="T3", column="active", action_type="REPORT")
        self.assertEqual(self.driver._classify_task_state(t3)[0], TaskStatus.COMPLETED.value)

        # 4. Evaluated score '8/10'
        t4 = DiscoveredTask(task_id="t4", title="T4", column="active", score="8/10", action_type="SUBMIT")
        self.assertEqual(self.driver._classify_task_state(t4)[0], TaskStatus.COMPLETED.value)

        # 5. Placeholder score '--/10' in active column -> DISCOVERED (NOT completed)
        t5 = DiscoveredTask(task_id="t5", title="T5", column="active", score="--/10", action_type="SUBMIT")
        self.assertEqual(self.driver._classify_task_state(t5)[0], TaskStatus.DISCOVERED.value)


class TestAdversarialSessionRecoveryCascade(unittest.TestCase):
    """Stress-tests the 4-tier session recovery cascade and MFA detection."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.mock_hitl = MagicMock(spec=HitlHandler)
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            hitl_handler=self.mock_hitl,
        )

    def test_tier_1_success_on_tasks_url(self):
        """Tier 1: On /tasks with visible DOM indicator -> instant success."""
        self.mock_page.url = "https://v2.zenclass.in/tasks"
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True) as mock_nav:
            mock_vis.return_value = True
            self.assertTrue(self.driver.is_authenticated())
            mock_nav.assert_not_called()

    def test_tier_1_rejection_when_on_login_route(self):
        """Tier 1: Even if indicator is visible, if URL has '/login', Tier 1 MUST NOT accept."""
        self.mock_page.url = "https://v2.zenclass.in/login"
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True):
            mock_vis.return_value = True
            # Tier 1 should be bypassed, Tier 2 storage fails, Tier 3 probe fails
            self.mock_page.evaluate.return_value = None
            self.assertFalse(self.driver.is_authenticated())

    def test_tier_1_rejection_on_untrusted_domain(self):
        """Tier 1: Indicator visible on malicious/third-party domain MUST NOT authenticate."""
        self.mock_page.url = "https://phishing-zenclass.com/tasks"
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True):
            mock_vis.return_value = True
            self.mock_page.evaluate.return_value = None
            self.assertFalse(self.driver.is_authenticated())

    def test_tier_2_storage_expiry_and_token_length(self):
        """Tier 2: Checks unexpired expiry timestamp and token string validation."""
        self.mock_page.url = "https://v2.zenclass.in/dashboard"

        # Case A: Valid unexpired token
        future_ms = (time.time() + 1800) * 1000
        valid_payload = json.dumps({"authToken": "long_jwt_token_zenclass_valid_12345", "expiry": future_ms})
        self.mock_page.evaluate.return_value = valid_payload
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis:
            mock_vis.return_value = False
            self.assertTrue(self.driver.is_authenticated())

        # Case B: Expired token
        past_ms = (time.time() - 1800) * 1000
        expired_payload = json.dumps({"authToken": "long_jwt_token_zenclass_valid_12345", "expiry": past_ms})
        self.mock_page.evaluate.return_value = expired_payload
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True):
            mock_vis.return_value = False
            self.mock_page.url = "https://v2.zenclass.in/login"
            self.assertFalse(self.driver.is_authenticated())

        # Case C: Short token (length <= 10)
        short_payload = json.dumps({"authToken": "short", "expiry": future_ms})
        self.mock_page.evaluate.return_value = short_payload
        with patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "navigate", autospec=True):
            mock_vis.return_value = False
            self.mock_page.url = "https://v2.zenclass.in/login"
            self.assertFalse(self.driver.is_authenticated())

    def test_tier_3_probe_navigation_behavior(self):
        """Tier 3: Probe navigation to /tasks succeeds or detects redirect."""
        # Case A: Probe succeeds
        self.mock_page.url = "about:blank"
        self.mock_page.evaluate.return_value = None

        def probe_success(url, wait_until=None, timeout=None):
            self.mock_page.url = "https://v2.zenclass.in/tasks"

        with patch.object(self.driver, "navigate", autospec=True) as mock_nav, \
             patch.object(self.driver, "check_guardrails", autospec=True) as mock_guard, \
             patch.object(self.driver, "is_visible", autospec=True) as mock_vis, \
             patch.object(self.driver, "sync_session_state", autospec=True), \
             patch.object(self.driver, "persist_session", autospec=True):
            mock_nav.side_effect = probe_success
            mock_vis.side_effect = lambda sel, timeout=0.5: sel in ZenClassTasksDriver.POST_LOGIN_DOM_INDICATORS
            self.assertTrue(self.driver.is_authenticated())
            mock_guard.assert_called_once()

        # Case B: Probe redirects to /login -> returns False
        def probe_redirect(url, wait_until=None, timeout=None):
            self.mock_page.url = "https://v2.zenclass.in/login"

        with patch.object(self.driver, "navigate", autospec=True) as mock_nav, \
             patch.object(self.driver, "check_guardrails", autospec=True), \
             patch.object(self.driver, "is_visible", autospec=True) as mock_vis:
            mock_nav.side_effect = probe_redirect
            mock_vis.return_value = False
            self.assertFalse(self.driver.is_authenticated())

    def test_mfa_detection_and_terminal_bell_alert(self):
        """Stress: MFA detection (.login-mfa-active) triggers audible terminal alert."""
        self.mock_page.url = "https://v2.zenclass.in/login"

        with patch.object(self.driver, "find_first_selector", autospec=True) as mock_find:
            mock_find.return_value = ".login-mfa-active"
            self.mock_hitl.check_and_handle_guardrails.return_value = True

            triggered = self.driver.check_mfa_guardrail(task_id="mfa-stress-check")
            self.assertTrue(triggered)
            self.mock_hitl.check_and_handle_guardrails.assert_called_once_with(
                self.mock_page,
                task_id="mfa-stress-check",
                context_desc="ZenClass MFA Two-Factor Verification"
            )

        # Verify HitlHandler emits terminal bell (\a) to stdout
        real_hitl = HitlHandler(interactive=False, audible_bell=True)
        captured_stdout = io.StringIO()
        with patch("sys.stdout", captured_stdout):
            real_hitl.emit_alert()
        self.assertIn("\a", captured_stdout.getvalue(), "Audible terminal bell (\a) was not emitted!")


class TestStaticASTCleanCodeVerification(unittest.TestCase):
    """Rigorous AST-level static check verifying zero mock evaluate shims or fake DOM mutations."""

    def test_ast_inspection_of_zenclass_tasks_driver(self):
        """Parses drivers/zenclass_tasks_driver.py AST to enforce clean code constraints."""
        driver_path = Path(PROJECT_ROOT) / "drivers" / "zenclass_tasks_driver.py"
        self.assertTrue(driver_path.exists())

        source_code = driver_path.read_text(encoding="utf-8")
        parsed_ast = ast.parse(source_code, filename="zenclass_tasks_driver.py")

        # 1. No test framework imports in production driver
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(alias.name, ["unittest", "pytest", "mock"], f"Illegal import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                self.assertNotIn("unittest", module, f"Illegal import from: {module}")
                self.assertNotIn("pytest", module, f"Illegal import from: {module}")

        # 2. No isinstance checks with Mock/MagicMock
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "isinstance":
                for arg in node.args:
                    if isinstance(arg, ast.Name) and "Mock" in arg.id:
                        self.fail(f"Illegal mock typecheck detected in AST: {arg.id}")

        # 3. No mock_evaluate attributes or fake DOM script shims
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Attribute):
                self.assertNotIn("mock_evaluate", node.attr)
                self.assertNotIn("mockEvaluate", node.attr)

        # 4. Text regex scan for evaluate shims
        forbidden_regexes = [
            r"isinstance\([^,]+evaluate,\s*(?:MagicMock|Mock)\)",
            r"mock_evaluate",
            r"mockEvaluate",
            r"__mock__",
            r"unittest\.mock",
            r"from unittest\.mock import",
        ]
        for rgx in forbidden_regexes:
            matches = re.findall(rgx, source_code)
            self.assertEqual(len(matches), 0, f"Detected forbidden pattern '{rgx}' in {driver_path}")


if __name__ == "__main__":
    unittest.main()
