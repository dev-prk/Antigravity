"""
Test Feature 9: Guvi Authentication.
Verifies login form submission, credential verification via usercheck.php, and session cookies.
"""

import json
import unittest
import urllib.request
from tests.e2e.harness.mock_server import MockPlatformServer
from tests.e2e.harness.dom_fixtures import GUVI_LOGIN_HTML


class TestFeature09GuviAuth(unittest.TestCase):
    """Verifies Guvi Authentication specifications from PROJECT.md §Feature 9 & spec_miner_survey_2 §1.1."""

    def test_login_form_selectors_present(self):
        """Authoritative source: spec_miner_survey_2 §1.1."""
        self.assertIn('id="email"', GUVI_LOGIN_HTML)
        self.assertIn('id="password"', GUVI_LOGIN_HTML)
        self.assertIn('id="logged-in"', GUVI_LOGIN_HTML)
        self.assertIn('id="login-btn"', GUVI_LOGIN_HTML)
        self.assertIn('class="invalid-feedback"', GUVI_LOGIN_HTML)

    def test_valid_credentials_authentication(self):
        """Authoritative source: ORIGINAL_REQUEST §Reference Material - devsh.pareek@gmail.com / Dev@99#$%esh."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/usercheck.php"
            payload = json.dumps({
                "emails": "devsh.pareek@gmail.com",
                "password": "Dev@99#$%esh",
                "loggedInType": "loggedInUser"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            self.assertEqual(data["status"], "success")
            self.assertTrue(data["authToken"].startswith("auth:"))
            self.assertEqual(data["cusername"], "Devesh Pareek")
            self.assertGreaterEqual(data["userpoints"], 0)

    def test_invalid_credentials_rejected(self):
        """Verifies 401 error and failure message for invalid password."""
        with MockPlatformServer() as server:
            url = f"{server.base_url()}/usercheck.php"
            payload = json.dumps({
                "emails": "devsh.pareek@gmail.com",
                "password": "wrong_password",
                "loggedInType": "loggedInUser"
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req)
                self.fail("Expected HTTPError 401 on invalid credentials")
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 401)
                data = json.loads(e.read().decode("utf-8"))
                self.assertEqual(data["status"], "fail")
                self.assertIn("Incorrect Email or Password", data["message"])


if __name__ == "__main__":
    unittest.main()
