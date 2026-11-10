# Handoff Report — Explorer M1-3: Human-in-the-Loop (HITL) Handler & Unified CLI Interface

**Agent ID**: `explorer_m1_3`  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_3/`  
**Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Milestone**: Milestone 1 (Core Foundation & Infrastructure)  
**Timestamp**: 2026-11-10T15:05:00Z  
**Handoff Type**: Hard (Task Complete)

---

## 1. Observation

Direct system inspection, requirement extraction, and reverse-engineered platform specifications from the workspace were analyzed:

1. **Requirement R1 (Foreground Platform Authentication and Interaction)**:
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (lines 18–21):
     > "Authenticate to Guvi and ZenClass using the provided credentials via a visible foreground browser window (headed mode) so execution can be monitored in real time. Never fabricate completion or attempt to bypass authentication, CAPTCHA, access controls, or assessment restrictions; immediately halt and prompt the user when human intervention (such as CAPTCHA or OTP verification) is required."
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (lines 36):
     > "Encountering CAPTCHA, OTP, or identity-sensitive assessment restrictions halts execution and prompts for human participation without fabricating results or attempting unauthorized bypass."

2. **Requirement R2 (Autonomous Problem and Task Completion & Project Pause Protocol)**:
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (lines 22–26):
     > "Discover and complete all pending and uncompleted items across Guvi CodeKata, ZenClass tasks, and ZenClass projects... For ZenClass projects requiring external repository creation or deployed application URLs, prepare all solution code locally and pause to prompt the user for repository hosting or deployment links."
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (line 37):
     > "For projects requiring external repository hosting or live deployment URLs, solution code is prepared locally and execution pauses with an explicit prompt for human input."

3. **Guvi Guardrails & DOM Signatures**:
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_2/handoff.md` (lines 18–19, 34, 57–73):
     - Account activation gate modal: `<div id="myModal">` with `<button id="sendmail">` triggered when login API returns `access: "activate"`, `access: "deleted"`, or `access: "notexist"`.
     - Cloudflare Turnstile & anti-bot challenge: Google reCAPTCHA v3 script (`render=6LdADb4UAAAAAA1feb36sozffPYRKKOqD9WPbibp`) and Cloudflare Turnstile iframes (`iframe[src*="challenges.cloudflare.com"]`, `div.cf-turnstile`, `#challenge-stage`).
     - Guided tour overlay: Dialogs `#welcome`, `#liveClass`, `#finish` (`That's It! You Are Ready!`).

4. **ZenClass Guardrails & Dynamic Field Signatures**:
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/handoff.md` (lines 46–49, 78–99):
     - MFA/OTP Step-up Auth: UI adds CSS class `login-mfa-active` and `login-mfa-wrapper` to `.login-content-wrapper` and renders challenge component `g.A` with `email` and `challenge`.
     - Dynamic 13-field project/task modal (Module 41486): Inputs with placeholder `Enter Link` inside `.submit-form-container-web`, mapped to keys:
       `frontEnd_Deployed_Url`, `backEnd_Deployed_Url`, `frontEnd_SourceCode`, `backEnd_SourceCode`, `github_Url`, `g-drive_Url`, `submission_Url`, `linkedin_post_Url`, `document_Url`, `figma_Url`, `figma_prototype_Url`, `dribble_Url`, `behance_Url`.
     - ZenClass Client-Side URL Regex: `/^(ftp|http|https):\/\/[^ "]+$/`. Invalid URLs show `.validation-error-text` with `"<Field Name> is not valid"`.

5. **Project Plan Interface Contracts**:
   - File: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md` (lines 65–68, 77–87):
     - Interface contract:
       ```python
       ### core/hitl_handler.py ↔ Drivers
       - check_and_handle_guardrails(page: Page) -> bool
       - request_project_links(project_title: str, project_id: str, local_code_dir: str, required_fields: List[str]) -> Dict[str, str]
       ```
     - CLI entrypoint: `main.py` supporting `run-all`, `run-codekata`, `run-zenclass`, `resume`, `report`.

---

## 2. Logic Chain

1. **Strict Compliance Policy with Zero Fabrication**:
   - From Observation 1, R1 strictly forbids attempting to solve CAPTCHAs via OCR hacks or third-party paid solving APIs, and forbids fabricating task completions.
   - From Observation 2, R2 requires local synthesis of full project deliverables in `projects/<project_slug>/`, followed by an interactive pause prompting the user for external GitHub repo and live deployment links.
   - *Inference*: `core/hitl_handler.py` must act as an unyielding security and ethics gatekeeper: whenever a challenge or external dependency is detected, it must halt automation, alert the user via terminal bell and visual formatting, wait for human resolution in the visible browser window or CLI, and verify resolution before allowing execution to proceed.

2. **DOM Guardrail Detection Architecture**:
   - From Observations 3 and 4, there are 6 distinct guardrail categories across Guvi and ZenClass:
     1. `CLOUDFLARE_TURNSTILE`: Cloudflare interstitial or challenge widget.
     2. `RECAPTCHA`: Google reCAPTCHA checkbox or challenge iframe.
     3. `OTP_CHALLENGE`: Standard OTP input fields during login.
     4. `ZENCLASS_MFA`: ZenClass `.login-mfa-active` element.
     5. `GUVI_ACTIVATION_MODAL`: Guvi `#myModal` activation requirement.
     6. `ACCOUNT_RESTRICTION`: Account disabled or assessment restriction notices.
   - *Inference*: The detection engine should maintain an extensible table of DOM selectors and evaluate them with short timeouts (e.g. 500ms) or via `page.query_selector`. If any selector matches, a `GuardrailEvent` dataclass is constructed describing the exact platform, challenge type, and user instructions.

3. **Multi-Modal Interactive Pause & Terminal Rendering**:
   - Users may be focused on the browser, a terminal, or another screen.
   - *Inference*: The pause mechanism must trigger:
     1. **Audible alert**: Emit terminal bell `\a` (ASCII 0x07) 3 times with a 200ms gap to ring the system alert bell on macOS.
     2. **Visual layout**: Render a distinct ANSI-bordered box (yellow for security challenges, cyan for project links) containing:
        - Challenge description and context
        - Exact instructions for the human
        - Action prompt (`[Enter]` to continue, `'skip'` to mark blocked, `'abort'` to exit)
     3. **URL Validation**: For project links, each input must be validated against the URL regex `/^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/` before returning, preventing submission rejection by ZenClass frontend (Observation 4).
     4. **JSON File Pre-fill Option**: Support an optional `--links-file links.json` parameter so power users or automated pipelines can provide project URLs non-interactively if desired.

4. **State Machine & Database Synchronization**:
   - Whenever an interactive pause begins, the handler must update the state database via `state_manager.update_task_status(...)` with `status="PAUSED_FOR_HUMAN"`, `failure_reason="Awaiting human resolution for <guardrail>"`.
   - When the user resumes and the guardrail is cleared, status returns to `IN_PROGRESS`. If the user skips or cancels, status transitions to `BLOCKED_HUMAN_REQUIRED`.

5. **Unified CLI Architecture (`main.py`)**:
   - From Observation 5, `main.py` needs 5 subcommands: `run-all`, `run-codekata`, `run-zenclass`, `resume`, `report`.
   - *Inference*: Using standard Python `argparse.ArgumentParser` with subparsers provides standard CLI ergonomics, `--help` generation, and shell script compatibility without external CLI dependencies.
   - `main.py` coordinates:
     - Configuration loading (`config.py`)
     - State management initialization (`data/automation_state.db`)
     - Persistent headed browser launch (`core/browser.py`)
     - Driver execution with HITL protection
     - Post-run reporting (`reports/SUMMARY_REPORT.md` and `reports/summary.json`)
     - Clean `SIGINT` (Ctrl+C) trap ensuring browser contexts close gracefully and SQLite state is saved.

---

## 3. Detailed Component Specifications

### 3.1 `core/hitl_handler.py` Specification

```python
"""
core/hitl_handler.py - Human-in-the-Loop (HITL) Handler
Ensures strict compliance with Requirements R1 & R2:
- Never fabricate completion or bypass authentication/CAPTCHA/OTP.
- Immediately halt and prompt the user when human intervention is required.
- Pause execution for ZenClass projects requiring external repo/deployment URLs.
"""

from __future__ import annotations
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger("hitl_handler")

class GuardrailType(str, Enum):
    CLOUDFLARE_TURNSTILE = "cloudflare_turnstile"
    RECAPTCHA = "recaptcha"
    OTP_CHALLENGE = "otp_challenge"
    ZENCLASS_MFA = "zenclass_mfa"
    GUVI_ACTIVATION_MODAL = "guvi_activation_modal"
    ACCOUNT_RESTRICTION = "account_restriction"
    GENERIC_BOT_CHECK = "generic_bot_check"

@dataclass
class GuardrailRule:
    guardrail_type: GuardrailType
    platform: str
    selector: str
    description: str
    instruction: str

@dataclass
class GuardrailEvent:
    guardrail_type: GuardrailType
    platform: str
    selector: str
    description: str
    instruction: str
    detected_at: float = 0.0

# Registered DOM guardrail rules
GUARDRAIL_RULES: List[GuardrailRule] = [
    # ZenClass MFA / Step-up authentication
    GuardrailRule(
        guardrail_type=GuardrailType.ZENCLASS_MFA,
        platform="zenclass",
        selector=".login-content-wrapper.login-mfa-active, .login-mfa-active, div.login-mfa-wrapper",
        description="ZenClass MFA / Two-Factor Authentication Challenge",
        instruction="Check your email or authenticator app, enter the MFA verification code in the browser, and submit."
    ),
    # Guvi Account Activation Gate
    GuardrailRule(
        guardrail_type=GuardrailType.GUVI_ACTIVATION_MODAL,
        platform="guvi",
        selector="#myModal, #myModal #sendmail, div.modal:has(#sendmail)",
        description="Guvi Account Activation / Verification Modal",
        instruction="Guvi requires account activation. Click 'Send Mail' or follow the instructions in the modal."
    ),
    # Cloudflare Turnstile & Cloudflare Challenge
    GuardrailRule(
        guardrail_type=GuardrailType.CLOUDFLARE_TURNSTILE,
        platform="any",
        selector="iframe[src*='challenges.cloudflare.com'], div.cf-turnstile, #cf-stage, #challenge-stage, div[id*='cf-turnstile']",
        description="Cloudflare Turnstile Verification / Bot Protection",
        instruction="Click the Cloudflare Turnstile checkbox in the visible browser window to verify humanity."
    ),
    # Google reCAPTCHA
    GuardrailRule(
        guardrail_type=GuardrailType.RECAPTCHA,
        platform="any",
        selector="iframe[src*='google.com/recaptcha'], iframe[src*='recaptcha/api2/anchor'], div.g-recaptcha",
        description="Google reCAPTCHA Verification",
        instruction="Solve the reCAPTCHA challenge displayed in the visible browser window."
    ),
    # Generic OTP / Verification code input
    GuardrailRule(
        guardrail_type=GuardrailType.OTP_CHALLENGE,
        platform="any",
        selector="input[name*='otp' i], input[placeholder*='OTP' i], #otp, input[autocomplete='one-time-code']",
        description="OTP / One-Time Passcode Request",
        instruction="Enter the OTP received on your mobile or email into the browser form."
    ),
    # ZenClass / Guvi Account Disabled or Restricted
    GuardrailRule(
        guardrail_type=GuardrailType.ACCOUNT_RESTRICTION,
        platform="any",
        selector="div:has-text('Account disabled'), div:has-text('Contact Coordinator'), div:has-text('Assessment restricted')",
        description="Platform Account Restriction / Assessment Locked",
        instruction="The platform has restricted this feature. Contact your coordinator or resolve access permissions."
    ),
]

URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https:// or ftp://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class HitlHandler:
    """
    Coordinates human intervention prompts, audible alerts, and project link acquisition.
    """

    def __init__(
        self,
        interactive: bool = True,
        audible_bell: bool = True,
        state_manager: Optional[Any] = None,
        links_file: Optional[str] = None,
    ):
        self.interactive = interactive
        self.audible_bell = audible_bell
        self.state_manager = state_manager
        self.links_file = links_file

    def emit_alert(self) -> None:
        """Emits audible terminal bells to alert the user."""
        if not self.audible_bell:
            return
        try:
            for _ in range(3):
                sys.stdout.write("\a")
                sys.stdout.flush()
                time.sleep(0.15)
        except Exception as e:
            logger.debug(f"Terminal bell failed: {e}")

    def render_box(
        self,
        title: str,
        lines: List[str],
        color: str = "yellow",
        min_width: int = 76,
    ) -> str:
        """
        Renders a visually prominent ANSI-colored terminal box.
        Colors: 'yellow', 'cyan', 'red', 'green'.
        """
        color_codes = {
            "yellow": "\033[1;33m",
            "cyan": "\033[1;36m",
            "red": "\033[1;31m",
            "green": "\033[1;32m",
            "reset": "\033[0m",
            "bold": "\033[1m",
        }
        c = color_codes.get(color, color_codes["yellow"])
        reset = color_codes["reset"]
        bold = color_codes["bold"]

        max_len = max([len(line) for line in lines] + [len(title)])
        width = max(max_len + 4, min_width)

        top = f"{c}╔{'═' * (width - 2)}╗{reset}"
        title_bar = f"{c}║{reset} {bold}{title.center(width - 4)}{reset} {c}║{reset}"
        divider = f"{c}╠{'═' * (width - 2)}╣{reset}"
        bottom = f"{c}╚{'═' * (width - 2)}╝{reset}"

        content_lines = []
        for line in lines:
            padded = line.ljust(width - 4)
            content_lines.append(f"{c}║{reset}  {padded[:width-4]}  {c}║{reset}")

        return "\n" + "\n".join([top, title_bar, divider] + content_lines + [bottom]) + "\n"

    def detect_guardrail(self, page: Any) -> Optional[GuardrailEvent]:
        """
        Inspects the active Playwright page DOM for any registered guardrails.
        Returns GuardrailEvent if detected, None otherwise.
        """
        try:
            # Check Cloudflare title or body text directly
            title = page.title() or ""
            if "Just a moment..." in title or "Attention Required!" in title:
                return GuardrailEvent(
                    guardrail_type=GuardrailType.CLOUDFLARE_TURNSTILE,
                    platform="cloudflare",
                    selector="title",
                    description="Cloudflare Security Interstitial Page",
                    instruction="Complete the Cloudflare verification challenge in the browser.",
                    detected_at=time.time(),
                )

            for rule in GUARDRAIL_RULES:
                element = page.query_selector(rule.selector)
                if element is not None:
                    # Verify element is visible
                    try:
                        if element.is_visible():
                            return GuardrailEvent(
                                guardrail_type=rule.guardrail_type,
                                platform=rule.platform,
                                selector=rule.selector,
                                description=rule.description,
                                instruction=rule.instruction,
                                detected_at=time.time(),
                            )
                    except Exception:
                        # Element exists in DOM
                        return GuardrailEvent(
                            guardrail_type=rule.guardrail_type,
                            platform=rule.platform,
                            selector=rule.selector,
                            description=rule.description,
                            instruction=rule.instruction,
                            detected_at=time.time(),
                        )
        except Exception as e:
            logger.debug(f"Guardrail DOM inspection exception: {e}")
        return None

    def check_and_handle_guardrails(
        self,
        page: Any,
        task_id: Optional[str] = None,
        context_desc: str = "Active Operation",
    ) -> bool:
        """
        Implements Requirement R1:
        Checks for security challenges, MFA, OTP, or activation gates.
        If detected:
          1. Alerts user with audible bell.
          2. Renders prominent terminal warning box.
          3. Prompts user to resolve it in the visible browser.
          4. Re-verifies resolution before proceeding.
        Returns True if a guardrail was detected and resolved; False if none was detected.
        Raises RuntimeError or returns False if non-interactive or user aborted.
        """
        event = self.detect_guardrail(page)
        if not event:
            return False

        logger.warning(f"Guardrail detected: {event.description} (type={event.guardrail_type})")
        self.emit_alert()

        # Update state manager if attached
        if self.state_manager and task_id:
            try:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status="PAUSED_FOR_HUMAN",
                    failure_reason=f"Blocked by {event.description}",
                    next_action="Awaiting human resolution in foreground browser",
                )
            except Exception as e:
                logger.warning(f"Failed to record state pause: {e}")

        box = self.render_box(
            title="⚠️  HUMAN INTERVENTION REQUIRED (R1 GUARDRAIL)  ⚠️",
            lines=[
                f"Platform:    {event.platform.upper()}",
                f"Challenge:   {event.description}",
                f"Context:     {context_desc}",
                f"URL:         {page.url}",
                "",
                "ACTION REQUIRED IN FOREGROUND BROWSER:",
                f"  -> {event.instruction}",
                "",
                "The browser window is open on your desktop. Solve the challenge",
                "manually. Automation will NOT attempt bypass or falsify completion.",
            ],
            color="yellow",
        )
        print(box, file=sys.stderr)

        if not self.interactive:
            logger.error("Non-interactive mode active: cannot pause for human. Marking task blocked.")
            if self.state_manager and task_id:
                self.state_manager.update_task_status(
                    task_id=task_id,
                    status="BLOCKED_HUMAN_REQUIRED",
                    failure_reason=f"Unresolved {event.description} in non-interactive run",
                )
            return False

        # Interactive resolution loop
        while True:
            try:
                choice = input(">> Press [Enter] after completing in browser (or type 'skip'/'abort'): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n[HITL] Aborted by user interrupt.")
                sys.exit(130)

            if choice.lower() == "abort":
                logger.info("User requested execution abort.")
                sys.exit(0)
            elif choice.lower() == "skip":
                logger.warning(f"User chose to skip task {task_id}.")
                if self.state_manager and task_id:
                    self.state_manager.update_task_status(
                        task_id=task_id,
                        status="BLOCKED_HUMAN_REQUIRED",
                        failure_reason=f"User skipped {event.description}",
                    )
                return False

            # Verify that guardrail is cleared
            time.sleep(1.0)
            remaining_event = self.detect_guardrail(page)
            if remaining_event is None:
                print("\033[1;32m[HITL] Verification successful! Challenge cleared. Resuming automation...\033[0m\n")
                if self.state_manager and task_id:
                    self.state_manager.update_task_status(
                        task_id=task_id,
                        status="IN_PROGRESS",
                        next_action="Resumed after human verification",
                    )
                return True
            else:
                print(f"\033[1;31m[HITL] Guardrail still present ({remaining_event.description}). Please complete the action in the browser.\033[0m")

    def request_project_links(
        self,
        project_title: str,
        project_id: str,
        local_code_dir: str,
        required_fields: List[str],
        links_file: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Implements Requirement R2:
        Pauses execution when a ZenClass project requires external repository
        or deployment links.
        1. Emits audible alert and displays local code path and required links.
        2. Checks links_file (if provided or present in config).
        3. Prompts user interactively for each required field, with URL validation.
        Returns a dictionary mapping required field names to valid URLs.
        """
        logger.info(f"Requesting project submission links for '{project_title}' ({project_id})")
        self.emit_alert()

        # Check pre-filled links file first
        target_links_file = links_file or self.links_file
        prefilled_links: Dict[str, str] = {}
        if target_links_file and os.path.exists(target_links_file):
            try:
                with open(target_links_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if project_id in data:
                        prefilled_links = data[project_id]
                    elif project_title in data:
                        prefilled_links = data[project_title]
                    elif "default" in data:
                        prefilled_links = data["default"]
                    else:
                        prefilled_links = data
            except Exception as e:
                logger.warning(f"Failed to read links file {target_links_file}: {e}")

        # If all required fields are pre-filled and valid, return immediately
        if prefilled_links and all(f in prefilled_links and self.validate_url(prefilled_links[f]) for f in required_fields):
            logger.info("All required project links satisfied via pre-filled links configuration.")
            return {f: prefilled_links[f] for f in required_fields}

        box = self.render_box(
            title="📦  ZENCLASS PROJECT DEPLOYMENT LINKS REQUIRED (R2)  📦",
            lines=[
                f"Project Title:   {project_title}",
                f"Project ID:      {project_id}",
                f"Local Code:      {local_code_dir}",
                "",
                "All solution code, dependencies, and README have been generated",
                "and validated locally in the directory above.",
                "",
                "STEPS TO COMPLETE:",
                "  1. Create a GitHub repository and push the code from the directory above.",
                "  2. Deploy frontend to Netlify/Vercel and backend to Render/Railway (if applicable).",
                "  3. Enter the active repository and deployment URLs below.",
            ],
            color="cyan",
        )
        print(box, file=sys.stderr)

        if not self.interactive:
            raise RuntimeError(
                f"Non-interactive run cannot supply project links for '{project_title}'. "
                f"Provide --links-file or run interactively."
            )

        collected_links: Dict[str, str] = {}
        for field in required_fields:
            field_label = field.replace("_", " ").title()
            default_val = prefilled_links.get(field, "")

            while True:
                prompt_msg = f">> Enter {field_label}"
                if default_val:
                    prompt_msg += f" [{default_val}]"
                prompt_msg += ": "

                try:
                    val = input(prompt_msg).strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n[HITL] Aborted by user interrupt.")
                    sys.exit(130)

                if not val and default_val:
                    val = default_val

                if self.validate_url(val):
                    collected_links[field] = val
                    break
                else:
                    print(
                        f"\033[1;31m  Invalid URL '{val}'. Must start with http:// or https:// and contain a valid domain.\033[0m"
                    )

        print("\033[1;32m[HITL] All project links verified! Proceeding with platform submission...\033[0m\n")
        return collected_links

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validates that a URL is non-empty and well-formed."""
        if not url or not isinstance(url, str):
            return False
        return bool(URL_REGEX.match(url.strip()))
```

---

### 3.2 Unified CLI Interface (`main.py`) Specification

```python
"""
main.py - ZenClass & Guvi CodeKata Automation Suite CLI Entrypoint

Commands:
  run-all         Execute Guvi CodeKata, ZenClass tasks, and ZenClass projects
  run-codekata    Execute Guvi CodeKata automation only
  run-zenclass    Execute ZenClass automation (tasks, projects, or both)
  resume          Resume execution from saved SQLite state (pending/blocked items)
  report          Generate Markdown & JSON summary reports without launching browser
"""

from __future__ import annotations
import argparse
import logging
import os
import signal
import sys
import time
from typing import List, Optional

# Import configuration and core components
# from config import Config
# from core.browser import BrowserManager
# from core.state_manager import StateManager
# from core.hitl_handler import HitlHandler
# from core.reporter import Reporter
# from drivers.guvi_driver import GuviDriver
# from drivers.zenclass_driver import ZenClassDriver

logger = logging.getLogger("automation_cli")


def setup_logging(level_name: str = "INFO") -> None:
    """Configures structured, colored CLI logging."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


def create_cli_parser() -> argparse.ArgumentParser:
    """Constructs the argument parser with subcommands and options."""
    parser = argparse.ArgumentParser(
        prog="zenclass_guvi",
        description="Autonomous ZenClass & Guvi CodeKata Automation Suite (R1, R2, R3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default: False, headed foreground as per R1)",
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=50,
        help="Playwright slow_mo delay in milliseconds (default: 50ms)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of problems/tasks to attempt in this run",
    )
    parser.add_argument(
        "--interactive",
        dest="interactive",
        action="store_true",
        default=True,
        help="Enable interactive terminal prompts for CAPTCHA/MFA and project URLs (default: True)",
    )
    parser.add_argument(
        "--no-interactive",
        dest="interactive",
        action="store_false",
        help="Disable interactive terminal prompts (mark HITL tasks as blocked)",
    )
    parser.add_argument(
        "--links-file",
        type=str,
        default=None,
        help="Path to JSON file containing pre-filled repository and deployment links",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/automation_state.db",
        help="Path to SQLite persistent state tracking database",
    )
    parser.add_argument(
        "--reports-dir",
        type=str,
        default="reports",
        help="Directory to write executive Markdown and JSON reports",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity level (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Automation commands")

    # Command: run-all
    p_run_all = subparsers.add_parser(
        "run-all",
        help="Run full automation pipeline across Guvi CodeKata, ZenClass tasks, and projects",
    )
    p_run_all.add_argument(
        "--order",
        choices=["codekata-first", "zenclass-first"],
        default="codekata-first",
        help="Execution order between platforms (default: codekata-first)",
    )

    # Command: run-codekata
    p_codekata = subparsers.add_parser(
        "run-codekata",
        help="Run Guvi CodeKata automation (discovery, solver, sandbox, submission)",
    )
    p_codekata.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter CodeKata problems by category/topic (e.g., 'Basics', 'Strings')",
    )
    p_codekata.add_argument(
        "--task-id",
        type=str,
        default=None,
        help="Execute single CodeKata problem by slug or title",
    )

    # Command: run-zenclass
    p_zenclass = subparsers.add_parser(
        "run-zenclass",
        help="Run ZenClass tasks and/or projects automation",
    )
    p_zenclass.add_argument(
        "--type",
        choices=["tasks", "projects", "all"],
        default="all",
        help="Scope of ZenClass automation: tasks, projects, or all (default: all)",
    )
    p_zenclass.add_argument(
        "--task-id",
        type=str,
        default=None,
        help="Execute single ZenClass task or project by ID",
    )

    # Command: resume
    p_resume = subparsers.add_parser(
        "resume",
        help="Resume execution from SQLite state for pending, failed, or blocked tasks",
    )
    p_resume.add_argument(
        "--platform",
        choices=["all", "guvi", "zenclass"],
        default="all",
        help="Filter platform to resume (default: all)",
    )
    p_resume.add_argument(
        "--include-failed",
        action="store_true",
        default=True,
        help="Retry failed tasks in addition to pending/blocked tasks (default: True)",
    )

    # Command: report
    p_report = subparsers.add_parser(
        "report",
        help="Generate Markdown & JSON summary reports from database without launching browser",
    )

    return parser


class AutomationRunner:
    """Lifecycle controller managing browser, state, drivers, and shutdown signals."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.browser_manager = None
        self.state_manager = None
        self.hitl_handler = None
        self.reporter = None
        self._shutdown_registered = False

    def register_signal_handlers(self) -> None:
        """Gracefully catches SIGINT (Ctrl+C) and SIGTERM."""
        def handle_sigint(signum, frame):
            print("\n\033[1;33m[SHUTDOWN] Interrupt signal caught. Gracefully saving state and closing browser...\033[0m")
            self.cleanup()
            sys.exit(130)

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigint)
        self._shutdown_registered = True

    def initialize_services(self) -> None:
        """Initializes configuration, state database, and reporting."""
        setup_logging(self.args.log_level)
        self.register_signal_handlers()

        # In full implementation:
        # self.state_manager = StateManager(db_path=self.args.db_path)
        # self.hitl_handler = HitlHandler(
        #     interactive=self.args.interactive,
        #     state_manager=self.state_manager,
        #     links_file=self.args.links_file,
        # )
        # self.reporter = Reporter(
        #     state_manager=self.state_manager,
        #     output_dir=self.args.reports_dir,
        # )
        logger.info(f"Initialized state tracking: {self.args.db_path}")

    def initialize_browser(self) -> None:
        """Launches persistent headed browser session."""
        logger.info(f"Launching browser (headless={self.args.headless}, slow_mo={self.args.slow_mo}ms)...")
        # In full implementation:
        # self.browser_manager = BrowserManager(headless=self.args.headless, slow_mo=self.args.slow_mo)
        # self.browser_manager.launch()

    def cleanup(self) -> None:
        """Flushes state and closes browser profile cleanly."""
        try:
            if self.browser_manager:
                logger.info("Closing browser context (preserving cookies and profile)...")
                # self.browser_manager.close_context()
            if self.state_manager:
                logger.info("Exporting atomic JSON state summary...")
                # self.state_manager.export_state_json()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def execute(self) -> int:
        """Dispatches command to relevant drivers and produces summary report."""
        if not self.args.command:
            print("No command specified. Use --help for usage.")
            return 1

        self.initialize_services()

        # Fast path: report-only does not require browser initialization
        if self.args.command == "report":
            logger.info("Generating summary reports from state database...")
            # report_path = self.reporter.generate_markdown_report()
            # json_path = self.reporter.generate_json_summary()
            # print(f"Report generated: {report_path}")
            return 0

        # Launch headed browser for automation commands
        self.initialize_browser()
        try:
            if self.args.command == "run-all":
                logger.info("Starting run-all automation pipeline...")
                # execute_guvi_codekata(...)
                # execute_zenclass(...)

            elif self.args.command == "run-codekata":
                logger.info(f"Starting CodeKata automation (limit={self.args.limit})...")
                # execute_guvi_codekata(...)

            elif self.args.command == "run-zenclass":
                logger.info(f"Starting ZenClass automation (type={self.args.type})...")
                # execute_zenclass(...)

            elif self.args.command == "resume":
                logger.info(f"Resuming automation from state database (platform={self.args.platform})...")
                # resume_pending_tasks(...)

            # Generate final reports on completion
            # self.reporter.generate_markdown_report()
            # self.reporter.generate_json_summary()
            return 0

        except Exception as e:
            logger.exception(f"Unhandled error during execution: {e}")
            return 1
        finally:
            self.cleanup()


def main() -> None:
    parser = create_cli_parser()
    args = parser.parse_args()
    runner = AutomationRunner(args)
    sys.exit(runner.execute())


if __name__ == "__main__":
    main()
```

---

## 4. Error Handling and Edge Cases

| Edge Case | Risk / Impact | Design Mitigation in HITL / CLI |
|---|---|---|
| **Cloudflare Turnstile Appears Mid-Session** | Execution hangs waiting for elements behind challenge | `check_and_handle_guardrails` called before critical actions; emits `\a`, renders warning box, awaits human resolution, re-checks DOM. |
| **ZenClass `.login-mfa-active` Triggered** | Login fails with timeout or unhandled exception | Guardrail rule detects `.login-mfa-active`; halts immediately; prompts user to submit MFA in browser; resumes only when dashboard is mounted. |
| **Guvi `#myModal` Activation Gate** | Account cannot solve problems or browse catalog | Guardrail rule identifies `#myModal`; pauses runner; instructs human to activate or resolve account status. |
| **Malformed Project Link Input** | ZenClass frontend regex `/^(ftp\|http\|https):\/\/[^ "]+$/` rejects form with inline red error | `request_project_links` executes regex validation loop before returning URLs to driver; rejects non-URL inputs immediately in CLI. |
| **User Presses Ctrl+C (SIGINT)** | Abrupt crash could corrupt SQLite database or leave browser profile locked | `AutomationRunner` traps `SIGINT`, flushes atomic JSON state export, calls `browser.close_context()`, and exits with code 130. |
| **Non-Interactive Execution (`--no-interactive`)** | Script could block indefinitely on `input()` | `HitlHandler` checks `self.interactive`. In non-interactive mode, records task as `BLOCKED_HUMAN_REQUIRED`, logs explanation, and skips task cleanly. |
| **Pre-filled URLs Available (`--links-file`)** | Unnecessary interactive prompt when URLs are known | `request_project_links` checks `--links-file` first. If all required keys are present and valid, returns without pausing. |

---

## 5. Caveats

- In accordance with team explorer rules, this design is read-only. No code modifications to the `zenclass_guvi/` folder have been written.
- The `HitlHandler` relies on visible foreground browser execution (`headless=False`) as mandated by Requirement R1. In true headless mode, human interaction in the browser viewport is impossible, which is why `--headless` defaults to `False`.
- Quizzes, HYREX assessments, and PET items appearing in ZenClass Tasks feed redirect to external third-party testing domains; the HITL handler or ZenClass driver must flag these as `BLOCKED_EXTERNAL_ASSESSMENT` rather than treating them as standard tasks.

---

## 6. Conclusion

The Human-in-the-Loop Handler (`core/hitl_handler.py`) and Unified CLI Interface (`main.py`) designs strictly fulfill Requirements R1, R2, and R3:
1. **Zero Fabrication & Zero Bypass (R1)**: Clear architecture that detects Cloudflare Turnstile, reCAPTCHA, OTP, ZenClass `.login-mfa-active`, and Guvi `#myModal`, halts automation immediately, and waits for human resolution.
2. **Interactive Project Protocol (R2)**: Standardized pause procedure with terminal bell (`\a`), ANSI-bordered instruction box, and URL-validated CLI prompts for ZenClass repository and deployment links.
3. **Ergonomic CLI (`main.py`)**: Subcommands `run-all`, `run-codekata`, `run-zenclass`, `resume`, `report` with robust arguments, signal handling, and clean reporting hooks.

---

## 7. Verification Method

To independently verify this design:
1. Inspect the handoff document:
   ```bash
   cat /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_3/handoff.md
   ```
2. Verify syntax and type annotations of proposed classes using Python 3:
   ```bash
   python3 -m py_compile /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m1_3/handoff.md  # (Extract snippets or run when implemented)
   ```
3. When implemented in `zenclass_guvi/core/hitl_handler.py` and `zenclass_guvi/main.py`, test the CLI and HITL handler using:
   ```bash
   python3 zenclass_guvi/main.py --help
   python3 zenclass_guvi/main.py run-all --help
   python3 zenclass_guvi/main.py report --help
   pytest zenclass_guvi/tests/e2e/tier1_features/
   ```
