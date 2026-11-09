# Milestone 2 Explorer 2 Handoff Report: Skill References Sub-docs Blueprint

**Document Status**: Authoritative Explorer Handoff Report  
**Agent**: `m2_explorer_2` (Skill References Sub-docs Explorer)  
**Parent / Orchestrator**: `cb7d9db9-6105-4e8f-9a3c-1ba50aaa0049`  
**Milestone**: Milestone 2 (Antigravity "claude" Skill Specification Package)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/`  
**Date**: November 2026 (Investigation Timestamp: 2026-11-06T21:52:00Z)  
**Primary Deliverable**: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md`  

---

## 1. Observation

1. **Project Index and Architecture Requirements (`PROJECT.md`)**:
   - Lines 88–92 of `/Users/devesh/Documents/Antigravity/Random Ask/PROJECT.md` define the mandatory code layout for the 4 core reference documents under `skills/claude/references/`:
     ```
     skills/claude/references/
     ├── extended_thinking.md          # Pillar 1: Cognitive scratchpad & pacing
     ├── epistemic_humility.md         # Pillar 2: Calibration, anti-sycophancy, bounds
     ├── solution_architecture.md      # Pillar 3: Modularity, types, defensive design
     └── planning_execution.md         # Pillar 4: Constraint anchoring, step indexing
     ```
   - Lines 45–60 establish interface contracts: `SKILL.md` must be $\le 24,000$ bytes (conforming to the Antigravity runtime limit) and must offload granular domain guidelines to `references/`.
   - Feature 7 (line 24) mandates: *"Progressive Disclosure Hierarchy (`references/`): Modular sub-documents (`references/*.md`) for extended thinking, epistemic humility, architecture standards, and planning execution under the 24KB limit."*

2. **Antigravity Customization Architecture & Runtime Discovery (`survey_spec_miner_2/survey_report.md`)**:
   - Section 2.1 (lines 35–43) defines the progressive disclosure model:
     > *"references/ (Recommended for Complex Skills): Contains granular markdown sub-documentation... In accordance with Antigravity's progressive disclosure principle, files here are not injected into the model's initial prompt; the agent reads them on demand via file inspection tools (view_file) only when relevant."*
   - Section 4.1 (lines 224–250) models the 3-tier disclosure hierarchy: Tier 1 (Catalog entry in system prompt: ~50 tokens), Tier 2 (`SKILL.md` body read upon trigger: ~1,500–3,000 tokens), Tier 3 (Modular references in `references/` read on demand).
   - Section 4.2 (lines 257–287) documents the native Go template from the Antigravity `language_server` binary instructing models to inspect skill files using exact relative/absolute paths.

3. **Cognitive Trait Modeling (`docs/research/claude_cognitive_architecture_report.md`)**:
   - Section 2 (lines 87–268): Dissects extended thinking, test-time compute scaling laws (Snell et al. 2024), conversational metacognition, linguistic markers of cognitive velocity control, the autoregressive commitment trap, and the chain-of-thought faithfulness paradox (Lanham et al. 2023).
   - Section 3 (lines 269–383): Details epistemic humility, the pathology of sycophancy (Perez et al. 2022), the human preference optimization bug in RLHF (Sharma et al. 2023), the multi-turn capitulation trap (*"Are you sure?"*), long-tail hallucination notices, citation restraint, and 1–2 sentence non-preachy refusals.
   - Section 4 (lines 384–538): Catalogs Anthropic's official system prompt operational directives: verbatim puzzle constraint quoting, discrete character/sub-word indexing, decisive single-choice recommendation, post-code explanation suppression, and prose dominance.
   - Section 5 (lines 539–738): Outlines lean agentic harness engineering ("Lean on the model, strip down the harness", Schluntz & Zhang 2024), parallel read-only vs serialized mutation queues, progressive elaboration, strong type boundaries, 3-tier error taxonomy, and zero-stub craftsmanship.
   - Section 6 (lines 739–850): Formalizes the universal `<claude_thinking>` 4-phase cognitive scratchpad scaffold.

4. **Adversarial Hardening Recommendations (`m1_challenger_2/handoff.md`)**:
   - Challenge 1 (lines 18–31): Verbatim puzzle constraint quotation directive in `docs/research/claude_cognitive_architecture_report.md` line 422 contained a duplicate token `"before"`. Mitigation: rectify into clean Anthropic wording without duplicate tokens in Milestone 2.
   - Challenge 2 (lines 32–41): Sub-word counting heuristics fail on Unicode combining diacritics (NFC vs NFD, e.g. `"café"` being 4 vs 5 codepoints) and multi-codepoint grapheme clusters (emojis like `"👨‍👩‍👧‍👦"` containing 7 codepoints), hyphenated token delimiters, and autoregressive drift on strings $>40$ characters. Mitigation: specify Unicode NFC normalization and grapheme cluster grouping before 1-indexed numbering.
   - Challenge 3 (lines 42–53): Post-code explanation suppression causes friction when users explicitly pre-authorize explanations upfront, repeats redundantly across multi-block responses, or blocks operational prerequisite commands (`pip install`, test commands). Mitigation: pre-authorized explanation bypass, single opt-in query after final code block, and exemption of operational prerequisites.
   - Challenge 4 (lines 54–59): Single decisive recommendation heuristic conflicts with comparative user prompts (*"Compare the top 3 relational databases"*). Mitigation: explicit comparative requests override single-choice heuristic.

5. **E2E Test Infrastructure Invariants (`tests/e2e/`)**:
   - `test_tier1_feature_coverage.py`:
     - Line 431: Asserts all 4 files exist in `skills/claude/references/` (`extended_thinking.md`, `epistemic_humility.md`, `solution_architecture.md`, `planning_execution.md`).
     - Line 449: Asserts `SKILL.md` contains valid relative links (`./references/` or `references/`).
     - Line 460: Asserts sub-documents start with Markdown header `#`.
     - Line 470: Asserts total size of `references/` markdown files $> 1,000$ bytes.
     - Line 476: Asserts all reference links use POSIX forward slashes (no Windows `\`).
   - `test_tier2_boundaries.py`:
     - Lines 408–411: Asserts all relative markdown links in `SKILL.md` resolve to existing physical files.
     - Line 430: Asserts no reference file is 0 bytes.
     - Line 440: Asserts all reference filenames are strictly lowercase.
     - Line 451: Asserts `references/` contains *only* `.md` files (rejects `.json`, `.py`, etc.).
   - `test_tier3_combinations.py`:
     - Line 128: Asserts `SKILL.md` links to all 4 reference filenames.
     - Lines 169–174: Asserts `references/solution_architecture.md` contains `"modular"`, `"decoupling"`, or `"architecture"`, matching `examples/complex_refactoring_architecture.md`.

---

## 2. Logic Chain

1. **Premise 1 (Progressive Disclosure Architecture)**: `SKILL.md` must remain concise ($\le 24$KB) to avoid diluting the model's prompt context upon activation. Detailed multi-page specifications for Claude's 4 cognitive pillars must be offloaded into modular reference sub-documents.
2. **Premise 2 (Direct Mapping to Cognitive Pillars)**:
   - Pillar 1 (Extended Thinking & Pacing) $\to$ `references/extended_thinking.md`
   - Pillar 2 (Epistemic Calibration & Anti-Sycophancy) $\to$ `references/epistemic_humility.md`
   - Pillar 3 (Modularity, Typing & Defensive Craftsmanship) $\to$ `references/solution_architecture.md`
   - Pillar 4 (Constraint Anchoring, Index Counting & Operational Directives) $\to$ `references/planning_execution.md`
3. **Premise 3 (Incorporation of Challenger Hardening)**: The edge cases identified by `m1_challenger_2` must be addressed inside the reference sub-docs to prevent model failures in downstream benchmarks and Tier 2/4 E2E tests:
   - Unicode NFC normalization and grapheme cluster grouping resolved in `planning_execution.md`.
   - Pre-authorized explanation override, multi-block opt-in consolidation, and command exemption resolved in `planning_execution.md` and `extended_thinking.md`.
   - Comparative prompt override resolved in `planning_execution.md`.
   - Typographical erratum resolved in `planning_execution.md`.
   - Bimodal execution branching (System 1 vs System 2) resolved in `extended_thinking.md`.
4. **Premise 4 (Test Suite Contract Compliance)**: All 4 files must be lowercase `.md` files starting with `#`, reside in `skills/claude/references/`, be linked from `SKILL.md` via POSIX `./references/<name>.md`, contain no non-markdown sibling files, and exceed 1,000 bytes in aggregate.
5. **Conclusion**: By producing exhaustive blueprints for all 4 sub-documents in `analysis.md` (covering tables of contents, theoretical rationale, operational directives, code exemplars, and test mappings), `m2_worker_1` can implement the complete `references/` package without ambiguity or missing requirements.

---

## 3. Caveats

1. **Read-Only Scope Enforcement**: As an explorer agent (`m2_explorer_2`), this investigation is strictly read-only. No files were created or modified inside `skills/claude/` or other project directories. All blueprints and specifications reside in `analysis.md` within `.agents/teamwork/m2_explorer_2/`.
2. **Implementation Responsibility**: Actual file creation in `skills/claude/references/` will be executed by the implementation worker (`m2_worker_1`).
3. **Host Environment Tool Constraints**: The skill provides cognitive and formatting directives for target models; it does not replace the native Antigravity host tools (`view_file`, `run_command`, etc.).

---

## 4. Conclusion

The architectural investigation and structural blueprinting of the four core reference sub-documents in `skills/claude/references/` is **COMPLETE** and fully documented in:
`/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md`

### Summary of Blueprinted Deliverables for `m2_worker_1`:

1. **`skills/claude/references/extended_thinking.md`** (~14 KB):
   - Theoretical foundation: Autoregressive commitment trap & Lanham et al. (2023) causal conditioning.
   - Bimodal execution: System 1 (budget = 0, instantaneous) vs System 2 (budget 1k–128k tokens).
   - Dynamic token budget scaling tiers (Tier 0 to Tier 3) and capacity inequality invariant.
   - Internal monologue anatomy: Conversational metacognition, velocity control linguistic markers.
   - Dynamic backtracking protocol and branching hypothesis simulation ($\ge 2$ approaches).
   - Complete 4-phase `<claude_thinking>` protocol specification, strict tag boundaries, and anti-nesting rules.

2. **`skills/claude/references/epistemic_humility.md`** (~14 KB):
   - Theoretical foundation: Perez et al. (2022) sycophancy scaling and Sharma et al. (2023) preference bug.
   - Multi-turn capitulation defense: *"Are you sure?"* pushback handling, reflexive apology prohibition.
   - Epistemic demarcation: 3-tier distinction (Verified Facts, Deductive Inferences, Working Assumptions).
   - Long-tail knowledge: Latent parametric density monitoring, mandatory use of the term *"hallucinate"*, zero fake URLs.
   - Bibliographic discipline: Concept-first citations, explicit refusal to confabulate academic literature.
   - Refusal protocol: 1–2 neutral sentences, zero preachiness, zero apologies, constructive technical pivot.
   - Terminology non-correction and presumption of legitimacy.

3. **`skills/claude/references/solution_architecture.md`** (~16 KB):
   - Architectural philosophy: "Lean on the model, strip down the harness" (Schluntz & Zhang 2024).
   - Tool concurrency contract: Parallel read-only queue vs strictly serialized mutation queue.
   - Context engineering: Context collapsing, surgical AST replacements (`replace_file_content`), external disk memory (`CLAUDE.md`, `progress.md`).
   - 5-stage progressive elaboration lifecycle (Domain Boundaries $\to$ Typed Contracts $\to$ Pure Domain Logic $\to$ Adapters $\to$ Defensive Wrappers).
   - Strong typing: Frozen dataclasses, Pydantic models, immutable value objects, `__post_init__` validation.
   - 3-tier error handling taxonomy: Domain Errors (local catch, zero retry), Transient Errors (exponential backoff + jitter, circuit breakers), Fatal Errors (fail-fast, rollback).
   - Production craftsmanship: Zero-stub policy (ban on `// TODO`, `pass`), explicit `NotImplementedError` fallbacks, deterministic verification interlocks.

4. **`skills/claude/references/planning_execution.md`** (~16 KB):
   - Verbatim constraint quoting: Anthropic directive, neutralizing the "Classic Variant Trap", clean phrasing without duplicate tokens, preservation of negative constraints.
   - Discrete index counting: Sub-word BPE blindness neutralization, canonical `char(index)` ledger.
   - Unicode NFC & grapheme cluster boundary handling: NFC normalization (`café`), multi-codepoint emojis (`👨‍👩‍👧‍👦`), hyphenated token delimiter semantics, counter drift mitigation (>40 chars).
   - Decisive single-choice recommendation heuristic: Neutralizing option sprawl, context-driven defense, comparative prompt override protocol.
   - Post-code explanation suppression: Immediate closing syntax, polite opt-in formula, upfront user pre-authorization override, multi-block aggregation (opt-in after final block), operational prerequisites exemption.
   - Natural prose dominance: Flowing paragraphs over fragmented bulleted lists, substantive sentence bullets.
   - Conversational discipline: Zero conversational pleasantries (*"Certainly!"* banned), direct technical entry.
   - Task planning: Topological dependency DAGs, critical path identification, verifiable validation gate checks.

---

## 5. Verification Method

To independently verify the completeness, consistency, and compliance of this blueprint:

1. **Verify Deliverable Existence & Size**:
   ```bash
   ls -lh "/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md"
   ```
   *Expected Result*: File exists with size $\approx 47$ KB.

2. **Verify Section Heading & Blueprint Coverage in `analysis.md`**:
   ```bash
   grep -E "^## [0-9]" "/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md"
   ```
   *Expected Result*: All 8 major sections present, covering executive scope, interaction matrix, detailed specifications for all 4 reference documents, implementation guidance for `m2_worker_1`, and summary table.

3. **Verify Adversarial Hardening Inclusions**:
   ```bash
   grep -i -E "(unicode|grapheme|pre-authorization|comparative|erratum|bimodal)" "/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/m2_explorer_2/analysis.md"
   ```
   *Expected Result*: Multiple confirmed hits across all Challenger recommendations.

4. **Verify E2E Test Suite Readiness**:
   ```bash
   python3 -m pytest -m m1 tests/e2e/ -v
   ```
   *Expected Result*: 10 passed, 0 failed, 166 deselected in $<0.1$s, confirming test suite health.
