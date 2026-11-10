#!/usr/bin/env python3
"""
Forensic Integrity Verification Script for Milestone 1.
Executed independently by auditor_m1_1 to empirically probe all components.
"""

import os
import sys
import tempfile
import sqlite3
import json
import time
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")
sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskRecord, TaskStatus, TaskResult
from core.hitl_handler import HitlHandler, GuardrailType, GUARDRAIL_RULES
from core.reporter import SummaryReporter


def test_section(name):
    print(f"\n{'='*20} [AUDIT] {name} {'='*20}")


def check(condition, desc):
    if condition:
        print(f"  [PASS] {desc}")
    else:
        print(f"  [FAIL] {desc}")
        raise AssertionError(f"Integrity check failed: {desc}")


def run_forensic_checks():
    test_section("1. Config & Headed Default Verification (R1)")
    check(config.HEADLESS is False, "config.HEADLESS defaults strictly to False")
    check("https://www.guvi.in/code-kata/" == config.GUVI_CODEKATA_URL, "Guvi CodeKata URL is authentic")
    check("https://v2.zenclass.in/tasks" == config.ZENCLASS_TASKS_URL, "ZenClass Tasks URL is authentic")
    check("https://v2.zenclass.in/projects" == config.ZENCLASS_PROJECTS_URL, "ZenClass Projects URL is authentic")
    check("--disable-blink-features=AutomationControlled" in config.BROWSER_ARGS, "Anti-detection arg is set")
    check("--start-maximized" in config.BROWSER_ARGS, "Start maximized arg is set")

    test_section("2. StateManager & SQLite Direct Forensic Inspection (R3)")
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = os.path.join(tmp_dir, "forensic.db")
        json_file = os.path.join(tmp_dir, "forensic_export.json")
        sm = StateManager(db_path=db_file, json_export_path=json_file)

        # Check DB file on disk
        check(os.path.exists(db_file), "SQLite DB file actually exists on filesystem")

        # Inspect DB schema directly via sqlite3 library
        raw_conn = sqlite3.connect(db_file)
        raw_cur = raw_conn.cursor()

        # Check WAL mode
        raw_cur.execute("PRAGMA journal_mode;")
        wal_mode = raw_cur.fetchone()[0]
        check(wal_mode.lower() == "wal", f"SQLite is running in WAL mode (got {wal_mode})")

        # Check tables
        raw_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in raw_cur.fetchall()]
        check("tasks" in tables, "Table 'tasks' exists in SQLite schema")
        check("task_attempts" in tables, "Table 'task_attempts' exists in SQLite schema")
        check("execution_runs" in tables, "Table 'execution_runs' exists in SQLite schema")

        # Insert task and check all 9 R3 fields directly from raw sqlite3
        t = sm.record_task(
            task_id="probe-001",
            platform="guvi_codekata",
            title="Forensic Probe Task",
            category="Algorithmic",
            url="https://guvi.in/probe",
            status="pending",
            attempts=0,
            result="UNATTEMPTED",
            failure_reason="None so far",
            next_action="RUN_AUDIT",
            time_spent_seconds=12.5,
            metadata={"probe": True}
        )
        check(t is not None, "record_task returned TaskRecord instance")

        # Check raw row in SQLite
        raw_cur.execute("SELECT * FROM tasks WHERE task_id='probe-001'")
        row = raw_cur.fetchone()
        col_names = [d[0] for d in raw_cur.description]
        row_dict = dict(zip(col_names, row))

        # 9 Required R3 fields:
        # platform, task_id, task_category, status, attempt_count, result, timestamp, failure_reason, next_action
        check(row_dict["task_id"] == "probe-001", "Row task_id matches")
        check(row_dict["platform"] == "guvi_codekata", "Row platform matches")
        check(row_dict["task_category"] == "Algorithmic", "Row task_category matches")
        check(row_dict["status"] == "pending", "Row status matches")
        check(row_dict["attempt_count"] == 0, "Row attempt_count matches")
        check(row_dict["result"] == "UNATTEMPTED", "Row result matches")
        check(row_dict["failure_reason"] == "None so far", "Row failure_reason matches")
        check(row_dict["next_action"] == "RUN_AUDIT", "Row next_action matches")
        check("updated_at" in row_dict, "Row updated_at timestamp exists")

        # Check TaskRecord.to_dict() compliance
        t_dict = t.to_dict()
        required_9 = [
            "platform", "task_id", "task_category", "status",
            "attempt_count", "result", "timestamp", "failure_reason", "next_action"
        ]
        for field_name in required_9:
            check(field_name in t_dict, f"TaskRecord.to_dict() contains mandatory field: {field_name}")

        # Check atomic JSON export
        export_out = sm.export_state_json(json_file)
        check(os.path.exists(export_out), "Exported state JSON file exists on disk")
        with open(export_out, "r", encoding="utf-8") as f:
            export_data = json.load(f)
        check("summary" in export_data, "Export JSON has 'summary'")
        check("tasks" in export_data, "Export JSON has 'tasks'")
        check(export_data["tasks"][0]["task_id"] == "probe-001", "Export JSON task matches probe-001")

        raw_conn.close()
        sm.close()

    test_section("3. BrowserManager Real Execution & Headed Flag (R1)")
    with tempfile.TemporaryDirectory() as tmp_dir:
        profile = Path(tmp_dir) / "profile"
        storage = Path(tmp_dir) / "storage.json"
        bm = BrowserManager(
            profile_dir=profile,
            storage_state_path=storage,
            headless=False,
            slow_mo=10.0
        )
        check(bm.headless is False, "BrowserManager instantiated with headed mode (headless=False)")

        try:
            with bm:
                ctx = bm.get_context()
                check(ctx is not None, "BrowserContext successfully launched")
                page = bm.get_page("data:text/html,<html><head><title>Forensic Title</title></head><body><div id='content'>Forensic Body</div></body></html>")
                title = page.title()
                check(title == "Forensic Title", f"Page navigated and evaluated title: '{title}'")
                body_text = page.inner_text("#content")
                check(body_text == "Forensic Body", f"Page DOM query returned: '{body_text}'")

                # Verify navigator.webdriver anti-detection
                is_webdriver = page.evaluate("navigator.webdriver")
                check(is_webdriver is False, "navigator.webdriver evaluated to False in headed context")

                # Verify screenshot capture
                shot_path = bm.save_screenshot(name="audit_test", page=page)
                check(shot_path is not None and shot_path.exists(), f"Screenshot successfully saved: {shot_path}")
                if shot_path and shot_path.exists():
                    shot_path.unlink()  # Clean up

            check(storage.exists(), "storage_state.json successfully serialized upon close()")
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                print(f"  [WARN] Playwright chromium binary not installed: {e}")
            else:
                raise

    test_section("4. Human-in-the-Loop & Anti-Bypass Forensics (R1, R2)")
    hitl = HitlHandler(interactive=False, audible_bell=False)

    # Test static detection of security challenges
    test_htmls = [
        ('<div class="login-mfa-active">MFA required</div>', True, "ZenClass MFA detected"),
        ('<div id="myModal"><div id="sendmail"></div></div>', True, "Guvi activation modal detected"),
        ('<div class="cf-turnstile">Cloudflare</div>', True, "Cloudflare turnstile detected"),
        ('<script src="https://www.google.com/recaptcha/api.js"></script>', True, "Google reCAPTCHA detected"),
        ('<html><body>Clean Page</body></html>', False, "Clean page does not falsely trigger"),
    ]
    for html_sample, expected, label in test_htmls:
        result = hitl.check_guardrails_in_html(html_sample)
        check(result == expected, f"HITL HTML check: {label} (got {result})")

    # Test URL validation for project links
    valid_test_urls = [
        "https://github.com/user/zenclass-capstone",
        "http://frontend.vercel.app",
        "https://backend.onrender.com/api",
        "ftp://archive.org/file.zip"
    ]
    for u in valid_test_urls:
        check(hitl.validate_url(u) is True, f"Valid URL accepted: {u}")

    invalid_test_urls = [
        "",
        "not-a-url",
        "javascript:alert(1)",
        "http://",
        "https://invalid url with spaces"
    ]
    for u in invalid_test_urls:
        check(hitl.validate_url(u) is False, f"Invalid URL rejected: {u}")

    test_section("5. Executive Summary Reporting Verification (R3)")
    with tempfile.TemporaryDirectory() as tmp_dir:
        rep_db = os.path.join(tmp_dir, "rep_test.db")
        rep_dir = os.path.join(tmp_dir, "reports")
        sm = StateManager(db_path=rep_db)

        # Seed realistic task distribution
        sm.record_task("p1", "guvi_codekata", "Task 1", "Easy", "", "completed", 1, "Solved!", "", time_spent_seconds=5.0)
        sm.record_task("p2", "guvi_codekata", "Task 2", "Hard", "", "completed", 2, "Solved!", "", time_spent_seconds=15.0)
        sm.record_task("p3", "zenclass_tasks", "Task 3", "JS", "", "pending", 0, "", "", time_spent_seconds=0.0)
        sm.record_task("p4", "zenclass_projects", "Project 1", "Capstone", "", "blocked", 1, "MFA", "MFA required", time_spent_seconds=2.0)
        sm.record_task("p5", "guvi_codekata", "Task 5", "Math", "", "failed", 3, "Timeout", "TLE", time_spent_seconds=30.0)

        reporter = SummaryReporter(state_manager=sm, report_dir=rep_dir)
        md_path, json_path = reporter.generate_all_reports()

        check(os.path.exists(md_path), f"SUMMARY_REPORT.md created at {md_path}")
        check(os.path.exists(json_path), f"summary.json created at {json_path}")

        # Check Markdown contents
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        check("Executive Summary" in md_text, "Markdown has 'Executive Summary'")
        check("Platform Breakdown Matrix" in md_text, "Markdown has 'Platform Breakdown Matrix'")
        check("🚨 Human Intervention Required" in md_text, "Markdown has 'Human Intervention Required' section")
        check("Category Breakdown" in md_text, "Markdown has 'Category Breakdown'")
        check("Project 1" in md_text, "Blocked task 'Project 1' listed under human intervention")
        check("MFA required" in md_text, "Failure reason 'MFA required' included")

        # Check JSON contents
        with open(json_path, "r", encoding="utf-8") as f:
            json_metrics = json.load(f)

        m = json_metrics["summary_metrics"]
        check(m["total_discovered"] == 5, f"total_discovered is 5 (got {m['total_discovered']})")
        check(m["total_completed"] == 2, f"total_completed is 2 (got {m['total_completed']})")
        check(m["total_pending"] == 1, f"total_pending is 1 (got {m['total_pending']})")
        check(m["total_blocked"] == 1, f"total_blocked is 1 (got {m['total_blocked']})")
        check(m["total_failed"] == 1, f"total_failed is 1 (got {m['total_failed']})")
        check(m["success_rate_percent"] == 40.0, f"success_rate_percent is 40.0 (got {m['success_rate_percent']})")
        check(m["total_time_spent_seconds"] == 52.0, f"total_time_spent_seconds is 52.0 (got {m['total_time_spent_seconds']})")
        check(len(json_metrics["human_intervention_issues"]) >= 1, "human_intervention_issues captured")

        sm.close()

    test_section("6. CLI Entrypoint End-to-End Execution")
    with tempfile.TemporaryDirectory() as tmp_dir:
        cli_db = os.path.join(tmp_dir, "cli_probe.db")
        cli_rep = os.path.join(tmp_dir, "cli_reports")

        # Run main.py report
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "main.py"),
            "--db-path", cli_db,
            "--reports-dir", cli_rep,
            "report"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        check(proc.returncode == 0, f"CLI 'report' command exited with code 0 (got {proc.returncode})")
        check(os.path.exists(os.path.join(cli_rep, "SUMMARY_REPORT.md")), "CLI generated SUMMARY_REPORT.md")
        check(os.path.exists(os.path.join(cli_rep, "summary.json")), "CLI generated summary.json")

    print("\n" + "=" * 60)
    print("ALL FORENSIC CHECKS PASSED WITH ZERO INTEGRITY VIOLATIONS")
    print("=" * 60)


if __name__ == "__main__":
    run_forensic_checks()
