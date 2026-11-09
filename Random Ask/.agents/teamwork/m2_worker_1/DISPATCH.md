# Task Assignment: Milestone 2 Skill Package Implementer (`m2_worker_1`)

## Working Directory
`/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_worker_1/`

## Context & Inputs
- Original Request: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md`
- Master Project Index: `/Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md`
- M2 Explorer 1 Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/analysis.md`
- M2 Explorer 2 Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md`
- M2 Explorer 3 Analysis: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_3/analysis.md`
- Master Research Report: `/Users/devesh/Documents/Antigravity/Random Ask/docs/research/claude_cognitive_architecture_report.md`
- E2E Test Suite Index: `/Users/devesh/Documents/Antigravity/Random Ask/TEST_INFRA.md` & `/Users/devesh/Documents/Antigravity/Random Ask/TEST_READY.md`

## Exclusive Write Ownership
You have exclusive write ownership over `/Users/devesh/Documents/Antigravity/Random Ask/skills/claude/` and all its subdirectories:
- `skills/claude/SKILL.md`
- `skills/claude/references/extended_thinking.md`
- `skills/claude/references/epistemic_humility.md`
- `skills/claude/references/solution_architecture.md`
- `skills/claude/references/planning_execution.md`
- `skills/claude/examples/distributed_systems_consensus.md`
- `skills/claude/examples/complex_refactoring_architecture.md`
- `skills/claude/examples/logic_puzzle_constraint_anchoring.md`
- `skills/claude/resources/behavioral_checklist.json`
- `skills/claude/resources/prompt_scaffolds.md`

DO NOT modify files outside `skills/claude/` and your working directory.

## Objective
Implement the complete Antigravity skill package for the "claude" skill by extracting and assembling the comprehensive blueprints created by `m2_explorer_1`, `m2_explorer_2`, and `m2_explorer_3`:
1. `SKILL.md`: Root specification with valid YAML frontmatter (`name: claude`, description, regex-compliant, dual-trigger support, `metadata: { icon: psychology, category: reasoning }`), strictly under 24,000 bytes, progressive disclosure linking to `references/`, `examples/`, `resources/`, Universal `<claude_thinking>` 4-phase directive, and operational heuristics.
2. `references/*.md`: 4 reference sub-documents detailing extended thinking, epistemic humility, solution architecture, and planning/execution (incorporating Unicode NFC counting, user explanation override, and bimodal context branching).
3. `examples/*.md`: 3 realistic multi-turn reasoning exemplars (distributed systems Raft consensus, complex refactoring with clean AST-validated Python code, logic puzzle with verbatim double-quote constraint quoting and discrete index counting).
4. `resources/behavioral_checklist.json`: Valid JSON defining all 12 canonical markers (M01 to M12).
5. `resources/prompt_scaffolds.md`: Multi-model prompt wrappers for GPT-4o, Gemini 2.0 Pro, Llama 3.3, Qwen 2.5, DeepSeek with balanced variable braces (`{{...}}`).

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification Requirements
Run the build and test verification suite:
`python3 -m pytest -m m2 tests/e2e/ -v`
and
`python3 -m pytest tests/e2e/ --allow-pending -v`

Ensure all Milestone 2 E2E tests pass with exit code 0.
Write your handoff report to `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_worker_1/handoff.md`.
Notify the orchestrator when complete.

## 2026-11-06T21:43:20Z
[Message] timestamp=2026-11-06T21:43:20Z sender=cb7d9db9-6105-4e8f-9a3c-1ba50aaa0049 priority=MESSAGE_PRIORITY_HIGH content=You are m2_worker_1 (role: Skill Package Implementer).
Your working directory is /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_worker_1/

You MUST read:
1. ORIGINAL_REQUEST.md: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md
2. Master Project Index: /Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md
3. M2 Explorer 1 Analysis: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/analysis.md
4. M2 Explorer 2 Analysis: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md
5. M2 Explorer 3 Analysis: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_3/analysis.md
6. Master Research Report: /Users/devesh/Documents/Antigravity/Random Ask/docs/research/claude_cognitive_architecture_report.md
7. DISPATCH.md: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_worker_1/DISPATCH.md

Exclusive Write Ownership:
You own all files in /Users/devesh/Documents/Antigravity/Random Ask/skills/claude/

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Implement all 10 package files in skills/claude/:
- SKILL.md
- references/extended_thinking.md
- references/epistemic_humility.md
- references/solution_architecture.md
- references/planning_execution.md
- examples/distributed_systems_consensus.md
- examples/complex_refactoring_architecture.md
- examples/logic_puzzle_constraint_anchoring.md
- resources/behavioral_checklist.json
- resources/prompt_scaffolds.md

Run test verification:
`python3 -m pytest -m m2 tests/e2e/ -v`
and
`python3 -m pytest tests/e2e/ --allow-pending -v`

Write your handoff report to /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_worker_1/handoff.md
Maintain progress.md with regular "Last visited" timestamps.
When complete, notify the orchestrator via send_message.
