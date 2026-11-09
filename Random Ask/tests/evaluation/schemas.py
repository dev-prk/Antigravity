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
        if not self.score_1 or not str(self.score_1).strip():
            raise ValueError("Rubric anchor for score 1 must be a non-empty string.")
        if not self.score_3 or not str(self.score_3).strip():
            raise ValueError("Rubric anchor for score 3 must be a non-empty string.")
        if not self.score_5 or not str(self.score_5).strip():
            raise ValueError("Rubric anchor for score 5 must be a non-empty string.")

    def to_dict(self, dual_format: bool = True) -> Dict[str, str]:
        """Returns rubric dictionary with both numeric string and score_X keys if dual_format is True."""
        res = {
            "score_1": str(self.score_1).strip(),
            "score_3": str(self.score_3).strip(),
            "score_5": str(self.score_5).strip(),
        }
        if dual_format:
            res["1"] = res["score_1"]
            res["3"] = res["score_3"]
            res["5"] = res["score_5"]
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RubricAnchors":
        if not isinstance(data, dict):
            raise TypeError(f"Rubric must be a dictionary, got {type(data)}")
        s1 = data.get("score_1") or data.get("1")
        s3 = data.get("score_3") or data.get("3")
        s5 = data.get("score_5") or data.get("5")
        if not s1 or not str(s1).strip():
            raise ValueError("Missing score 1 anchor ('1' or 'score_1')")
        if not s3 or not str(s3).strip():
            raise ValueError("Missing score 3 anchor ('3' or 'score_3')")
        if not s5 or not str(s5).strip():
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
        if self.dimension == "CR" and len(self.prompt) <= 100:
            raise ValueError(f"CR benchmark prompt '{self.id}' must exceed 100 chars for constraint quoting, got {len(self.prompt)}")

        # 4. Rubric Validation
        anchors = RubricAnchors.from_dict(self.rubric)
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
            if not isinstance(val, (int, float)) or isinstance(val, bool) or math.isnan(val):
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
        resolved = {}
        for dim in CANONICAL_DIMENSIONS:
            val = data.get(dim)
            if val is None:
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
            self.markers = {f"M{i:02d}": 0 for i in range(1, 13)}
        if len(self.markers) != 12:
            raise ValueError(f"Expected exactly 12 markers, got {len(self.markers)}")
        for i in range(1, 13):
            m_id = f"M{i:02d}"
            if m_id not in self.markers:
                raise ValueError(f"Missing marker: {m_id}")
            val = self.markers[m_id]
            if isinstance(val, bool) or val not in (0, 1):
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
        if "response_a" not in self.scores or "response_b" not in self.scores:
            raise ValueError("Judge output 'scores' must contain 'response_a' and 'response_b'")
        DimensionScore.from_dict(self.scores["response_a"])
        DimensionScore.from_dict(self.scores["response_b"])

        if "response_a" not in self.behavioral_checklist or "response_b" not in self.behavioral_checklist:
            raise ValueError("Judge output 'behavioral_checklist' must contain 'response_a' and 'response_b'")
        MarkerChecklist.from_dict(self.behavioral_checklist["response_a"])
        MarkerChecklist.from_dict(self.behavioral_checklist["response_b"])

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
    pass1_forward: JudgeEvaluationResult
    pass2_reverse: JudgeEvaluationResult
    win_rate_b: float
    position_bias_detected: bool

    @classmethod
    def compute(
        cls, pass1: JudgeEvaluationResult, pass2: JudgeEvaluationResult
    ) -> "DualRunPositionSwapResult":
        if pass1.pairwise_preference == "B_better":
            p1_b = 1.0
        elif pass1.pairwise_preference == "tie":
            p1_b = 0.5
        else:
            p1_b = 0.0

        if pass2.pairwise_preference == "A_better":
            p2_b = 1.0
        elif pass2.pairwise_preference == "tie":
            p2_b = 0.5
        else:
            p2_b = 0.0

        win_rate = (p1_b + p2_b) / 2.0

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
    Guarantees unique, canonical benchmark cases.
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
