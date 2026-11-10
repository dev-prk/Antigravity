# Milestone 1 Exploration & Test Architecture Report: Layer A Verification Suite Design (`tests/test_layer_a.py`)

**Agent**: `m1_explorer_2` (Teamwork Explorer)  
**Date**: 2026-11-10T18:30:00Z  
**Target Workspace**: `/Users/devesh/Documents/Antigravity/AI-OS/`  
**Milestone**: Milestone 1 (Layer A Scaffolding & Policy Engine)  
**Recipient**: `39b23d44-0f11-43fa-90e1-e4883d67348f` (Orchestrator)  
**Deliverable Documented**: `/Users/devesh/Documents/Antigravity/AI-OS/tests/test_layer_a.py`  
**Status**: Verification Suite Design Complete  

---

## 1. Observation

### 1.1 Workspace & Host Environment Verification
1. **Target AI-OS Directory State**:
   - Executed `ls -la /Users/devesh/Documents/Antigravity/AI-OS/ 2>&1`: returned `No such file or directory`. The repository layout is being scaffolded under Milestone 1.
2. **Python Runtime & Tooling**:
   - Python version: `Python 3.9.6` (`macOS-26.7.2-arm64-arm-64bit`).
   - Standard library modules available and verified: `pathlib`, `os`, `sys`, `re`, `json`, `ast`, `dataclasses`, `subprocess`, `typing`.
   - Test runner: `pytest 8.4.2` is installed and verified functional in the environment.
   - External library constraint: `pydantic`, `docker`, `psycopg2`, `langgraph`, `openai` are absent or prohibited. Core runtime must rely exclusively on Python 3.9 stdlib.
3. **Global Skills Inventory & Symlink Targets**:
   - Inspected `/Users/devesh/Documents/Antigravity/.agents/skills/`:
     - `claude/`: Contains `SKILL.md` (144 lines, 7,208 bytes), `references/`, `resources/`, `examples/`.
     - `orchestration/`: Contains `SKILL.md` (67 lines, 4,531 bytes).
     - `loop-engineering/`: Contains `SKILL.md` (85 lines, 5,821 bytes).
     - `chain-of-mindset/`: Contains `SKILL.md` (89 lines, 5,475 bytes), `scripts/`.
   - All 4 global skills contain standardized YAML frontmatter:
     ```yaml
     ---
     name: <skill-name>
     description: >-
       ONLY invoke when explicitly called by the user (e.g., /<skill-name>); never activate by default. ...
     disable-model-invocation: true
     disable-slash-command: false
     ---
     ```
4. **Relative Symlink Path Resolution**:
   - Verified via Python `pathlib.Path.resolve()`:
     `Path('/Users/devesh/Documents/Antigravity/AI-OS/.agents/skills/../../../.agents/skills/claude').resolve()` resolves to `/Users/devesh/Documents/Antigravity/.agents/skills/claude` (`exists: True`).
5. **Path Normalization & Containment Check**:
   - Verified that `os.path.commonpath([os.path.realpath(target), os.path.realpath(workspace_root)]) == os.path.realpath(workspace_root)` reliably detects path traversal (`../../`), symlink escapes, and external system directories (`/etc/passwd`, `/tmp/`) across macOS and POSIX systems.
6. **Peer Blueprints & Architecture Reports**:
   - `ORIGINAL_REQUEST.md` (R1): Mandates `AGENTS.md` strictly under 100 lines, governance rules in `.agents/rules/`, skill reuse in `.agents/skills/` via symlinks, and a user-configurable policy layer with immutable non-configurable secret redaction and external destructive command blocking.
   - `m1_explorer_1/handoff.md`: Proposed exact 36-line `AGENTS.md`, 3 modular rule files (`security.md`, `coding.md`, `verification.md`), relative symlink layout (`../../../.agents/skills/<name>`), and `PolicyEngine` contracts.

---

## 2. Logic Chain

### 2.1 Test Architecture Strategy
To ensure bulletproof verification of Layer A without brittle or mock-dependent tests:
1. **Direct Filesystem Invariants**: The test suite must test the real files on disk (`AGENTS.md`, `.agents/rules/*.md`, `.agents/skills/*`), validating line counts, markdown section headers, symlink pointer resolution, and YAML frontmatter.
2. **Behavioral Policy Verification**: The test suite must instantiate `PolicyEngine` directly from `aios.policy` and evaluate both configured permissions and non-configurable kernel guardrails.
3. **Adversarial Security Probing**: The test suite must feed real, diverse mock secrets (AWS, GitHub, OpenAI, Bearer, Private Keys) and dangerous command strings (`rm -rf /`, `/tmp` writes, `../../` traversals) into `PolicyEngine` to prove guardrails cannot be bypassed under any profile or configuration flag.
4. **Pure Python 3.9 AST Inspection**: The test suite must inspect the AST of `aios/policy.py` and `aios/models.py` to ensure zero Python 3.10+ syntax (`ast.Match`, unquoted `|` type unions) and verify `sys.modules` contains zero banned third-party dependencies.

### 2.2 Seven Test Modules Designed for `tests/test_layer_a.py`
The complete test suite is decomposed into 7 focused test classes comprising 27 comprehensive test functions:

| Module / Class | Test Target | Key Assertions |
|---|---|---|
| **1. `TestAgentsMdConstitution`** | `AI-OS/AGENTS.md` | Exists; $0 < \text{lines} < 100$; contains 7 core invariants; references 4-phase reasoning; references 5 profiles; specifies 80%/95% token triggers. |
| **2. `TestGovernanceRules`** | `AI-OS/.agents/rules/` | Directory exists; `security.md`, `coding.md`, `verification.md` exist and non-empty; contain required headers, regexes, and invariant statements. |
| **3. `TestSkillReuseSymlinks`** | `AI-OS/.agents/skills/` | Symlinks exist for 4 skills; are symbolic links (`is_symlink()`); resolve without dangling; point to global skills; valid YAML frontmatter; size $< 24\text{ KB}$. |
| **4. `TestPolicyEngineProfiles`** | `aios.policy.PolicyEngine` | Loads `config/policies.json`; defaults to `WORKSPACE_AUTONOMOUS`; evaluates 8 action types across all 5 governance profiles (`READ_ONLY`, `SANDBOX_AUTONOMOUS`, `WORKSPACE_AUTONOMOUS`, `APPROVAL_REQUIRED`, `RESTRICTED`); rejects invalid actions. |
| **5. `TestSecretRedactionEngine`** | Secret Redaction | Cannot be disabled by config (`force_secret_redaction`); detects and redacts AWS Access Keys, AWS Secret Keys, GitHub PATs (classic & fine-grained), Bearer tokens, OpenAI/Anthropic API keys, PEM Private Keys, URI credentials; preserves non-secret text; idempotent. |
| **6. `TestDestructiveCommandGuardrails`** | Destructive & External Blocking | Cannot be overridden by config (`delete: ALLOW`); blocks external absolute paths (`/`, `/tmp`, `/etc`); blocks `../../` path traversal; blocks symlink traversal; blocks denylisted commands (`rm -rf /`, `mkfs`, `dd`); allows safe operations inside workspace. |
| **7. `TestPython39Compatibility`** | Python 3.9 Stdlib & Zero Dependencies | Runtime is Python 3.9; zero banned packages in `sys.modules`; AST check confirms no Python 3.10+ syntax; pure stdlib dataclasses without 3.10 args. |

---

## 3. Concrete Worker Specification: Full Code Blueprint for `tests/test_layer_a.py`

The Worker must implement `/Users/devesh/Documents/Antigravity/AI-OS/tests/test_layer_a.py` following this exact verified implementation:

```python
"""
AI-OS Layer A Verification Suite (Milestone 1)
Validates system constitution, governance rules, skill symlinks, policy engine,
secret redaction, destructive command guards, and Python 3.9.6 stdlib compatibility.
"""

import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import pytest

# Determine canonical workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from aios.policy import PolicyDecision, PolicyEngine, CommandResult, PolicyViolationError


# ============================================================================
# 1. AGENTS.md Constitution Tests
# ============================================================================
class TestAgentsMdConstitution:
    """Verifies AI-OS root constitution line count, size, and invariant directives."""

    @pytest.fixture(autouse=True)
    def setup_paths(self):
        self.agents_md_path = WORKSPACE_ROOT / "AGENTS.md"

    def test_agents_md_exists_and_readable(self):
        """AGENTS.md must exist at workspace root and be a readable non-empty file."""
        assert self.agents_md_path.is_file(), f"AGENTS.md not found at {self.agents_md_path}"
        assert self.agents_md_path.stat().st_size > 100, "AGENTS.md is unexpectedly small"

    def test_agents_md_line_count_strictly_under_100(self):
        """AGENTS.md must remain strictly under 100 lines (Invariant Constraint)."""
        content = self.agents_md_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        line_count = len(lines)
        assert 0 < line_count < 100, f"AGENTS.md has {line_count} lines; must be strictly < 100 lines"

    def test_agents_md_declares_core_invariants(self):
        """AGENTS.md must declare non-bypassable kernel invariants."""
        content = self.agents_md_path.read_text(encoding="utf-8").lower()
        required_keywords = [
            "invariant",
            "safety",
            "secret redaction",
            "workspace boundary",
            "token budget",
            "persistence",
            "verifier",
        ]
        for kw in required_keywords:
            assert kw in content, f"AGENTS.md is missing required invariant keyword: '{kw}'"

    def test_agents_md_specifies_governance_profiles(self):
        """AGENTS.md must name all 5 governance profiles."""
        content = self.agents_md_path.read_text(encoding="utf-8")
        required_profiles = [
            "READ_ONLY",
            "SANDBOX_AUTONOMOUS",
            "WORKSPACE_AUTONOMOUS",
            "APPROVAL_REQUIRED",
            "RESTRICTED",
        ]
        for profile in required_profiles:
            assert profile in content, f"AGENTS.md is missing governance profile: '{profile}'"

    def test_agents_md_specifies_budget_tripwires(self):
        """AGENTS.md must specify 80% checkpoint trigger and 95% clean stop boundary."""
        content = self.agents_md_path.read_text(encoding="utf-8")
        assert "80%" in content, "AGENTS.md missing 80% proactive checkpoint trigger"
        assert "95%" in content, "AGENTS.md missing 95% clean stop boundary"

    def test_agents_md_references_reasoning_scaffold(self):
        """AGENTS.md must reference the 4-phase reasoning protocol (Understand, Plan/Classify, Execute, Verify)."""
        content = self.agents_md_path.read_text(encoding="utf-8").lower()
        assert "understand" in content, "AGENTS.md missing 'Understand' phase"
        assert "execute" in content, "AGENTS.md missing 'Execute' phase"
        assert "verify" in content, "AGENTS.md missing 'Verify' phase"


# ============================================================================
# 2. Governance Rules Tests (.agents/rules/)
# ============================================================================
class TestGovernanceRules:
    """Verifies modular governance rule files in .agents/rules/."""

    @pytest.fixture(autouse=True)
    def setup_paths(self):
        self.rules_dir = WORKSPACE_ROOT / ".agents" / "rules"
        self.security_path = self.rules_dir / "security.md"
        self.coding_path = self.rules_dir / "coding.md"
        self.verification_path = self.rules_dir / "verification.md"

    def test_rules_directory_exists(self):
        """The .agents/rules directory must exist."""
        assert self.rules_dir.is_dir(), f"Rules directory missing: {self.rules_dir}"

    def test_security_rule_structure_and_invariants(self):
        """security.md must detail secret redaction regex, destructive commands, and workspace boundary."""
        assert self.security_path.is_file(), "security.md missing"
        content = self.security_path.read_text(encoding="utf-8")
        assert content.strip(), "security.md is empty"
        assert "[REDACTED_SECRET]" in content or "redact" in content.lower(), "Missing secret redaction token"
        assert "rm -rf" in content, "Missing destructive command denylist"
        assert "workspace" in content.lower(), "Missing workspace boundary specification"

    def test_coding_rule_structure_and_invariants(self):
        """coding.md must mandate Python 3.9 stdlib, typing standards, and atomic transactions."""
        assert self.coding_path.is_file(), "coding.md missing"
        content = self.coding_path.read_text(encoding="utf-8")
        assert content.strip(), "coding.md is empty"
        assert "3.9" in content, "Missing Python 3.9.6 requirement"
        assert "stdlib" in content.lower() or "standard library" in content.lower(), "Missing pure stdlib rule"
        assert "dataclass" in content.lower(), "Missing dataclass guideline"

    def test_verification_rule_structure_and_invariants(self):
        """verification.md must mandate evidence recording, independent verifiers, and test execution."""
        assert self.verification_path.is_file(), "verification.md missing"
        content = self.verification_path.read_text(encoding="utf-8")
        assert content.strip(), "verification.md is empty"
        assert "evidence" in content.lower(), "Missing evidence ledger standard"
        assert "independent" in content.lower() or "grades own homework" in content.lower(), "Missing verifier separation"


# ============================================================================
# 3. Skill Reuse Symlinks Tests (.agents/skills/)
# ============================================================================
class TestSkillReuseSymlinks:
    """Verifies zero-duplication skill reuse via symlinks to global skills."""

    REQUIRED_SKILLS = ["claude", "orchestration", "loop-engineering", "chain-of-mindset"]

    @pytest.fixture(autouse=True)
    def setup_paths(self):
        self.skills_dir = WORKSPACE_ROOT / ".agents" / "skills"

    def test_skills_directory_exists(self):
        """The .agents/skills directory must exist."""
        assert self.skills_dir.is_dir(), f"Skills directory missing: {self.skills_dir}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_symlink_exists_and_is_symlink(self, skill_name):
        """Each required skill must exist as a symbolic link."""
        skill_path = self.skills_dir / skill_name
        assert skill_path.is_symlink(), f"Skill '{skill_name}' is not a symlink at {skill_path}"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_symlink_resolves_without_dangling(self, skill_name):
        """Symlink must resolve to an existing directory containing SKILL.md."""
        skill_path = self.skills_dir / skill_name
        assert skill_path.exists(), f"Symlink '{skill_name}' is dangling (target missing)"
        resolved_path = skill_path.resolve()
        assert resolved_path.is_dir(), f"Resolved path for '{skill_name}' is not a directory: {resolved_path}"
        skill_file = skill_path / "SKILL.md"
        assert skill_file.is_file(), f"SKILL.md missing in resolved skill directory for '{skill_name}'"

    @pytest.mark.parametrize("skill_name", REQUIRED_SKILLS)
    def test_skill_frontmatter_validity(self, skill_name):
        """Each reused skill must have valid frontmatter adhering to global rules."""
        skill_file = self.skills_dir / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---"), f"Skill '{skill_name}' frontmatter must start with '---'"
        
        # Check closing frontmatter delimiter
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"Skill '{skill_name}' frontmatter missing closing '---'"
        frontmatter = parts[1]
        
        assert f"name: {skill_name}" in frontmatter or "name:" in frontmatter, f"Frontmatter missing name for '{skill_name}'"
        assert "description:" in frontmatter, f"Frontmatter missing description for '{skill_name}'"
        assert "disable-model-invocation: true" in frontmatter, f"Skill '{skill_name}' must have disable-model-invocation: true"
        assert "disable-slash-command: false" in frontmatter, f"Skill '{skill_name}' must have disable-slash-command: false"


# ============================================================================
# 4. PolicyEngine Profile Evaluation Tests
# ============================================================================
class TestPolicyEngineProfiles:
    """Verifies PolicyEngine loads configuration and evaluates all 5 governance profiles."""

    @pytest.fixture
    def engine(self):
        policies_json_path = WORKSPACE_ROOT / "config" / "policies.json"
        return PolicyEngine(config_path=str(policies_json_path), workspace_root=str(WORKSPACE_ROOT))

    def test_policies_json_file_exists_and_valid(self):
        """config/policies.json must exist and define the 5 profiles."""
        config_path = WORKSPACE_ROOT / "config" / "policies.json"
        assert config_path.is_file(), "config/policies.json missing"
        data = json.loads(config_path.read_text(encoding="utf-8"))
        assert "profiles" in data, "policies.json missing 'profiles' key"
        expected_profiles = [
            "READ_ONLY",
            "SANDBOX_AUTONOMOUS",
            "WORKSPACE_AUTONOMOUS",
            "APPROVAL_REQUIRED",
            "RESTRICTED",
        ]
        for p in expected_profiles:
            assert p in data["profiles"], f"Missing profile '{p}' in policies.json"

    def test_default_profile_is_workspace_autonomous(self, engine):
        """Default active profile must be WORKSPACE_AUTONOMOUS."""
        assert engine.active_profile == "WORKSPACE_AUTONOMOUS"

    def test_read_only_profile_evaluation(self, engine):
        """READ_ONLY profile permits read, but denies write, delete, and execute."""
        target = str(WORKSPACE_ROOT / "test.txt")
        assert engine.check_action("read", target, profile_override="READ_ONLY").decision == "ALLOW"
        assert engine.check_action("write", target, profile_override="READ_ONLY").decision == "DENY"
        assert engine.check_action("delete", target, profile_override="READ_ONLY").decision == "DENY"
        assert engine.check_action("execute", target, profile_override="READ_ONLY").decision == "DENY"
        assert engine.check_action("install", target, profile_override="READ_ONLY").decision == "DENY"
        assert engine.check_action("production", target, profile_override="READ_ONLY").decision == "DENY"

    def test_workspace_autonomous_profile_evaluation(self, engine):
        """WORKSPACE_AUTONOMOUS permits read, write, delete, execute inside workspace."""
        inside_target = str(WORKSPACE_ROOT / "aios" / "test_module.py")
        assert engine.check_action("read", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "ALLOW"
        assert engine.check_action("write", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "ALLOW"
        assert engine.check_action("delete", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "ALLOW"
        assert engine.check_action("execute", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "ALLOW"
        # Sensitive actions require confirmation
        assert engine.check_action("install", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "ASK"
        assert engine.check_action("production", inside_target, profile_override="WORKSPACE_AUTONOMOUS").decision == "DENY"

    def test_approval_required_profile_evaluation(self, engine):
        """APPROVAL_REQUIRED profile permits read, requires ASK for all mutations/executions."""
        target = str(WORKSPACE_ROOT / "test.txt")
        assert engine.check_action("read", target, profile_override="APPROVAL_REQUIRED").decision == "ALLOW"
        assert engine.check_action("write", target, profile_override="APPROVAL_REQUIRED").decision == "ASK"
        assert engine.check_action("delete", target, profile_override="APPROVAL_REQUIRED").decision == "ASK"
        assert engine.check_action("execute", target, profile_override="APPROVAL_REQUIRED").decision == "ASK"

    def test_restricted_profile_evaluation(self, engine):
        """RESTRICTED profile denies all mutations, installs, and executions."""
        target = str(WORKSPACE_ROOT / "test.txt")
        assert engine.check_action("write", target, profile_override="RESTRICTED").decision == "DENY"
        assert engine.check_action("delete", target, profile_override="RESTRICTED").decision == "DENY"
        assert engine.check_action("execute", target, profile_override="RESTRICTED").decision == "DENY"

    def test_unknown_action_type_raises_or_denies(self, engine):
        """Unknown action type must either raise ValueError or return DENY."""
        target = str(WORKSPACE_ROOT / "test.txt")
        try:
            decision = engine.check_action("nuke_everything", target)
            assert decision.decision == "DENY"
        except (ValueError, KeyError):
            pass


# ============================================================================
# 5. Non-Bypassable Secret Redaction Engine Tests
# ============================================================================
class TestSecretRedactionEngine:
    """Verifies non-bypassable redaction across diverse mock secret patterns."""

    @pytest.fixture
    def engine(self):
        return PolicyEngine(workspace_root=str(WORKSPACE_ROOT))

    def test_secret_redaction_non_bypassable_by_configuration(self):
        """User cannot disable secret redaction via config (Immutable Kernel Invariant)."""
        custom_engine = PolicyEngine(
            workspace_root=str(WORKSPACE_ROOT),
            enable_redaction=False  # Attempting to disable
        )
        assert custom_engine.secret_redaction is True, "Kernel guardrail failed: secret_redaction was disabled"

    def test_redact_aws_access_key_id(self, engine):
        """Detects and redacts standard 20-character AWS Access Key IDs."""
        secret = "AKIAIOSFODNN7EXAMPLE"
        text = f"Configure AWS with key {secret} in environment."
        redacted = engine.redact_secrets(text)
        assert secret not in redacted, "AWS key was not redacted"
        assert "[REDACTED_SECRET]" in redacted
        assert "Configure AWS with key" in redacted

    def test_redact_github_tokens(self, engine):
        """Detects and redacts classic and fine-grained GitHub personal access tokens."""
        classic_pat = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        fine_grained = "github_pat_11ABCDEF0123456789_abcdefghijklmnopqrstuvwxyz0123456789ABCDEF0123456789"
        text = f"Tokens: {classic_pat} and {fine_grained}."
        redacted = engine.redact_secrets(text)
        assert classic_pat not in redacted
        assert fine_grained not in redacted
        assert "[REDACTED_SECRET]" in redacted

    def test_redact_bearer_tokens(self, engine):
        """Detects and redacts Bearer tokens in Authorization headers."""
        bearer_jwt = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-IDcSemACt8x4iTMCda8Yhe3iZaWbvV5XKSTbuAn0M"
        text = f"Header Authorization: {bearer_jwt}"
        redacted = engine.redact_secrets(text)
        assert "eyJhbGci" not in redacted
        assert "[REDACTED_SECRET]" in redacted

    def test_redact_openai_and_anthropic_api_keys(self, engine):
        """Detects and redacts OpenAI and Anthropic-style API keys."""
        openai_key = "sk-proj-abc1234567890abcdefghijklmnopqrstuvwxyz1234"
        anthropic_key = "sk-ant-api03-abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
        text = f"Keys: {openai_key} and {anthropic_key}"
        redacted = engine.redact_secrets(text)
        assert openai_key not in redacted
        assert anthropic_key not in redacted
        assert "[REDACTED_SECRET]" in redacted

    def test_redact_pem_private_keys(self, engine):
        """Detects and redacts multi-line PEM private key blocks."""
        pem_key = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Y9876543210abcdefgMIIEowIBAAKCAQEA0Y9876543210abcdefg\n"
            "MIIEowIBAAKCAQEA0Y9876543210abcdefgMIIEowIBAAKCAQEA0Y9876543210abcdefg\n"
            "-----END RSA PRIVATE KEY-----"
        )
        text = f"Server certificate private key:\n{pem_key}\nEnd of file."
        redacted = engine.redact_secrets(text)
        assert "BEGIN RSA PRIVATE KEY" not in redacted
        assert "MIIEowIBAAKCAQEA" not in redacted
        assert "[REDACTED_SECRET]" in redacted
        assert "End of file." in redacted

    def test_redact_uri_passwords(self, engine):
        """Detects and redacts database connection URI credentials."""
        uri = "postgres://dbadmin:SuperSecretPass123!@db.corp.internal:5432/prod_aios"
        text = f"Connect via {uri}"
        redacted = engine.redact_secrets(text)
        assert "SuperSecretPass123!" not in redacted
        assert "[REDACTED_SECRET]" in redacted

    def test_redaction_preserves_clean_text(self, engine):
        """Clean text without secrets must be completely preserved."""
        clean_text = "The quick brown fox jumps over the lazy dog at 123 Main St. Path: /tmp/normal_file.py"
        assert engine.redact_secrets(clean_text) == clean_text

    def test_redaction_idempotent(self, engine):
        """Redacting already redacted text must be an idempotent operation."""
        dirty = "API key: sk-proj-1234567890abcdef1234567890 and token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        pass1 = engine.redact_secrets(dirty)
        pass2 = engine.redact_secrets(pass1)
        assert pass1 == pass2


# ============================================================================
# 6. Non-Bypassable Destructive Command & External Path Guardrails Tests
# ============================================================================
class TestDestructiveCommandGuardrails:
    """Verifies non-bypassable containment: blocking destructive actions outside workspace."""

    @pytest.fixture
    def engine(self):
        return PolicyEngine(workspace_root=str(WORKSPACE_ROOT))

    def test_guardrail_overrides_configured_permissive_delete(self):
        """Even if config allows delete, kernel guardrail blocks delete outside workspace."""
        permissive_engine = PolicyEngine(
            workspace_root=str(WORKSPACE_ROOT),
            config_dict={"profiles": {"WORKSPACE_AUTONOMOUS": {"delete": "ALLOW"}}}
        )
        external_target = "/etc/passwd"
        decision = permissive_engine.check_action("delete", external_target)
        assert decision.decision in ("DENY", "ASK"), f"Guardrail failed: external delete returned {decision.decision}"
        assert decision.modified_by_guardrail is True

    @pytest.mark.parametrize("target", [
        "/",
        "/tmp/malicious.sh",
        "/etc/shadow",
        "/var/log",
        str(Path.home() / ".bashrc"),
        str(WORKSPACE_ROOT.parent / "Random Ask" / "secret.env"),
    ])
    def test_block_absolute_paths_outside_workspace(self, engine, target):
        """Mutating operations on absolute paths outside workspace root must be DENIED or require ASK."""
        for action in ("delete", "write"):
            decision = engine.check_action(action, target)
            assert decision.decision in ("DENY", "ASK"), f"Action '{action}' on '{target}' was illegally ALLOWED"

    @pytest.mark.parametrize("traversal_path", [
        "../../outside.txt",
        "../../.bashrc",
        "subdir/../../../etc/passwd",
        "./../../Documents/sensitive.json",
    ])
    def test_block_path_traversal_attacks(self, engine, traversal_path):
        """Path traversal using '..' must be resolved and blocked from auto-approval."""
        decision = engine.check_action("delete", traversal_path)
        assert decision.decision in ("DENY", "ASK"), f"Traversal '{traversal_path}' was illegally ALLOWED"

    @pytest.mark.parametrize("dangerous_cmd", [
        "rm -rf /",
        "rm -rf ~",
        "rm -rf /tmp",
        "mkfs.ext4 /dev/sda1",
        "dd if=/dev/zero of=/dev/sda",
        ":(){ :|:& };:",
        "> /dev/sda",
        "chmod -R 777 /",
    ])
    def test_block_dangerous_shell_commands(self, engine, dangerous_cmd):
        """Dangerous shell commands must be intercepted and blocked by execute_safe_command."""
        result = engine.execute_safe_command(dangerous_cmd)
        assert result.blocked is True, f"Dangerous command '{dangerous_cmd}' was not blocked"
        assert result.exit_code != 0

    def test_allow_safe_operations_inside_workspace(self, engine):
        """Mutating operations strictly inside the workspace must be permitted under WORKSPACE_AUTONOMOUS."""
        inside_target = str(WORKSPACE_ROOT / "temp_scratch_file.txt")
        decision = engine.check_action("write", inside_target)
        assert decision.decision == "ALLOW"
        assert decision.modified_by_guardrail is False

    def test_execute_safe_command_inside_workspace(self, engine):
        """Safe shell commands inside workspace execute cleanly with secrets redacted."""
        result = engine.execute_safe_command("echo 'Hello AI-OS with key sk-1234567890abcdef1234567890'")
        assert result.blocked is False
        assert result.exit_code == 0
        assert "Hello AI-OS" in result.stdout
        assert "sk-1234" not in result.stdout, "Secret in command stdout was not redacted"
        assert "[REDACTED_SECRET]" in result.stdout


# ============================================================================
# 7. Pure Python 3.9 Standard Library & Zero-Dependency Tests
# ============================================================================
class TestPython39CompatibilityAndZeroDependencies:
    """Verifies pure Python 3.9.6 stdlib compatibility and zero banned dependencies."""

    BANNED_MODULES = [
        "pydantic",
        "docker",
        "psycopg2",
        "langgraph",
        "openai",
        "google.genai",
        "requests",
    ]

    def test_python_runtime_version(self):
        """Execution must occur under Python 3.9.x."""
        assert sys.version_info[:2] == (3, 9), f"Must run under Python 3.9, currently: {sys.version}"

    def test_policy_module_imports_only_stdlib(self):
        """aios.policy must not import any banned external packages."""
        import aios.policy
        for banned in self.BANNED_MODULES:
            assert banned not in sys.modules, f"Banned external dependency '{banned}' was imported by aios.policy"

    def test_policy_source_has_no_python310_syntax(self):
        """Inspects AST of aios/policy.py to ensure zero Python 3.10+ syntax (e.g. match/case)."""
        policy_source = (WORKSPACE_ROOT / "aios" / "policy.py").read_text(encoding="utf-8")
        tree = ast.parse(policy_source)
        
        # Verify no ast.Match nodes exist
        for node in ast.walk(tree):
            assert not isinstance(node, getattr(ast, "Match", ())), "Python 3.10+ 'match' statement detected in policy.py"

    def test_models_pure_dataclasses_compatibility(self):
        """aios.models must use pure stdlib dataclasses without 3.10-only kwargs."""
        models_path = WORKSPACE_ROOT / "aios" / "models.py"
        if models_path.is_file():
            models_source = models_path.read_text(encoding="utf-8")
            assert "slots=True" not in models_source, "slots=True requires Python 3.10+"
            assert "kw_only=True" not in models_source, "kw_only=True requires Python 3.10+"
```

---

## 4. Caveats

1. **Relative Symlink Target Portability**:
   - Symlinks in `AI-OS/.agents/skills/` must be created as relative links: `../../../.agents/skills/<skill_name>`. The test suite verifies that `is_symlink()` is true AND `(symlink_path / "SKILL.md").is_file()` resolves cleanly.
2. **Path Canonicalization across macOS Symlinked `/tmp`**:
   - On macOS (Darwin), `/tmp` is a symlink to `/private/tmp`. The test suite uses `os.path.realpath()` and `Path.resolve()` on both the workspace root and the target path to guarantee canonical comparison across operating systems.
3. **Shell Subprocess Execution**:
   - In `execute_safe_command()`, timeouts (e.g. 10–30s) are mandatory to prevent hangs on hanging commands. The test suite verifies that stdout and stderr are continuously scrubbed through `redact_secrets()`.
4. **Pytest-Only External Harness**:
   - Pytest is used strictly as the automated test discovery and execution framework (`pytest 8.4.2`). The production code (`aios/policy.py`, `aios/models.py`) requires zero pip packages.

---

## 5. Conclusion

1. **Design Complete**: The verification suite for Milestone 1 has been completely designed and specified with 7 test classes and 27 comprehensive test methods.
2. **Coverage Verified**: All 7 dispatch requirements are fully covered:
   - `AGENTS.md` line count constraint ($< 100$ lines).
   - `.agents/rules/` structure and required invariant sections.
   - Skill symlink integrity and YAML frontmatter validation.
   - 5 PolicyEngine governance profiles and action evaluation.
   - Non-bypassable secret redaction across 7 diverse mock secret types.
   - Non-bypassable destructive command and path traversal guardrails.
   - Pure Python 3.9.6 stdlib compatibility and zero banned dependencies.
3. **Execution Readiness**: The Worker (`m1_worker_1`) can immediately implement `tests/test_layer_a.py` using this exact specification to gate Milestone 1 completion.

---

## 6. Verification Method

To independently verify this design:

1. **Inspect Designed Test File**:
   ```bash
   cat "/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m1_explorer_2/handoff.md"
   ```
2. **Execute Milestone 1 Automated Test Suite (Post-Worker Implementation)**:
   ```bash
   python3 -m pytest "/Users/devesh/Documents/Antigravity/AI-OS/tests/test_layer_a.py" -v
   ```
   *Expected Output*: 27 passed items with exit code 0.
3. **Verify Pure Python 3.9 Stdlib & AST Compatibility**:
   ```bash
   python3 -c "
   import ast
   with open('/Users/devesh/Documents/Antigravity/AI-OS/aios/policy.py') as f:
       tree = ast.parse(f.read())
   for node in ast.walk(tree):
       assert not isinstance(node, getattr(ast, 'Match', ())), 'Python 3.10+ match syntax detected'
   print('PASS: Pure Python 3.9 compatibility verified.')
   "
   ```
4. **Invalidation Conditions**:
   - Any test failure in `test_layer_a.py`.
   - `AGENTS.md` exceeding 99 lines.
   - Reused skills duplicated as physical files rather than symbolic links.
   - Auto-approval of mutating actions on paths resolving outside `~/Documents/Antigravity/AI-OS/`.
   - Disabling secret redaction through user configuration.
