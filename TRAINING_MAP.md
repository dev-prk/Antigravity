# Antigravity Training Map

The single source of state for the "train Antigravity like a child" project. A new session reads
this file instead of old chats. Update it at the end of every session (scorecard + next steps).

Last updated: 2026-11-24

## Graph

```mermaid
graph TD
  U[Devesh<br/>vision + final judge] -->|asks| C[Claude<br/>planner · architect · mentor · auditor]
  C -->|writes brief + exam tasks| A[Antigravity · Gemini 4 Argon<br/>executor]
  A -->|loads| S["/deliver skill<br/>.agents/skills/deliver/SKILL.md"]
  S -->|real cases| E[references/examples.md<br/>lessons 1–5]
  A -->|builds in| T[SkillTest/<br/>current test app]
  A -->|writes evidence| P[PROGRESS.md<br/>brief + audit trail]
  C -->|audits: hand math, contrast,<br/>edge cases| T
  C -->|failure found| L[New lesson]
  L -->|added to| E
  L -->|rule tightened in| S
  G[GEMINI.md<br/>always-on rules] -.->|loaded every chat| A
  X[Exam set<br/>NOT BUILT YET] -.->|scores progress| A
```

**Loop:** Claude briefs → Argon builds with `/deliver` → Claude audits every step → each failure
becomes a lesson → the lesson tightens the skill → re-test on a *new* task (never the same one,
since its answer is now in the examples).

## Nodes (where things live)

| Node | Path |
|---|---|
| Skill | `~/Documents/Antigravity/.agents/skills/deliver/SKILL.md` (symlinked to `~/.claude/skills/deliver`) |
| Lessons | `.../deliver/references/examples.md` |
| Always-on rules | `~/Documents/Antigravity/GEMINI.md` (repo auto-pushes to GitHub via the Stop hook) |
| Test 1 app (resume matcher) | `~/Documents/Antigravity/SkillTest_run1/` |
| Test 2 app (EXPLAIN analyzer) | `~/Documents/Antigravity/SkillTest/` (runs on :8765 via `run.sh`) |
| Argon transcripts | `~/.gemini/antigravity/brain/<id>/.system_generated/logs/transcript.jsonl` |
| Chat index | `~/.gemini/antigravity/conversation_summaries.db` |

## Why Antigravity failed (from 200+ old chats)

1. No reasoning: 0 thinking tokens; it went straight to writing big files.
2. Scope blow-up: 9 questions in a row, every "Recommended" option the biggest.
3. Faked parts: hardcoded user inputs; keyword if/else posing as AI.
4. Self-certification: "verified" because its own tests passed; invented metrics.
5. Symptom patching after rejection ("You're 100% right" + more branches).
6. Process theatre: 180 sub-agents, visible `<claude_thinking>` rituals.

## Scorecard (audited by Claude, not self-reported)

| Behaviour | Before skill | Test 1 (resume matcher) | Test 2 (EXPLAIN analyzer) |
|---|---|---|---|
| Looks before building | ❌ | ✅ found working Gemini key, real resumes | ✅ |
| Writes brief with expert gaps | ❌ | ✅ | ✅ correct DBA math (loops, 8 KiB blocks) |
| Small build-run loops | ❌ | ❌ 640-line file in one go | ⚠️ appended chunks, but a 74 KB engine |
| Output comes from the input | ❌ | ❌ canned advice; pastry chef scored "89" | ✅ |
| Contrast / bad-input test | ❌ | ❌ | ✅ healthy plan → 0 findings |
| Edge-case math | — | ❌ "8+ years" not parsed | ❌ parallel plans: self time ×3 |
| Honest report | ❌ | ⚠️ | ⚠️ claimed timings "confirmed", parallel untested |
| Scope discipline | ❌ | ❌ | ❌ JSON + practice mode + presets |

## Open lessons (not yet in the skill)

- **Report only what was tested.** "Confirmed exclusive timings" without trying parallel plans is
  an overclaim. The "Not checked" list must name the untested cases the expert gap itself raised.
- **Scope:** the "smallest version" keeps growing. Consider a hard rule: v1 = only the must-haves,
  with extras offered as a one-line list after delivery.

## Next steps

1. Add the two open lessons to `/deliver` (examples.md #6).
2. Optional: have Argon fix the parallel bug from a one-line hint, to test the rejection flow
   (section 8).
3. Build the exam set: 5 fixed tasks from past failures plus a scoring rubric Claude applies.
   Re-run it when new Gemini models ship.
4. Keep `LESSONS.md` short: promote proven lessons into the skill, delete unused ones.
