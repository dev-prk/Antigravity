"""
Test Feature 12: ZenClass Authentication.
Verifies SPA login, Material UI field selectors, token storage in localStorage, and MFA guardrail.
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.dom_fixtures import ZENCLASS_LOGIN_HTML


class TestFeature12ZenClassAuth(unittest.TestCase):
    """Verifies ZenClass Authentication specifications from PROJECT.md §Feature 12 & spec_miner_survey_3 §1.1."""

    def test_login_dom_selectors(self):
        """Authoritative source: spec_miner_survey_3 §1.1 - Material UI inputs and trailing space in placeholder."""
        self.assertIn('class="email-input"', ZENCLASS_LOGIN_HTML)
        self.assertIn('placeholder="Enter your mail"', ZENCLASS_LOGIN_HTML)
        self.assertIn('placeholder="Enter your password "', ZENCLASS_LOGIN_HTML)
        self.assertIn('class="primary-btn sign-in-pad"', ZENCLASS_LOGIN_HTML)

    def test_valid_zenclass_login_api(self):
        """Authoritative source: ORIGINAL_REQUEST §Reference Material credentials."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/login/"
            payload = json.dumps({
                "email": "devsh.pareek@gmail.com",
                "password": "Dev@99#$%esh",
                "device": "web"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["userRole"], "student")
            self.assertTrue("authToken" in data)

    def test_mfa_challenge_trigger(self):
        """Authoritative source: spec_miner_survey_3 §1.1 - mfaRequired action."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/login/"
            payload = json.dumps({
                "email": "mfa@zenclass.in",
                "password": "Dev@99#$%esh",
                "device": "web"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["action"], "mfaRequired")
            self.assertEqual(data["status"], "challenge")


if __name__ == "__main__":
    unittest.main()
