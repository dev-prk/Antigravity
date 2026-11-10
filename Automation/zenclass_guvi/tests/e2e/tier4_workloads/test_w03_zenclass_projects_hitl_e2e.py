"""
Tier 4 Real-World Workload Scenario 3: ZenClass Projects with Human-in-the-Loop Pause Protocol.
Simulates end-to-end 5-stage lifecycle: Discovery -> Local Code Synthesis -> Local Build -> Human Pause -> Submission.
"""

import json
import os
import shutil
import tempfile
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.contract_loader import get_state_manager, get_hitl_handler


class TestWorkloadZenClassProjectsHITLE2E(unittest.TestCase):
    """Full workload simulation of ZenClass project synthesis, local build, HITL pause, and submission."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_mgr, _ = get_state_manager(":memory:")
        self.hitl, _ = get_hitl_handler()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_five_stage_project_hitl_workflow(self):
        """Executes full 5-stage protocol required by ORIGINAL_REQUEST §R2 & spec_miner_survey_3 §140-167."""
        with MockPlatformServer() as server:
            # Stage 1: Discovery & Parsing
            project_id = "proj-501"
            project_title = "Full Stack E-Commerce Platform"
            required_links = ["github_Url", "frontEnd_Deployed_Url"]

            self.state_mgr.record_task(
                task_id=project_id,
                platform="zenclass",
                title=project_title,
                category="Projects",
                url="https://v2.zenclass.in/projects",
                status="in_progress",
                attempts=1,
                result="Synthesizing local code",
                failure_reason="",
                next_action="synthesis"
            )

            # Stage 2: Local Code Synthesis in projects/<slug>/
            slug = "fullstack-ecommerce"
            local_proj_dir = os.path.join(self.temp_dir, slug)
            os.makedirs(os.path.join(local_proj_dir, "client", "src"), exist_ok=True)
            os.makedirs(os.path.join(local_proj_dir, "server"), exist_ok=True)

            with open(os.path.join(local_proj_dir, "README.md"), "w") as f:
                f.write(f"# {project_title}\n\nFull stack capstone application.")

            with open(os.path.join(local_proj_dir, "client", "package.json"), "w") as f:
                json.dump({"name": "ecommerce-client", "version": "1.0.0"}, f)

            with open(os.path.join(local_proj_dir, "server", "package.json"), "w") as f:
                json.dump({"name": "ecommerce-server", "version": "1.0.0"}, f)

            # Stage 3: Local Test & Build Verification
            self.assertTrue(os.path.exists(os.path.join(local_proj_dir, "README.md")))
            with open(os.path.join(local_proj_dir, "client", "package.json")) as f:
                client_pkg = json.load(f)
            self.assertEqual(client_pkg["name"], "ecommerce-client")

            # Stage 4: Interactive Human Pause Protocol
            # Record state as blocked waiting for user
            self.state_mgr.record_task(
                task_id=project_id,
                platform="zenclass",
                title=project_title,
                category="Projects",
                url="https://v2.zenclass.in/projects",
                status="blocked",
                attempts=1,
                result="Awaiting user repository and deployment URLs",
                failure_reason="Human-in-the-loop input required",
                next_action="prompt_user"
            )

            task_blocked = self.state_mgr.get_task(project_id)
            self.assertEqual(task_blocked.status, "blocked")

            # Simulate user providing the links at the pause prompt
            user_links = {
                "github_Url": "https://github.com/devsh/ecommerce-capstone",
                "frontEnd_Deployed_Url": "https://ecommerce-capstone.vercel.app"
            }
            collected_links = self.hitl.request_project_links(
                project_title=project_title,
                project_id=project_id,
                local_code_dir=local_proj_dir,
                required_fields=required_links,
                user_inputs=user_links
            )
            self.assertEqual(collected_links["github_Url"], user_links["github_Url"])

            # Stage 5: Submission & Verification
            submit_url = f"{server.base_url()}/projects/submit-project"
            payload = json.dumps({"submissionId": project_id, "submission": collected_links}).encode("utf-8")
            req = urllib.request.Request(submit_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertIn("Project submitted successfully", data["message"])

            # Record final completed state
            self.state_mgr.record_task(
                task_id=project_id,
                platform="zenclass",
                title=project_title,
                category="Projects",
                url="https://v2.zenclass.in/projects",
                status="completed",
                attempts=1,
                result="Submitted successfully",
                failure_reason="",
                next_action="none",
                metadata=collected_links
            )

            final_task = self.state_mgr.get_task(project_id)
            self.assertEqual(final_task.status, "completed")
            self.assertEqual(final_task.metadata["github_Url"], "https://github.com/devsh/ecommerce-capstone")


if __name__ == "__main__":
    unittest.main()
