"""
Dynamic Contract Loader for Progressive Testability.
Bridges E2E tests to real zenclass_guvi modules or canonical reference oracles.
"""

import sys
import os
from typing import Tuple, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.e2e.harness.reference_oracle import (
    ReferenceStateManager,
    ReferenceSandbox,
    ReferenceHITLHandler,
    ReferenceReporter,
    CANONICAL_PROBLEMS,
    ProblemSpec,
    ValidationResult,
    TaskRecord,
)


def get_state_manager(db_path: str = ":memory:") -> Tuple[Any, str]:
    """Returns (state_manager_instance, source_label)."""
    try:
        from core.state_manager import StateManager
        return StateManager(db_path), "live"
    except (ImportError, AttributeError):
        return ReferenceStateManager(db_path), "oracle"


def get_hitl_handler() -> Tuple[Any, str]:
    """Returns (hitl_handler_instance, source_label)."""
    try:
        try:
            from core.hitl_handler import HitlHandler as HandlerClass
        except ImportError:
            from core.hitl_handler import HITLHandler as HandlerClass
        return HandlerClass(interactive=False, audible_bell=False), "live"
    except (ImportError, AttributeError):
        return ReferenceHITLHandler(), "oracle"


def get_reporter() -> Tuple[Any, str]:
    """Returns (reporter_class_or_instance, source_label)."""
    try:
        from core.reporter import Reporter
        return Reporter, "live"
    except (ImportError, AttributeError):
        return ReferenceReporter, "oracle"


def get_sandbox() -> Tuple[Any, str]:
    """Returns (sandbox_class_or_instance, source_label)."""
    try:
        from solver.test_runner import SubprocessSandbox
        return SubprocessSandbox, "live"
    except (ImportError, AttributeError):
        return ReferenceSandbox, "oracle"


def get_code_generator() -> Tuple[Any, str]:
    """Returns (generator_func_or_class, source_label)."""
    try:
        from solver.code_generator import synthesize_solution
        return synthesize_solution, "live"
    except (ImportError, AttributeError):
        # Canonical solver synthesizer
        def oracle_synthesizer(spec_or_slug: Any) -> str:
            slug = getattr(spec_or_slug, "slug", str(spec_or_slug))
            if slug in CANONICAL_PROBLEMS:
                return CANONICAL_PROBLEMS[slug]["canonical_solution"]
            # Fallback algorithmic template
            return (
                "import sys\n"
                "def solve():\n"
                "    inp = sys.stdin.read().strip()\n"
                "    print(inp)\n"
                "solve()\n"
            )
        return oracle_synthesizer, "oracle"


def get_problem_extractor() -> Tuple[Any, str]:
    """Returns (extractor_func_or_class, source_label)."""
    try:
        from solver.extractor import extract_problem_spec
        return extract_problem_spec, "live"
    except (ImportError, AttributeError):
        def oracle_extractor(html_text: str) -> ProblemSpec:
            import re
            title_m = re.search(r'class="problem-title">(.*?)<', html_text)
            desc_m = re.search(r'class="problem-statement">(.*?)</div>', html_text, re.DOTALL)
            in_m = re.search(r'class="input-description">(.*?)</div>', html_text, re.DOTALL)
            out_m = re.search(r'class="output-description">(.*?)</div>', html_text, re.DOTALL)
            s_in_m = re.search(r'class="sample-input">(.*?)</div>', html_text, re.DOTALL)
            s_out_m = re.search(r'class="sample-output">(.*?)</div>', html_text, re.DOTALL)

            return ProblemSpec(
                title=title_m.group(1).strip() if title_m else "Unknown",
                description=desc_m.group(1).strip() if desc_m else "",
                input_desc=in_m.group(1).strip() if in_m else "",
                output_desc=out_m.group(1).strip() if out_m else "",
                sample_input=s_in_m.group(1).strip() if s_in_m else "",
                sample_output=s_out_m.group(1).strip() if s_out_m else ""
            )
        return oracle_extractor, "oracle"
