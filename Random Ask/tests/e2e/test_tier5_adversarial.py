"""
tests/e2e/test_tier5_adversarial.py
Milestone 5 Tier 5 White-Box Adversarial Coverage Hardening Test Suite.

Contains 22 rigorous adversarial test cases stress-testing:
- Mathematical routines, statistical moments, bootstrap resamples, and singularities
- Schema parsing, prompt injection resilience, malformed types, and off-by-one bounds
- Dual-run position-swapping bias detection symmetry and LLM-as-a-judge json repair
- CLI runner fault tolerance, exit codes, and directory auto-creation
- AST validation of Python code exemplars and Antigravity metadata safety
"""

from __future__ import annotations

import ast
import json
import math
import os
import re
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List

import pytest

from tests.evaluation.judge import (
    CANONICAL_DIMENSIONS as JUDGE_DIMENSIONS,
    EvaluationJudge,
    JudgeConfig,
    JudgeOutput,
    PositionSwapResult,
    clamp_score,
    compute_position_swap_win_rate,
    parse_judge_json,
)
from tests.evaluation.runner import (
    EvaluationRunner,
    estimate_token_count,
    run_evaluation,
)
from tests.evaluation.schemas import (
    CANONICAL_12_MARKERS,
    CANONICAL_15_BENCHMARK_IDS,
    CANONICAL_DIMENSIONS,
    BenchmarkCase,
    DimensionCode,
    DimensionScore,
    DualRunPositionSwapResult,
    JudgeEvaluationResult,
    MarkerChecklist,
    RubricAnchors,
    load_benchmarks,
)
from tests.evaluation.scoring import (
    CANONICAL_CCRS_WEIGHTS,
    DIMENSION_TO_MARKERS,
    MARKER_TO_DIMENSION,
    StatisticalBounds,
    bootstrap_confidence_interval,
    compute_aggregate_metrics,
    compute_bcr,
    compute_ccrs,
    compute_debiased_win_rate,
    compute_dimension_bcr,
    compute_dimension_scores,
    compute_information_density,
    compute_statistical_bounds,
    compute_verbosity_ratio,
    evaluate_contrastive_delta,
    sample_mean,
    sample_sem,
    sample_std,
)


# ---------------------------------------------------------------------------
# Test 1: BenchmarkCase ID Pattern and Prefix-Dimension Mismatch
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_01_benchmark_case_id_pattern_and_prefix_mismatch():
    """Verify BenchmarkCase rejects non-canonical ID regexes and prefix-dimension mismatches."""
    valid_rubric = {"1": "Anchor 1", "3": "Anchor 3", "5": "Anchor 5"}
    long_prompt = "A" * 150

    # 1. Non-canonical regex patterns
    invalid_ids = ["TC-CR-1", "TC-CR-001", "TC-XX-01", "tc-cr-01", "TC-CR-01-A", ""]
    for bad_id in invalid_ids:
        with pytest.raises(ValueError):
            BenchmarkCase(
                id=bad_id,
                dimension="CR",
                prompt=long_prompt,
                rubric=valid_rubric,
            )

    # 2. Prefix-dimension mismatch
    with pytest.raises(ValueError, match="does not match dimension"):
        BenchmarkCase(
            id="TC-CR-01",
            dimension="SA",
            prompt=long_prompt,
            rubric=valid_rubric,
        )

    # 3. Canonical valid instantiation
    case = BenchmarkCase(
        id="TC-CR-01",
        dimension="CR",
        prompt=long_prompt,
        rubric=valid_rubric,
    )
    assert case.id == "TC-CR-01"
    assert case.dimension == "CR"


# ---------------------------------------------------------------------------
# Test 2: CR Prompt Length Boundary Stress (99, 100, 101)
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_02_cr_prompt_length_boundary_stress():
    """Stress-test off-by-one prompt length boundary for CR benchmarks (> 100 characters)."""
    valid_rubric = {"1": "Poor", "3": "Moderate", "5": "Excellent"}

    # 99 chars: MUST fail
    prompt_99 = "x" * 99
    with pytest.raises(ValueError, match="must exceed 100 chars"):
        BenchmarkCase(id="TC-CR-01", dimension="CR", prompt=prompt_99, rubric=valid_rubric)

    # 100 chars: MUST fail (len <= 100)
    prompt_100 = "x" * 100
    with pytest.raises(ValueError, match="must exceed 100 chars"):
        BenchmarkCase(id="TC-CR-01", dimension="CR", prompt=prompt_100, rubric=valid_rubric)

    # 101 chars: MUST pass
    prompt_101 = "x" * 101
    case = BenchmarkCase(id="TC-CR-01", dimension="CR", prompt=prompt_101, rubric=valid_rubric)
    assert len(case.prompt) == 101

    # Non-CR dimensions do not enforce > 100 char limit
    case_pd = BenchmarkCase(id="TC-PD-01", dimension="PD", prompt="Short prompt", rubric=valid_rubric)
    assert case_pd.id == "TC-PD-01"


# ---------------------------------------------------------------------------
# Test 3: Rubric Anchors Malformed Inputs and Whitespace Rejection
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_03_rubric_anchors_malformed_and_whitespace():
    """Verify RubricAnchors rejects non-dicts, whitespace strings, and missing scores."""
    # Non-dict inputs
    for non_dict in ["not a dict", [1, 3, 5], None, 42]:
        with pytest.raises(TypeError):
            RubricAnchors.from_dict(non_dict)  # type: ignore

    # Whitespace-only anchor
    with pytest.raises(ValueError, match="Missing score 1 anchor"):
        RubricAnchors.from_dict({"1": "   \n\t  ", "3": "Valid", "5": "Valid"})

    # Missing anchor
    with pytest.raises(ValueError, match="Missing score 3 anchor"):
        RubricAnchors.from_dict({"1": "Valid", "5": "Valid"})

    # Dual format conversion
    anchors = RubricAnchors(score_1="Base", score_3="Mid", score_5="High")
    dict_repr = anchors.to_dict(dual_format=True)
    assert dict_repr["1"] == "Base"
    assert dict_repr["score_1"] == "Base"
    assert dict_repr["3"] == "Mid"
    assert dict_repr["score_3"] == "Mid"
    assert dict_repr["5"] == "High"
    assert dict_repr["score_5"] == "High"


# ---------------------------------------------------------------------------
# Test 4: DimensionScore NaN, Inf, and Boolean Rejection
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_04_dimension_score_nan_inf_bool_rejection():
    """Verify DimensionScore strictly rejects booleans, NaN, Inf, and out-of-range floats."""
    # Boolean rejection
    with pytest.raises(TypeError, match="must be numeric"):
        DimensionScore(CR=True, PD=3.0, SA=3.0, EP=3.0, EH=3.0)

    # NaN rejection
    with pytest.raises(TypeError, match="must be numeric"):
        DimensionScore(CR=float("nan"), PD=3.0, SA=3.0, EP=3.0, EH=3.0)

    # Out of bounds: 0.999
    with pytest.raises(ValueError, match="out of canonical range"):
        DimensionScore(CR=0.999, PD=3.0, SA=3.0, EP=3.0, EH=3.0)

    # Out of bounds: 5.001
    with pytest.raises(ValueError, match="out of canonical range"):
        DimensionScore(CR=5.001, PD=3.0, SA=3.0, EP=3.0, EH=3.0)

    # Valid boundary floats: exactly 1.0 and 5.0
    valid_score = DimensionScore(CR=1.0, PD=5.0, SA=3.0, EP=2.5, EH=4.5)
    assert valid_score.CR == 1.0
    assert valid_score.PD == 5.0


# ---------------------------------------------------------------------------
# Test 5: MarkerChecklist Strict Typing, Integer Set, and Count Invariants
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_05_marker_checklist_strict_typing_and_count():
    """Verify MarkerChecklist enforces exact 12-marker domain, int in {0, 1}, and rejects booleans."""
    valid_markers = {f"M{i:02d}": 1 for i in range(1, 13)}

    # Boolean value in marker
    bad_bool_markers = dict(valid_markers)
    bad_bool_markers["M01"] = True  # type: ignore
    with pytest.raises(ValueError, match="must be 0 or 1"):
        MarkerChecklist(markers=bad_bool_markers)

    # Out-of-range integer value: 2
    bad_val_markers = dict(valid_markers)
    bad_val_markers["M02"] = 2
    with pytest.raises(ValueError, match="must be 0 or 1"):
        MarkerChecklist(markers=bad_val_markers)

    # Count mismatch: 11 markers
    missing_one = {f"M{i:02d}": 1 for i in range(1, 12)}
    with pytest.raises(ValueError, match="Expected exactly 12 markers"):
        MarkerChecklist(markers=missing_one)

    # Default constructor initializes all 12 markers to 0
    default_checklist = MarkerChecklist()
    assert len(default_checklist.markers) == 12
    assert all(v == 0 for v in default_checklist.markers.values())


# ---------------------------------------------------------------------------
# Test 6: load_benchmarks Corrupted JSONL Lines, Whitespace, and Duplicates
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_06_load_benchmarks_corrupted_jsonl_and_duplicates(tmp_path: Path):
    """Verify load_benchmarks catches JSON syntax errors, duplicates, and skips empty lines."""
    # 1. File with corrupted JSON on line 2
    corrupt_file = tmp_path / "corrupt.jsonl"
    corrupt_file.write_text(
        '{"id": "TC-CR-01", "dimension": "CR", "prompt": "' + ("A" * 120) + '", "rubric": {"1": "A", "3": "B", "5": "C"}}\n'
        'NOT_A_VALID_JSON_OBJECT\n'
    )
    with pytest.raises(ValueError, match="Invalid JSON at line 2"):
        load_benchmarks(corrupt_file)

    # 2. File with duplicate benchmark ID
    dup_file = tmp_path / "dup.jsonl"
    item_str = json.dumps({
        "id": "TC-PD-01", "dimension": "PD", "prompt": "Prompt text", "rubric": {"1": "A", "3": "B", "5": "C"}
    })
    dup_file.write_text(f"{item_str}\n\n   \n{item_str}\n")
    with pytest.raises(ValueError, match="Duplicate benchmark ID detected: 'TC-PD-01'"):
        load_benchmarks(dup_file)

    # 3. File with valid cases interspersed with empty and whitespace lines
    clean_file = tmp_path / "clean.jsonl"
    item1 = json.dumps({"id": "TC-PD-01", "dimension": "PD", "prompt": "P1", "rubric": {"1": "A", "3": "B", "5": "C"}})
    item2 = json.dumps({"id": "TC-PD-02", "dimension": "PD", "prompt": "P2", "rubric": {"1": "A", "3": "B", "5": "C"}})
    clean_file.write_text(f"\n   \n{item1}\n\n\t\n{item2}\n\n")
    cases = load_benchmarks(clean_file)
    assert len(cases) == 2
    assert cases[0].id == "TC-PD-01"
    assert cases[1].id == "TC-PD-02"


# ---------------------------------------------------------------------------
# Test 7: Canonical CCRS Weights Immutability and Mathematical Attribution
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_07_canonical_weights_immutability_and_attribution():
    """Verify CANONICAL_CCRS_WEIGHTS is immutable and matches exact mathematical specifications."""
    # Immutability check (MappingProxyType)
    assert isinstance(CANONICAL_CCRS_WEIGHTS, MappingProxyType)
    with pytest.raises(TypeError):
        CANONICAL_CCRS_WEIGHTS["CR"] = 0.50  # type: ignore

    # Sum of weights must equal 1.00 exactly
    total_weight = sum(CANONICAL_CCRS_WEIGHTS.values())
    assert math.isclose(total_weight, 1.0, abs_tol=1e-9)

    # Exact weights attribution per dimension
    expected_weights = {
        "CR": 0.20,
        "PD": 0.20,
        "SA": 0.25,
        "EP": 0.20,
        "EH": 0.15,
    }
    assert dict(CANONICAL_CCRS_WEIGHTS) == expected_weights


# ---------------------------------------------------------------------------
# Test 8: CCRS Boundary Extremes, Floating Point Precision, and Type Safety
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_08_ccrs_boundary_extremes_and_type_safety():
    """Verify compute_ccrs behavior across [1.0, 5.0] extremes, float precision, and invalid types."""
    # Floor: all 1.0 -> 0.0%
    assert compute_ccrs({"CR": 1.0, "PD": 1.0, "SA": 1.0, "EP": 1.0, "EH": 1.0}) == 0.0

    # Ceiling: all 5.0 -> 100.0%
    assert compute_ccrs({"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0}) == 100.0

    # Midpoint: all 3.0 -> 50.0%
    assert compute_ccrs({"CR": 3.0, "PD": 3.0, "SA": 3.0, "EP": 3.0, "EH": 3.0}) == 50.0

    # Boolean score rejection
    with pytest.raises(TypeError, match="must be numeric"):
        compute_ccrs({"CR": True, "PD": 3.0, "SA": 3.0, "EP": 3.0, "EH": 3.0})  # type: ignore

    # NaN score rejection
    with pytest.raises(TypeError, match="must be numeric"):
        compute_ccrs({"CR": float("nan"), "PD": 3.0, "SA": 3.0, "EP": 3.0, "EH": 3.0})

    # Missing dimension
    with pytest.raises(ValueError, match="Missing dimension"):
        compute_ccrs({"CR": 3.0, "PD": 3.0, "SA": 3.0, "EP": 3.0})

    # Sub-epsilon boundary precision: 1.000000000001 must not trigger negative CCRS
    sub_eps_score = compute_ccrs({"CR": 1.000000000001, "PD": 1.0, "SA": 1.0, "EP": 1.0, "EH": 1.0})
    assert 0.0 <= sub_eps_score <= 100.0


# ---------------------------------------------------------------------------
# Test 9: BCR Strict Contract, Dimension Slicing, and Type Validation
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_09_bcr_strict_contract_and_dimension_slicing():
    """Verify compute_bcr and compute_dimension_bcr mathematical correctness and contracts."""
    # All 0s -> 0.0%
    zeros = {f"M{i:02d}": 0 for i in range(1, 13)}
    assert compute_bcr(zeros) == 0.0

    # All 1s -> 100.0%
    ones = {f"M{i:02d}": 1 for i in range(1, 13)}
    assert compute_bcr(ones) == 100.0

    # 6 ones, 6 zeros -> 50.0%
    half = {f"M{i:02d}": (1 if i <= 6 else 0) for i in range(1, 13)}
    assert compute_bcr(half) == 50.0

    # Invalid length
    with pytest.raises(ValueError, match="Expected 12 markers"):
        compute_bcr({f"M{i:02d}": 1 for i in range(1, 11)})

    # Dimension slicing
    # SA has 3 markers: M05, M06, M07. If M05=1, M06=1, M07=0 -> 2/3 * 100 = 66.6667%
    sa_slice_bcr = compute_dimension_bcr(half, "SA")
    assert sa_slice_bcr == 66.6667

    # Unknown dimension slicing
    with pytest.raises(ValueError, match="Unknown dimension"):
        compute_dimension_bcr(half, "UNKNOWN_DIM")


# ---------------------------------------------------------------------------
# Test 10: Information Density Singularity Protection (T <= 1)
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_10_information_density_singularity_protection():
    """Verify compute_information_density returns 0.0 for T <= 1 (log2(0) and log2(1) guards)."""
    # Token count 0: log2(0) is -inf -> guarded to 0.0
    assert compute_information_density(100.0, 0) == 0.0

    # Token count 1: log2(1) is 0 -> division by zero guarded to 0.0
    assert compute_information_density(100.0, 1) == 0.0

    # Negative tokens -> guarded to 0.0
    assert compute_information_density(100.0, -100) == 0.0

    # Token count 2: log2(2) == 1.0 -> IDS == CCRS
    assert compute_information_density(75.5, 2) == 75.5

    # Token count 1024: log2(1024) == 10.0 -> IDS == CCRS / 10.0
    assert compute_information_density(80.0, 1024) == 8.0

    # CCRS == 0.0
    assert compute_information_density(0.0, 500) == 0.0


# ---------------------------------------------------------------------------
# Test 11: Statistical Bounds and Bootstrap Invariants (N=0, N=1, Identical)
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_11_statistical_bounds_and_bootstrap_invariants():
    """Verify statistical moments and bootstrap confidence interval edge cases."""
    # N = 0: Empty sequence
    ci_empty = bootstrap_confidence_interval([])
    assert ci_empty == (0.0, 0.0)
    bounds_empty = compute_statistical_bounds([])
    assert bounds_empty.count == 0
    assert bounds_empty.mean == 0.0
    assert bounds_empty.sem == 0.0

    # N = 1: Single observation
    ci_single = bootstrap_confidence_interval([88.5])
    assert ci_single == (88.5, 88.5)
    bounds_single = compute_statistical_bounds([88.5])
    assert bounds_single.count == 1
    assert bounds_single.mean == 88.5
    assert bounds_single.std == 0.0
    assert bounds_single.sem == 0.0

    # Identical observations: std must be 0.0, CI must collapse to the point value
    identical_data = [42.0, 42.0, 42.0, 42.0, 42.0]
    ci_ident = bootstrap_confidence_interval(identical_data, seed=42)
    assert ci_ident == (42.0, 42.0)
    bounds_ident = compute_statistical_bounds(identical_data)
    assert bounds_ident.std == 0.0
    assert bounds_ident.ci_lower == 42.0
    assert bounds_ident.ci_upper == 42.0

    # Invariant: CI Lower <= Mean <= CI Upper
    data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    bounds = compute_statistical_bounds(data, seed=42)
    assert bounds.ci_lower <= bounds.mean <= bounds.ci_upper


# ---------------------------------------------------------------------------
# Test 12: Judge JSON Markdown Fence, Preamble Extraction, and Trailing Comma Repair
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_12_judge_json_markdown_fence_and_preamble_extraction():
    """Verify parse_judge_json extracts JSON from markdown blocks and auto-repairs trailing commas."""
    raw_response = """
    Certainly! Here is my detailed technical evaluation:

    ```json
    {
      "scores": {
        "response_a": {"CR": 4.5, "PD": 4.0, "SA": 4.5, "EP": 4.0, "EH": 4.5,},
        "response_b": {"CR": 2.0, "PD": 2.0, "SA": 2.0, "EP": 2.0, "EH": 2.0,},
      },
      "behavioral_checklist": {
        "response_a": {"M01": 1, "M02": 1, "M03": 1, "M04": 1, "M05": 1, "M06": 1, "M07": 1, "M08": 1, "M09": 1, "M10": 1, "M11": 1, "M12": 1,},
        "response_b": {"M01": 0, "M02": 0, "M03": 0, "M04": 0, "M05": 0, "M06": 0, "M07": 0, "M08": 0, "M09": 0, "M10": 0, "M11": 0, "M12": 0,},
      },
      "pairwise_preference": "A_better",
      "justification": "Response A demonstrated comprehensive architectural blueprinting and verification commands.",
    }
    ```

    Please let me know if you need any further analysis.
    """
    parsed = parse_judge_json(raw_response)
    assert parsed["pairwise_preference"] == "A_better"
    assert parsed["scores"]["response_a"]["CR"] == 4.5
    assert parsed["scores"]["response_b"]["CR"] == 2.0
    assert parsed["behavioral_checklist"]["response_a"]["M01"] == 1
    assert parsed["behavioral_checklist"]["response_b"]["M12"] == 0
    assert "Response A demonstrated" in parsed["justification"]


# ---------------------------------------------------------------------------
# Test 13: Judge JSON Score Clamping, Dimension Aliasing, and Fallback Resilience
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_13_judge_json_score_clamping_and_fallback_resilience():
    """Verify parse_judge_json clamps extreme scores, maps dimension aliases, and defaults safely."""
    raw = {
        "scores": {
            "response_a": {
                "complex_reasoning": 99.0,  # Clamped to 5.0
                "pd": -10.0,                # Clamped to 1.0
                "solution architecture": "bad_type",  # Defaults to 3.0
                "ep": 4.2,
                "eh": 3.8,
            },
            # response_b omitted entirely -> should default to 3.0 for all dimensions
        },
        "behavioral_checklist": {
            # response_a and response_b omitted -> default to 0 for all markers
        },
        "pairwise_preference": "INVALID_PREFERENCE",  # Should fall back to 'tie'
        "justification": None,                        # Should fall back to standard justification
    }

    parsed = parse_judge_json(json.dumps(raw))
    # Score clamping and alias resolution
    assert parsed["scores"]["response_a"]["CR"] == 5.0
    assert parsed["scores"]["response_a"]["PD"] == 1.0
    assert parsed["scores"]["response_a"]["SA"] == 3.0
    assert parsed["scores"]["response_a"]["EP"] == 4.2
    assert parsed["scores"]["response_a"]["EH"] == 3.8

    # Missing response_b defaulted
    assert parsed["scores"]["response_b"]["CR"] == 3.0

    # Behavioral checklist defaulted
    assert parsed["behavioral_checklist"]["response_a"]["M01"] == 0
    assert parsed["behavioral_checklist"]["response_b"]["M12"] == 0

    # Fallbacks
    assert parsed["pairwise_preference"] == "tie"
    assert isinstance(parsed["justification"], str) and len(parsed["justification"]) > 0


# ---------------------------------------------------------------------------
# Test 14: Dual-Run Position-Swap Bias Detection Engine Symmetry
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_14_dual_run_position_swap_bias_detection_engine():
    """Verify position swap win rate calculation and detection of position bias vs merit wins."""
    # Merit win for Candidate B (Pass 1: B wins, Pass 2: A wins because target is swapped to A)
    win_rate_merit = compute_position_swap_win_rate(pass1_pref="B_better", pass2_pref="A_better", target="B")
    assert win_rate_merit == 1.0

    # Merit win for Candidate A
    win_rate_base = compute_position_swap_win_rate(pass1_pref="A_better", pass2_pref="B_better", target="B")
    assert win_rate_base == 0.0

    # Pure Position Bias: First position (A) always preferred regardless of candidate
    win_rate_pos_a = compute_position_swap_win_rate(pass1_pref="A_better", pass2_pref="A_better", target="B")
    assert win_rate_pos_a == 0.5

    # Pure Position Bias: Second position (B) always preferred regardless of candidate
    win_rate_pos_b = compute_position_swap_win_rate(pass1_pref="B_better", pass2_pref="B_better", target="B")
    assert win_rate_pos_b == 0.5

    # Dual ties
    win_rate_tie = compute_position_swap_win_rate(pass1_pref="tie", pass2_pref="tie", target="B")
    assert win_rate_tie == 0.5


# ---------------------------------------------------------------------------
# Test 15: Runner CLI Error Exit Codes and Parent Directory Auto-Creation
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_15_runner_cli_error_codes_and_directory_autocreation(tmp_path: Path):
    """Verify run_evaluation exits with code 1 on missing file and creates target directories."""
    # 1. Non-existent benchmark file -> exit code 1
    missing_benchmarks = str(tmp_path / "does_not_exist.jsonl")
    exit_code_missing = run_evaluation(benchmarks_path=missing_benchmarks)
    assert exit_code_missing == 1

    # 2. Valid benchmark file with deeply nested output path
    valid_benchmark_file = tmp_path / "test_benches.jsonl"
    item = json.dumps({
        "id": "TC-CR-01",
        "dimension": "CR",
        "prompt": "Explain Raft consensus partitioned state machine replication safety constraints." * 3,
        "rubric": {"1": "Bad", "3": "Fair", "5": "Good"},
    })
    valid_benchmark_file.write_text(item + "\n")

    nested_output = tmp_path / "deeply" / "nested" / "results" / "eval.json"
    assert not nested_output.parent.exists()

    exit_code = run_evaluation(
        benchmarks_path=str(valid_benchmark_file),
        output_path=str(nested_output),
        limit=1,
    )
    assert exit_code == 0
    assert nested_output.exists()
    data = json.loads(nested_output.read_text())
    assert data["metadata"]["benchmarks_evaluated"] == 1


# ---------------------------------------------------------------------------
# Test 16: Runner Token Count Estimation Boundary Cases
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_16_runner_estimate_token_count_edge_cases():
    """Verify estimate_token_count guards against 0 tokens on empty/whitespace inputs."""
    # Empty string
    assert estimate_token_count("") == 1

    # Whitespace only
    assert estimate_token_count("   \n\t\r  ") == 1

    # Single word
    assert estimate_token_count("hello") >= 1

    # Unicode & Emoji strings
    emoji_str = "🚀 🔥 💡 Architecture & Systems Engineering"
    assert estimate_token_count(emoji_str) >= 1

    # Large synthetic text (10,000 words)
    large_text = "word " * 10000
    assert estimate_token_count(large_text) == 13300


# ---------------------------------------------------------------------------
# Test 17: Contrastive Delta Evaluation and Length Mismatch Guard
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_17_contrastive_delta_evaluation_and_length_mismatch():
    """Verify evaluate_contrastive_delta requires equal non-empty sequences and computes deltas."""
    # Empty sequences
    with pytest.raises(ValueError, match="Cannot evaluate delta on empty results"):
        evaluate_contrastive_delta([], [])

    item1 = {
        "scores": {"CR": 2.0, "PD": 2.0, "SA": 2.0, "EP": 2.0, "EH": 2.0},
        "behavioral_checklist": {f"M{i:02d}": 0 for i in range(1, 13)},
        "token_count": 100,
    }
    item2 = {
        "scores": {"CR": 4.0, "PD": 4.0, "SA": 4.0, "EP": 4.0, "EH": 4.0},
        "behavioral_checklist": {f"M{i:02d}": 1 for i in range(1, 13)},
        "token_count": 200,
    }

    # Length mismatch
    with pytest.raises(ValueError, match="must have identical lengths"):
        evaluate_contrastive_delta([item1, item1], [item2])

    # Paired delta calculation
    deltas = evaluate_contrastive_delta([item1], [item2])
    assert deltas["count"] == 1
    # Base CCRS: (2 - 1)/4 * 100 = 25.0%. Skill CCRS: (4 - 1)/4 * 100 = 75.0%. Delta = +50.0%
    assert deltas["delta_ccrs"]["mean"] == 50.0
    # Base BCR: 0.0%. Skill BCR: 100.0%. Delta = +100.0%
    assert deltas["delta_bcr"]["mean"] == 100.0
    # Verbosity ratio: 200 / 100 = 2.0
    assert deltas["verbosity_ratio"] == 2.0


# ---------------------------------------------------------------------------
# Test 18: Scratchpad Parser Malformed XML, Inverted Tags, and Missing Phases
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_18_scratchpad_parser_adversarial_malformed_xml():
    """Verify scratchpad parser catches missing tags, inverted order, and out-of-order phases."""
    from tests.e2e.conftest import parse_claude_thinking_scratchpad

    # 1. Missing opening tag
    res1 = parse_claude_thinking_scratchpad("Content without opening </claude_thinking>")
    assert not res1["has_tag"]
    assert any("Missing <claude_thinking>" in e for e in res1["errors"])

    # 2. Missing closing tag
    res2 = parse_claude_thinking_scratchpad("<claude_thinking> Unclosed scratchpad...")
    assert res2["has_tag"]
    assert not res2["is_closed"]
    assert any("Missing </claude_thinking>" in e for e in res2["errors"])

    # 3. Missing Phase 3
    incomplete_phases = """
    <claude_thinking>
    PHASE 1: Constraint Anchoring
    PHASE 2: Hypothesis Exploration & Counter-Factual Stress Testing
    PHASE 4: Output Calibration
    </claude_thinking>
    """
    res3 = parse_claude_thinking_scratchpad(incomplete_phases)
    assert any("PHASE 3" in e for e in res3["errors"])

    # 4. Out-of-order phases (Phase 4 before Phase 1)
    inverted_phases = """
    <claude_thinking>
    PHASE 4: Output Calibration
    PHASE 1: Constraint Anchoring
    PHASE 2: Hypothesis Exploration
    PHASE 3: Architectural Blueprinting
    </claude_thinking>
    """
    res4 = parse_claude_thinking_scratchpad(inverted_phases)
    assert any("Out-of-order" in e for e in res4["errors"])

    # 5. Clean, fully compliant scratchpad
    clean_thinking = """
    <claude_thinking>
    PHASE 1: Constraint Anchoring
    PHASE 2: Hypothesis Exploration
    PHASE 3: Architectural Blueprinting
    PHASE 4: Output Calibration
    </claude_thinking>
    """
    res5 = parse_claude_thinking_scratchpad(clean_thinking)
    assert res5["has_tag"]
    assert res5["is_closed"]
    assert len(res5["phases_found"]) == 4
    assert len(res5["errors"]) == 0


# ---------------------------------------------------------------------------
# Test 19: Skill Frontmatter Adversarial Command Injections and Type Safety
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_19_skill_frontmatter_adversarial_injections_and_types():
    """Verify validate_skill_metadata catches shell command injection and schema violations."""
    from tests.e2e.conftest import validate_skill_metadata

    # 1. Command injection in skill name
    bad_name = {"name": "claude; rm -rf /", "description": "Valid description text for the skill"}
    errors1 = validate_skill_metadata(bad_name)
    assert any("violates regex" in e for e in errors1)

    # 2. Skill name exceeding 64 characters
    long_name = {"name": "a" * 65, "description": "Valid description text for the skill"}
    errors2 = validate_skill_metadata(long_name)
    assert any("violates regex" in e for e in errors2)

    # 3. Missing or trivial description
    short_desc = {"name": "claude", "description": "tiny"}
    errors3 = validate_skill_metadata(short_desc)
    assert any("substantive description" in e for e in errors3)

    # 4. Non-boolean invocation flags
    bad_flags = {"name": "claude", "description": "Valid description text", "disable-slash-command": "false"}
    errors4 = validate_skill_metadata(bad_flags)
    assert any("must be a boolean" in e for e in errors4)

    # 5. Clean frontmatter
    clean = {
        "name": "claude",
        "description": "Enables any model to emulate Claude's latest cognitive reasoning patterns.",
        "disable-slash-command": False,
        "disable-model-invocation": False,
    }
    assert len(validate_skill_metadata(clean)) == 0


# ---------------------------------------------------------------------------
# Test 20: Exemplar Python Code Block AST Audit
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_20_exemplar_python_code_block_ast_audit(project_root: Path):
    """Verify all Python code snippets in skills/claude/examples/*.md parse cleanly via AST."""
    examples_dir = project_root / "skills" / "claude" / "examples"
    assert examples_dir.is_dir()

    md_files = list(examples_dir.glob("*.md"))
    assert len(md_files) >= 3

    total_code_blocks = 0
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        # Extract python code blocks: ```python ... ```
        py_blocks = re.findall(r"```python\s*\n(.*?)\n```", content, re.DOTALL)
        for idx, block in enumerate(py_blocks, start=1):
            total_code_blocks += 1
            try:
                ast.parse(block)
            except SyntaxError as e:
                pytest.fail(f"SyntaxError in {md_file.name} python block {idx}: {e}")

    assert total_code_blocks >= 2, f"Expected at least 2 python code blocks across exemplars, found {total_code_blocks}"


# ---------------------------------------------------------------------------
# Test 21: Behavioral Checklist JSON Integrity and Rubric Dimension Alignment
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_21_behavioral_checklist_integrity_and_rubric_anchors(project_root: Path):
    """Verify behavioral_checklist.json schema and alignment with canonical dimensions and markers."""
    checklist_path = project_root / "skills" / "claude" / "resources" / "behavioral_checklist.json"
    assert checklist_path.is_file()

    data = json.loads(checklist_path.read_text(encoding="utf-8"))
    markers = data.get("markers", [])
    assert len(markers) == 12

    seen_ids = set()
    for m in markers:
        m_id = m["id"]
        assert m_id in CANONICAL_12_MARKERS
        seen_ids.add(m_id)
        assert m["dimension"] in CANONICAL_DIMENSIONS
        assert isinstance(m["name"], str) and len(m["name"]) > 0
        assert math.isclose(m["weight"], 1.0 / 12.0, abs_tol=1e-3)

    assert len(seen_ids) == 12


# ---------------------------------------------------------------------------
# Test 22: End-to-End Evaluation Runner Results Schema Conformance
# ---------------------------------------------------------------------------

@pytest.mark.tier5
@pytest.mark.m5
def test_t5_adv_22_runner_results_schema_conformance(project_root: Path, tmp_path: Path):
    """Verify EvaluationRunner generates fully compliant results schema with all required keys."""
    benchmarks_path = project_root / "tests" / "evaluation" / "benchmarks.jsonl"
    output_path = tmp_path / "runner_test_output.json"

    runner = EvaluationRunner(
        benchmarks_path=benchmarks_path,
        output_path=output_path,
        mock_mode=True,
        limit=2,
    )
    payload = runner.run()

    # Validate top-level schema
    assert "metadata" in payload
    assert "summary_metrics" in payload
    assert "benchmark_results" in payload

    # Validate metadata
    assert payload["metadata"]["benchmarks_evaluated"] == 2
    assert payload["metadata"]["mock_mode"] is True

    # Validate summary metrics
    summary = payload["summary_metrics"]
    for key in ["overall_skill_win_rate", "mean_ccrs_baseline", "mean_ccrs_skill", "delta_ccrs", "mean_bcr_baseline", "mean_bcr_skill", "delta_bcr"]:
        assert key in summary
        assert isinstance(summary[key], (int, float))

    # Validate case records
    cases = payload["benchmark_results"]
    assert len(cases) == 2
    for c in cases:
        assert "id" in c
        assert "dimension" in c
        assert "outputs" in c
        assert "baseline" in c["outputs"]
        assert "skill" in c["outputs"]
        assert "evaluation" in c
        ev = c["evaluation"]
        assert "skill_win_rate" in ev
        assert "baseline_ccrs" in ev
        assert "skill_ccrs" in ev
        assert "delta_ccrs" in ev
        assert "position_bias_detected" in ev
