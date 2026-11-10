"""
test_m2_solver.py - Comprehensive Unit and Integration Test Suite for Milestone 2.

Validates:
- Problem Statement Extractor (solver/extractor.py):
  - ProblemSpecification data model, properties, and backward compatibility
  - Multi-strategy parsing (CSS classes, labeled text blocks, negative lookaheads)
  - Playwright Page mock and raw HTML string support
  - Sparse and empty HTML degradation
- Autonomous Python 3 Code Synthesizer (solver/code_generator.py):
  - Canonical solvers for known Guvi CodeKata problems
  - Algorithmic template library (Arrays, Strings, Math, Dynamic Programming)
  - AST syntax verification
  - Dual contract: generate_solution (GeneratedSolution) & synthesize_solution (str)
- Sandboxed Subprocess Test Runner (solver/test_runner.py):
  - Subprocess isolation via sys.executable
  - Stdin feeding, stdout/stderr capture, exit codes, durations
  - Strict timeout enforcement and clean process termination
  - Output normalization (CRLF -> LF, line trailing space, float tolerance)
  - Backward compatibility: ValidationResult properties & SubprocessSandbox class
- Ace Editor Adapter (solver/ace_adapter.py):
  - 4-step CDP keyboard injection sequence
  - JavaScript direct API fallback
  - Editor buffer retrieval and readiness synchronization
- Package Exports (solver/__init__.py):
  - Clean API contract exports
"""

import ast
import math
import sys
import unittest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

# Import solver components
import solver
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
    CANONICAL_SOLVERS,
)
from solver.test_runner import (
    TestCaseResult,
    ValidationResult,
    test_solution,
    validate_solution,
    SubprocessSandbox,
    normalize_output,
    outputs_match,
)
from solver.ace_adapter import (
    AceEditorAdapter,
    inject_code,
    inject_code_into_ace,
    get_editor_code,
    wait_for_editor,
)
from tests.e2e.harness.dom_fixtures import GUVI_WORKSPACE_HTML
from tests.e2e.harness.reference_oracle import CANONICAL_PROBLEMS


# =====================================================================
# 1. Problem Specification Data Model Tests
# =====================================================================

class TestProblemSpecificationDataModel(unittest.TestCase):
    """Verifies ProblemSpecification data model and backward compatibility aliases."""

    def test_default_values(self):
        spec = ProblemSpecification()
        self.assertEqual(spec.title, "Unknown")
        self.assertEqual(spec.description, "")
        self.assertEqual(spec.input_spec, "")
        self.assertEqual(spec.output_spec, "")
        self.assertEqual(spec.sample_cases, [])
        self.assertEqual(spec.constraints, "")
        self.assertEqual(spec.category, "General")
        self.assertEqual(spec.sample_input, "")
        self.assertEqual(spec.sample_output, "")
        self.assertEqual(spec.input_desc, "")
        self.assertEqual(spec.output_desc, "")

    def test_property_aliases_and_setters(self):
        spec = ProblemSpecification(
            title="Sum Problem",
            input_spec="Two ints",
            output_spec="One int",
            sample_cases=[SampleCase(input_text="1 2", expected_output="3")]
        )
        # Test getters
        self.assertEqual(spec.input_desc, "Two ints")
        self.assertEqual(spec.output_desc, "One int")
        self.assertEqual(spec.sample_input, "1 2")
        self.assertEqual(spec.sample_output, "3")

        # Test setters
        spec.input_desc = "Modified input"
        spec.output_desc = "Modified output"
        self.assertEqual(spec.input_spec, "Modified input")
        self.assertEqual(spec.output_spec, "Modified output")

    def test_slug_derivation(self):
        spec = ProblemSpecification(title="1. Odd or Even Sum")
        self.assertEqual(spec.slug, "odd-or-even-sum")

        spec_custom = ProblemSpecification(title="Custom Title", _slug="custom-slug")
        self.assertEqual(spec_custom.slug, "custom-slug")

    def test_sample_case_properties_and_serialization(self):
        sc = SampleCase(input_text="42\n", expected_output="yes", case_number=2, explanation="Basic test")
        self.assertEqual(sc.input_data, "42\n")
        self.assertEqual(sc.input, "42\n")
        self.assertEqual(sc.expected, "yes")

        sc.input_data = "100"
        self.assertEqual(sc.input_text, "100")

        d = sc.to_dict()
        self.assertEqual(d["case_number"], 2)
        self.assertEqual(d["input_text"], "100")
        self.assertEqual(d["expected_output"], "yes")
        self.assertEqual(d["explanation"], "Basic test")

    def test_problem_spec_alias(self):
        self.assertIs(ProblemSpec, ProblemSpecification)


# =====================================================================
# 2. Problem Extractor Tests
# =====================================================================

class TestProblemExtractor(unittest.TestCase):
    """Verifies extraction from HTML snippets, Playwright pages, and Qwik SSR blocks."""

    def test_extract_from_full_workspace_html(self):
        spec = extract_problem_spec(GUVI_WORKSPACE_HTML)
        self.assertEqual(spec.title, "Odd or Even Sum")
        self.assertIn("add them and state whether the sum is even or odd", spec.description)
        self.assertIn("Two integers N and M", spec.input_desc)
        self.assertIn("Print \"even\" or \"odd\"", spec.output_desc)
        self.assertEqual(spec.sample_input, "9 2")
        self.assertEqual(spec.sample_output, "odd")
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].input_text, "9 2")
        self.assertEqual(spec.sample_cases[0].expected_output, "odd")

    def test_extract_sparse_html_fallback(self):
        sparse = '<div class="problem-title">Find Min</div><div class="sample-input">5 1 2</div>'
        spec = extract_problem_spec(sparse)
        self.assertEqual(spec.title, "Find Min")
        self.assertEqual(spec.sample_input, "5 1 2")
        self.assertEqual(spec.sample_output, "")
        self.assertEqual(spec.description, "")

    def test_extract_empty_and_none(self):
        spec1 = extract_problem_spec("")
        self.assertEqual(spec1.title, "Unknown")
        self.assertEqual(spec1.sample_input, "")

        spec2 = extract_problem_spec(None)
        self.assertEqual(spec2.title, "Unknown")

        spec3 = extract_problem_spec("   \n\t  ")
        self.assertEqual(spec3.title, "Unknown")

    def test_extract_labeled_text_headings(self):
        text_html = """
        <div class="qwik-content">
          <h1>Palindrome String</h1>
          <p>Problem Statement: Determine if given string is a palindrome.</p>
          <p>Input Description: Single string without spaces.</p>
          <p>Output Description: Print yes or no.</p>
          <p>Constraints: Length <= 1000</p>
          <p>Sample Input: racecar</p>
          <p>Sample Output: yes</p>
          <p>Explanation: racecar reads the same forward and backwards.</p>
        </div>
        """
        spec = extract_problem_spec(text_html)
        self.assertEqual(spec.title, "Palindrome String")
        self.assertIn("palindrome", spec.description.lower())
        self.assertIn("single string", spec.input_spec.lower())
        self.assertIn("yes or no", spec.output_spec.lower())
        self.assertIn("1000", spec.constraints)
        self.assertEqual(spec.sample_input, "racecar")
        self.assertEqual(spec.sample_output, "yes")
        self.assertEqual(len(spec.sample_cases), 1)
        self.assertEqual(spec.sample_cases[0].explanation, "racecar reads the same forward and backwards.")

    def test_extract_multiline_sample_io(self):
        multiline_html = """
        <h1 class="problem-title">Array Sum</h1>
        <div class="sample-input">
          5
          1 2 3 4 5
        </div>
        <div class="sample-output">
          15
        </div>
        """
        spec = extract_problem_spec(multiline_html)
        self.assertIn("5\n1 2 3 4 5", spec.sample_input)
        self.assertEqual(spec.sample_output, "15")

    def test_extract_from_playwright_page_mock(self):
        mock_page = MagicMock()
        mock_page.content.return_value = GUVI_WORKSPACE_HTML
        spec = extract_problem_spec(mock_page)
        self.assertEqual(spec.title, "Odd or Even Sum")
        self.assertEqual(spec.sample_input, "9 2")


# =====================================================================
# 3. Autonomous Code Generator Tests
# =====================================================================

class TestCodeGenerator(unittest.TestCase):
    """Verifies algorithmic code synthesis and AST parsing."""

    def test_canonical_solvers_ast_syntax(self):
        for slug in ["odd-or-even-sum", "reverse-a-string", "sum-of-array", "palindrome-check", "prime-numbers-count"]:
            code = synthesize_solution(slug)
            self.assertTrue(len(code.strip()) > 0)
            try:
                tree = ast.parse(code)
                self.assertIsNotNone(tree)
            except SyntaxError as e:
                self.fail(f"Canonical solver for {slug} failed AST validation: {e}")

    def test_stdin_and_stdout_in_synthesized_code(self):
        code = synthesize_solution("odd-or-even-sum")
        self.assertTrue("sys.stdin" in code or "input(" in code)
        self.assertIn("print", code)

    def test_generate_solution_rich_metadata(self):
        sol = generate_solution("reverse-a-string")
        self.assertIsInstance(sol, GeneratedSolution)
        self.assertIn("sys.stdin", sol.code)
        self.assertEqual(sol.category, "Strings")
        self.assertGreaterEqual(sol.confidence, 0.95)
        self.assertTrue(len(sol.explanation) > 0)

    def test_synthesize_solution_from_problem_specification(self):
        spec = ProblemSpecification(title="Reverse a String")
        code = synthesize_solution(spec)
        self.assertIn("[::-1]", code)

    def test_synthesize_solution_from_dictionary(self):
        prob_dict = {"title": "Odd or Even Sum", "sample_input": "9 2", "sample_output": "odd"}
        code = synthesize_solution(prob_dict)
        self.assertIn("% 2", code)

    def test_algorithmic_template_selection(self):
        # Math gcd
        code_gcd = synthesize_solution(ProblemSpecification(title="Find GCD and LCM", description="compute greatest common divisor"))
        self.assertIn("math.gcd", code_gcd)

        # Math factorial
        code_fact = synthesize_solution(ProblemSpecification(title="Factorial Calculation", description="compute n factorial"))
        self.assertIn("math.factorial", code_fact)

        # Fibonacci
        code_fib = synthesize_solution(ProblemSpecification(title="Fibonacci Sequence", description="first n fibonacci numbers"))
        self.assertIn("fib", code_fib)

        # Kadane
        code_kadane = synthesize_solution(ProblemSpecification(title="Maximum Subarray", description="kadane algorithm largest contiguous sum"))
        self.assertIn("max_so_far", code_kadane)

        # Strings vowel count
        code_vowel = synthesize_solution(ProblemSpecification(title="Count Vowels", description="find total number of vowels"))
        self.assertIn("aeiou", code_vowel.lower())

        # Array sorting
        code_sort = synthesize_solution(ProblemSpecification(title="Sort Array", description="sort given array in ascending order"))
        self.assertIn("sort", code_sort)

        # Deduplicate
        code_dedup = synthesize_solution(ProblemSpecification(title="Remove Duplicates", description="remove duplicate numbers from array"))
        self.assertIn("seen", code_dedup)

        # Min Max
        code_min_max = synthesize_solution(ProblemSpecification(title="Find Minimum and Maximum", description="find min and max of array"))
        self.assertIn("min(nums)", code_min_max)


# =====================================================================
# 4. Subprocess Test Runner Tests
# =====================================================================

class TestSubprocessTestRunner(unittest.TestCase):
    """Verifies sandboxed subprocess execution, timeouts, and normalization."""

    def test_validate_correct_solution(self):
        code = CANONICAL_PROBLEMS["odd-or-even-sum"]["canonical_solution"]
        res = validate_solution(code, "9 2", "odd")
        self.assertTrue(res.passed)
        self.assertEqual(res.stdout, "odd")
        self.assertEqual(res.exit_code, 0)
        self.assertGreater(res.duration_ms, 0.0)
        self.assertIsNone(res.error_message)

    def test_validate_incorrect_output(self):
        wrong_code = "print('not_matching')"
        res = validate_solution(wrong_code, "9 2", "odd")
        self.assertFalse(res.passed)
        self.assertEqual(res.stdout, "not_matching")
        self.assertIn("Output mismatch", res.error_message)

    def test_validate_runtime_exception(self):
        crash_code = "import sys\nval = 10 / 0\n"
        res = validate_solution(crash_code, "", "")
        self.assertFalse(res.passed)
        self.assertNotEqual(res.exit_code, 0)
        self.assertIn("ZeroDivisionError", res.stderr)

    def test_timeout_enforcement(self):
        loop_code = "while True: pass"
        res = validate_solution(loop_code, "", "", timeout_sec=0.3)
        self.assertFalse(res.passed)
        self.assertEqual(res.exit_code, -1)
        self.assertIn("timed out", (res.error_message or "").lower())
        self.assertEqual(res.stderr, "TimeoutExpired")

    def test_empty_code_and_empty_output_boundary(self):
        res = validate_solution("", "", "")
        self.assertTrue(res.passed)
        self.assertEqual(res.stdout, "")
        self.assertEqual(res.exit_code, 0)

    def test_empty_code_non_empty_output(self):
        res = validate_solution("", "", "expected_something")
        self.assertFalse(res.passed)
        self.assertEqual(res.exit_code, 1)

    def test_unicode_and_special_characters(self):
        code = "import sys\nprint('Processed: ' + sys.stdin.read().strip() + ' 🚀')"
        res = validate_solution(code, "Hello 世界", "Processed: Hello 世界 🚀")
        self.assertTrue(res.passed)

    def test_output_normalization_crlf_and_trailing_spaces(self):
        self.assertEqual(normalize_output("line 1   \r\nline 2   \r\n"), "line 1\nline 2")
        self.assertEqual(normalize_output("\n\nhello\n\n"), "hello")

    def test_float_numerical_tolerance(self):
        self.assertTrue(outputs_match("3.141592", "3.1416"))
        self.assertTrue(outputs_match("10.00001 20.00002", "10.0 20.0"))
        self.assertFalse(outputs_match("10.5", "10.0"))

    def test_case_insensitive_keywords(self):
        self.assertTrue(outputs_match("YES", "yes"))
        self.assertTrue(outputs_match("Even", "EVEN"))
        self.assertTrue(outputs_match("True", "true"))

    def test_multi_case_test_solution(self):
        code = CANONICAL_PROBLEMS["odd-or-even-sum"]["canonical_solution"]
        cases = [
            SampleCase(input_text="9 2", expected_output="odd"),
            SampleCase(input_text="10 20", expected_output="even"),
            SampleCase(input_text="3 3", expected_output="even"),
        ]
        val = test_solution(code, cases)
        self.assertTrue(val.all_passed)
        self.assertTrue(val.passed)
        self.assertEqual(val.passed_count, 3)
        self.assertEqual(val.total_count, 3)
        self.assertEqual(len(val.results), 3)

    def test_subprocess_sandbox_class_contract(self):
        code = "import sys; print(sys.stdin.read().strip())"
        res = SubprocessSandbox.validate_solution(code, "echo_test", "echo_test")
        self.assertTrue(res.passed)
        self.assertEqual(res.stdout, "echo_test")


# =====================================================================
# 5. Ace Editor Adapter Tests
# =====================================================================

class TestAceEditorAdapter(unittest.TestCase):
    """Verifies Ace Editor CDP keyboard injection and JavaScript fallback."""

    def test_cdp_keyboard_injection_sequence(self):
        """Simulates Playwright Page to record the 4-step CDP injection sequence."""
        mock_page = MagicMock()
        recorded_calls = []

        mock_page.click.side_effect = lambda sel, **kw: recorded_calls.append(("click", sel))
        mock_page.keyboard.press.side_effect = lambda key: recorded_calls.append(("press", key))
        mock_page.keyboard.insert_text.side_effect = lambda text: recorded_calls.append(("insert_text", text))
        # Mock evaluate for verification check
        sample_code = "print('Hello Guvi')"
        mock_page.evaluate.return_value = sample_code

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, sample_code, verify=True)

        self.assertTrue(success)
        self.assertEqual(recorded_calls[0], ("click", "#editor textarea.ace_text-input"))
        # Modifier check: Meta on darwin, Control on others
        expected_mod = "Meta+A" if sys.platform == "darwin" else "Control+A"
        self.assertEqual(recorded_calls[1], ("press", expected_mod))
        self.assertEqual(recorded_calls[2], ("press", "Backspace"))
        self.assertEqual(recorded_calls[3], ("insert_text", sample_code))

    def test_js_api_fallback_when_keyboard_fails(self):
        """Verifies direct JS evaluation when keyboard injection raises exception."""
        mock_page = MagicMock()
        mock_page.click.side_effect = Exception("Element not clickable")
        # JS evaluate returns True on setValue and matches code on getValue
        sample_code = "print('Fallback')"
        mock_page.evaluate.side_effect = lambda script, arg=None: sample_code if "getValue" in script else True

        adapter = AceEditorAdapter()
        success = adapter.inject_code(mock_page, sample_code, verify=True)
        self.assertTrue(success)

    def test_get_editor_code(self):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "def solve(): pass"
        code = get_editor_code(mock_page)
        self.assertEqual(code, "def solve(): pass")

    def test_wait_for_editor(self):
        mock_page = MagicMock()
        mock_page.wait_for_selector.return_value = None
        mock_page.wait_for_function.return_value = None
        self.assertTrue(wait_for_editor(mock_page, timeout=1.0))

    def test_alias_inject_code_into_ace(self):
        self.assertIs(inject_code_into_ace, inject_code)


# =====================================================================
# 6. Package Exports Tests
# =====================================================================

class TestPackageExports(unittest.TestCase):
    """Verifies that solver package exposes all required public symbols."""

    def test_clean_package_exports(self):
        expected_symbols = [
            "SampleCase", "ProblemSpecification", "ProblemSpec", "ProblemExtractor", "extract_problem_spec",
            "GeneratedSolution", "generate_solution", "synthesize_solution",
            "TestCaseResult", "ValidationResult", "test_solution", "validate_solution", "SubprocessSandbox",
            "AceEditorAdapter", "inject_code", "inject_code_into_ace", "get_editor_code", "wait_for_editor"
        ]
        for sym in expected_symbols:
            self.assertTrue(hasattr(solver, sym), f"solver package missing export: {sym}")
            self.assertIn(sym, solver.__all__)


if __name__ == "__main__":
    unittest.main()
