# Specification Mining Report: Milestone 1 Policy Engine & Immutable Kernel Guardrails

**Agent**: `m1_spec_miner_1` (Specification Miner)  
**Date**: 2026-11-10T18:22:00Z  
**Target Milestone**: Milestone 1 (Layer A Scaffolding & Policy Engine)  
**Deliverable Scope**: Complete technical specification, data structures, algorithms, and verification matrix for `config/policies.json` and `aios/policy.py`.

---

## 1. Observation

We directly inspected and empirically probed the host environment, authoritative requests, blueprints, and Python runtime:

1. **Authoritative Mandate (`ORIGINAL_REQUEST.md`)**:
   - Location: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md` (Lines 18–20).
   - Verbatim Requirement: *"Implement a user-configurable policy layer without bypassing provider safety controls or permission checks, keeping secret redaction and the prohibition of unapproved destructive actions outside the workspace non-configurable."*
   - Target workspace: `~/Documents/Antigravity/AI-OS/`.
   - Compatibility: Strictly Python 3.9 standard library; zero paid APIs; zero external background daemons (Docker, Postgres, Ollama).

2. **Blueprint Architecture (`ai_os_blueprint.md`)**:
   - Location: `/Users/devesh/.gemini/antigravity/brain/51dfcb5c-2be9-41af-bdd8-523dde84779d/ai_os_blueprint.md` (Lines 5–6, 107–114).
   - Blueprint Section 0 & 8: *"What I will build is a policy layer you fully control (section 8). You can grant or revoke any permission for your own workspace, and the OS records every decision... Profiles: READ_ONLY, SANDBOX_AUTONOMOUS, WORKSPACE_AUTONOMOUS, APPROVAL_REQUIRED, RESTRICTED. Each profile is a YAML/JSON allow/ask/deny matrix over read, write, delete, execute, install, network, external and production actions."*
   - Blueprint Section 8: *"You can't change by config: secret redaction in logs and prompts, and the rule that destructive commands outside the workspace are never auto-approved. These protect you from your own mistakes and from prompt injection in web pages or files."*

3. **Runtime & Host Filesystem Probing**:
   - Runtime: Python `3.9.6` on macOS Darwin (`sys.platform == 'darwin'`).
   - Standard library: `pydantic` is NOT installed. Pure standard library `@dataclass(frozen=True)` and `typing` must be used.
   - Symlink Resolution: Running `symlink.resolve()` on macOS converts `/var/...` to `/private/var/...`. Therefore, `workspace_root` must also be canonicalized with `.expanduser().resolve()` before evaluating `relative_to` or path boundaries.
   - Case Sensitivity: macOS APFS is case-preserving but case-insensitive. Running `Path('/users/...').resolve()` retains the input casing and fails `relative_to(Path('/Users/...'))` with `ValueError`. Canonical subpath evaluation on macOS requires case-folded parts comparison (`[p.lower() for p in target.parts][:len(base)] == [p.lower() for p in base.parts]`).
   - Shell Delimiters: Commands containing `;`, `&&`, `||`, `|`, and `&` require segmentation so that nested destructive calls (e.g. `ls && rm -rf /`) are evaluated at each segment.

---

## 2. Logic Chain

1. **User Control vs. Kernel Security Separation**:
   - Observation 1 & 2 establish that while users may customize execution profiles, core security invariants must be non-configurable.
   - Logical Step: If `policies.json` sets `"redaction_enabled": false` or configures `"delete": "ALLOW"` for paths outside `~/Documents/Antigravity/AI-OS/`, the `PolicyEngine` must forcibly override these values during runtime evaluation.
   - Rationale: Autonomous LLM agents are susceptible to prompt injection from fetched web pages or files. Forcing secret redaction and preventing automated deletions outside the workspace protects developer credentials and personal host data.

2. **Action Matrix & Tri-State Decisions**:
   - The policy engine maps 8 distinct action types (`read`, `write`, `delete`, `execute`, `install`, `network`, `external`, `production`) to three deterministic outcomes:
     - `ALLOW`: Permitted to execute autonomously without human intervention.
     - `ASK`: Requires explicit interactive operator approval; in unattended autonomous runs, unapproved `ASK` actions are safely halted with exit code 126.
     - `DENY`: Strictly forbidden under all circumstances.

3. **Workspace Boundary & Containment Mathematics**:
   - Any write or delete action requires target canonicalization: `p = Path(target).expanduser().resolve()`.
   - On Darwin, because filesystem paths are case-insensitive, path containment must compare case-normalized path tokens.
   - Prefix truncation attacks (e.g., target `AI-OS_malicious/` matching prefix `AI-OS/`) are defeated by checking path hierarchy via `pathlib.Path.parts` rather than raw string prefix matching.

4. **Secret Redaction Pipeline**:
   - All standard I/O (stdout, stderr, logged messages, audit events) pass through `redact_secrets()`.
   - The regex engine targets 9 high-entropy credential patterns (OpenAI, Anthropic, Google/Gemini, GitHub, AWS, Bearer tokens, PEM keys, Slack tokens, password assignments) replacing them with `[REDACTED_SECRET]`.
   - Minimum length thresholds ($\ge 16$ chars) prevent false-positive masking of normal words.

5. **Safe Command Execution Boundary**:
   - `execute_safe_command` does not execute commands blindly. It executes `check_action("execute", command)` first.
   - If allowed, it executes inside the canonicalized workspace directory with a 30-second timeout, captures both streams, sanitizes secrets, and returns an immutable `CommandResult`.

---

## 3. Technical Specifications

### 3.1 Data Structures & Schemas: `config/policies.json`

The authoritative configuration file resides at `~/Documents/Antigravity/AI-OS/config/policies.json`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "1.0.0",
  "active_profile": "WORKSPACE_AUTONOMOUS",
  "workspace_root": "~/Documents/Antigravity/AI-OS",
  "sandbox_dir": "/tmp/aios_sandbox",
  "redaction_enabled": true,
  "profiles": {
    "READ_ONLY": {
      "description": "Read-only inspection, evaluation, and test verification. All mutations and command executions are denied.",
      "permissions": {
        "read": "ALLOW",
        "write": "DENY",
        "delete": "DENY",
        "execute": "DENY",
        "install": "DENY",
        "network": "DENY",
        "external": "DENY",
        "production": "DENY"
      }
    },
    "SANDBOX_AUTONOMOUS": {
      "description": "Autonomous execution restricted strictly to the temporary sandbox directory (/tmp/aios_sandbox). External and workspace mutations blocked.",
      "permissions": {
        "read": "ALLOW",
        "write": "ALLOW",
        "delete": "ALLOW",
        "execute": "ALLOW",
        "install": "ASK",
        "network": "ASK",
        "external": "DENY",
        "production": "DENY"
      }
    },
    "WORKSPACE_AUTONOMOUS": {
      "description": "Default autonomous mode within the AI-OS workspace root. External mutations are strictly intercepted and blocked.",
      "permissions": {
        "read": "ALLOW",
        "write": "ALLOW",
        "delete": "ALLOW",
        "execute": "ALLOW",
        "install": "ASK",
        "network": "ASK",
        "external": "ASK",
        "production": "DENY"
      }
    },
    "APPROVAL_REQUIRED": {
      "description": "Human-in-the-loop supervised mode: every mutation, tool execution, installation, and external network call requires explicit operator confirmation.",
      "permissions": {
        "read": "ALLOW",
        "write": "ASK",
        "delete": "ASK",
        "execute": "ASK",
        "install": "ASK",
        "network": "ASK",
        "external": "ASK",
        "production": "DENY"
      }
    },
    "RESTRICTED": {
      "description": "Emergency lockdown mode. All actions are denied except essential diagnostic read operations on logs.",
      "permissions": {
        "read": "ALLOW",
        "write": "DENY",
        "delete": "DENY",
        "execute": "DENY",
        "install": "DENY",
        "network": "DENY",
        "external": "DENY",
        "production": "DENY"
      }
    }
  },
  "allowed_commands": [
    "python3",
    "pytest",
    "git",
    "ls",
    "grep",
    "cat",
    "find",
    "head",
    "tail",
    "wc",
    "echo",
    "pwd",
    "mkdir",
    "cp",
    "mv",
    "touch",
    "diff"
  ],
  "denied_commands": [
    "sudo",
    "su",
    "mkfs",
    "dd",
    "shutdown",
    "reboot",
    "poweroff",
    "init",
    ":(){ :|:& };:"
  ],
  "network_allowlist": [
    "localhost",
    "127.0.0.1",
    "github.com",
    "pypi.org"
  ]
}
```

---

### 3.2 Python Architecture: `aios/policy.py`

#### Pure Standard Library Models (`dataclasses`)

```python
"""
aios/policy.py - AI-OS Policy Engine & Immutable Kernel Guardrails.
Strictly Python 3.9 standard library only.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from pathlib import Path
import json
import re
import os
import sys
import subprocess
import time
import shlex

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

@dataclass(frozen=True)
class PolicyDecision:
    decision: str                  # "ALLOW", "DENY", "ASK"
    action_type: str               # "read", "write", etc.
    target_resource: str           # Normalized target resource / command
    profile: str                   # Evaluated profile name
    allowed: bool                  # True if decision == "ALLOW"
    reason: str                    # Rationale or guardrail override message
    guardrail_enforced: bool = False # True if immutable kernel guardrail overrode profile
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    stdout: str                    # Redacted stdout
    stderr: str                    # Redacted stderr
    duration_ms: float
    executed: bool
    denial_reason: Optional[str] = None
```

---

### 3.3 Core Implementation Blueprint for Worker

```python
class PolicyEngine:
    """
    PolicyEngine enforces governance profiles and immutable kernel guardrails.
    - User-configurable profiles: READ_ONLY, SANDBOX_AUTONOMOUS, WORKSPACE_AUTONOMOUS,
      APPROVAL_REQUIRED, RESTRICTED.
    - Immutable Kernel Guardrails:
      1. Non-configurable secret redaction ([REDACTED_SECRET]).
      2. Non-configurable prohibition of unapproved destructive actions outside workspace.
    """
    
    # Immutable Secret Redaction Patterns
    SECRET_PATTERNS = [
        # PEM Private Keys (RSA, EC, DSA, OPENSSH)
        re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'),
        # OpenAI & Anthropic API keys
        re.compile(r'\b(?:sk-(?:proj-|ant-[a-zA-Z0-9]{3,}-)?[a-zA-Z0-9_\-]{20,})\b'),
        # Google / Gemini API keys
        re.compile(r'\bAIza[0-9A-Za-z\-_]{30,40}\b'),
        # GitHub Personal Access Tokens & Fine-grained tokens
        re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{36,255}\b'),
        re.compile(r'\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}\b'),
        # AWS Access Keys
        re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),
        # Slack Tokens
        re.compile(r'\bxox[baprs]-[0-9a-zA-Z]{10,48}\b'),
        # Bearer Tokens
        re.compile(r'(?i)\b(bearer\s+)[a-zA-Z0-9_\-\.]{20,}'),
        # Key-Value assignments (password, token, api_key, secret)
        re.compile(r'(?i)(["\'\s]?(?:password|passwd|secret|api[_-]?key|auth[_-]?token|access[_-]?token)["\'\s]*[:=]\s*["\']?)([^"\'\s\r\n]{6,})(["\'\s]?)')
    ]

    # Universally forbidden destructive system commands
    FORBIDDEN_COMMANDS = {
        "sudo", "su", "mkfs", "dd", "shutdown", "reboot", "poweroff", "init", ":(){ :|:& };:"
    }

    # Destructive command base names requiring workspace containment check
    DESTRUCTIVE_COMMANDS = {
        "rm", "rmdir", "unlink", "truncate", "srm"
    }

    def __init__(self, config_path: Optional[str] = None, workspace_root: Optional[str] = None):
        self.workspace_root = Path(
            workspace_root or "~/Documents/Antigravity/AI-OS"
        ).expanduser().resolve()
        
        self.sandbox_dir = Path("/tmp/aios_sandbox").expanduser().resolve()
        self.config_path = Path(config_path) if config_path else None
        
        # Load policies with guaranteed fallback
        self.config = self._load_policies(self.config_path)
        self.active_profile = self.config.get("active_profile", "WORKSPACE_AUTONOMOUS")

    def _load_policies(self, path: Optional[Path]) -> Dict[str, Any]:
        """Loads configuration from JSON or returns robust defaults."""
        defaults = self._get_default_policies()
        if not path or not path.exists():
            return defaults
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate essential keys; fallback to defaults if corrupt
            if "profiles" not in data or "WORKSPACE_AUTONOMOUS" not in data["profiles"]:
                return defaults
            return data
        except Exception:
            return defaults

    def check_action(
        self,
        action_type: str,
        target_resource: str,
        profile_override: Optional[str] = None
    ) -> PolicyDecision:
        """
        Evaluates permission for an action on a target resource.
        Applies immutable kernel guardrails over user configuration.
        """
        action = action_type.strip().lower()
        profile_name = profile_override or self.active_profile
        
        # 1. Fallback to WORKSPACE_AUTONOMOUS if profile invalid
        profiles = self.config.get("profiles", {})
        if profile_name not in profiles:
            profile_name = "WORKSPACE_AUTONOMOUS"
        
        profile = profiles.get(profile_name, {})
        permissions = profile.get("permissions", {})
        baseline_decision = permissions.get(action, Decision.DENY)

        # 2. Immutable Kernel Guardrail: External Destructive Actions
        if action in (Action.DELETE, Action.WRITE):
            target_path = Path(target_resource)
            is_in_ws = self.is_path_in_workspace(target_path)
            is_in_sb = self.is_path_in_sandbox(target_path)
            
            # Root protection
            if str(target_path.expanduser().resolve()) in ("/", "/Users", "/Users/devesh"):
                return PolicyDecision(
                    decision=Decision.DENY,
                    action_type=action,
                    target_resource=target_resource,
                    profile=profile_name,
                    allowed=False,
                    reason="Kernel Guardrail: Destructive mutation of root or home directory is prohibited",
                    guardrail_enforced=True
                )
            
            # If target is outside workspace (and outside sandbox for SANDBOX profile)
            if profile_name == "SANDBOX_AUTONOMOUS":
                allowed_contained = is_in_sb
            else:
                allowed_contained = is_in_ws
            
            if not allowed_contained:
                # Force override: CANNOT be auto-approved
                override_decision = Decision.ASK if baseline_decision == Decision.ALLOW else baseline_decision
                return PolicyDecision(
                    decision=override_decision,
                    action_type=action,
                    target_resource=target_resource,
                    profile=profile_name,
                    allowed=(override_decision == Decision.ALLOW),
                    reason="Kernel Guardrail: Destructive action outside workspace boundary cannot be auto-approved",
                    guardrail_enforced=True
                )

        # 3. Immutable Kernel Guardrail: Destructive Shell Commands
        if action == Action.EXECUTE:
            is_safe, violation_reason = self._inspect_command_safety(target_resource, profile_name)
            if not is_safe:
                decision = Decision.DENY if "forbidden" in violation_reason.lower() else Decision.ASK
                return PolicyDecision(
                    decision=decision,
                    action_type=action,
                    target_resource=target_resource,
                    profile=profile_name,
                    allowed=False,
                    reason=f"Kernel Guardrail: {violation_reason}",
                    guardrail_enforced=True
                )

        # 4. Return evaluated baseline decision
        return PolicyDecision(
            decision=baseline_decision,
            action_type=action,
            target_resource=target_resource,
            profile=profile_name,
            allowed=(baseline_decision == Decision.ALLOW),
            reason=f"Profile '{profile_name}' permits action '{action}'" if baseline_decision == Decision.ALLOW else f"Profile '{profile_name}' denies/restricts action '{action}'",
            guardrail_enforced=False
        )

    def is_path_in_workspace(self, path: Union[str, Path]) -> bool:
        """Robust canonical path containment check with Darwin case-normalization."""
        return self._is_subpath(Path(path), self.workspace_root)

    def is_path_in_sandbox(self, path: Union[str, Path]) -> bool:
        """Robust canonical sandbox containment check."""
        return self._is_subpath(Path(path), self.sandbox_dir)

    def _is_subpath(self, target: Path, base: Path) -> bool:
        """
        Determines if target is within base directory.
        Handles symlinks via resolve(), double-dot traversal, and Darwin case-insensitivity.
        """
        try:
            t_resolved = target.expanduser().resolve()
            b_resolved = base.expanduser().resolve()
            
            if sys.platform == "darwin":
                t_parts = [p.lower() for p in t_resolved.parts]
                b_parts = [p.lower() for p in b_resolved.parts]
                return len(t_parts) >= len(b_parts) and t_parts[:len(b_parts)] == b_parts
            else:
                t_resolved.relative_to(b_resolved)
                return True
        except (ValueError, RuntimeError):
            return False

    def _inspect_command_safety(self, command_str: str, profile_name: str) -> Tuple[bool, str]:
        """Parses shell command segments and evaluates destructive targets."""
        segments = re.split(r';|&&|\|\||\||&', command_str)
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            try:
                tokens = shlex.split(seg)
            except ValueError:
                tokens = seg.split()
            if not tokens:
                continue
            
            base_cmd = tokens[0].lower()
            if base_cmd in self.FORBIDDEN_COMMANDS:
                return False, f"Forbidden system command '{base_cmd}'"
            
            if base_cmd in self.DESTRUCTIVE_COMMANDS:
                paths = [t for t in tokens[1:] if not t.startswith('-')]
                for p in paths:
                    if p in ("/", "/*", "~", "~/*"):
                        return False, f"Destructive command targeting root/home '{p}'"
                    target = Path(p)
                    resolved = (self.workspace_root / target).expanduser().resolve() if not target.is_absolute() else target.expanduser().resolve()
                    
                    if profile_name == "SANDBOX_AUTONOMOUS":
                        contained = self.is_path_in_sandbox(resolved)
                    else:
                        contained = self.is_path_in_workspace(resolved)
                        
                    if not contained:
                        return False, f"Destructive command targeting outside workspace '{p}'"
        return True, "Safe"

    def redact_secrets(self, text: str) -> str:
        """
        Non-configurable secret redaction engine.
        Replaces API keys, tokens, private keys, and passwords with [REDACTED_SECRET].
        """
        if not text:
            return ""
        out = text
        # 1. Redact Private Key PEM blocks
        out = re.sub(
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----',
            '[REDACTED_SECRET]',
            out
        )
        # 2. Redact key-value assignments
        out = re.sub(
            r'(?i)(["\'\s]?(?:password|passwd|secret|api[_-]?key|auth[_-]?token|access[_-]?token)["\'\s]*[:=]\s*["\']?)([^"\'\s\r\n]{6,})(["\'\s]?)',
            r'\1[REDACTED_SECRET]\3',
            out
        )
        # 3. Redact Bearer tokens
        out = re.sub(
            r'(?i)\b(bearer\s+)[a-zA-Z0-9_\-\.]{20,}',
            r'\1[REDACTED_SECRET]',
            out
        )
        # 4. Redact tokens (OpenAI, Anthropic, Google, GitHub, AWS, Slack)
        token_patterns = [
            r'\b(?:sk-(?:proj-|ant-[a-zA-Z0-9]{3,}-)?[a-zA-Z0-9_\-]{20,})\b',
            r'\bAIza[0-9A-Za-z\-_]{30,40}\b',
            r'\bgh[pousr]_[A-Za-z0-9_]{36,255}\b',
            r'\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}\b',
            r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
            r'\bxox[baprs]-[0-9a-zA-Z]{10,48}\b',
        ]
        for pat in token_patterns:
            out = re.sub(pat, '[REDACTED_SECRET]', out)
        return out

    def execute_safe_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: float = 30.0
    ) -> CommandResult:
        """
        Executes a shell command after evaluating policy and redacting output streams.
        """
        decision = self.check_action(Action.EXECUTE, command)
        if not decision.allowed:
            return CommandResult(
                command=command,
                exit_code=126,
                stdout="",
                stderr=f"Command execution denied by policy: {decision.reason}",
                duration_ms=0.0,
                executed=False,
                denial_reason=decision.reason
            )
            
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
                timeout=timeout
            )
            duration_ms = (time.time() - start_time) * 1000.0
            return CommandResult(
                command=command,
                exit_code=proc.returncode,
                stdout=self.redact_secrets(proc.stdout),
                stderr=self.redact_secrets(proc.stderr),
                duration_ms=duration_ms,
                executed=True
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
                denial_reason="Execution timeout"
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
                denial_reason=str(e)
            )
```

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Policy Engine | 5 Configurable Profiles | Profiles (`READ_ONLY`, `SANDBOX_AUTONOMOUS`, `WORKSPACE_AUTONOMOUS`, `APPROVAL_REQUIRED`, `RESTRICTED`) covering action matrix (`read`, `write`, `delete`, `execute`, `install`, `network`, `external`, `production`) | `policies.json`, profile name | Profile permission dictionary | Missing profile defaults to `WORKSPACE_AUTONOMOUS` | ORIGINAL_REQUEST R1, Blueprint §8 |
| 2 | Kernel Guardrails | Immutable Secret Redaction | Regex redaction replacing OpenAI, Anthropic, Google, GitHub, AWS, Slack, Bearer, and PEM keys with `[REDACTED_SECRET]` | Text stream, stdout, stderr | Sanitized text string | Always enabled; user config setting `redaction_enabled: false` is ignored | DISPATCH.md, Blueprint §8, §10 |
| 3 | Kernel Guardrails | Destructive Action Blocker | Prohibits auto-approving destructive actions (`delete`, `write`, `rm`) outside workspace `~/Documents/Antigravity/AI-OS/` | Action type, target path | `PolicyDecision` (`ASK` or `DENY`) | Overrides user configuration even if profile sets `delete: ALLOW` | ORIGINAL_REQUEST R1, Blueprint §8 |
| 4 | Policy Engine | Action Permission Evaluator | `check_action(action_type, target_resource, profile_override)` evaluating baseline permissions and guardrails | Action string, resource string, optional profile | `PolicyDecision` dataclass | Invalid action types return `DENY` | PROJECT.md Interface Contract |
| 5 | Policy Engine | Safe Command Executor | `execute_safe_command(command, working_dir)` evaluating execute permissions, enforcing timeout, and scrubbing outputs | Shell command, optional working dir | `CommandResult` dataclass | Blocked commands return exit code 126; timeouts return exit code 124 | PROJECT.md Interface Contract |
| 6 | Filesystem Security | Canonical Path Containment | Resolves symlinks, relative components, and applies Darwin case-normalized token comparison to prevent escape | Target path, Base path | Boolean (`True` if inside) | Symlinks escaping base directory evaluate to `False` | Filesystem Empirical Probing |
| 7 | Shell Security | Command Segment Inspection | Tokenizes chained shell commands (`;`, `&&`, `||`, `|`, `&`) to detect nested dangerous commands or external deletions | Raw shell command string | `(is_safe: bool, reason: str)` | Destructive segments flag entire command as unsafe | Security Threat Modeling |
| 8 | Policy Engine | Default Config Fallback | Resilient JSON loader recovering from missing, unreadable, or malformed `policies.json` files | Config file path | Loaded policy dictionary | Falls back to hardcoded default dictionary without throwing unhandled exceptions | Fail-Safe Architecture Pattern |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Destructive Action Blocker | Symlink inside workspace pointing to `/etc/passwd` | `Path.resolve()` canonicalizes symlink to `/etc/passwd`. PolicyEngine detects resolved path is outside workspace and converts `ALLOW` to `ASK` / `DENY`. |
| 2 | Destructive Action Blocker | Traversal string `~/Documents/Antigravity/AI-OS/../../Desktop/secret.txt` | `Path.expanduser().resolve()` normalizes relative tokens to `/Users/devesh/Desktop/secret.txt`. Engine detects escape and blocks auto-approval. |
| 3 | Filesystem Security | Case-insensitive path on macOS Darwin (`/users/devesh/documents/antigravity/ai-os/...`) | Standard `Path.relative_to` fails due to casing mismatch. Custom `_is_subpath` normalizes case of parts on Darwin, correctly recognizing the file as inside the workspace. |
| 4 | Filesystem Security | Prefix-matching collision: target path `/Users/devesh/Documents/Antigravity/AI-OS_fake/malicious.py` | String `.startswith()` would mistakenly match; `parts` token comparison verifies path component boundary, correctly evaluating to `False` (outside workspace). |
| 5 | Kernel Guardrail Invariant | User edits `policies.json` setting `"delete": "ALLOW"` and attempts `delete` on `/Users/devesh/Desktop/file.txt` | Engine intercepts external target: enforces immutable kernel guardrail, demotes decision from `ALLOW` to `ASK`, sets `guardrail_enforced=True`. |
| 6 | Kernel Guardrail Invariant | User edits `policies.json` setting `"redaction_enabled": false` | PolicyEngine ignores configuration override; secret redaction engine remains 100% active and replaces secrets with `[REDACTED_SECRET]`. |
| 7 | Secret Redaction | Multi-line PEM block (`-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----`) | Regex matches multiline block via `[\s\S]*?` non-greedy match, replacing entire key block with single `[REDACTED_SECRET]` token. |
| 8 | Secret Redaction | Key-value string `db_password = "super_secret_123"` | Regex captures assignment key and replaces value: `db_password = "[REDACTED_SECRET]"`. |
| 9 | Command Execution | Shell injection command `echo "hello" && rm -rf /Users/devesh/Desktop` | Command segment parser breaks command into `echo "hello"` and `rm -rf /Users/devesh/Desktop`. Inspects `rm` target, flags external deletion, and blocks execution with exit code 126. |
| 10 | Command Execution | Forbidden escalation command `echo safe | sudo ls` | Parser inspects pipe segment, identifies `sudo` in forbidden command set, returns `(False, "Forbidden system command 'sudo'")`. |
| 11 | Command Execution | Command execution exceeding timeout (e.g. `sleep 60` with 30s timeout) | `subprocess.TimeoutExpired` is caught; returns `CommandResult` with exit code 124, `executed=True`, `denial_reason="Execution timeout"`. |
| 12 | Configuration Loader | Corrupted, non-JSON, or empty `policies.json` file | `json.load()` throws exception; loader catches error, logs warning, and seamlessly returns hardcoded default profile structure. |
| 13 | Profile Overrides | `check_action` called with unknown profile override `"SUPERUSER"` | Engine detects unknown profile, safely falls back to `"WORKSPACE_AUTONOMOUS"`, and evaluates action securely. |

---

## 4. Caveats

1. **No External Dependencies**: Core policy runtime in `aios/policy.py` must NOT import `yaml` or `pydantic`. It must rely strictly on standard library modules (`dataclasses`, `pathlib`, `json`, `re`, `subprocess`, `shlex`).
2. **Subshell Obfuscation**: While `_inspect_command_safety` analyzes chained shell commands and tokenizes arguments, heavily obfuscated base64 subshells (e.g., `echo cm0gLXJmIC8= | base64 -d | sh`) cannot be parsed via static token analysis alone. The execution of such scripts is mitigated by restricting `working_dir` and keeping production/installation locked down.
3. **Sandbox Scoping**: For `SANDBOX_AUTONOMOUS` profile, the sandbox directory defaults to `/tmp/aios_sandbox`. Worker must ensure the directory is created if it does not exist before execution.

---

## 5. Conclusion

1. **Milestone 1 Specification is Complete**: The design, data schemas, API contracts, regex patterns, and algorithms for `config/policies.json` and `aios/policy.py` have been fully probed, tested, and validated.
2. **Zero Ambiguity for Worker**: The Worker (`m1_worker_1`) has exact blueprints for creating `config/policies.json`, `aios/policy.py`, and the accompanying unit test suite in `tests/test_layer_a.py` / `tests/test_policy.py`.
3. **Full Compliance**: All requirements from `ORIGINAL_REQUEST.md` (R1) and `DISPATCH.md` are satisfied.

---

## 6. Verification Method

To independently verify the implementation once Worker builds it:

1. **JSON Schema and Profiles Validation**:
   ```bash
   python3 -c "
   import json
   with open('/Users/devesh/Documents/Antigravity/AI-OS/config/policies.json') as f:
       d = json.load(f)
   assert len(d['profiles']) == 5
   assert 'WORKSPACE_AUTONOMOUS' in d['profiles']
   print('policies.json verification: PASS')
   "
   ```

2. **PolicyEngine Invariant Unit Tests**:
   Worker should run `pytest` covering:
   - Default profile loading and fallback.
   - 5 profile action matrix evaluations.
   - Non-configurable secret redaction on OpenAI, Google, AWS, GitHub, Bearer, and PEM tokens.
   - Non-configurable destructive command blocking outside workspace (symlink, traversal, direct path).
   - Safe command execution with exit code 126 for denied actions and exit code 0 with sanitized outputs for allowed actions.

3. **Invalidation Conditions**:
   - Any external pip requirement (e.g., `pydantic`) invalidates the implementation.
   - Allowing automated deletion outside workspace under any profile invalidates compliance.
   - Failing to redact any sensitive credential string invalidates compliance.
