"""
test_m1_core.py - Comprehensive Unit and Integration Test Suite for Milestone 1
Validates:
- Configuration parameters and default headed mode (Requirement R1)
- Headed Browser Lifecycle & persistence (core/browser.py)
- Thread-safe persistent State Manager with WAL mode & atomic JSON export (core/state_manager.py)
- Human-in-the-Loop Handler & guardrail detection (core/hitl_handler.py)
- Executive Markdown & machine-readable JSON Summary Reporter (core/reporter.py)
- Unified CLI interface parsing and signal handling (main.py)
"""

import json
import os
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

import config
from core.browser import BrowserManager, get_browser_manager, close_context
from core.state_manager import (
    StateManager,
    TaskRecord,
    TaskStatus,
    TaskPlatform,
    TaskResult
)
from core.hitl_handler import (
    HitlHandler,
    HITLHandler,
    GuardrailType,
    GuardrailRule,
    GUARDRAIL_RULES
)
from core.reporter import SummaryReporter, Reporter
from main import create_cli_parser, AutomationRunner


class TestConfig(unittest.TestCase):
    """Verifies configuration parameters strictly satisfy requirements."""

    def test_default_headed_mode(self):
        """Authoritative source: ORIGINAL_REQUEST §R1 & PROJECT.md: headless=False."""
        self.assertFalse(
            config.HEADLESS,
            "Browser execution MUST default to headless=False for foreground visual monitoring."
        )

    def test_platform_urls(self):
        """Verifies reference URLs match user requirements."""
        self.assertEqual(config.GUVI_CODEKATA_URL, "https://www.guvi.in/code-kata/")
        self.assertEqual(config.ZENCLASS_TASKS_URL, "https://v2.zenclass.in/tasks")
        self.assertEqual(config.ZENCLASS_PROJECTS_URL, "https://v2.zenclass.in/projects")

    def test_browser_flags_include_anti_detection(self):
        """Verifies stealth bot mitigation flags."""
        self.assertIn("--disable-blink-features=AutomationControlled", config.BROWSER_ARGS)
        self.assertIn("--start-maximized", config.BROWSER_ARGS)
        self.assertIn("--enable-automation", config.IGNORE_DEFAULT_ARGS)


class TestBrowserManager(unittest.TestCase):
    """Verifies BrowserManager lifecycle and persistence mechanics."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_browser_")
        self.profile_dir = Path(self.temp_dir) / ".test_profile"
        self.state_file = Path(self.temp_dir) / "storage_state.json"

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_browser_manager_initialization(self):
        """Verifies BrowserManager uses default headed settings."""
        bm = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.state_file,
            headless=False
        )
        self.assertFalse(bm.headless)
        self.assertEqual(bm.profile_dir, self.profile_dir)
        self.assertEqual(bm.storage_state_path, self.state_file)

    def test_browser_persistent_launch_and_cleanup(self):
        """Verifies headed Chromium launch, navigation, tab reuse, and clean shutdown."""
        bm = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.state_file,
            headless=False,
            slow_mo=10.0
        )
        try:
            with bm:
                ctx = bm.get_context()
                self.assertIsNotNone(ctx)

                page = bm.get_page("data:text/html,<html><body><h1>Headed Test</h1></body></html>")
                self.assertEqual(page.inner_text("h1"), "Headed Test")

                # Verify anti-detection flag
                webdriver_flag = page.evaluate("navigator.webdriver")
                self.assertFalse(webdriver_flag, "navigator.webdriver must evaluate to False")

                # Verify tab reuse (does not create orphaned tabs)
                page2 = bm.get_page()
                self.assertEqual(page, page2)

                # Test auxiliary tab management
                extra_page = ctx.new_page()
                self.assertEqual(len(ctx.pages), 2)
                closed = bm.close_auxiliary_tabs(keep_page=page)
                self.assertEqual(closed, 1)
                self.assertEqual(len(ctx.pages), 1)

            # Context closed: verify storage state file was dumped
            self.assertTrue(self.state_file.exists())
            with open(self.state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            self.assertIn("cookies", state_data)

        except Exception as e:
            # If Playwright browser binaries are not present or headless display unavailable in test runner
            if "Executable doesn't exist" in str(e) or "Host system is missing dependencies" in str(e):
                self.skipTest(f"Playwright browser dependencies unavailable: {e}")
            else:
                raise


class TestStateManager(unittest.TestCase):
    """Verifies SQLite state persistence, R3 compliance, and atomic JSON export."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sm_")
        self.db_path = os.path.join(self.temp_dir, "test_state.db")
        self.json_path = os.path.join(self.temp_dir, "state_summary.json")
        self.sm = StateManager(db_path=self.db_path, json_export_path=self.json_path)

    def tearDown(self):
        self.sm.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sqlite_wal_mode(self):
        """Verifies database initializes with Write-Ahead Logging for crash resilience."""
        cursor = self.sm.conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        self.assertEqual(mode.lower(), "wal")

    def test_record_task_all_nine_fields(self):
        """Verifies all 9 mandatory R3 fields are captured in record and export."""
        task = self.sm.record_task(
            task_id="guvi-001",
            platform="guvi_codekata",
            title="Sum of Two Numbers",
            category="Easy",
            url="https://www.guvi.in/code-kata/sum/",
            status="pending",
            attempts=0,
            result="UNATTEMPTED",
            failure_reason=None,
            next_action="SOLVE_AND_SUBMIT",
            time_spent_seconds=0.0,
            metadata={"difficulty": "Easy", "points": 20}
        )
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, "guvi-001")
        self.assertEqual(task.platform, "guvi_codekata")
        self.assertEqual(task.task_category, "Easy")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.attempt_count, 0)
        self.assertEqual(task.result, "UNATTEMPTED")
        self.assertIsNone(task.failure_reason)
        self.assertEqual(task.next_action, "SOLVE_AND_SUBMIT")

        # Verify property aliases
        self.assertEqual(task.attempts, 0)
        self.assertEqual(task.category, "Easy")

        # Verify R3 dictionary representation
        d = task.to_dict()
        required_r3_fields = [
            "platform", "task_id", "task_category", "status",
            "attempt_count", "result", "timestamp", "failure_reason", "next_action"
        ]
        for field_name in required_r3_fields:
            self.assertIn(field_name, d, f"Missing required R3 field: {field_name}")

    def test_update_task_status_and_attempts(self):
        """Verifies status transitions, attempt counter increments, and attempt logging."""
        self.sm.record_task(
            task_id="zen-001",
            platform="zenclass",
            title="Day 1 HTML/CSS",
            category="Tasks",
            status="pending"
        )

        # Transition to in_progress
        self.sm.update_task_status(
            task_id="zen-001",
            status="in_progress",
            time_spent_seconds=5.0
        )
        t_prog = self.sm.get_task("zen-001")
        self.assertEqual(t_prog.status, "in_progress")
        self.assertEqual(t_prog.time_spent_seconds, 5.0)

        # Transition to completed with attempt increment
        self.sm.update_task_status(
            task_id="zen-001",
            status="completed",
            result="Submitted",
            next_action="none",
            time_spent_seconds=10.0,
            increment_attempts=True
        )
        t_comp = self.sm.get_task("zen-001")
        self.assertEqual(t_comp.status, "completed")
        self.assertEqual(t_comp.attempt_count, 1)
        self.assertEqual(t_comp.attempts, 1)
        self.assertEqual(t_comp.time_spent_seconds, 15.0)

        # Verify attempt log history
        attempts = self.sm.get_task_attempts("zen-001")
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[1].status, "completed")

    def test_batch_record_tasks_performance(self):
        """Verifies bulk upsert of 500 tasks completes rapidly in a single transaction."""
        batch = [
            {
                "task_id": f"batch_{i}",
                "platform": "guvi_codekata",
                "category": "Math",
                "title": f"Batch Problem {i}",
                "url": f"https://guvi.in/p/{i}",
                "status": "pending",
                "attempts": 0,
                "result": ""
            }
            for i in range(500)
        ]
        start_t = time.time()
        count = self.sm.batch_record_tasks(batch)
        duration = time.time() - start_t
        self.assertEqual(count, 500)
        self.assertLess(duration, 2.0, "Bulk insert must complete in < 2 seconds")

    def test_summary_statistics_calculation(self):
        """Verifies accurate calculation of total, completed, pending, blocked, and success rate."""
        self.sm.record_task("t1", "guvi", "Prob 1", "CodeKata", "", "completed", 1, "Solved!", "")
        self.sm.record_task("t2", "guvi", "Prob 2", "CodeKata", "", "completed", 1, "Solved!", "")
        self.sm.record_task("t3", "guvi", "Prob 3", "CodeKata", "", "pending", 0, "", "")
        self.sm.record_task("t4", "zenclass", "Task 1", "Tasks", "", "blocked", 1, "Failed", "MFA required")

        stats = self.sm.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 4)
        self.assertEqual(stats["total_completed"], 2)
        self.assertEqual(stats["total_pending"], 1)
        self.assertEqual(stats["total_blocked"], 1)
        self.assertEqual(stats["success_rate_percent"], 50.0)

        # Platform breakdown
        self.assertIn("guvi", stats["by_platform"])
        self.assertEqual(stats["by_platform"]["guvi"]["total_completed"], 2)

        # Human intervention issues
        self.assertEqual(len(stats["human_intervention_issues"]), 1)
        self.assertEqual(stats["human_intervention_issues"][0]["task_id"], "t4")

    def test_atomic_json_export(self):
        """Verifies atomic state export creates a valid JSON snapshot without file corruption."""
        self.sm.record_task("t1", "guvi", "Prob 1", "CodeKata", "", "completed", 1, "OK")
        out_path = self.sm.export_state_json(self.json_path)

        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("summary", data)
        self.assertIn("tasks", data)
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["task_id"], "t1")

    def test_thread_safety_concurrency(self):
        """Verifies thread safety under concurrent writes across multiple threads."""
        errors = []

        def worker(thread_idx: int):
            try:
                for i in range(15):
                    self.sm.record_task(
                        task_id=f"thread_{thread_idx}_task_{i}",
                        platform="guvi",
                        title=f"Task {i}",
                        status="completed",
                        auto_export_json=False
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent database writes raised errors: {errors}")
        stats = self.sm.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 60)
        self.assertEqual(stats["total_completed"], 60)


class TestHitlHandler(unittest.TestCase):
    """Verifies Human-in-the-Loop guardrail detection, audible alert, and project prompts."""

    def setUp(self):
        self.hitl = HitlHandler(interactive=False, audible_bell=False)

    def test_html_guardrail_detection(self):
        """Verifies static DOM signatures for ZenClass MFA, Guvi modal, Cloudflare, and reCAPTCHA."""
        # ZenClass MFA
        mfa_html = '<div class="login-content-wrapper login-mfa-wrapper login-mfa-active">MFA</div>'
        self.assertTrue(self.hitl.check_guardrails_in_html(mfa_html))

        # Guvi activation modal
        guvi_modal_html = '<div id="myModal" class="modal"><button id="sendmail">Send</button></div>'
        self.assertTrue(self.hitl.check_guardrails_in_html(guvi_modal_html))

        # Cloudflare turnstile
        cf_html = '<div class="cf-turnstile" data-sitekey="0x4AAAAAA..."></div>'
        self.assertTrue(self.hitl.check_guardrails_in_html(cf_html))

        # reCAPTCHA
        recaptcha_html = '<script src="https://www.google.com/recaptcha/api.js?render=6LdADb4U"></script>'
        self.assertTrue(self.hitl.check_guardrails_in_html(recaptcha_html))

        # Clean HTML should not trigger
        clean_html = '<html><body><h1>Welcome to ZenClass</h1><form><input name="email"></form></body></html>'
        self.assertFalse(self.hitl.check_guardrails_in_html(clean_html))

    def test_url_validation_regex(self):
        """Verifies validation regex permits valid HTTP/HTTPS/FTP URLs and rejects malformed ones."""
        valid_urls = [
            "https://github.com/user/capstone-project",
            "http://zenclass-capstone.netlify.app",
            "https://mern-api.onrender.com",
            "ftp://files.example.com/build.zip",
        ]
        for url in valid_urls:
            self.assertTrue(self.hitl.validate_url(url), f"Valid URL was rejected: {url}")

        invalid_urls = [
            "not-a-url",
            "htp://typo.com",
            "https://",
            "http://with space/test",
            "javascript:alert(1)",
            "",
            None,
        ]
        for url in invalid_urls:
            self.assertFalse(self.hitl.validate_url(url), f"Invalid URL was accepted: {url}")

    def test_request_project_links_with_user_inputs(self):
        """Verifies project links prompt returns validated URLs from user_inputs."""
        mock_inputs = {
            "github_Url": "https://github.com/testuser/zenclass-capstone",
            "frontEnd_Deployed_Url": "https://zenclass-capstone.netlify.app",
        }
        res = self.hitl.request_project_links(
            project_title="Full Stack Capstone",
            project_id="proj-101",
            local_code_dir="/mock/projects/capstone",
            required_fields=["github_Url", "frontEnd_Deployed_Url"],
            user_inputs=mock_inputs
        )
        self.assertEqual(res["github_Url"], "https://github.com/testuser/zenclass-capstone")
        self.assertEqual(res["frontEnd_Deployed_Url"], "https://zenclass-capstone.netlify.app")

    def test_request_project_links_with_links_file(self):
        """Verifies pre-filled links file bypasses interactive prompt."""
        temp_dir = tempfile.mkdtemp()
        links_path = os.path.join(temp_dir, "links.json")
        with open(links_path, "w", encoding="utf-8") as f:
            json.dump({
                "proj-202": {
                    "github_Url": "https://github.com/user/prefilled",
                    "frontEnd_Deployed_Url": "https://prefilled.netlify.app"
                }
            }, f)

        try:
            res = self.hitl.request_project_links(
                project_title="Prefilled Project",
                project_id="proj-202",
                local_code_dir="/mock/projects/prefilled",
                required_fields=["github_Url", "frontEnd_Deployed_Url"],
                links_file=links_path
            )
            self.assertEqual(res["github_Url"], "https://github.com/user/prefilled")
            self.assertEqual(res["frontEnd_Deployed_Url"], "https://prefilled.netlify.app")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_render_box_formatting(self):
        """Verifies ANSI box rendering format."""
        box = self.hitl.render_box(
            title="TEST BOX",
            lines=["Line 1", "Line 2"],
            color="cyan"
        )
        self.assertIn("TEST BOX", box)
        self.assertIn("Line 1", box)
        self.assertIn("Line 2", box)


class TestSummaryReporter(unittest.TestCase):
    """Verifies executive Markdown reports and JSON summary compilation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_rep_")
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.sm = StateManager(db_path=self.db_path)
        self.reporter = SummaryReporter(state_manager=self.sm, report_dir=self.temp_dir)

    def tearDown(self):
        self.sm.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_all_reports(self):
        """Verifies generation of both SUMMARY_REPORT.md and summary.json."""
        self.sm.record_task("t1", "guvi_codekata", "Odd Even", "Easy", "", "completed", 1, "Solved!", "")
        self.sm.record_task("t2", "zenclass_tasks", "JS Promises", "JS", "", "blocked", 1, "MFA", "MFA required")

        md_path, json_path = self.reporter.generate_all_reports()

        self.assertTrue(os.path.exists(md_path))
        self.assertTrue(os.path.exists(json_path))

        # Verify Markdown content
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        self.assertIn("ZenClass & Guvi Automation Execution Summary Report", md_content)
        self.assertIn("Total Tasks Discovered", md_content)
        self.assertIn("Odd Even", md_content)
        self.assertIn("JS Promises", md_content)
        self.assertIn("Human Intervention Required", md_content)

        # Verify JSON content
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        self.assertEqual(json_data["summary_metrics"]["total_discovered"], 2)
        self.assertEqual(json_data["summary_metrics"]["total_completed"], 1)
        self.assertEqual(json_data["summary_metrics"]["total_blocked"], 1)

    def test_functional_generate_report_api(self):
        """Verifies static/classmethod generate_report API for E2E harness compatibility."""
        stats = {
            "total_discovered": 5,
            "total_completed": 4,
            "total_pending": 0,
            "total_blocked": 1,
            "success_rate_percent": 80.0
        }
        tasks = [
            TaskRecord("task-1", "guvi", "CodeKata", "Sum Prob", "", "completed", 1, "Solved!"),
            TaskRecord("task-2", "zenclass", "Tasks", "HTML Modal", "", "blocked", 1, "MFA Required"),
        ]

        reports = Reporter.generate_report(stats, tasks, output_dir=self.temp_dir)
        self.assertTrue(os.path.exists(reports["markdown"]))
        self.assertTrue(os.path.exists(reports["json"]))


class TestCLIInterface(unittest.TestCase):
    """Verifies CLI argument parser, subcommands, and flag dispatch."""

    def setUp(self):
        self.parser = create_cli_parser()

    def test_subcommand_parsing(self):
        """Verifies all 5 required subcommands parse cleanly."""
        commands = ["run-all", "run-codekata", "run-zenclass", "resume", "report"]
        for cmd in commands:
            args = self.parser.parse_args([cmd])
            self.assertEqual(args.command, cmd)

    def test_cli_flags(self):
        """Verifies global CLI flags."""
        args = self.parser.parse_args([
            "--headless",
            "--slow-mo", "100",
            "--limit", "10",
            "--no-interactive",
            "run-codekata",
            "--category", "Basics"
        ])
        self.assertTrue(args.headless)
        self.assertEqual(args.slow_mo, 100.0)
        self.assertEqual(args.limit, 10)
        self.assertFalse(args.interactive)
        self.assertEqual(args.command, "run-codekata")
        self.assertEqual(args.category, "Basics")

    def test_report_subcommand_execution(self):
        """Verifies AutomationRunner executes 'report' subcommand cleanly without browser."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "cli_test.db")
        reports_dir = os.path.join(temp_dir, "reports")

        # Pre-seed database
        sm = StateManager(db_path=db_path)
        sm.record_task("cli-t1", "guvi", "Problem 1", status="completed", result="Solved!")
        sm.close()

        args = self.parser.parse_args([
            "--db-path", db_path,
            "--reports-dir", reports_dir,
            "report"
        ])
        runner = AutomationRunner(args)
        exit_code = runner.execute()
        self.assertEqual(exit_code, 0)

        # Confirm report generated
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "SUMMARY_REPORT.md")))
        self.assertTrue(os.path.exists(os.path.join(reports_dir, "summary.json")))

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
