# Dispatch Assignment: Milestone 3 Worker (`worker_m3_1`)

**Timestamp**: 2026-11-10T16:15:00Z  
**Role**: Implementation Worker (`teamwork_worker`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_1`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Target Milestone**: Milestone 3 — Guvi CodeKata Driver & Automation Pipeline  

---

## 1. Objective

Implement the complete, production-grade Guvi CodeKata Driver and automation pipeline in `zenclass_guvi/drivers/`:
1. `zenclass_guvi/drivers/base_driver.py`: Foundational base driver providing navigation, safe click/fill/visibility checks, modal dismissals, diagnostic screenshots, session persistence, and HITL guardrail hooks adhering strictly to Requirement R1.
2. `zenclass_guvi/drivers/guvi_driver.py`: Full autonomous platform driver for Guvi CodeKata:
   - Authentication lifecycle: Cascade selector resolution, natural typing cadence, session persistence (`authToken` and `data/storage_state.json`), pre-login session probe, guardrail handling (`#myModal`, Cloudflare Turnstile, reCAPTCHA, OTP).
   - Catalog Discovery & Pending Filtering: 143-page table discovery, `#completed-icon_svg__a` solved vs pending classification, metadata extraction, atomic SQLite `batch_record_tasks`.
   - Problem Solving Pipeline (`solve_problem`): Workspace navigation, guardrail check, problem specification extraction (`solver.extractor`), code synthesis (`solver.code_generator`), local subprocess sandbox pre-check (`solver.test_runner`), Ace Editor code injection (`solver.ace_adapter`), Run Code execution & test pill verification, Submit Code execution & `Solved!` positive verification, StateManager 9 R3 fields update.
   - Pipeline Orchestrator (`run_pipeline`): End-to-end execution loop integrating auth, catalog discovery, pending batch loop, and executive report generation (`core.reporter`).
3. `zenclass_guvi/drivers/__init__.py`: Clean export of `BaseDriver` and `GuviDriver`.
4. `zenclass_guvi/main.py`: Wire `GuviDriver.run_pipeline()` into CLI subcommands `run-codekata` and `run-all`.
5. `zenclass_guvi/tests/test_m3_guvi.py`: Comprehensive test suite verifying all driver behaviors across authentication, catalog parsing, completed SVG detection, solve pipeline, and pipeline orchestration.

---

## 2. Mandatory Anti-Cheating Warning

> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

---

## 3. Authoritative Reference Inputs

You MUST read these reference files before beginning work:
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` (Authoritative user request)
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md` (Architecture & Milestone 3 specifications)
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_1/handoff.md` (Authentication & session blueprints)
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_2/handoff.md` (Catalog crawler, solve pipeline, orchestrator blueprints)

---

## 4. Exclusive Write Ownership

You own and may modify ONLY these files:
- `zenclass_guvi/drivers/base_driver.py` (New file)
- `zenclass_guvi/drivers/guvi_driver.py` (New file)
- `zenclass_guvi/drivers/__init__.py` (New or update)
- `zenclass_guvi/main.py` (Wire GuviDriver into CLI)
- `zenclass_guvi/tests/test_m3_guvi.py` (New test file)

DO NOT modify files outside your write ownership without explicit approval.

---

## 5. Verification Requirements

You MUST execute the following verification commands and record exact terminal outputs in your `handoff.md`:
1. `pytest tests/test_m3_guvi.py -v` (or `python3 -m unittest tests/test_m3_guvi.py`)
2. `pytest tests/test_m1_core.py tests/test_m2_solver.py -v` (verify zero regressions on M1 & M2)
3. `python3 tests/e2e/test_runner.py --all` (verify all 78 E2E tests pass with 100% success rate)

---

## 6. Output Deliverable

Write your final handoff report to `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m3_1/handoff.md` following the Handoff Protocol (Observation, Logic Chain, Caveats, Conclusion, Verification Method). Notify the orchestrator via `send_message`.
