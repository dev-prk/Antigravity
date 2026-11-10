"""
Tier 4 Real-World Workload Scenario 2: ZenClass Tasks Discovery and Dynamic Submission.
Simulates end-to-end task Kanban inspection, dynamic modal mapping, URL validation, and positive confirmation.
"""

import json
import re
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.contract_loader import get_state_manager
from tests.e2e.harness.dom_fixtures import (
    ZENCLASS_TASKS_HTML,
    ZENCLASS_SUBMISSION_MODAL_HTML
)


class TestWorkloadZenClassTasksE2E(unittest.TestCase):
    """Full workload simulation of autonomous ZenClass tasks completion."""

    def setUp(self):
        self.state_mgr, _ = get_state_manager(":memory:")

    def test_zenclass_tasks_discovery_and_submission_workflow(self):
        """End-to-end workflow: Kanban discovery -> Extract active/redo -> Populate URLs -> Submit -> Verify."""
        with MockPlatformServer() as server:
            # 1. Kanban Discovery: parse active and pending tasks
            card_matches = re.findall(
                r'id="individual-card" data-task-id="([^"]+)">(.*?)</div>\s*</div>',
                ZENCLASS_TASKS_HTML,
                re.DOTALL
            )
            discovered_tasks = []
            for t_id, card_html in card_matches:
                name_m = re.search(r'class="task-name">(.*?)<', card_html)
                is_redo = "Redo" in card_html
                is_completed = "common-score-text" in card_html

                status = "completed" if is_completed else ("redo" if is_redo else "pending")
                discovered_tasks.append((t_id, name_m.group(1).strip() if name_m else "Task", status))

            self.assertEqual(len(discovered_tasks), 3)

            # 2. Process actionable tasks (pending and redo)
            url_pattern = re.compile(r"^(ftp|http|https)://[^ \"]+$")

            for t_id, title, status in discovered_tasks:
                if status == "completed":
                    self.state_mgr.record_task(
                        task_id=t_id, platform="zenclass", title=title,
                        category="Tasks", url="", status="completed",
                        attempts=1, result="Evaluated 10/10", failure_reason="", next_action="none"
                    )
                    continue

                # Prepare dynamic submission payload
                submission_payload = {
                    "frontEnd_Deployed_Url": f"https://zenclass-{t_id}.netlify.app",
                    "github_Url": f"https://github.com/devsh/zenclass-{t_id}"
                }
                # Validate URLs against schema
                for field_name, url_val in submission_payload.items():
                    self.assertTrue(url_pattern.match(url_val), f"Invalid URL for {field_name}: {url_val}")

                # Submit to API
                api_url = f"{server.base_url()}/task/task-submit"
                payload = json.dumps({"submissionId": t_id, "submission": submission_payload}).encode("utf-8")
                req = urllib.request.Request(api_url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))

                self.assertEqual(resp_data["status"], "success")
                self.assertIn("Task Submitted Suceessfully", resp_data["message"])

                # Update state
                self.state_mgr.record_task(
                    task_id=t_id, platform="zenclass", title=title,
                    category="Tasks", url="", status="completed",
                    attempts=2 if status == "redo" else 1,
                    result="Submitted Successfully",
                    failure_reason="",
                    next_action="none",
                    metadata=submission_payload
                )

            # 3. Verify final state
            stats = self.state_mgr.get_summary_stats()
            self.assertEqual(stats["total_discovered"], 3)
            self.assertEqual(stats["total_completed"], 3)
            self.assertEqual(stats["total_pending"], 0)
            self.assertEqual(stats["success_rate_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
