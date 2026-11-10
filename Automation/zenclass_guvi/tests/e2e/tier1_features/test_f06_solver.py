"""
Test Feature 6: Autonomous Python 3 Solver.
Verifies algorithmic code synthesis for standard programming patterns.
"""

import ast
import unittest
from tests.e2e.harness.contract_loader import get_code_generator
from tests.e2e.harness.reference_oracle import CANONICAL_PROBLEMS


class TestFeature06PythonSolver(unittest.TestCase):
    """Verifies Autonomous Python 3 Solver specifications from PROJECT.md §Feature 6 & ORIGINAL_REQUEST §R2."""

    def setUp(self):
        self.solver, self.source = get_code_generator()

    def test_synthesize_valid_python_syntax(self):
        """Authoritative source: PROJECT.md §7 - returns valid candidate Python 3 source code."""
        for slug in CANONICAL_PROBLEMS:
            code = self.solver(slug)
            self.assertIsInstance(code, str)
            self.assertTrue(len(code.strip()) > 0)
            # Must parse without syntax errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                self.fail(f"Generated code for '{slug}' failed AST syntax validation: {e}")

    def test_synthesized_code_includes_stdin_handling(self):
        """Verifies candidate solution reads from standard input and writes to standard output."""
        code = self.solver("odd-or-even-sum")
        self.assertTrue("sys.stdin" in code or "input(" in code)
        self.assertIn("print", code)


if __name__ == "__main__":
    unittest.main()
