"""
Tier 3 Pairwise Tests: Auth to Problem / Task Discovery.
Verifies seamless handover from authenticated session to catalog discovery on Guvi and ZenClass.
"""

import json
import re
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer


class TestPairwiseAuthToDiscovery(unittest.TestCase):
    """Verifies that authentication establishes sessions that successfully access discovery catalogs."""

    def test_guvi_auth_then_codekata_discovery(self):
        """Pairwise flow: Guvi login -> session cookies -> fetch CodeKata table -> discover pending problems."""
        with MockPlatformServer() as server:
            # Step 1: Authenticate
            login_url = f"{server.base_url()}/usercheck.php"
            login_payload = json.dumps({
                "emails": "devsh.pareek@gmail.com",
                "password": "Dev@99#$%esh",
                "loggedInType": "loggedInUser"
            }).encode("utf-8")
            req = urllib.request.Request(login_url, data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                auth_data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(auth_data["status"], "success")
            auth_token = auth_data["authToken"]

            # Step 2: Access catalog with session cookie
            catalog_url = f"{server.base_url()}/code-kata/"
            catalog_req = urllib.request.Request(catalog_url, headers={"Cookie": f"authToken={auth_token}"})
            with urllib.request.urlopen(catalog_req) as resp:
                catalog_html = resp.read().decode("utf-8")

            # Step 3: Discover pending problems
            rows = re.findall(r'<tr class="cursor-pointer" data-slug="([^"]+)">(.*?)</tr>', catalog_html, re.DOTALL)
            pending = [slug for slug, html in rows if "#completed-icon_svg__a" not in html]
            self.assertGreater(len(pending), 0)
            self.assertIn("reverse-a-string", pending)

    def test_zenclass_auth_then_tasks_discovery(self):
        """Pairwise flow: ZenClass login -> JWT token -> fetch Tasks Kanban -> discover active/pending tasks."""
        with MockPlatformServer() as server:
            # Step 1: Authenticate
            login_url = f"{server.base_url()}/login/"
            login_payload = json.dumps({
                "email": "devsh.pareek@gmail.com",
                "password": "Dev@99#$%esh",
                "device": "web"
            }).encode("utf-8")
            req = urllib.request.Request(login_url, data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                auth_data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(auth_data["status"], "success")
            jwt_token = auth_data["authToken"]

            # Step 2: Access tasks board
            tasks_url = f"{server.base_url()}/tasks"
            tasks_req = urllib.request.Request(tasks_url, headers={"Authorization": f"Bearer {jwt_token}"})
            with urllib.request.urlopen(tasks_req) as resp:
                tasks_html = resp.read().decode("utf-8")

            # Step 3: Inspect active tasks count
            count_match = re.search(r'class="active-tasks-count">(\d+)<', tasks_html)
            self.assertIsNotNone(count_match)
            self.assertGreater(int(count_match.group(1)), 0)


if __name__ == "__main__":
    unittest.main()
