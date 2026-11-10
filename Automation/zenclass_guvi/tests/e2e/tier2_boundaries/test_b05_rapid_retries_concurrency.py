"""
Tier 2 Boundary Tests: Rapid Retries and Concurrency.
Verifies rapid sequential updates, retry counters, and transactional consistency in SQLite state.
"""

import threading
import unittest
from tests.e2e.harness.contract_loader import get_state_manager


class TestBoundaryRapidRetriesConcurrency(unittest.TestCase):
    """Verifies state manager behavior during rapid retries and multi-threaded operations."""

    def setUp(self):
        self.state_mgr, _ = get_state_manager(":memory:")

    def test_rapid_task_retry_counter_updates(self):
        """Verifies rapid sequential updates to the same task properly increment attempt count."""
        task_id = "retry-task-001"
        for attempt in range(1, 10):
            self.state_mgr.record_task(
                task_id=task_id,
                platform="guvi",
                title="Retry Problem",
                category="CodeKata",
                url="https://guvi.in/test",
                status="pending" if attempt < 9 else "completed",
                attempts=attempt,
                result=f"Attempt {attempt}",
                failure_reason=f"Error {attempt}" if attempt < 9 else "",
                next_action="retry" if attempt < 9 else "none"
            )

        task = self.state_mgr.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.attempts, 9)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.result, "Attempt 9")

    def test_concurrent_task_insertions(self):
        """Verifies concurrent threads inserting different tasks do not corrupt database."""
        errors = []

        def worker(thread_idx: int):
            try:
                for i in range(10):
                    t_id = f"thread_{thread_idx}_task_{i}"
                    self.state_mgr.record_task(
                        task_id=t_id,
                        platform="zenclass",
                        title=f"Task {i}",
                        category="Tasks",
                        url="",
                        status="completed",
                        attempts=1,
                        result="OK",
                        failure_reason="",
                        next_action="none"
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent database writes raised errors: {errors}")
        stats = self.state_mgr.get_summary_stats()
        self.assertEqual(stats["total_discovered"], 40)
        self.assertEqual(stats["total_completed"], 40)


if __name__ == "__main__":
    unittest.main()
