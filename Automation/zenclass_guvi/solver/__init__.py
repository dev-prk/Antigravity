"""
solver - Autonomous Problem Solving and Sandboxed Execution Package.
"""

from solver.extractor import (
    SampleCase,
    ProblemSpecification,
    ProblemSpec,
    ProblemExtractor,
    extract_problem_spec,
)
from solver.code_generator import (
    GeneratedSolution,
    generate_solution,
    synthesize_solution,
)
from solver.test_runner import (
    TestCaseResult,
    ValidationResult,
    test_solution,
    validate_solution,
    SubprocessSandbox,
)
from solver.ace_adapter import (
    AceEditorAdapter,
    inject_code,
    inject_code_into_ace,
    get_editor_code,
    wait_for_editor,
)
from solver.project_synthesizer import (
    ProjectSynthesizer,
    ProjectSpec as ProjectSynthesisSpec,
    ProjectType,
    SynthesisResult,
)
from solver.project_validator import (
    ProjectValidator,
    ProjectValidationResult,
    ValidationReport,
    HTMLTagValidator,
)

__all__ = [
    # Extractor
    "SampleCase",
    "ProblemSpecification",
    "ProblemSpec",
    "ProblemExtractor",
    "extract_problem_spec",
    # Code Generator
    "GeneratedSolution",
    "generate_solution",
    "synthesize_solution",
    # Test Runner & Sandbox
    "TestCaseResult",
    "ValidationResult",
    "test_solution",
    "validate_solution",
    "SubprocessSandbox",
    # Ace Editor Adapter
    "AceEditorAdapter",
    "inject_code",
    "inject_code_into_ace",
    "get_editor_code",
    "wait_for_editor",
    # Project Synthesizer & Validator
    "ProjectSynthesizer",
    "ProjectSynthesisSpec",
    "ProjectType",
    "SynthesisResult",
    "ProjectValidator",
    "ProjectValidationResult",
    "ValidationReport",
    "HTMLTagValidator",
]

