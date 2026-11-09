# Project: claude-skill

## Architecture
The "claude" skill project enables any AI model (GPT-4o, Gemini 2.0, open-weights) to reliably emulate the latest Claude models' thinking, reasoning, architecture, and problem-solving patterns. The project is organized in a Dual-Track Architecture:
1. **Implementation Track**:
   - Milestone 1: Authoritative Research Report on Claude's Cognitive Architecture.
   - Milestone 2: Antigravity Skill Specification Package (`skills/claude/`).
   - Milestone 3: Comparative Evaluation Benchmark Suite & Automated Runner (`tests/evaluation/`).
   - Milestone 4: Empirical Validation Execution & Comparative Analysis Report (`docs/evaluation/`).
   - Milestone 5: Final Milestone (100% E2E Pass across Tiers 1-4 + Tier 5 Adversarial Coverage Hardening).
2. **E2E Testing Track**:
   - Independent opaque-box test infrastructure (`tests/e2e/`) verifying all features across 4 tiers (Feature Coverage, Boundary & Corner Cases, Cross-Feature Combinations, Real-World Application Scenarios).

## Feature Inventory
Every feature from the Survey phase is mapped below with an assigned milestone:
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Claude Cognitive Architecture Research Report | Comprehensive research report deconstructing Claude 3.5/3.7/Opus cognitive traits, extended thinking, epistemic humility, system prompt directives, Claude Code agentic harness, and cross-model elicitation | M1 | Survey 1 |
| 2 | Universal `<claude_thinking>` 4-Phase Scratchpad | Mandatory 4-phase cognitive scratchpad scaffold (Constraint Anchoring, Hypothesis Exploration & Counter-Factual Stress Testing, Architectural Blueprinting, Output Calibration) | M1, M2 | Survey 1 |
| 3 | Epistemic Humility & Anti-Sycophancy Rules | Operational rules for admitting uncertainty, explicit hallucination notices, premise verification, and single decisive recommendation | M1, M2 | Survey 1 |
| 4 | Verbatim Constraint Quoting & Index Counting | Strict system prompt rules quoting puzzle constraints word-for-word and assigning numbers to discrete items/letters before answering | M1, M2 | Survey 1 |
| 5 | Post-Code Explanation Suppression & Concise Delivery | Suppression of unsolicited post-code breakdowns, offering breakdowns only upon request, prose preference over lists | M1, M2 | Survey 1 |
| 6 | Antigravity Skill Root Specification (`SKILL.md`) | Reusable Antigravity skill specification with valid YAML frontmatter (`name: claude`, regex-compliant, dual slash-command and semantic invocation, description) | M2 | Survey 2 |
| 7 | Progressive Disclosure Hierarchy (`references/`) | Modular sub-documents (`references/*.md`) for extended thinking, epistemic humility, architecture standards, and planning execution under the 24KB limit | M2 | Survey 2 |
| 8 | Reference Implementations & Exemplars (`examples/`) | Realistic examples demonstrating Claude-style multi-turn reasoning traces, complex decomposition, system architecture blueprints, and counterfactual tests | M2 | Survey 2 |
| 9 | Verification Checklists & Scaffolds (`resources/`) | Machine-readable checklists, scoring anchors, and prompt scaffolds for multi-model adaptation | M2 | Survey 2 |
| 10 | 5-Dimensional Benchmark Suite (`benchmarks.jsonl`) | 15 high-friction test cases (`TC-CR-01` to `TC-EH-03`) spanning Complex Reasoning, Problem Decomposition, Solution Architecture, Execution Planning, and Epistemic Humility with baseline failure traps and 1-3-5 rubric anchors | M3 | Survey 3 |
| 11 | Contrastive Triad Evaluation Runner (`runner.py`, `judge.py`) | Automated evaluation runner executing Condition 0 (Baseline) vs Condition 1 (Skill) with dual-run position-swapping ($A/B \to B/A$) and length-controlled normalization | M3 | Survey 3 |
| 12 | Composite Scoring Engine (CCRS & BCR) | Scoring engine implementing the Composite Claude Replication Score and 12-Marker Binary Behavioral Checklist | M3 | Survey 3 |
| 13 | Documented Comparative Validation Results | Empirical evaluation report documenting comparative model outputs with and without the skill, proving replication of Claude's problem-solving and architectural patterns | M4 | Survey 3 |
| 14 | Opaque-Box E2E Test Suite (Tiers 1-4) | Comprehensive requirement-driven opaque-box test suite verifying all package artifacts, schemas, CLI tools, and end-to-end workflows | E2E Track | Dual Track Spec |
| 15 | Tier 5 Adversarial Coverage Hardening | White-box adversarial edge-case generation and hardening by Challengers | M5 | Dual Track Spec |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Research Report & Cognitive Modeling Synthesis | Comprehensive research report in `docs/research/claude_cognitive_architecture_report.md` | Survey complete | DONE |
| M2 | Antigravity "claude" Skill Specification Package | Complete `skills/claude/` package (`SKILL.md`, `references/`, `examples/`, `resources/`) | M1 contracts | PLANNED |
| M3 | Comparative Evaluation Suite & Benchmark Runner | `tests/evaluation/` benchmark suite (15 test cases), runner, judge, and scoring engine | Survey 3, M2 contracts | PLANNED |
| M4 | Empirical Validation & Comparative Results Documentation | Run evaluations, score outputs, compile `docs/evaluation/comparative_evaluation_report.md` | M2, M3 | PLANNED |
| M5 | Final Milestone: 100% E2E Pass & Tier 5 Adversarial Hardening | Pass 100% E2E test suite (Tiers 1-4) and execute Tier 5 Challenger-driven adversarial hardening | M1, M2, M3, M4, TEST_READY | PLANNED |
| E2E | E2E Testing Track Orchestrator | Opaque-box test suite across Tiers 1-4, publish `TEST_INFRA.md` & `TEST_READY.md` | Survey complete | DONE |

## Interface Contracts
### `skills/claude/SKILL.md` ↔ Antigravity Runtime
- Frontmatter:
  ```yaml
  ---
  name: claude
  description: Enables any model to replicate Claude's latest thinking, reasoning, architecture, and problem-solving patterns through structured cognitive scratchpads, epistemic humility, constraint anchoring, and clean execution.
  metadata:
    icon: psychology
    category: reasoning
  disable-slash-command: false
  disable-model-invocation: false
  ---
  ```
- File size: `SKILL.md` must be ≤24,000 bytes (conforming to Antigravity 24KB limit). Sub-documents placed in `references/`.
- Scratchpad Tag: `<claude_thinking>...</claude_thinking>` with 4 internal phases.

### `tests/evaluation/` ↔ Benchmarks & Runner
- Data format: `tests/evaluation/benchmarks.jsonl` where each line conforms to:
  ```json
  {
    "id": "TC-CR-01",
    "dimension": "Complex Reasoning",
    "prompt": "...",
    "baseline_failure_mode": "...",
    "claude_behaviors": ["..."],
    "rubric": {"1": "...", "3": "...", "5": "..."}
  }
  ```
- Runner CLI:
  `python3 tests/evaluation/runner.py --benchmarks tests/evaluation/benchmarks.jsonl --output results/evaluation_results.json`
- Metrics:
  - CCRS: $[0, 100]$ Composite Claude Replication Score
  - BCR: $[0, 100\%]$ Behavioral Compliance Rate across 12 markers

## Code Layout
```
/Users/devesh/Documents/Antigravity/Random Ask/
├── PROJECT.md                                # Project master governance & index
├── TEST_INFRA.md                             # E2E test suite index (published by E2E track)
├── TEST_READY.md                             # Signal when E2E test suite is ready
├── skills/
│   └── claude/
│       ├── SKILL.md                          # Mandatory skill entrypoint with YAML frontmatter
│       ├── references/
│       │   ├── extended_thinking.md          # Pillar 1: Cognitive scratchpad & pacing
│       │   ├── epistemic_humility.md         # Pillar 2: Calibration, anti-sycophancy, bounds
│       │   ├── solution_architecture.md      # Pillar 3: Modularity, types, defensive design
│       │   └── planning_execution.md         # Pillar 4: Constraint anchoring, step indexing
│       ├── examples/
│       │   ├── distributed_systems_consensus.md  # Raft / Paxos architectural trace
│       │   ├── complex_refactoring_architecture.md# Monolith decomposition trace
│       │   └── logic_puzzle_constraint_anchoring.md# Constraint quotation trace
│       └── resources/
│           ├── behavioral_checklist.json     # 12-marker evaluation checklist
│           └── prompt_scaffolds.md           # Multi-model prompting scaffolds
├── docs/
│   ├── research/
│   │   └── claude_cognitive_architecture_report.md # Research report on latest Claude models
│   └── evaluation/
│       ├── comparative_evaluation_report.md        # Comprehensive empirical validation report
│       └── benchmark_rubrics.md                    # Rubric anchors and scoring guidelines
└── tests/
    ├── evaluation/
    │   ├── benchmarks.jsonl                  # 15 curated benchmark test cases
    │   ├── runner.py                         # Evaluation test runner
    │   ├── judge.py                          # Dual-run position-swapping LLM judge
    │   ├── scoring.py                        # CCRS and BCR scoring logic
    │   └── schemas.py                        # Pydantic/dataclass validation schemas
    └── e2e/
        ├── conftest.py                       # Pytest fixtures and environment setup
        ├── test_tier1_feature_coverage.py    # Tier 1: ≥5 tests per feature
        ├── test_tier2_boundaries.py          # Tier 2: Boundary & corner cases
        ├── test_tier3_combinations.py        # Tier 3: Cross-feature interactions
        └── test_tier4_real_world.py          # Tier 4: Realistic end-to-end workflows
```
