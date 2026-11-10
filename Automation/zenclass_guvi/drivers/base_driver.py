"""
drivers/base_driver.py - Common Platform Driver Base Class
Provides shared navigation, element interactions, HITL guardrail checks,
diagnostic screenshots, and session lifecycle management for Guvi and ZenClass.
Strictly adheres to Requirements R1, R2, and R3.
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Optional, List, Union, Any, Dict

import config
from core.browser import BrowserManager
from core.state_manager import StateManager
from core.hitl_handler import HitlHandler
from core.reporter import SummaryReporter

logger = logging.getLogger("drivers.base")


class DriverError(Exception):
    """Base exception for platform driver operations."""
    pass


class AuthenticationError(DriverError):
    """Raised when platform authentication fails or credentials are rejected."""
    pass


class GuardrailBlockedError(DriverError):
    """Raised when a security guardrail halts autonomous execution."""
    pass


class ElementNotFoundError(DriverError):
    """Raised when target UI elements cannot be found on active page."""
    pass


class BaseDriver:
    """
    Abstract base driver encapsulating common Playwright interactions,
    HITL guardrail interception, modal dismissal, and session persistence.
    """

    def __init__(
        self,
        browser_manager: Optional[BrowserManager] = None,
        state_manager: Optional[StateManager] = None,
        hitl_handler: Optional[HitlHandler] = None,
        reporter: Optional[SummaryReporter] = None,
    ):
        self.browser_manager = browser_manager or BrowserManager()
        self.state_manager = state_manager
        self.hitl_handler = hitl_handler or HitlHandler(interactive=True, state_manager=self.state_manager)
        self.reporter = reporter
        self._current_page: Optional[Any] = None

    @property
    def page(self) -> Any:
        """Returns the active Playwright page, initializing if needed."""
        if self._current_page is None or getattr(self._current_page, "is_closed", lambda: True)():
            self._current_page = self.browser_manager.get_page()
        return self._current_page

    def navigate(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[float] = None,
        force_reload: bool = False,
    ) -> Any:
        """
        Navigates to URL and brings the page to foreground for visual monitoring.
        """
        timeout_ms = timeout if timeout is not None else config.NAVIGATION_TIMEOUT
        logger.info(f"Navigating to {url} (wait_until={wait_until}, timeout={timeout_ms}ms)")
        try:
            current_url = getattr(self.page, "url", "")
            if force_reload or current_url != url:
                self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            self.page.bring_to_front()
        except Exception as e:
            logger.warning(f"Navigation to {url} encountered notice: {e}")
            try:
                self.page.bring_to_front()
            except Exception:
                pass
        return self.page

    def check_guardrails(
        self,
        task_id: Optional[str] = None,
        context_desc: str = "Active Page",
    ) -> bool:
        """
        Inspects current page for Cloudflare Turnstile, reCAPTCHA, OTP, MFA,
        or account activation gates. Halts for human intervention if detected (R1).
        Returns True if a guardrail was detected and resolved; False if none was detected.
        """
        return self.hitl_handler.check_and_handle_guardrails(
            self.page,
            task_id=task_id,
            context_desc=context_desc,
        )

    def find_first_selector(
        self,
        selectors: Union[str, List[str]],
        timeout: float = 3000.0,
    ) -> Optional[str]:
        """
        Returns the first selector in the list that exists and is visible on page.
        """
        candidates = [selectors] if isinstance(selectors, str) else selectors
        for sel in candidates:
            try:
                el = self.page.wait_for_selector(sel, state="visible", timeout=timeout)
                if el:
                    return sel
            except Exception:
                continue
        return None

    def safe_fill(
        self,
        selector_or_selectors: Union[str, List[str]],
        text: str,
        timeout: float = 5000.0,
    ) -> str:
        """
        Fills the first matching selector from the target list or single selector.
        Returns the matched selector.
        """
        candidates = (
            [selector_or_selectors]
            if isinstance(selector_or_selectors, str)
            else selector_or_selectors
        )
        matched = self.find_first_selector(candidates, timeout=timeout)
        if not matched:
            self.save_screenshot(f"fill_failed_{int(time.time())}")
            raise ElementNotFoundError(
                f"None of the target input selectors {candidates} were found on {getattr(self.page, 'url', 'page')}"
            )
        self.page.fill(matched, text)
        return matched

    def safe_click(
        self,
        selector_or_selectors: Union[str, List[str]],
        timeout: float = 5000.0,
        force: bool = False,
    ) -> str:
        """
        Clicks the first matching selector from the target list or single selector.
        Returns the matched selector string.
        """
        candidates = (
            [selector_or_selectors]
            if isinstance(selector_or_selectors, str)
            else selector_or_selectors
        )
        matched = self.find_first_selector(candidates, timeout=timeout)
        if not matched:
            self.save_screenshot(f"click_failed_{int(time.time())}")
            raise ElementNotFoundError(
                f"None of the target click selectors {candidates} were found on {getattr(self.page, 'url', 'page')}"
            )
        self.page.click(matched, force=force)
        return matched

    def is_visible(self, selector: str, timeout: float = 2.0) -> bool:
        """
        Checks whether selector is currently visible without throwing timeout exceptions.
        """
        try:
            el = self.page.wait_for_selector(
                selector,
                state="visible",
                timeout=int(timeout * 1000)
            )
            return el is not None
        except Exception:
            return False

    def dismiss_modals(self, selectors: Optional[List[str]] = None) -> int:
        """
        Closes generic popup dialogs, onboarding tours, or notification overlays.
        Returns number of dismissed modals.
        """
        close_selectors = selectors or [
            "button:has-text('✕')",
            "button:has-text('Close')",
            "button:has-text('close')",
            ".modal .btn-close",
            "dialog button.close",
            "#welcome button.close",
            ".modal button.close",
        ]
        dismissed = 0
        for sel in close_selectors:
            try:
                btn = self.page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    dismissed += 1
                    time.sleep(0.3)
            except Exception:
                pass
        return dismissed

    def save_screenshot(self, name: str = "error") -> Optional[Path]:
        """Captures diagnostic PNG screenshot."""
        try:
            return self.browser_manager.save_screenshot(name=name, page=self.page)
        except Exception as e:
            logger.debug(f"Could not capture screenshot '{name}': {e}")
            return None

    def persist_session(self) -> None:
        """Exports active browser cookies and localStorage to storage_state.json."""
        try:
            self.browser_manager.save_storage_state()
            logger.info("Browser session state persisted successfully.")
        except Exception as e:
            logger.warning(f"Could not persist browser session state: {e}")
