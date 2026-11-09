"""
Pytest configuration and shared fixtures for the Claude Antigravity Skill E2E test suite.
Provides opaque-box fixtures, path locators, schema validators, and progressive testability helpers.
"""

import os
import re
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
import pytest
import yaml

# ---------------------------------------------------------------------------
# Pytest Configuration & Markers
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    """Add CLI options for progressive testability."""
    parser.addoption(
        "--allow-pending",
        action="store_true",
        default=False,
        help="Skip tests when target milestone deliverables are pending rather than failing.",
    )

def pytest_configure(config):
    """Register custom markers for tiers, milestones, and features."""
    config.addinivalue_line("markers", "tier1: Tier 1 Feature Coverage tests (≥5 tests per feature)")
    config.addinivalue_line("markers", "tier2: Tier 2 Boundary & Corner Case tests (≥5 tests per feature)")
    config.addinivalue_line("markers", "tier3: Tier 3 Cross-Feature Combination interaction tests")
    config.addinivalue_line("markers", "tier4: Tier 4 Real-World Application Scenario tests")
    config.addinivalue_line("markers", "tier5: Tier 5 Adversarial Coverage Hardening tests")
    config.addinivalue_line("markers", "m1: Milestone 1 Research Report tests")
    config.addinivalue_line("markers", "m2: Milestone 2 Antigravity Skill Specification Package tests")
    config.addinivalue_line("markers", "m3: Milestone 3 Comparative Evaluation Suite tests")
    config.addinivalue_line("markers", "m4: Milestone 4 Empirical Validation Report tests")
    config.addinivalue_line("markers", "m5: Milestone 5 100% Pass and Hardening tests")
    for i in range(1, 16):
        config.addinivalue_line("markers", f"feature_{i}: Tests covering Feature {i}")

# ---------------------------------------------------------------------------
# Path Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Returns absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent.parent

@pytest.fixture(scope="session")
def skills_dir(project_root: Path) -> Path:
    """Returns absolute path to the skills/claude directory."""
    return project_root / "skills" / "claude"

@pytest.fixture(scope="session")
def docs_dir(project_root: Path) -> Path:
    """Returns absolute path to the docs directory."""
    return project_root / "docs"

@pytest.fixture(scope="session")
def eval_dir(project_root: Path) -> Path:
    """Returns absolute path to the tests/evaluation directory."""
    return project_root / "tests" / "evaluation"

@pytest.fixture(scope="session")
def results_dir(project_root: Path) -> Path:
    """Returns absolute path to the results directory."""
    return project_root / "results"

@pytest.fixture(scope="session")
def e2e_dir(project_root: Path) -> Path:
    """Returns absolute path to the tests/e2e directory."""
    return project_root / "tests" / "e2e"

# ---------------------------------------------------------------------------
# Progressive Testability Helper
# ---------------------------------------------------------------------------

@pytest.fixture
def deliverable_checker(request):
    """
    Returns a callable that checks if a deliverable exists.
    If missing and --allow-pending is active, skips the test.
    Otherwise asserts presence with a descriptive failure message.
    """
    allow_pending = request.config.getoption("--allow-pending", default=False)

    def _check(path: Path, feature_id: str, milestone: str) -> Path:
        if not path.exists():
            msg = f"Deliverable missing: '{path}' for {feature_id} (Milestone {milestone})"
            if allow_pending:
                pytest.skip(msg)
            else:
                pytest.fail(msg)
        return path

    return _check

# ---------------------------------------------------------------------------
# Authoritative Oracle Data & Specifications
# ---------------------------------------------------------------------------

CANONICAL_CCRS_WEIGHTS = {
    "CR": 0.20,
    "PD": 0.20,
    "SA": 0.25,
    "EP": 0.20,
    "EH": 0.15,
}

CANONICAL_12_MARKERS = [
    {"id": "M01", "name": "Deliberate Scratchpad / Pacing"},
    {"id": "M02", "name": "Premise Integrity Check"},
    {"id": "M03", "name": "Stated vs. Inferred Delineation"},
    {"id": "M04", "name": "MECE Decomposition"},
    {"id": "M05", "name": "Typed Interface Contracts"},
    {"id": "M06", "name": "Failure Domain Modeling"},
    {"id": "M07", "name": "Trade-Off Justification"},
    {"id": "M08", "name": "Dependency Ordering (DAG)"},
    {"id": "M09", "name": "Falsifiable Verification Commands"},
    {"id": "M10", "name": "Rollback & Abort Strategy"},
    {"id": "M11", "name": "Boundary & Edge Case Enumeration"},
    {"id": "M12", "name": "Resistance to Hallucination"},
]

CANONICAL_15_BENCHMARK_IDS = [
    "TC-CR-01", "TC-CR-02", "TC-CR-03",
    "TC-PD-01", "TC-PD-02", "TC-PD-03",
    "TC-SA-01", "TC-SA-02", "TC-SA-03",
    "TC-EP-01", "TC-EP-02", "TC-EP-03",
    "TC-EH-01", "TC-EH-02", "TC-EH-03",
]

@pytest.fixture(scope="session")
def ccrs_weights() -> Dict[str, float]:
    return dict(CANONICAL_CCRS_WEIGHTS)

@pytest.fixture(scope="session")
def canonical_markers() -> List[Dict[str, str]]:
    return list(CANONICAL_12_MARKERS)

@pytest.fixture(scope="session")
def canonical_benchmark_ids() -> List[str]:
    return list(CANONICAL_15_BENCHMARK_IDS)

# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

def parse_yaml_frontmatter(content: str) -> Dict[str, Any]:
    """
    Extracts and parses YAML frontmatter enclosed in '---'.
    Raises ValueError if frontmatter delimiters or YAML syntax are invalid.
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        raise ValueError("Invalid frontmatter: content must start with triple-hyphen delimiters '---'")
    raw_yaml = match.group(1)
    body = match.group(2)
    parsed = yaml.safe_load(raw_yaml)
    if not isinstance(parsed, dict):
        raise ValueError(f"Frontmatter did not parse into a dictionary: {type(parsed)}")
    parsed["__body__"] = body
    return parsed

def validate_skill_metadata(frontmatter: Dict[str, Any]) -> List[str]:
    """
    Validates skill frontmatter according to Antigravity runtime requirements:
    - name: required, matches ^[A-Za-z0-9._-]{1,64}$
    - description: required, non-empty, contains 3rd-person trigger instruction
    - disable-slash-command: boolean if present
    - disable-model-invocation: boolean if present
    """
    errors = []
    name = frontmatter.get("name")
    if not name:
        errors.append("Missing required frontmatter field: 'name'")
    elif not isinstance(name, str):
        errors.append("Frontmatter 'name' must be a string")
    elif not re.match(r"^[A-Za-z0-9._-]{1,64}$", name):
        errors.append(f"Frontmatter 'name' '{name}' violates regex '^[A-Za-z0-9._-]{{1,64}}$'")

    desc = frontmatter.get("description")
    if not desc:
        errors.append("Missing required frontmatter field: 'description'")
    elif not isinstance(desc, str) or len(desc.strip()) < 10:
        errors.append("Frontmatter 'description' must be a non-empty string with substantive description")

    for flag in ["disable-slash-command", "disable-model-invocation"]:
        if flag in frontmatter and not isinstance(frontmatter[flag], bool):
            errors.append(f"Frontmatter '{flag}' must be a boolean")

    return errors

def parse_claude_thinking_scratchpad(text: str) -> Dict[str, Any]:
    """
    Parses <claude_thinking>...</claude_thinking> block and extracts the 4 mandatory phases.
    Returns dictionary with parsed phases and validation status.
    """
    res = {
        "has_tag": False,
        "is_closed": False,
        "phases_found": [],
        "errors": [],
    }
    open_tag = "<claude_thinking>"
    close_tag = "</claude_thinking>"

    if open_tag not in text:
        res["errors"].append("Missing <claude_thinking> opening tag")
        return res
    res["has_tag"] = True

    if close_tag not in text:
        res["errors"].append("Missing </claude_thinking> closing tag (unclosed scratchpad)")
        return res
    res["is_closed"] = True

    # Extract inner content
    start = text.index(open_tag) + len(open_tag)
    end = text.index(close_tag)
    if end < start:
        res["errors"].append("Malformed tags: closing tag appears before opening tag")
        return res

    inner = text[start:end]

    # Check for the 4 phases
    phases = [
        ("PHASE 1", r"(?:PHASE\s*1|Phase\s*1).*?(?:CONSTRAINT|Constraint)"),
        ("PHASE 2", r"(?:PHASE\s*2|Phase\s*2).*?(?:HYPOTHESIS|Hypothesis|COUNTER|Counter)"),
        ("PHASE 3", r"(?:PHASE\s*3|Phase\s*3).*?(?:ARCHITECTURAL|Architectural|BLUEPRINT|Blueprint)"),
        ("PHASE 4", r"(?:PHASE\s*4|Phase\s*4).*?(?:OUTPUT|Output|CALIBRATION|Calibration|RESTRAINT|Restraint)"),
    ]

    last_pos = -1
    for name, pattern in phases:
        match = re.search(pattern, inner, re.IGNORECASE)
        if match:
            res["phases_found"].append(name)
            if match.start() < last_pos:
                res["errors"].append(f"Out-of-order phase detected: {name} appears before previous phase")
            last_pos = match.start()
        else:
            res["errors"].append(f"Missing mandatory scratchpad phase: {name}")

    return res

def oracle_compute_ccrs(scores: Dict[str, float]) -> float:
    """
    Computes CCRS according to the canonical formula:
    CCRS = sum(w_i * (S_i - 1) / 4) * 100%
    scores dictionary must map 'CR', 'PD', 'SA', 'EP', 'EH' to scores in [1, 5].
    """
    weights = CANONICAL_CCRS_WEIGHTS
    for dim, w in weights.items():
        if dim not in scores:
            raise ValueError(f"Missing dimension in scores: {dim}")
        s = scores[dim]
        if s < 1.0 or s > 5.0:
            raise ValueError(f"Score for {dim} out of range [1, 5]: {s}")

    weighted_sum = sum(weights[dim] * ((scores[dim] - 1.0) / 4.0) for dim in weights)
    return round(weighted_sum * 100.0, 4)

def oracle_compute_bcr(markers: Dict[str, int]) -> float:
    """
    Computes BCR according to the canonical formula:
    BCR = sum(M_j) / 12 * 100%
    markers dictionary must contain M01..M12 as integers in {0, 1}.
    """
    if len(markers) != 12:
        raise ValueError(f"Expected 12 markers, got {len(markers)}")
    total = 0
    for i in range(1, 13):
        m_id = f"M{i:02d}"
        if m_id not in markers:
            raise ValueError(f"Missing marker: {m_id}")
        val = markers[m_id]
        if val not in (0, 1):
            raise ValueError(f"Marker {m_id} value must be 0 or 1, got {val}")
        total += val
    return round((total / 12.0) * 100.0, 4)

def oracle_compute_information_density(ccrs: float, token_count: int) -> float:
    """Computes IDS = CCRS / log2(token_count). Guards against zero/one tokens."""
    if token_count <= 1:
        return 0.0
    return round(ccrs / math.log2(token_count), 4)

@pytest.fixture(scope="session")
def oracle_helpers():
    """Provides oracle calculation helper methods to tests."""
    return {
        "compute_ccrs": oracle_compute_ccrs,
        "compute_bcr": oracle_compute_bcr,
        "compute_ids": oracle_compute_information_density,
        "parse_frontmatter": parse_yaml_frontmatter,
        "validate_metadata": validate_skill_metadata,
        "parse_thinking": parse_claude_thinking_scratchpad,
    }
