## 2026-11-10T15:41:09Z
You are worker_m2_1, a specialized implementation worker.

## Working Directory
Your working directory is: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1`
Write all notes, temporary files, and your final handoff report (`handoff.md`) inside this directory.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Authoritative Inputs
1. You MUST read the authoritative user request at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. Read the master project blueprint and interface contracts at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. Read the blueprints from Explorer M2-1 at:
   - Report: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1/handoff.md`
   - Extractor blueprint: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1/proposed_extractor.py`
   - Ace Adapter blueprint: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_1/proposed_ace_adapter.py`
4. Read the blueprints from Explorer M2-2 at:
   - Report & complete code blueprints: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m2_2/handoff.md`

## Scope & Exclusive Write Ownership
You own exclusive write access to:
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/__init__.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/extractor.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/code_generator.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/test_runner.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/ace_adapter.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/test_m2_solver.py`

## Implementation Details

1. **`solver/__init__.py`**:
   - Clean package export exposing:
     - `SampleCase`, `ProblemSpecification`, `ProblemSpec`, `ProblemExtractor`, `extract_problem_spec`
     - `GeneratedSolution`, `generate_solution`, `synthesize_solution`
     - `TestCaseResult`, `ValidationResult`, `test_solution`, `validate_solution`, `SubprocessSandbox`
     - `AceEditorAdapter`, `inject_code`, `inject_code_into_ace`, `get_editor_code`, `wait_for_editor`

2. **`solver/extractor.py`**:
   - Implement `ProblemSpecification` data class with property aliases (`input_desc`, `output_desc`, `sample_input`, `sample_output`) for 100% backward compatibility with `ProblemSpec`.
   - Dual-input support: Playwright `Page` or raw HTML `str`.
   - Multi-strategy extraction: CSS classes (`.problem-title`, `.problem-statement`, `.sample-input`, `.sample-output`), labeled text headings, and negative lookahead regex.
   - Clean fallback on sparse or empty HTML (`title == "Unknown"`).

3. **`solver/code_generator.py`**:
   - Implement `GeneratedSolution` data class and `generate_solution` / `synthesize_solution` functions.
   - Dual contract: `generate_solution(problem) -> GeneratedSolution` and `synthesize_solution(problem) -> str`.
   - Canonical solvers for known CodeKata problems (`odd-or-even-sum`, `reverse-a-string`, `sum-of-array`, `palindrome-check`, `prime-numbers-count`).
   - Algorithmic template library: Arrays (min/max, sorting, deduplication, Kadane), Strings (vowel counts, palindrome, reverse), Math (primes, GCD/LCM, factorial, fibonacci), and I/O fallback.
   - AST validation via `ast.parse()`.

4. **`solver/test_runner.py`**:
   - Implement `TestCaseResult`, `ValidationResult` (with `.passed`, `.stdout`, `.stderr`, `.exit_code`, `.duration_ms`, `.error_message` properties).
   - Sandboxed subprocess execution using `sys.executable -c <code>`.
   - Stdin piping, stdout/stderr capture, strict timeout (default 2.0s), `proc.kill()` on `TimeoutExpired`.
   - Output normalization: CRLF to LF, per-line trailing space stripping, outer whitespace stripping, float numerical tolerance.
   - Single-case function `validate_solution` and class `SubprocessSandbox.validate_solution` for E2E harness compatibility.

5. **`solver/ace_adapter.py`**:
   - Implement `AceEditorAdapter` with functions `inject_code` (and alias `inject_code_into_ace`), `get_editor_code`, `wait_for_editor`.
   - 4-step CDP keyboard injection sequence: click `#editor textarea.ace_text-input`, `Meta+A`/`Control+A`, `Backspace`, `insert_text(code)`.
   - Fallback to JavaScript `ace.edit('editor').setValue(code, 1)`.

6. **Unit Verification Suite (`tests/test_m2_solver.py`)**:
   - Write comprehensive tests covering all 4 modules (extraction, synthesis, sandboxed runner, Ace adapter mock injection).

## Verification Requirements
Run the following commands and ensure all pass:
```bash
cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
python3 -m pytest tests/test_m2_solver.py -v
python3 -m pytest tests/test_m1_core.py -v
python3 tests/e2e/test_runner.py --all
```

Produce a full handoff report in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1/handoff.md` with:
- Observation (what was implemented, build/test results)
- Logic Chain
- Caveats
- Conclusion
- Verification Method

Send a completion message back to parent when done.
