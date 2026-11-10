"""
Configuration module for Guvi CodeKata and ZenClass Automation Suite.
Defines platform URLs, credentials, paths, timeouts, and browser execution flags.
Strictly adheres to Requirement R1 (headed foreground browser execution).
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
GUVI_EMAIL = USER_EMAIL
GUVI_PASSWORD = USER_PASSWORD
ZENCLASS_EMAIL = USER_EMAIL
ZENCLASS_PASSWORD = USER_PASSWORD

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
CODEKATA_HEADLESS = os.getenv("AUTOMATION_CODEKATA_HEADLESS", "true").lower() in ("true", "1", "yes")
SLOW_MO = float(os.getenv("AUTOMATION_SLOW_MO", "50.0"))  # 50ms realistic human cadence
NAVIGATION_TIMEOUT = float(os.getenv("AUTOMATION_NAV_TIMEOUT", "30000.0"))  # 30 seconds
DEFAULT_TIMEOUT = float(os.getenv("AUTOMATION_TIMEOUT", "10000.0"))  # 10 seconds

# CodeKata Difficulty Settings
DEFAULT_CODEKATA_DIFFICULTIES = ["Medium", "Hard"]
VALID_CODEKATA_DIFFICULTIES = ["Easy", "Medium", "Hard"]

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


class Config:
    """Class wrapper exposing configuration settings for OOP access."""
    BASE_DIR = BASE_DIR
    BROWSER_PROFILE_DIR = BROWSER_PROFILE_DIR
    DATA_DIR = DATA_DIR
    REPORTS_DIR = REPORTS_DIR
    PROJECTS_DIR = PROJECTS_DIR
    SCREENSHOTS_DIR = SCREENSHOTS_DIR

    DB_PATH = DB_PATH
    STATE_SUMMARY_JSON = STATE_SUMMARY_JSON
    STORAGE_STATE_PATH = STORAGE_STATE_PATH
    SUMMARY_REPORT_MD = SUMMARY_REPORT_MD
    SUMMARY_REPORT_JSON = SUMMARY_REPORT_JSON

    USER_EMAIL = USER_EMAIL
    USER_PASSWORD = USER_PASSWORD

    GUVI_BASE_URL = GUVI_BASE_URL
    GUVI_LOGIN_URL = GUVI_LOGIN_URL
    GUVI_CODEKATA_URL = GUVI_CODEKATA_URL
    ZENCLASS_BASE_URL = ZENCLASS_BASE_URL
    ZENCLASS_LOGIN_URL = ZENCLASS_LOGIN_URL
    ZENCLASS_TASKS_URL = ZENCLASS_TASKS_URL
    ZENCLASS_PROJECTS_URL = ZENCLASS_PROJECTS_URL
    ZENCLASS_DASHBOARD_URL = ZENCLASS_DASHBOARD_URL

    HEADLESS = HEADLESS
    CODEKATA_HEADLESS = CODEKATA_HEADLESS
    DEFAULT_CODEKATA_DIFFICULTIES = DEFAULT_CODEKATA_DIFFICULTIES
    VALID_CODEKATA_DIFFICULTIES = VALID_CODEKATA_DIFFICULTIES
    SLOW_MO = SLOW_MO
    NAVIGATION_TIMEOUT = NAVIGATION_TIMEOUT
    DEFAULT_TIMEOUT = DEFAULT_TIMEOUT

    BROWSER_ARGS = BROWSER_ARGS
    IGNORE_DEFAULT_ARGS = IGNORE_DEFAULT_ARGS

    DEFAULT_LANGUAGE = DEFAULT_LANGUAGE
    MAX_SUBMISSION_ATTEMPTS = MAX_SUBMISSION_ATTEMPTS
    LOCAL_TEST_TIMEOUT_SECONDS = LOCAL_TEST_TIMEOUT_SECONDS

    HITL_ALERT_BEEP = HITL_ALERT_BEEP
    HITL_POLL_INTERVAL_SECONDS = HITL_POLL_INTERVAL_SECONDS
    HITL_MAX_WAIT_SECONDS = HITL_MAX_WAIT_SECONDS

    LOG_LEVEL = LOG_LEVEL
    LOG_FORMAT = LOG_FORMAT
