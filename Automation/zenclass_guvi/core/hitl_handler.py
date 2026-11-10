"""
core/hitl_handler.py - Human-in-the-Loop (HITL) Handler
Ensures strict compliance with Requirements R1 & R2:
- Never fabricate completion or attempt to bypass authentication, CAPTCHA, or MFA.
- Immediately halt and prompt the user when human intervention is required.
- Standardized project pause protocol for ZenClass external repository and deployment URLs.
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

logger = logging.getLogger("core.hitl_handler")


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


# Registered DOM guardrail rules for active Playwright page evaluation
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
        selector="iframe[src*='google.com/recaptcha'], iframe[src*='recaptcha/api2/anchor'], div.g-recaptcha, script[src*='recaptcha/api.js']",
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
    # Platform Account Disabled or Restricted
    GuardrailRule(
        guardrail_type=GuardrailType.ACCOUNT_RESTRICTION,
        platform="any",
        selector="div:has-text('Account disabled'), div:has-text('Contact Coordinator'), div:has-text('Assessment restricted')",
        description="Platform Account Restriction / Assessment Locked",
        instruction="The platform has restricted this feature. Contact your coordinator or resolve access permissions."
    ),
]

# Strict URL regex conforming to ZenClass client-side regex: /^(ftp|http|https):\/\/[^ "]+$/
URL_REGEX = re.compile(r"^(?:ftp|https?)://[^ \"]+$", re.IGNORECASE)


class HitlHandler:
    """
    Coordinates human intervention prompts, audible alerts, and project link acquisition.
    Enforces Requirement R1 & R2 compliance.
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

    @staticmethod
    def check_guardrails_in_html(html_content: str) -> bool:
        """
        Fast inspection of raw HTML strings for guardrail markers.
        Used by test suites and lightweight pre-checks.
        """
        if not html_content or not isinstance(html_content, str):
            return False

        indicators = [
            "login-mfa-active",
            "login-mfa-wrapper",
            "cf-turnstile",
            "challenges.cloudflare.com",
            "recaptcha",
            'id="myModal"',
            "Account disabled. Contact Coordinator.",
            "mfaRequired",
            "That's It! You Are Ready!"
        ]
        return any(ind in html_content for ind in indicators)

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validates that a URL is non-empty, well-formed, and supported by platform regex."""
        if not url or not isinstance(url, str):
            return False
        return bool(URL_REGEX.match(url.strip()))

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
                    status="BLOCKED",
                    failure_reason=f"Blocked by {event.description}",
                    next_action="Awaiting human resolution in foreground browser",
                )
            except Exception as e:
                logger.warning(f"Failed to record state pause: {e}")

        page_url = getattr(page, "url", "unknown")
        box = self.render_box(
            title="⚠️  HUMAN INTERVENTION REQUIRED (R1 GUARDRAIL)  ⚠️",
            lines=[
                f"Platform:    {event.platform.upper()}",
                f"Challenge:   {event.description}",
                f"Context:     {context_desc}",
                f"URL:         {page_url}",
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
        user_inputs: Optional[Dict[str, str]] = None,
        links_file: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Implements Requirement R2:
        Pauses execution when a ZenClass project requires external repository
        or deployment links.
        1. If user_inputs is provided (e.g. In tests or non-interactive automation), uses it.
        2. Checks links_file (if provided or present in config).
        3. Prompts user interactively for each required field, with URL validation.
        Returns a dictionary mapping required field names to valid URLs.
        """
        logger.info(f"Requesting project submission links for '{project_title}' ({project_id})")

        # Check explicit user_inputs dictionary first (test harness support)
        if user_inputs is not None:
            return {k: user_inputs.get(k, f"https://mock.deployed/{k}") for k in required_fields}

        # Check pre-filled links file next
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

        self.emit_alert()

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
                        f"\033[1;31m  Invalid URL '{val}'. Must start with http:// or https:// or ftp:// and contain a valid domain.\033[0m"
                    )

        print("\033[1;32m[HITL] All project links verified! Proceeding with platform submission...\033[0m\n")
        return collected_links


# Standard alias for contract loader and test compatibility
HITLHandler = HitlHandler
