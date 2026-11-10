"""
Tier 3 Pairwise Tests: State Persistence Across Runner Runs.
Verifies that subsequent runs reload existing SQLite state, skip completed tasks, and process remaining pending items.
"""

import os
import shutil
import tempfile
import unittest
from tests.e2e.harness.contract_loader import get_state_manager


class TestPairwiseStatePersistenceAcrossRuns(unittest.TestCase):
    """Verifies that state is maintained across process terminations and restarts."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "persistent_state.db")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rerun_skips_completed_and_resumes_pending(self):
        """Run 1 completes problem 1 and leaves problem 2 pending. Run 2 reads state and executes problem 2 only."""
        # --- Run 1 ---
        run1_mgr, _ = get_state_manager(self.db_path)
        run1_mgr.record_task(
            task_id="p-1",
            platform="guvi",
            title="Problem 1",
            category="CodeKata",
            url="",
            status="completed",
            attempts=1,
            result="Solved!",
            failure_reason="",
            next_action="none"
        )
        run1_mgr.record_task(
            task_id="p-2",
            platform="guvi",
            title="Problem 2",
            category="CodeKata",
            url="",
            status="pending",
            attempts=0,
            result="Unattempted",
            failure_reason="",
            next_action="solve"
        )
        # Process terminates (run1_mgr out of scope)

        # --- Run 2 (Process Restart) ---
        run2_mgr, _ = get_state_manager(self.db_path)
        # Check pending tasks
        pending = run2_mgr.get_pending_tasks("guvi")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].task_id, "p-2")

        # Complete pending task
        run2_mgr.record_task(
            task_id="p-2",
            platform="guvi",
            title="Problem 2",
            category="CodeKata",
            url="",
            status="completed",
            attempts=1,
            result="Solved!",
            failure_reason="",
            next_action="none"
        )

        # --- Verification ---
        stats = run2_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 2)
        self.assertEqual(stats["total_completed"], 2)
        self.assertEqual(stats["total_pending"], 0)
        self.assertEqual(stats["success_rate_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
