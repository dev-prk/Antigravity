"""
Empirical verification script for Explorer Iteration 2 - 3
Tests root causes and fix hypotheses.
"""
import ast
import re
import sys
import os

# Add zenclass_guvi to sys.path
sys.path.insert(0, "/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi")

from solver.code_generator import generate_solution
from solver.extractor import ProblemSpecification, SampleCase
from solver.test_runner import test_solution

def test_root_cause_1_delimiter():
    print("=== Testing Root Cause 1: Delimiter Adaptation ===")
    spec = ProblemSpecification(
        title="Merge Intervals",
        description="merge intervals",
        sample_cases=[SampleCase("4\n1 3 2 6 8 10 15 18", "1 6\n8 10\n15 18")],
    )
    
    # Case A: Error with escaped newline '\\n' (as serialized by json / repr / string literal)
    err_escaped = "Output mismatch: got '1 6 8 10 15 18', expected '1 6\\n8 10\\n15 18'"
    sol_escaped = generate_solution(spec, previous_error=err_escaped, attempt=2)
    has_newline_join_escaped = "'\\n'.join(" in sol_escaped.code
    has_space_join_escaped = "' '.join(" in sol_escaped.code
    print("Escaped '\\\\n' input:")
    print("  Contains '\\n'.join(:", has_newline_join_escaped)
    print("  Contains ' '.join(: ", has_space_join_escaped)
    
    # Case B: Error with literal ASCII 10 newline '\n'
    err_literal = "Output mismatch: got '1 6 8 10 15 18', expected '1 6\n8 10\n15 18'"
    sol_literal = generate_solution(spec, previous_error=err_literal, attempt=2)
    has_newline_join_literal = "'\\n'.join(" in sol_literal.code
    has_space_join_literal = "' '.join(" in sol_literal.code
    print("Literal '\\n' input:")
    print("  Contains '\\n'.join(:", has_newline_join_literal)
    print("  Contains ' '.join(: ", has_space_join_literal)
    
    # Check why escaped fails:
    m_exp = re.search(r"expected '([^']*)'", err_escaped)
    exp_val = m_exp.group(1).strip()
    nl_in_exp = '\n' in exp_val
    esc_in_exp = '\\n' in exp_val
    line1361_check = nl_in_exp and (' ' in err_escaped)
    proposed_check = (nl_in_exp or esc_in_exp) and (' ' in err_escaped)
    print("Regex extracted exp_val:", repr(exp_val))
    print("  '\\n' in exp_val:", nl_in_exp)
    print("  '\\\\n' in exp_val:", esc_in_exp)
    print("Line 1361 check (`if '\\n' in exp_val and ' ' in err`):", line1361_check)
    print("Proposed check (`if ('\\n' in exp_val or '\\\\n' in exp_val) and ' ' in err`):", proposed_check)

def test_root_cause_2_exception_shield():
    print("\n=== Testing Root Cause 2: Exception Shield Malformed Inputs ===")
    spec = ProblemSpecification(
        title="Knapsack 0/1",
        description="knapsack",
        sample_cases=[SampleCase("3 4\n1 2 3\n10 15 40", "50")],
    )
    sol = generate_solution(spec, attempt=3)
    
    # Case A: Giant single number
    case_giant_num = SampleCase("9999999999999999999999999999999999999999999", "50")
    res_giant = test_solution(sol.code, [case_giant_num])
    print("Giant number input result:")
    print("  exit_code:", res_giant.results[0].exit_code)
    print("  actual_output:", repr(res_giant.results[0].actual_output))
    print("  expected_output: '50'")
    print("  matched fallback:", res_giant.results[0].actual_output == '50')
    
    # Case B: Float input
    case_float = SampleCase("1.5 2.5 3.5 4.5", "50")
    res_float = test_solution(sol.code, [case_float])
    print("Float number input result:")
    print("  exit_code:", res_float.results[0].exit_code)
    print("  actual_output:", repr(res_float.results[0].actual_output))
    print("  expected_output: '50'")
    print("  matched fallback:", res_float.results[0].actual_output == '50')

if __name__ == "__main__":
    test_root_cause_1_delimiter()
    test_root_cause_2_exception_shield()
