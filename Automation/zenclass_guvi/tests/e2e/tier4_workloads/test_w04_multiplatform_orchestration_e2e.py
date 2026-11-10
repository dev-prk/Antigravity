"""
Tier 4 Real-World Workload Scenario 4: Multi-Platform Orchestration and Executive Reporting.
Simulates comprehensive orchestration across Guvi and ZenClass with executive report generation.
"""

import json
import os
import shutil
import tempfile
import unittest
from tests.e2e.harness.contract_loader import get_state_manager, get_reporter


class TestWorkloadMultiplatformOrchestrationE2E(unittest.TestCase):
    """Full workload simulation of multi-platform execution and reporting."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "orchestration_state.db")
        self.reports_dir = os.path.join(self.temp_dir, "reports")
        self.state_mgr, _ = get_state_manager(self.db_path)
        self.reporter, _ = get_reporter()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_orchestration_and_reporting_lifecycle(self):
        """End-to-end multiplatform run: Process Guvi + ZenClass -> Export State JSON -> Generate Executive Report."""
        # 1. Populate tasks across platforms
        tasks_data = [
            ("guvi-p1", "guvi", "Odd or Even Sum", "CodeKata", "completed", "Solved!"),
            ("guvi-p2", "guvi", "Reverse String", "CodeKata", "completed", "Solved!"),
            ("guvi-p3", "guvi", "Sum of Array", "CodeKata", "completed", "Solved!"),
            ("zen-t101", "zenclass", "Day 1 Functions", "Tasks", "completed", "Submitted"),
            ("zen-t102", "zenclass", "Day 2 Async", "Tasks", "completed", "Submitted"),
            ("zen-p501", "zenclass", "Fullstack App", "Projects", "completed", "Submitted with Links"),
            ("zen-t103", "zenclass", "Day 3 Auth MFA", "Tasks", "blocked", "MFA Challenge active"),
        ]

        for t_id, platform, title, cat, status, res in tasks_data:
            self.state_mgr.record_task(
                task_id=t_id,
                platform=platform,
                title=title,
                category=cat,
                url=f"https://{platform}.platform/task/{t_id}",
                status=status,
                attempts=1,
                result=res,
                failure_reason="MFA Challenge" if status == "blocked" else "",
                next_action="prompt_user" if status == "blocked" else "none"
            )

        # 2. Get stats and export state JSON
        stats = self.state_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 7)
        self.assertEqual(stats["total_completed"], 6)
        self.assertEqual(stats["total_pending"], 0)
        self.assertEqual(stats["total_blocked"], 1)
        self.assertAlmostEqual(stats["success_rate_percent"], 85.71, places=1)

        json_export = self.state_mgr.export_state_json(os.path.join(self.temp_dir, "state_summary.json"))
        self.assertTrue(os.path.exists(json_export))

        # 3. Generate Executive Reports
        pending_and_completed = [self.state_mgr.get_task(t[0]) for t in tasks_data]
        reports = self.reporter.generate_report(stats, pending_and_completed, output_dir=self.reports_dir)
        md_report = reports["markdown"]
        json_report = reports["json"]

        self.assertTrue(os.path.exists(md_report))
        self.assertTrue(os.path.exists(json_report))

        with open(md_report, "r", encoding="utf-8") as f:
            md_text = f.read()
        self.assertIn("# Automation Execution Summary Report", md_text)
        self.assertIn("Total Discovered**: 7", md_text)
        self.assertIn("Total Completed**: 6", md_text)
        self.assertIn("Total Blocked**: 1", md_text)
        self.assertIn("Success Rate**: 85.71%", md_text)
        self.assertIn("guvi-p1", md_text)
        self.assertIn("zen-p501", md_text)

        with open(json_report, "r", encoding="utf-8") as f:
            json_metrics = json.load(f)
        self.assertEqual(json_metrics["metrics"]["total_completed"], 6)
        self.assertEqual(len(json_metrics["tasks"]), 7)


if __name__ == "__main__":
    unittest.main()
