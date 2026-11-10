"""
Test Feature 2: Persistent State Manager.
Verifies SQLite tracking database, task recording, atomic state JSON export, and summary statistics.
"""

import json
import os
import tempfile
import unittest

from tests.e2e.harness.contract_loader import get_state_manager


class TestFeature02StateManager(unittest.TestCase):
    """Verifies Persistent State Manager specifications from PROJECT.md §Feature 2 & ORIGINAL_REQUEST §R3."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_state.db")
        self.state_mgr, self.source = get_state_manager(self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_record_and_get_task(self):
        """Authoritative source: PROJECT.md §Interface Contracts - record_task and get_task."""
        self.state_mgr.record_task(
            task_id="codekata-1",
            platform="guvi",
            title="1. Odd or Even Sum",
            category="CodeKata",
            url="https://www.guvi.in/code-kata/odd-or-even-sum/",
            status="completed",
            attempts=1,
            result="Solved!",
            failure_reason="",
            next_action="none",
            metadata={"points": 30, "difficulty": "Easy"}
        )

        task = self.state_mgr.get_task("codekata-1")
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, "codekata-1")
        self.assertEqual(task.platform, "guvi")
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.attempts, 1)
        self.assertEqual(task.result, "Solved!")
        self.assertEqual(task.metadata.get("points"), 30)

    def test_get_pending_tasks_filtering(self):
        """Verifies pending and redo tasks are retrieved while completed tasks are filtered out."""
        self.state_mgr.record_task(
            task_id="task-101",
            platform="zenclass",
            title="Day 1: JS Basics",
            category="Tasks",
            url="https://v2.zenclass.in/tasks",
            status="completed",
            attempts=1,
            result="Success",
            failure_reason="",
            next_action="none"
        )
        self.state_mgr.record_task(
            task_id="task-102",
            platform="zenclass",
            title="Day 2: Async Await",
            category="Tasks",
            url="https://v2.zenclass.in/tasks",
            status="pending",
            attempts=0,
            result="Unattempted",
            failure_reason="",
            next_action="solve"
        )
        self.state_mgr.record_task(
            task_id="task-103",
            platform="zenclass",
            title="Day 3: Fetch API",
            category="Tasks",
            url="https://v2.zenclass.in/tasks",
            status="redo",
            attempts=1,
            result="Needs fixes",
            failure_reason="Failed test 2",
            next_action="resubmit"
        )

        pending = self.state_mgr.get_pending_tasks("zenclass")
        self.assertEqual(len(pending), 2)
        ids = [t.task_id for t in pending]
        self.assertIn("task-102", ids)
        self.assertIn("task-103", ids)
        self.assertNotIn("task-101", ids)

    def test_summary_statistics_calculation(self):
        """Verifies correct calculation of total, completed, pending, blocked, and success rate."""
        self.state_mgr.record_task("t1", "guvi", "Prob 1", "CodeKata", "", "completed", 1, "OK", "", "")
        self.state_mgr.record_task("t2", "guvi", "Prob 2", "CodeKata", "", "completed", 1, "OK", "", "")
        self.state_mgr.record_task("t3", "guvi", "Prob 3", "CodeKata", "", "pending", 0, "", "", "")
        self.state_mgr.record_task("t4", "zenclass", "Task 1", "Tasks", "", "blocked", 2, "Fail", "MFA required", "prompt_user")

        stats = self.state_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 4)
        self.assertEqual(stats["total_completed"], 2)
        self.assertEqual(stats["total_pending"], 1)
        self.assertEqual(stats["total_blocked"], 1)
        self.assertEqual(stats["success_rate_percent"], 50.0)

    def test_export_state_json_file(self):
        """Authoritative source: PROJECT.md §6 - atomic JSON export data/state_summary.json."""
        self.state_mgr.record_task("t1", "guvi", "Prob 1", "CodeKata", "", "completed", 1, "OK", "", "")
        export_file = os.path.join(self.temp_dir, "state_summary.json")
        out_path = self.state_mgr.export_state_json(export_file)

        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("summary", data)
        self.assertIn("tasks", data)
        self.assertEqual(data["summary"]["total_completed"], 1)


if __name__ == "__main__":
    unittest.main()
