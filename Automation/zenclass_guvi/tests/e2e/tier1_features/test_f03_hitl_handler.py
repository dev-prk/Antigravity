"""
Test Feature 3: Human-in-the-Loop Handler.
Verifies detection of CAPTCHA, Cloudflare Turnstile, OTP, MFA (.login-mfa-active), and project link prompts.
"""

import unittest
from tests.e2e.harness.contract_loader import get_hitl_handler
from tests.e2e.harness.dom_fixtures import (
    GUVI_LOGIN_HTML,
    ZENCLASS_LOGIN_HTML
)


class TestFeature03HITLHandler(unittest.TestCase):
    """Verifies Human-in-the-Loop Handler specifications from PROJECT.md §Feature 3 & ORIGINAL_REQUEST §R1."""

    def setUp(self):
        self.hitl, self.source = get_hitl_handler()

    def test_detects_mfa_active_in_zenclass(self):
        """Authoritative source: spec_miner_survey_3 §1.1 - class .login-mfa-active."""
        mfa_html = '<div class="login-content-wrapper login-mfa-wrapper login-mfa-active">MFA Challenge</div>'
        self.assertTrue(self.hitl.check_guardrails_in_html(mfa_html))

    def test_detects_activation_modal_in_guvi(self):
        """Authoritative source: spec_miner_survey_2 §1.1 - modal #myModal sendmail."""
        modal_html = '<div id="myModal" class="modal"><button id="sendmail">Resend</button></div>'
        self.assertTrue(self.hitl.check_guardrails_in_html(modal_html))

    def test_detects_cloudflare_turnstile_and_recaptcha(self):
        """Authoritative source: spec_miner_survey_2 §Table 1 Feature 18."""
        cf_html = '<div class="cf-turnstile" data-sitekey="0x4AAAAAA..."></div>'
        recaptcha_html = '<script src="https://www.google.com/recaptcha/api.js?render=6LdADb4UAAAAAA1feb36sozffPYRKKOqD9WPbibp"></script>'
        self.assertTrue(self.hitl.check_guardrails_in_html(cf_html))
        self.assertTrue(self.hitl.check_guardrails_in_html(recaptcha_html))

    def test_clean_pages_do_not_trigger_hitl(self):
        """Verifies clean login pages without challenge do not false-positive trigger HITL."""
        self.assertFalse(self.hitl.check_guardrails_in_html(ZENCLASS_LOGIN_HTML))

    def test_request_project_links_prompt(self):
        """Authoritative source: PROJECT.md §Interface Contracts - request_project_links."""
        mock_user_input = {
            "github_Url": "https://github.com/testuser/zen-capstone",
            "frontEnd_Deployed_Url": "https://zen-capstone.netlify.app"
        }
        res = self.hitl.request_project_links(
            project_title="Full Stack App",
            project_id="proj-501",
            local_code_dir="/mock/projects/full-stack-app",
            required_fields=["github_Url", "frontEnd_Deployed_Url"],
            user_inputs=mock_user_input
        )
        self.assertEqual(res["github_Url"], "https://github.com/testuser/zen-capstone")
        self.assertEqual(res["frontEnd_Deployed_Url"], "https://zen-capstone.netlify.app")


if __name__ == "__main__":
    unittest.main()
