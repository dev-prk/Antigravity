Implement Phase 3a (Layer A: Antigravity-native instructions, rules, skills, and handoff protocol) and Phase 3b (SQLite state, task ledger, HANDOFF.md, and token budget management) of the model-agnostic AI-OS blueprint, operating strictly within consumption limits and without paid APIs.

Working directory: ~/Documents/Antigravity/AI-OS/
Integrity mode: [OPEN: Integrity restrictions on external code, pre-built frameworks, or tools?]

Reference material: /Users/devesh/.gemini/antigravity/brain/51dfcb5c-2be9-41af-bdd8-523dde84779d/ai_os_blueprint.md

## Requirements

### R1. Layer A Implementation (Antigravity-Native Scaffolding)
Establish the Antigravity-native layer including AGENTS.md invariants, governance rules, and core reasoning skills by reusing existing skills (`claude`, `orchestration`, `loop-engineering`, `chain-of-mindset`) from `~/Documents/Antigravity/.agents/skills/`. Implement the structured reasoning and handoff protocol without modifying provider safety controls.

### R2. Phase 3b State and Task Management Runtime
Implement a Python 3.9-compatible SQLite state engine, task ledger, token budget tracking, and `HANDOFF.md` generator/resumer in `aios/` that operates with zero paid APIs and requires no new runtime installations (no Docker, Postgres, Ollama, or Python 3.12 without explicit approval).

### R3. Token Budgeting and Phased Execution
Enforce strict budget caps and phase boundary stops. After completing each phase, write state checkpoints and a concise `HANDOFF.md` (≤1.5k tokens) capturing goal, completed steps, next actions, and blockers, stopping cleanly instead of exhausting limits mid-phase.

### R4. Verification and Evidence
[OPEN: What verification resources and test mechanisms should validate completion of Phase 3a and Phase 3b?]

## Acceptance Criteria

### Execution & Governance
- [ ] Layer A configuration and rules are established in `~/Documents/Antigravity/AI-OS/` adhering to Python 3.9 compatibility and workspace sync rules.
- [ ] No paid APIs, external service keys, or unapproved runtime tools are introduced.
- [ ] Policy layer enforces workspace boundaries and secret redaction without bypassing provider safety mechanisms.

### State & Budget
- [ ] SQLite database initialises tables for tasks, steps, evidence, decisions, checkpoints, and budget usage.
- [ ] Token budgeting mechanism tracks usage and triggers clean handoff generation at threshold boundaries.
- [ ] [OPEN: Acceptance criteria for Phase 3a/3b exit tests?]
