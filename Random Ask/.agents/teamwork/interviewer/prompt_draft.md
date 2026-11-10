Build Phase 3a (Layer A: Antigravity-native rules, skills, and handoff protocol) and Phase 3b (SQLite state, task ledger, HANDOFF.md, and token budget management) of the model-agnostic AI-OS for production workspace use, strictly managing token consumption to avoid exhausting limits mid-project.

Working directory: ~/Documents/Antigravity/AI-OS/
Integrity mode: development

Reference material: /Users/devesh/.gemini/antigravity/brain/51dfcb5c-2be9-41af-bdd8-523dde84779d/ai_os_blueprint.md

## Verification Resources
- Existing benchmark runner in `~/Documents/Antigravity/Random Ask/tests/evaluation`
- Existing skills in `~/Documents/Antigravity/.agents/skills/` (`claude`, `orchestration`, `loop-engineering`, `chain-of-mindset`)

## Requirements

### R1. Layer A Implementation (Antigravity-Native Scaffolding)
Establish Layer A in `~/Documents/Antigravity/AI-OS/` including an `AGENTS.md` (invariants under 100 lines), governance rules (`.agents/rules/`), and reasoning skills (`.agents/skills/`) by reusing existing skills (`claude`, `orchestration`, `loop-engineering`, `chain-of-mindset`) rather than rewriting them. Implement a user-configurable policy layer without bypassing provider safety controls or permission checks, keeping secret redaction and the prohibition of unapproved destructive actions outside the workspace non-configurable.

### R2. Phase 3b State and Task Management Runtime
Implement a Python 3.9-compatible runtime in `aios/` with an SQLite state database (`tasks`, `steps`, `evidence`, `decisions`, `facts`, `checkpoints`, `budget_usage`, `audit_log`), a task ledger, and an automated `HANDOFF.md` generator/resumer (target ≤1.5k tokens). Require zero paid APIs, add no API keys, and introduce no external service dependencies (no Docker, Postgres, Ollama, or Python 3.12).

### R3. Token Budgeting and Phased Execution Boundary
Implement token consumption tracking with hard task/session budgets. Ensure execution writes a checkpoint and a concise `HANDOFF.md` (goal, done, next action, blockers) at phase boundaries or budget thresholds (e.g. 80%), stopping cleanly rather than failing mid-phase.

### R4. Automated Testing and Resume Verification
Verify the build using automated tests and command output evidence before reporting completion. Test SQLite state operations, task ledger updates, budget threshold triggers, and execute an automated kill/resume test demonstrating that a stopped task cleanly continues from `HANDOFF.md` and database state, leveraging the existing benchmark runner in `~/Documents/Antigravity/Random Ask/tests/evaluation`.

## Acceptance Criteria

### Governance & Compatibility
- [ ] All code runs cleanly on Python 3.9.6 with no syntax or library incompatibilities.
- [ ] No paid API keys or external services (Docker, Postgres, Ollama) are required or configured.
- [ ] Policy layer enforces secret redaction and prevents auto-approval of destructive actions outside `~/Documents/Antigravity/AI-OS/`.
- [ ] Existing skills in `~/Documents/Antigravity/.agents/skills/` are reused without duplicate rewrites.

### State, Ledger & Handoff
- [ ] SQLite database initialises all required tables (`tasks`, `steps`, `evidence`, `decisions`, `facts`, `checkpoints`, `budget_usage`, `audit_log`) and performs CRUD operations.
- [ ] Budget tracker accurately records token usage and fires checkpoints at configured budget thresholds.
- [ ] `HANDOFF.md` is generated with goal, done, next action, and blockers, staying within 1.5k tokens.

### Verification Evidence
- [ ] Automated test suite runs and passes for the SQLite database, task ledger, budget tracker, and handoff generator.
- [ ] An automated kill/resume test succeeds: a simulated interrupted task resumes execution using `HANDOFF.md` and the SQLite checkpoint.
- [ ] Real command output and test execution logs are provided as verifiable evidence of Phase 3a and Phase 3b completion.
