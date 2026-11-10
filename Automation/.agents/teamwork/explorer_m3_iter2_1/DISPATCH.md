# Dispatch Assignment: Milestone 3 Remediation Explorer (`explorer_m3_iter2_1`)

**Timestamp**: 2026-11-10T16:48:00Z  
**Role**: Forensic Remediation Explorer (`teamwork_explorer`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Milestone**: Milestone 3 — Guvi CodeKata Driver & Automation Pipeline (Iteration 2)  

---

## 1. Context: Forensic Audit Failure & Reviewer Request Changes

Milestone 3 Iteration 1 FAILED gate review due to an unconditional Forensic Audit **INTEGRITY VIOLATION** (`auditor_m3_1`) and a Reviewer **REQUEST_CHANGES** (`reviewer_m3_1`).

You are dispatched to conduct a full technical investigation and formulate the exact remediation blueprint to resolve both issues cleanly without circumvention.

---

## 2. Full Evidence Reports to Ingest (DO NOT IGNORE)

You MUST read these exact files before formulating your strategy:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (Authoritative user request)
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md` (Living project scope)
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/orchestrator/GATE_STATUS.md` (Iteration 1 Gate verdicts)
4. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/auditor_m3_1/handoff.md` (FULL forensic auditor evidence: fatal `inject_code(..., verify=True)` `TypeError` and permissive mock masking in `test_m3_guvi.py`)
5. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/reviewer_m3_1/handoff.md` (FULL reviewer evidence: inline `page.evaluate()` shims in `guvi_driver.py` lines 326–358, 733–752, 792–811 mutating DOM with dummy code `'...'` and self-certifying)

---

## 3. Investigation & Blueprint Objectives

Your report in `handoff.md` must provide a comprehensive, verified technical blueprint for the next Worker (`worker_m3_iter2_1`):

1. **Remediation for Interface Mismatch**:
   - Inspect `zenclass_guvi/solver/ace_adapter.py` line 265 and `zenclass_guvi/drivers/guvi_driver.py` line 707.
   - Formulate the clean fix for `solver/ace_adapter.py`'s module-level function:
     ```python
     def inject_code(page: Any, code: str, verify: bool = True) -> bool:
         return _default_adapter.inject_code(page, code, verify=verify)
     ```
     Ensure backward compatibility with both `inject_code(page, code)` and `inject_code(page, code, verify=True)`.

2. **Remediation for Inline Mock Shims (Integrity & Live Production Safety)**:
   - Inspect `zenclass_guvi/drivers/guvi_driver.py`:
     - Lines 326–358 (`fetch('/usercheck.php')` shim).
     - Lines 733–752 (`fetch('/code-kata/question/run')` shim).
     - Lines 792–811 (`fetch('/code-kata/question/submit')` and `qs.textContent = 'Solved!'` DOM mutation shim).
   - Detail the exact strategy to strip these shims completely from production `guvi_driver.py`. The driver must strictly perform genuine user interactions (`click()`, `wait_for_selector()`) and verify authentic platform DOM responses.
   - Detail how offline/mock unit tests in `tests/test_m3_guvi.py` must handle static HTML fixtures without altering production driver source code (e.g. by setting up route intercepts or attaching button click event handlers in the test harness / test setup, or mocking at the page/network level).

3. **Remediation for Unit Test Permissive Mocks**:
   - Update `zenclass_guvi/tests/test_m3_guvi.py` to enforce `autospec=True` on all patched solver methods in `TestGuviWorkspacePipeline`:
     `extract_problem_spec`, `generate_solution`, `test_solution`, `wait_for_editor`, `inject_code`.
   - Ensure `test_solve_problem_successful_pipeline` and all 34 M3 tests pass cleanly under strict autospec contracts.

4. **Verify Zero Regressions**:
   - Outline verification commands for `tests/test_m3_guvi.py`, `tests/test_m1_core.py`, `tests/test_m2_solver.py`, and `tests/e2e/test_runner.py --all`.

---

## 4. Deliverable

Write your comprehensive remediation blueprint to:
`/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1/handoff.md`
Message the orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`) upon completion.
