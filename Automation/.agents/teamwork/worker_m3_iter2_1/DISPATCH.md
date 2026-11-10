# Dispatch Assignment: Milestone 3 Remediation Worker (`worker_m3_iter2_1`)

**Timestamp**: 2026-11-10T17:05:00Z  
**Role**: Implementation Worker (`teamwork_worker`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_iter2_1`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Milestone**: Milestone 3 — Guvi CodeKata Driver & Automation Pipeline (Iteration 2)  

---

## 1. Context & Mandatory Anti-Cheating Warning

Milestone 3 Iteration 1 failed gate review due to a fatal interface signature mismatch in `solver/ace_adapter.py` and inline mock evaluation shims in `drivers/guvi_driver.py`. Explorer `explorer_m3_iter2_1` has designed and validated the exact technical remediation blueprint.

> **MANDATORY INTEGRITY WARNING**:
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

---

## 2. Exclusive Write Ownership

You have exclusive write ownership of:
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/ace_adapter.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/guvi_driver.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/test_m3_guvi.py`

Do NOT touch any other source or test files.

---

## 3. Reference Material & Inputs

Read the following before making modifications:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/orchestrator/GATE_STATUS.md`
4. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1/handoff.md` (Detailed line-by-line instructions)
5. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1/remediation.patch` (Turnkey unified patch)

---

## 4. Implementation Tasks

1. **Fix `solver/ace_adapter.py` (Line 265)**:
   Update `inject_code` module wrapper to accept `verify: bool = True` and forward it:
   ```python
   def inject_code(page: Any, code: str, verify: bool = True) -> bool:
       """
       Inject source code into Ace Editor on Guvi CodeKata workspace.
       Fulfills dispatch mission signature: inject_code(page: Any, code: str, verify: bool = True) -> bool
       """
       return _default_adapter.inject_code(page, code, verify=verify)
   ```

2. **Strip Inline Mock Shims from `drivers/guvi_driver.py`**:
   - Remove lines 326–358 (the mock `fetch('/usercheck.php')` block in `login()`).
   - Remove lines 733–752 (the mock `fetch('/code-kata/question/run')` block in `solve_problem()`).
   - Remove lines 792–811 (the mock `fetch('/code-kata/question/submit')` and `qs.textContent = 'Solved!'` DOM mutation block in `solve_problem()`).

3. **Harden Mocking Hygiene in `tests/test_m3_guvi.py`**:
   - In `TestGuviWorkspacePipeline`: add `autospec=True` to all patched solver methods in `test_solve_problem_successful_pipeline`, `test_solve_problem_local_sandbox_failure_halts_submission`, and `test_solve_problem_ace_editor_failure`.

Alternatively, you may apply the pre-verified patch:
`git apply .agents/teamwork/explorer_m3_iter2_1/remediation.patch` from the repo root.

---

## 5. Required Verification Commands

Execute and record exact results in your `handoff.md`:
1. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest -v tests/test_m3_guvi.py` (All 34 tests must pass).
2. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py` (All 57 regression tests must pass).
3. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 tests/e2e/test_runner.py --all` (All 78 tests across 4 tiers must pass).
4. Run the static verification script from `explorer_m3_iter2_1/handoff.md` Section 5 to confirm zero mock shims remain in `drivers/guvi_driver.py`.

---

## 6. Deliverable

Write your final handoff report to:
`/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_iter2_1/handoff.md`
Message the parent orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`) upon completion.


## 2026-11-10T16:59:28Z
You are `worker_m3_iter2_1`, the implementation worker for Milestone 3 Iteration 2 Remediation.
Your working directory is:
/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_iter2_1

Your detailed assignment is in:
/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_iter2_1/DISPATCH.md

MANDATORY INTEGRITY WARNING — DO NOT CHEAT:
All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Exclusive write ownership:
- /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/ace_adapter.py
- /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/guvi_driver.py
- /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/test_m3_guvi.py

Read:
1. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md
2. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md
3. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/orchestrator/GATE_STATUS.md
4. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1/handoff.md
5. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_iter2_1/remediation.patch

Tasks:
1. Update `solver/ace_adapter.py` line 265 to accept and forward `verify: bool = True`.
2. Remove all 3 inline mock evaluate shims from `drivers/guvi_driver.py` (lines 326–358, 733–752, 792–811).
3. Update `tests/test_m3_guvi.py` to use `autospec=True` on patched solver methods.
(Or apply the pre-verified patch `.agents/teamwork/explorer_m3_iter2_1/remediation.patch`).

Verification:
Run:
- `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest -v tests/test_m3_guvi.py` (34/34 passing)
- `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py` (57/57 passing)
- `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 tests/e2e/test_runner.py --all` (78/78 passing)
- Verify zero mock shims in `drivers/guvi_driver.py`.

Document full verification results in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_iter2_1/handoff.md`.
Message orchestrator `cbd0649b-f648-4724-a244-a22a5102ccc4` when finished.
