"""
Tier 3 Pairwise Tests: Sandbox to Platform Submission and State Update.
Verifies validated code submission, positive platform feedback, and atomic state recording.
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.contract_loader import get_sandbox, get_state_manager
from tests.e2e.harness.mock_server import MockPlatformServer


class TestPairwiseSandboxToSubmissionVerify(unittest.TestCase):
    """Verifies that code passing the sandbox is submitted to platform and recorded in state database."""

    def setUp(self):
        self.sandbox, _ = get_sandbox()
        self.state_mgr, _ = get_state_manager(":memory:")

    def test_sandbox_validated_code_submission_lifecycle(self):
        """Pipeline: Sandbox check OK -> Submit API -> Confirm Solved -> StateManager record completed."""
        code = (
            "import sys\n"
            "def solve():\n"
            "    parts = sys.stdin.read().split()\n"
            "    print('odd' if (int(parts[0]) + int(parts[1])) % 2 != 0 else 'even')\n"
            "solve()\n"
        )
        # 1. Sandbox verification
        sandbox_res = self.sandbox.validate_solution(code, "9 2", "odd")
        self.assertTrue(sandbox_res.passed)

        # 2. Submit to platform API
        with MockPlatformServer() as server:
            submit_url = f"{server.base_url()}/code-kata/question/submit"
            payload = json.dumps({"question_id": 1, "code": code}).encode("utf-8")
            req = urllib.request.Request(submit_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["message"], "Solved!")
            self.assertTrue(data["completed"])

            # 3. Update persistent state
            self.state_mgr.record_task(
                task_id="codekata-1",
                platform="guvi",
                title="1. Odd or Even Sum",
                category="CodeKata",
                url="https://guvi.in/code-kata/odd-or-even-sum",
                status="completed",
                attempts=1,
                result="Solved!",
                failure_reason="",
                next_action="none",
                metadata={"earned_points": data["earned_points"]}
            )

        # 4. Verify record in state database
        task = self.state_mgr.get_task("codekata-1")
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.attempts, 1)
        self.assertEqual(task.metadata["earned_points"], 30)


if __name__ == "__main__":
    unittest.main()
