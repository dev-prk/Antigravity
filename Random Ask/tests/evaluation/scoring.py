"""
tests/evaluation/scoring.py
Scoring engine and statistical metrics architecture for Milestone 3.

Provides canonical calculations for:
- Composite Claude Replication Score (CCRS) normalized on [0.0, 100.0]
- Binary Behavioral Compliance Rate (BCR) across 12 canonical markers (M01-M12)
- Information Density Score (IDS) with zero/one token singularity protection
- Verbosity Ratio and length normalization
- Statistical aggregation, dimension means, and bootstrap confidence intervals
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
# Authoritative Canonical Constants
# ---------------------------------------------------------------------------

_CANONICAL_CCRS_WEIGHTS_DICT: Dict[str, float] = {
    "CR": 0.20,  # Complex Multi-Step Reasoning
    "PD": 0.20,  # Problem Decomposition & Ambiguity Resolution
    "SA": 0.25,  # Solution Architecture & Systems Engineering
    "EP": 0.20,  # Execution Planning & Verifiability
    "EH": 0.15,  # Epistemic Humility & Edge Case Detection
}

# Immutable mapping proxy to prevent in-place mutation (Test 2.14.3)
CANONICAL_CCRS_WEIGHTS: Mapping[str, float] = MappingProxyType(_CANONICAL_CCRS_WEIGHTS_DICT)

CANONICAL_12_MARKERS: List[Dict[str, Any]] = [
    {"id": "M01", "name": "Deliberate Scratchpad / Pacing", "dimension": "CR", "weight": 0.0833},
    {"id": "M02", "name": "Premise Integrity Check", "dimension": "EH", "weight": 0.0833},
    {"id": "M03", "name": "Stated vs. Inferred Delineation", "dimension": "PD", "weight": 0.0833},
    {"id": "M04", "name": "MECE Decomposition", "dimension": "PD", "weight": 0.0833},
    {"id": "M05", "name": "Typed Interface Contracts", "dimension": "SA", "weight": 0.0833},
    {"id": "M06", "name": "Failure Domain Modeling", "dimension": "SA", "weight": 0.0833},
    {"id": "M07", "name": "Trade-Off Justification", "dimension": "SA", "weight": 0.0833},
    {"id": "M08", "name": "Dependency Ordering (DAG)", "dimension": "EP", "weight": 0.0833},
    {"id": "M09", "name": "Falsifiable Verification Commands", "dimension": "EP", "weight": 0.0833},
    {"id": "M10", "name": "Rollback & Abort Strategy", "dimension": "EP", "weight": 0.0833},
    {"id": "M11", "name": "Boundary & Edge Case Enumeration", "dimension": "CR", "weight": 0.0833},
    {"id": "M12", "name": "Resistance to Hallucination", "dimension": "EH", "weight": 0.0833},
]

MARKER_TO_DIMENSION: Dict[str, str] = {
    "M01": "CR",
    "M02": "EH",
    "M03": "PD",
    "M04": "PD",
    "M05": "SA",
    "M06": "SA",
    "M07": "SA",
    "M08": "EP",
    "M09": "EP",
    "M10": "EP",
    "M11": "CR",
    "M12": "EH",
}

DIMENSION_TO_MARKERS: Dict[str, List[str]] = {
    "CR": ["M01", "M11"],
    "PD": ["M03", "M04"],
    "SA": ["M05", "M06", "M07"],
    "EP": ["M08", "M09", "M10"],
    "EH": ["M02", "M12"],
}

CANONICAL_DIMENSIONS: Tuple[str, ...] = ("CR", "PD", "SA", "EP", "EH")


# ---------------------------------------------------------------------------
# Data Models / Schemas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DimensionScores:
    """Strongly typed container for 5 rubric dimension scores in [1.0, 5.0]."""
    CR: float
    PD: float
    SA: float
    EP: float
    EH: float

    def to_dict(self) -> Dict[str, float]:
        return {"CR": self.CR, "PD": self.PD, "SA": self.SA, "EP": self.EP, "EH": self.EH}

    @classmethod
    def from_dict(cls, data: Mapping[str, float]) -> DimensionScores:
        for dim in CANONICAL_DIMENSIONS:
            if dim not in data:
                raise ValueError(f"Missing dimension in scores: {dim}")
            val = float(data[dim])
            if val < 1.0 or val > 5.0:
                raise ValueError(f"Score for {dim} out of range [1, 5]: {val}")
        return cls(
            CR=float(data["CR"]),
            PD=float(data["PD"]),
            SA=float(data["SA"]),
            EP=float(data["EP"]),
            EH=float(data["EH"]),
        )


@dataclass(frozen=True)
class EvaluationScoreCard:
    """Individual test case evaluation result."""
    test_case_id: str
    ccrs: float
    bcr: float
    ids: float
    token_count: int
    dimension_scores: Dict[str, float]
    behavioral_checklist: Dict[str, int]
    dimension_bcr: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class StatisticalBounds:
    """Container for sample moments and confidence intervals."""
    count: int
    mean: float
    std: float
    sem: float
    ci_lower: float
    ci_upper: float
    min_val: float
    max_val: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "count": self.count,
            "mean": self.mean,
            "std": self.std,
            "sem": self.sem,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "min": self.min_val,
            "max": self.max_val,
        }


# ---------------------------------------------------------------------------
# Core Scoring Functions
# ---------------------------------------------------------------------------

def compute_ccrs(
    scores: Mapping[str, float],
    weights: Optional[Mapping[str, float]] = None,
) -> float:
    """
    Computes the Composite Claude Replication Score (CCRS) normalized on [0.0, 100.0]%.

    Formula:
        CCRS = sum(w_i * (S_i - 1.0) / 4.0) * 100.0%

    Args:
        scores: Dictionary mapping dimension codes ('CR', 'PD', 'SA', 'EP', 'EH')
                to scores in the range [1.0, 5.0].
        weights: Optional custom weights mapping. Defaults to CANONICAL_CCRS_WEIGHTS.

    Returns:
        float: Normalized CCRS percentage in [0.0, 100.0], rounded to 4 decimal places.

    Raises:
        ValueError: If any required dimension is missing or a score is outside [1.0, 5.0].
        TypeError: If a score is non-numeric or boolean.
    """
    w_map = weights if weights is not None else CANONICAL_CCRS_WEIGHTS

    for dim in w_map:
        if dim not in scores:
            raise ValueError(f"Missing dimension in scores: {dim}")
        raw_val = scores[dim]
        if not isinstance(raw_val, (int, float)) or isinstance(raw_val, bool) or math.isnan(raw_val):
            raise TypeError(f"Score for {dim} must be numeric, got {type(raw_val).__name__}: {raw_val}")
        s = float(raw_val)
        if s < 1.0 or s > 5.0:
            raise ValueError(f"Score for {dim} out of range [1, 5]: {s}")

    weighted_sum = sum(w_map[dim] * ((float(scores[dim]) - 1.0) / 4.0) for dim in w_map)
    return round(weighted_sum * 100.0, 4)


def oracle_compute_ccrs(scores: Dict[str, float]) -> float:
    """Compatibility alias matching tests/e2e/conftest.py oracle helper."""
    return compute_ccrs(scores)


def compute_bcr(markers: Mapping[str, int]) -> float:
    """
    Computes the Binary Behavioral Compliance Rate (BCR) across all 12 markers.

    Formula:
        BCR = sum(M_j) / 12.0 * 100.0%

    Args:
        markers: Dictionary containing keys M01..M12 with integer values in {0, 1}.

    Returns:
        float: Compliance percentage in [0.0, 100.0], rounded to 4 decimal places.

    Raises:
        ValueError: If len(markers) != 12, a marker key is missing, or a value is not in {0, 1}.
    """
    if len(markers) != 12:
        raise ValueError(f"Expected 12 markers, got {len(markers)}")

    total = 0
    for i in range(1, 13):
        m_id = f"M{i:02d}"
        if m_id not in markers:
            raise ValueError(f"Missing marker: {m_id}")
        val = markers[m_id]
        if isinstance(val, bool) or val not in (0, 1):
            raise ValueError(f"Marker {m_id} value must be 0 or 1, got {val}")
        total += int(val)

    return round((total / 12.0) * 100.0, 4)


def oracle_compute_bcr(markers: Dict[str, int]) -> float:
    """Compatibility alias matching tests/e2e/conftest.py oracle helper."""
    return compute_bcr(markers)


def compute_information_density(ccrs: float, token_count: int) -> float:
    """
    Computes the Information Density Score (IDS) with zero/one-token singularity protection.

    Formula:
        IDS = CCRS / log2(TokenCount)

    Singularity Protection:
        If token_count <= 1: returns 0.0 (guards against log2(0) = -inf and log2(1) = 0).

    Args:
        ccrs: Composite Claude Replication Score in [0.0, 100.0].
        token_count: Number of generated tokens.

    Returns:
        float: Information Density Score, rounded to 4 decimal places.
    """
    if token_count <= 1:
        return 0.0
    return round(ccrs / math.log2(token_count), 4)


def compute_ids(ccrs: float, token_count: int) -> float:
    """Direct alias for compute_information_density."""
    return compute_information_density(ccrs, token_count)


def oracle_compute_information_density(ccrs: float, token_count: int) -> float:
    """Compatibility alias matching tests/e2e/conftest.py oracle helper."""
    return compute_information_density(ccrs, token_count)


def compute_verbosity_ratio(tokens_skilled: int, tokens_baseline: int) -> float:
    """
    Computes the Verbosity Ratio between skilled and baseline responses.

    Formula:
        V_ratio = tokens_skilled / tokens_baseline

    Args:
        tokens_skilled: Generated token count with skill equipped.
        tokens_baseline: Generated token count for unequipped baseline.

    Returns:
        float: Verbosity ratio rounded to 2 decimal places (or 0.0 if baseline <= 0).
    """
    if tokens_baseline <= 0:
        return 0.0
    return round(tokens_skilled / tokens_baseline, 2)


def compute_dimension_bcr(markers: Mapping[str, int], dimension: str) -> float:
    """
    Computes BCR compliance rate restricted to markers belonging to a given dimension.

    Args:
        markers: Dictionary containing M01..M12 evaluations.
        dimension: Dimension code ('CR', 'PD', 'SA', 'EP', 'EH').

    Returns:
        float: Percentage of satisfied markers in that dimension [0.0, 100.0].
    """
    if dimension not in DIMENSION_TO_MARKERS:
        raise ValueError(f"Unknown dimension: {dimension}")
    dim_markers = DIMENSION_TO_MARKERS[dimension]
    total = sum(int(markers[m]) for m in dim_markers if m in markers)
    return round((total / float(len(dim_markers))) * 100.0, 4)


def compute_dimension_scores(test_case_scores: Sequence[Mapping[str, float]]) -> Dict[str, float]:
    """
    Calculates average rubric scores across a sequence of evaluated test cases per dimension.

    Args:
        test_case_scores: List of dicts mapping dimension codes to rubric scores.

    Returns:
        Dict[str, float]: Mean score per dimension, rounded to 4 decimal places.
    """
    if not test_case_scores:
        raise ValueError("Cannot compute dimension scores on empty sequence")

    n = len(test_case_scores)
    dim_sums: Dict[str, float] = {d: 0.0 for d in CANONICAL_DIMENSIONS}

    for scores in test_case_scores:
        for d in CANONICAL_DIMENSIONS:
            if d not in scores:
                raise ValueError(f"Missing dimension '{d}' in test case scores")
            dim_sums[d] += float(scores[d])

    return {d: round(dim_sums[d] / n, 4) for d in CANONICAL_DIMENSIONS}


# ---------------------------------------------------------------------------
# Statistical Bounds & Bootstrap Engine
# ---------------------------------------------------------------------------

def sample_mean(values: Sequence[float]) -> float:
    """Computes arithmetic mean of a float sequence."""
    if not values:
        raise ValueError("Cannot compute mean of empty sequence")
    return float(statistics.fmean(values))


def sample_std(values: Sequence[float], ddof: int = 1) -> float:
    """
    Computes sample standard deviation with Bessel's correction (ddof=1).
    Returns 0.0 if len(values) <= ddof.
    """
    if len(values) <= ddof:
        return 0.0
    return float(statistics.stdev(values))


def sample_sem(values: Sequence[float]) -> float:
    """
    Computes Standard Error of the Mean (SEM = s / sqrt(N)).
    Returns 0.0 if len(values) <= 1.
    """
    if len(values) <= 1:
        return 0.0
    s = sample_std(values, ddof=1)
    return s / math.sqrt(len(values))


def bootstrap_confidence_interval(
    data: Sequence[float],
    confidence: float = 0.95,
    n_bootstrap: int = 2000,
    seed: Optional[int] = 42,
) -> Tuple[float, float]:
    """
    Computes non-parametric bootstrap confidence interval for the sample mean.

    Args:
        data: Sequence of numeric observations.
        confidence: Confidence level in (0.0, 1.0) (default 0.95 for 95% CI).
        n_bootstrap: Number of bootstrap iterations (default 2000).
        seed: Random seed for deterministic reproducibility (default 42).

    Returns:
        Tuple[float, float]: (lower_bound, upper_bound) rounded to 4 decimal places.
    """
    n = len(data)
    if n == 0:
        return (0.0, 0.0)
    if n == 1:
        val = round(float(data[0]), 4)
        return (val, val)

    rng = random.Random(seed)
    data_list = [float(x) for x in data]

    boot_means: List[float] = [
        statistics.fmean(rng.choices(data_list, k=n))
        for _ in range(n_bootstrap)
    ]
    boot_means.sort()

    alpha = 1.0 - confidence
    low_idx = max(0, min(n_bootstrap - 1, int(n_bootstrap * (alpha / 2.0))))
    high_idx = max(0, min(n_bootstrap - 1, int(n_bootstrap * (1.0 - alpha / 2.0))))

    return (round(boot_means[low_idx], 4), round(boot_means[high_idx], 4))


def compute_statistical_bounds(
    data: Sequence[float],
    confidence: float = 0.95,
    n_bootstrap: int = 2000,
    seed: Optional[int] = 42,
) -> StatisticalBounds:
    """
    Calculates sample moments, bounds, and bootstrap confidence intervals for a sequence.
    """
    n = len(data)
    if n == 0:
        return StatisticalBounds(
            count=0, mean=0.0, std=0.0, sem=0.0,
            ci_lower=0.0, ci_upper=0.0, min_val=0.0, max_val=0.0
        )

    mean_val = sample_mean(data)
    std_val = sample_std(data)
    sem_val = sample_sem(data)
    ci_low, ci_high = bootstrap_confidence_interval(data, confidence, n_bootstrap, seed)

    return StatisticalBounds(
        count=n,
        mean=round(mean_val, 4),
        std=round(std_val, 4),
        sem=round(sem_val, 4),
        ci_lower=ci_low,
        ci_upper=ci_high,
        min_val=round(min(data), 4),
        max_val=round(max(data), 4),
    )


# ---------------------------------------------------------------------------
# Aggregation & Paired Delta Analysis
# ---------------------------------------------------------------------------

def compute_debiased_win_rate(
    pass1_preferences: Sequence[str],
    pass2_preferences: Sequence[str],
) -> float:
    """
    Computes debiased win rate for skill-equipped candidate across position-swapped runs.

    In Pass 1:
        Candidate A = Baseline, Candidate B = Skill-Equipped.
        A 'B_better' preference yields 1 win for skill.
    In Pass 2:
        Candidate A = Skill-Equipped, Candidate B = Baseline.
        An 'A_better' preference yields 1 win for skill.
    Ties ('tie') award 0.5 wins.

    Args:
        pass1_preferences: List of judge preferences for Pass 1 ('A_better', 'B_better', 'tie').
        pass2_preferences: List of judge preferences for Pass 2 ('A_better', 'B_better', 'tie').

    Returns:
        float: Debiased win rate in [0.0, 1.0].
    """
    if len(pass1_preferences) != len(pass2_preferences):
        raise ValueError("Pass 1 and Pass 2 preferences must have identical lengths")
    if not pass1_preferences:
        return 0.0

    total_skill_points = 0.0
    for p1, p2 in zip(pass1_preferences, pass2_preferences):
        if p1 == "B_better":
            total_skill_points += 1.0
        elif p1 == "tie":
            total_skill_points += 0.5

        if p2 == "A_better":
            total_skill_points += 1.0
        elif p2 == "tie":
            total_skill_points += 0.5

    return round(total_skill_points / (2.0 * len(pass1_preferences)), 4)


def compute_aggregate_metrics(results: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates evaluation results across test cases into dimension means,
    composite metrics, token statistics, and marker compliance rates.

    Args:
        results: Sequence of dicts where each dict contains:
            - 'scores': Dict[str, float]
            - 'behavioral_checklist': Dict[str, int]
            - 'token_count' (or 'tokens'): int

    Returns:
        Dict[str, Any]: Comprehensive aggregate dictionary.
    """
    if not results:
        raise ValueError("Cannot aggregate empty results sequence")

    ccrs_list: List[float] = []
    bcr_list: List[float] = []
    ids_list: List[float] = []
    tokens_list: List[int] = []
    scores_list: List[Mapping[str, float]] = []
    marker_pass_counts: Dict[str, int] = {f"M{i:02d}": 0 for i in range(1, 13)}

    for res in results:
        scores = res["scores"]
        markers = res["behavioral_checklist"]
        tokens = int(res.get("token_count", res.get("tokens", 0)))

        c = compute_ccrs(scores)
        b = compute_bcr(markers)
        i_dens = compute_information_density(c, tokens)

        ccrs_list.append(c)
        bcr_list.append(b)
        ids_list.append(i_dens)
        tokens_list.append(tokens)
        scores_list.append(scores)

        for m_id, v in markers.items():
            if m_id in marker_pass_counts and int(v) == 1:
                marker_pass_counts[m_id] += 1

    n = len(results)
    dim_means = compute_dimension_scores(scores_list)
    dim_bcr_means: Dict[str, float] = {}
    for d in CANONICAL_DIMENSIONS:
        rates = [compute_dimension_bcr(r["behavioral_checklist"], d) for r in results]
        dim_bcr_means[d] = round(statistics.fmean(rates), 4)

    return {
        "count": n,
        "ccrs": compute_statistical_bounds(ccrs_list).to_dict(),
        "bcr": compute_statistical_bounds(bcr_list).to_dict(),
        "ids": compute_statistical_bounds(ids_list).to_dict(),
        "tokens": {
            "total": sum(tokens_list),
            "mean": round(statistics.fmean(tokens_list), 2),
            "min": min(tokens_list),
            "max": max(tokens_list),
        },
        "dimension_score_means": dim_means,
        "dimension_bcr_means": dim_bcr_means,
        "marker_pass_rates": {
            m: round((count / n) * 100.0, 2)
            for m, count in marker_pass_counts.items()
        },
    }


def evaluate_contrastive_delta(
    baseline_results: Sequence[Mapping[str, Any]],
    skilled_results: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """
    Computes paired contrastive deltas (Skilled minus Baseline) across matched test cases.

    Returns:
        Dict[str, Any]: Contains mean deltas, paired bootstrap CIs, and verbosity ratio.
    """
    if len(baseline_results) != len(skilled_results):
        raise ValueError("Baseline and skilled results must have identical lengths")
    if not baseline_results:
        raise ValueError("Cannot evaluate delta on empty results")

    delta_ccrs_list: List[float] = []
    delta_bcr_list: List[float] = []
    delta_ids_list: List[float] = []

    total_base_tokens = 0
    total_skill_tokens = 0

    for base, skill in zip(baseline_results, skilled_results):
        c_base = compute_ccrs(base["scores"])
        c_skill = compute_ccrs(skill["scores"])
        b_base = compute_bcr(base["behavioral_checklist"])
        b_skill = compute_bcr(skill["behavioral_checklist"])

        t_base = int(base.get("token_count", base.get("tokens", 0)))
        t_skill = int(skill.get("token_count", skill.get("tokens", 0)))

        ids_base = compute_information_density(c_base, t_base)
        ids_skill = compute_information_density(c_skill, t_skill)

        delta_ccrs_list.append(c_skill - c_base)
        delta_bcr_list.append(b_skill - b_base)
        delta_ids_list.append(ids_skill - ids_base)

        total_base_tokens += t_base
        total_skill_tokens += t_skill

    v_ratio = compute_verbosity_ratio(total_skill_tokens, total_base_tokens)

    return {
        "count": len(baseline_results),
        "delta_ccrs": compute_statistical_bounds(delta_ccrs_list).to_dict(),
        "delta_bcr": compute_statistical_bounds(delta_bcr_list).to_dict(),
        "delta_ids": compute_statistical_bounds(delta_ids_list).to_dict(),
        "verbosity_ratio": v_ratio,
        "raw_deltas": {
            "ccrs": delta_ccrs_list,
            "bcr": delta_bcr_list,
            "ids": delta_ids_list,
        },
    }
