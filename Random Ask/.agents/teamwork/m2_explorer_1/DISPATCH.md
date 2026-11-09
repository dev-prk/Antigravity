# Task Assignment: Milestone 2 Explorer 1 (`m2_explorer_1`)

## Working Directory
`/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/`

## Context & Inputs
- Original Request: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md`
- Master Project Index: `/Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md`
- Milestone 1 Report: `/Users/devesh/Documents/Antigravity/Random Ask/docs/research/claude_cognitive_architecture_report.md`
- Survey 2 Spec Mining Report: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/survey_spec_miner_2/survey_report.md`
- E2E Test Suite Index: `/Users/devesh/Documents/Antigravity/Random Ask/TEST_INFRA.md` & `/Users/devesh/Documents/Antigravity/Random Ask/TEST_READY.md`

## Milestone Objective
Milestone 2: Design and implement the complete Antigravity "claude" skill specification package in `skills/claude/`.

## Your Specific Scope
Investigate and design the root specification file `skills/claude/SKILL.md`:
1. Valid YAML frontmatter:
   - `name: claude` (regex `^[A-Za-z0-9._-]{1,64}$`)
   - `description`: comprehensive third-person description stating what the skill does and when to use it for semantic model invocation.
   - `disable-slash-command: false`
   - `disable-model-invocation: false`
   - `metadata: { icon: psychology, category: reasoning }`
2. Size and context limits: Must strictly remain under 24,000 bytes (conforming to Antigravity 24KB limit).
3. Progressive disclosure structure: serves as an executive instruction orchestrator linking to `references/` sub-documents.
4. Universal `<claude_thinking>` cognitive scratchpad directive with 4 phases (Constraint Anchoring, Hypothesis Exploration & Counter-Factual Stress Testing, Architectural Blueprinting, Output Calibration).
5. Operational rules: verbatim constraint quoting, index counting, single decisive recommendation, post-code explanation suppression, and prose preference.
6. Provide exact section outline and recommended implementation blueprint for `skills/claude/SKILL.md`.

Write your analysis to `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/analysis.md`.
Write your handoff report to `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/handoff.md`.
Notify the orchestrator via `send_message`.

## 2026-11-06T21:34:42Z
[Message] timestamp=2026-11-06T21:34:42Z sender=cb7d9db9-6105-4e8f-9a3c-1ba50aaa0049 priority=MESSAGE_PRIORITY_HIGH content=You are m2_explorer_1 (role: Skill Root Specification Explorer).
Your working directory is /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/

You MUST read:
1. ORIGINAL_REQUEST.md: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/ORIGINAL_REQUEST.md
2. Master Project Index: /Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md
3. Milestone 1 Report: /Users/devesh/Documents/Antigravity/Random Ask/docs/research/claude_cognitive_architecture_report.md
4. Survey 2 Spec Mining Report: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/survey_spec_miner_2/survey_report.md
5. DISPATCH.md: /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/DISPATCH.md

Investigate and blueprint skills/claude/SKILL.md: YAML frontmatter conformance, 24KB limit adherence, progressive disclosure architecture, and universal scratchpad integration.
Write analysis to /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/analysis.md
Write handoff report to /Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_1/handoff.md
Maintain progress.md with regular "Last visited" timestamps.
When complete, notify the orchestrator via send_message.
