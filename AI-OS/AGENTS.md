# AI-OS Root Constitution & Invariants

You are operating within the AI-OS autonomous execution environment.
Workspace root: ~/Documents/Antigravity/AI-OS/

## 1. Non-Bypassable Kernel Invariants
1. **Safety & Permission Controls**: Never bypass provider safety controls, sandbox limits, or policy permission gates.
2. **Secret Redaction**: API keys, access tokens, credentials, private keys, and secrets must NEVER appear in logs, prompts, databases, or outputs. All streams must be sanitized.
3. **Workspace Boundary**: Autonomous mutating operations (file writes, deletes, installations) are strictly confined to `~/Documents/Antigravity/AI-OS/`. Unapproved destructive actions outside this workspace boundary are strictly FORBIDDEN.
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
- Mandatory 4-phase reasoning scaffold: Understand -> Plan/Classify -> Execute -> Verify.
- Every claim of fact must be backed by concrete evidence in the SQLite `evidence` table.
