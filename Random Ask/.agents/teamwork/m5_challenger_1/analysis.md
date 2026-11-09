# Milestone 5 Phase 2: Tier 5 White-Box Adversarial Coverage Analysis

**Author**: `m5_challenger_1` (Empirical Challenger)  
**Date**: 2026-11-07  
**Scope**: `skills/claude/`, `tests/evaluation/`, `tests/e2e/`  

---

## 1. Executive Summary

As part of Milestone 5 Phase 2 (Tier 5 White-Box Adversarial Coverage Hardening), an adversarial audit was conducted on the Claude Antigravity Skill package (`skills/claude/`) and the evaluation engine (`tests/evaluation/`). 

While Tiers 1-4 provided broad opaque-box coverage across 176 test cases, white-box source code inspection revealed several unexercised edge cases, implicit invariants, boundary conditions, and potential attack vectors:
1. **Schema & Typology Invariants**: Python's type hierarchy treats `isinstance(True, int) == True`. Explicit guards against booleans, `math.isnan`, and `float('inf')` in `DimensionScore` and `MarkerChecklist` needed rigorous adversarial boundary testing.
2. **Boundary Length Thresholds**: The strict CR prompt threshold in `BenchmarkCase.__post_init__` (`len(prompt) <= 100`) required off-by-one boundary validation ($99, 100, 101$).
3. **JSON Repair & Malformed LLM Outputs**: `parse_judge_json` includes regex-based JSON extraction and trailing-comma repair, which required adversarial stress testing against markdown fences, preambles, trailing commas, and score clamping.
4. **Mathematical & Statistical Singularities**: `compute_information_density` singularity handling for $N \le 1$ tokens ($\log_2(0)$, $\log_2(1)$), bootstrap CI edge cases ($N=0, N=1$), and position-bias detection symmetry.
5. **CLI Fault Tolerance**: CLI runner behavior under invalid benchmark paths, directory auto-creation, and token count estimations on Unicode/empty strings.

To harden the codebase against these failure modes, a comprehensive Tier 5 adversarial test suite (`tests/e2e/test_tier5_adversarial.py`) with 22 rigorous adversarial test cases decorated with `@pytest.mark.tier5` and `@pytest.mark.m5` has been authored and verified empirically.

---

## 2. Threat Modeling & White-Box Source Analysis

### 2.1 `tests/evaluation/schemas.py`
- **Prefix-Dimension Coherence**: `BenchmarkCase` verifies `id.startswith(f"TC-{self.dimension}")` and regex `^TC-(CR|PD|SA|EP|EH)-\d{2}$`. Any mismatch (e.g., `id="TC-CR-01"` with `dimension="SA"`) must fail immediately.
- **CR Prompt Length Guard**: Explicit validation `if self.dimension == "CR" and len(self.prompt) <= 100` enforces that complex reasoning prompts cannot be trivial strings. Tested boundaries: 99 (fail), 100 (fail), 101 (pass).
- **Rubric Anchors Strictness**: `RubricAnchors.from_dict` enforces non-empty strings and raises `TypeError` on non-dict inputs, rejecting whitespace-only anchors.
- **Boolean & NaN Type Leakage**: In Python, `isinstance(True, int)` is true. `DimensionScore` and `MarkerChecklist` explicitly guard against booleans, `math.isnan(val)`, and out-of-range floats. Tested inputs: `True`, `float('nan')`, `float('inf')`, `0.999`, `5.001`.
- **Duplicate ID Detection in JSONL**: `load_benchmarks` tracks `seen_ids` and raises `ValueError` on duplicates, while gracefully skipping empty lines.

### 2.2 `tests/evaluation/scoring.py`
- **Immutability of Weights**: `CANONICAL_CCRS_WEIGHTS` is encapsulated in `MappingProxyType`. Direct mutation attempts must raise `TypeError`.
- **Singularity in Information Density**: $IDS = CCRS / \log_2(T)$. When $T \le 1$, division by zero ($\log_2(1) = 0$) or negative infinity ($\log_2(0) = -\infty$) would occur. Hardened protection must return `0.0`.
- **Bootstrap Confidence Interval Edge Cases**: Sequence lengths of $N=0$ and $N=1$ must not crash `sample_sem` or `bootstrap_confidence_interval`.
- **Paired Delta Dimension Matching**: `evaluate_contrastive_delta` must reject mismatched sequence lengths with `ValueError`.

### 2.3 `tests/evaluation/judge.py`
- **LLM Output Extraction**: Judges often return text wrapping JSON in ` ```json ... ``` ` or accompanied by conversational filler. `parse_judge_json` must extract the valid JSON object.
- **Auto-Repair of Trailing Commas**: Trailing commas before `}` or `]` must be parsed or repaired cleanly.
- **Score Clamping & Alias Mapping**: Out-of-bounds scores (e.g., 99.9, -5.0) must be clamped to $[1.0, 5.0]$. Dimension aliases (e.g., `"complex reasoning"`) must normalize to `"CR"`. Unknown preferences must fall back to `"tie"`.
- **Position Bias Detection Symmetry**: When a judge exhibits pure position bias ($A$ preferred in both passes or $B$ preferred in both passes), `position_bias_detected` must be `True`.

### 2.4 `tests/evaluation/runner.py`
- **Graceful CLI Exit Codes**: Missing benchmark files must raise `FileNotFoundError` and return exit code 1 without unhandled stack traces.
- **Directory Autocreation**: The runner must auto-create parent directories for output paths if they do not exist.
- **Token Count Estimation**: Empty strings or whitespace-only inputs must return at least 1 token to prevent downstream division issues.

### 2.5 `skills/claude/`
- **Antigravity Metadata Invariants**: Skill name regex (`^[A-Za-z0-9._-]{1,64}$`), size $\le 24,000$ bytes, and substantive descriptions.
- **Scratchpad Tags**: Missing closing tag, inverted tag sequence, missing phases, or out-of-order phases must be detected.
- **Exemplar Python Code Blocks**: All Python code blocks in `skills/claude/examples/*.md` must compile cleanly with `ast.parse`.

---

## 3. Tier 5 Adversarial Test Specification

The following 22 test cases are defined in `tests/e2e/test_tier5_adversarial.py`:

| Test ID | Test Function | Target Component | Adversarial Vulnerability / Edge Case Tested |
|---|---|---|---|
| T5-01 | `test_t5_adv_01_benchmark_case_id_pattern_and_prefix_mismatch` | `schemas.BenchmarkCase` | Invalid regex format (`TC-CR-1`, `TC-CR-001`) and prefix-dimension mismatch |
| T5-02 | `test_t5_adv_02_cr_prompt_length_boundary_stress` | `schemas.BenchmarkCase` | Exact boundary validation: 99 chars (fail), 100 chars (fail), 101 chars (pass) |
| T5-03 | `test_t5_adv_03_rubric_anchors_malformed_and_whitespace` | `schemas.RubricAnchors` | Non-dict inputs (`TypeError`), whitespace-only anchors (`ValueError`), dual format |
| T5-04 | `test_t5_adv_04_dimension_score_nan_inf_bool_rejection` | `schemas.DimensionScore` | Rejection of `True`, `float('nan')`, `float('inf')`, out-of-bounds floats (`0.999`, `5.001`) |
| T5-05 | `test_t5_adv_05_marker_checklist_strict_typing_and_count` | `schemas.MarkerChecklist` | Rejection of boolean values, out-of-range integers (-1, 2), count != 12, unknown markers |
| T5-06 | `test_t5_adv_06_load_benchmarks_corrupted_jsonl_and_duplicates` | `schemas.load_benchmarks` | Handling of JSON syntax error, duplicate benchmark IDs, skipping whitespace lines |
| T5-07 | `test_t5_adv_07_canonical_weights_immutability_and_attribution` | `scoring.CANONICAL_CCRS_WEIGHTS` | Mutation attempt on `MappingProxyType`, sum == 1.0, exact weight attribution |
| T5-08 | `test_t5_adv_08_ccrs_boundary_extremes_and_type_safety` | `scoring.compute_ccrs` | Boundary scores (1s -> 0.0, 5s -> 100.0, 3s -> 50.0), type errors, missing dimensions |
| T5-09 | `test_t5_adv_09_bcr_strict_contract_and_dimension_slicing` | `scoring.compute_bcr` | Full zeros, full ones, invalid marker count, dimension BCR slicing (`compute_dimension_bcr`) |
| T5-10 | `test_t5_adv_10_information_density_singularity_protection` | `scoring.compute_information_density` | Zero token, one token, negative token singularity protection; exact logarithmic scaling |
| T5-11 | `test_t5_adv_11_statistical_bounds_and_bootstrap_invariants` | `scoring.bootstrap_confidence_interval` | Empty list, single element list, deterministic seed reproducibility, interval bounds |
| T5-12 | `test_t5_adv_12_judge_json_markdown_fence_and_preamble_extraction` | `judge.parse_judge_json` | Extraction from markdown ```json blocks, leading/trailing chatter, trailing comma repair |
| T5-13 | `test_t5_adv_13_judge_json_score_clamping_and_fallback_resilience` | `judge.parse_judge_json` | Clamping extreme scores (-5 -> 1.0, 99.9 -> 5.0), fallback to 3.0, alias mapping, tie fallback |
| T5-14 | `test_t5_adv_14_dual_run_position_swap_bias_detection_engine` | `judge.PositionSwapResult` | Detection of pure position bias (A/A, B/B) vs debiased merit wins (B/A) and double tie |
| T5-15 | `test_t5_adv_15_runner_cli_error_codes_and_directory_autocreation` | `runner.run_evaluation` | Exit code 1 on missing benchmark, directory auto-creation for output, limit flag |
| T5-16 | `test_t5_adv_16_runner_estimate_token_count_edge_cases` | `runner.estimate_token_count` | Empty string -> 1, whitespace string -> 1, large 10k-word input, Unicode/emoji safety |
| T5-17 | `test_t5_adv_17_contrastive_delta_evaluation_and_length_mismatch` | `scoring.evaluate_contrastive_delta` | Mismatched lengths error, empty results error, paired delta calculation accuracy |
| T5-18 | `test_t5_adv_18_scratchpad_parser_adversarial_malformed_xml` | `conftest.parse_claude_thinking_scratchpad` | Unclosed tags, inverted tags, missing phase 3, out-of-order phases, XML nesting |
| T5-19 | `test_t5_adv_19_skill_frontmatter_adversarial_injections_and_types` | `conftest.validate_skill_metadata` | Command injection in name, length > 64 chars, non-boolean flags, description < 10 chars |
| T5-20 | `test_t5_adv_20_exemplar_python_code_block_ast_audit` | `skills/claude/examples/*.md` | AST parse audit of all Python code blocks across all markdown exemplars |
| T5-21 | `test_t5_adv_21_behavioral_checklist_integrity_and_rubric_anchors` | `skills/claude/resources/` | Behavioral checklist 12-marker schema, canonical dimensions, benchmark rubric alignment |
| T5-22 | `test_t5_adv_22_runner_results_schema_conformance` | `runner.EvaluationRunner` | Full execution and validation against `RunnerOutput` schema |

---

## 4. Verification and Execution Plan

1. Create `tests/e2e/test_tier5_adversarial.py` with all 22 test cases.
2. Run targeted execution: `python3 -m pytest tests/e2e/test_tier5_adversarial.py -v`.
3. Run full test suite execution: `python3 -m pytest tests/e2e/ -v` (176 existing + 22 Tier 5 = 198 tests total).
4. Verify 100% pass rate with zero regressions.
