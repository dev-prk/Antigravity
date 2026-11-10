# Milestone 1 Exploration & Architecture Blueprint Report: Layer A Scaffolding & Policy Engine

**Agent**: `m1_explorer_1` (Teamwork Explorer)  
**Date**: 2026-11-10T18:20:00Z  
**Target Workspace**: `/Users/devesh/Documents/Antigravity/AI-OS/`  
**Milestone**: Milestone 1 (Layer A Scaffolding & Policy Engine)  
**Recipient**: `39b23d44-0f11-43fa-90e1-e4883d67348f` (Orchestrator)  
**Status**: Exploration & Blueprint Complete  

---

## 1. Observation

### 1.1 Direct Environment & Filesystem Observations
1. **Target Directory State**:
   - Inspected `ls -la /Users/devesh/Documents/Antigravity/AI-OS/ 2>&1`: directory is currently non-existent (`No such file or directory`). The Worker will initialize this workspace cleanly.
2. **Available Global Skills Inventory**:
   - Inspected `/Users/devesh/Documents/Antigravity/.agents/skills/`:
     - `claude/`: Contains `SKILL.md` (7,208 bytes), `examples/`, `references/`, `resources/`. 4-phase cognitive scratchpad.
     - `orchestration/`: Contains `SKILL.md` (4,531 bytes). Lead agent decomposition, bounded tasks, effort budgeting.
     - `loop-engineering/`: Contains `SKILL.md` (5,821 bytes). 5-component loop pattern, dual exit gates, circuit breakers, hard budget caps.
     - `chain-of-mindset/`: Contains `SKILL.md` (5,475 bytes), `scripts/`. Dynamic cognitive mode switching (Algorithmic, Spatial, Divergent, Convergent).
   - All four target skills are fully present, functional, and conform to the global rule (`disable-model-invocation: true`, `disable-slash-command: false`).
3. **Symlink Relative Path Resolution**:
   - Calculated relative path from `~/Documents/Antigravity/AI-OS/.agents/skills/` to global skills in `~/Documents/Antigravity/.agents/skills/`:
     - From `AI-OS/.agents/skills/`:
       - `..` resolves to `AI-OS/.agents/`
       - `../..` resolves to `AI-OS/`
       - `../../..` resolves to `~/Documents/Antigravity/`
       - `../../../.agents/skills/<skill>` resolves to `~/Documents/Antigravity/.agents/skills/<skill>`
     - Empirically verified via Python `pathlib.Path.resolve()`:
       `pathlib.Path('/Users/devesh/Documents/Antigravity/AI-OS/.agents/skills/../../../.agents/skills/claude').resolve()` $\to$ `/Users/devesh/Documents/Antigravity/.agents/skills/claude` (`exists: True`).
4. **Authoritative Mandates & Invariants**:
   - `ORIGINAL_REQUEST.md` (R1): Establish Layer A in `~/Documents/Antigravity/AI-OS/` with `AGENTS.md` (invariants under 100 lines), governance rules (`.agents/rules/`), and reasoning skills (`.agents/skills/`) reusing existing skills without duplication. User-configurable policy layer without bypassing safety controls, keeping secret redaction and prohibition of unapproved external destructive actions non-configurable.
   - `PROJECT.md` (Feature 1–5):
     - Feature 1: `AGENTS.md` Constitution (< 100 lines).
     - Feature 2: Governance Rules (`security.md`, `coding.md`, `verification.md`).
     - Feature 3: Skill Reuse Symlinks (`claude`, `orchestration`, `loop-engineering`, `chain-of-mindset`).
     - Feature 4: Policy Engine (`READ_ONLY`, `SANDBOX_AUTONOMOUS`, `WORKSPACE_AUTONOMOUS`, `APPROVAL_REQUIRED`, `RESTRICTED`).
     - Feature 5: Immutable Kernel Guardrails (secret redaction, external destructive blocking).
5. **Python Runtime & Dependencies**:
   - Python version: `3.9.6`. Standard library provides `sqlite3`, `dataclasses`, `json`, `pathlib`, `re`, `subprocess`, `typing`.
   - `pydantic` is NOT installed. Pure standard library `@dataclass` must be used for data contracts.

---

## 2. Logic Chain

### 2.1 AGENTS.md Constitution Design (< 100 Lines)
- **Constraint**: `wc -l < AGENTS.md` must be strictly $< 100$.
- **Function**: Serves as the immutable root system prompt and constitution for any AI agent executing within AI-OS.
- **Deduction**: The file must contain only high-leverage invariants that prevent catastrophic failures, maintain token discipline, and enforce safety boundaries, delegating granular procedural rules to `.agents/rules/`.
- **Exact Blueprint (36 Lines)**:
  ```markdown
  # AI-OS Root Constitution & Invariants

  You are operating within the AI-OS autonomous execution environment.
  Workspace root: ~/Documents/Antigravity/AI-OS/

  ## 1. Non-Bypassable Kernel Invariants
  1. **Safety & Permission Controls**: Never bypass provider safety controls, sandbox limits, or policy permission gates.
  2. **Secret Redaction**: API keys, access tokens, credentials, private keys, and secrets must NEVER appear in logs, prompts, databases, or outputs. All streams must be sanitized.
  3. **Workspace Boundary**: Autonomous mutating operations (file writes, deletes, installations) are strictly confined to `~/Documents/Antigravity/AI-OS/`. Unapproved destructive actions outside this workspace are strictly FORBIDDEN.
  4. **Token Budget Discipline**: Enforce hard token budgets. At 80% task token budget, trigger a state checkpoint and generate `HANDOFF.md`. At 95%, halt execution cleanly (exit code 0) rather than failing mid-phase.
  5. **State Persistence & Resumability**: Every task must persist state across the 8-table SQLite schema (`aios.db`) and maintain an automated `HANDOFF.md` (strictly <= 1,500 tokens). Resumption must continue from the next pending step without duplicate execution.
  6. **Zero External Services & Paid APIs**: Zero paid API keys, zero external database servers (no Postgres, Docker, or Ollama). Pure Python 3.9 standard library and local SQLite only.
  7. **Verifier Separation**: A generator agent never grades its own work. Completion claims require independent verification backed by recorded command evidence.

  ## 2. Governance Profiles
  Policy loaded from `config/policies.json`:
  - `READ_ONLY`: Inspection only. File modifications and process execution denied.
  - `SANDBOX_AUTONOMOUS`: Autonomous execution restricted to isolated sandbox directory.
  - `WORKSPACE_AUTONOMOUS`: Default profile. Full autonomy inside `~/Documents/Antigravity/AI-OS/`. External destructive operations denied.
  - `APPROVAL_REQUIRED`: All mutating and execution operations require human operator approval.
  - `RESTRICTED`: Minimal diagnostic execution only.

  ## 3. Skill & Reasoning Invariants
  - Reusable skills reside in `.agents/skills/` (`claude`, `orchestration`, `loop-engineering`, `chain-of-mindset`) and must be progressively loaded without byte duplication.
  - Mandatory 4-phase reasoning: Understand -> Classify/Plan -> Execute -> Verify.
  - Every claim of fact must be backed by concrete evidence in the SQLite `evidence` table.
  ```

### 2.2 Modular Governance Rules (`.agents/rules/`)
Divided into three authoritative documents:
1. **`security.md`**:
   - **Secret Redaction Rules**:
     - Strict regex suite: OpenAI keys (`\b(?:sk|pk)-(?:live|test)?[a-zA-Z0-9_\-]{20,}\b`), Google/Gemini API keys (`\bAIza[0-9A-Za-z\-_]{35}\b`), GitHub tokens (`\bgh[pousr]_[a-zA-Z0-9]{36,255}\b`), AWS Access Key IDs (`\bAKIA[0-9A-Z]{16}\b`), PEM Private Keys (`-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----`), Bearer tokens (`(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}`), Password/secret assignments (`(?i)(?:password|passwd|secret|api_key|token)\s*[:=]\s*['"][^'"]{4,}['"]`).
     - Replacement token: `[REDACTED_SECRET]`.
     - Kernel rule: Non-configurable. If user configuration sets `force_secret_redaction: false`, PolicyEngine forcibly sets it to `true` and logs an audit security warning.
   - **Destructive Command Blocking**:
     - Denylisted patterns: `rm -rf /`, `rm -rf ~`, `mkfs`, `dd if=`, fork bombs, `git reset --hard` (outside repository), `DROP DATABASE`, `TRUNCATE TABLE`.
   - **Path Containment**:
     - Canonical root: `~/Documents/Antigravity/AI-OS/` (resolved via `os.path.realpath`).
     - Any path escaping the workspace boundary via `..` or symlinks is blocked or escalated to `ASK`.
2. **`coding.md`**:
   - **Python 3.9 Standard Library Mandate**: 100% compliant with Python 3.9.6 stdlib. No pip dependencies in `aios/` runtime.
   - **Syntax Constraints**: No Python 3.10+ `match/case` statements. No `|` union type annotations without `from __future__ import annotations`. Use `typing.Union`, `typing.Optional`, `typing.List`, `typing.Dict`.
   - **Data Modeling**: Standard library `@dataclass(frozen=...)` with `.to_dict()` and `.from_dict()` serialization methods.
   - **Atomic Transactions**: SQLite context manager `with conn: ...` for ACID guarantees.
3. **`verification.md`**:
   - **Evidentiary Standard**: Every verified fact or completed step must reference an entry in the SQLite `evidence` table containing `command`, `exit_code` (0 for pass), `stdout`, `stderr`, and SHA-256 `content_hash`.
   - **Verifier Separation**: "Generator never grades own homework." Implementation work must be verified by automated test suites or an independent verifier module.
   - **Interruption/Resumption Verification**: Automated tests must demonstrate task resumption without re-executing completed steps.

### 2.3 Skill Reuse Symlink Architecture (`.agents/skills/`)
- To strictly adhere to the user requirement ("reuse existing skills... rather than rewriting them"), create relative symbolic links inside `AI-OS/.agents/skills/`:
  - `AI-OS/.agents/skills/claude` $\to$ `../../../.agents/skills/claude`
  - `AI-OS/.agents/skills/orchestration` $\to$ `../../../.agents/skills/orchestration`
  - `AI-OS/.agents/skills/loop-engineering` $\to$ `../../../.agents/skills/loop-engineering`
  - `AI-OS/.agents/skills/chain-of-mindset` $\to$ `../../../.agents/skills/chain-of-mindset`
- Accompany with `AI-OS/.agents/skills/README.md` documenting the integration and cognitive reasoning mapping.

### 2.4 User-Configurable Policy Engine & Kernel Guardrails
- **File**: `config/policies.json`
- **Profiles**:
  - `READ_ONLY`: Read allowed; writes, deletes, executions denied.
  - `SANDBOX_AUTONOMOUS`: Full autonomy inside isolated sandbox directory.
  - `WORKSPACE_AUTONOMOUS`: Full autonomy inside workspace; external actions denied/asked.
  - `APPROVAL_REQUIRED`: All mutations and executions require confirmation.
  - `RESTRICTED`: Minimal survival actions only.
- **Kernel Guardrail Overrides (Non-Configurable in `aios/policy.py`)**:
  1. `force_secret_redaction`: Forced `True` at code level regardless of user JSON.
  2. `block_unapproved_external_destructive`: Any `delete` or destructive operation targeting a path resolving outside `workspace_root` cannot be `ALLOW`. It is forcibly converted to `ASK` or `DENY`.
  3. `execute_safe_command`: Shell command executor that blocks destructive denylist patterns, captures subprocess execution, and scrubs secrets from stdout/stderr.

---

## 3. Caveats

1. **Relative vs Absolute Symlinks**:
   - Symlinks MUST use relative paths (`../../../.agents/skills/<skill>`) rather than absolute paths (`/Users/devesh/...`) so that the repository remains portable across machines and CI environments without broken links.
2. **Directory Resolution & Traversal**:
   - Path containment checking in `PolicyEngine` must use `pathlib.Path(target).resolve()` to dereference symlinks and collapse `../` sequences before comparing with `workspace_root.resolve()`.
3. **Pydantic Absence**:
   - Because `pydantic` is not installed in the environment, all policy data classes must use Python standard library `@dataclass`.
4. **Shell Subprocess Execution**:
   - In `execute_safe_command`, timeouts must be enforced (default 30s) and secrets redacted even when a command fails or throws `CalledProcessError`.

---

## 4. Conclusion & Concrete Worker Instructions

The architectural design for Milestone 1 is completely specified, verified against constraints, and ready for immediate implementation by `m1_worker_1`.

### Concrete File Inventory for Worker to Create:
1. `~/Documents/Antigravity/AI-OS/AGENTS.md` (36 lines, strictly $< 100$ lines).
2. `~/Documents/Antigravity/AI-OS/.agents/rules/security.md` (Secret redactor, destructive command guards, workspace boundary).
3. `~/Documents/Antigravity/AI-OS/.agents/rules/coding.md` (Python 3.9 stdlib, type hints, dataclasses, error handling).
4. `~/Documents/Antigravity/AI-OS/.agents/rules/verification.md` (Evidence requirements, independent verifier separation).
5. `~/Documents/Antigravity/AI-OS/.agents/skills/` (Symlinks for `claude`, `orchestration`, `loop-engineering`, `chain-of-mindset` pointing to `../../../.agents/skills/<name>`, plus `README.md`).
6. `~/Documents/Antigravity/AI-OS/config/policies.json` (5 governance profiles + kernel invariants).
7. `~/Documents/Antigravity/AI-OS/aios/__init__.py` and `aios/policy.py` (`PolicyEngine`, `PolicyDecision`, `CommandResult`, `PolicyViolationError`).
8. `~/Documents/Antigravity/AI-OS/tests/__init__.py` and `tests/test_layer_a.py` (Complete unit test suite verifying all Layer A requirements).

---

## 5. Verification Method

The Worker and Auditor can independently verify Milestone 1 implementation by executing:

1. **Verify `AGENTS.md` Line Count (< 100 Lines)**:
   ```bash
   line_count=$(wc -l < "/Users/devesh/Documents/Antigravity/AI-OS/AGENTS.md")
   echo "AGENTS.md line count: $line_count"
   test "$line_count" -lt 100 && echo "PASS: AGENTS.md under 100 lines"
   ```
2. **Verify Symlink Resolution**:
   ```bash
   for skill in claude orchestration loop-engineering chain-of-mindset; do
     test -f "/Users/devesh/Documents/Antigravity/AI-OS/.agents/skills/$skill/SKILL.md" && echo "PASS: $skill resolves" || echo "FAIL: $skill broken"
   done
   ```
3. **Run Automated Test Suite for Layer A**:
   ```bash
   python3 -m pytest "/Users/devesh/Documents/Antigravity/AI-OS/tests/test_layer_a.py" -v
   ```
4. **Verify Kernel Guardrail Overrides Offline**:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '/Users/devesh/Documents/Antigravity/AI-OS')
   from aios.policy import PolicyEngine
   engine = PolicyEngine()
   # Secret redaction check
   redacted = engine.redact_secrets('key=sk-1234567890abcdef1234567890 and token=ghp_1234567890abcdefghijklmnopqrstuvwxyz1234')
   assert 'sk-' not in redacted and 'ghp_' not in redacted, 'Failed secret redaction'
   # External destructive check
   decision = engine.check_action('delete', '/etc/passwd')
   assert decision.decision in ('DENY', 'ASK'), 'Failed destructive block'
   print('PASS: PolicyEngine kernel guardrails verified.')
   "
   ```
5. **Invalidation Conditions**:
   - `AGENTS.md` contains 100 or more lines.
   - Any skill is duplicated as a file instead of a symbolic link.
   - Symlinks are broken or point to non-existent directories.
   - Destructive actions outside `~/Documents/Antigravity/AI-OS/` can be auto-approved under any configuration profile.
   - Secret redaction can be disabled via configuration.
