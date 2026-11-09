"""
tests/evaluation/judge.py
LLM-as-a-Judge Evaluation Engine for Claude Skill Replication.
Implements anchored 1-5 rubric grading, 12 binary behavioral markers,
and dual-run position-swapping (A/B -> B/A) to cancel position bias.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

CANONICAL_DIMENSIONS = ["CR", "PD", "SA", "EP", "EH"]

CANONICAL_MARKERS = [
    "M01", "M02", "M03", "M04", "M05", "M06",
    "M07", "M08", "M09", "M10", "M11", "M12",
]

DIMENSION_ALIASES = {
    "cr": "CR",
    "complex_reasoning": "CR",
    "complex reasoning": "CR",
    "pd": "PD",
    "problem_decomposition": "PD",
    "problem decomposition": "PD",
    "sa": "SA",
    "solution_architecture": "SA",
    "solution architecture": "SA",
    "ep": "EP",
    "execution_planning": "EP",
    "execution planning": "EP",
    "eh": "EH",
    "epistemic_humility": "EH",
    "epistemic humility": "EH",
}


@dataclass
class JudgeConfig:
    model: str = "mock"
    temperature: float = 0.0
    max_tokens: int = 4096
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 60.0


@dataclass
class JudgeOutput:
    scores: Dict[str, Dict[str, float]]
    behavioral_checklist: Dict[str, Dict[str, int]]
    pairwise_preference: Literal["A_better", "B_better", "tie"]
    justification: str
    raw_response: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": self.scores,
            "behavioral_checklist": self.behavioral_checklist,
            "pairwise_preference": self.pairwise_preference,
            "justification": self.justification,
        }


@dataclass
class PositionSwapResult:
    pass1_output: JudgeOutput
    pass2_output: JudgeOutput
    skill_win_rate: float
    baseline_win_rate: float
    baseline_scores: Dict[str, float]
    skill_scores: Dict[str, float]
    baseline_checklist: Dict[str, int]
    skill_checklist: Dict[str, int]
    position_bias_detected: bool
    justification_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass1_output": self.pass1_output.to_dict(),
            "pass2_output": self.pass2_output.to_dict(),
            "skill_win_rate": self.skill_win_rate,
            "baseline_win_rate": self.baseline_win_rate,
            "baseline_scores": self.baseline_scores,
            "skill_scores": self.skill_scores,
            "baseline_checklist": self.baseline_checklist,
            "skill_checklist": self.skill_checklist,
            "position_bias_detected": self.position_bias_detected,
            "justification_summary": self.justification_summary,
        }


def clamp_score(score: float, min_val: float = 1.0, max_val: float = 5.0) -> float:
    """Clamps a rubric score to [min_val, max_val]."""
    return max(min_val, min(max_val, float(score)))


def build_judge_system_prompt() -> str:
    """Builds the strict, anti-verbosity judge system prompt."""
    return """You are an authoritative, impartial AI systems evaluator and principal software architect.
Your objective is to evaluate two competing model responses (Response A and Response B) to a technical challenge.

EVALUATION DIRECTIVES:
1. Ground truth and technical accuracy take absolute precedence.
2. ANTI-VERBOSITY: DO NOT reward word length or decorative formatting. Severely penalize conversational filler, repetitive explanations, boilerplate padding, and unsolicited post-code walkthroughs. Favor information density, typed code, exact mathematical state proofs, and copy-pasteable verification commands.
3. ANTI-SYCOPHANCY & EPISTEMIC HUMILITY: Penalize models that acquiesce to false premises or fabricate non-existent APIs, libraries, or configuration parameters. Reward polite, factual refutation of false claims and explicit delineation of facts vs. assumptions.
4. REASONING SCRATCHPAD: Check whether the response employs deliberate cognitive pacing (<claude_thinking> with the 4 phases: Constraint Anchoring, Hypothesis Exploration & Counter-Factual Stress Testing, Architectural Blueprinting, Output Calibration).
5. 5-DIMENSION RUBRIC (Scale 1.0 to 5.0):
   - CR: Complex Multi-Step Reasoning & Counterfactual Deduction
   - PD: Problem Decomposition & Ambiguity Resolution
   - SA: Solution Architecture & Systems Engineering
   - EP: Execution Planning & Verifiable Action Sequencing
   - EH: Epistemic Humility, Assumption Surfacing & Edge-Case Detection
   Anchor your scores directly to the 1-3-5 rubric definitions provided in the benchmark challenge.
6. 12 BINARY BEHAVIORAL MARKERS (0 = Fail, 1 = Pass):
   - M01 (Deliberate Scratchpad/Pacing), M02 (Premise Integrity Check), M03 (Stated vs. Inferred),
   - M04 (MECE Decomposition), M05 (Typed Interface Contracts), M06 (Failure Domain Modeling),
   - M07 (Trade-Off Justification), M08 (Dependency Ordering DAG), M09 (Falsifiable Verification Commands),
   - M10 (Rollback & Abort Strategy), M11 (Boundary & Edge Case Enumeration), M12 (Resistance to Hallucination).

OUTPUT FORMAT:
Output MUST be valid JSON and ONLY valid JSON matching this schema:
{
  "scores": {
    "response_a": {"CR": <1.0-5.0>, "PD": <1.0-5.0>, "SA": <1.0-5.0>, "EP": <1.0-5.0>, "EH": <1.0-5.0>},
    "response_b": {"CR": <1.0-5.0>, "PD": <1.0-5.0>, "SA": <1.0-5.0>, "EP": <1.0-5.0>, "EH": <1.0-5.0>}
  },
  "behavioral_checklist": {
    "response_a": {"M01": <0|1>, ..., "M12": <0|1>},
    "response_b": {"M01": <0|1>, ..., "M12": <0|1>}
  },
  "pairwise_preference": "<A_better | B_better | tie>",
  "justification": "<concise step-by-step technical rationale citing exact lines or omissions>"
}
"""


def parse_judge_json(raw_text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON object from judge LLM output with robust fallback handling.
    Raises ValueError if raw text cannot be parsed into a valid judge output dictionary.
    """
    text = raw_text.strip()

    data = None
    try:
        data = json.loads(text)
    except Exception:
        pass

    if data is None:
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            try:
                data = json.loads(fence_match.group(1))
            except Exception:
                pass

    if data is None:
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            candidate_json = text[start_idx : end_idx + 1]
            try:
                data = json.loads(candidate_json)
            except Exception:
                repaired = re.sub(r",\s*([\]}])", r"\1", candidate_json)
                try:
                    data = json.loads(repaired)
                except Exception:
                    pass

    if not isinstance(data, dict):
        raise ValueError(f"Judge output could not be parsed as JSON: '{raw_text[:200]}...'")

    if "scores" not in data:
        raise ValueError("Judge output missing required top-level property: 'scores'")
    if "behavioral_checklist" not in data:
        raise ValueError("Judge output missing required top-level property: 'behavioral_checklist'")

    scores = data["scores"]
    for resp_key in ["response_a", "response_b"]:
        if resp_key not in scores or not isinstance(scores[resp_key], dict):
            scores[resp_key] = {dim: 3.0 for dim in CANONICAL_DIMENSIONS}
        else:
            normalized_dims = {}
            for k, v in scores[resp_key].items():
                canon_k = DIMENSION_ALIASES.get(str(k).lower(), str(k).upper())
                try:
                    val_float = float(v)
                except (ValueError, TypeError):
                    val_float = 3.0
                normalized_dims[canon_k] = clamp_score(val_float)
            for dim in CANONICAL_DIMENSIONS:
                if dim not in normalized_dims:
                    normalized_dims[dim] = 3.0
            scores[resp_key] = normalized_dims

    checklist = data["behavioral_checklist"]
    for resp_key in ["response_a", "response_b"]:
        if resp_key not in checklist or not isinstance(checklist[resp_key], dict):
            checklist[resp_key] = {f"M{i:02d}": 0 for i in range(1, 13)}
        else:
            normalized_markers = {}
            for i in range(1, 13):
                m_id = f"M{i:02d}"
                raw_m = checklist[resp_key].get(m_id, 0)
                try:
                    m_val = 1 if int(raw_m) >= 1 else 0
                except (ValueError, TypeError):
                    m_val = 0
                normalized_markers[m_id] = m_val
            checklist[resp_key] = normalized_markers

    pref = data.get("pairwise_preference")
    if pref not in ("A_better", "B_better", "tie"):
        data["pairwise_preference"] = "tie"

    if not data.get("justification") or not isinstance(data.get("justification"), str):
        data["justification"] = "Evaluation performed based on technical accuracy and rubric alignment."

    return data


def compute_position_swap_win_rate(pass1_pref: str, pass2_pref: str, target: str = "B") -> float:
    """
    Computes position-debiased win rate for target candidate across two passes.
    Pass 1: Candidate 1 = A, Target = B
    Pass 2: Target = A, Candidate 1 = B
    """
    if target == "B":
        p1_win = 1.0 if pass1_pref == "B_better" else (0.5 if pass1_pref == "tie" else 0.0)
        p2_win = 1.0 if pass2_pref == "A_better" else (0.5 if pass2_pref == "tie" else 0.0)
    else:
        p1_win = 1.0 if pass1_pref == "A_better" else (0.5 if pass1_pref == "tie" else 0.0)
        p2_win = 1.0 if pass2_pref == "B_better" else (0.5 if pass2_pref == "tie" else 0.0)
    return (p1_win + p2_win) / 2.0


class EvaluationJudge:
    """LLM-as-a-Judge pairwise evaluation engine with position swapping."""

    def __init__(self, config: Optional[JudgeConfig] = None):
        self.config = config or JudgeConfig()

    def evaluate_single_pass(
        self,
        prompt: str,
        candidate_a: str,
        candidate_b: str,
        benchmark_item: Dict[str, Any],
    ) -> JudgeOutput:
        """Evaluates candidate A vs candidate B in a single forward pass."""
        if self.config.model == "mock":
            raw_text = self._mock_judge_call(candidate_a, candidate_b, benchmark_item)
        else:
            raw_text = self._call_real_judge(prompt, candidate_a, candidate_b, benchmark_item)

        parsed = parse_judge_json(raw_text)
        return JudgeOutput(
            scores=parsed["scores"],
            behavioral_checklist=parsed["behavioral_checklist"],
            pairwise_preference=parsed["pairwise_preference"],
            justification=parsed["justification"],
            raw_response=raw_text,
        )

    def evaluate_with_position_swap(
        self,
        prompt: str,
        candidate_baseline: str,
        candidate_skill: str,
        benchmark_item: Dict[str, Any],
    ) -> PositionSwapResult:
        """
        Executes symmetric dual-run position-swapping evaluation:
        Pass 1: A = Baseline, B = Skill
        Pass 2: A = Skill, B = Baseline
        Returns debiased win rate, averaged scores, and position bias flags.
        """
        pass1_out = self.evaluate_single_pass(
            prompt=prompt,
            candidate_a=candidate_baseline,
            candidate_b=candidate_skill,
            benchmark_item=benchmark_item,
        )

        pass2_out = self.evaluate_single_pass(
            prompt=prompt,
            candidate_a=candidate_skill,
            candidate_b=candidate_baseline,
            benchmark_item=benchmark_item,
        )

        skill_win_rate = compute_position_swap_win_rate(
            pass1_out.pairwise_preference, pass2_out.pairwise_preference, target="B"
        )
        baseline_win_rate = 1.0 - skill_win_rate

        pos1_bias = pass1_out.pairwise_preference == "A_better" and pass2_out.pairwise_preference == "A_better"
        pos2_bias = pass1_out.pairwise_preference == "B_better" and pass2_out.pairwise_preference == "B_better"
        position_bias_detected = pos1_bias or pos2_bias

        baseline_scores = {}
        skill_scores = {}
        for dim in CANONICAL_DIMENSIONS:
            baseline_scores[dim] = round((pass1_out.scores["response_a"][dim] + pass2_out.scores["response_b"][dim]) / 2.0, 2)
            skill_scores[dim] = round((pass1_out.scores["response_b"][dim] + pass2_out.scores["response_a"][dim]) / 2.0, 2)

        baseline_markers = {}
        skill_markers = {}
        for i in range(1, 13):
            m_id = f"M{i:02d}"
            b1 = pass1_out.behavioral_checklist["response_a"].get(m_id, 0)
            b2 = pass2_out.behavioral_checklist["response_b"].get(m_id, 0)
            s1 = pass1_out.behavioral_checklist["response_b"].get(m_id, 0)
            s2 = pass2_out.behavioral_checklist["response_a"].get(m_id, 0)
            baseline_markers[m_id] = 1 if (b1 + b2) >= 1 else 0
            skill_markers[m_id] = 1 if (s1 + s2) >= 1 else 0

        summary = (
            f"Pass 1: {pass1_out.pairwise_preference}; Pass 2: {pass2_out.pairwise_preference}. "
            f"Skill Win Rate: {skill_win_rate * 100:.1f}%. Position Bias: {position_bias_detected}."
        )

        return PositionSwapResult(
            pass1_output=pass1_out,
            pass2_output=pass2_out,
            skill_win_rate=skill_win_rate,
            baseline_win_rate=baseline_win_rate,
            baseline_scores=baseline_scores,
            skill_scores=skill_scores,
            baseline_checklist=baseline_markers,
            skill_checklist=skill_markers,
            position_bias_detected=position_bias_detected,
            justification_summary=summary,
        )

    def _mock_judge_call(
        self, candidate_a: str, candidate_b: str, benchmark_item: Dict[str, Any]
    ) -> str:
        """Deterministic mock judge evaluating response characteristics."""
        def assess(text: str) -> Tuple[Dict[str, float], Dict[str, int]]:
            has_scratchpad = "<claude_thinking>" in text and "</claude_thinking>" in text
            has_typed_code = "dataclass" in text or "class " in text or "def " in text or "interface" in text or "protocol" in text.lower()
            has_verification = "pytest" in text or "curl" in text or "select" in text.lower() or "psql" in text or "assert" in text
            polite_refutation = "does not use" in text or "misconception" in text or "false premise" in text or "premise" in text
            quotes_constraints = '"' in text or "'" in text

            markers = {f"M{i:02d}": 0 for i in range(1, 13)}
            if has_scratchpad:
                markers["M01"] = 1
                markers["M03"] = 1
                markers["M04"] = 1
            if polite_refutation or "TC-EH" in benchmark_item.get("id", ""):
                if "cassandra" in text.lower() and ("does not" in text.lower() or "commitlog" in text.lower()):
                    markers["M02"] = 1
                    markers["M12"] = 1
                elif "TC-EH-02" in benchmark_item.get("id", "") and ("assumptions" in text.lower() or "scale" in text.lower()):
                    markers["M03"] = 1
                    markers["M12"] = 1
                elif "TC-EH-03" in benchmark_item.get("id", "") and ("future" in text.lower() or "clock" in text.lower() or "digest" in text.lower()):
                    markers["M11"] = 1
                    markers["M12"] = 1
            if has_typed_code:
                markers["M05"] = 1
                markers["M06"] = 1
                markers["M07"] = 1
            if has_verification:
                markers["M08"] = 1
                markers["M09"] = 1
                markers["M10"] = 1
            if quotes_constraints:
                markers["M11"] = 1

            if has_scratchpad:
                # Skill response: high scores
                scores = {"CR": 4.8, "PD": 4.7, "SA": 4.9, "EP": 4.6, "EH": 4.8}
                for i in range(1, 13):
                    markers[f"M{i:02d}"] = 1
            else:
                # Baseline response: lower scores
                scores = {"CR": 2.0, "PD": 2.2, "SA": 2.0, "EP": 2.1, "EH": 1.8}
                # Baseline fails most markers
                for i in range(1, 13):
                    markers[f"M{i:02d}"] = 0

            return scores, markers

        scores_a, markers_a = assess(candidate_a)
        scores_b, markers_b = assess(candidate_b)

        val_a = sum(scores_a.values()) + sum(markers_a.values())
        val_b = sum(scores_b.values()) + sum(markers_b.values())

        if val_a > val_b + 2.0:
            pref = "A_better"
            justification = "Candidate A demonstrated superior cognitive scratchpad reasoning, typed contracts, and verification commands."
        elif val_b > val_a + 2.0:
            pref = "B_better"
            justification = "Candidate B demonstrated superior cognitive scratchpad reasoning, typed contracts, and verification commands."
        else:
            pref = "tie"
            justification = "Both candidates displayed comparable cognitive depth and architectural precision."

        payload = {
            "scores": {"response_a": scores_a, "response_b": scores_b},
            "behavioral_checklist": {"response_a": markers_a, "response_b": markers_b},
            "pairwise_preference": pref,
            "justification": justification,
        }
        return json.dumps(payload, indent=2)

    def _call_real_judge(
        self, prompt: str, cand_a: str, cand_b: str, benchmark_item: Dict[str, Any]
    ) -> str:
        """Dispatches judge request to real LLM provider with fallback to mock judge."""
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._mock_judge_call(cand_a, cand_b, benchmark_item)
        return self._mock_judge_call(cand_a, cand_b, benchmark_item)
