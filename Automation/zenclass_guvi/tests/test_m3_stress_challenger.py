"""
tests/test_m3_stress_challenger.py
Adversarial empirical stress suite for Milestone 3 Iteration 2 Gate Review.
Authored by challenger_m3_iter2_1 to empirically probe:
  1. inject_code signature, parameter combinations, and type error resilience.
  2. Integration between guvi_driver.solve_problem() and ace_adapter.inject_code().
  3. autospec=True sensitivity oracle (verifying it catches divergence).
  4. AceEditorAdapter edge cases: large code payloads, Unicode, malformed pages, fallback paths.
  5. Static & dynamic forensic audit for mock shims.
  6. Negative conditions & boundary behavior in solve_problem pipeline.
"""

import inspect
import sys
import unittest
from unittest.mock import MagicMock, patch

from solver.ace_adapter import AceEditorAdapter, inject_code, get_editor_code
from drivers.guvi_driver import GuviDriver
from solver.extractor import ProblemSpecification, SampleCase
from solver.code_generator import GeneratedSolution
from solver.test_runner import ValidationResult, TestCaseResult
from core.state_manager import StateManager, TaskStatus, TaskResult


class TestAceAdapterSignatureAndStress(unittest.TestCase):
    """Empirically stress-test inject_code signature, parameter permutations, and edge inputs."""

    def test_signature_inspection(self):
        """Verify inspect.signature has page, code, verify=True with default value."""
        sig = inspect.signature(inject_code)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["page", "code", "verify"])
        self.assertTrue(sig.parameters["verify"].default is True)

        adapter_sig = inspect.signature(AceEditorAdapter.inject_code)
        adapter_params = list(adapter_sig.parameters.keys())
        self.assertEqual(adapter_params, ["self", "page", "code", "verify"])
        self.assertTrue(adapter_sig.parameters["verify"].default is True)

    def test_inject_code_parameter_permutations(self):
        """Verify all calling conventions do not raise TypeError."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "print(1)"

        # 1. Positional (page, code) -> verify defaults to True
        res1 = inject_code(mock_page, "print(1)")
        self.assertTrue(res1)

        # 2. Positional + Keyword verify=True
        res2 = inject_code(mock_page, "print(1)", verify=True)
        self.assertTrue(res2)

        # 3. Positional + Keyword verify=False
        res3 = inject_code(mock_page, "print(1)", verify=False)
        self.assertTrue(res3)

        # 4. Positional (page, code, True)
        res4 = inject_code(mock_page, "print(1)", True)
        self.assertTrue(res4)

        # 5. Positional (page, code, False)
        res5 = inject_code(mock_page, "print(1)", False)
        self.assertTrue(res5)

        # 6. Keyword-only args
        res6 = inject_code(page=mock_page, code="print(1)", verify=True)
        self.assertTrue(res6)
        res7 = inject_code(page=mock_page, code="print(1)", verify=False)
        self.assertTrue(res7)

    def test_inject_code_edge_inputs(self):
        """Test edge case inputs: None code, empty code, unicode, 100k char payload."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = ""

        # None code should normalize to ""
        self.assertTrue(inject_code(mock_page, None, verify=False))

        # Empty code
        self.assertTrue(inject_code(mock_page, "", verify=False))

        # Windows CRLF normalization
        crlf_code = "line1\r\ndef test():\r\n    return True\r\n"
        mock_page.evaluate.return_value = "line1\ndef test():\n    return True\n"
        self.assertTrue(inject_code(mock_page, crlf_code, verify=True))

        # Large payload stress test (50,000 lines)
        large_code = "\n".join([f"x_{i} = {i}" for i in range(50000)])
        mock_page.evaluate.return_value = large_code
        self.assertTrue(inject_code(mock_page, large_code, verify=True))

    def test_verify_flag_behavior(self):
        """Verify that verify=True queries editor buffer, while verify=False does not."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "some_code"

        # With verify=False, evaluate should NOT be called for verification
        mock_page.reset_mock()
        inject_code(mock_page, "some_code", verify=False)
        # keyboard.insert_text should be called
        mock_page.keyboard.insert_text.assert_called_once_with("some_code")
        # evaluate should NOT be called
        mock_page.evaluate.assert_not_called()

        # With verify=True, evaluate should be called to verify buffer
        mock_page.reset_mock()
        inject_code(mock_page, "some_code", verify=True)
        mock_page.keyboard.insert_text.assert_called_once_with("some_code")
        mock_page.evaluate.assert_called()

    def test_keyboard_failure_fallback_to_js(self):
        """When keyboard throws exception, verify it gracefully falls back to JS API."""
        mock_page = MagicMock()
        mock_page.keyboard.press.side_effect = RuntimeError("CDP disconnected")
        mock_page.evaluate.return_value = True  # JS fallback succeeds

        adapter = AceEditorAdapter()
        res = adapter.inject_code(mock_page, "x = 42", verify=False)
        self.assertTrue(res)
        mock_page.evaluate.assert_called()

    def test_both_keyboard_and_js_fail_returns_false(self):
        """When both keyboard and JS fallback fail, inject_code returns False without raising."""
        mock_page = MagicMock()
        mock_page.keyboard = None
        mock_page.evaluate.return_value = False

        adapter = AceEditorAdapter()
        res = adapter.inject_code(mock_page, "x = 42", verify=False)
        self.assertFalse(res)

    def test_malformed_page_without_attributes(self):
        """When page object is a dummy object without keyboard or evaluate."""
        class DummyObject:
            pass

        dummy = DummyObject()
        adapter = AceEditorAdapter()
        res = adapter.inject_code(dummy, "x = 42", verify=True)
        self.assertFalse(res)

        code = adapter.get_code(dummy)
        self.assertEqual(code, "")


class TestAutospecSensitivityOracle(unittest.TestCase):
    """Empirically prove that autospec=True strictly catches interface signature mismatches."""

    def test_autospec_catches_invalid_verify_if_missing(self):
        """Create a dummy function without 'verify' and verify autospec rejects verify=True."""
        def old_inject_code(page, code):
            return True

        with patch("drivers.guvi_driver.inject_code", side_effect=old_inject_code, autospec=old_inject_code):
            from drivers.guvi_driver import inject_code as patched_inject
            with self.assertRaises(TypeError) as ctx:
                patched_inject("page", "code", verify=True)
            self.assertIn("unexpected keyword argument 'verify'", str(ctx.exception))

    def test_autospec_passes_with_current_inject_code(self):
        """Verify current inject_code in drivers.guvi_driver passes autospec with verify=True."""
        with patch("drivers.guvi_driver.inject_code", autospec=True) as mock_inject:
            from drivers.guvi_driver import inject_code as patched_inject
            # Calling with verify=True must succeed
            patched_inject("page", "code", verify=True)
            mock_inject.assert_called_once_with("page", "code", verify=True)

            # Calling with verify=False must succeed
            patched_inject("page", "code", verify=False)
            self.assertEqual(mock_inject.call_count, 2)


class TestSolveProblemIntegration(unittest.TestCase):
    """Empirically test solve_problem() integration with real ace_adapter and real signature."""

    def setUp(self):
        self.mock_bm = MagicMock()
        self.mock_page = MagicMock()
        self.mock_bm.get_page.return_value = self.mock_page
        self.state_manager = StateManager(":memory:")
        self.mock_hitl = MagicMock()
        self.mock_hitl.check_and_handle_guardrails.return_value = False

        self.driver = GuviDriver(
            browser_manager=self.mock_bm,
            state_manager=self.state_manager,
            hitl_handler=self.mock_hitl,
        )

    def tearDown(self):
        self.state_manager.close()

    @patch("drivers.guvi_driver.extract_problem_spec", autospec=True)
    @patch("drivers.guvi_driver.generate_solution", autospec=True)
    @patch("drivers.guvi_driver.test_solution", autospec=True)
    @patch("drivers.guvi_driver.wait_for_editor", autospec=True)
    def test_solve_problem_calls_real_ace_adapter_inject_code(
        self,
        mock_wait_editor,
        mock_test_sol,
        mock_gen_sol,
        mock_extract_spec,
    ):
        """Run solve_problem with REAL inject_code (unpatched) and verify zero TypeError."""
        mock_extract_spec.return_value = ProblemSpecification(
            title="Sample Task",
            description="Sample description",
            sample_cases=[SampleCase(input_text="1 2\n", expected_output="3\n")]
        )
        mock_gen_sol.return_value = GeneratedSolution(
            code="a, b = map(int, input().split())\nprint(a + b)\n",
            category="Math",
            confidence=1.0,
            explanation="Sum"
        )
        mock_test_sol.return_value = ValidationResult(
            all_passed=True,
            passed_count=1,
            total_count=1,
            results=[TestCaseResult(
                passed=True,
                input_data="1 2\n",
                expected_output="3\n",
                actual_output="3\n",
                error_message="",
                duration=0.01,
            )]
        )
        mock_wait_editor.return_value = True

        # Setup mock_page to satisfy real AceEditorAdapter injection & verification
        sol_code = "a, b = map(int, input().split())\nprint(a + b)\n"
        def fake_evaluate(script, *args):
            if isinstance(script, str) and "getValue" in script:
                return sol_code
            if isinstance(script, str) and "el.value" in script:
                return "PYTHON 3"
            return True

        self.mock_page.evaluate.side_effect = fake_evaluate
        self.mock_page.keyboard.insert_text = MagicMock()
        self.mock_page.click = MagicMock()

        # DOM UI elements for Run and Submit
        qs_status = MagicMock()
        qs_status.inner_text.return_value = "Solved!"
        modal_elem = MagicMock()
        modal_elem.is_visible.return_value = True
        modal_elem.inner_text.return_value = "Congratulations! You have earned +30 Geekoins"

        def fake_qs(sel):
            if "question-status" in sel:
                return qs_status
            if "success_modal" in sel or "Geekoins" in sel:
                return modal_elem
            return MagicMock()

        self.mock_page.query_selector.side_effect = fake_qs

        # drivers.guvi_driver.inject_code is NOT patched!
        result = self.driver.solve_problem("sample-task")

        self.assertTrue(result["success"])
        self.assertEqual(result["points"], 30)
        self.mock_page.keyboard.insert_text.assert_called_once_with(sol_code)

    @patch("drivers.guvi_driver.extract_problem_spec", autospec=True)
    @patch("drivers.guvi_driver.generate_solution", autospec=True)
    @patch("drivers.guvi_driver.test_solution", autospec=True)
    @patch("drivers.guvi_driver.wait_for_editor", autospec=True)
    def test_solve_problem_when_real_injection_fails(
        self,
        mock_wait_editor,
        mock_test_sol,
        mock_gen_sol,
        mock_extract_spec,
    ):
        """When real inject_code returns False, solve_problem handles it cleanly with failure state."""
        mock_extract_spec.return_value = ProblemSpecification(
            title="Sample Task",
            description="Sample description",
            sample_cases=[SampleCase(input_text="1\n", expected_output="1\n")]
        )
        mock_gen_sol.return_value = GeneratedSolution(code="print(1)\n", category="Math", confidence=1.0, explanation="Print 1")
        mock_test_sol.return_value = ValidationResult(all_passed=True, passed_count=1, total_count=1, results=[])
        mock_wait_editor.return_value = True

        # Make evaluate fail to inject or verify
        self.mock_page.keyboard = None
        self.mock_page.evaluate.return_value = False

        result = self.driver.solve_problem("sample-task")
        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "ACE_INJECTION")
        task = self.state_manager.get_task("guvi-sample-task")
        self.assertEqual(task.status, TaskStatus.FAILED.value)
        self.assertEqual(task.result, TaskResult.SUBMISSION_FAILED.value)


class TestForensicAuditNoResidualShims(unittest.TestCase):
    """Forensic verification that zero mock evaluate shims exist in production driver."""

    def test_no_mock_shims_in_guvi_driver(self):
        import drivers.guvi_driver as gd
        import inspect

        source = inspect.getsource(gd)
        # Check for forbidden mock fetch calls
        self.assertNotIn("fetch('/code-kata/question/run'", source)
        self.assertNotIn("fetch('/code-kata/question/submit'", source)
        self.assertNotIn("fetch('/usercheck.php'", source)
        self.assertNotIn('fetch("/code-kata/question/run"', source)
        self.assertNotIn('fetch("/code-kata/question/submit"', source)
        self.assertNotIn('fetch("/usercheck.php"', source)

        # Check for forbidden mock DOM mutations
        self.assertNotIn("qs.textContent = 'Solved!'", source)
        self.assertNotIn('qs.textContent = "Solved!"', source)
        self.assertNotIn("modal.style.display = 'block'", source)
        self.assertNotIn('modal.style.display = "block"', source)


if __name__ == "__main__":
    unittest.main()
