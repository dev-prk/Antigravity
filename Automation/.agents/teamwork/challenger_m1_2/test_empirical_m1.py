"""
Empirical Verification & Adversarial Stress Harness for Milestone 1
Targeting:
- BrowserManager (anti-detection, headed mode compliance R1, tab reuse, session serialization)
- HitlHandler (guardrail detection across DOM variations, false-positive resistance, URL validation)
- Config (R1 compliance, timeouts, browser args)
"""

import sys
import os
import json
import tempfile
import shutil
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.browser import BrowserManager
from core.hitl_handler import HitlHandler, GuardrailType, GuardrailEvent


class TestBrowserManagerEmpirical(unittest.TestCase):
    """Empirical verification of BrowserManager anti-detection, tab reuse, and session serialization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="challenger_bm_")
        self.profile_dir = Path(self.temp_dir) / ".browser_profile"
        self.storage_state_file = Path(self.temp_dir) / "storage_state.json"

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_r1_headed_default_compliance(self):
        """Verify BrowserManager defaults strictly to headed foreground execution (R1)."""
        # 1. Config level check
        self.assertFalse(config.HEADLESS, "config.HEADLESS must be False strictly adhering to R1")
        self.assertEqual(config.HEADLESS, False)

        # 2. BrowserManager instance with defaults
        bm_default = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.storage_state_file
        )
        self.assertFalse(bm_default.headless, "Default BrowserManager.headless must be False")

        # 3. Explicit headless=False
        bm_explicit = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.storage_state_file,
            headless=False
        )
        self.assertFalse(bm_explicit.headless, "Explicit headless=False must remain False")

    def test_chromium_launch_args_anti_detection(self):
        """Verify Chromium launch arguments contain anti-detection flags."""
        self.assertIn(
            "--disable-blink-features=AutomationControlled",
            config.BROWSER_ARGS,
            "Chromium launch args must include '--disable-blink-features=AutomationControlled'"
        )
        self.assertIn(
            "--enable-automation",
            config.IGNORE_DEFAULT_ARGS,
            "Chromium ignore_default_args must include '--enable-automation'"
        )

    def test_live_browser_anti_detection_navigator_webdriver(self):
        """Launch headed Chromium and verify navigator.webdriver is undefined or false."""
        bm = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.storage_state_file,
            headless=False,
            slow_mo=0.0
        )
        try:
            with bm:
                page = bm.get_page("data:text/html,<html><body><h1>Anti-detection test</h1></body></html>")
                webdriver_val = page.evaluate("navigator.webdriver")
                # navigator.webdriver should be False or undefined/None
                self.assertFalse(
                    bool(webdriver_val),
                    f"navigator.webdriver was detected as {webdriver_val}, should be False or undefined"
                )

                # Check userAgent does not contain HeadlessChrome
                user_agent = page.evaluate("navigator.userAgent")
                self.assertNotIn(
                    "HeadlessChrome",
                    user_agent,
                    "Browser running in headed mode must not identify as HeadlessChrome"
                )
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self.skipTest(f"Playwright browser executable missing: {e}")
            else:
                raise

    def test_live_browser_tab_reuse(self):
        """Verify get_page() reuses initial blank page and does not spawn redundant blank tabs."""
        bm = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.storage_state_file,
            headless=False,
            slow_mo=0.0
        )
        try:
            with bm:
                ctx = bm.get_context()
                # Chromium launch_persistent_context opens 1 initial page
                initial_pages_count = len(ctx.pages)
                self.assertEqual(initial_pages_count, 1, "Context should start with exactly 1 initial tab")

                # First call to get_page()
                page1 = bm.get_page()
                self.assertEqual(len(ctx.pages), 1, "get_page() must reuse the initial tab without creating new ones")
                self.assertEqual(page1, ctx.pages[0])

                # Second call to get_page()
                page2 = bm.get_page()
                self.assertEqual(len(ctx.pages), 1, "Repeated get_page() must not spawn additional tabs")
                self.assertEqual(page1, page2)

                # Call get_page with a URL
                page3 = bm.get_page("data:text/html,<html><body><h1>Tab Reuse</h1></body></html>")
                self.assertEqual(len(ctx.pages), 1, "get_page(url) must navigate in the existing active tab")
                self.assertEqual(page1, page3)
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self.skipTest(f"Playwright browser executable missing: {e}")
            else:
                raise

    def test_session_serialization_storage_state(self):
        """Verify close() and save_storage_state() produce a valid JSON file containing cookies and origins."""
        bm = BrowserManager(
            profile_dir=self.profile_dir,
            storage_state_path=self.storage_state_file,
            headless=False,
            slow_mo=0.0
        )
        try:
            with bm:
                ctx = bm.get_context()
                page = bm.get_page("data:text/html,<html><body><h1>Cookie test</h1></body></html>")
                # Set a dummy cookie
                ctx.add_cookies([
                    {
                        "name": "session_token",
                        "value": "xyz123abc456",
                        "domain": "localhost",
                        "path": "/",
                        "expires": -1,
                        "httpOnly": False,
                        "secure": False,
                        "sameSite": "Lax"
                    }
                ])
                # Explicit save
                bm.save_storage_state()
                self.assertTrue(self.storage_state_file.exists(), "storage_state.json must exist after save")

            # After context exit, file should persist and be valid JSON
            self.assertTrue(self.storage_state_file.exists(), "storage_state.json must persist after close()")
            with open(self.storage_state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)

            self.assertIn("cookies", state_data, "storage_state JSON must contain 'cookies' key")
            self.assertIn("origins", state_data, "storage_state JSON must contain 'origins' key")
            cookie_names = [c["name"] for c in state_data["cookies"]]
            self.assertIn("session_token", cookie_names, "Custom cookie must be serialized in storage_state.json")

        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self.skipTest(f"Playwright browser executable missing: {e}")
            else:
                raise


class TestHitlHandlerEmpirical(unittest.TestCase):
    """Empirical testing of HitlHandler guardrail detection across DOM variations and false-positive checks."""

    @classmethod
    def setUpClass(cls):
        # We start a persistent browser once to run DOM evaluations
        cls.temp_dir = tempfile.mkdtemp(prefix="challenger_hitl_")
        cls.profile_dir = Path(cls.temp_dir) / ".browser_profile"
        cls.storage_state_file = Path(cls.temp_dir) / "storage_state.json"
        cls.bm = BrowserManager(
            profile_dir=cls.profile_dir,
            storage_state_path=cls.storage_state_file,
            headless=False,
            slow_mo=0.0
        )
        cls.ctx = cls.bm.start()
        cls.page = cls.bm.get_page()
        cls.hitl = HitlHandler(interactive=False, audible_bell=False)

    @classmethod
    def tearDownClass(cls):
        cls.bm.close()
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _set_html(self, html: str):
        self.page.set_content(html, wait_until="domcontentloaded")

    def test_api_check_guardrails_presence_check(self):
        """Check whether check_guardrails or detect_guardrail is present on HitlHandler."""
        # Does check_guardrails exist as an alias or method?
        has_check_guardrails = hasattr(self.hitl, "check_guardrails")
        has_detect_guardrail = hasattr(self.hitl, "detect_guardrail")
        has_check_and_handle = hasattr(self.hitl, "check_and_handle_guardrails")
        has_html_check = hasattr(self.hitl, "check_guardrails_in_html")

        print(f"\n[API Audit] HitlHandler API inspection:")
        print(f"  - hasattr(hitl, 'check_guardrails'): {has_check_guardrails}")
        print(f"  - hasattr(hitl, 'detect_guardrail'): {has_detect_guardrail}")
        print(f"  - hasattr(hitl, 'check_and_handle_guardrails'): {has_check_and_handle}")
        print(f"  - hasattr(hitl, 'check_guardrails_in_html'): {has_html_check}")

        self.assertTrue(has_detect_guardrail, "HitlHandler must provide detect_guardrail(page)")
        self.assertTrue(has_check_and_handle, "HitlHandler must provide check_and_handle_guardrails(page)")

    def test_cloudflare_turnstile_detection(self):
        """Test detection of Cloudflare Turnstile variations."""
        # Variation 1: iframe src challenges.cloudflare.com
        html_iframe = """
        <html><body>
            <iframe src="https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2/av0/rcv/0/sample" width="300" height="65"></iframe>
        </body></html>
        """
        self._set_html(html_iframe)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect Cloudflare Turnstile iframe")
        self.assertEqual(event.guardrail_type, GuardrailType.CLOUDFLARE_TURNSTILE)

        # Variation 2: div.cf-turnstile
        html_div = """
        <html><body>
            <div class="cf-turnstile" data-sitekey="0x4AAAAAA">Verification widget</div>
        </body></html>
        """
        self._set_html(html_div)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect div.cf-turnstile")
        self.assertEqual(event.guardrail_type, GuardrailType.CLOUDFLARE_TURNSTILE)

        # Variation 3: challenge-stage
        html_stage = """
        <html><body>
            <div id="challenge-stage">Performing security check...</div>
        </body></html>
        """
        self._set_html(html_stage)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect #challenge-stage")
        self.assertEqual(event.guardrail_type, GuardrailType.CLOUDFLARE_TURNSTILE)

    def test_recaptcha_detection(self):
        """Test detection of Google reCAPTCHA variations."""
        # Variation 1: iframe src google.com/recaptcha
        html_recaptcha_iframe = """
        <html><body>
            <iframe src="https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Ld" width="304" height="78"></iframe>
        </body></html>
        """
        self._set_html(html_recaptcha_iframe)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect Google reCAPTCHA iframe")
        self.assertEqual(event.guardrail_type, GuardrailType.RECAPTCHA)

        # Variation 2: div.g-recaptcha
        html_recaptcha_div = """
        <html><body>
            <div class="g-recaptcha" data-sitekey="6LdSample">reCAPTCHA box</div>
        </body></html>
        """
        self._set_html(html_recaptcha_div)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect div.g-recaptcha")
        self.assertEqual(event.guardrail_type, GuardrailType.RECAPTCHA)

    def test_otp_input_detection(self):
        """Test detection of OTP input variations."""
        # Variation 1: input with id="otp"
        html_otp_id = """
        <html><body>
            <form>
                <input id="otp" type="tel" maxlength="6" value="">
            </form>
        </body></html>
        """
        self._set_html(html_otp_id)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect input#otp")
        self.assertEqual(event.guardrail_type, GuardrailType.OTP_CHALLENGE)

        # Variation 2: input with placeholder="Enter OTP"
        html_otp_placeholder = """
        <html><body>
            <form>
                <input type="text" placeholder="Enter 6-digit OTP">
            </form>
        </body></html>
        """
        self._set_html(html_otp_placeholder)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect input with OTP placeholder")
        self.assertEqual(event.guardrail_type, GuardrailType.OTP_CHALLENGE)

        # Variation 3: input with autocomplete="one-time-code"
        html_otp_autocomplete = """
        <html><body>
            <form>
                <input type="tel" autocomplete="one-time-code" maxlength="6">
            </form>
        </body></html>
        """
        self._set_html(html_otp_autocomplete)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect input with autocomplete='one-time-code'")
        self.assertEqual(event.guardrail_type, GuardrailType.OTP_CHALLENGE)

        # Variation 4 (Stress/Adversarial): input[type="tel"][maxlength="6"] without id or otp name
        html_otp_tel = """
        <html><body>
            <form>
                <input type="tel" maxlength="6">
            </form>
        </body></html>
        """
        self._set_html(html_otp_tel)
        event_tel = self.hitl.detect_guardrail(self.page)
        # Check if bare input[type='tel'][maxlength='6'] is detected or if it requires selector enhancement
        print(f"[OTP Check] input[type='tel'][maxlength='6'] detected: {event_tel is not None}")

    def test_zenclass_mfa_detection(self):
        """Test detection of ZenClass MFA step-up authentication."""
        # Variation 1: .login-content-wrapper.login-mfa-active
        html_mfa1 = """
        <html><body>
            <div class="login-content-wrapper login-mfa-active">
                <h2>Two-Factor Authentication</h2>
                <input type="text" id="mfaCode">
            </div>
        </body></html>
        """
        self._set_html(html_mfa1)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect .login-content-wrapper.login-mfa-active")
        self.assertEqual(event.guardrail_type, GuardrailType.ZENCLASS_MFA)

        # Variation 2: div.login-mfa-wrapper
        html_mfa2 = """
        <html><body>
            <div class="login-mfa-wrapper">
                <p>Enter authentication code</p>
            </div>
        </body></html>
        """
        self._set_html(html_mfa2)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect div.login-mfa-wrapper")
        self.assertEqual(event.guardrail_type, GuardrailType.ZENCLASS_MFA)

    def test_guvi_activation_modal_detection(self):
        """Test detection of Guvi Account Activation modal."""
        # Variation 1: #myModal with visible content
        html_guvi_modal = """
        <html><body>
            <div id="myModal" class="modal show" style="display: block;">
                <div class="modal-dialog">
                    <h4>Account Verification</h4>
                    <button id="sendmail">Send Mail</button>
                </div>
            </div>
        </body></html>
        """
        self._set_html(html_guvi_modal)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect visible #myModal")
        self.assertEqual(event.guardrail_type, GuardrailType.GUVI_ACTIVATION_MODAL)

        # Variation 2: modal with #sendmail
        html_sendmail = """
        <html><body>
            <div class="modal show" style="display: block;">
                <button id="sendmail">Activate Account</button>
            </div>
        </body></html>
        """
        self._set_html(html_sendmail)
        event = self.hitl.detect_guardrail(self.page)
        self.assertIsNotNone(event, "Must detect modal with #sendmail")
        self.assertEqual(event.guardrail_type, GuardrailType.GUVI_ACTIVATION_MODAL)

    def test_false_positive_resistance(self):
        """Verify clean pages without security challenges return None."""
        clean_pages = [
            # 1. Blank page
            "<html><body><h1>Welcome</h1></body></html>",
            # 2. Standard ZenClass login form
            """
            <html><body>
                <div class="login-content-wrapper">
                    <h2>Sign in to ZenClass</h2>
                    <form>
                        <input type="email" name="email" placeholder="Email Address">
                        <input type="password" name="password" placeholder="Password">
                        <button type="submit">Sign In</button>
                    </form>
                </div>
            </body></html>
            """,
            # 3. Standard Guvi CodeKata editor page
            """
            <html><body>
                <div class="codekata-container">
                    <div id="editor">print("Hello World")</div>
                    <button class="run-code">Run</button>
                    <button class="submit-code">Submit</button>
                </div>
            </body></html>
            """,
            # 4. Hidden modal (e.g. standard Bootstrap modal not shown)
            """
            <html><body>
                <div id="myModal" class="modal fade" style="display: none;" aria-hidden="true">
                    <div class="modal-body">Hidden content</div>
                </div>
            </body></html>
            """,
        ]

        for i, page_html in enumerate(clean_pages):
            self._set_html(page_html)
            event = self.hitl.detect_guardrail(self.page)
            self.assertIsNone(
                event,
                f"Clean page variant #{i+1} must return None, but triggered: {event}"
            )


class TestUrlValidationEmpirical(unittest.TestCase):
    """Adversarial testing of HitlHandler.validate_url with valid and malicious/malformed inputs."""

    def test_valid_urls(self):
        """Verify acceptance of legitimate repository and deployment URLs."""
        valid_samples = [
            "https://github.com/user/project",
            "https://github.com/devesh/zenclass-automation.git",
            "http://github.com/sample/repo",
            "https://my-app.vercel.app",
            "https://my-project.netlify.app",
            "https://sub.domain.org/app/index.html?v=1#readme",
            "ftp://files.zenclass.in/submissions/project.zip",
            "http://localhost:3000",
            "https://127.0.0.1:8080/deploy",
        ]
        for url in valid_samples:
            self.assertTrue(
                HitlHandler.validate_url(url),
                f"Legitimate URL '{url}' should be accepted as valid"
            )

    def test_invalid_and_malicious_urls(self):
        """Verify rejection of invalid, malicious, or malformed URLs."""
        invalid_samples = [
            "javascript:alert(1)",
            "javascript://alert(1)",
            "http://",
            "https://",
            "ftp://",
            "not-a-url",
            "",
            "   ",
            None,
            12345,
            {"url": "https://github.com"},
            "https://example.com/path with spaces",
            'https://example.com/quote"test',
            "data:text/html,<html><script>alert(1)</script></html>",
            "file:///etc/passwd",
            "chrome://settings",
            "mailto:user@example.com",
            "ssh://git@github.com:user/repo.git",
        ]
        for url in invalid_samples:
            self.assertFalse(
                HitlHandler.validate_url(url),
                f"Malicious or malformed URL '{url}' must be rejected"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
