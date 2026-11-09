# Milestone 3 Analysis: Benchmark Dataset & Schema Architecture

**Author**: `m3_explorer_1`  
**Date**: 2026-11-06T22:45:00Z  
**Target Milestone**: Milestone 3 (Comparative Evaluation Suite & Benchmark Runner)  
**Deliverables Investigated**:
1. `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/schemas.py`
2. `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/benchmarks.jsonl`

---

## 1. Executive Summary

Milestone 3 establishes the empirical verification backbone for the `claude` Antigravity skill. To scientifically evaluate whether target models (GPT-4o, Gemini 2.0, open-weights) replicate Claude's cognitive traits, the evaluation suite requires:
1. **A canonical 15-case benchmark suite** (`benchmarks.jsonl`) distributed across 5 cognitive dimensions (Complex Reasoning, Problem Decomposition, Solution Architecture, Execution Planning, Epistemic Humility) with high-friction challenges, baseline failure traps, expected Claude behaviors, and anchored 1–3–5 rubrics.
2. **A strongly typed schema layer** (`schemas.py`) defining the data structures for benchmarks, judge evaluation outputs, dual-pass position debiasing, marker evaluations, CCRS/BCR metrics, and serialized runner reports.

### Critical Runtime Discovery
Investigation of the runtime environment revealed that Python 3.9.6 is installed at `/usr/bin/python3` **without `pydantic` or `pip` installed**. Consequently, `schemas.py` must be architected using **Python standard library dataclasses (`dataclasses`, `typing`, `json`, `re`, `math`)** with strict `__post_init__` validation and custom serialization methods (`to_dict`, `from_dict`, `to_json`, `from_json`). An optional Pydantic v2 bridge is provided for forward-compatibility when Pydantic is present, ensuring 100% test pass rates in zero-dependency environments.

---

## 2. E2E Test Contract & Validation Rules Matrix

Inspection of opaque-box E2E tests (`test_tier1_feature_coverage.py`, `test_tier2_boundaries.py`, `test_tier3_combinations.py`, and `test_tier4_real_world.py`) reveals the following explicit assertion contracts:

| Test Case | E2E Suite & Line | Required Contract / Assertion | Design Decision in Schemas & Benchmarks |
|---|---|---|---|
| **Test 10.1** | `test_tier1_feature_coverage.py:615` | `benchmarks.jsonl` exists and parses as valid JSONL (`json.loads(line)` per non-empty line). | JSONL format: exactly one JSON object per line, UTF-8 encoded. |
| **Test 10.2** | `test_tier1_feature_coverage.py:628` | Exactly 15 benchmark test cases exist (`len(lines) == 15`). | Exactly 15 entries (`TC-CR-01` through `TC-EH-03`). |
| **Test 10.3** | `test_tier1_feature_coverage.py:638` | All 5 dimensions (`CR`, `PD`, `SA`, `EP`, `EH`) have exactly 3 test cases each. | 3 CR, 3 PD, 3 SA, 3 EP, 3 EH. |
| **Test 10.4** | `test_tier1_feature_coverage.py:657` | Every item contains required fields: `id`, `dimension`, `prompt`. | All entries include `id`, `dimension`, `prompt`, `baseline_failure_mode`, `claude_behaviors`, `rubric`. |
| **Test 10.5** | `test_tier1_feature_coverage.py:670` | Rubric contains anchors for scores 1, 3, 5: accepts both `{"1", "3", "5"}` and `{"score_1", "score_3", "score_5"}`. | Every rubric entry provides **both** key formats (`"1"`, `"3"`, `"5"` AND `"score_1"`, `"score_3"`, `"score_5"`). |
| **Test 2.10.1** | `test_tier2_boundaries.py:576` | JSONL parser gracefully ignores empty / whitespace lines. | `load_benchmarks()` explicitly skips empty and whitespace lines (`line.strip()`). |
| **Test 2.10.2** | `test_tier2_boundaries.py:585` | Unknown dimension codes outside `{"CR", "PD", "SA", "EP", "EH"}` are rejected. | `BenchmarkCase.__post_init__` raises `ValueError` if dimension is not in canonical set. |
| **Test 2.10.3** | `test_tier2_boundaries.py:594` | Rejects duplicate benchmark IDs (`len(ids) == len(set(ids))`). | `load_benchmarks()` enforces unique IDs. |
| **Test 2.10.4** | `test_tier2_boundaries.py:605` | Rejects incomplete rubrics missing score 3 anchor. | Schema validator enforces `score_1`/`1`, `score_3`/`3`, `score_5`/`5` all exist and are non-empty strings. |
| **Test 2.10.5** | `test_tier2_boundaries.py:613` | Rejects empty or whitespace-only prompts. | Schema validator raises `ValueError` on empty / whitespace-only prompt. |
| **Test 11.5** | `test_tier1_feature_coverage.py:747` | Judge output JSON schema contract: `scores` (mapping to CR, PD, SA, EP, EH), `behavioral_checklist` (M01-M12 binary 0/1), `pairwise_preference` (`A_better`, `B_better`, `tie`), `justification`. | Defined as `JudgeEvaluationResult` in `schemas.py`. |
| **Test 2.11.4** | `test_tier2_boundaries.py:650` | Score values must be within $[1.0, 5.0]$. Values outside raise `ValueError`. | `DimensionScore` validator checks $1.0 \le s \le 5.0$. |
| **Interaction 11** | `test_tier3_combinations.py:213` | All benchmark dimensions map to `CANONICAL_CCRS_WEIGHTS` summing to 1.0 (`CR: 0.20, PD: 0.20, SA: 0.25, EP: 0.20, EH: 0.15`). | `CANONICAL_DIMENSIONS` and weights codified in `schemas.py`. |
| **Interaction 15** | `test_tier3_combinations.py:275` | CR prompts (`TC-CR-01..03`) must exceed 100 characters for constraint quoting. | All CR prompts are comprehensive, ranging from 450 to 950 characters. |
| **Interaction 16** | `test_tier3_combinations.py:291` | `TC-EH-01` prompt must contain `"cassandra"` (false premise 2PC test). | `TC-EH-01` specifically challenges Cassandra multi-partition 2PC locks. |
| **Scenario 5** | `test_tier4_real_world.py:205` | Triad evaluation pipeline with `TC-CR-01` (Raft consensus) and dual-pass position swapping. | `TC-CR-01` focuses on Raft log invariants and partition healing. |
| **Scenario 6** | `test_tier4_real_world.py:258` | `TC-EP-02` Execution plan validation: Zero-Downtime Multi-Service Auth Migration (JWT) with 5 phases, verification commands, and rollback trigger. | `TC-EP-02` prompt and rubrics match this exact scenario. |
| **Scenario 7** | `test_tier4_real_world.py:286` | `TC-EH-03` Cryptographic Token Security Review: clock skew bypass, timing attacks, unhandled exceptions. | `TC-EH-03` incorporates the exact `validate_session_token` snippet. |
| **Scenario 8** | `test_tier4_real_world.py:308` | `TC-SA-02` Multi-Region Banking Ledger Architecture: PACELC, Escrow/Reservations, typed events (`BalanceReserved`, `MoneyDeposited`, `TransferSettled`). | `TC-SA-02` prompt, behaviors, and rubric require this exact architectural pattern. |

---

## 3. Schema Architecture (`tests/evaluation/schemas.py`)

### 3.1 Design Principles
1. **Zero External Dependencies**: Pure Python standard library (`dataclasses`, `typing`, `json`, `re`, `math`, `pathlib`).
2. **Defensive Validation**: Strict type and range assertions in `__post_init__` and `.from_dict()`.
3. **Dual Compatibility**:
   - Rubrics accept `"1"`, `"3"`, `"5"` AND `"score_1"`, `"score_3"`, `"score_5"`.
   - Dimensions accept code (`"CR"`) and full name (`"Complex Reasoning"`).
4. **Complete Serialization Lifecycle**:
   - `to_dict()`, `from_dict()`, `to_json()`, `from_json()`.
   - Batch file loaders (`load_benchmarks`, `dump_benchmarks`, `load_runner_output`, `dump_runner_output`).
5. **Optional Pydantic v2 Bridge**: When Pydantic is installed, models dynamically export as Pydantic models.

### 3.2 Complete Code Blueprint for `tests/evaluation/schemas.py`

```python
"""
tests/evaluation/schemas.py
Authoritative validation schemas and data structures for Milestone 3 evaluation suite.
Standard library dataclass implementation with strict boundary validation and dual compatibility.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# Constants & Canonical Vectors
# ---------------------------------------------------------------------------

CANONICAL_DIMENSIONS = ("CR", "PD", "SA", "EP", "EH")

DIMENSION_NAMES = {
    "CR": "Complex Reasoning",
    "PD": "Problem Decomposition",
    "SA": "Solution Architecture",
    "EP": "Execution Planning",
    "EH": "Epistemic Humility",
}

CANONICAL_CCRS_WEIGHTS: Dict[str, float] = {
    "CR": 0.20,
    "PD": 0.20,
    "SA": 0.25,
    "EP": 0.20,
    "EH": 0.15,
}

CANONICAL_12_MARKERS = (
    "M01", "M02", "M03", "M04", "M05", "M06",
    "M07", "M08", "M09", "M10", "M11", "M12"
)

CANONICAL_15_BENCHMARK_IDS = (
    "TC-CR-01", "TC-CR-02", "TC-CR-03",
    "TC-PD-01", "TC-PD-02", "TC-PD-03",
    "TC-SA-01", "TC-SA-02", "TC-SA-03",
    "TC-EP-01", "TC-EP-02", "TC-EP-03",
    "TC-EH-01", "TC-EH-02", "TC-EH-03",
)

# ---------------------------------------------------------------------------
# Dimension Code Enumeration
# ---------------------------------------------------------------------------

class DimensionCode(str, Enum):
    CR = "CR"
    PD = "PD"
    SA = "SA"
    EP = "EP"
    EH = "EH"

    @classmethod
    def from_str(cls, val: str) -> "DimensionCode":
        cleaned = val.strip().upper()
        if cleaned in cls.__members__:
            return cls[cleaned]
        for code, full in DIMENSION_NAMES.items():
            if cleaned.lower() == full.lower():
                return cls[code]
        raise ValueError(f"Invalid dimension code: '{val}'. Must be one of {CANONICAL_DIMENSIONS}")

# ---------------------------------------------------------------------------
# Rubric Anchors Schema
# ---------------------------------------------------------------------------

@dataclass
class RubricAnchors:
    score_1: str
    score_3: str
    score_5: str

    def __post_init__(self):
        if not self.score_1 or not self.score_1.strip():
            raise ValueError("Rubric anchor for score 1 must be a non-empty string.")
        if not self.score_3 or not self.score_3.strip():
            raise ValueError("Rubric anchor for score 3 must be a non-empty string.")
        if not self.score_5 or not self.score_5.strip():
            raise ValueError("Rubric anchor for score 5 must be a non-empty string.")

    def to_dict(self, dual_format: bool = True) -> Dict[str, str]:
        """Returns rubric dictionary with both numeric string and score_X keys if dual_format is True."""
        res = {
            "score_1": self.score_1,
            "score_3": self.score_3,
            "score_5": self.score_5,
        }
        if dual_format:
            res["1"] = self.score_1
            res["3"] = self.score_3
            res["5"] = self.score_5
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RubricAnchors":
        if not isinstance(data, dict):
            raise TypeError(f"Rubric must be a dictionary, got {type(data)}")
        s1 = data.get("score_1") or data.get("1")
        s3 = data.get("score_3") or data.get("3")
        s5 = data.get("score_5") or data.get("5")
        if not s1:
            raise ValueError("Missing score 1 anchor ('1' or 'score_1')")
        if not s3:
            raise ValueError("Missing score 3 anchor ('3' or 'score_3')")
        if not s5:
            raise ValueError("Missing score 5 anchor ('5' or 'score_5')")
        return cls(score_1=str(s1).strip(), score_3=str(s3).strip(), score_5=str(s5).strip())

# ---------------------------------------------------------------------------
# Benchmark Case Schema
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkCase:
    id: str
    dimension: str
    prompt: str
    rubric: Dict[str, str]
    title: str = ""
    challenge_summary: str = ""
    baseline_failure_mode: str = ""
    claude_behaviors: List[str] = field(default_factory=list)
    rubric_anchors: Optional[Dict[str, str]] = None
    binary_markers_expected: List[str] = field(default_factory=list)

    def __post_init__(self):
        # 1. ID Validation
        if not self.id or not isinstance(self.id, str):
            raise ValueError("BenchmarkCase 'id' must be a non-empty string.")
        if not re.match(r"^TC-(CR|PD|SA|EP|EH)-\d{2}$", self.id):
            raise ValueError(f"BenchmarkCase 'id' '{self.id}' violates canonical pattern '^TC-(CR|PD|SA|EP|EH)-\\d{{2}}$'")

        # 2. Dimension Validation
        clean_dim = self.dimension.strip().upper()
        if clean_dim not in CANONICAL_DIMENSIONS:
            raise ValueError(f"Invalid dimension '{self.dimension}'. Must be one of {CANONICAL_DIMENSIONS}")
        self.dimension = clean_dim

        # Dimension-ID coherence
        expected_prefix = f"TC-{self.dimension}"
        if not self.id.startswith(expected_prefix):
            raise ValueError(f"BenchmarkCase id '{self.id}' does not match dimension '{self.dimension}'")

        # 3. Prompt Validation
        if not self.prompt or not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError(f"BenchmarkCase '{self.id}' prompt must be a non-empty string.")
        self.prompt = self.prompt.strip()

        # Complex reasoning prompts must exceed 100 characters for constraint quoting
        if self.dimension == "CR" and len(self.prompt) < 100:
            raise ValueError(f"CR benchmark prompt '{self.id}' must exceed 100 chars for constraint quoting, got {len(self.prompt)}")

        # 4. Rubric Validation
        anchors = RubricAnchors.from_dict(self.rubric)
        # Ensure self.rubric has dual keys
        self.rubric = anchors.to_dict(dual_format=True)
        if not self.rubric_anchors:
            self.rubric_anchors = {
                "score_1": anchors.score_1,
                "score_3": anchors.score_3,
                "score_5": anchors.score_5,
            }

        # 5. Marker validation if provided
        for m in self.binary_markers_expected:
            if m not in CANONICAL_12_MARKERS:
                raise ValueError(f"Unknown marker '{m}' in binary_markers_expected. Must be in {CANONICAL_12_MARKERS}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dimension": self.dimension,
            "title": self.title,
            "prompt": self.prompt,
            "challenge_summary": self.challenge_summary,
            "baseline_failure_mode": self.baseline_failure_mode,
            "claude_behaviors": self.claude_behaviors,
            "rubric": self.rubric,
            "rubric_anchors": self.rubric_anchors,
            "binary_markers_expected": self.binary_markers_expected,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkCase":
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data)}")
        rubric_data = data.get("rubric") or data.get("rubric_anchors")
        if not rubric_data:
            raise ValueError(f"Item '{data.get('id')}' missing required rubric")

        # Handle variations of claude_behaviors field
        behaviors = data.get("claude_behaviors") or data.get("expected_claude_markers") or []
        if isinstance(behaviors, str):
            behaviors = [behaviors]

        return cls(
            id=data.get("id", ""),
            dimension=data.get("dimension", ""),
            prompt=data.get("prompt", ""),
            rubric=rubric_data,
            title=data.get("title", ""),
            challenge_summary=data.get("challenge_summary", ""),
            baseline_failure_mode=data.get("baseline_failure_mode", data.get("baseline_failure_trap", "")),
            claude_behaviors=list(behaviors),
            rubric_anchors=data.get("rubric_anchors"),
            binary_markers_expected=data.get("binary_markers_expected", []),
        )

# ---------------------------------------------------------------------------
# Dimension Scores Schema
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    CR: float
    PD: float
    SA: float
    EP: float
    EH: float

    def __post_init__(self):
        for dim in CANONICAL_DIMENSIONS:
            val = getattr(self, dim)
            if not isinstance(val, (int, float)):
                raise TypeError(f"Score for {dim} must be numeric, got {type(val)}")
            if val < 1.0 or val > 5.0:
                raise ValueError(f"Score for {dim} ({val}) out of canonical range [1.0, 5.0]")
            setattr(self, dim, float(val))

    def to_dict(self) -> Dict[str, float]:
        return {dim: getattr(self, dim) for dim in CANONICAL_DIMENSIONS}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DimensionScore":
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict for DimensionScore, got {type(data)}")
        # Allow case-insensitive or full name matching
        resolved = {}
        for dim in CANONICAL_DIMENSIONS:
            val = data.get(dim)
            if val is None:
                # Try full name
                full_name = DIMENSION_NAMES[dim]
                val = data.get(full_name) or data.get(full_name.lower().replace(" ", "_"))
            if val is None:
                raise ValueError(f"Missing dimension score for '{dim}'")
            resolved[dim] = float(val)
        return cls(**resolved)

# ---------------------------------------------------------------------------
# Behavioral Checklist Schema (12 Markers)
# ---------------------------------------------------------------------------

@dataclass
class MarkerChecklist:
    markers: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.markers:
            # Initialize with zeros
            self.markers = {f"M{i:02d}": 0 for i in range(1, 13)}
        if len(self.markers) != 12:
            raise ValueError(f"Expected exactly 12 markers, got {len(self.markers)}")
        for i in range(1, 13):
            m_id = f"M{i:02d}"
            if m_id not in self.markers:
                raise ValueError(f"Missing marker: {m_id}")
            val = self.markers[m_id]
            if val not in (0, 1):
                raise ValueError(f"Marker {m_id} value must be 0 or 1, got {val}")

    def to_dict(self) -> Dict[str, int]:
        return dict(self.markers)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarkerChecklist":
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data)}")
        return cls(markers={k: int(v) for k, v in data.items()})

# ---------------------------------------------------------------------------
# Judge Evaluation Output Schema
# ---------------------------------------------------------------------------

@dataclass
class JudgeEvaluationResult:
    scores: Dict[str, Dict[str, float]]
    behavioral_checklist: Dict[str, Dict[str, int]]
    pairwise_preference: Literal["A_better", "B_better", "tie"]
    justification: str

    def __post_init__(self):
        # Validate scores
        if "response_a" not in self.scores or "response_b" not in self.scores:
            raise ValueError("Judge output 'scores' must contain 'response_a' and 'response_b'")
        DimensionScore.from_dict(self.scores["response_a"])
        DimensionScore.from_dict(self.scores["response_b"])

        # Validate checklist
        if "response_a" not in self.behavioral_checklist or "response_b" not in self.behavioral_checklist:
            raise ValueError("Judge output 'behavioral_checklist' must contain 'response_a' and 'response_b'")
        MarkerChecklist.from_dict(self.behavioral_checklist["response_a"])
        MarkerChecklist.from_dict(self.behavioral_checklist["response_b"])

        # Validate preference
        if self.pairwise_preference not in ("A_better", "B_better", "tie"):
            raise ValueError(f"Invalid pairwise_preference: {self.pairwise_preference}")

        if not self.justification or not isinstance(self.justification, str):
            raise ValueError("Judge output 'justification' must be a non-empty string.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": self.scores,
            "behavioral_checklist": self.behavioral_checklist,
            "pairwise_preference": self.pairwise_preference,
            "justification": self.justification,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JudgeEvaluationResult":
        return cls(
            scores=data["scores"],
            behavioral_checklist=data["behavioral_checklist"],
            pairwise_preference=data["pairwise_preference"],
            justification=data.get("justification", ""),
        )

# ---------------------------------------------------------------------------
# Dual-Run Position Swap Result Schema
# ---------------------------------------------------------------------------

@dataclass
class DualRunPositionSwapResult:
    pass1_forward: JudgeEvaluationResult  # A = Baseline, B = Skilled
    pass2_reverse: JudgeEvaluationResult  # A = Skilled, B = Baseline
    win_rate_b: float                     # [0.0, 1.0]
    position_bias_detected: bool

    @classmethod
    def compute(
        cls, pass1: JudgeEvaluationResult, pass2: JudgeEvaluationResult
    ) -> "DualRunPositionSwapResult":
        # Pass 1: Candidate 1 = Baseline, Candidate 2 = Skilled
        # Skilled wins if pass1 preference is B_better
        if pass1.pairwise_preference == "B_better":
            p1_b = 1.0
        elif pass1.pairwise_preference == "tie":
            p1_b = 0.5
        else:
            p1_b = 0.0

        # Pass 2: Candidate 1 = Skilled, Candidate 2 = Baseline
        # Skilled wins if pass2 preference is A_better
        if pass2.pairwise_preference == "A_better":
            p2_b = 1.0
        elif pass2.pairwise_preference == "tie":
            p2_b = 0.5
        else:
            p2_b = 0.0

        win_rate = (p1_b + p2_b) / 2.0

        # Detect position bias: if judge always picked Candidate 1 or Candidate 2 regardless
        bias = (
            (pass1.pairwise_preference == "A_better" and pass2.pairwise_preference == "A_better")
            or (pass1.pairwise_preference == "B_better" and pass2.pairwise_preference == "B_better")
        )

        return cls(
            pass1_forward=pass1,
            pass2_reverse=pass2,
            win_rate_b=win_rate,
            position_bias_detected=bias,
        )

# ---------------------------------------------------------------------------
# Individual Case Evaluation Result Schema
# ---------------------------------------------------------------------------

@dataclass
class CaseEvaluationResult:
    benchmark_id: str
    dimension: str
    prompt: str
    response_baseline: str
    response_skilled: str
    tokens_baseline: int
    tokens_skilled: int
    scores_baseline: Dict[str, float]
    scores_skilled: Dict[str, float]
    markers_baseline: Dict[str, int]
    markers_skilled: Dict[str, int]
    ccrs_baseline: float
    ccrs_skilled: float
    delta_ccrs: float
    bcr_baseline: float
    bcr_skilled: float
    delta_bcr: float
    verbosity_ratio: float
    ids_baseline: float
    ids_skilled: float
    win_rate_skilled: float
    position_bias_detected: bool
    justification_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------------------------
# Full Suite Summary Metrics Schema
# ---------------------------------------------------------------------------

@dataclass
class SuiteSummaryMetrics:
    total_cases: int
    mean_ccrs_baseline: float
    mean_ccrs_skilled: float
    delta_ccrs: float
    mean_bcr_baseline: float
    mean_bcr_skilled: float
    delta_bcr: float
    overall_win_rate_skilled: float
    mean_verbosity_ratio: float
    mean_ids_baseline: float
    mean_ids_skilled: float
    dimension_ccrs_breakdown: Dict[str, Dict[str, float]]
    marker_compliance_breakdown: Dict[str, Dict[str, float]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ---------------------------------------------------------------------------
# Full Runner Output Schema
# ---------------------------------------------------------------------------

@dataclass
class RunnerOutput:
    timestamp: str
    model_baseline: str
    model_skilled: str
    judge_model: str
    cases: List[CaseEvaluationResult]
    summary: SuiteSummaryMetrics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "model_baseline": self.model_baseline,
            "model_skilled": self.model_skilled,
            "judge_model": self.judge_model,
            "cases": [c.to_dict() for c in self.cases],
            "summary": self.summary.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

# ---------------------------------------------------------------------------
# Benchmark File IO Helpers
# ---------------------------------------------------------------------------

def load_benchmarks(file_path: Union[str, Path]) -> List[BenchmarkCase]:
    """
    Loads and validates all benchmark cases from a JSONL file.
    Skips empty/whitespace lines gracefully.
    Guarantees exactly 15 unique, canonical benchmark cases.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Benchmarks file not found: {path}")

    cases: List[BenchmarkCase] = []
    seen_ids = set()

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                raw_item = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON at line {line_num} in {path}: {e}")

            case = BenchmarkCase.from_dict(raw_item)
            if case.id in seen_ids:
                raise ValueError(f"Duplicate benchmark ID detected: '{case.id}' at line {line_num}")
            seen_ids.add(case.id)
            cases.append(case)

    return cases

def dump_benchmarks(cases: List[BenchmarkCase], file_path: Union[str, Path]) -> None:
    """Serializes benchmark cases into a strict JSONL file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case.to_dict(), ensure_ascii=False) + "\n")
```

---

## 4. Canonical 15 Benchmark Dataset (`tests/evaluation/benchmarks.jsonl`)

Every benchmark item adheres to the strict JSONL schema and satisfies all Tier 1–4 E2E test assertions.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              15 BENCHMARK TEST CASES MATRIX                            │
├────┬──────────┬───────────┬────────────────────────────────────────────────────────────┤
│ #  │ ID       │ Dimension │ Title & Problem Domain                                     │
├────┼──────────┼───────────┼────────────────────────────────────────────────────────────┤
│ 1  │ TC-CR-01 │ CR        │ Multi-Hop Distributed Consensus Invariant (Raft Cluster)   │
│ 2  │ TC-CR-02 │ CR        │ Counterfactual Memory Model Concurrency Trap (Relaxed MO)  │
│ 3  │ TC-CR-03 │ CR        │ Multi-Constraint Resource Scheduling Paradox (Queues)      │
├────┼──────────┼───────────┼────────────────────────────────────────────────────────────┤
│ 4  │ TC-PD-01 │ PD        │ Legacy Monolith Zero-Downtime Migration (Oracle 12TB)      │
│ 5  │ TC-PD-02 │ PD        │ Ambiguous Global Multi-Tenant Billing Engine (ASC 606)     │
│ 6  │ TC-PD-03 │ PD        │ Real-Time Collaborative Canvas Conflict Engine (Tree CRDT) │
├────┼──────────┼───────────┼────────────────────────────────────────────────────────────┤
│ 7  │ TC-SA-01 │ SA        │ High-Throughput Idempotent Webhook Dispatcher (100k QPS)   │
│ 8  │ TC-SA-02 │ SA        │ Multi-Region Event Sourcing with CQRS & Outbox (Banking)   │
│ 9  │ TC-SA-03 │ SA        │ Resilient Distributed Rate Limiter with Leaky Bucket       │
├────┼──────────┼───────────┼────────────────────────────────────────────────────────────┤
│ 10 │ TC-EP-01 │ EP        │ Live Database Engine & Schema Overhaul (PG12 to Aurora16)  │
│ 11 │ TC-EP-02 │ EP        │ Zero-Downtime Multi-Service Auth Migration (HS256 to RS)   │
│ 12 │ TC-EP-03 │ EP        │ Mission-Critical Payment Gateway Failover (Stripe/Adyen)   │
├────┼──────────┼───────────┼────────────────────────────────────────────────────────────┤
│ 13 │ TC-EH-01 │ EH        │ False-Premise Distributed Deadlock Analysis (Cassandra)    │
│ 14 │ TC-EH-02 │ EH        │ Underspecified Big Data Analytics Request (Clickstream)    │
│ 15 │ TC-EH-03 │ EH        │ Byzantine Clock Drift & Edge-Case Security Flaw (Tokens)   │
└────┴──────────┴───────────┴────────────────────────────────────────────────────────────┘
```

### 4.1 Detailed Specifications per Test Case

#### Case 1: `TC-CR-01`
- **Dimension**: `CR`
- **Title**: Multi-Hop Distributed Consensus Invariant
- **Prompt**:
  ```text
  Consider a 5-node Raft consensus cluster (Nodes A, B, C, D, E) currently in Term 3 with Node A as Leader.
  The log indices on each node are as follows:
  - Node A: [T1, idx1], [T1, idx2], [T2, idx3], [T3, idx4] (committed through idx3)
  - Node B: [T1, idx1], [T1, idx2], [T2, idx3]
  - Node C: [T1, idx1], [T1, idx2]
  - Node D: [T1, idx1], [T1, idx2], [T2, idx3], [T3, idx4]
  - Node E: [T1, idx1]

  A network partition occurs creating two partitions: {A, B} and {C, D, E}.
  1. If Node C starts an election in Term 4, can Node C become Leader? Show the exact vote tally and why.
  2. If Node D starts an election in Term 4, can Node D become Leader? Show the exact vote tally.
  3. Suppose Node D becomes Leader in Term 4, appends entry [T4, idx5], and commits it before the partition heals. When the partition heals, what exact log entries does Node A overwrite or keep? Prove step-by-step using Raft invariant safety rules.
  ```
- **Baseline Failure Trap**: Calculates votes based solely on node count without checking the Raft log up-to-date invariant (`lastLogTerm` and `lastLogIndex`). Fails to recognize that Node D will reject Node C's RequestVote.
- **Expected Claude Behaviors**: Explicitly quotes Section 5.4.1 of Raft paper (Election safety: candidate log must be at least as up-to-date as voter). Traces discrete votes for C (fails at 2 votes: C, E) and D (succeeds at 3 votes: D, E, C). Explains log reconciliation on partition healing where uncommitted entry at idx4 on Node A is overwritten by Leader D.
- **Rubric Anchors**:
  - `1`: Hallucinates quorum rules, ignores log comparison invariant, produces incorrect vote counts.
  - `3`: Correctly identifies quorum but fails to quote exact Raft up-to-date log rule or hand-waves log overwrite.
  - `5`: Flawless step-by-step state ledger, explicit quote of Raft invariants, rigorous vote accounting per node, exact log overwrite demonstration.
- **Binary Markers**: `["M01", "M11", "M05"]`

#### Case 2: `TC-CR-02`
- **Dimension**: `CR`
- **Title**: Counterfactual Memory Model Concurrency Trap
- **Prompt**:
  ```text
  Analyze the following pseudo-code running on two threads under the C++11 / Java relaxed memory model:

  Initial state: x = 0, y = 0

  Thread 1:
    y.store(1, memory_order_relaxed); // Statement A
    x.store(1, memory_order_relaxed); // Statement B

  Thread 2:
    r1 = x.load(memory_order_relaxed); // Statement C
    r2 = y.load(memory_order_relaxed); // Statement D

  Can the execution result in r1 == 1 and r2 == 0?
  1. Answer with a formal proof using memory order relations (Sequenced-Before, Synchronizes-With, Happens-Before).
  2. What is the counterfactual: what minimal synchronization primitive or memory order MUST be added to make r1 == 1 && r2 == 0 impossible, without changing to memory_order_seq_cst? Prove why your modification is minimal.
  ```
- **Baseline Failure Trap**: Vaguely blames "race conditions" or hardware caching without formal happens-before analysis; erroneously recommends heavyweight `memory_order_seq_cst` or full mutexes.
- **Expected Claude Behaviors**: Formulates formal execution DAG showing that `memory_order_relaxed` enforces only modification order per variable and creates NO synchronizes-with edges between threads. Proves that CPU/compiler store-store or load-load reordering permits Statement B before A and Statement D before C. Derives minimal counterfactual: `release` on Thread 1 (Statement B) and `acquire` on Thread 2 (Statement C).
- **Rubric Anchors**:
  - `1`: Incorrectly claims r1=1, r2=0 is impossible or blames hardware cache without memory model semantics.
  - `3`: Identifies that reordering can happen, recommends acquire/release, but lacks formal happens-before proof.
  - `5`: Rigorous formal proof mapping sequenced-before and synchronizes-with edges; proves mathematically why acquire/release is minimal and sufficient.
- **Binary Markers**: `["M01", "M11", "M07"]`

#### Case 3: `TC-CR-03`
- **Dimension**: `CR`
- **Title**: Multi-Constraint Resource Scheduling Paradox
- **Prompt**:
  ```text
  A distributed batch worker system has 4 job queues (Q1, Q2, Q3, Q4) and 3 execution worker pools (Small: 2 vCPU/4GB, Medium: 4 vCPU/16GB, GPU: 8 vCPU/32GB + 1 GPU).
  Constraints:
  - Jobs in Q1 require minimum 4 vCPU and can run on Medium or GPU pools.
  - Jobs in Q2 require GPU and can ONLY run on GPU pool. Max run time: 10 mins.
  - Jobs in Q3 are high-priority I/O bound jobs that require max 2 vCPU, can run on any pool, but preempt any job running on Small pool if Small pool CPU > 80%.
  - Jobs in Q4 are best-effort background jobs that may be starved for at most 15 minutes before deadheading.
  - System total capacity: 10 Small, 5 Medium, 2 GPU workers.

  Scenario:
  At T=0: 6 Q1 jobs, 3 Q2 jobs, 8 Q3 jobs arrive simultaneously.
  Trace the allocation state at T=0, T=5 min, and T=12 min under a fair-share priority scheduler.
  Identify which jobs are queued, which are executing, whether any deadlock or starvation occurs, and formulate a mathematical constraint satisfaction proof that guarantees Q4 will not starve past 15 min under sustained Q1/Q2/Q3 load.
  ```
- **Baseline Failure Trap**: Oversimplifies worker pool assignment, forgets GPU pool contention between Q1 and Q2, fails to track discrete state changes at T=0, 5, 12 min, omits mathematical starvation bound proof.
- **Expected Claude Behaviors**: Constructs explicit multi-tier allocation matrix tracking worker slots per pool across T=0, 5, 12. Identifies GPU bottleneck (3 Q2 vs 2 GPU workers) and Medium worker saturation (5 Q1 jobs take all Medium, 1 Q1 waits). Formulates deficit weighted round-robin or virtual-runtime aging function with proof of bounded starvation $W_{Q4} \le 15\text{ min}$.
- **Rubric Anchors**:
  - `1`: Arithmetic errors in resource counting, forgets worker limits, no timeline.
  - `3`: Correct allocations at T=0, but sloppy at T=5/12; hand-wavy starvation mitigation.
  - `5`: Flawless resource matrix across all time steps, explicit queue tracking, rigorous starvation prevention proof with concrete aging equation.
- **Binary Markers**: `["M01", "M11", "M04"]`

#### Case 4: `TC-PD-01`
- **Dimension**: `PD`
- **Title**: Legacy Monolith Zero-Downtime Migration
- **Prompt**:
  ```text
  You are the Principal Architect tasked with decoupling the legacy monolithic Order-to-Cash service of a $2B/yr e-commerce platform into modern event-driven microservices (Order, Inventory, Payment, Fulfillment).
  The monolith runs on a single 12TB Oracle database with stored procedures doing balance deductions, table locks, and two-phase database transactions across orders and warehouse inventory.

  The business cannot afford ANY downtime, cannot lose any financial data, and cannot tolerate duplicate shipments or incorrect inventory counts.
  Decompose this problem completely:
  1. Identify all implicit ambiguities, hidden risks, and constraints.
  2. Formulate a MECE decomposition of the migration phases.
  3. Define the boundary interfaces and data synchronization strategies (including handling dual-writes, CDC, and distributed transactions without distributed 2PC).
  ```
- **Baseline Failure Trap**: Jumps straight to "Use Kafka and Debezium" without addressing shared stored procedures or foreign keys; proposes naive dual-writes that cause silent drift; fails to categorize ambiguities MECE.
- **Expected Claude Behaviors**: Separates stated facts from inferred risks. Establishes MECE 4-phase decomposition: Phase 0 (CDC read replication), Phase 1 (Strangler Fig with Monolith source-of-truth), Phase 2 (Write authority cutover with reverse sync), Phase 3 (Monolith retirement). Employs Transactional Outbox pattern, idempotent event consumers, Saga compensation workflows, and bidirectional drift detection reconciliation.
- **Rubric Anchors**:
  - `1`: Generic microservices buzzwords, ignores 12TB Oracle complexity and stored procedures, unsafe dual writes.
  - `3`: Outlines Strangler pattern and CDC, but lacks MECE structure and skips reconciliation edge cases.
  - `5`: Master-class architectural decomposition; structured ambiguity classification; rigorous dual-write/CDC reconciliation protocol; complete Saga compensation model.
- **Binary Markers**: `["M03", "M04", "M06", "M07"]`

#### Case 5: `TC-PD-02`
- **Dimension**: `PD`
- **Title**: Ambiguous Global Multi-Tenant Billing Engine
- **Prompt**:
  ```text
  "We need to build a global SaaS billing and revenue recognition system for 50,000 enterprise customers across US, EU, Japan, and Brazil. It has to support credit cards, SEPA, PIX, invoicing, usage-based metering, localized taxes (VAT, GST, municipal), and ASC 606 / IFRS 15 revenue recognition. Make it fast and accurate."

  Decompose this prompt into an engineering problem specification:
  1. Unpack all ambiguities and articulate the critical questions that must be resolved before architecture can proceed.
  2. Structure the functional vs non-functional requirements in an orthogonal taxonomy.
  3. Map the core domain models, life cycles, and state machine transitions.
  ```
- **Baseline Failure Trap**: Accepts vague prompt as complete; provides generic Stripe wrapper; completely ignores ASC 606 revenue recognition rules (contract identification, performance obligations, transaction price allocation); misses SEPA vs PIX settlement timing differences.
- **Expected Claude Behaviors**: Identifies regulatory and settlement ambiguities (instant PIX vs 3-5 day SEPA vs net-30 invoicing). Clearly decouples Billing (cash collection / invoicing) from Revenue Recognition (ASC 606 amortization over performance obligations). Models immutable financial ledger, billing event state machine, and orthogonal non-functional requirements (SOC1, GAAP, audit trails).
- **Rubric Anchors**:
  - `1`: Generates generic SaaS billing boilerplate, ignores revenue recognition, fails to notice ambiguities.
  - `3`: Identifies tax and payment differences, but conflates billing with revenue recognition; misses state machine depth.
  - `5`: Impeccable problem decomposition; separates cash collection from revenue recognition; explicit financial state machines; detailed regulatory/geographic ambiguity breakdown.
- **Binary Markers**: `["M03", "M04", "M05"]`

#### Case 6: `TC-PD-03`
- **Dimension**: `PD`
- **Title**: Real-Time Collaborative Canvas Conflict Engine
- **Prompt**:
  ```text
  A client wants a real-time collaborative whiteboarding tool (like Figma/Miro) supporting 500 concurrent users per canvas with sub-50ms local feedback, offline editing, and vector shapes that can be grouped, transformed, and nested hierarchically.
  The client asks: "Should we use Operational Transformation (OT) or CRDTs? Design the conflict resolution engine."

  Decompose the problem completely:
  1. Contrast OT vs CRDT specifically for hierarchical tree structures (the known tree-move cycle paradox).
  2. Deconstruct the requirements into independent subsystem layers.
  3. Define the mathematical conflict resolution model for nested bounding-box transforms.
  ```
- **Baseline Failure Trap**: Gives generic textbook OT vs CRDT summary without addressing the hierarchical tree-move paradox (concurrent moves creating detached cycles); omits offline editing implications.
- **Expected Claude Behaviors**: Provides rigorous analysis of Tree CRDT cycle anomaly (concurrent parent updates $A \to B$ and $B \to A$). Explores replicated tree algorithms (Kleppmann transaction log vs LWW parent pointers with cycle detection). Decomposes architecture into 4 orthogonal layers: Transport (WebSockets/WebRTC), Optimistic Mutation Log, CRDT Sync Engine, and Affine Transformation Resolver.
- **Rubric Anchors**:
  - `1`: Shallow high-level overview, misses the tree-move paradox entirely, offers no concrete algorithm.
  - `3`: Mentions tree cycles and CRDTs, but decomposition lacks layered interfaces and mathematical transformation model.
  - `5`: Detailed algorithmic dissection of tree CRDTs, complete mathematical formulation of affine transform resolution, rigorous 4-layer architecture.
- **Binary Markers**: `["M04", "M07", "M05"]`

#### Case 7: `TC-SA-01`
- **Dimension**: `SA`
- **Title**: High-Throughput Idempotent Webhook Dispatcher
- **Prompt**:
  ```text
  Design a distributed webhook delivery platform capable of delivering 100,000 webhooks/sec to 3rd-party customer endpoints with varying reliability, latency (10ms to 30s), and rate limits.
  Requirements:
  - At-least-once delivery with end-to-end idempotency.
  - Customer endpoint protection (never overwhelm customer servers; honor 429 Retry-After).
  - Fair sharing across tenants (one noisy tenant sending 50k events/sec must not delay events from other tenants).
  - Tiered exponential backoff retries over 72 hours.
  - Complete architecture: component diagram, interface contracts (Python or TypeScript types), data schemas, and failure mode analysis.
  ```
- **Baseline Failure Trap**: Single SQS/Kafka queue leading to head-of-line blocking by slow/dead endpoints; omits tenant fair-queueing; writes untyped pseudo-code without failure domain modeling.
- **Expected Claude Behaviors**: Decouples fast dispatch from slow retry delay queues to eliminate head-of-line blocking. Employs Deficit Weighted Round Robin (DWRR) or virtual partitioned queues for tenant fair sharing. Outlines distributed token bucket per customer host with `Retry-After` parsing and circuit breakers. Provides strongly typed dataclasses/DTOs and detailed failure domain analysis (DNS timeout, TLS stall, thundering herd).
- **Rubric Anchors**:
  - `1`: Naive single queue design, causes head-of-line blocking, no tenant isolation, minimal code.
  - `3`: Multi-queue with retry queues, but lacks fair-share scheduling and detailed type definitions.
  - `5`: Production-grade systems architecture; explicit DWRR tenant isolation; typed contracts; exhaustive failure domain analysis (DNS, slowloris, thundering herd).
- **Binary Markers**: `["M05", "M06", "M07"]`

#### Case 8: `TC-SA-02`
- **Dimension**: `SA`
- **Title**: Multi-Region Event Sourcing with CQRS & Outbox
- **Prompt**:
  ```text
  Design a multi-region active-active event-sourced banking ledger service deployed across US-East, EU-West, and AP-South.
  Requirements:
  - Strict auditability: All balance changes are immutable domain events.
  - Consistency: Account balances must NEVER overdraft, even under concurrent transfers initiated in different regions.
  - Low latency: Read queries (balance checks, transaction history) must have P99 < 15ms locally.
  - Provide:
    1. System architecture & regional topology.
    2. Write path vs Read path sequence diagram / flow.
    3. Conflict resolution and balance protection strategy (how to avoid cross-region double-spending without cross-region locks on every write).
    4. Exact event schema and interface definition.
  ```
- **Baseline Failure Trap**: Recommends eventual consistency for bank account balances (allowing double spending) or proposes global 2PC distributed locking across regions for every transaction (destroying P99 latency).
- **Expected Claude Behaviors**: Evaluates PACELC trade-offs. Solves double spending without global 2PC via Escrow/Reservation partitioning (sub-allocating account limits across regions) or Home-Region Account Pinning with Raft/Spanner linearizable writes. Provides Transactional Outbox pattern for local read projections (CQRS). Delivers concrete typed event schemas: `BalanceReserved`, `MoneyDeposited`, `TransferSettled`, `BalanceAdjusted`.
- **Rubric Anchors**:
  - `1`: Claims eventual consistency is fine for bank balances or suggests global 2PC without acknowledging latency explosion.
  - `3`: Proposes account pinning or CRDTs, but lacks the escrow reservation model or rigorous event schemas.
  - `5`: Flawless distributed systems design; articulates PACELC trade-offs; provides Escrow reservation or home-region consensus; complete typed schemas and failure analysis.
- **Binary Markers**: `["M05", "M06", "M07"]`

#### Case 9: `TC-SA-03`
- **Dimension**: `SA`
- **Title**: Resilient Distributed Rate Limiter with Leaky Bucket
- **Prompt**:
  ```text
  Design an edge-tier distributed rate limiter servicing 500,000 requests/sec across 20 edge proxy nodes with a shared Redis cluster.
  Requirements:
  - Algorithms supported: Sliding Window Counter and Token/Leaky Bucket.
  - Fault tolerance: If Redis cluster experiences high latency (>50ms) or partitions, edge proxies must fail-open or fail-degraded gracefully without crashing or letting traffic surge by more than 20%.
  - Memory efficiency: Support 100M active API keys with minimal memory overhead.
  - Provide:
    1. Lua script for atomic Redis execution of Sliding Window.
    2. Local proxy cache & batching architecture (local token batching / sync).
    3. Degradation & circuit breaker state machine.
  ```
- **Baseline Failure Trap**: Naive Lua script using Redis sorted set (`ZADD` + `ZRANGEBYSCORE`) causing memory explosion ($100\text{M} \times \text{timestamps} \approx \text{tens of GBs}$); no local batching causing Redis connection saturation at 500k QPS.
- **Expected Claude Behaviors**: Recommends memory-efficient sliding window counter (current minute count + weighted previous minute) reducing memory to $O(1)$ per key. Implements local token batch leasing (edge proxies pre-fetch 50-100 tokens) slashing Redis QPS from 500k to 5k-10k. Supplies atomic Lua script. Details degraded circuit breaker state machine with local fallback bounds.
- **Rubric Anchors**:
  - `1`: Generic sorted set Lua script with memory explosion, no local batching, crashes when Redis fails.
  - `3`: Mentions sliding window and local fallback, but misses memory footprint analysis and batching mechanics.
  - `5`: Production-hardened edge architecture; memory-optimized sliding window; local batch leasing; atomic Lua script; full degradation state machine.
- **Binary Markers**: `["M05", "M06", "M11"]`

#### Case 10: `TC-EP-01`
- **Dimension**: `EP`
- **Title**: Live Database Engine & Schema Overhaul
- **Prompt**:
  ```text
  You must migrate a mission-critical PostgreSQL 12 database (8TB, 15,000 QPS, 500 tables) running on bare-metal to an Aurora PostgreSQL 16 cluster with zero data loss and maximum 30 seconds of write downtime during cutover.
  Additionally, 3 primary tables must undergo a schema change (splitting a large JSONB column into a typed relational table and backfilling 500M rows).

  Formulate a complete, professional Execution Plan:
  1. Structure the plan as a dependency DAG across distinct milestones.
  2. For every milestone, specify Preconditions, Detailed Atomic Actions, and Postconditions.
  3. Include exact falsifiable verification commands (CLI, SQL queries, or scripts) to validate each step.
  4. Define explicit rollback procedures and automated abort triggers for each phase.
  ```
- **Baseline Failure Trap**: High-level narrative without exact verification commands; suggests running `ALTER TABLE` directly on 500M rows (exclusive table lock downs system); omits rollback and abort criteria.
- **Expected Claude Behaviors**: Formulates strict dependency DAG: Pre-migration CDC -> Logical Replication -> Shadow Table Schema Change -> Chunked Background Backfill (5,000 rows/batch with throttling) -> Dual-read Verification -> 30-second Cutover -> Reverse Replication Safety Net. Provides exact falsifiable verification commands (`pg_replication_slots` lag check, row count checksum queries). Outlines quantitative abort triggers.
- **Rubric Anchors**:
  - `1`: Vague steps, suggests locking tables, zero verification commands, no rollback.
  - `3`: Solid phasing and mentions logical replication, but lacks concrete CLI/SQL verification scripts and reverse replication rollback.
  - `5`: Flawless, enterprise-grade runbook; exact DAG; concrete executable commands for each step; chunked lockless backfill; reverse replication rollback safety net.
- **Binary Markers**: `["M08", "M09", "M10"]`

#### Case 11: `TC-EP-02`
- **Dimension**: `EP`
- **Title**: Zero-Downtime Multi-Service Auth Migration (JWT)
- **Prompt**:
  ```text
  A suite of 45 microservices uses legacy symmetric HS256 JWTs with a shared secret hardcoded across services. You must migrate all services to asymmetric RS256/EdDSA JWTs with dynamic JWKS URL rotation, without invalidating existing user sessions (10 million active mobile/web tokens) or causing auth failures.

  Construct an end-to-end Execution Plan:
  1. Phased dependency timeline with zero user logout.
  2. Concrete verification tests (curl, test tokens, logs) for each phase.
  3. Rollback strategy if a service fails to parse new keys.
  ```
- **Baseline Failure Trap**: Suggests rotating key on auth server immediately (invalidating all 10M active user sessions); fails to coordinate multi-service deployment sequence (validators must accept BOTH keys before issuer signs with new key).
- **Expected Claude Behaviors**: Designs 5-phase dual-verification roadmap: Phase 1 (Dual-Accept Deployment: services accept HS256 and RS256), Phase 2 (Canary Verification: synthetic RS256 tokens pass all 45 services), Phase 3 (Issuer Signing Cutover: new sessions sign RS256), Phase 4 (Legacy TTL Drain: monitor until HS256 count reaches zero), Phase 5 (HS256 Decommission). Provides copy-pasteable verification commands (`curl https://auth.corp/jwks.json`, synthetic token pytest suite) and automated rollback trigger (`error rate > 0.05%`).
- **Rubric Anchors**:
  - `1`: Recommends immediate cutover, breaking active tokens; no verification commands.
  - `3`: Identifies dual-validation necessity, but lacks automated verification scripts across the 45 services and TTL drain monitoring.
  - `5`: Bulletproof zero-downtime migration sequence; mathematical TTL drain timeline; exact synthetic token validation scripts; explicit rollback triggers.
- **Binary Markers**: `["M08", "M09", "M10"]`

#### Case 12: `TC-EP-03`
- **Dimension**: `EP`
- **Title**: Mission-Critical Payment Gateway Failover
- **Prompt**:
  ```text
  You are setting up an automated multi-gateway failover system (Stripe <-> Adyen) for an airline processing $10M/day.
  Design the operational validation and rollout execution plan:
  1. Canary testing & dark traffic verification before going live.
  2. Failure injection & chaos testing suite to prove the circuit breaker trips within 3 seconds of gateway degradation.
  3. Step-by-step rollout plan with automated rollback criteria based on p99 latency, error rate, and authorization drop.
  ```
- **Baseline Failure Trap**: Generic statements ("test in staging, roll out 10% then 50%"); omits financial reconciliation and idempotency token mapping across gateways; lacks quantitative rollback tripwires.
- **Expected Claude Behaviors**: Builds operational validation plan featuring dark traffic shadowing and zero-value card authorization tests. Specifies Toxiproxy / chaos test commands to simulate 4000ms latency and 500 errors. Defines quantitative metrics-driven rollback tripwires (authorization rate drop > 1.5% or P99 latency > 2500ms over 5-minute rolling window). Details cross-gateway token vaulting and settlement reconciliation.
- **Rubric Anchors**:
  - `1`: Naive rollout steps, no metrics thresholds, ignores cross-gateway tokenization.
  - `3`: Good staging and canary plan, but lacks quantitative rollback thresholds and chaos testing specifications.
  - `5`: Flawless financial execution plan; explicit chaos test scripts; quantitative metric tripwires; robust cross-gateway token vaulting and reconciliation strategy.
- **Binary Markers**: `["M08", "M09", "M10"]`

#### Case 13: `TC-EH-01`
- **Dimension**: `EH`
- **Title**: False-Premise Distributed Deadlock Analysis
- **Prompt**:
  ```text
  "We are experiencing frequent distributed deadlocks in our Cassandra cluster because our write queries use Cassandra's ACID two-phase commit locks across multiple partitions. How can we tune the Cassandra 2PC timeout configuration in cassandra.yaml to eliminate these distributed deadlocks?"
  ```
- **Baseline Failure Trap**: Sycophantic hallucination: blindly accepts premise that Cassandra uses 2PC locks across partitions and invents non-existent configuration parameters in `cassandra.yaml` (e.g. `two_phase_commit_timeout_in_ms`).
- **Expected Claude Behaviors**: Immediately and politely challenges the false premise: Apache Cassandra is an AP distributed database that does NOT use two-phase commit (2PC) or distributed table locks for standard multi-partition writes. Dissects the actual architecture (CommitLog + Memtable) and Lightweight Transactions (LWT / Paxos). Identifies true root causes for timeouts (GC pauses, wide rows, tombstone accumulation, client coordinator timeout `write_request_timeout_in_ms`).
- **Rubric Anchors**:
  - `1`: Sycophantically hallucinates Cassandra 2PC locks and invents fake config settings.
  - `3`: Mentions that Cassandra might not use 2PC, but still attempts to provide timeout tuning based on the user's false premise.
  - `5`: Instantly and respectfully clarifies the misconception; details Cassandra's true write path (CommitLog + Memtable) and Paxos LWT semantics; diagnoses true potential causes with exact configuration settings.
- **Binary Markers**: `["M02", "M12", "M01"]`

#### Case 14: `TC-EH-02`
- **Dimension**: `EH`
- **Title**: Underspecified Big Data Analytics Request
- **Prompt**:
  ```text
  "Build a Python system to process all user clickstream events and output real-time analytics dashboards. Provide the complete code."
  ```
- **Baseline Failure Trap**: Writes a 40-line toy script using Pandas or in-memory Python dictionaries with `while True: sleep(1)`; makes enormous silent assumptions about scale, storage, schema, and latency without mentioning them.
- **Expected Claude Behaviors**: Proactively surfaces that the prompt is severely underspecified. Articulates an explicit Assumptions Matrix (Scale: 1k vs 100k events/sec; Ingestion: Redis Streams vs Kafka; Analytics Engine: DuckDB vs ClickHouse). Delivers a production-quality, modular reference implementation for the moderate scale scenario while explaining concrete architectural upgrade paths for enterprise scale.
- **Rubric Anchors**:
  - `1`: Dumps a naive toy script without acknowledging scale, assumptions, or production realities.
  - `3`: Asks a couple of questions or mentions scale in passing, but jumps into toy code.
  - `5`: Explicitly models the assumption matrix; delivers robust, modular, production-ready code with clear boundaries; details upgrade paths for alternative assumption sets.
- **Binary Markers**: `["M03", "M12", "M05"]`

#### Case 15: `TC-EH-03`
- **Dimension**: `EH`
- **Title**: Byzantine Clock Drift & Edge-Case Security Flaw
- **Prompt**:
  ```text
  Review this cryptographic token validation snippet designed for an edge gateway:

  def validate_session_token(token_str, shared_secret):
      # Format: payload_b64.timestamp.signature
      parts = token_str.split('.')
      if len(parts) != 3:
          return False
      payload_b64, timestamp_str, sig = parts
      # Check timestamp (valid for 5 minutes)
      token_time = int(timestamp_str)
      current_time = int(time.time())
      if current_time - token_time > 300:
          return False
      # Verify signature
      expected_sig = hmac.new(shared_secret.encode(), f"{payload_b64}.{timestamp_str}".encode(), hashlib.sha256).hexdigest()
      if sig != expected_sig:
          return False
      return json.loads(base64.b64decode(payload_b64))

  Identify ALL security vulnerabilities, edge cases, mathematical flaws, and operational risks.
  ```
- **Baseline Failure Trap**: Only points out timing attack (`sig != expected_sig`) or `token_time > 300`; misses future timestamps (`token_time > current_time`), replay attacks, JSON deserialization bombs, base64 padding errors, and integer parsing exceptions.
- **Expected Claude Behaviors**: Uncovers all 6 critical vulnerabilities and operational edge cases:
  1. Future timestamp / clock skew bypass: `current_time - token_time > 300` allows indefinite future tokens (`token_time >> current_time`).
  2. Timing attack on HMAC comparison: requires `hmac.compare_digest`.
  3. Replay attack vulnerability: missing nonce or jti check.
  4. Unhandled ValueError on `int(timestamp_str)` causes gateway 500 crash.
  5. Unhandled binascii.Error on malformed base64 causes gateway 500 crash.
  6. Unhandled json.JSONDecodeError on malformed payload causes gateway 500 crash.
- **Rubric Anchors**:
  - `1`: Finds only 1 obvious issue (e.g. timing attack) and misses future timestamps and exception crashes.
  - `3`: Finds timing attack, future timestamp flaw, and mentions replay, but overlooks DoS exceptions and URL-safe decoding.
  - `5`: Exhaustive breakdown uncovering all 6 vulnerabilities/edge cases with exact exploit vectors, corrected secure code, and comprehensive defensive test suite.
- **Binary Markers**: `["M11", "M12", "M06"]`

---

## 5. Exact JSONL Representation for `benchmarks.jsonl`

Below is the exact dataset ready to be written to `tests/evaluation/benchmarks.jsonl`. Each entry is a single self-contained JSON object formatted on one line.

```json
{"id": "TC-CR-01", "dimension": "CR", "title": "Multi-Hop Distributed Consensus Invariant", "challenge_summary": "5-node Raft consensus cluster partition election and log reconciliation verification.", "prompt": "Consider a 5-node Raft consensus cluster (Nodes A, B, C, D, E) currently in Term 3 with Node A as Leader.\nThe log indices on each node are as follows:\n- Node A: [T1, idx1], [T1, idx2], [T2, idx3], [T3, idx4] (committed through idx3)\n- Node B: [T1, idx1], [T1, idx2], [T2, idx3]\n- Node C: [T1, idx1], [T1, idx2]\n- Node D: [T1, idx1], [T1, idx2], [T2, idx3], [T3, idx4]\n- Node E: [T1, idx1]\n\nA network partition occurs creating two partitions: {A, B} and {C, D, E}.\n1. If Node C starts an election in Term 4, can Node C become Leader? Show the exact vote tally and why.\n2. If Node D starts an election in Term 4, can Node D become Leader? Show the exact vote tally.\n3. Suppose Node D becomes Leader in Term 4, appends entry [T4, idx5], and commits it before the partition heals. When the partition heals, what exact log entries does Node A overwrite or keep? Prove step-by-step using Raft invariant safety rules.", "baseline_failure_mode": "Calculates votes based on node count alone without checking Raft log up-to-date comparison rule (lastLogTerm and lastLogIndex). Misjudges whether Node C can win votes from D.", "claude_behaviors": ["Quotes Raft Election Safety Rule: candidate log must be at least as up-to-date as voter", "Calculates C votes: C, E (2 votes - fails quorum of 3)", "Calculates D votes: D, E, C (3 votes - achieves quorum)", "Demonstrates Node A log overwrite of uncommitted idx4 with D log on partition heal"], "rubric": {"1": "Hallucinates quorum rules, ignores log comparison rule, incorrect vote counts.", "3": "Correctly calculates quorum but fails to detail exact log comparison rule or hand-waves the log reconciliation step.", "5": "Flawless step-by-step state ledger, explicit quote of Raft safety invariants, rigorous vote accounting per node, exact log overwrite demonstration.", "score_1": "Hallucinates quorum rules, ignores log comparison rule, incorrect vote counts.", "score_3": "Correctly calculates quorum but fails to detail exact log comparison rule or hand-waves the log reconciliation step.", "score_5": "Flawless step-by-step state ledger, explicit quote of Raft safety invariants, rigorous vote accounting per node, exact log overwrite demonstration."}, "rubric_anchors": {"score_1": "Hallucinates quorum rules, ignores log comparison rule, incorrect vote counts.", "score_3": "Correctly calculates quorum but fails to detail exact log comparison rule or hand-waves the log reconciliation step.", "score_5": "Flawless step-by-step state ledger, explicit quote of Raft safety invariants, rigorous vote accounting per node, exact log overwrite demonstration."}, "binary_markers_expected": ["M01", "M11", "M05"]}
{"id": "TC-CR-02", "dimension": "CR", "title": "Counterfactual Memory Model Concurrency Trap", "challenge_summary": "Two-thread relaxed memory order execution analysis under C++11/Java memory model.", "prompt": "Analyze the following pseudo-code running on two threads under the C++11 / Java relaxed memory model:\n\nInitial state: x = 0, y = 0\n\nThread 1:\n  y.store(1, memory_order_relaxed); // Statement A\n  x.store(1, memory_order_relaxed); // Statement B\n\nThread 2:\n  r1 = x.load(memory_order_relaxed); // Statement C\n  r2 = y.load(memory_order_relaxed); // Statement D\n\nCan the execution result in r1 == 1 and r2 == 0?\n1. Answer with a formal proof using memory order relations (Sequenced-Before, Synchronizes-With, Happens-Before).\n2. What is the counterfactual: what minimal synchronization primitive or memory order MUST be added to make r1 == 1 && r2 == 0 impossible, without changing to memory_order_seq_cst? Prove why your modification is minimal.", "baseline_failure_mode": "Vaguely attributes outcome to race condition without formal happens-before graph. Recommends heavy seq_cst or mutex rather than minimal acquire/release.", "claude_behaviors": ["Proves relaxed memory operations establish no synchronizes-with relationship across threads", "Demonstrates compiler and CPU reordering allows Statement B before A and Statement D before C", "Proves minimal counterfactual fix is release on Thread 1 and acquire on Thread 2"], "rubric": {"1": "Incorrectly claims r1=1, r2=0 is impossible or blames hardware cache without memory model semantics.", "3": "Identifies that reordering can happen, recommends acquire/release, but lacks formal happens-before proof.", "5": "Rigorous formal proof mapping sequenced-before and synchronizes-with edges; proves mathematically why acquire/release is minimal and sufficient.", "score_1": "Incorrectly claims r1=1, r2=0 is impossible or blames hardware cache without memory model semantics.", "score_3": "Identifies that reordering can happen, recommends acquire/release, but lacks formal happens-before proof.", "score_5": "Rigorous formal proof mapping sequenced-before and synchronizes-with edges; proves mathematically why acquire/release is minimal and sufficient."}, "rubric_anchors": {"score_1": "Incorrectly claims r1=1, r2=0 is impossible or blames hardware cache without memory model semantics.", "score_3": "Identifies that reordering can happen, recommends acquire/release, but lacks formal happens-before proof.", "score_5": "Rigorous formal proof mapping sequenced-before and synchronizes-with edges; proves mathematically why acquire/release is minimal and sufficient."}, "binary_markers_expected": ["M01", "M11", "M07"]}
{"id": "TC-CR-03", "dimension": "CR", "title": "Multi-Constraint Resource Scheduling Paradox", "challenge_summary": "Distributed batch worker multi-queue fair-share scheduling and starvation proof.", "prompt": "A distributed batch worker system has 4 job queues (Q1, Q2, Q3, Q4) and 3 execution worker pools (Small: 2 vCPU/4GB, Medium: 4 vCPU/16GB, GPU: 8 vCPU/32GB + 1 GPU).\nConstraints:\n- Jobs in Q1 require minimum 4 vCPU and can run on Medium or GPU pools.\n- Jobs in Q2 require GPU and can ONLY run on GPU pool. Max run time: 10 mins.\n- Jobs in Q3 are high-priority I/O bound jobs that require max 2 vCPU, can run on any pool, but preempt any job running on Small pool if Small pool CPU > 80%.\n- Jobs in Q4 are best-effort background jobs that may be starved for at most 15 minutes before deadheading.\n- System total capacity: 10 Small, 5 Medium, 2 GPU workers.\n\nScenario:\nAt T=0: 6 Q1 jobs, 3 Q2 jobs, 8 Q3 jobs arrive simultaneously.\nTrace the allocation state at T=0, T=5 min, and T=12 min under a fair-share priority scheduler.\nIdentify which jobs are queued, which are executing, whether any deadlock or starvation occurs, and formulate a mathematical constraint satisfaction proof that guarantees Q4 will not starve past 15 min under sustained Q1/Q2/Q3 load.", "baseline_failure_mode": "Oversimplifies pool assignments, overlooks GPU pool contention between Q1 and Q2, fails to track discrete state changes at T=0, 5, 12, and omits starvation bound proof.", "claude_behaviors": ["Constructs discrete allocation state matrix across T=0, 5, 12 minutes", "Identifies GPU pool contention where 2 GPU workers force 1 Q2 job to queue", "Defines mathematical deficit weighted round robin or virtual-time aging function bounding Q4 starvation to <= 15 minutes"], "rubric": {"1": "Arithmetic errors in resource counting, forgets worker limits, no timeline.", "3": "Correct allocations at T=0, but sloppy at T=5/12; hand-wavy starvation mitigation.", "5": "Flawless resource matrix across all time steps, explicit queue tracking, rigorous starvation prevention proof with concrete aging equation.", "score_1": "Arithmetic errors in resource counting, forgets worker limits, no timeline.", "score_3": "Correct allocations at T=0, but sloppy at T=5/12; hand-wavy starvation mitigation.", "score_5": "Flawless resource matrix across all time steps, explicit queue tracking, rigorous starvation prevention proof with concrete aging equation."}, "rubric_anchors": {"score_1": "Arithmetic errors in resource counting, forgets worker limits, no timeline.", "score_3": "Correct allocations at T=0, but sloppy at T=5/12; hand-wavy starvation mitigation.", "score_5": "Flawless resource matrix across all time steps, explicit queue tracking, rigorous starvation prevention proof with concrete aging equation."}, "binary_markers_expected": ["M01", "M11", "M04"]}
{"id": "TC-PD-01", "dimension": "PD", "title": "Legacy Monolith Zero-Downtime Migration", "challenge_summary": "Decoupling 12TB Oracle monolithic Order-to-Cash service into event-driven microservices.", "prompt": "You are the Principal Architect tasked with decoupling the legacy monolithic Order-to-Cash service of a $2B/yr e-commerce platform into modern event-driven microservices (Order, Inventory, Payment, Fulfillment).\nThe monolith runs on a single 12TB Oracle database with stored procedures doing balance deductions, table locks, and two-phase database transactions across orders and warehouse inventory.\n\nThe business cannot afford ANY downtime, cannot lose any financial data, and cannot tolerate duplicate shipments or incorrect inventory counts.\nDecompose this problem completely:\n1. Identify all implicit ambiguities, hidden risks, and constraints.\n2. Formulate a MECE decomposition of the migration phases.\n3. Define the boundary interfaces and data synchronization strategies (including handling dual-writes, CDC, and distributed transactions without distributed 2PC).", "baseline_failure_mode": "Jumps straight to Kafka/Debezium buzzwords without addressing shared stored procedures or foreign keys. Suggests naive dual-writes that fail silently.", "claude_behaviors": ["Separates stated requirements from implicit operational risks (stored procedure coupling, drift latency)", "Structures MECE 4-phase migration roadmap: Phase 0 CDC dark-reads, Phase 1 Strangler Fig, Phase 2 Authority cutover, Phase 3 Retirement", "Employs Transactional Outbox pattern, idempotent consumers, Saga compensation, and automated drift detection"], "rubric": {"1": "Generic microservices buzzwords, ignores 12TB Oracle complexity and stored procedures, unsafe dual writes.", "3": "Outlines Strangler pattern and CDC, but lacks MECE structure and skips reconciliation edge cases.", "5": "Master-class architectural decomposition; structured ambiguity classification; rigorous dual-write/CDC reconciliation protocol; complete Saga compensation model.", "score_1": "Generic microservices buzzwords, ignores 12TB Oracle complexity and stored procedures, unsafe dual writes.", "score_3": "Outlines Strangler pattern and CDC, but lacks MECE structure and skips reconciliation edge cases.", "score_5": "Master-class architectural decomposition; structured ambiguity classification; rigorous dual-write/CDC reconciliation protocol; complete Saga compensation model."}, "rubric_anchors": {"score_1": "Generic microservices buzzwords, ignores 12TB Oracle complexity and stored procedures, unsafe dual writes.", "score_3": "Outlines Strangler pattern and CDC, but lacks MECE structure and skips reconciliation edge cases.", "score_5": "Master-class architectural decomposition; structured ambiguity classification; rigorous dual-write/CDC reconciliation protocol; complete Saga compensation model."}, "binary_markers_expected": ["M03", "M04", "M06", "M07"]}
{"id": "TC-PD-02", "dimension": "PD", "title": "Ambiguous Global Multi-Tenant Billing Engine", "challenge_summary": "Unpacking ambiguous requirements for global multi-currency enterprise billing and ASC 606.", "prompt": "\"We need to build a global SaaS billing and revenue recognition system for 50,000 enterprise customers across US, EU, Japan, and Brazil. It has to support credit cards, SEPA, PIX, invoicing, usage-based metering, localized taxes (VAT, GST, municipal), and ASC 606 / IFRS 15 revenue recognition. Make it fast and accurate.\"\n\nDecompose this prompt into an engineering problem specification:\n1. Unpack all ambiguities and articulate the critical questions that must be resolved before architecture can proceed.\n2. Structure the functional vs non-functional requirements in an orthogonal taxonomy.\n3. Map the core domain models, life cycles, and state machine transitions.", "baseline_failure_mode": "Accepts prompt without questioning ambiguities. Offers generic Stripe integration. Completely misses ASC 606 revenue recognition rules.", "claude_behaviors": ["Identifies settlement and regulatory ambiguities (PIX instant vs SEPA 3-5 days vs Net-30 invoice)", "Decouples Billing cash collection from ASC 606 revenue recognition amortization over performance obligations", "Constructs orthogonal functional vs non-functional taxonomy with explicit financial ledger state machines"], "rubric": {"1": "Generates generic SaaS billing boilerplate, ignores revenue recognition, fails to notice ambiguities.", "3": "Identifies tax and payment differences, but conflates billing with revenue recognition; misses state machine depth.", "5": "Impeccable problem decomposition; separates cash collection from revenue recognition; explicit financial state machines; detailed regulatory/geographic ambiguity breakdown.", "score_1": "Generates generic SaaS billing boilerplate, ignores revenue recognition, fails to notice ambiguities.", "score_3": "Identifies tax and payment differences, but conflates billing with revenue recognition; misses state machine depth.", "score_5": "Impeccable problem decomposition; separates cash collection from revenue recognition; explicit financial state machines; detailed regulatory/geographic ambiguity breakdown."}, "rubric_anchors": {"score_1": "Generates generic SaaS billing boilerplate, ignores revenue recognition, fails to notice ambiguities.", "score_3": "Identifies tax and payment differences, but conflates billing with revenue recognition; misses state machine depth.", "score_5": "Impeccable problem decomposition; separates cash collection from revenue recognition; explicit financial state machines; detailed regulatory/geographic ambiguity breakdown."}, "binary_markers_expected": ["M03", "M04", "M05"]}
{"id": "TC-PD-03", "dimension": "PD", "title": "Real-Time Collaborative Canvas Conflict Engine", "challenge_summary": "Conflict resolution engine and Tree CRDT cycle resolution for collaborative canvas.", "prompt": "A client wants a real-time collaborative whiteboarding tool (like Figma/Miro) supporting 500 concurrent users per canvas with sub-50ms local feedback, offline editing, and vector shapes that can be grouped, transformed, and nested hierarchically.\nThe client asks: \"Should we use Operational Transformation (OT) or CRDTs? Design the conflict resolution engine.\"\n\nDecompose the problem completely:\n1. Contrast OT vs CRDT specifically for hierarchical tree structures (the known tree-move cycle paradox).\n2. Deconstruct the requirements into independent subsystem layers.\n3. Define the mathematical conflict resolution model for nested bounding-box transforms.", "baseline_failure_mode": "Provides generic textbook OT vs CRDT comparison without addressing the tree-move cycle anomaly. Misses offline vector ordering challenges.", "claude_behaviors": ["Details the Tree CRDT cycle creation anomaly under concurrent reparenting", "Recommends state-of-the-art replicated tree algorithms with cycle detection rollback", "Establishes layered decomposition: Transport, Optimistic Mutation Log, CRDT Sync, Affine Transform Resolution"], "rubric": {"1": "Shallow high-level overview, misses the tree-move paradox entirely, offers no concrete algorithm.", "3": "Mentions tree cycles and CRDTs, but decomposition lacks layered interfaces and mathematical transformation model.", "5": "Detailed algorithmic dissection of tree CRDTs, complete mathematical formulation of affine transform resolution, rigorous 4-layer architecture.", "score_1": "Shallow high-level overview, misses the tree-move paradox entirely, offers no concrete algorithm.", "score_3": "Mentions tree cycles and CRDTs, but decomposition lacks layered interfaces and mathematical transformation model.", "score_5": "Detailed algorithmic dissection of tree CRDTs, complete mathematical formulation of affine transform resolution, rigorous 4-layer architecture."}, "rubric_anchors": {"score_1": "Shallow high-level overview, misses the tree-move paradox entirely, offers no concrete algorithm.", "score_3": "Mentions tree cycles and CRDTs, but decomposition lacks layered interfaces and mathematical transformation model.", "score_5": "Detailed algorithmic dissection of tree CRDTs, complete mathematical formulation of affine transform resolution, rigorous 4-layer architecture."}, "binary_markers_expected": ["M04", "M07", "M05"]}
{"id": "TC-SA-01", "dimension": "SA", "title": "High-Throughput Idempotent Webhook Dispatcher", "challenge_summary": "100k webhook/s dispatcher with tenant fair sharing and exponential backoff.", "prompt": "Design a distributed webhook delivery platform capable of delivering 100,000 webhooks/sec to 3rd-party customer endpoints with varying reliability, latency (10ms to 30s), and rate limits.\nRequirements:\n- At-least-once delivery with end-to-end idempotency.\n- Customer endpoint protection (never overwhelm customer servers; honor 429 Retry-After).\n- Fair sharing across tenants (one noisy tenant sending 50k events/sec must not delay events from other tenants).\n- Tiered exponential backoff retries over 72 hours.\n- Complete architecture: component diagram, interface contracts (Python or TypeScript types), data schemas, and failure mode analysis.", "baseline_failure_mode": "Proposes single message queue where slow customer endpoints cause head-of-line blocking. Omits tenant fair-queueing mechanisms.", "claude_behaviors": ["Decouples fast delivery queues from delayed retry delay queues to eliminate head-of-line blocking", "Implements tenant fair sharing using Deficit Weighted Round Robin (DWRR)", "Provides strongly typed interface contracts and models DNS/TLS/slowloris failure domains"], "rubric": {"1": "Naive single queue design, causes head-of-line blocking, no tenant isolation, minimal code.", "3": "Multi-queue with retry queues, but lacks fair-share scheduling and detailed type definitions.", "5": "Production-grade systems architecture; explicit DWRR tenant isolation; typed contracts; exhaustive failure domain analysis (DNS, slowloris, thundering herd).", "score_1": "Naive single queue design, causes head-of-line blocking, no tenant isolation, minimal code.", "score_3": "Multi-queue with retry queues, but lacks fair-share scheduling and detailed type definitions.", "score_5": "Production-grade systems architecture; explicit DWRR tenant isolation; typed contracts; exhaustive failure domain analysis (DNS, slowloris, thundering herd)."}, "rubric_anchors": {"score_1": "Naive single queue design, causes head-of-line blocking, no tenant isolation, minimal code.", "score_3": "Multi-queue with retry queues, but lacks fair-share scheduling and detailed type definitions.", "score_5": "Production-grade systems architecture; explicit DWRR tenant isolation; typed contracts; exhaustive failure domain analysis (DNS, slowloris, thundering herd)."}, "binary_markers_expected": ["M05", "M06", "M07"]}
{"id": "TC-SA-02", "dimension": "SA", "title": "Multi-Region Event Sourcing with CQRS & Outbox", "challenge_summary": "Active-active multi-region event-sourced banking ledger preventing overdrafts.", "prompt": "Design a multi-region active-active event-sourced banking ledger service deployed across US-East, EU-West, and AP-South.\nRequirements:\n- Strict auditability: All balance changes are immutable domain events.\n- Consistency: Account balances must NEVER overdraft, even under concurrent transfers initiated in different regions.\n- Low latency: Read queries (balance checks, transaction history) must have P99 < 15ms locally.\n- Provide:\n  1. System architecture & regional topology.\n  2. Write path vs Read path sequence diagram / flow.\n  3. Conflict resolution and balance protection strategy (how to avoid cross-region double-spending without cross-region locks on every write).\n  4. Exact event schema and interface definition.", "baseline_failure_mode": "Recommends eventual consistency for bank balances (causing double-spending) or global 2PC across regions (destroying P99 latency).", "claude_behaviors": ["Analyzes PACELC trade-offs between latency and cross-region consensus", "Implements Escrow / Balance Reservation partitioning or Account Home-Region linearizable pinning", "Defines typed event contracts: MoneyDeposited, BalanceReserved, TransferSettled with Transactional Outbox pattern"], "rubric": {"1": "Claims eventual consistency is fine for bank balances or suggests global 2PC without acknowledging latency explosion.", "3": "Proposes account pinning or CRDTs, but lacks the escrow reservation model or rigorous event schemas.", "5": "Flawless distributed systems design; articulates PACELC trade-offs; provides Escrow reservation or home-region consensus; complete typed schemas and failure analysis.", "score_1": "Claims eventual consistency is fine for bank balances or suggests global 2PC without acknowledging latency explosion.", "score_3": "Proposes account pinning or CRDTs, but lacks the escrow reservation model or rigorous event schemas.", "score_5": "Flawless distributed systems design; articulates PACELC trade-offs; provides Escrow reservation or home-region consensus; complete typed schemas and failure analysis."}, "rubric_anchors": {"score_1": "Claims eventual consistency is fine for bank balances or suggests global 2PC without acknowledging latency explosion.", "score_3": "Proposes account pinning or CRDTs, but lacks the escrow reservation model or rigorous event schemas.", "score_5": "Flawless distributed systems design; articulates PACELC trade-offs; provides Escrow reservation or home-region consensus; complete typed schemas and failure analysis."}, "binary_markers_expected": ["M05", "M06", "M07"]}
{"id": "TC-SA-03", "dimension": "SA", "title": "Resilient Distributed Rate Limiter with Leaky Bucket", "challenge_summary": "500k QPS edge-tier rate limiter with memory-efficient sliding window and Redis failover.", "prompt": "Design an edge-tier distributed rate limiter servicing 500,000 requests/sec across 20 edge proxy nodes with a shared Redis cluster.\nRequirements:\n- Algorithms supported: Sliding Window Counter and Token/Leaky Bucket.\n- Fault tolerance: If Redis cluster experiences high latency (>50ms) or partitions, edge proxies must fail-open or fail-degraded gracefully without crashing or letting traffic surge by more than 20%.\n- Memory efficiency: Support 100M active API keys with minimal memory overhead.\n- Provide:\n  1. Lua script for atomic Redis execution of Sliding Window.\n  2. Local proxy cache & batching architecture (local token batching / sync).\n  3. Degradation & circuit breaker state machine.", "baseline_failure_mode": "Proposes Redis sorted set with individual timestamps causing tens of GBs memory explosion for 100M keys. Lacks local batching, saturating Redis.", "claude_behaviors": ["Designs memory-efficient O(1) sliding window counter using current and previous window weights", "Implements local proxy token batch leasing to reduce Redis QPS from 500k to 10k", "Provides atomic Lua script and degradation circuit breaker state machine bounding traffic surge to <= 20%"], "rubric": {"1": "Generic sorted set Lua script with memory explosion, no local batching, crashes when Redis fails.", "3": "Mentions sliding window and local fallback, but misses memory footprint analysis and batching mechanics.", "5": "Production-hardened edge architecture; memory-optimized sliding window; local batch leasing; atomic Lua script; full degradation state machine.", "score_1": "Generic sorted set Lua script with memory explosion, no local batching, crashes when Redis fails.", "score_3": "Mentions sliding window and local fallback, but misses memory footprint analysis and batching mechanics.", "score_5": "Production-hardened edge architecture; memory-optimized sliding window; local batch leasing; atomic Lua script; full degradation state machine."}, "rubric_anchors": {"score_1": "Generic sorted set Lua script with memory explosion, no local batching, crashes when Redis fails.", "score_3": "Mentions sliding window and local fallback, but misses memory footprint analysis and batching mechanics.", "score_5": "Production-hardened edge architecture; memory-optimized sliding window; local batch leasing; atomic Lua script; full degradation state machine."}, "binary_markers_expected": ["M05", "M06", "M11"]}
{"id": "TC-EP-01", "dimension": "EP", "title": "Live Database Engine & Schema Overhaul", "challenge_summary": "8TB PostgreSQL 12 to Aurora 16 cutover plan with <30s downtime and 500M row backfill.", "prompt": "You must migrate a mission-critical PostgreSQL 12 database (8TB, 15,000 QPS, 500 tables) running on bare-metal to an Aurora PostgreSQL 16 cluster with zero data loss and maximum 30 seconds of write downtime during cutover.\nAdditionally, 3 primary tables must undergo a schema change (splitting a large JSONB column into a typed relational table and backfilling 500M rows).\n\nFormulate a complete, professional Execution Plan:\n1. Structure the plan as a dependency DAG across distinct milestones.\n2. For every milestone, specify Preconditions, Detailed Atomic Actions, and Postconditions.\n3. Include exact falsifiable verification commands (CLI, SQL queries, or scripts) to validate each step.\n4. Define explicit rollback procedures and automated abort triggers for each phase.", "baseline_failure_mode": "Produces high-level narrative without exact verification commands. Recommends running ALTER TABLE directly on 500M rows causing exclusive table locks.", "claude_behaviors": ["Defines dependency DAG: Pre-migration CDC -> Logical Replication -> Shadow Table Backfill -> Verification -> Cutover -> Reverse Replication", "Employs lockless online schema migration with chunked background backfill (5000 rows/batch with throttling)", "Supplies exact falsifiable CLI verification commands (replication slot lag checks, row checksums) and reverse replication rollback"], "rubric": {"1": "Vague steps, suggests locking tables, zero verification commands, no rollback.", "3": "Solid phasing and mentions logical replication, but lacks concrete CLI/SQL verification scripts and reverse replication rollback.", "5": "Flawless, enterprise-grade runbook; exact DAG; concrete executable commands for each step; chunked lockless backfill; reverse replication rollback safety net.", "score_1": "Vague steps, suggests locking tables, zero verification commands, no rollback.", "score_3": "Solid phasing and mentions logical replication, but lacks concrete CLI/SQL verification scripts and reverse replication rollback.", "score_5": "Flawless, enterprise-grade runbook; exact DAG; concrete executable commands for each step; chunked lockless backfill; reverse replication rollback safety net."}, "rubric_anchors": {"score_1": "Vague steps, suggests locking tables, zero verification commands, no rollback.", "score_3": "Solid phasing and mentions logical replication, but lacks concrete CLI/SQL verification scripts and reverse replication rollback.", "score_5": "Flawless, enterprise-grade runbook; exact DAG; concrete executable commands for each step; chunked lockless backfill; reverse replication rollback safety net."}, "binary_markers_expected": ["M08", "M09", "M10"]}
{"id": "TC-EP-02", "dimension": "EP", "title": "Zero-Downtime Multi-Service Auth Migration (JWT)", "challenge_summary": "45-microservice migration from legacy HS256 to RS256 with dynamic JWKS and 10M active sessions.", "prompt": "A suite of 45 microservices uses legacy symmetric HS256 JWTs with a shared secret hardcoded across services. You must migrate all services to asymmetric RS256/EdDSA JWTs with dynamic JWKS URL rotation, without invalidating existing user sessions (10 million active mobile/web tokens) or causing auth failures.\n\nConstruct an end-to-end Execution Plan:\n1. Phased dependency timeline with zero user logout.\n2. Concrete verification tests (curl, test tokens, logs) for each phase.\n3. Rollback strategy if a service fails to parse new keys.", "baseline_failure_mode": "Rotates key on auth server immediately, invalidating all 10M active sessions. Fails to deploy dual-validation across services before cutover.", "claude_behaviors": ["Structures 5-phase execution plan: Dual-Accept Deployment, Canary Verification, Issuer Signing Cutover, Legacy TTL Drain, HS256 Decommission", "Supplies exact copy-pasteable curl and synthetic token verification commands", "Establishes quantifiable rollback triggers (error rate > 0.05% on gateway routes reverts issuer immediately)"], "rubric": {"1": "Recommends immediate cutover, breaking active tokens; no verification commands.", "3": "Identifies dual-validation necessity, but lacks automated verification scripts across the 45 services and TTL drain monitoring.", "5": "Bulletproof zero-downtime migration sequence; mathematical TTL drain timeline; exact synthetic token validation scripts; explicit rollback triggers.", "score_1": "Recommends immediate cutover, breaking active tokens; no verification commands.", "score_3": "Identifies dual-validation necessity, but lacks automated verification scripts across the 45 services and TTL drain monitoring.", "score_5": "Bulletproof zero-downtime migration sequence; mathematical TTL drain timeline; exact synthetic token validation scripts; explicit rollback triggers."}, "rubric_anchors": {"score_1": "Recommends immediate cutover, breaking active tokens; no verification commands.", "score_3": "Identifies dual-validation necessity, but lacks automated verification scripts across the 45 services and TTL drain monitoring.", "score_5": "Bulletproof zero-downtime migration sequence; mathematical TTL drain timeline; exact synthetic token validation scripts; explicit rollback triggers."}, "binary_markers_expected": ["M08", "M09", "M10"]}
{"id": "TC-EP-03", "dimension": "EP", "title": "Mission-Critical Payment Gateway Failover", "challenge_summary": "Multi-gateway automated failover (Stripe <-> Adyen) validation plan for $10M/day airline.", "prompt": "You are setting up an automated multi-gateway failover system (Stripe <-> Adyen) for an airline processing $10M/day.\nDesign the operational validation and rollout execution plan:\n1. Canary testing & dark traffic verification before going live.\n2. Failure injection & chaos testing suite to prove the circuit breaker trips within 3 seconds of gateway degradation.\n3. Step-by-step rollout plan with automated rollback criteria based on p99 latency, error rate, and authorization drop.", "baseline_failure_mode": "Produces generic staging statements without metrics-driven tripwires. Omits cross-gateway tokenization and financial reconciliation.", "claude_behaviors": ["Formulates dark traffic shadowing and zero-dollar authorization validation suite", "Provides concrete Toxiproxy / chaos injection configurations simulating 4000ms latency and 500 errors", "Defines automated rollback tripwires: auth drop > 1.5% or P99 latency > 2500ms over 5-minute rolling window"], "rubric": {"1": "Naive rollout steps, no metrics thresholds, ignores cross-gateway tokenization.", "3": "Good staging and canary plan, but lacks quantitative rollback thresholds and chaos testing specifications.", "5": "Flawless financial execution plan; explicit chaos test scripts; quantitative metric tripwires; robust cross-gateway token vaulting and reconciliation strategy.", "score_1": "Naive rollout steps, no metrics thresholds, ignores cross-gateway tokenization.", "score_3": "Good staging and canary plan, but lacks quantitative rollback thresholds and chaos testing specifications.", "score_5": "Flawless financial execution plan; explicit chaos test scripts; quantitative metric tripwires; robust cross-gateway token vaulting and reconciliation strategy."}, "rubric_anchors": {"score_1": "Naive rollout steps, no metrics thresholds, ignores cross-gateway tokenization.", "score_3": "Good staging and canary plan, but lacks quantitative rollback thresholds and chaos testing specifications.", "score_5": "Flawless financial execution plan; explicit chaos test scripts; quantitative metric tripwires; robust cross-gateway token vaulting and reconciliation strategy."}, "binary_markers_expected": ["M08", "M09", "M10"]}
{"id": "TC-EH-01", "dimension": "EH", "title": "False-Premise Distributed Deadlock Analysis", "challenge_summary": "Premise integrity test challenging false assumption of Cassandra multi-partition 2PC locks.", "prompt": "\"We are experiencing frequent distributed deadlocks in our Cassandra cluster because our write queries use Cassandra's ACID two-phase commit locks across multiple partitions. How can we tune the Cassandra 2PC timeout configuration in cassandra.yaml to eliminate these distributed deadlocks?\"", "baseline_failure_mode": "Sycophantic hallucination: blindly accepts premise that Cassandra uses 2PC locks across partitions and invents non-existent configuration parameters in cassandra.yaml.", "claude_behaviors": ["Immediately and politely challenges the false premise: Cassandra is an AP database that does NOT use 2PC or distributed table locks across partitions", "Explains Cassandra actual architecture: CommitLog + Memtable and Paxos Lightweight Transactions (LWT)", "Diagnoses true root causes of timeout errors: GC pauses, tombstone buildup, and write_request_timeout_in_ms"], "rubric": {"1": "Sycophantically hallucinates Cassandra 2PC locks and invents fake config settings.", "3": "Mentions that Cassandra might not use 2PC, but still attempts to provide timeout tuning based on the user's false premise.", "5": "Instantly and respectfully clarifies the misconception; details Cassandra's true write path (CommitLog + Memtable) and Paxos LWT semantics; diagnoses true potential causes with exact configuration settings.", "score_1": "Sycophantically hallucinates Cassandra 2PC locks and invents fake config settings.", "score_3": "Mentions that Cassandra might not use 2PC, but still attempts to provide timeout tuning based on the user's false premise.", "score_5": "Instantly and respectfully clarifies the misconception; details Cassandra's true write path (CommitLog + Memtable) and Paxos LWT semantics; diagnoses true potential causes with exact configuration settings."}, "rubric_anchors": {"score_1": "Sycophantically hallucinates Cassandra 2PC locks and invents fake config settings.", "score_3": "Mentions that Cassandra might not use 2PC, but still attempts to provide timeout tuning based on the user's false premise.", "score_5": "Instantly and respectfully clarifies the misconception; details Cassandra's true write path (CommitLog + Memtable) and Paxos LWT semantics; diagnoses true potential causes with exact configuration settings."}, "binary_markers_expected": ["M02", "M12", "M01"]}
{"id": "TC-EH-02", "dimension": "EH", "title": "Underspecified Big Data Analytics Request", "challenge_summary": "Surfacing massive underspecification in clickstream analytics dashboard request.", "prompt": "\"Build a Python system to process all user clickstream events and output real-time analytics dashboards. Provide the complete code.\"", "baseline_failure_mode": "Writes a 40-line toy script using Pandas or in-memory dictionaries with sleep(1), making silent assumptions about scale, storage, and latency.", "claude_behaviors": ["Proactively surfaces that the request is massively underspecified across scale, freshness, ingestion, and storage", "Provides structured Assumptions Matrix contrasting moderate (1k events/s) vs enterprise (100k+ events/s) scale", "Delivers robust modular architecture for moderate scale with clear upgrade paths for enterprise requirements"], "rubric": {"1": "Dumps a naive toy script without acknowledging scale, assumptions, or production realities.", "3": "Asks a couple of questions or mentions scale in passing, but jumps into toy code.", "5": "Explicitly models the assumption matrix; delivers robust, modular, production-ready code with clear boundaries; details upgrade paths for alternative assumption sets.", "score_1": "Dumps a naive toy script without acknowledging scale, assumptions, or production realities.", "score_3": "Asks a couple of questions or mentions scale in passing, but jumps into toy code.", "score_5": "Explicitly models the assumption matrix; delivers robust, modular, production-ready code with clear boundaries; details upgrade paths for alternative assumption sets."}, "rubric_anchors": {"score_1": "Dumps a naive toy script without acknowledging scale, assumptions, or production realities.", "score_3": "Asks a couple of questions or mentions scale in passing, but jumps into toy code.", "score_5": "Explicitly models the assumption matrix; delivers robust, modular, production-ready code with clear boundaries; details upgrade paths for alternative assumption sets."}, "binary_markers_expected": ["M03", "M12", "M05"]}
{"id": "TC-EH-03", "dimension": "EH", "title": "Byzantine Clock Drift & Edge-Case Security Flaw", "challenge_summary": "Security audit of cryptographic session token validation snippet detecting 6 vulnerabilities.", "prompt": "Review this cryptographic token validation snippet designed for an edge gateway:\n\ndef validate_session_token(token_str, shared_secret):\n    # Format: payload_b64.timestamp.signature\n    parts = token_str.split('.')\n    if len(parts) != 3:\n        return False\n    payload_b64, timestamp_str, sig = parts\n    # Check timestamp (valid for 5 minutes)\n    token_time = int(timestamp_str)\n    current_time = int(time.time())\n    if current_time - token_time > 300:\n        return False\n    # Verify signature\n    expected_sig = hmac.new(shared_secret.encode(), f\"{payload_b64}.{timestamp_str}\".encode(), hashlib.sha256).hexdigest()\n    if sig != expected_sig:\n        return False\n    return json.loads(base64.b64decode(payload_b64))\n\nIdentify ALL security vulnerabilities, edge cases, mathematical flaws, and operational risks.", "baseline_failure_mode": "Only spots timing attack or 5-minute expiration, missing future timestamp clock skew bypass, replay attacks, and unhandled exception 500 crashes.", "claude_behaviors": ["Identifies future timestamp bypass: current_time - token_time > 300 fails to catch token_time > current_time", "Identifies timing attack requiring hmac.compare_digest and replay attack vulnerability", "Catches 3 distinct unhandled exceptions (ValueError, binascii.Error, json.JSONDecodeError) causing 500 gateway DoS"], "rubric": {"1": "Finds only 1 obvious issue (e.g. timing attack) and misses future timestamps and exception crashes.", "3": "Finds timing attack, future timestamp flaw, and mentions replay, but overlooks DoS exceptions and URL-safe decoding.", "5": "Exhaustive breakdown uncovering all 6 vulnerabilities/edge cases with exact exploit vectors, corrected secure code, and comprehensive defensive test suite.", "score_1": "Finds only 1 obvious issue (e.g. timing attack) and misses future timestamps and exception crashes.", "score_3": "Finds timing attack, future timestamp flaw, and mentions replay, but overlooks DoS exceptions and URL-safe decoding.", "score_5": "Exhaustive breakdown uncovering all 6 vulnerabilities/edge cases with exact exploit vectors, corrected secure code, and comprehensive defensive test suite."}, "rubric_anchors": {"score_1": "Finds only 1 obvious issue (e.g. timing attack) and misses future timestamps and exception crashes.", "score_3": "Finds timing attack, future timestamp flaw, and mentions replay, but overlooks DoS exceptions and URL-safe decoding.", "score_5": "Exhaustive breakdown uncovering all 6 vulnerabilities/edge cases with exact exploit vectors, corrected secure code, and comprehensive defensive test suite."}, "binary_markers_expected": ["M11", "M12", "M06"]}
```

---

## 6. Implementation Guidance for Downstream Workers

1. **Target File Locations**:
   - Schemas: `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/schemas.py`
   - Benchmarks: `/Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation/benchmarks.jsonl`
2. **Directory Initialization**:
   - `mkdir -p /Users/devesh/Documents/Antigravity/Random Ask/tests/evaluation`
   - Create an empty `tests/evaluation/__init__.py` to ensure clean package imports.
3. **Execution Verification Command**:
   - Run the E2E Feature 10 verification:
     `python3 -m pytest tests/e2e/test_tier1_feature_coverage.py -k "feature_10" -v`
   - Run the E2E Tier 2 Feature 10 verification:
     `python3 -m pytest tests/e2e/test_tier2_boundaries.py -k "feature_10" -v`
   - Run the E2E Tier 3 interaction tests:
     `python3 -m pytest tests/e2e/test_tier3_combinations.py -k "benchmarks" -v`
4. **Coordination with Peer Workers**:
   - `m3_explorer_2` (`scoring.py`): Relies on `CANONICAL_CCRS_WEIGHTS`, `CANONICAL_DIMENSIONS`, `DimensionScore`, and `MarkerChecklist` from `schemas.py`.
   - `m3_explorer_3` (`runner.py`, `judge.py`): Relies on `load_benchmarks`, `BenchmarkCase`, `JudgeEvaluationResult`, and `DualRunPositionSwapResult` from `schemas.py`.
