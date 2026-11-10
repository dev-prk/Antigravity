# Empirical Challenge Report: Milestone 2 — Autonomous Problem Solver & Subprocess Sandbox

**Date**: 2026-11-10T16:05:00Z  
**Agent ID**: `challenger_m2_1`  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/challenger_m2_1`  
**Handoff Type**: Hard (Challenge Complete)  
**Verdict**: **APPROVE**  

---

## 1. Observation

Direct adversarial verification and empirical stress testing was performed on `zenclass_guvi/solver/code_generator.py` and `zenclass_guvi/solver/test_runner.py` across five independently executed stress harnesses comprising 115 individual stress assertions:

### A. Baseline Verification
- Unit test suite: `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m pytest tests/test_m2_solver.py -v`
  - Output: `35 passed in 0.51s`
- E2E 4-Tier regression suite: `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 tests/e2e/test_runner.py --all`
  - Output: `Ran 78 tests in 8.823s ... OK (Tier 1: 54, Tier 2: 14, Tier 3: 6, Tier 4: 4)`

### B. Harness 1: Subprocess Timeout & Zombie Process Leakage (`harness_1_timeout_zombies.py`)
- **Commands & Execution**: `python3 harness_1_timeout_zombies.py`
- **Pathological Scenarios Tested**:
  1. Infinite CPU loop (`while True: pass`, timeout=0.2s):
     - Duration: `0.2045s`, passed: `False`, exit_code: `-1`, stderr: `'TimeoutExpired'`, error_message: `'Execution timed out after 0.2 seconds'`. -> **PASS**
  2. Infinite sleep loop (`while True: time.sleep(0.05)`, timeout=0.2s):
     - Duration: `0.2041s`, passed: `False`, exit_code: `-1`, stderr: `'TimeoutExpired'`. -> **PASS**
  3. Infinite stdout flood (`while True: sys.stdout.write('A'*4096)`, timeout=0.3s):
     - Duration: `0.3632s`, passed: `False`, exit_code: `-1`, stderr: `'TimeoutExpired'`. -> **PASS**
  4. Deep recursive calls in an infinite loop (`r(500)` loop, timeout=0.2s):
     - Duration: `0.2290s`, passed: `False`, exit_code: `-1`, stderr: `'TimeoutExpired'`. -> **PASS**
  5. Subprocess spawn attempt with sleep child (`subprocess.Popen(...)`, timeout=0.2s):
     - Duration: `0.2161s`, passed: `False`, exit_code: `-1`, stderr: `'TimeoutExpired'`. -> **PASS**
  6. Unbounded recursion hitting `RecursionError` (runtime failure, not timeout):
     - Exit code: `1`, stderr contains `'RecursionError'`. -> **PASS**
  7. Multi-case isolation via `test_solution`:
     - 3 cases (`"1 2" -> 3`, `"while" -> timeout`, `"5 5" -> 10`):
     - Passed count: `2/3`, `all_passed: False`, results exit codes: `[0, -1, 0]`. -> **PASS**
  8. OS process table inspection (`ps -eo pid,ppid,state,command`):
     - Initial zombie processes: `0`. Final zombie processes: `0`. Defunct processes: `0`. -> **PASS**
- **Result**: 7/7 tests passed (100%).

### C. Harness 2: AST Validity Under Extreme & Adversarial Inputs (`harness_2_ast_extreme.py`)
- **Commands & Execution**: `python3 harness_2_ast_extreme.py`
- **Adversarial Vectors Tested**:
  - 24 extreme inputs fed to `synthesize_solution()` and `generate_solution()`, verified with `ast.parse()` and `compile(code, '<test>', 'exec')`:
    - Empty string `""` -> Valid AST & Compiles
    - Whitespace only `"   \n\t "` -> Valid AST & Compiles
    - Single characters `"a"`, `"z"` -> Valid AST & Compiles
    - Empty `ProblemSpecification(title="", description="", input_spec="", output_spec="")` -> Valid AST & Compiles
    - Python `None` input -> Valid AST & Compiles
    - Numeric inputs (`999999`, `3.14159`) -> Valid AST & Compiles
    - Raw binary bytes (`b"\x00\x01\x02\xff\xfe\xab"`) -> Valid AST & Compiles
    - Malformed dictionaries with non-string keys and null sample cases -> Valid AST & Compiles
    - 10,000-character random ASCII string -> Valid AST & Compiles
    - 50,000-character repeating string `"A" * 50000` -> Valid AST & Compiles
    - 10,000-character newline string `"\n" * 10000` -> Valid AST & Compiles
    - Python code injection in title (`__import__('os').system(...)`) -> Valid AST & Compiles
    - Syntax error in title (`def broken_code(::): return }}}`) -> Valid AST & Compiles
    - Triple quotes inside description (`''' """ ''' """ \'\'\' """`) -> Valid AST & Compiles
    - SQL injection string (`'; DROP TABLE tasks; --`) -> Valid AST & Compiles
    - Shell injection string (`$(rm -rf /) \`cat /etc/passwd\``) -> Valid AST & Compiles
    - XSS HTML payload (`<script>alert('xss');</script>`) -> Valid AST & Compiles
    - Null bytes and control chars (`\x00\x01\x02...\x7f`) -> Valid AST & Compiles
    - Complex multilingual unicode and emojis (`🚀🔥🤖 CodeKata Задача 123! 日本語`) -> Valid AST & Compiles
    - Nested brackets and adversarial spec with all fields corrupted -> Valid AST & Compiles
- **Result**: 24/24 tests passed (100%). Zero `SyntaxError` raised.

### D. Harness 3: Execution Accuracy on Canonical Problems (`harness_3_canonical_accuracy.py`)
- **Commands & Execution**: `python3 harness_3_canonical_accuracy.py`
- **Canonical Solvers & Test Vectors Tested**:
  1. `odd-or-even-sum`: 9 vectors tested (including large `1000000000 1000000001`, negative numbers `-5 5`, `-3 4`, `-2 -4`, multi-line formatting `7\n8\n`, surrounding spaces `   1   3   `) -> 9/9 passed.
  2. `reverse-a-string`: 7 vectors tested (`hello`, `guvi`, `a`, `12345`, `racecar`, `Hello World!`, `abc def`) -> 7/7 passed.
  3. `sum-of-array`: 7 vectors tested (multiline arrays, negative elements, single line arrays, zero arrays, single elements) -> 7/7 passed.
  4. `palindrome-check`: 8 vectors tested (`racecar`, `madam`, `automation`, `a`, `noon`, `python`, `12321`, `12345`) -> 8/8 passed.
  5. `prime-numbers-count`: 13 vectors tested:
     - Range queries: `2 10` -> `4`, `1 10` -> `4`, `10 20` -> `4`, `20 30` -> `2`, `1 1` -> `0`, `0 1` -> `0`, `2 2` -> `1`
     - Single number queries: `2` -> `yes`, `3` -> `yes`, `4` -> `no`, `17` -> `yes`, `1` -> `no`, `0` -> `no` -> 13/13 passed.
  - Dual contract validation: Verified both slug-based synthesis and `ProblemSpecification`-based synthesis, plus `SubprocessSandbox.validate_solution` and batch `test_solution`.
- **Result**: 44/44 test vectors passed (100.00% accuracy).

### E. Harness 4: Float Tolerance & Output Normalization (`harness_4_float_normalization.py`)
- **Commands & Execution**: `python3 harness_4_float_normalization.py`
- **Normalization & Tolerance Scenarios Tested**:
  - `normalize_output`: 8/8 passed (CRLF `\r\n` -> `\n`, lone CR `\r` -> `\n`, mixed endings, per-line trailing space/tab stripping, outer blank lines).
  - `outputs_match`: 23/23 passed:
    - Exact string matches and formatting equivalence
    - Case-insensitive tokens (`YES/yes`, `No/no`, `TRUE/true`, `FALSE/false`, `EVEN/even`, `Odd/odd`)
    - Case-sensitive preservation for non-token strings (`HELLO` vs `hello` correctly returns `False`)
    - Float tolerance: `3.141592` vs `3.1416` (relative diff 8e-6 <= 1e-4) -> `True`
    - Small numbers: `0.00001` vs `0.00002` (absolute diff <= 1e-4) -> `True`
    - Large numbers: `100.005` vs `100.0` (relative diff <= 1e-4) -> `True`
    - Float mismatch outside tolerance: `100.1` vs `100.0` -> `False`
    - Scientific notation: `1e-5` vs `0.00001` -> `True`, `1.23e2` vs `123.0` -> `True`
    - Multi-float vectors: `1.00001 2.00002 3.00003` vs `1.0 2.0 3.0` -> `True`
    - Mixed text-number lines: `Area = 3.141592 sq cm` vs `Area = 3.1416 sq cm` -> `True`
  - Live subprocess float execution: Python code calculating `math.pi * 2.0 * 2.0` (actual `12.566370614359172`) compared against expected `12.5664` -> `validate_solution` returned `passed=True`, `exit_code=0`.
- **Result**: 32/32 tests passed (100%).

### F. Harness 5: Edge Cases, Large Payloads & Boundary Stress (`harness_5_stress_edge_cases.py`)
- **Commands & Execution**: `python3 harness_5_stress_edge_cases.py`
- **Boundary Scenarios Tested**:
  1. Massive 2MB stdin payload (1,000,000 numbers): Execution completed in `0.04s`, returned `len=1000000` with zero deadlock. -> **PASS**
  2. Multilingual UTF-8 fidelity (Tamil, Hindi, Chinese, Arabic, Emojis): Exact bidirectional UTF-8 piping preserved. -> **PASS**
  3. Specific exit code preservation (`sys.exit(42)`): Returned `exit_code = 42`, `passed = False`. -> **PASS**
  4. Runtime exception handling (`ZeroDivisionError`): Captured `exit_code = 1`, stderr contains `'ZeroDivisionError'`, `passed = False`. -> **PASS**
  5. Direct syntax error in runner (`def f(:`): Captured `exit_code = 1`, stderr contains `'SyntaxError'`, `passed = False`. -> **PASS**
  6. Ultra-tight timeout (`0.001s`): Returned `exit_code = -1`, stderr `'TimeoutExpired'`, `passed = False`. -> **PASS**
  7. API symbol export completeness: Verified all 18 public symbols cleanly exported on `solver` package namespace. -> **PASS**
- **Result**: 7/7 tests passed (100%).

---

## 2. Logic Chain

1. **Timeout Enforcement & Clean OS Cleanup**:
   - *Observation*: Subprocess executions under `validate_solution` and `test_solution` were challenged with infinite CPU loops (`while True: pass`), infinite sleep (`while True: time.sleep(0.05)`), recursive loops, and stdout flood attacks under tight timeouts (0.2s - 0.3s).
   - *Inference*: In every scenario, `subprocess.run(timeout=timeout)` caught `subprocess.TimeoutExpired`, killed the child process, recorded `exit_code = -1`, `stderr = "TimeoutExpired"`, and returned within budget (`duration <= timeout + 0.1s`).
   - *OS Process Table Verification*: Inspection of `ps -eo pid,ppid,state,command` before and after showed exactly 0 zombie (`<defunct>`) processes and 0 lingering python worker processes.

2. **AST Robustness Under Hostile Inputs**:
   - *Observation*: 24 adversarial vectors ranging from empty strings to 50,000-character repeats, code injections, SQL payloads, and null bytes were passed to `synthesize_solution`.
   - *Inference*: `_normalize_problem` safely handles string, dictionary, dataclass, and raw primitive representations. Even when adversarial strings trigger fallback, `ast.parse()` validates the code before returning. In 100% of cases, the returned string is syntactically valid Python 3 that compiles under `compile(..., 'exec')`.

3. **Algorithmic Accuracy on Canonical Problems**:
   - *Observation*: All 44 test vectors across Guvi CodeKata's canonical problems (`odd-or-even-sum`, `reverse-a-string`, `sum-of-array`, `palindrome-check`, `prime-numbers-count`) were executed through `synthesize_solution` and `validate_solution`.
   - *Inference*: Every test vector passed with exact expected output or acceptable token match. Both single-case and batch test runner modes confirmed 100.00% pass rate.

4. **Formatting Equivalence & Numerical Tolerances**:
   - *Observation*: `normalize_output` converts CRLF/CR to LF, strips trailing spaces per line, and eliminates surrounding whitespace. `outputs_match` incorporates case-insensitive parity/boolean token checks and token-by-token numerical float comparison (`math.isclose(..., rel_tol=1e-4, abs_tol=1e-4)`).
   - *Inference*: Floating point rounding variations (e.g. `3.141592` vs `3.1416`, `12.56637...` vs `12.5664`) correctly evaluate as matching, while true value mismatches or token count discrepancies are reliably rejected.

---

## 3. Caveats

1. **Host Python Architecture**: All subprocess sandboxing was verified on Python 3.9.6 (Darwin / Apple Silicon). Standard library `subprocess.run` behavior is uniform across POSIX systems.
2. **Network/Browser Isolation**: The solver components (`code_generator.py`, `test_runner.py`) operate purely offline as intended; live browser automation with Ace Editor (`ace_adapter.py`) requires a Playwright foreground session (validated in M1 and mocked in M2 tests, to be exercised end-to-end in M3).

---

## 4. Conclusion

**Verdict: APPROVE**

Milestone 2 implementation (`solver/code_generator.py` and `solver/test_runner.py`) successfully withstood all adversarial attack vectors:
- Zero zombie processes leaked under infinite loops, recursive calls, and sleep calls.
- Strict timeout enforcement returning `exit_code = -1` and `stderr = 'TimeoutExpired'`.
- 100% AST syntax validity across 24 extreme, adversarial, and injection inputs.
- 100.00% execution accuracy (44/44 test vectors) across all 5 canonical CodeKata problems.
- Robust output normalization handling CRLF line endings, trailing spaces, and floating point tolerances.
- Resilient large payload handling (2MB stdin throughput without deadlocks) and UTF-8 encoding fidelity.

The codebase is production-ready for Milestone 3 (Guvi CodeKata Driver & Automation).

---

## 5. Verification Method

To independently execute and verify the empirical challenge test suite, run:

```bash
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi

# 1. Run Baseline Test Suites
python3 -m pytest tests/test_m2_solver.py -v
python3 tests/e2e/test_runner.py --all

# 2. Run Adversarial Stress Harnesses
python3 ../.agents/teamwork/challenger_m2_1/harness_1_timeout_zombies.py
python3 ../.agents/teamwork/challenger_m2_1/harness_2_ast_extreme.py
python3 ../.agents/teamwork/challenger_m2_1/harness_3_canonical_accuracy.py
python3 ../.agents/teamwork/challenger_m2_1/harness_4_float_normalization.py
python3 ../.agents/teamwork/challenger_m2_1/harness_5_stress_edge_cases.py

# 3. Verify OS Process Table Cleanliness
ps -eo pid,state,command | grep -i python
```

### Invalidation Conditions
- If `harness_1_timeout_zombies.py` detects any defunct/zombie processes in `ps`.
- If `harness_2_ast_extreme.py` raises `SyntaxError` on any adversarial input.
- If `harness_3_canonical_accuracy.py` achieves less than 100% pass rate.
- If `harness_4_float_normalization.py` fails on CRLF or 1e-4 float tolerance comparisons.
