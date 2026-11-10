"""
Tier 3 Pairwise Tests: HITL Guardrail Trigger to Pause, Resolution, and State Transition.
Verifies state lifecycle during human intervention: in_progress -> blocked -> user input -> completed.
"""

import unittest
from tests.e2e.harness.contract_loader import get_hitl_handler, get_state_manager


class TestPairwiseHITLPauseResumeState(unittest.TestCase):
    """Verifies that encountering guardrails updates task status to blocked, pauses, and resumes cleanly."""

    def setUp(self):
        self.hitl, _ = get_hitl_handler()
        self.state_mgr, _ = get_state_manager(":memory:")

    def test_hitl_guardrail_lifecycle_and_state_transitions(self):
        """Flow: Start task -> Guardrail detected -> Record blocked -> User solves -> Resume & complete."""
        task_id = "zen-proj-501"
        # 1. Start task
        self.state_mgr.record_task(
            task_id=task_id,
            platform="zenclass",
            title="E-Commerce Project",
            category="Projects",
            url="https://v2.zenclass.in/projects",
            status="in_progress",
            attempts=1,
            result="Building local code",
            failure_reason="",
            next_action="build"
        )
        task = self.state_mgr.get_task(task_id)
        self.assertEqual(task.status, "in_progress")

        # 2. Guardrail detected (need human deployment URLs)
        self.state_mgr.record_task(
            task_id=task_id,
            platform="zenclass",
            title="E-Commerce Project",
            category="Projects",
            url="https://v2.zenclass.in/projects",
            status="blocked",
            attempts=1,
            result="Awaiting user links",
            failure_reason="Human deployment URL required",
            next_action="prompt_user"
        )
        task = self.state_mgr.get_task(task_id)
        self.assertEqual(task.status, "blocked")

        # 3. User supplies URLs via HITL handler
        mock_input = {
            "github_Url": "https://github.com/user/zen-ecommerce",
            "frontEnd_Deployed_Url": "https://zen-ecommerce.netlify.app"
        }
        collected = self.hitl.request_project_links(
            project_title=task.title,
            project_id=task_id,
            local_code_dir="/mock/dir",
            required_fields=["github_Url", "frontEnd_Deployed_Url"],
            user_inputs=mock_input
        )
        self.assertTrue(len(collected["github_Url"]) > 0)

        # 4. Resume and finalize submission
        self.state_mgr.record_task(
            task_id=task_id,
            platform="zenclass",
            title="E-Commerce Project",
            category="Projects",
            url="https://v2.zenclass.in/projects",
            status="completed",
            attempts=1,
            result="Submitted Successfully",
            failure_reason="",
            next_action="none",
            metadata=collected
        )
        task = self.state_mgr.get_task(task_id)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.metadata["github_Url"], "https://github.com/user/zen-ecommerce")


if __name__ == "__main__":
    unittest.main()
