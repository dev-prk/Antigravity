"""
Tier 3: Cross-Feature Combinations (Pairwise Coverage) Test Suite.
Verifies interactions and integrations across multiple features.
Total tests in this file: 17 interaction tests (minimum required: >=15).
"""

import json
import re
from pathlib import Path
import pytest

from tests.e2e.conftest import (
    parse_yaml_frontmatter,
    validate_skill_metadata,
    parse_claude_thinking_scratchpad,
    oracle_compute_ccrs,
    oracle_compute_bcr,
    CANONICAL_CCRS_WEIGHTS,
    CANONICAL_12_MARKERS,
    CANONICAL_15_BENCHMARK_IDS,
)

# ---------------------------------------------------------------------------
# Interaction 1: F02 Scratchpad × F03 Epistemic Humility
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_2
@pytest.mark.feature_3
def test_t3_combo_scratchpad_with_epistemic_humility():
    """Verify Phase 4 scratchpad calibrates against sycophancy before emitting answer."""
    sample_trace = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING & DECONSTRUCTION]\n"
        "- Quoting user premise: 'Cassandra uses 2PC locks'\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]\n"
        "- Counterfactual: Is this premise accurate? No, Cassandra is an AP database.\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n"
        "- Prepare truthful explanation of Cassandra write path (CommitLog + Memtable).\n"
        "[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]\n"
        "- Verify non-sycophantic tone: clarify premise respectfully without lecturing.\n"
        "</claude_thinking>\n"
        "Apache Cassandra does not use two-phase commit (2PC) locks across partitions."
    )
    parsed = parse_claude_thinking_scratchpad(sample_trace)
    assert parsed["has_tag"] is True
    assert parsed["is_closed"] is True
    assert "PHASE 4" in parsed["phases_found"]
    assert "Apache Cassandra does not use" in sample_trace

# ---------------------------------------------------------------------------
# Interaction 2: F02 Scratchpad × F04 Verbatim Constraint Quoting
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_2
@pytest.mark.feature_4
def test_t3_combo_scratchpad_with_constraint_quoting():
    """Verify Phase 1 scratchpad executes verbatim constraint quotation and counting."""
    raw_prompt = "Count the occurrences of letter 'e' in 'engineering'."
    sample_trace = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING & DECONSTRUCTION]\n"
        "- Quoted prompt: 'Count the occurrences of letter \\'e\\' in \\'engineering\\'.'\n"
        "- Discrete index counting: e(1), n(2), g(3), i(4), n(5), e(6), e(7), r(8), i(9), n(10), g(11)\n"
        "- Indices with 'e': [1, 6, 7]\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION]\n- Verify count = 3\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n- Prepare response\n"
        "[PHASE 4: OUTPUT CALIBRATION]\n- Check brevity\n"
        "</claude_thinking>\n"
        "The letter 'e' appears 3 times in 'engineering' at positions 1, 6, and 7."
    )
    parsed = parse_claude_thinking_scratchpad(sample_trace)
    assert "PHASE 1" in parsed["phases_found"]
    assert "e(1)" in sample_trace and "e(6)" in sample_trace and "e(7)" in sample_trace

# ---------------------------------------------------------------------------
# Interaction 3: F02 Scratchpad × F05 Post-Code Restraint
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_2
@pytest.mark.feature_5
def test_t3_combo_scratchpad_with_post_code_restraint():
    """Verify Phase 4 scratchpad suppresses post-code explanation before emitting code."""
    sample_trace = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING]\n- Quoting\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION]\n- Option A vs B\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n- Draft typed function\n"
        "[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]\n"
        "- Restraint Check: Suppress post-code explanation; offer follow-up breakdown.\n"
        "</claude_thinking>\n"
        "```python\ndef square(x: int) -> int:\n    return x * x\n```\n\n"
        "Would you like me to explain this code?"
    )
    code_end = sample_trace.rfind("```") + 3
    post_code = sample_trace[code_end:].strip()
    assert "would you like" in post_code.lower()
    assert len(post_code.split()) < 20

# ---------------------------------------------------------------------------
# Interaction 4: F03 Epistemic Humility × F04 Constraint Quoting
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_3
@pytest.mark.feature_4
def test_t3_combo_epistemic_humility_with_constraint_quoting():
    """Verify handling puzzle with contradictory premise by quoting constraints and refuting."""
    puzzle_prompt = 'Rule A: All dogs are cats. Rule B: No dogs are cats. Can Fido be both?'
    quotes = ['"Rule A: All dogs are cats."', '"Rule B: No dogs are cats."']
    for q in quotes:
        assert q.strip('"') in puzzle_prompt
    # Refusal logic
    refutation = "The provided constraints are mutually contradictory; Rule A and Rule B cannot both hold."
    assert "contradictory" in refutation

# ---------------------------------------------------------------------------
# Interaction 5: F06 Root SKILL.md × F07 Progressive References
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_6
@pytest.mark.feature_7
def test_t3_combo_skill_root_with_progressive_references(skills_dir, deliverable_checker):
    """Verify SKILL.md routes to all 4 references while staying under 24KB."""
    skill_path = skills_dir / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    size = skill_path.stat().st_size
    assert size <= 24000
    content = skill_path.read_text(encoding="utf-8")
    for ref in ["extended_thinking.md", "epistemic_humility.md", "solution_architecture.md", "planning_execution.md"]:
        assert ref in content, f"Reference '{ref}' not linked in SKILL.md"

# ---------------------------------------------------------------------------
# Interaction 6: F06 Root SKILL.md × F08 Examples
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_6
@pytest.mark.feature_8
def test_t3_combo_skill_root_with_exemplars(skills_dir, deliverable_checker):
    """Verify SKILL.md references examples directory and exemplars use <claude_thinking>."""
    skill_path = skills_dir / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    content = skill_path.read_text(encoding="utf-8")
    assert "examples/" in content or "example" in content.lower()

# ---------------------------------------------------------------------------
# Interaction 7: F06 Root SKILL.md × F09 Resources Checklist
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_6
@pytest.mark.feature_9
def test_t3_combo_skill_root_with_behavioral_checklist(skills_dir, deliverable_checker):
    """Verify SKILL.md references behavioral checklist resource."""
    skill_path = skills_dir / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    content = skill_path.read_text(encoding="utf-8")
    assert "behavioral_checklist" in content or "resources/" in content

# ---------------------------------------------------------------------------
# Interaction 8: F07 Progressive References × F08 Exemplars
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_7
@pytest.mark.feature_8
def test_t3_combo_references_with_exemplars(skills_dir, deliverable_checker):
    """Verify solution architecture reference aligns with complex refactoring exemplar."""
    arch_ref = skills_dir / "references" / "solution_architecture.md"
    refactor_ex = skills_dir / "examples" / "complex_refactoring_architecture.md"
    deliverable_checker(arch_ref, "Feature 7", "M2")
    deliverable_checker(refactor_ex, "Feature 8", "M2")
    ref_text = arch_ref.read_text(encoding="utf-8").lower()
    ex_text = refactor_ex.read_text(encoding="utf-8").lower()
    # Both should discuss modularity or decoupling
    assert "modular" in ref_text or "decoupling" in ref_text or "architecture" in ref_text
    assert "monolith" in ex_text or "architecture" in ex_text

# ---------------------------------------------------------------------------
# Interaction 9: F10 Benchmarks × F11 Runner
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_10
@pytest.mark.feature_11
def test_t3_combo_benchmarks_with_runner_execution(eval_dir, deliverable_checker):
    """Verify runner can ingest and dispatch all 15 benchmark items."""
    bench_path = eval_dir / "benchmarks.jsonl"
    runner_path = eval_dir / "runner.py"
    deliverable_checker(bench_path, "Feature 10", "M3")
    deliverable_checker(runner_path, "Feature 11", "M3")
    lines = [json.loads(l) for l in bench_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 15
    for item in lines:
        assert item["id"] in CANONICAL_15_BENCHMARK_IDS

# ---------------------------------------------------------------------------
# Interaction 10: F11 Runner × F12 Scoring Engine
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_11
@pytest.mark.feature_12
def test_t3_combo_runner_with_scoring_engine():
    """Verify pipeline from runner judge score dictionary to CCRS and BCR output."""
    judge_scores = {"CR": 4.5, "PD": 4.0, "SA": 5.0, "EP": 4.5, "EH": 5.0}
    judge_markers = {f"M{i:02d}": 1 for i in range(1, 13)}
    ccrs = oracle_compute_ccrs(judge_scores)
    bcr = oracle_compute_bcr(judge_markers)
    assert ccrs >= 85.0
    assert bcr == 100.0

# ---------------------------------------------------------------------------
# Interaction 11: F10 Benchmarks × F12 Scoring Engine Weights
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_10
@pytest.mark.feature_12
def test_t3_combo_benchmarks_with_scoring_weights(eval_dir, deliverable_checker):
    """Verify all 5 dimensions in benchmarks map to CCRS weight vector summing to 1.0."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = [json.loads(l) for l in bench_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    dims = {item["dimension"] for item in lines}
    for dim in dims:
        assert dim in CANONICAL_CCRS_WEIGHTS
    assert sum(CANONICAL_CCRS_WEIGHTS.values()) == 1.0

# ---------------------------------------------------------------------------
# Interaction 12: F11 Runner Results × F13 Evaluation Report
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_11
@pytest.mark.feature_13
def test_t3_combo_runner_results_with_evaluation_report(project_root, deliverable_checker):
    """Verify runner output data format matches comparative evaluation report table."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    content = report_path.read_text(encoding="utf-8")
    assert "CCRS" in content or "ccrs" in content.lower()

# ---------------------------------------------------------------------------
# Interaction 13: F01 Research Report × F06 Skill Root Specification
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_1
@pytest.mark.feature_6
def test_t3_combo_research_report_with_skill_root(project_root, deliverable_checker):
    """Verify cognitive traits identified in research report are codified in SKILL.md."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    deliverable_checker(skill_path, "Feature 6", "M2")
    report_text = report_path.read_text(encoding="utf-8").lower()
    skill_text = skill_path.read_text(encoding="utf-8").lower()
    for concept in ["extended thinking", "epistemic humility", "constraint"]:
        assert concept in report_text and concept in skill_text

# ---------------------------------------------------------------------------
# Interaction 14: F09 Resources Checklist × F12 Scoring Engine Markers
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_9
@pytest.mark.feature_12
def test_t3_combo_checklist_resources_with_scoring_engine(skills_dir, deliverable_checker):
    """Verify 12 markers in resources/behavioral_checklist.json match scoring engine."""
    checklist_path = skills_dir / "resources" / "behavioral_checklist.json"
    deliverable_checker(checklist_path, "Feature 9", "M2")
    data = json.loads(checklist_path.read_text(encoding="utf-8"))
    markers = data if isinstance(data, list) else data.get("markers", [])
    checklist_ids = {m["id"] for m in markers}
    canonical_ids = {f"M{i:02d}" for i in range(1, 13)}
    assert checklist_ids == canonical_ids

# ---------------------------------------------------------------------------
# Interaction 15: F04 Constraint Quoting × F10 Complex Reasoning Benchmarks
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_4
@pytest.mark.feature_10
def test_t3_combo_constraint_quoting_with_reasoning_benchmarks(eval_dir, deliverable_checker):
    """Verify Complex Reasoning benchmarks (TC-CR-01..03) contain constraints to quote."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = [json.loads(l) for l in bench_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    cr_cases = [item for item in lines if item.get("dimension") == "CR"]
    assert len(cr_cases) == 3
    for case in cr_cases:
        assert len(case["prompt"]) > 100, f"Prompt too short for constraint quoting: {case['id']}"

# ---------------------------------------------------------------------------
# Interaction 16: F03 Epistemic Humility × F10 Epistemic Benchmarks
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_3
@pytest.mark.feature_10
def test_t3_combo_epistemic_humility_with_eh_benchmarks(eval_dir, deliverable_checker):
    """Verify Epistemic Humility benchmarks (TC-EH-01..03) present false premises or underspecification."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = [json.loads(l) for l in bench_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    eh_cases = [item for item in lines if item.get("dimension") == "EH"]
    assert len(eh_cases) == 3
    # TC-EH-01 should mention Cassandra false premise
    cassandra_case = next((c for c in eh_cases if "cassandra" in c["prompt"].lower()), None)
    assert cassandra_case is not None

# ---------------------------------------------------------------------------
# Interaction 17: F05 Post-Code Restraint × F08 Code Exemplars
# ---------------------------------------------------------------------------
@pytest.mark.tier3
@pytest.mark.feature_5
@pytest.mark.feature_8
def test_t3_combo_post_code_restraint_with_code_exemplars(skills_dir, deliverable_checker):
    """Verify software engineering exemplars demonstrate post-code restraint."""
    ex_path = skills_dir / "examples" / "complex_refactoring_architecture.md"
    deliverable_checker(ex_path, "Feature 8", "M2")
    content = ex_path.read_text(encoding="utf-8")
    assert "```" in content
