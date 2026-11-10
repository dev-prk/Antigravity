"""
Tier 4 Real-World Workload Scenario 1: Multi-Problem Solving on Guvi CodeKata.
Simulates end-to-end discovery, completed filtering, multi-problem solving, sandboxing, submit, and state persistence.
"""

import json
import re
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.contract_loader import (
    get_state_manager,
    get_sandbox,
    get_code_generator
)
from tests.e2e.harness.reference_oracle import CANONICAL_PROBLEMS
from tests.e2e.harness.dom_fixtures import GUVI_CODEKATA_TABLE_HTML


class TestWorkloadGuviCodeKataE2E(unittest.TestCase):
    """Full workload simulation of autonomous Guvi CodeKata problem completion."""

    def setUp(self):
        self.state_mgr, _ = get_state_manager(":memory:")
        self.sandbox, _ = get_sandbox()
        self.code_gen, _ = get_code_generator()

    def test_multi_problem_guvi_codekata_workflow(self):
        """End-to-end workload: Login -> Table discovery -> Filter solved -> Solve 3 pending -> Submit & Record."""
        with MockPlatformServer() as server:
            # 1. Login
            login_url = f"{server.base_url()}/usercheck.php"
            login_payload = json.dumps({
                "emails": "devsh.pareek@gmail.com",
                "password": "Dev@99#$%esh",
                "loggedInType": "loggedInUser"
            }).encode("utf-8")
            req = urllib.request.Request(login_url, data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                auth = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(auth["status"], "success")

            # 2. Discover problems from catalog table
            rows = re.findall(
                r'<tr class="cursor-pointer" data-slug="([^"]+)">(.*?)</tr>',
                GUVI_CODEKATA_TABLE_HTML,
                re.DOTALL
            )
            # Filter already solved vs pending
            pending_problems = []
            for slug, row_html in rows:
                if "#completed-icon_svg__a" in row_html:
                    # Record already completed in state
                    self.state_mgr.record_task(
                        task_id=f"guvi-{slug}",
                        platform="guvi",
                        title=slug.replace("-", " ").title(),
                        category="CodeKata",
                        url=f"https://guvi.in/code-kata/{slug}",
                        status="completed",
                        attempts=1,
                        result="Already Solved",
                        failure_reason="",
                        next_action="none"
                    )
                else:
                    pending_problems.append(slug)

            self.assertEqual(len(pending_problems), 3)

            # 3. Solve each pending problem sequentially
            for slug in pending_problems:
                self.assertIn(slug, CANONICAL_PROBLEMS)
                prob_data = CANONICAL_PROBLEMS[slug]

                # Synthesize code
                code = self.code_gen(slug)

                # Validate in sandbox against sample I/O
                sample_test = prob_data["test_vectors"][0]
                val_result = self.sandbox.validate_solution(
                    code,
                    sample_test["input"],
                    sample_test["expected"]
                )
                self.assertTrue(val_result.passed, f"Sandbox failed for {slug}: {val_result.error_message}")

                # Submit to platform
                submit_url = f"{server.base_url()}/code-kata/question/submit"
                payload = json.dumps({"question_id": slug, "code": code}).encode("utf-8")
                req = urllib.request.Request(submit_url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req) as resp:
                    sub_resp = json.loads(resp.read().decode("utf-8"))

                self.assertTrue(sub_resp["completed"])
                self.assertEqual(sub_resp["message"], "Solved!")

                # Record completion in state
                self.state_mgr.record_task(
                    task_id=f"guvi-{slug}",
                    platform="guvi",
                    title=prob_data["title"],
                    category="CodeKata",
                    url=f"https://guvi.in/code-kata/{slug}",
                    status="completed",
                    attempts=1,
                    result="Solved!",
                    failure_reason="",
                    next_action="none",
                    metadata={"points": sub_resp["earned_points"]}
                )

            # 4. Verify overall state
            stats = self.state_mgr.get_summary_stats()
            self.assertEqual(stats["total_discovered"], 5)
            self.assertEqual(stats["total_completed"], 5)
            self.assertEqual(stats["total_pending"], 0)
            self.assertEqual(stats["success_rate_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
