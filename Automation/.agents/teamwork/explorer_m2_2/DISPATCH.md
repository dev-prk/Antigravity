## 2026-11-10T15:30:08Z
You are explorer_m2_2, an exploration subagent.

## Working Directory
Your working directory is: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_2`
Write all notes, research, and your final handoff report (`handoff.md`) inside this directory.

## Authoritative Inputs
1. You MUST read the authoritative user request at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. Read the master project blueprint and interface contracts at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. Read the reference oracle in the E2E test suite:
   `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/e2e/harness/reference_oracle.py`

## Mission: Blueprint `solver/code_generator.py` and `solver/test_runner.py`
Milestone 2 requires building the autonomous algorithmic solution synthesizer and sandboxed test runner.

Investigate and produce concrete, production-ready blueprints for:
1. **`solver/code_generator.py`**:
   - Algorithmic Python 3 solution synthesis across typical competitive programming categories:
     - Basic I/O & formatting (numbers on single line, multiple lines, comma-separated, space-separated)
     - Arrays & Lists (sums, min/max, frequency, sorting, reversal, rotation, duplicate removal)
     - Strings (reversal, palindrome checks, vowel counting, casing, anagrams, substring counts)
     - Mathematics & Number Theory (prime checking, sieve, GCD, LCM, factorial, fibonacci, base conversion, sum of digits)
     - Two pointers, sliding window, greedy heuristics
     - Dynamic programming (LIS, knapsack, coin change, grid paths)
   - Synthesis strategy:
     - Direct template matching based on problem statement keywords, title, category, and sample I/O pattern.
     - Deterministic standard solvers for known Guvi CodeKata problems.
     - Robust standard input handling: `sys.stdin.read().strip().split()` pattern supporting varied whitespace and line feeds.
     - Standard output formatting matching the exact expected format (trailing newlines, space vs line separation).
   - Data class: `GeneratedSolution` with `code: str`, `category: str`, `confidence: float`, `explanation: str`.
   - Function signature: `generate_solution(problem: ProblemSpecification) -> GeneratedSolution`.

2. **`solver/test_runner.py`**:
   - Sandboxed local execution using `subprocess.run`:
     - Isolated process execution (`sys.executable`, `-c`, `code`)
     - Feeding `sample_case.input_data` via stdin pipe
     - Capturing stdout and stderr
     - Enforcing strict timeout (default: 2.0s) with `subprocess.TimeoutExpired` handling
     - Output normalization: stripping leading/trailing whitespace, normalizing CRLF to LF, handling trailing spaces per line
     - Comparing actual output with `sample_case.expected_output`
   - Data class: `TestCaseResult` with `passed: bool`, `input_data: str`, `expected_output: str`, `actual_output: str`, `error_message: str`, `duration: float`.
   - Data class: `ValidationResult` with `all_passed: bool`, `passed_count: int`, `total_count: int`, `results: List[TestCaseResult]`.
   - Function signature: `test_solution(code: str, sample_cases: List[SampleCase], timeout: float = 2.0) -> ValidationResult`.

Write your full blueprint and design in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_2/handoff.md`.
Send a completion message back to parent when done.
