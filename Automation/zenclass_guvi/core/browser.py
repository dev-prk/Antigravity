"""
core/browser.py - Headed Foreground Browser Lifecycle Manager
Manages visible Chromium persistent contexts, anti-detection flags, tab lifecycle,
screenshot diagnostics, and dual-layer session persistence for Guvi & ZenClass.
Strictly satisfies Requirement R1 (visible foreground browser execution).
"""

from __future__ import annotations
import atexit
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, List, Any

try:
    from playwright.sync_api import (
        sync_playwright,
        BrowserContext,
        Page,
        Playwright,
        Error as PlaywrightError
    )
except ImportError:
    # Fallback types if playwright is not yet loaded in current python environment
    sync_playwright = None  # type: ignore
    BrowserContext = Any  # type: ignore
    Page = Any  # type: ignore
    Playwright = Any  # type: ignore
    PlaywrightError = Exception  # type: ignore

import config

logger = logging.getLogger("core.browser")


class BrowserManager:
    """
    Manages a persistent headed Chromium browser session adhering to Requirement R1.
    Provides session persistence, anti-detection, tab cleanup, and graceful teardown.
    """

    def __init__(
        self,
        profile_dir: Optional[Path] = None,
        storage_state_path: Optional[Path] = None,
        headless: Optional[bool] = None,
        slow_mo: Optional[float] = None,
        navigation_timeout: Optional[float] = None,
        default_timeout: Optional[float] = None,
    ):
        self.profile_dir = Path(profile_dir or config.BROWSER_PROFILE_DIR)
        self.storage_state_path = Path(storage_state_path or config.STORAGE_STATE_PATH)
        self.headless = config.HEADLESS if headless is None else headless
        self.slow_mo = config.SLOW_MO if slow_mo is None else slow_mo
        self.navigation_timeout = config.NAVIGATION_TIMEOUT if navigation_timeout is None else navigation_timeout
        self.default_timeout = config.DEFAULT_TIMEOUT if default_timeout is None else default_timeout

        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._active_page: Optional[Page] = None
        self._registered_atexit = False

    def start(self) -> BrowserContext:
        """
        Launches the persistent Chromium context in headed mode with anti-detection flags.
        Restores cookies from storage_state if available.
        """
        if self._context is not None:
            return self._context

        if sync_playwright is None:
            raise RuntimeError("Playwright is not installed. Please run `pip install playwright && playwright install chromium`.")

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        if self.storage_state_path:
            self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Launching headed persistent Chromium context at {self.profile_dir} "
            f"(headless={self.headless}, slow_mo={self.slow_mo}ms)"
        )

        self._playwright = sync_playwright().start()

        try:
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                no_viewport=True,
                args=config.BROWSER_ARGS,
                ignore_default_args=config.IGNORE_DEFAULT_ARGS,
                slow_mo=self.slow_mo,
            )

            self._context.set_default_navigation_timeout(self.navigation_timeout)
            self._context.set_default_timeout(self.default_timeout)

            # Restore secondary layer cookies from storage state if present
            self._restore_storage_state()

            # Register cleanup hook once
            if not self._registered_atexit:
                atexit.register(self.close)
                self._registered_atexit = True

            logger.info("Headed browser context successfully initialized.")
            return self._context

        except PlaywrightError as e:
            logger.error(f"Failed to launch browser persistent context: {e}")
            if "SingletonLock" in str(e) or "Process is already running" in str(e):
                logger.error(
                    "Profile directory appears locked by another Chromium instance. "
                    "Ensure existing browser processes are closed."
                )
            self.close()
            raise

    def launch(self) -> BrowserContext:
        """Alias for start() satisfying alternative caller naming."""
        return self.start()

    def _restore_storage_state(self) -> None:
        """Injects serialized cookies from storage_state.json if available."""
        if self._context and self.storage_state_path and self.storage_state_path.exists():
            try:
                with open(self.storage_state_path, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                cookies = state_data.get("cookies", [])
                if cookies:
                    self._context.add_cookies(cookies)
                    logger.info(f"Injected {len(cookies)} cookies from {self.storage_state_path}")
            except Exception as e:
                logger.warning(f"Failed to restore cookies from storage state: {e}")

    def get_context(self) -> BrowserContext:
        """Returns the active persistent BrowserContext, starting it if necessary."""
        if self._context is None:
            self.start()
        return self._context

    def get_page(self, url: Optional[str] = None, force_reload: bool = False) -> Page:
        """
        Retrieves the active page (reusing initial tab if available), brings it to front,
        and navigates to the specified URL if requested.
        """
        ctx = self.get_context()

        # Locate existing open page or create a new one
        open_pages = [p for p in ctx.pages if not p.is_closed()]
        if open_pages:
            self._active_page = open_pages[0]
        else:
            self._active_page = ctx.new_page()

        try:
            self._active_page.bring_to_front()
        except Exception:
            pass

        if url:
            current_url = self._active_page.url
            if force_reload or current_url != url:
                logger.info(f"Navigating to {url}")
                self._active_page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.navigation_timeout
                )
            else:
                logger.debug(f"Page already at {url}, skipping navigation.")

        return self._active_page

    def close_auxiliary_tabs(self, keep_page: Optional[Page] = None) -> int:
        """
        Closes extraneous popup or secondary tabs to prevent tab proliferation.
        Keeps the specified page (or current active page).
        """
        if not self._context:
            return 0
        target = keep_page or self._active_page
        closed_count = 0
        for page in list(self._context.pages):
            if page != target and not page.is_closed():
                try:
                    page.close()
                    closed_count += 1
                except Exception as e:
                    logger.debug(f"Error closing auxiliary tab: {e}")
        return closed_count

    def save_storage_state(self) -> None:
        """Serializes all active cookies and storage origins to JSON."""
        if self._context and self.storage_state_path:
            try:
                self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
                self._context.storage_state(path=str(self.storage_state_path))
                logger.info(f"Exported browser storage state to {self.storage_state_path}")
            except Exception as e:
                logger.warning(f"Could not export storage state: {e}")

    def save_screenshot(self, name: str = "error", page: Optional[Page] = None) -> Optional[Path]:
        """Captures a diagnostic PNG screenshot of the current page view."""
        target = page or self._active_page
        if not target or target.is_closed():
            return None
        filename = f"{int(time.time())}_{name}.png"
        filepath = config.SCREENSHOTS_DIR / filename
        try:
            target.screenshot(path=str(filepath), full_page=False)
            logger.info(f"Saved diagnostic screenshot to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def close(self) -> None:
        """Gracefully dumps storage state, closes context, and stops Playwright."""
        if self._context:
            logger.info("Saving storage state and closing browser context...")
            try:
                self.save_storage_state()
            except Exception as e:
                logger.warning(f"Error saving storage state on exit: {e}")
            try:
                self._context.close()
            except Exception as e:
                logger.warning(f"Error closing browser context: {e}")
            self._context = None
            self._active_page = None

        if self._playwright:
            try:
                self._playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright runtime: {e}")
            self._playwright = None

    def close_context(self) -> None:
        """Alias for close()."""
        self.close()

    def __enter__(self) -> "BrowserManager":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


# Module-level singleton pattern satisfying PROJECT.md interface contract
_global_browser_manager: Optional[BrowserManager] = None


def get_browser_manager() -> BrowserManager:
    """Returns or instantiates the global BrowserManager singleton."""
    global _global_browser_manager
    if _global_browser_manager is None:
        _global_browser_manager = BrowserManager()
    return _global_browser_manager


def get_browser_context() -> BrowserContext:
    """Interface Contract: Returns active persistent headed context."""
    return get_browser_manager().get_context()


def get_page(url: Optional[str] = None) -> Page:
    """Interface Contract: Returns active page or navigates to specified URL."""
    return get_browser_manager().get_page(url=url)


def close_context() -> None:
    """Interface Contract: Gracefully saves cookies and closes browser."""
    global _global_browser_manager
    if _global_browser_manager is not None:
        _global_browser_manager.close()
        _global_browser_manager = None
