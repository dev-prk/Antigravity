"""
Test Feature 4: Reporting Engine.
Verifies generation of executive Markdown report (reports/SUMMARY_REPORT.md) and machine-readable JSON metrics.
"""

import json
import os
import shutil
import tempfile
import unittest

from tests.e2e.harness.contract_loader import get_reporter
from tests.e2e.harness.reference_oracle import TaskRecord


class TestFeature04Reporter(unittest.TestCase):
    """Verifies Reporting Engine specifications from PROJECT.md §Feature 4 & ORIGINAL_REQUEST §R3."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.reporter, self.source = get_reporter()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_markdown_and_json_reports(self):
        """Authoritative source: ORIGINAL_REQUEST §R3 & PROJECT.md §13."""
        stats = {
            "total_discovered": 10,
            "total_completed": 8,
            "total_pending": 1,
            "total_blocked": 1,
            "success_rate_percent": 80.0
        }
        tasks = [
            TaskRecord("t1", "guvi", "Prob 1", "CodeKata", "url1", "completed", 1, "Solved!", "", ""),
            TaskRecord("t2", "zenclass", "Task 1", "Tasks", "url2", "blocked", 2, "Failed", "MFA required", "prompt_user")
        ]

        reports = self.reporter.generate_report(stats, tasks, output_dir=self.temp_dir)
        md_file = reports["markdown"]
        json_file = reports["json"]

        self.assertTrue(os.path.exists(md_file))
        self.assertTrue(os.path.exists(json_file))

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# Automation Execution Summary Report", content)
        self.assertIn("Total Discovered**: 10", content)
        self.assertIn("Success Rate**: 80.0%", content)
        self.assertIn("Prob 1", content)

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["metrics"]["total_completed"], 8)
        self.assertEqual(len(data["tasks"]), 2)


if __name__ == "__main__":
    unittest.main()
