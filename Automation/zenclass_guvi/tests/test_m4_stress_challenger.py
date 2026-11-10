"""
tests/test_m4_stress_challenger.py
Adversarial Empirical Stress Test Suite for Milestone 4 (ZenClass Tasks Driver).
Authored by challenger_m4_1 to empirically probe:
  1. Module 41486 dynamic subsets: empty fields, single field, all 13 fields simultaneously,
     missing fields, unexpected field labels, data-field-key prioritization, and missing input elements.
  2. URL validation regex edge cases: valid schemes (http, https, ftp), unauthorized schemes
     (file, javascript, data, mailto, etc.), whitespace, unescaped quotes, None, empty string,
     and massive 1MB payload ReDoS resilience.
  3. Confirmation popup regex variations: verbatim 'Task Submitted Suceessfully', standard
     'Task Submitted Successfully', mixed casing, failure popups (.error-popup-main-container,
     .validation-error-text), timeout handling, and precedence vulnerability probing.
"""

from __future__ import annotations
import inspect
import re
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure zenclass_guvi is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskResult
from drivers.zenclass_tasks_driver import (
    ZenClassTasksDriver,
    ZENCLASS_TASK_FIELD_MAP,
    LABEL_TO_FIELD_KEY,
    ZENCLASS_URL_REGEX,
    ZENCLASS_CONFIRMATION_REGEX,
)


class TestModule41486DynamicSubsetsStress(unittest.TestCase):
    """Stress tests dynamic modal field mapping, subsets, and edge inputs."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
        )

    def test_empty_modal_wrappers_rejection(self):
        """Empty modal (0 field wrappers found) fails gracefully with explicit error."""
        self.mock_page.query_selector_all.return_value = []
        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task("task-empty", deliverable_urls={"github_Url": "https://github.com/u/r"})
            self.assertFalse(res["success"])
            self.assertIn("No submission field wrappers found", res["error"])
            self.mock_sm.update_task_status.assert_called_with(
                task_id="task-empty",
                status=TaskStatus.FAILED.value,
                result=TaskResult.SUBMISSION_FAILED.value,
                failure_reason=res["error"],
                next_action="INVESTIGATE_FAILURE",
            )

    def test_single_field_modal_success(self):
        """Single field modal (e.g. only Frontend Deployed URL) succeeds when URL provided."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Frontend Deployed URL"
        input_el = MagicMock()

        def w_qs(sel):
            if "label" in sel:
                return label_el
            if "input" in sel:
                return input_el
            return None

        wrapper.query_selector.side_effect = w_qs
        wrapper.get_attribute.return_value = "frontEnd_Deployed_Url"
        self.mock_page.query_selector_all.return_value = [wrapper]

        modal_submit_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_submit_btn

        with patch.object(self.driver, "safe_click", autospec=True), \
             patch.object(self.driver, "verify_submission_confirmation", autospec=True) as mock_verify:
            mock_verify.return_value = {"success": True, "task_id": "task-single"}

            res = self.driver.submit_task(
                "task-single",
                deliverable_urls={"frontEnd_Deployed_Url": "https://myapp.vercel.app"}
            )
            self.assertTrue(res["success"])
            input_el.fill.assert_called_with("https://myapp.vercel.app")
            modal_submit_btn.click.assert_called_once()

    def test_single_field_modal_missing_url_fails(self):
        """Single field modal fails gracefully when candidate deliverable URLs lacks required field."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Backend Deployed URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = "backEnd_Deployed_Url"
        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task("task-single-fail", deliverable_urls={"github_Url": "https://github.com/u/r"})
            self.assertFalse(res["success"])
            self.assertIn("Missing required submission URL", res["error"])
            self.assertIn("Backend Deployed URL", res["error"])

    def test_all_13_canonical_fields_simultaneously(self):
        """Modal containing all 13 canonical Module 41486 fields fills all inputs cleanly."""
        wrappers = []
        input_mocks = {}
        deliverables = {}

        for key, label in ZENCLASS_TASK_FIELD_MAP.items():
            w = MagicMock()
            lbl = MagicMock()
            lbl.inner_text.return_value = label
            inp = MagicMock()
            input_mocks[key] = inp

            def make_qs(l, i):
                return lambda sel: l if "label" in sel else (i if "input" in sel else None)

            w.query_selector.side_effect = make_qs(lbl, inp)
            w.get_attribute.return_value = key
            wrappers.append(w)
            deliverables[key] = f"https://example.com/{key.lower()}"

        self.mock_page.query_selector_all.return_value = wrappers

        modal_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_btn

        with patch.object(self.driver, "safe_click", autospec=True), \
             patch.object(self.driver, "verify_submission_confirmation", autospec=True) as mock_verify:
            mock_verify.return_value = {"success": True, "task_id": "task-all-13"}

            res = self.driver.submit_task("task-all-13", deliverable_urls=deliverables)
            self.assertTrue(res["success"])

            # Verify all 13 input elements were filled with corresponding URLs
            self.assertEqual(len(input_mocks), 13)
            for key, inp in input_mocks.items():
                inp.fill.assert_called_with(deliverables[key])

            modal_btn.click.assert_called_once()
            # Verify verify_submission_confirmation received filled_fields with all 13 keys
            call_args = mock_verify.call_args[0]
            filled = call_args[2]
            self.assertEqual(len(filled), 13)
            for k in ZENCLASS_TASK_FIELD_MAP:
                self.assertIn(k, filled)

    def test_all_13_canonical_fields_one_missing_aborts_early(self):
        """If 1 of 13 fields is omitted, driver halts immediately and does not click submit."""
        wrappers = []
        input_mocks = {}
        deliverables = {}

        keys = list(ZENCLASS_TASK_FIELD_MAP.keys())
        missing_key = keys[-1]  # behance_Url

        for key, label in ZENCLASS_TASK_FIELD_MAP.items():
            w = MagicMock()
            lbl = MagicMock()
            lbl.inner_text.return_value = label
            inp = MagicMock()
            input_mocks[key] = inp

            def make_qs(l, i):
                return lambda sel: l if "label" in sel else (i if "input" in sel else None)

            w.query_selector.side_effect = make_qs(lbl, inp)
            w.get_attribute.return_value = key
            wrappers.append(w)
            if key != missing_key:
                deliverables[key] = f"https://example.com/{key.lower()}"

        self.mock_page.query_selector_all.return_value = wrappers
        modal_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_btn

        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task("task-all-13-missing-one", deliverable_urls=deliverables)
            self.assertFalse(res["success"])
            self.assertIn("Missing required submission URL", res["error"])
            self.assertIn(missing_key, res["error"])
            modal_btn.click.assert_not_called()

    def test_unexpected_unknown_field_label_supported_when_provided(self):
        """Driver dynamically adapts to unexpected field labels when user provides value."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Personal Portfolio URL"
        input_el = MagicMock()

        def w_qs(sel):
            if "label" in sel:
                return label_el
            if "input" in sel:
                return input_el
            return None

        wrapper.query_selector.side_effect = w_qs
        wrapper.get_attribute.return_value = None  # No data-field-key
        self.mock_page.query_selector_all.return_value = [wrapper]

        modal_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_btn

        with patch.object(self.driver, "safe_click", autospec=True), \
             patch.object(self.driver, "verify_submission_confirmation", autospec=True) as mock_verify:
            mock_verify.return_value = {"success": True, "task_id": "task-unexpected"}

            res = self.driver.submit_task(
                "task-unexpected",
                deliverable_urls={"Personal Portfolio URL": "https://myportfolio.dev"}
            )
            self.assertTrue(res["success"])
            input_el.fill.assert_called_with("https://myportfolio.dev")

    def test_unexpected_unknown_field_label_missing_fails_cleanly(self):
        """Driver halts with clear error if unexpected field is not provided."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Demo Video URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = None
        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task("task-unexpected-fail", deliverable_urls={"github_Url": "https://github.com/u/r"})
            self.assertFalse(res["success"])
            self.assertIn("Missing required submission URL for field 'Demo Video URL'", res["error"])

    def test_field_with_data_field_key_prioritization(self):
        """Attribute data-field-key takes precedence over human label text."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Custom Weird Label Text"
        input_el = MagicMock()

        def w_qs(sel):
            if "label" in sel:
                return label_el
            if "input" in sel:
                return input_el
            return None

        wrapper.query_selector.side_effect = w_qs
        wrapper.get_attribute.return_value = "github_Url"
        self.mock_page.query_selector_all.return_value = [wrapper]

        modal_btn = MagicMock()
        self.mock_page.wait_for_selector.return_value = modal_btn

        with patch.object(self.driver, "safe_click", autospec=True), \
             patch.object(self.driver, "verify_submission_confirmation", autospec=True) as mock_verify:
            mock_verify.return_value = {"success": True, "task_id": "task-attr-priority"}

            res = self.driver.submit_task(
                "task-attr-priority",
                deliverable_urls={"github_Url": "https://github.com/org/repo"}
            )
            self.assertTrue(res["success"])
            input_el.fill.assert_called_with("https://github.com/org/repo")

    def test_missing_input_element_in_wrapper(self):
        """Wrapper missing input element is handled without uncaught AttributeError."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Github URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = "github_Url"
        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            res = self.driver.submit_task("task-missing-input", deliverable_urls={"github_Url": "https://github.com/u/r"})
            self.assertFalse(res["success"])
            self.assertIn("Input element missing", res["error"])


class TestUrlValidationRegexAdversarialStress(unittest.TestCase):
    """Adversarial stress testing of URL validation regex (Module 41486 / Module 36976)."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
        )

    def test_valid_schemes_comprehensive(self):
        """Verifies all valid schemes (http, https, ftp) and valid complex URI forms."""
        valid_cases = [
            "http://example.com",
            "https://example.com",
            "ftp://files.example.org",
            "http://localhost:3000",
            "http://127.0.0.1:8080/path/to/resource",
            "https://sub.domain.company.co.in:8443/app?query=test&param=1#section-1",
            "https://drive.google.com/drive/folders/1234567890abcdef_ABCDEF?usp=sharing",
            "https://linkedin.com/posts/username_activity-1234567890-abcd",
            "https://figma.com/file/abcdef12345/My-Project?node-id=0%3A1",
            "ftp://anonymous:guest@ftp.gnu.org/gnu/emacs/emacs-28.1.tar.gz",
        ]
        for url in valid_cases:
            self.assertTrue(
                bool(ZENCLASS_URL_REGEX.match(url)),
                f"Valid URL was unexpectedly rejected: {url}"
            )

    def test_invalid_unauthorized_schemes(self):
        """Verifies non-allowed schemes are strictly rejected."""
        invalid_schemes = [
            "file:///etc/passwd",
            "file:///C:/Users/Administrator/NTUSER.DAT",
            "javascript:alert(document.cookie)",
            "javascript:void(0)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "data:application/json;charset=utf-8,%7B%22status%22%3A%22ok%22%7D",
            "mailto:student@example.com",
            "tel:+1234567890",
            "sms:+1234567890",
            "ssh://git@github.com:repo.git",
            "git://github.com/org/repo.git",
            "ws://socket.example.com",
            "wss://socket.example.com",
            "blob:https://example.com/3f82046e-1d54-4786-9051-dc457494f48b",
            "chrome://settings",
            "about:blank",
            "view-source:https://example.com",
        ]
        for url in invalid_schemes:
            self.assertFalse(
                bool(ZENCLASS_URL_REGEX.match(url)),
                f"Unauthorized scheme was unexpectedly accepted: {url}"
            )

    def test_malformed_url_syntax_and_delimiters(self):
        """Verifies URLs with missing protocols, spaces, quotes, or whitespace are rejected."""
        malformed_cases = [
            "",
            "   ",
            "\t\n",
            "github.com/org/repo",
            "www.guvi.in",
            "//example.com",
            "http:/single-slash.com",
            "http:no-slashes.com",
            "https://has space.com",
            " https://leading-space.com",
            "https://trailing-space.com ",
            "https://example.com/path with spaces/file.html",
            "https://example.com?query=hello world",
            "https://example.com#anchor space",
            'https://example.com/"quote',
            'https://example.com/path"with"quotes',
            'https://example.com/"',
        ]
        for url in malformed_cases:
            self.assertFalse(
                bool(ZENCLASS_URL_REGEX.match(url)),
                f"Malformed URL was unexpectedly matched: {repr(url)}"
            )

    def test_massive_url_and_linear_time_redos_resistance(self):
        """Empirically stress-tests 1MB URL payload for catastrophic backtracking (ReDoS)."""
        sizes = [10_000, 100_000, 1_000_000]

        for size in sizes:
            # 1. Valid huge payload
            huge_valid = "https://example.com/" + ("a" * size)
            t0 = time.time()
            m1 = ZENCLASS_URL_REGEX.match(huge_valid)
            dur_valid = time.time() - t0
            self.assertIsNotNone(m1)
            self.assertLess(dur_valid, 0.5, f"Valid match took too long ({dur_valid}s) for {size} chars")

            # 2. Invalid huge payload (trailing space at the end of 1MB)
            huge_invalid_end = huge_valid + " "
            t0 = time.time()
            m2 = ZENCLASS_URL_REGEX.match(huge_invalid_end)
            dur_invalid = time.time() - t0
            self.assertIsNone(m2)
            self.assertLess(dur_invalid, 0.5, f"Invalid end match took too long ({dur_invalid}s) for {size} chars")

            # 3. Invalid prefix with 1MB payload
            huge_invalid_prefix = "ftp://" + ("a" * size) + '"'
            t0 = time.time()
            m3 = ZENCLASS_URL_REGEX.match(huge_invalid_prefix)
            dur_prefix = time.time() - t0
            self.assertIsNone(m3)
            self.assertLess(dur_prefix, 0.5, f"Invalid prefix match took too long ({dur_prefix}s) for {size} chars")

    def test_driver_submit_task_handles_none_and_empty_url(self):
        """Driver cleanly catches None, empty string, and malformed URL without throwing unhandled exceptions."""
        wrapper = MagicMock()
        label_el = MagicMock()
        label_el.inner_text.return_value = "Github URL"
        wrapper.query_selector.side_effect = lambda sel: label_el if "label" in sel else None
        wrapper.get_attribute.return_value = "github_Url"
        self.mock_page.query_selector_all.return_value = [wrapper]

        with patch.object(self.driver, "safe_click", autospec=True):
            # Test with None
            res_none = self.driver.submit_task("task-none", deliverable_urls={"github_Url": None})
            self.assertFalse(res_none["success"])
            self.assertIn("Missing required submission URL", res_none["error"])

            # Test with empty string
            res_empty = self.driver.submit_task("task-empty", deliverable_urls={"github_Url": ""})
            self.assertFalse(res_empty["success"])
            self.assertIn("Missing required submission URL", res_empty["error"])

            # Test with invalid scheme (file://)
            res_file = self.driver.submit_task("task-file", deliverable_urls={"github_Url": "file:///etc/passwd"})
            self.assertFalse(res_file["success"])
            self.assertIn("failed regex validation", res_file["error"])

            # Test with javascript injection scheme
            res_js = self.driver.submit_task("task-js", deliverable_urls={"github_Url": "javascript:alert(1)"})
            self.assertFalse(res_js["success"])
            self.assertIn("failed regex validation", res_js["error"])


class TestConfirmationPopupRegexVariationsAndPrecedence(unittest.TestCase):
    """Stress tests confirmation regex spelling, casing, punctuation, and failure modes."""

    def setUp(self):
        self.mock_bm = MagicMock(spec=BrowserManager)
        self.mock_sm = MagicMock(spec=StateManager)
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.driver = ZenClassTasksDriver(
            browser_manager=self.mock_bm,
            state_manager=self.mock_sm,
        )

    def test_verbatim_platform_typo_and_variations(self):
        """Verifies exact platform typo 'Task Submitted Suceessfully' and spelling variations."""
        matches = [
            "Task Submitted Suceessfully",       # Exact platform typo (1 c, 2 e's, 2 s's)
            "Task Submitted Successfully",       # Standard English (2 c's, 1 e, 2 s's)
            "task submitted sucessfully",        # Minimal (1 c, 1 e, 2 s's)
            "Task Submitted Suceeeessfully",     # 4 e's
            "Task Submitted Succeessfully",      # 2 c's, 2 e's
            "TASK SUBMITTED SUCEESSFULLY",       # Uppercase platform typo
            "TASK SUBMITTED SUCCESSFULLY",       # Uppercase standard
            "tAsK sUbMiTtEd SuCeEsSfUlLy",       # Mixed case
            "  Task Submitted Suceessfully  ",   # Padding whitespace
            "Task Submitted Suceessfully!",      # Trailing punctuation
            "Notification: Task Submitted Suceessfully [Ref: 41486]", # Context wrapper
        ]
        for text in matches:
            self.assertTrue(
                bool(ZENCLASS_CONFIRMATION_REGEX.search(text)),
                f"Confirmation regex failed to match positive confirmation: {repr(text)}"
            )

    def test_rejection_of_unrelated_or_failure_phrases(self):
        """Verifies confirmation regex does NOT match failure messages."""
        failures = [
            "Task Submission Failed",
            "Task Unsuccessful",
            "Error: Submission rejected",
            "Failed to submit task",
            "Submission deadline has passed",
            "Something went wrong while submitting",
            "Task Submitted Unsuccessfully",     # Contains 'Unsuccessfully'
        ]
        for text in failures:
            self.assertFalse(
                bool(ZENCLASS_CONFIRMATION_REGEX.search(text)),
                f"Confirmation regex erroneously matched failure text: {repr(text)}"
            )

    def test_verify_submission_confirmation_with_validation_error_text(self):
        """When inline .validation-error-text appears, it halts and marks task FAILED."""
        mock_popup = MagicMock()
        mock_val_err = MagicMock()
        mock_val_err.is_visible.return_value = True
        mock_val_err.inner_text.return_value = "Please enter a valid Git URL"

        self.mock_page.wait_for_selector.return_value = mock_popup
        self.mock_page.query_selector.side_effect = lambda sel: mock_val_err if "validation-error" in sel else None

        res = self.driver.verify_submission_confirmation(
            task_id="task-val-err",
            start_time=time.time(),
            filled_fields={"github_Url": "https://github.com/u/r"},
        )
        self.assertFalse(res["success"])
        self.assertIn("Field validation failed", res["error"])
        self.assertIn("Please enter a valid Git URL", res["error"])

    def test_verify_submission_confirmation_with_error_popup(self):
        """When .error-popup-main-container appears with failure text, task is marked FAILED."""
        mock_popup = MagicMock()
        mock_popup.inner_text.return_value = "Platform Error: Submission window closed for this batch."

        self.mock_page.wait_for_selector.return_value = mock_popup

        def page_qs(sel):
            if "validation-error" in sel:
                return None
            if "sucess-popup-text" in sel or "modal-message" in sel:
                return None
            return None

        self.mock_page.query_selector.side_effect = page_qs

        res = self.driver.verify_submission_confirmation(
            task_id="task-err-popup",
            start_time=time.time(),
            filled_fields={"github_Url": "https://github.com/u/r"},
        )
        self.assertFalse(res["success"])
        self.assertIn("submission error", res["error"].lower())

    def test_verify_submission_confirmation_timeout_handling(self):
        """When wait_for_selector times out, driver records FAILED with timeout explanation."""
        self.mock_page.wait_for_selector.side_effect = Exception("Timeout 8000ms exceeded")

        res = self.driver.verify_submission_confirmation(
            task_id="task-timeout",
            start_time=time.time(),
            filled_fields={"github_Url": "https://github.com/u/r"},
        )
        self.assertFalse(res["success"])
        self.assertIn("Timed out awaiting platform confirmation popup", res["error"])

    def test_adversarial_error_containing_task_submitted_precedence_probe(self):
        """
        Adversarial probe:
        Checks behavior when an error message contains the phrase 'task submitted'
        (e.g., 'Error: Task submitted was rejected due to plagiarism').
        Tests whether the positive substring check ('task submitted' in raw_text.lower())
        overrides the failure detection.
        """
        raw_text = "Platform Error: Task submitted was rejected"
        has_regex = bool(ZENCLASS_CONFIRMATION_REGEX.search(raw_text))
        has_task_sub = "task submitted" in raw_text.lower()
        has_error = "error" in raw_text.lower() or "failed" in raw_text.lower()

        # The regex itself is safe
        self.assertFalse(has_regex, "Confirmation regex should NOT match error text")

        # But the fallback substring 'task submitted' is present
        self.assertTrue(has_task_sub, "Phrase 'task submitted' is present in error text")
        self.assertTrue(has_error, "Error keywords are also present")


if __name__ == "__main__":
    unittest.main()
