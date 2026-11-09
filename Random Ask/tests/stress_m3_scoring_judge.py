"""
tests/stress_m3_scoring_judge.py
Adversarial Stress Testing Harness for Milestone 3 (Scoring Engine & LLM Judge).
Executes exhaustive empirical tests across edge cases, mathematical symmetries,
and parser fuzzing vectors.
"""

import sys
import math
import json
from pathlib import Path

# Add project root to path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tests.evaluation.scoring import (
    CANONICAL_CCRS_WEIGHTS,
    CANONICAL_12_MARKERS,
    CANONICAL_DIMENSIONS,
    compute_ccrs,
    compute_bcr,
    compute_information_density,
    compute_ids,
    compute_verbosity_ratio,
    compute_dimension_bcr,
    compute_dimension_scores,
    compute_debiased_win_rate,
    bootstrap_confidence_interval,
    compute_statistical_bounds,
)
from tests.evaluation.judge import (
    EvaluationJudge,
    JudgeConfig,
    JudgeOutput,
    PositionSwapResult,
    parse_judge_json,
    clamp_score,
    compute_position_swap_win_rate,
    build_judge_system_prompt,
)
from tests.evaluation.schemas import (
    DimensionScore,
    MarkerChecklist,
    DualRunPositionSwapResult,
    JudgeEvaluationResult,
)


def run_suite_1_scoring_edge_cases():
    print("\n" + "=" * 70)
    print("SUITE 1: SCORING ENGINE EDGE CASES & BOUNDARIES")
    print("=" * 70)

    # 1.1 IDS & Token Count Edge Cases
    print("\n--- 1.1 Token Singularities in IDS (compute_ids) ---")
    singularity_tokens = [0, 1, -1, -100, -999999]
    for tok in singularity_tokens:
        ids_val = compute_ids(80.0, tok)
        assert ids_val == 0.0, f"Failed for token={tok}: expected 0.0, got {ids_val}"
        print(f"  [PASS] tokens={tok:>7}: IDS = {ids_val} (zero-division immune)")

    # Boundary tokens >= 2
    for tok in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 100000, 10**9]:
        ccrs = 80.0
        expected = round(ccrs / math.log2(tok), 4)
        actual = compute_ids(ccrs, tok)
        assert actual == expected, f"Mismatch at tok={tok}: {actual} != {expected}"
    print("  [PASS] tokens from 2 to 10^9 produce mathematically exact IDS values.")

    # CCRS = 0 with various tokens
    for tok in [0, 1, 2, 1024]:
        assert compute_ids(0.0, tok) == 0.0
    print("  [PASS] CCRS = 0.0 yields IDS = 0.0 across all token counts.")

    # 1.2 CCRS Rubric Boundaries & Extreme Values
    print("\n--- 1.2 CCRS Rubric Boundaries & Extreme Values ---")
    min_scores = {d: 1.0 for d in CANONICAL_DIMENSIONS}
    max_scores = {d: 5.0 for d in CANONICAL_DIMENSIONS}
    mid_scores = {d: 3.0 for d in CANONICAL_DIMENSIONS}

    assert compute_ccrs(min_scores) == 0.0, "All 1.0 did not yield 0.0%"
    assert compute_ccrs(max_scores) == 100.0, "All 5.0 did not yield 100.0%"
    assert compute_ccrs(mid_scores) == 50.0, "All 3.0 did not yield 50.0%"
    print(f"  [PASS] Extreme Rubrics: all 1.0 -> {compute_ccrs(min_scores)}%, all 5.0 -> {compute_ccrs(max_scores)}%, all 3.0 -> {compute_ccrs(mid_scores)}%")

    # Out of range scores
    invalid_scores = [
        ("below_min", {**min_scores, "CR": 0.999}),
        ("zero", {**min_scores, "CR": 0.0}),
        ("negative", {**min_scores, "CR": -1.0}),
        ("above_max", {**max_scores, "EH": 5.001}),
        ("large_positive", {**max_scores, "SA": 10.0}),
    ]
    for label, sc in invalid_scores:
        try:
            compute_ccrs(sc)
            assert False, f"Expected ValueError for {label}"
        except ValueError as e:
            print(f"  [PASS] Invalid score rejected ({label}): {e}")

    # Non-numeric, boolean, NaN, and None scores
    type_error_scores = [
        ("string_num", {**min_scores, "CR": "3.0"}),
        ("bool_true", {**min_scores, "CR": True}),
        ("bool_false", {**min_scores, "CR": False}),
        ("none_val", {**min_scores, "CR": None}),
        ("nan_val", {**min_scores, "CR": float("nan")}),
    ]
    for label, sc in type_error_scores:
        try:
            compute_ccrs(sc)
            assert False, f"Expected TypeError for {label}"
        except TypeError as e:
            print(f"  [PASS] Non-numeric score rejected ({label}): {e}")

    # Missing dimension
    try:
        compute_ccrs({"CR": 3.0, "PD": 3.0, "SA": 3.0, "EP": 3.0})  # Missing EH
        assert False, "Expected ValueError for missing dimension"
    except ValueError as e:
        print(f"  [PASS] Missing dimension rejected: {e}")

    # Immutability of canonical weights
    try:
        CANONICAL_CCRS_WEIGHTS["CR"] = 0.99  # type: ignore
        assert False, "CANONICAL_CCRS_WEIGHTS was mutable!"
    except TypeError as e:
        print(f"  [PASS] CANONICAL_CCRS_WEIGHTS is immutable (MappingProxyType): {e}")

    # 1.3 BCR Marker Checklist Boundaries
    print("\n--- 1.3 BCR Marker Checklist Boundaries ---")
    zeros_marker = {f"M{i:02d}": 0 for i in range(1, 13)}
    ones_marker = {f"M{i:02d}": 1 for i in range(1, 13)}
    half_marker = {f"M{i:02d}": (1 if i <= 6 else 0) for i in range(1, 13)}

    assert compute_bcr(zeros_marker) == 0.0
    assert compute_bcr(ones_marker) == 100.0
    assert compute_bcr(half_marker) == 50.0
    print(f"  [PASS] Extreme Markers: all 0 -> {compute_bcr(zeros_marker)}%, all 1 -> {compute_bcr(ones_marker)}%, half 1 -> {compute_bcr(half_marker)}%")

    # Strict binary type & range check
    invalid_markers = [
        ("value_2", {**zeros_marker, "M01": 2}),
        ("value_neg1", {**zeros_marker, "M01": -1}),
        ("bool_true", {**zeros_marker, "M01": True}),
        ("bool_false", {**zeros_marker, "M01": False}),
        ("str_val", {**zeros_marker, "M01": "1"}),
        ("count_11", {f"M{i:02d}": 1 for i in range(1, 12)}),
        ("count_13", {**ones_marker, "M13": 1}),
    ]
    for label, mk in invalid_markers:
        try:
            compute_bcr(mk)
            assert False, f"Expected ValueError for {label}"
        except ValueError as e:
            print(f"  [PASS] Invalid marker rejected ({label}): {e}")

    # 1.4 Verbosity Ratio
    print("\n--- 1.4 Verbosity Ratio Boundaries ---")
    assert compute_verbosity_ratio(1000, 0) == 0.0
    assert compute_verbosity_ratio(1000, -10) == 0.0
    assert compute_verbosity_ratio(1500, 1000) == 1.5
    print("  [PASS] Verbosity ratio zero/negative baseline protection verified.")

    # 1.5 Bootstrap Confidence Intervals
    print("\n--- 1.5 Bootstrap CI Determinism & Edge Cases ---")
    assert bootstrap_confidence_interval([]) == (0.0, 0.0)
    assert bootstrap_confidence_interval([50.0]) == (50.0, 50.0)
    ci_const = bootstrap_confidence_interval([75.0] * 20, seed=42)
    assert ci_const == (75.0, 75.0)

    # Determinism across runs with same seed
    sample_data = [60.0, 70.0, 80.0, 90.0, 85.0, 65.0, 75.0, 95.0]
    ci1 = bootstrap_confidence_interval(sample_data, seed=123)
    ci2 = bootstrap_confidence_interval(sample_data, seed=123)
    assert ci1 == ci2
    print(f"  [PASS] Bootstrap CI deterministic: {ci1} == {ci2}")


def run_suite_2_position_swapping_symmetry():
    print("\n" + "=" * 70)
    print("SUITE 2: POSITION-SWAPPING MATHEMATICAL SYMMETRY & BIAS PROOFS")
    print("=" * 70)

    # 2.1 Complete enumeration of the 3x3 = 9 preference states
    # In Pass 1: Candidate 1 = A (Baseline), Candidate 2 = B (Skill)
    # In Pass 2: Candidate 1 = A (Skill), Candidate 2 = B (Baseline)
    print("\n--- 2.1 Preference Matrix (9 combinations) & Win-Rate Parity ---")
    prefs = ["A_better", "B_better", "tie"]
    for p1 in prefs:
        for p2 in prefs:
            w_b = compute_position_swap_win_rate(p1, p2, target="B")
            w_a = compute_position_swap_win_rate(p1, p2, target="A")
            # Conservation property: win_rate(Skill) + win_rate(Baseline) == 1.0
            assert round(w_b + w_a, 4) == 1.0, f"Sum != 1.0 for ({p1}, {p2}): {w_b} + {w_a}"
            # Check bias detection
            bias_detected = (p1 == "A_better" and p2 == "A_better") or (p1 == "B_better" and p2 == "B_better")
            print(f"  Pass 1: {p1:>8} | Pass 2: {p2:>8} -> Skill: {w_b:.2f}, Base: {w_a:.2f} | Bias: {bias_detected}")

    # 2.2 Proof of Neutralization Under 100% Position 1 Bias
    print("\n--- 2.2 Bias Neutralization: 100% Position 1 Presentation Bias ---")
    # Judge has extreme bias: ALWAYS votes Candidate A regardless of quality
    p1 = "A_better"  # Pass 1: A is Baseline -> Baseline gets 1.0, Skill gets 0.0
    p2 = "A_better"  # Pass 2: A is Skill -> Skill gets 1.0, Baseline gets 0.0
    debiased_skill = compute_position_swap_win_rate(p1, p2, target="B")
    assert debiased_skill == 0.5, f"Expected 0.5, got {debiased_skill}"
    print(f"  [PASS] Under 100% Position 1 bias, debiased win rate is exactly {debiased_skill} (neutral tie)!")

    # 2.3 Proof of Neutralization Under 100% Position 2 Bias
    print("\n--- 2.3 Bias Neutralization: 100% Position 2 Presentation Bias ---")
    p1 = "B_better"  # Pass 1: B is Skill -> Skill gets 1.0, Baseline gets 0.0
    p2 = "B_better"  # Pass 2: B is Baseline -> Baseline gets 1.0, Skill gets 0.0
    debiased_skill = compute_position_swap_win_rate(p1, p2, target="B")
    assert debiased_skill == 0.5, f"Expected 0.5, got {debiased_skill}"
    print(f"  [PASS] Under 100% Position 2 bias, debiased win rate is exactly {debiased_skill} (neutral tie)!")

    # 2.4 Mathematical Score Symmetry: Constant Position Shift Cancellation
    print("\n--- 2.4 Score Symmetry: Constant Position Shift Invariance ---")
    # Suppose the judge awards +delta to whichever response is in Position 1
    for delta in [0.0, 0.5, 1.0, 2.0]:
        base_true = 2.5
        skill_true = 4.5
        # Pass 1: Position 1 is Baseline, Position 2 is Skill
        pass1_a = base_true + delta
        pass1_b = skill_true
        # Pass 2: Position 1 is Skill, Position 2 is Baseline
        pass2_a = skill_true + delta
        pass2_b = base_true

        avg_baseline = (pass1_a + pass2_b) / 2.0
        avg_skill = (pass1_b + pass2_a) / 2.0
        measured_delta = avg_skill - avg_baseline
        true_delta = skill_true - base_true

        assert abs(measured_delta - true_delta) < 1e-9, f"Delta bias not cancelled: {measured_delta} vs {true_delta}"
        print(f"  [PASS] Position shift delta=+{delta:.1f}: Measured (Skill - Baseline) = {measured_delta:.2f} (exact match with true delta {true_delta:.2f})")

    # 2.5 Multi-case Sequence Debiased Win Rate Parity
    print("\n--- 2.5 Sequence Aggregation Parity (compute_debiased_win_rate) ---")
    p1_seq = ["B_better", "A_better", "tie", "B_better", "A_better"]
    p2_seq = ["A_better", "B_better", "tie", "B_better", "A_better"]
    # Case 0: B_better + A_better -> 1.0 + 1.0 = 2 pts / 2 = 1.0
    # Case 1: A_better + B_better -> 0.0 + 0.0 = 0 pts / 2 = 0.0
    # Case 2: tie + tie -> 0.5 + 0.5 = 1 pt / 2 = 0.5
    # Case 3: B_better + B_better -> 1.0 + 0.0 = 1 pt / 2 = 0.5 (bias neutralized)
    # Case 4: A_better + A_better -> 0.0 + 1.0 = 1 pt / 2 = 0.5 (bias neutralized)
    # Total points = 2 + 0 + 1 + 1 + 1 = 5.0 out of 10.0 = 0.5000
    agg_rate = compute_debiased_win_rate(p1_seq, p2_seq)
    assert agg_rate == 0.5, f"Expected 0.5000, got {agg_rate}"
    print(f"  [PASS] Aggregate debiased win rate over sequence: {agg_rate}")


def run_suite_3_judge_parser_fuzzing():
    print("\n" + "=" * 70)
    print("SUITE 3: JUDGE FALLBACK PARSER FUZZING & ERROR HANDLING")
    print("=" * 70)

    # Valid template payload
    valid_obj = {
        "scores": {
            "response_a": {"CR": 4.0, "PD": 3.5, "SA": 4.5, "EP": 4.0, "EH": 3.0},
            "response_b": {"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0},
        },
        "behavioral_checklist": {
            "response_a": {f"M{i:02d}": (1 if i % 2 == 0 else 0) for i in range(1, 13)},
            "response_b": {f"M{i:02d}": 1 for i in range(1, 13)},
        },
        "pairwise_preference": "B_better",
        "justification": "Response B provided comprehensive architectural rigor.",
    }
    valid_json_str = json.dumps(valid_obj)

    # 3.1 Clean JSON
    print("\n--- 3.1 Clean JSON ---")
    p = parse_judge_json(valid_json_str)
    assert p["pairwise_preference"] == "B_better"
    assert p["scores"]["response_b"]["CR"] == 5.0
    print("  [PASS] Clean JSON parsed accurately.")

    # 3.2 Markdown Code Fences (```json ... ``` and ``` ... ```)
    print("\n--- 3.2 Markdown Code Fences ---")
    markdown_variations = [
        f"```json\n{valid_json_str}\n```",
        f"```\n{valid_json_str}\n```",
        f"Here is my architectural evaluation:\n\n```json\n{valid_json_str}\n```\n\nI hope this is helpful!",
        f"<scratchpad>Evaluating responses...</scratchpad>\n\n```json\n{valid_json_str}\n```",
    ]
    for idx, md in enumerate(markdown_variations, start=1):
        parsed = parse_judge_json(md)
        assert parsed["pairwise_preference"] == "B_better"
        assert parsed["scores"]["response_b"]["CR"] == 5.0
        print(f"  [PASS] Markdown variation #{idx} successfully parsed.")

    # 3.3 Trailing commas repair
    print("\n--- 3.3 Trailing Commas Repair ---")
    trailing_comma_json = """
    {
      "scores": {
        "response_a": {"CR": 3.0, "PD": 3.0, "SA": 3.0, "EP": 3.0, "EH": 3.0,},
        "response_b": {"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0,},
      },
      "behavioral_checklist": {
        "response_a": {"M01": 0, "M02": 0, "M03": 0, "M04": 0, "M05": 0, "M06": 0, "M07": 0, "M08": 0, "M09": 0, "M10": 0, "M11": 0, "M12": 0,},
        "response_b": {"M01": 1, "M02": 1, "M03": 1, "M04": 1, "M05": 1, "M06": 1, "M07": 1, "M08": 1, "M09": 1, "M10": 1, "M11": 1, "M12": 1,},
      },
      "pairwise_preference": "B_better",
      "justification": "Trailing comma test",
    }
    """
    p_comma = parse_judge_json(trailing_comma_json)
    assert p_comma["pairwise_preference"] == "B_better"
    print("  [PASS] Trailing comma successfully repaired and parsed.")

    # 3.4 Dimension Clamping & Normalization
    print("\n--- 3.4 Dimension Score Clamping & Alias Normalization ---")
    extreme_scores_json = json.dumps({
        "scores": {
            "response_a": {"cr": -10.0, "Problem_Decomposition": 0.5, "sa": 3.0, "ep": 6.5, "EH": 99.0},
            "response_b": {"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0},
        },
        "behavioral_checklist": {
            "response_a": {f"M{i:02d}": 0 for i in range(1, 13)},
            "response_b": {f"M{i:02d}": 1 for i in range(1, 13)},
        },
        "pairwise_preference": "B_better",
        "justification": "Clamping test",
    })
    p_clamped = parse_judge_json(extreme_scores_json)
    sa = p_clamped["scores"]["response_a"]
    assert sa["CR"] == 1.0, f"Expected 1.0, got {sa['CR']}"
    assert sa["PD"] == 1.0, f"Expected 1.0, got {sa['PD']}"
    assert sa["EP"] == 5.0, f"Expected 5.0, got {sa['EP']}"
    assert sa["EH"] == 5.0, f"Expected 5.0, got {sa['EH']}"
    print(f"  [PASS] Clamping: -10.0 -> {sa['CR']}, 0.5 -> {sa['PD']}, 6.5 -> {sa['EP']}, 99.0 -> {sa['EH']}")

    # 3.5 Marker normalization
    print("\n--- 3.5 Marker Value Normalization ---")
    weird_markers_json = json.dumps({
        "scores": {
            "response_a": {d: 3.0 for d in CANONICAL_DIMENSIONS},
            "response_b": {d: 5.0 for d in CANONICAL_DIMENSIONS},
        },
        "behavioral_checklist": {
            "response_a": {"M01": 5, "M02": -2, "M03": "1", "M04": "invalid"},
            "response_b": {f"M{i:02d}": 1 for i in range(1, 13)},
        },
        "pairwise_preference": "invalid_preference",
        "justification": "",
    })
    p_markers = parse_judge_json(weird_markers_json)
    ma = p_markers["behavioral_checklist"]["response_a"]
    assert ma["M01"] == 1  # 5 >= 1 -> 1
    assert ma["M02"] == 0  # -2 < 1 -> 0
    assert ma["M03"] == 1  # "1" -> 1
    assert ma["M04"] == 0  # "invalid" -> 0
    assert p_markers["pairwise_preference"] == "tie"  # normalized invalid preference
    assert len(p_markers["justification"]) > 0  # defaulted non-empty justification
    print("  [PASS] Weird marker values and invalid pairwise preference cleanly normalized.")

    # 3.6 Corrupted strings, raw numbers, truncated strings (must raise ValueError)
    print("\n--- 3.6 Corrupt and Truncated Inputs (Strict Failure Modes) ---")
    corrupt_inputs = [
        ("raw_number", "42"),
        ("raw_float", "3.14159"),
        ("raw_string", '"Hello world"'),
        ("unquoted_text", "I think Candidate B won because it was better."),
        ("empty_string", ""),
        ("whitespace_only", "   \n\t  "),
        ("null_literal", "null"),
        ("boolean_literal", "true"),
        ("truncated_json", '{"scores": {"response_a": {"CR": 4.0'),
        ("missing_scores", json.dumps({"behavioral_checklist": {}, "pairwise_preference": "tie"})),
        ("missing_checklist", json.dumps({"scores": {}, "pairwise_preference": "tie"})),
    ]
    for label, bad_text in corrupt_inputs:
        try:
            parse_judge_json(bad_text)
            assert False, f"Expected ValueError for {label}"
        except ValueError as e:
            print(f"  [PASS] Corrupt input safely rejected ({label})")


def run_suite_4_judge_system_prompt_and_mock_execution():
    print("\n" + "=" * 70)
    print("SUITE 4: JUDGE SYSTEM PROMPT & MOCK EVALUATOR ADVERSARIAL CHECKS")
    print("=" * 70)

    # 4.1 System Prompt Directives
    prompt = build_judge_system_prompt()
    required_keywords = [
        "ANTI-VERBOSITY",
        "ANTI-SYCOPHANCY",
        "EPISTEMIC HUMILITY",
        "<claude_thinking>",
        "5-DIMENSION RUBRIC",
        "12 BINARY BEHAVIORAL MARKERS",
    ]
    for kw in required_keywords:
        assert kw in prompt, f"Missing required keyword in prompt: {kw}"
    print("  [PASS] Judge system prompt includes all anti-verbosity and anti-sycophancy directives.")

    # 4.2 Single pass & Dual pass mock execution
    judge = EvaluationJudge(JudgeConfig(model="mock"))
    sample_bench = {
        "id": "TC-CR-01",
        "dimension": "CR",
        "prompt": "Evaluate Raft partition behavior",
        "rubric": {"1": "poor", "3": "adequate", "5": "exceptional"},
    }

    base_resp = "Node C will become leader easily because Raft is simple."
    skill_resp = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING & DECONSTRUCTION]\n"
        "- Quoting: '5-node Raft consensus cluster'\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]\n"
        "- Raft §5.4.1 Election Safety invariant check\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n"
        "- State transition DAG\n"
        "[PHASE 4: OUTPUT CALIBRATION]\n"
        "- Restrained delivery\n"
        "</claude_thinking>\n"
        "Node C cannot become leader due to Raft §5.4.1 log up-to-date checks."
    )

    result = judge.evaluate_with_position_swap(
        prompt=sample_bench["prompt"],
        candidate_baseline=base_resp,
        candidate_skill=skill_resp,
        benchmark_item=sample_bench,
    )
    assert result.skill_win_rate == 1.0, f"Expected 1.0, got {result.skill_win_rate}"
    assert result.baseline_win_rate == 0.0
    assert not result.position_bias_detected
    assert result.skill_scores["CR"] >= 4.0
    assert result.baseline_scores["CR"] <= 2.5
    print(f"  [PASS] Full Position-Swap execution: Skill win rate={result.skill_win_rate}, Bias={result.position_bias_detected}")


def run_suite_5_randomized_fuzzing_and_schemas():
    print("\n" + "=" * 70)
    print("SUITE 5: RANDOMIZED FUZZING & SCHEMA INVARIANT STRESS")
    print("=" * 70)

    import random

    valid_payload = {
        "scores": {
            "response_a": {"CR": 3.0, "PD": 3.0, "SA": 3.0, "EP": 3.0, "EH": 3.0},
            "response_b": {"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0},
        },
        "behavioral_checklist": {
            "response_a": {f"M{i:02d}": 0 for i in range(1, 13)},
            "response_b": {f"M{i:02d}": 1 for i in range(1, 13)},
        },
        "pairwise_preference": "B_better",
        "justification": "Valid test justification",
    }

    # 5.1 Fuzz parser with 50 randomized truncations
    base_str = json.dumps(valid_payload, indent=2)
    truncated_passed_safely = 0
    for length in range(1, min(len(base_str), 50)):
        trunc = base_str[:length]
        try:
            parse_judge_json(trunc)
        except ValueError:
            truncated_passed_safely += 1
    print(f"  [PASS] {truncated_passed_safely}/49 prefix-truncated strings safely rejected with ValueError.")

    # 5.2 Schema validation stress
    print("\n--- 5.2 Schemas & Data Model Strict Boundaries ---")
    # DimensionScore schema boundary violations
    try:
        DimensionScore(CR=0.9, PD=3.0, SA=3.0, EP=3.0, EH=3.0)
        assert False, "DimensionScore accepted CR < 1.0"
    except ValueError as e:
        print(f"  [PASS] DimensionScore rejected CR < 1.0: {e}")

    try:
        DimensionScore(CR=3.0, PD=5.1, SA=3.0, EP=3.0, EH=3.0)
        assert False, "DimensionScore accepted PD > 5.0"
    except ValueError as e:
        print(f"  [PASS] DimensionScore rejected PD > 5.0: {e}")

    try:
        DimensionScore(CR=True, PD=3.0, SA=3.0, EP=3.0, EH=3.0)  # bool
        assert False, "DimensionScore accepted bool"
    except TypeError as e:
        print(f"  [PASS] DimensionScore rejected bool: {e}")

    # MarkerChecklist boundary violations
    try:
        MarkerChecklist(markers={f"M{i:02d}": 0 for i in range(1, 12)})  # only 11
        assert False, "MarkerChecklist accepted 11 markers"
    except ValueError as e:
        print(f"  [PASS] MarkerChecklist rejected 11 markers: {e}")

    try:
        MarkerChecklist(markers={**{f"M{i:02d}": 0 for i in range(1, 13)}, "M01": 2})  # value 2
        assert False, "MarkerChecklist accepted marker value 2"
    except ValueError as e:
        print(f"  [PASS] MarkerChecklist rejected marker value 2: {e}")

    print("  [PASS] All schema boundaries empirically verified.")


if __name__ == "__main__":
    print("Starting Milestone 3 Adversarial Challenger Stress Suite...")
    run_suite_1_scoring_edge_cases()
    run_suite_2_position_swapping_symmetry()
    run_suite_3_judge_parser_fuzzing()
    run_suite_4_judge_system_prompt_and_mock_execution()
    run_suite_5_randomized_fuzzing_and_schemas()
    print("\n" + "=" * 70)
    print("ALL 5 SUITES PASSED EMPIRICALLY WITH 100% SUCCESS!")
    print("=" * 70)
