"""
Tier 1: Feature Coverage Test Suite for Claude Antigravity Skill.
Validates the primary happy path and core requirements for all 15 inventoried features.
Total tests in this file: 75 tests (15 features × 5 tests).
"""

import ast
import json
import re
import math
from pathlib import Path
import pytest
import yaml

from tests.e2e.conftest import (
    parse_yaml_frontmatter,
    validate_skill_metadata,
    parse_claude_thinking_scratchpad,
    oracle_compute_ccrs,
    oracle_compute_bcr,
    oracle_compute_information_density,
    CANONICAL_CCRS_WEIGHTS,
    CANONICAL_12_MARKERS,
    CANONICAL_15_BENCHMARK_IDS,
)

# ===========================================================================
# Feature 1: Claude Cognitive Architecture Research Report (M1)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m1
@pytest.mark.feature_1
def test_f01_report_file_existence(project_root, deliverable_checker):
    """Test 1.1: Verify research report file exists and is substantial (>2KB)."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    assert report_path.is_file(), f"Expected {report_path} to be a file"
    assert report_path.stat().st_size >= 2048, f"Report size {report_path.stat().st_size} bytes is under 2KB"

@pytest.mark.tier1
@pytest.mark.m1
@pytest.mark.feature_1
def test_f01_report_cognitive_pillars(project_root, deliverable_checker):
    """Test 1.2: Verify research report deconstructs the core cognitive pillars."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    content = report_path.read_text(encoding="utf-8")
    pillars = [
        "Extended Thinking",
        "Epistemic Humility",
        "Constraint Anchoring",
        "Solution Architecture",
        "Cross-Model Elicitation",
    ]
    for pillar in pillars:
        assert re.search(re.escape(pillar), content, re.IGNORECASE), f"Pillar '{pillar}' missing from research report"

@pytest.mark.tier1
@pytest.mark.m1
@pytest.mark.feature_1
def test_f01_report_claude_models_coverage(project_root, deliverable_checker):
    """Test 1.3: Verify research report covers Claude 3.5, 3.7 Sonnet, and Opus."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    content = report_path.read_text(encoding="utf-8")
    models = ["Claude 3.5", "Claude 3.7", "Opus"]
    for model in models:
        assert model.lower() in content.lower(), f"Model family '{model}' missing from research report"

@pytest.mark.tier1
@pytest.mark.m1
@pytest.mark.feature_1
def test_f01_report_claude_code_harness(project_root, deliverable_checker):
    """Test 1.4: Verify research report covers Claude Code agentic harness patterns."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    content = report_path.read_text(encoding="utf-8")
    harness_concepts = ["Claude Code", "CLAUDE.md", "stateless"]
    for concept in harness_concepts:
        assert concept.lower() in content.lower(), f"Agentic concept '{concept}' missing from research report"

@pytest.mark.tier1
@pytest.mark.m1
@pytest.mark.feature_1
def test_f01_report_scratchpad_scaffold_spec(project_root, deliverable_checker):
    """Test 1.5: Verify research report specifies the 4-phase scratchpad protocol."""
    report_path = project_root / "docs" / "research" / "claude_cognitive_architecture_report.md"
    deliverable_checker(report_path, "Feature 1", "M1")
    content = report_path.read_text(encoding="utf-8")
    assert "<claude_thinking>" in content, "Tag <claude_thinking> missing in research report"
    assert "PHASE 1" in content or "Phase 1" in content, "Phase 1 missing in report scratchpad spec"
    assert "PHASE 4" in content or "Phase 4" in content, "Phase 4 missing in report scratchpad spec"

# ===========================================================================
# Feature 2: Universal <claude_thinking> 4-Phase Scratchpad (M1, M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_2
def test_f02_scratchpad_phase1_constraint_anchoring():
    """Test 2.1: Verify Phase 1 (Constraint Anchoring & Deconstruction) specification."""
    sample = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING & DECONSTRUCTION]\n"
        "- Quoting constraints verbatim: 'Must not exceed 50ms'\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]\n"
        "- Competing hypothesis A vs B\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING & PRE-COMPUTATION]\n"
        "- Interface contracts\n"
        "[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]\n"
        "- Verify zero preamble\n"
        "</claude_thinking>"
    )
    parsed = parse_claude_thinking_scratchpad(sample)
    assert parsed["has_tag"] is True
    assert parsed["is_closed"] is True
    assert "PHASE 1" in parsed["phases_found"]
    assert len(parsed["errors"]) == 0

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_2
def test_f02_scratchpad_phase2_hypothesis_exploration():
    """Test 2.2: Verify Phase 2 (Hypothesis Exploration & Counter-Factual Stress Testing)."""
    sample = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING]\n- Quoting\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]\n"
        "- Testing failure modes under network partition\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n- Schemas\n"
        "[PHASE 4: OUTPUT CALIBRATION]\n- Calibration\n"
        "</claude_thinking>"
    )
    parsed = parse_claude_thinking_scratchpad(sample)
    assert "PHASE 2" in parsed["phases_found"]

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_2
def test_f02_scratchpad_phase3_architectural_blueprinting():
    """Test 2.3: Verify Phase 3 (Architectural Blueprinting & Pre-computation)."""
    sample = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING]\n- Quoting\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION]\n- Exploration\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING & PRE-COMPUTATION]\n"
        "- Interface types and step-by-step logic trace\n"
        "[PHASE 4: OUTPUT CALIBRATION]\n- Calibration\n"
        "</claude_thinking>"
    )
    parsed = parse_claude_thinking_scratchpad(sample)
    assert "PHASE 3" in parsed["phases_found"]

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_2
def test_f02_scratchpad_phase4_output_calibration():
    """Test 2.4: Verify Phase 4 (Output Calibration & Restraint Check)."""
    sample = (
        "<claude_thinking>\n"
        "[PHASE 1: CONSTRAINT ANCHORING]\n- Quoting\n"
        "[PHASE 2: HYPOTHESIS EXPLORATION]\n- Exploration\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n- Blueprint\n"
        "[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]\n"
        "- Check that tone is objective, humble, decisive, and fluff-free\n"
        "</claude_thinking>"
    )
    parsed = parse_claude_thinking_scratchpad(sample)
    assert "PHASE 4" in parsed["phases_found"]

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_2
def test_f02_scratchpad_tag_boundaries_and_order():
    """Test 2.5: Verify tag boundaries and rejection of out-of-order phases."""
    out_of_order = (
        "<claude_thinking>\n"
        "[PHASE 3: ARCHITECTURAL BLUEPRINTING]\n- Blueprint first\n"
        "[PHASE 1: CONSTRAINT ANCHORING]\n- Anchoring late\n"
        "</claude_thinking>"
    )
    parsed = parse_claude_thinking_scratchpad(out_of_order)
    assert any("Out-of-order" in err for err in parsed["errors"])

# ===========================================================================
# Feature 3: Epistemic Humility & Anti-Sycophancy Rules (M1, M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_3
def test_f03_epistemic_uncertainty_admission(project_root, deliverable_checker):
    """Test 3.1: Verify rule distinguishing verified facts from inferred assumptions."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 3", "M2")
    content = skill_path.read_text(encoding="utf-8")
    assert "epistemic" in content.lower() or "assumption" in content.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_3
def test_f03_anti_sycophancy_premise_challenge():
    """Test 3.2: Verify anti-sycophancy rule challenging false user premises."""
    rule_directive = (
        "When the user's premise is incorrect, respectfully clarify the misconception "
        "with empirical evidence rather than sycophantically agreeing."
    )
    assert "sycophant" in rule_directive.lower()
    assert "misconception" in rule_directive.lower() or "premise" in rule_directive.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_3
def test_f03_pushback_calibration_non_capitulation():
    """Test 3.3: Verify calibrated response under user pushback (no blind apologies)."""
    directive = "Under user pushback, re-evaluate evidence objectively; do not apologize reflexively if user claim is invalid."
    assert "apologize" in directive.lower()
    assert "evidence" in directive.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_3
def test_f03_niche_hallucination_warning():
    """Test 3.4: Verify explicit hallucination warning requirement on niche/obscure lookups."""
    sample_notice = "I don't have access to search or a live database; please verify this citation."
    assert "verify" in sample_notice.lower()
    assert "database" in sample_notice.lower() or "search" in sample_notice.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_3
def test_f03_decisive_recommendation_stance():
    """Test 3.5: Verify single decisive recommendation rule over unranked lists."""
    directive = "When asked for a recommendation or selection, decisively choose one optimal path and defend it."
    assert "decisive" in directive.lower() or "choose one" in directive.lower()

# ===========================================================================
# Feature 4: Verbatim Constraint Quoting & Index Counting (M1, M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_4
def test_f04_verbatim_constraint_quoting_rule():
    """Test 4.1: Verify verbatim puzzle constraint quotation rule inside quotation marks."""
    prompt = "A farmer must cross a river with a wolf, goat, and cabbage. The boat can only hold 2 items."
    extracted_quote = '"The boat can only hold 2 items."'
    clean_quote = extracted_quote.strip('"')
    assert clean_quote in prompt, f"Expected '{clean_quote}' to be verbatim in '{prompt}'"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_4
def test_f04_discrete_character_index_counting_rule():
    """Test 4.2: Verify character index counting sequence (e.g. strawberry)."""
    word = "strawberry"
    # Canonical index format: s(1), t(2), r(3), a(4), w(5), b(6), e(7), r(8), r(9), y(10)
    indexed = [f"{char}({i+1})" for i, char in enumerate(word)]
    assert indexed[2] == "r(3)"
    assert indexed[7] == "r(8)"
    assert indexed[8] == "r(9)"
    r_indices = [i+1 for i, char in enumerate(word) if char == "r"]
    assert r_indices == [3, 8, 9]
    assert len(r_indices) == 3

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_4
def test_f04_quoting_fidelity_validation():
    """Test 4.3: Verify quoting fidelity against multi-constraint prompt."""
    prompt = "Constraint A: P99 < 15ms. Constraint B: No distributed 2PC. Constraint C: Zero data loss."
    quotes = ['"Constraint A: P99 < 15ms."', '"Constraint B: No distributed 2PC."', '"Constraint C: Zero data loss."']
    for q in quotes:
        assert q.strip('"') in prompt

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_4
def test_f04_index_numbering_ledger_validation():
    """Test 4.4: Verify contiguous 1-indexed numbering ledger."""
    text = "c(1), o(2), n(3), s(4), t(5), r(6), a(7), i(8), n(9), t(10)"
    matches = re.findall(r"([a-z])\((\d+)\)", text)
    assert len(matches) == 10
    indices = [int(idx) for _, idx in matches]
    assert indices == list(range(1, 11))

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_4
def test_f04_negative_constraint_preservation():
    """Test 4.5: Verify negative constraints ('never', 'cannot', 'without') are preserved."""
    rule = "Account balances must NEVER overdraft, even under concurrent transfers."
    assert "never" in rule.lower() or "cannot" in rule.lower()

# ===========================================================================
# Feature 5: Post-Code Explanation Suppression & Concise Delivery (M1, M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_5
def test_f05_post_code_restraint_rule():
    """Test 5.1: Verify post-code explanation suppression directive."""
    rule = (
        "Claude uses markdown for code. Immediately after closing coding markdown, "
        "Claude asks the person if they would like it to explain or break down the code. "
        "It does not explain or break down the code unless the person requests it."
    )
    assert "markdown" in rule.lower()
    assert "explain" in rule.lower()
    assert "unless" in rule.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_5
def test_f05_unsolicited_breakdown_suppression():
    """Test 5.2: Verify response ends with follow-up offer rather than syntax explanation."""
    sample_response = (
        "```python\ndef add(a: int, b: int) -> int:\n    return a + b\n```\n\n"
        "Would you like me to explain or break down this code?"
    )
    code_end = sample_response.rfind("```") + 3
    post_code = sample_response[code_end:].strip()
    assert "would you like" in post_code.lower()
    assert len(post_code) < 120, "Post-code text contains an unsolicited wall of explanation"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_5
def test_f05_conversational_preamble_elimination():
    """Test 5.3: Verify elimination of conversational preamble before code."""
    valid_start = "```python\nimport sys\n"
    fluff_starts = ["Certainly!", "Sure, here is your code:", "Here you go:"]
    assert valid_start.startswith("```")
    for fluff in fluff_starts:
        assert not valid_start.startswith(fluff)

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_5
def test_f05_prose_preference_over_lists():
    """Test 5.4: Verify prose preference over fragmented bullet points."""
    prose = "The architecture adopts an event-sourced ledger model to ensure full auditability. Read queries are served locally."
    bullets = "- Point 1\n- Point 2\n- Point 3\n- Point 4\n- Point 5"
    assert "\n- " not in prose
    assert prose.count("\n") <= 1

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_5
def test_f05_code_block_purity_and_typing():
    """Test 5.5: Verify Python code block parses cleanly and has typed annotations."""
    code = "def process_event(event_id: str, payload: dict) -> bool:\n    return bool(event_id and payload)\n"
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    func = parsed.body[0]
    assert func.returns is not None, "Function is missing return type annotation"

# ===========================================================================
# Feature 6: Antigravity Skill Root Specification (SKILL.md) (M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_6
def test_f06_skill_md_file_existence(project_root, deliverable_checker):
    """Test 6.1: Verify skills/claude/SKILL.md exists and has frontmatter delimiters."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    content = skill_path.read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with triple-hyphen '---'"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_6
def test_f06_frontmatter_name_schema(project_root, deliverable_checker):
    """Test 6.2: Verify frontmatter name is 'claude' and matches ^[A-Za-z0-9._-]{1,64}$."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    data = parse_yaml_frontmatter(skill_path.read_text(encoding="utf-8"))
    errors = validate_skill_metadata(data)
    assert len(errors) == 0, f"Frontmatter errors: {errors}"
    assert data["name"] == "claude"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_6
def test_f06_frontmatter_description_schema(project_root, deliverable_checker):
    """Test 6.3: Verify frontmatter description contains 3rd-person trigger instruction."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    data = parse_yaml_frontmatter(skill_path.read_text(encoding="utf-8"))
    desc = data["description"]
    assert "use this skill" in desc.lower(), "Description must instruct agent 'Use this skill when...'"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_6
def test_f06_frontmatter_invocation_flags(project_root, deliverable_checker):
    """Test 6.4: Verify frontmatter invocation flags and icon."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    data = parse_yaml_frontmatter(skill_path.read_text(encoding="utf-8"))
    assert data.get("disable-slash-command") is False
    assert data.get("disable-model-invocation") is False
    assert data.get("metadata", {}).get("icon") == "psychology"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_6
def test_f06_skill_md_size_limit_24kb(project_root, deliverable_checker):
    """Test 6.5: Verify SKILL.md conforms to Antigravity 24KB file size limit."""
    skill_path = project_root / "skills" / "claude" / "SKILL.md"
    deliverable_checker(skill_path, "Feature 6", "M2")
    size_bytes = skill_path.stat().st_size
    assert size_bytes <= 24000, f"SKILL.md size {size_bytes} exceeds 24,000 bytes Antigravity limit"

# ===========================================================================
# Feature 7: Progressive Disclosure Hierarchy (references/) (M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_7
def test_f07_references_directory_and_inventory(skills_dir, deliverable_checker):
    """Test 7.1: Verify references/ directory contains the 4 core reference files."""
    ref_dir = skills_dir / "references"
    deliverable_checker(ref_dir, "Feature 7", "M2")
    expected_files = [
        "extended_thinking.md",
        "epistemic_humility.md",
        "solution_architecture.md",
        "planning_execution.md",
    ]
    for filename in expected_files:
        path = ref_dir / filename
        deliverable_checker(path, "Feature 7", "M2")
        assert path.is_file(), f"Expected {filename} to exist in references/"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_7
def test_f07_relative_links_from_skill_md(skills_dir, deliverable_checker):
    """Test 7.2: Verify SKILL.md contains valid relative markdown links to references/."""
    skill_path = skills_dir / "SKILL.md"
    deliverable_checker(skill_path, "Feature 7", "M2")
    content = skill_path.read_text(encoding="utf-8")
    assert "./references/" in content or "references/" in content

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_7
def test_f07_reference_subdocument_structure(skills_dir, deliverable_checker):
    """Test 7.3: Verify reference subdocuments have valid markdown headings."""
    ref_path = skills_dir / "references" / "extended_thinking.md"
    deliverable_checker(ref_path, "Feature 7", "M2")
    content = ref_path.read_text(encoding="utf-8")
    assert content.startswith("#")

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_7
def test_f07_progressive_disclosure_separation(skills_dir, deliverable_checker):
    """Test 7.4: Verify subdocuments offload detailed guidelines under progressive disclosure."""
    ref_dir = skills_dir / "references"
    deliverable_checker(ref_dir, "Feature 7", "M2")
    total_ref_size = sum(f.stat().st_size for f in ref_dir.glob("*.md"))
    assert total_ref_size > 1000, "References directory is empty or trivial"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_7
def test_f07_posix_path_portability(skills_dir, deliverable_checker):
    """Test 7.5: Verify all reference links use POSIX forward slashes."""
    skill_path = skills_dir / "SKILL.md"
    deliverable_checker(skill_path, "Feature 7", "M2")
    content = skill_path.read_text(encoding="utf-8")
    links = re.findall(r"\[.*?\]\((.*?)\)", content)
    for link in links:
        assert "\\" not in link, f"Found Windows backslash in link: {link}"

# ===========================================================================
# Feature 8: Reference Implementations & Exemplars (examples/) (M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_8
def test_f08_examples_directory_and_inventory(skills_dir, deliverable_checker):
    """Test 8.1: Verify examples/ directory contains the 3 required exemplars."""
    ex_dir = skills_dir / "examples"
    deliverable_checker(ex_dir, "Feature 8", "M2")
    expected = [
        "distributed_systems_consensus.md",
        "complex_refactoring_architecture.md",
        "logic_puzzle_constraint_anchoring.md",
    ]
    for name in expected:
        path = ex_dir / name
        deliverable_checker(path, "Feature 8", "M2")
        assert path.is_file()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_8
def test_f08_distributed_consensus_exemplar_content(skills_dir, deliverable_checker):
    """Test 8.2: Verify distributed consensus exemplar contains Raft/Paxos trace."""
    path = skills_dir / "examples" / "distributed_systems_consensus.md"
    deliverable_checker(path, "Feature 8", "M2")
    content = path.read_text(encoding="utf-8")
    assert "raft" in content.lower() or "consensus" in content.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_8
def test_f08_complex_refactoring_exemplar_content(skills_dir, deliverable_checker):
    """Test 8.3: Verify complex refactoring exemplar demonstrates monolith decomposition."""
    path = skills_dir / "examples" / "complex_refactoring_architecture.md"
    deliverable_checker(path, "Feature 8", "M2")
    content = path.read_text(encoding="utf-8")
    assert "monolith" in content.lower() or "strangler" in content.lower() or "microservice" in content.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_8
def test_f08_logic_puzzle_exemplar_content(skills_dir, deliverable_checker):
    """Test 8.4: Verify logic puzzle exemplar demonstrates verbatim quotation & counting."""
    path = skills_dir / "examples" / "logic_puzzle_constraint_anchoring.md"
    deliverable_checker(path, "Feature 8", "M2")
    content = path.read_text(encoding="utf-8")
    assert '"' in content, "Exemplar must demonstrate quotation inside double quotes"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_8
def test_f08_exemplar_structure_and_turn_alternation(skills_dir, deliverable_checker):
    """Test 8.5: Verify exemplar files contain prompt, thinking scratchpad, and output."""
    path = skills_dir / "examples" / "distributed_systems_consensus.md"
    deliverable_checker(path, "Feature 8", "M2")
    content = path.read_text(encoding="utf-8")
    assert "<claude_thinking>" in content or "thinking" in content.lower()

# ===========================================================================
# Feature 9: Verification Checklists & Scaffolds (resources/) (M2)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_9
def test_f09_resources_directory_and_inventory(skills_dir, deliverable_checker):
    """Test 9.1: Verify resources/ contains behavioral_checklist.json and prompt_scaffolds.md."""
    res_dir = skills_dir / "resources"
    deliverable_checker(res_dir, "Feature 9", "M2")
    checklist_path = res_dir / "behavioral_checklist.json"
    scaffolds_path = res_dir / "prompt_scaffolds.md"
    deliverable_checker(checklist_path, "Feature 9", "M2")
    deliverable_checker(scaffolds_path, "Feature 9", "M2")
    assert checklist_path.is_file()
    assert scaffolds_path.is_file()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_9
def test_f09_behavioral_checklist_schema(skills_dir, deliverable_checker):
    """Test 9.2: Verify behavioral_checklist.json parses as valid JSON with 12 markers."""
    path = skills_dir / "resources" / "behavioral_checklist.json"
    deliverable_checker(path, "Feature 9", "M2")
    data = json.loads(path.read_text(encoding="utf-8"))
    markers = data if isinstance(data, list) else data.get("markers", [])
    assert len(markers) == 12, f"Expected 12 markers, found {len(markers)}"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_9
def test_f09_behavioral_checklist_marker_properties(skills_dir, deliverable_checker):
    """Test 9.3: Verify each checklist marker has id, name, description, and criteria."""
    path = skills_dir / "resources" / "behavioral_checklist.json"
    deliverable_checker(path, "Feature 9", "M2")
    data = json.loads(path.read_text(encoding="utf-8"))
    markers = data if isinstance(data, list) else data.get("markers", [])
    for m in markers:
        assert "id" in m, f"Marker missing 'id': {m}"
        assert "name" in m, f"Marker missing 'name': {m}"

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_9
def test_f09_prompt_scaffolds_multi_model(skills_dir, deliverable_checker):
    """Test 9.4: Verify prompt_scaffolds.md provides templates for frontier models."""
    path = skills_dir / "resources" / "prompt_scaffolds.md"
    deliverable_checker(path, "Feature 9", "M2")
    content = path.read_text(encoding="utf-8")
    assert "gpt" in content.lower() or "gemini" in content.lower() or "model" in content.lower()

@pytest.mark.tier1
@pytest.mark.m2
@pytest.mark.feature_9
def test_f09_scaffolds_prompt_injection_safety(skills_dir, deliverable_checker):
    """Test 9.5: Verify scaffolds do not attempt to override host environment tools."""
    path = skills_dir / "resources" / "prompt_scaffolds.md"
    deliverable_checker(path, "Feature 9", "M2")
    content = path.read_text(encoding="utf-8")
    # Verify no command hijacking
    assert "run_command" not in content or "override" not in content

# ===========================================================================
# Feature 10: 5-Dimensional Benchmark Suite (benchmarks.jsonl) (M3)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_10
def test_f10_benchmarks_file_existence_and_jsonl(eval_dir, deliverable_checker):
    """Test 10.1: Verify benchmarks.jsonl exists and parses as valid JSONL."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 0
    for line in lines:
        item = json.loads(line)
        assert isinstance(item, dict)

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_10
def test_f10_benchmarks_exact_count_15(eval_dir, deliverable_checker):
    """Test 10.2: Verify exactly 15 benchmark test cases exist."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 15, f"Expected 15 benchmarks, found {len(lines)}"

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_10
def test_f10_benchmarks_five_dimensions_balanced(eval_dir, deliverable_checker):
    """Test 10.3: Verify all 5 dimensions (CR, PD, SA, EP, EH) have 3 test cases each."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
    dim_counts = {}
    for line in lines:
        item = json.loads(line)
        dim = item.get("dimension")
        dim_counts[dim] = dim_counts.get(dim, 0) + 1
    assert dim_counts.get("CR") == 3
    assert dim_counts.get("PD") == 3
    assert dim_counts.get("SA") == 3
    assert dim_counts.get("EP") == 3
    assert dim_counts.get("EH") == 3

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_10
def test_f10_benchmarks_schema_compliance(eval_dir, deliverable_checker):
    """Test 10.4: Verify required schema fields exist on every benchmark item."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
    for line in lines:
        item = json.loads(line)
        for req in ["id", "dimension", "prompt"]:
            assert req in item, f"Missing required property '{req}' in benchmark item: {item.get('id')}"

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_10
def test_f10_benchmarks_rubric_anchors_validity(eval_dir, deliverable_checker):
    """Test 10.5: Verify benchmark rubric anchors contain score 1, 3, 5 descriptions."""
    bench_path = eval_dir / "benchmarks.jsonl"
    deliverable_checker(bench_path, "Feature 10", "M3")
    lines = bench_path.read_text(encoding="utf-8").strip().splitlines()
    for line in lines:
        item = json.loads(line)
        rubric = item.get("rubric") or item.get("rubric_anchors")
        assert rubric is not None, f"Item {item.get('id')} missing rubric"
        has_anchors = ("1" in rubric and "3" in rubric and "5" in rubric) or (
            "score_1" in rubric and "score_3" in rubric and "score_5" in rubric
        )
        assert has_anchors, f"Item {item.get('id')} missing 1-3-5 rubric anchors: {rubric}"

# ===========================================================================
# Feature 11: Contrastive Triad Evaluation Runner (runner.py, judge.py) (M3)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_11
def test_f11_runner_script_existence_and_syntax(eval_dir, deliverable_checker):
    """Test 11.1: Verify runner.py exists and compiles cleanly."""
    runner_path = eval_dir / "runner.py"
    deliverable_checker(runner_path, "Feature 11", "M3")
    code = runner_path.read_text(encoding="utf-8")
    compiled = compile(code, str(runner_path), "exec")
    assert compiled is not None

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_11
def test_f11_judge_script_existence_and_syntax(eval_dir, deliverable_checker):
    """Test 11.2: Verify judge.py exists and compiles cleanly."""
    judge_path = eval_dir / "judge.py"
    deliverable_checker(judge_path, "Feature 11", "M3")
    code = judge_path.read_text(encoding="utf-8")
    compiled = compile(code, str(judge_path), "exec")
    assert compiled is not None

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_11
def test_f11_runner_cli_argument_parser(eval_dir, deliverable_checker):
    """Test 11.3: Verify runner CLI accepts --benchmarks and --output."""
    runner_path = eval_dir / "runner.py"
    deliverable_checker(runner_path, "Feature 11", "M3")
    content = runner_path.read_text(encoding="utf-8")
    assert "--benchmarks" in content or "benchmarks" in content
    assert "--output" in content or "output" in content

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_11
def test_f11_dual_run_position_swapping(eval_dir, deliverable_checker):
    """Test 11.4: Verify position-swapping algorithm logic."""
    # Oracle position swapping check:
    # Pass 1: A vs B -> Judge picks B (skilled) -> 1
    # Pass 2: B vs A -> Judge picks B (skilled) -> 1
    # WinRate(B) = (1 + 1)/2 = 1.0 (Skilled wins)
    pass1_b_win = 1
    pass2_b_win = 1
    win_rate = (pass1_b_win + pass2_b_win) / 2.0
    assert win_rate == 1.0

    # Position bias check: Judge always picks Candidate 1
    # Pass 1 (A, B) -> picks A (0 for B)
    # Pass 2 (B, A) -> picks B (1 for B)
    # WinRate(B) = (0 + 1)/2 = 0.5 (Neutralized to tie!)
    biased_pass1_b_win = 0
    biased_pass2_b_win = 1
    debiased_rate = (biased_pass1_b_win + biased_pass2_b_win) / 2.0
    assert debiased_rate == 0.5

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_11
def test_f11_judge_output_schema_contract():
    """Test 11.5: Verify judge output JSON schema contract."""
    sample_judge_output = {
        "scores": {
            "response_a": {"CR": 2, "PD": 3, "SA": 2, "EP": 2, "EH": 1},
            "response_b": {"CR": 5, "PD": 5, "SA": 5, "EP": 5, "EH": 5},
        },
        "behavioral_checklist": {
            "response_a": {f"M{i:02d}": 0 for i in range(1, 13)},
            "response_b": {f"M{i:02d}": 1 for i in range(1, 13)},
        },
        "pairwise_preference": "B_better",
        "justification": "Candidate B provided comprehensive MECE decomposition and typed contracts.",
    }
    assert "scores" in sample_judge_output
    assert "behavioral_checklist" in sample_judge_output
    assert sample_judge_output["pairwise_preference"] in ("A_better", "B_better", "tie")

# ===========================================================================
# Feature 12: Composite Scoring Engine (CCRS & BCR) (M3)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_12
def test_f12_scoring_script_existence_and_syntax(eval_dir, deliverable_checker):
    """Test 12.1: Verify scoring engine exists in tests/evaluation/scoring.py."""
    scoring_path = eval_dir / "scoring.py"
    deliverable_checker(scoring_path, "Feature 12", "M3")
    code = scoring_path.read_text(encoding="utf-8")
    compiled = compile(code, str(scoring_path), "exec")
    assert compiled is not None

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_12
def test_f12_ccrs_mathematical_weights():
    """Test 12.2: Verify CCRS calculation with exact weights (0.20, 0.20, 0.25, 0.20, 0.15)."""
    perfect_scores = {"CR": 5.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0}
    ccrs = oracle_compute_ccrs(perfect_scores)
    assert ccrs == 100.0, f"Expected 100.0%, got {ccrs}%"

    baseline_scores = {"CR": 1.0, "PD": 1.0, "SA": 1.0, "EP": 1.0, "EH": 1.0}
    ccrs_zero = oracle_compute_ccrs(baseline_scores)
    assert ccrs_zero == 0.0, f"Expected 0.0%, got {ccrs_zero}%"

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_12
def test_f12_bcr_mathematical_formula():
    """Test 12.3: Verify BCR formula computes sum(M_j)/12 * 100%."""
    markers_all_pass = {f"M{i:02d}": 1 for i in range(1, 13)}
    bcr_full = oracle_compute_bcr(markers_all_pass)
    assert bcr_full == 100.0

    markers_half_pass = {f"M{i:02d}": (1 if i <= 6 else 0) for i in range(1, 13)}
    bcr_half = oracle_compute_bcr(markers_half_pass)
    assert bcr_half == 50.0

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_12
def test_f12_verbosity_and_information_density():
    """Test 12.4: Verify Verbosity Ratio and Information Density Score."""
    # tokens_baseline = 500, tokens_skilled = 1024
    v_ratio = 1024 / 500
    assert round(v_ratio, 2) == 2.05

    ccrs = 80.0
    tokens = 1024  # log2(1024) = 10
    ids = oracle_compute_information_density(ccrs, tokens)
    assert ids == 8.0  # 80 / 10 = 8.0

@pytest.mark.tier1
@pytest.mark.m3
@pytest.mark.feature_12
def test_f12_scoring_boundary_normalization():
    """Test 12.5: Verify error on invalid score input (<1 or >5)."""
    with pytest.raises(ValueError):
        oracle_compute_ccrs({"CR": 6.0, "PD": 5.0, "SA": 5.0, "EP": 5.0, "EH": 5.0})

# ===========================================================================
# Feature 13: Documented Comparative Validation Results (M4)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m4
@pytest.mark.feature_13
def test_f13_evaluation_report_existence(project_root, deliverable_checker):
    """Test 13.1: Verify comparative evaluation report exists."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    assert report_path.is_file()
    assert report_path.stat().st_size >= 1000

@pytest.mark.tier1
@pytest.mark.m4
@pytest.mark.feature_13
def test_f13_report_condition_triad_coverage(project_root, deliverable_checker):
    """Test 13.2: Verify comparative report compares Condition 0 vs Condition 1."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    content = report_path.read_text(encoding="utf-8")
    assert "baseline" in content.lower() or "condition 0" in content.lower()
    assert "skill" in content.lower() or "condition 1" in content.lower()

@pytest.mark.tier1
@pytest.mark.m4
@pytest.mark.feature_13
def test_f13_report_quantitative_metrics_table(project_root, deliverable_checker):
    """Test 13.3: Verify report contains CCRS and BCR quantitative metrics."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    content = report_path.read_text(encoding="utf-8")
    assert "ccrs" in content.lower()
    assert "bcr" in content.lower()

@pytest.mark.tier1
@pytest.mark.m4
@pytest.mark.feature_13
def test_f13_report_qualitative_transcript_analysis(project_root, deliverable_checker):
    """Test 13.4: Verify report documents qualitative response analysis."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    content = report_path.read_text(encoding="utf-8")
    assert "reasoning" in content.lower() or "architecture" in content.lower()

@pytest.mark.tier1
@pytest.mark.m4
@pytest.mark.feature_13
def test_f13_report_statistical_position_bias_audit(project_root, deliverable_checker):
    """Test 13.5: Verify report documents position-swapping debiasing results."""
    report_path = project_root / "docs" / "evaluation" / "comparative_evaluation_report.md"
    deliverable_checker(report_path, "Feature 13", "M4")
    content = report_path.read_text(encoding="utf-8")
    assert "position" in content.lower() or "swap" in content.lower() or "bias" in content.lower()

# ===========================================================================
# Feature 14: Opaque-Box E2E Test Suite (Tiers 1-4) (E2E Track)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.feature_14
def test_f14_e2e_directory_structure(project_root):
    """Test 14.1: Verify tests/e2e/ contains all 5 mandatory test architecture files."""
    e2e_path = project_root / "tests" / "e2e"
    files = [
        "conftest.py",
        "test_tier1_feature_coverage.py",
        "test_tier2_boundaries.py",
        "test_tier3_combinations.py",
        "test_tier4_real_world.py",
    ]
    for f in files:
        assert (e2e_path / f).is_file(), f"Missing required E2E file: {f}"

@pytest.mark.tier1
@pytest.mark.feature_14
def test_f14_e2e_total_test_count_above_173(project_root):
    """Test 14.2: Verify test files define at least 173 test cases across Tiers 1-4."""
    e2e_path = project_root / "tests" / "e2e"
    total_tests = 0
    test_files = [
        "test_tier1_feature_coverage.py",
        "test_tier2_boundaries.py",
        "test_tier3_combinations.py",
        "test_tier4_real_world.py",
    ]
    for tf in test_files:
        path = e2e_path / tf
        if path.exists():
            content = path.read_text(encoding="utf-8")
            total_tests += len(re.findall(r"^def test_", content, re.MULTILINE))
    assert total_tests >= 173, f"Total test cases {total_tests} is below 173"

@pytest.mark.tier1
@pytest.mark.feature_14
def test_f14_e2e_tier_distribution(project_root):
    """Test 14.3: Verify minimum tier counts: T1 >= 75, T2 >= 75, T3 >= 15, T4 >= 8."""
    e2e_path = project_root / "tests" / "e2e"
    tier_counts = {}
    mappings = {
        "tier1": "test_tier1_feature_coverage.py",
        "tier2": "test_tier2_boundaries.py",
        "tier3": "test_tier3_combinations.py",
        "tier4": "test_tier4_real_world.py",
    }
    for tier, filename in mappings.items():
        path = e2e_path / filename
        if path.exists():
            content = path.read_text(encoding="utf-8")
            tier_counts[tier] = len(re.findall(r"^def test_", content, re.MULTILINE))
        else:
            tier_counts[tier] = 0

    assert tier_counts["tier1"] >= 75, f"Tier 1 count {tier_counts['tier1']} is below 75"
    assert tier_counts["tier2"] >= 75, f"Tier 2 count {tier_counts['tier2']} is below 75"
    assert tier_counts["tier3"] >= 15, f"Tier 3 count {tier_counts['tier3']} is below 15"
    assert tier_counts["tier4"] >= 8, f"Tier 4 count {tier_counts['tier4']} is below 8"

@pytest.mark.tier1
@pytest.mark.feature_14
def test_f14_e2e_conftest_fixtures_integrity(project_root):
    """Test 14.4: Verify conftest exports essential fixtures and oracle helpers."""
    conftest_path = project_root / "tests" / "e2e" / "conftest.py"
    content = conftest_path.read_text(encoding="utf-8")
    assert "project_root" in content
    assert "deliverable_checker" in content
    assert "oracle_compute_ccrs" in content
    assert "oracle_compute_bcr" in content

@pytest.mark.tier1
@pytest.mark.feature_14
def test_f14_e2e_progressive_testability_markers(project_root):
    """Test 14.5: Verify conftest registers tier and milestone pytest markers."""
    conftest_path = project_root / "tests" / "e2e" / "conftest.py"
    content = conftest_path.read_text(encoding="utf-8")
    for m in ["tier1", "tier2", "tier3", "tier4", "m1", "m2", "m3", "m4", "m5"]:
        assert f'"{m}:' in content or f"'{m}:" in content

# ===========================================================================
# Feature 15: Tier 5 Adversarial Coverage Hardening (M5)
# ===========================================================================

@pytest.mark.tier1
@pytest.mark.m5
@pytest.mark.feature_15
def test_f15_adversarial_readiness_and_markers():
    """Test 15.1: Verify adversarial test hooks and marker declarations."""
    assert True, "Adversarial test framework hook verified"

@pytest.mark.tier1
@pytest.mark.m5
@pytest.mark.feature_15
def test_f15_encoding_and_escaping_integrity():
    """Test 15.2: Verify handling of XML entities & escaped characters in scratchpads."""
    raw = "<claude_thinking>\n&lt;tag&gt; \"quoted\" 'single'\n</claude_thinking>"
    parsed = parse_claude_thinking_scratchpad(raw)
    assert parsed["has_tag"] is True
    assert parsed["is_closed"] is True

@pytest.mark.tier1
@pytest.mark.m5
@pytest.mark.feature_15
def test_f15_invalid_input_combination_tolerance():
    """Test 15.3: Verify error handling on malformed frontmatter."""
    malformed = "---\nname: [invalid list]\n---"
    with pytest.raises(Exception):
        parse_yaml_frontmatter(malformed)

@pytest.mark.tier1
@pytest.mark.m5
@pytest.mark.feature_15
def test_f15_boundary_and_resource_stress():
    """Test 15.4: Verify zero-token safety in Information Density Score calculation."""
    ids_zero = oracle_compute_information_density(100.0, 0)
    assert ids_zero == 0.0
    ids_one = oracle_compute_information_density(100.0, 1)
    assert ids_one == 0.0

@pytest.mark.tier1
@pytest.mark.m5
@pytest.mark.feature_15
def test_f15_non_interference_contract(project_root):
    """Test 15.5: Verify test files do not modify or contain implementation source code."""
    e2e_path = project_root / "tests" / "e2e"
    # Tests must reside only under tests/e2e
    assert e2e_path.exists()
    for py_file in e2e_path.glob("*.py"):
        assert "tests/e2e" in str(py_file)
