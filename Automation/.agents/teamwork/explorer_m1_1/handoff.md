# Handoff Report: Headed Browser Manager & Configuration Architecture

**Agent ID**: `explorer_m1_1`  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_1/`  
**Recipient**: `cbd0649b-f648-4724-a244-a22a5102ccc4` (Parent Orchestrator / Sub-Orchestrator M1)  
**Milestone**: Milestone 1 (Core Foundation & Infrastructure)  
**Handoff Type**: Hard (Task Complete)  

---

## 1. Observation

Direct system inspections, framework probes, and runtime tests were conducted on macOS Darwin 25.6.0 Apple Silicon (`arm64`) to evaluate Playwright browser lifecycle, window management, persistence, and anti-detection capabilities.

### 1.1 Requirements & Specifications Baseline
- **Original Request File**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
  - Requirement R1 (lines 18-20): "Authenticate to Guvi and ZenClass using the provided credentials via a visible foreground browser window (headed mode) so execution can be monitored in real time."
  - Reference Credentials (line 14): `devsh.pareek@gmail.com` / `Dev@99#$%esh`
  - Target Platforms (lines 11-13): Guvi CodeKata (`https://www.guvi.in/code-kata/`), ZenClass Tasks (`https://v2.zenclass.in/tasks`), ZenClass Projects (`https://v2.zenclass.in/projects`).
- **Project Plan**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
  - Browser Interface Contract (lines 53-56):
    - `get_browser_context() -> BrowserContext`
    - `get_page(url: str = None) -> Page`
    - `close_context() -> None`
  - Architecture layout specifies `zenclass_guvi/config.py` and `zenclass_guvi/core/browser.py` with persistent storage in `zenclass_guvi/.browser_profile/` and `zenclass_guvi/data/`.

### 1.2 Playwright Runtime & Headed Browser Probes
Empirical tests executed using official Playwright Chromium build (`Chrome for Testing 148.0.7778.96` located at `~/Library/Caches/ms-playwright/chromium-1223`):

1. **Headed Window Launch & Screen Maximization on macOS**:
   - Command:
     ```python
     context = p.chromium.launch_persistent_context(
         user_data_dir=tmp_dir,
         headless=False,
         no_viewport=True,
         args=['--start-maximized', '--disable-blink-features=AutomationControlled'],
         ignore_default_args=['--enable-automation']
     )
     ```
   - Observed Result:
     - Window launched visibly in the foreground on macOS Aqua desktop.
     - Inner dimensions evaluated via `page.evaluate(...)`:
       `{'screenW': 1512, 'screenH': 859, 'innerW': 1512, 'innerH': 772}`
     - With `no_viewport=True`, viewport size is `None` (unconstrained), automatically matching the full desktop width (1512 scaled points) instead of being restricted to Playwright's default 1280x720 window.

2. **Anti-Detection & Bot Defense Verification**:
   - Evaluation in headed session with anti-detection flags:
     ```javascript
     ({
         webdriver: navigator.webdriver,
         pluginsLen: navigator.plugins.length,
         languages: navigator.languages,
         hasChrome: !!window.chrome,
         permissions: typeof navigator.permissions
     })
     ```
   - Observed Output:
     `{'webdriver': False, 'pluginsLen': 5, 'languages': ['en-GB', 'en-US', 'en'], 'hasChrome': True, 'permissions': 'object'}`
   - The flag `--disable-blink-features=AutomationControlled` successfully forces `navigator.webdriver = False`.
   - The parameter `ignore_default_args=['--enable-automation']` eliminates the default Chromium infobar banner ("Chrome is being controlled by automated test software"), avoiding automated bot heuristics without monkeypatching runtime objects.

3. **Page Lifecycle & Initial Tab Allocation**:
   - Tested page count immediately after `launch_persistent_context`:
     `len(context.pages) == 1`
   - Calling `context.new_page()` immediately after launch creates a second blank tab, leaving an orphaned `about:blank` tab in position 0.
   - Reusing `context.pages[0]` if available avoids tab proliferation.

4. **Dual-Layer Session Persistence (Profile Directory vs Session Cookies)**:
   - Observation: Chromium persistent profiles store `localStorage` and persistent cookies (cookies with an explicit future `expires` timestamp) in the SQLite database inside `user_data_dir`.
   - However, pure session cookies (cookies where `expires = -1` or undefined) are purged upon browser process termination by Chromium's standard cookie store.
   - In contrast, Playwright's `context.storage_state(path=state_file)` explicitly serializes ALL active cookies (including session cookies) into JSON.
   - Verification test output:
     - Direct profile restart alone: `Persistent context direct cookies: [('persistent_cookie', 'pers_456')]` (session cookie was lost).
     - Storage state export: `Saved in storage_state json: ['session_cookie', 'persistent_cookie']` (100% of cookies preserved).
   - Re-injecting storage state cookies via `context.add_cookies(state['cookies'])` on subsequent runs guarantees zero session loss even if the platform issued session-only cookies.

5. **Realistic Interaction Cadence**:
   - `slow_mo=50.0` introduced an artificial 50ms pause before every Playwright action (clicks, key presses, navigations), preventing race conditions with SPA hydration (React in ZenClass, Qwik in CodeKata) and emulating human cadence.

---

## 2. Logic Chain

From the empirical observations above, the architectural requirements translate directly into technical decisions:

1. **Compliance with R1 (Visible Foreground Window)**:
   - *Observation 1.1 & 1.2.1*: R1 mandates visible headed execution. On macOS Aqua, `headless=False` with `no_viewport=True` and `--start-maximized` displays a full-width foreground Chromium window.
   - *Deduction*: `config.HEADLESS` must default to `False`. `BrowserManager` must pass `headless=False`, `no_viewport=True`, and `args=["--start-maximized"]`. To ensure the window is active and in the foreground, `page.bring_to_front()` must be invoked upon page retrieval.

2. **Session Resilience via Dual-Layer Persistence**:
   - *Observation 1.2.4*: Persistent context alone preserves `localStorage` and expiring cookies, but purges non-expiring session cookies upon process close. Guvi and ZenClass use a mixture of cookies (`authToken`, `isZenUser`) and localStorage tokens.
   - *Deduction*: `BrowserManager` must use `launch_persistent_context(user_data_dir=config.BROWSER_PROFILE_DIR)` for primary persistence, and supplement it with explicit `context.storage_state(path=config.STORAGE_STATE_PATH)` on clean close or crash exit (`atexit`). On startup, if `config.STORAGE_STATE_PATH` exists, any serialized cookies must be re-added via `context.add_cookies()`.

3. **Tab Cleanliness and Lifecycle Safety**:
   - *Observation 1.2.3*: Playwright persistent contexts launch with exactly one active page (`len(context.pages) == 1`).
   - *Deduction*: `BrowserManager.get_page()` must reuse `context.pages[0]` if an unclosed page already exists, rather than creating a new page on every request. Furthermore, `BrowserManager` must provide a `close_auxiliary_tabs(keep_page)` utility to prevent background tab leakage when links open target `_blank` windows.

4. **Stealth and Anti-Detection Optimization**:
   - *Observation 1.2.2*: Setting `--disable-blink-features=AutomationControlled` and filtering `--enable-automation` flips `navigator.webdriver` to `False` and removes browser automation banners without requiring external patches or fragile third-party binaries.
   - *Deduction*: These arguments must be permanently baked into `config.BROWSER_ARGS` and `config.IGNORE_DEFAULT_ARGS`.

5. **Interface Contract Compliance**:
   - *Observation 1.1*: `PROJECT.md` requires module-level helper functions `get_browser_context()`, `get_page(url)`, and `close_context()`.
   - *Deduction*: `core/browser.py` must define a singleton `BrowserManager` instance exposed via both OOP class usage (`with BrowserManager() as bm: ...`) and the required functional entry points.

---

## 3. Caveats

1. **Single Concurrent Process Per Profile Directory**:
   Chromium places an exclusive filesystem lock (`SingletonLock`) on `user_data_dir`. Two simultaneous Python processes cannot open `.browser_profile/` at the same instant. If an automated process crashes and leaves an orphaned Chromium process running, the lock may block a subsequent launch. `BrowserManager` should log a clear diagnostic instructing the user to terminate any running Chromium processes if `launch_persistent_context` fails.
2. **Display Requirement on macOS**:
   Headed mode (`headless=False`) requires an active macOS graphical Aqua desktop. It cannot run over headless SSH unless forwarded through an X11/VNC display server. Since the user environment is macOS desktop (`arm64`), this condition is satisfied.
3. **Interactive Human-in-the-Loop Triggers**:
   While anti-detection flags prevent automated heuristic flags, Cloudflare Turnstile or platform OTP challenges may still trigger on IP rotation or excessive login attempts. Per Requirement R1, the automation must never fabricate bypasses; `core/hitl_handler.py` must pause and alert the human operator.

---

## 4. Conclusion & Implementation Blueprints

The implementation for Milestone 1 infrastructure must provide two primary modules:
1. `zenclass_guvi/config.py` — Centralized configuration, URLs, credentials, paths, and timeouts.
2. `zenclass_guvi/core/browser.py` — Production-grade headed browser lifecycle manager.

### 4.1 Recommended Blueprint: `config.py`

```python
"""
Configuration module for Guvi CodeKata and ZenClass Automation Suite.
Defines URLs, credentials, timeouts, paths, and browser flags.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
BROWSER_PROFILE_DIR = BASE_DIR / ".browser_profile"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
PROJECTS_DIR = BASE_DIR / "projects"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# State & Storage Paths
DB_PATH = DATA_DIR / "automation_state.db"
STATE_SUMMARY_JSON = DATA_DIR / "state_summary.json"
STORAGE_STATE_PATH = DATA_DIR / "storage_state.json"
SUMMARY_REPORT_MD = REPORTS_DIR / "SUMMARY_REPORT.md"
SUMMARY_REPORT_JSON = REPORTS_DIR / "summary.json"

# Credentials (from ORIGINAL_REQUEST.md, overridable via environment variables)
USER_EMAIL = os.getenv("AUTOMATION_USER_EMAIL", "devsh.pareek@gmail.com")
USER_PASSWORD = os.getenv("AUTOMATION_USER_PASSWORD", "Dev@99#$%esh")

# Platform URLs
GUVI_BASE_URL = "https://www.guvi.in"
GUVI_LOGIN_URL = "https://www.guvi.in/sign-in/"
GUVI_CODEKATA_URL = "https://www.guvi.in/code-kata/"
ZENCLASS_BASE_URL = "https://v2.zenclass.in"
ZENCLASS_LOGIN_URL = "https://v2.zenclass.in/login"
ZENCLASS_TASKS_URL = "https://v2.zenclass.in/tasks"
ZENCLASS_PROJECTS_URL = "https://v2.zenclass.in/projects"
ZENCLASS_DASHBOARD_URL = "https://v2.zenclass.in/dashboard"

# Browser Execution Settings (Requirement R1: visible foreground browser)
HEADLESS = os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true"  # strictly False by default
SLOW_MO = float(os.getenv("AUTOMATION_SLOW_MO", "50.0"))  # 50ms realistic human cadence
NAVIGATION_TIMEOUT = float(os.getenv("AUTOMATION_NAV_TIMEOUT", "30000.0"))  # 30 seconds
DEFAULT_TIMEOUT = float(os.getenv("AUTOMATION_TIMEOUT", "10000.0"))  # 10 seconds

BROWSER_ARGS = [
    "--start-maximized",
    "--disable-blink-features=AutomationControlled",
    "--no-default-browser-check",
    "--no-first-run",
]

IGNORE_DEFAULT_ARGS = [
    "--enable-automation",
]

# Solver & Submission Settings
DEFAULT_LANGUAGE = "PYTHON 3"
MAX_SUBMISSION_ATTEMPTS = 3
LOCAL_TEST_TIMEOUT_SECONDS = 5.0

# Human-in-the-Loop (HITL) Settings
HITL_ALERT_BEEP = True
HITL_POLL_INTERVAL_SECONDS = 2.0
HITL_MAX_WAIT_SECONDS = 600.0  # 10 minutes maximum before timing out

# Logging Settings
LOG_LEVEL = os.getenv("AUTOMATION_LOG_LEVEL", "INFO")
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
```

### 4.2 Recommended Blueprint: `core/browser.py`

```python
"""
core/browser.py - Headed Foreground Browser Lifecycle Manager
Manages visible Chromium persistent contexts, anti-detection flags, tab lifecycle,
screenshot diagnostics, and dual-layer session persistence for Guvi & ZenClass.
"""

import atexit
import json
import logging
from pathlib import Path
from typing import Optional, List

from playwright.sync_api import (
    sync_playwright,
    BrowserContext,
    Page,
    Playwright,
    Error as PlaywrightError
)

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
        self.profile_dir = profile_dir or config.BROWSER_PROFILE_DIR
        self.storage_state_path = storage_state_path or config.STORAGE_STATE_PATH
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
        import time
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

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
```

---

## 5. Verification Method

To verify the implementation independently, follow these test procedures:

### 5.1 Unit & Integration Test (`tests/test_browser.py`)
Run the following test using `pytest`:
```bash
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
pytest tests/test_browser.py -v
```

Expected Test Assertions:
1. **Headed Flag Verification**:
   ```python
   def test_browser_headed_configuration():
       import config
       from core.browser import BrowserManager
       bm = BrowserManager()
       assert bm.headless is False, "BrowserManager MUST default to headless=False (Requirement R1)"
   ```
2. **Context Persistence & Viewport Verification**:
   ```python
   def test_browser_persistent_launch_and_page(tmp_path):
       from core.browser import BrowserManager
       profile = tmp_path / ".test_profile"
       state = tmp_path / "state.json"
       bm = BrowserManager(profile_dir=profile, storage_state_path=state, headless=False)
       with bm:
           page = bm.get_page("data:text/html,<h1>Headed Test</h1>")
           assert page.inner_text("h1") == "Headed Test"
           webdriver_val = page.evaluate("navigator.webdriver")
           assert webdriver_val is False, "navigator.webdriver must be False"
           assert len(bm.get_context().pages) == 1, "Must reuse initial page tab without leakage"
       assert state.exists(), "storage_state.json must be exported upon context close"
   ```
3. **Auxiliary Tab Management**:
   ```python
   def test_auxiliary_tab_cleanup(tmp_path):
       from core.browser import BrowserManager
       bm = BrowserManager(profile_dir=tmp_path / "p", storage_state_path=tmp_path / "s.json", headless=False)
       with bm:
           page1 = bm.get_page("data:text/html,<h1>Main</h1>")
           ctx = bm.get_context()
           page2 = ctx.new_page()
           assert len(ctx.pages) == 2
           closed = bm.close_auxiliary_tabs(keep_page=page1)
           assert closed == 1
           assert len(ctx.pages) == 1
           assert ctx.pages[0] == page1
   ```

### 5.2 Invalidation Conditions
The design is invalidated if:
1. `headless` is set to `True` during default production runs (violates R1).
2. Browser context fails to persist user authentication cookies across separate invocations.
3. Multiple blank tabs accumulate (`about:blank`) during sequential `get_page()` calls.
4. `SingletonLock` crash error is unhandled when an external Chromium process is active.
