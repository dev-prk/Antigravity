"""
aios/policy.py - AI-OS Policy Engine & Immutable Kernel Guardrails.

Strictly Python 3.9 standard library only.
Provides user-configurable governance profiles (READ_ONLY, SANDBOX_AUTONOMOUS,
WORKSPACE_AUTONOMOUS, APPROVAL_REQUIRED, RESTRICTED) with non-configurable
immutable kernel guardrails (secret redaction, external destructive blocking).
"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class Decision:
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"


class Action:
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    INSTALL = "install"
    NETWORK = "network"
    EXTERNAL = "external"
    PRODUCTION = "production"

    ALL_ACTIONS = {
        READ,
        WRITE,
        DELETE,
        EXECUTE,
        INSTALL,
        NETWORK,
        EXTERNAL,
        PRODUCTION,
    }


class PolicyViolationError(Exception):
    """Raised when an operation violates mandatory policy guardrails."""
    pass


@dataclass(frozen=True)
class PolicyDecision:
    """Represents the evaluated outcome of a policy check."""
    decision: str
    action_type: str
    target_resource: str
    profile: str
    allowed: bool
    reason: str
    guardrail_enforced: bool = False
    modified_by_guardrail: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandResult:
    """Represents the result of a policy-governed shell command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float = 0.0
    executed: bool = True
    denial_reason: Optional[str] = None
    blocked: bool = False


class PolicyEngine:
    """
    PolicyEngine enforces governance profiles and immutable kernel guardrails.

    - User-configurable profiles: READ_ONLY, SANDBOX_AUTONOMOUS, WORKSPACE_AUTONOMOUS,
      APPROVAL_REQUIRED, RESTRICTED.
    - Immutable Kernel Guardrails:
      1. Non-configurable secret redaction ([REDACTED_SECRET]).
      2. Non-configurable prohibition of unapproved destructive actions outside workspace.
    """

    DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
        "READ_ONLY": {
            "description": "Read-only inspection and evaluation. Mutations and executions denied.",
            "permissions": {
                "read": "ALLOW",
                "write": "DENY",
                "delete": "DENY",
                "execute": "DENY",
                "install": "DENY",
                "network": "DENY",
                "external": "DENY",
                "production": "DENY",
            },
        },
        "SANDBOX_AUTONOMOUS": {
            "description": "Autonomous execution restricted strictly to temporary sandbox.",
            "permissions": {
                "read": "ALLOW",
                "write": "ALLOW",
                "delete": "ALLOW",
                "execute": "ALLOW",
                "install": "ASK",
                "network": "ASK",
                "external": "DENY",
                "production": "DENY",
            },
        },
        "WORKSPACE_AUTONOMOUS": {
            "description": "Default autonomous mode within the AI-OS workspace root.",
            "permissions": {
                "read": "ALLOW",
                "write": "ALLOW",
                "delete": "ALLOW",
                "execute": "ALLOW",
                "install": "ASK",
                "network": "ASK",
                "external": "ASK",
                "production": "DENY",
            },
        },
        "APPROVAL_REQUIRED": {
            "description": "Supervised mode: mutations and executions require confirmation.",
            "permissions": {
                "read": "ALLOW",
                "write": "ASK",
                "delete": "ASK",
                "execute": "ASK",
                "install": "ASK",
                "network": "ASK",
                "external": "ASK",
                "production": "DENY",
            },
        },
        "RESTRICTED": {
            "description": "Emergency lockdown mode. All actions denied except reading logs.",
            "permissions": {
                "read": "ALLOW",
                "write": "DENY",
                "delete": "DENY",
                "execute": "DENY",
                "install": "DENY",
                "network": "DENY",
                "external": "DENY",
                "production": "DENY",
            },
        },
    }

    FORBIDDEN_COMMANDS: Set[str] = {
        "sudo", "su", "mkfs", "dd", "shutdown", "reboot", "poweroff", "init", ":(){ :|:& };:"
    }

    DESTRUCTIVE_COMMANDS: Set[str] = {
        "rm", "rmdir", "unlink", "truncate", "srm"
    }

    def __init__(
        self,
        config_path: Optional[str] = None,
        workspace_root: Optional[str] = None,
        enable_redaction: bool = True,
        config_dict: Optional[Dict[str, Any]] = None,
    ):
        self.workspace_root = Path(
            workspace_root or "~/Documents/Antigravity/AI-OS"
        ).expanduser().resolve()
        self.sandbox_dir = Path("/tmp/aios_sandbox").expanduser().resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

        # Kernel Guardrail Invariant: Secret redaction cannot be disabled
        self.secret_redaction: bool = True
        self.force_secret_redaction: bool = True

        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_policies(self.config_path, config_dict)
        self.active_profile = self.config.get("active_profile", "WORKSPACE_AUTONOMOUS")

    def _load_policies(
        self,
        path: Optional[Path],
        config_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Loads configuration from dict, file, or default fallback."""
        base_defaults: Dict[str, Any] = {
            "version": "1.0.0",
            "active_profile": "WORKSPACE_AUTONOMOUS",
            "workspace_root": str(self.workspace_root),
            "sandbox_dir": str(self.sandbox_dir),
            "redaction_enabled": True,
            "profiles": dict(self.DEFAULT_PROFILES),
        }

        if config_dict and isinstance(config_dict, dict):
            # Merge config_dict into defaults
            merged = dict(base_defaults)
            if "profiles" in config_dict:
                for k, v in config_dict["profiles"].items():
                    merged["profiles"][k] = v
            for k, v in config_dict.items():
                if k != "profiles":
                    merged[k] = v
            return merged

        if path and path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "profiles" in data and isinstance(data["profiles"], dict):
                    merged = dict(base_defaults)
                    merged.update(data)
                    return merged
            except Exception:
                pass

        return base_defaults

    def is_path_in_workspace(self, path: Union[str, Path]) -> bool:
        """Determines if target path is safely contained within workspace root."""
        return self._is_subpath(Path(path), self.workspace_root)

    def is_path_in_sandbox(self, path: Union[str, Path]) -> bool:
        """Determines if target path is safely contained within sandbox directory."""
        return self._is_subpath(Path(path), self.sandbox_dir)

    def _is_subpath(self, target: Path, base: Path) -> bool:
        """
        Robust canonical subpath check handling traversal, symlinks, and Darwin casing.
        """
        try:
            target_expanded = target.expanduser()
            base_expanded = base.expanduser()

            if not target_expanded.is_absolute():
                t_resolved = (base_expanded / target_expanded).resolve()
            else:
                t_resolved = target_expanded.resolve()

            b_resolved = base_expanded.resolve()

            # Direct root or empty checks
            if str(t_resolved) in ("/", "/Users", "/Users/devesh", "/etc", "/var", "/private/var"):
                if str(b_resolved) not in (str(t_resolved)):
                    return False

            # Commonpath comparison
            common = os.path.commonpath([
                os.path.realpath(str(t_resolved)),
                os.path.realpath(str(b_resolved)),
            ])
            if common != os.path.realpath(str(b_resolved)):
                return False

            # Case-normalization comparison across path parts
            t_parts = [p.lower() for p in t_resolved.parts]
            b_parts = [p.lower() for p in b_resolved.parts]
            return len(t_parts) >= len(b_parts) and t_parts[:len(b_parts)] == b_parts
        except Exception:
            return False

    def _inspect_command_safety(self, command_str: str, profile_name: str) -> Tuple[bool, str]:
        """
        Inspects shell command for forbidden utilities, destructive flags, or external escapes.
        """
        cmd_stripped = command_str.strip()

        # Check raw string signatures
        if ":(){ :|:& };:" in cmd_stripped:
            return False, "Fork bomb detected"

        if "> /dev/" in cmd_stripped:
            return False, "Direct disk redirection detected"

        # Check chained command segments
        segments = re.split(r';|&&|\|\||\||&', cmd_stripped)
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue

            # Tokenize segment
            try:
                tokens = shlex.split(seg)
            except ValueError:
                tokens = seg.split()

            if not tokens:
                continue

            base_cmd = tokens[0].lower()
            if base_cmd in self.FORBIDDEN_COMMANDS:
                return False, f"Forbidden system command '{base_cmd}'"

            # Check for chmod on root
            if base_cmd == "chmod":
                args = tokens[1:]
                if "-R" in args or "-r" in args:
                    for arg in args:
                        if arg in ("/", "/*", "/etc", "/var", "~", "~/*"):
                            return False, f"Recursive chmod on protected directory '{arg}'"

            # Check for mkfs / dd
            if base_cmd.startswith("mkfs") or base_cmd == "dd":
                return False, f"Destructive storage command '{base_cmd}'"

            # Check destructive file removals
            if base_cmd in self.DESTRUCTIVE_COMMANDS:
                paths = [t for t in tokens[1:] if not t.startswith("-")]
                for p in paths:
                    # Root / home / system directory checks
                    if p in ("/", "/*", "~", "~/*", "/tmp", "/tmp/*", "/etc", "/var"):
                        return False, f"Destructive command targeting system directory '{p}'"

                    p_path = Path(p)
                    if profile_name == "SANDBOX_AUTONOMOUS":
                        contained = self.is_path_in_sandbox(p_path)
                    else:
                        contained = self.is_path_in_workspace(p_path)

                    if not contained:
                        return False, f"Destructive command targeting path outside workspace: '{p}'"

        return True, "Safe"

    def check_action(
        self,
        action_type: str,
        target_resource: str,
        profile_override: Optional[str] = None,
    ) -> PolicyDecision:
        """
        Evaluates permissions for an action against the active profile and kernel guardrails.
        """
        action = action_type.strip().lower()
        if action not in Action.ALL_ACTIONS:
            return PolicyDecision(
                decision=Decision.DENY,
                action_type=action,
                target_resource=target_resource,
                profile=profile_override or self.active_profile,
                allowed=False,
                reason=f"Unknown or invalid action type '{action_type}'",
                guardrail_enforced=True,
                modified_by_guardrail=True,
            )

        profile_name = profile_override or self.active_profile
        profiles = self.config.get("profiles", {})
        if profile_name not in profiles:
            profile_name = "WORKSPACE_AUTONOMOUS"

        profile_data = profiles.get(profile_name, {})
        # Support both {"permissions": {...}} and flat {"delete": "ALLOW"}
        perms = profile_data.get("permissions", profile_data)
        baseline_decision = perms.get(action, Decision.DENY)
        if isinstance(baseline_decision, dict):
            baseline_decision = baseline_decision.get(action, Decision.DENY)

        # -----------------------------------------------------------------
        # Kernel Guardrail 1: External Destructive Actions (Write & Delete)
        # -----------------------------------------------------------------
        if action in (Action.DELETE, Action.WRITE):
            target_path = Path(target_resource)
            if profile_name == "SANDBOX_AUTONOMOUS":
                contained = self.is_path_in_sandbox(target_path)
            else:
                contained = self.is_path_in_workspace(target_path)

            if not contained:
                # If baseline allowed, kernel guardrail forcibly demotes to ASK or DENY
                modified = (baseline_decision == Decision.ALLOW)
                enforced_decision = Decision.ASK if baseline_decision == Decision.ALLOW else baseline_decision
                return PolicyDecision(
                    decision=enforced_decision,
                    action_type=action,
                    target_resource=target_resource,
                    profile=profile_name,
                    allowed=(enforced_decision == Decision.ALLOW),
                    reason="Kernel Guardrail: Destructive action outside workspace cannot be auto-approved",
                    guardrail_enforced=True,
                    modified_by_guardrail=modified,
                )

        # -----------------------------------------------------------------
        # Kernel Guardrail 2: Command Execution Safety
        # -----------------------------------------------------------------
        if action == Action.EXECUTE:
            is_safe, violation_reason = self._inspect_command_safety(target_resource, profile_name)
            if not is_safe:
                return PolicyDecision(
                    decision=Decision.DENY,
                    action_type=action,
                    target_resource=target_resource,
                    profile=profile_name,
                    allowed=False,
                    reason=f"Kernel Guardrail: {violation_reason}",
                    guardrail_enforced=True,
                    modified_by_guardrail=True,
                )

        # Return baseline evaluated decision
        return PolicyDecision(
            decision=baseline_decision,
            action_type=action,
            target_resource=target_resource,
            profile=profile_name,
            allowed=(baseline_decision == Decision.ALLOW),
            reason=f"Profile '{profile_name}' permits action '{action}'"
            if baseline_decision == Decision.ALLOW
            else f"Profile '{profile_name}' restricts action '{action}'",
            guardrail_enforced=False,
            modified_by_guardrail=False,
        )

    def redact_secrets(self, text: str) -> str:
        """
        Non-configurable secret redaction engine.
        Replaces API keys, tokens, credentials, private keys, and passwords
        with the token [REDACTED_SECRET].
        """
        if not text:
            return ""

        out = text

        # 1. Redact PEM Private Key Blocks
        out = re.sub(
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----',
            '[REDACTED_SECRET]',
            out,
        )

        # 2. Redact URI Passwords (protocol://user:password@host...)
        out = re.sub(
            r'([a-zA-Z][a-zA-Z0-9+.-]*://[^:\s/@]+:)([^@\s/]+)(@)',
            r'\1[REDACTED_SECRET]\3',
            out,
        )

        # 3. Redact Bearer Tokens
        out = re.sub(
            r'(?i)\b(bearer\s+)[a-zA-Z0-9_\-\.]{20,}',
            r'\1[REDACTED_SECRET]',
            out,
        )

        # 4. Redact Key-Value Assignments
        def _kv_repl(m):
            val = m.group(2)
            if val == "[REDACTED_SECRET]":
                return m.group(0)
            return f"{m.group(1)}[REDACTED_SECRET]{m.group(3)}"

        out = re.sub(
            r'(?i)(["\'\s]?(?:password|passwd|secret|api[_-]?key|auth[_-]?token|access[_-]?token)["\'\s]*[:=]\s*["\']?)([^"\'\s\r\n]{6,})(["\'\s]?)',
            _kv_repl,
            out,
        )

        # 5. Redact Specific High-Entropy Token Formats
        # OpenAI & Anthropic keys
        out = re.sub(r'\b(?:sk-[a-zA-Z0-9_\-]{20,})\b', '[REDACTED_SECRET]', out)
        # Google / Gemini keys
        out = re.sub(r'\bAIza[0-9A-Za-z\-_]{30,40}\b', '[REDACTED_SECRET]', out)
        # GitHub Classic PAT
        out = re.sub(r'\bgh[pousr]_[A-Za-z0-9_]{30,255}\b', '[REDACTED_SECRET]', out)
        # GitHub Fine-Grained PAT
        out = re.sub(r'\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{30,}\b', '[REDACTED_SECRET]', out)
        # AWS Access Key IDs
        out = re.sub(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b', '[REDACTED_SECRET]', out)
        # Slack Tokens
        out = re.sub(r'\bxox[baprs]-[0-9a-zA-Z]{10,48}\b', '[REDACTED_SECRET]', out)

        return out

    def execute_safe_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: float = 30.0,
    ) -> CommandResult:
        """
        Executes a shell command after safety inspection and output redaction.
        Dangerous commands are intercepted, returning blocked=True and exit_code != 0.
        """
        # 1. Inspect command safety
        is_safe, violation_reason = self._inspect_command_safety(command, self.active_profile)
        if not is_safe:
            return CommandResult(
                command=command,
                exit_code=126,
                stdout="",
                stderr=self.redact_secrets(f"Command execution denied by kernel guardrail: {violation_reason}"),
                duration_ms=0.0,
                executed=False,
                denial_reason=violation_reason,
                blocked=True,
            )

        # 2. Check policy action
        decision = self.check_action(Action.EXECUTE, command)
        if not decision.allowed:
            return CommandResult(
                command=command,
                exit_code=126,
                stdout="",
                stderr=self.redact_secrets(f"Command execution denied by policy: {decision.reason}"),
                duration_ms=0.0,
                executed=False,
                denial_reason=decision.reason,
                blocked=True,
            )

        # 3. Determine execution directory
        cwd = Path(working_dir or self.workspace_root).expanduser().resolve()
        cwd.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            duration_ms = (time.time() - start_time) * 1000.0
            return CommandResult(
                command=command,
                exit_code=proc.returncode,
                stdout=self.redact_secrets(proc.stdout),
                stderr=self.redact_secrets(proc.stderr),
                duration_ms=duration_ms,
                executed=True,
                blocked=False,
            )
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000.0
            return CommandResult(
                command=command,
                exit_code=124,
                stdout="",
                stderr=f"Command execution timed out after {timeout} seconds",
                duration_ms=duration_ms,
                executed=True,
                denial_reason="Execution timeout",
                blocked=True,
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=self.redact_secrets(str(e)),
                duration_ms=duration_ms,
                executed=False,
                denial_reason=str(e),
                blocked=False,
            )
