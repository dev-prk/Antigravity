## 2026-11-10T18:11:49Z

You are the implementation worker for Milestone 5 (ZenClass Projects Driver, Local Synthesis Engine, and R2 HITL Pause Protocol).

## Identity & Context
- Identity: M5 Implementation Worker
- Parent Orchestrator ID: cbd0649b-f648-4724-a244-a22a5102ccc4
- Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m5_1
- Project workspace directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi

## References (Read Before Starting)
1. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md
2. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md
3. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m5_1/handoff.md
4. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m5_2/handoff.md
5. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/zenclass_tasks_driver.py
6. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/hitl_handler.py
7. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/core/state_manager.py
8. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/e2e/tier4_workloads/test_w03_zenclass_projects_hitl_e2e.py

## Mandatory Integrity Warning
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected. Zero mock evaluate shims are permitted in production drivers. All `@patch` calls in tests MUST enforce `autospec=True`.

## Exclusive Write Scope
You own exclusively:
- `zenclass_guvi/solver/project_synthesizer.py`
- `zenclass_guvi/solver/project_validator.py`
- `zenclass_guvi/solver/__init__.py`
- `zenclass_guvi/drivers/zenclass_projects_driver.py`
- `zenclass_guvi/drivers/__init__.py`
- `zenclass_guvi/main.py`
- `zenclass_guvi/tests/test_m5_zenclass_projects.py`
Do NOT modify files outside this list.

## Implementation Tasks
1. `solver/project_synthesizer.py`:
   - Implement `ProjectSynthesizer`, `ProjectSpec`, `ProjectType`, and `SynthesisResult`.
   - Scaffolds `projects/<slug>/` with production-grade frontend (HTML5/CSS3/ES6+ JS), fullstack Node.js (Express), fullstack Python (Flask), package manifests, `.gitignore`, and detailed `README.md` (architecture diagram, local setup instructions, Vercel/Netlify/Render deployment guide, test checklist).
2. `solver/project_validator.py`:
   - Implement `ProjectValidator`, `ValidationReport`, `HTMLTagValidator` (stack-based balanced tag validator), CSS parser, JS syntax validator (`node --check` with Python fallback), Python syntax validator (`py_compile`/`ast.parse`), JSON validator, and artifact generation (`validation_report.json`).
3. `solver/__init__.py`:
   - Cleanly export `ProjectSynthesizer`, `ProjectValidator`, `ProjectSpec`, `ProjectType`, `SynthesisResult`, `ValidationReport`.
4. `drivers/zenclass_projects_driver.py`:
   - Implement `ZenClassProjectsDriver(BaseDriver)` with the full 5-stage lifecycle:
     - Stage 1: Discovery & Catalog Parsing (Kanban columns `.active-Project-heading`, `.pending-Project-heading`, `.completed-Project-heading`, card items `.itemactive-Project#individual-card`, card fields, detail modal extraction via `.view-project-container` and `.student-view-task-main-container`).
     - Stage 2: Local Code Synthesis in `projects/<slug>/` via `ProjectSynthesizer`.
     - Stage 3: Local Build & Syntax Validation via `ProjectValidator`.
     - Stage 4: Interactive Human Pause Protocol (Requirement R2) via `HitlHandler.request_project_links(...)` with audible terminal alerts (`\a`), ANSI prompt box, interactive user input, and graceful headless/non-interactive fallback to `TaskStatus.BLOCKED` / `TaskResult.AWAITING_INPUT`.
     - Stage 5: Dynamic 13-field Modal Submission via `.submit-form-container-web` and confirmation verification of `.sucess-popup-main-container` with `ZENCLASS_PROJECT_CONFIRMATION_REGEX`.
     - Pipeline: `run_projects_pipeline()` supporting limit and project_id targeting.
     - Persistent State: batch records all 9 mandatory R3 fields into SQLite `StateManager` with `platform="zenclass_projects"` and `task_category="Project"`.
     - Zero mock evaluate shims in production code.
5. `drivers/__init__.py`:
   - Export `ZenClassProjectsDriver`, `ZenClassProjectError`, `DiscoveredProject`.
6. `main.py`:
   - Add `run-zenclass-projects` subparser and wire `AutomationRunner.run_zenclass_projects()`.
7. `tests/test_m5_zenclass_projects.py`:
   - Comprehensive unit test suite covering synthesizer, validator, driver stages 1-5, HITL pause, dynamic modal mapping, and pipeline.
   - Enforce `autospec=True` on EVERY `@patch`.

## Verification Commands to Run & Pass
1. `python3 -m unittest -v tests/test_m5_zenclass_projects.py`
2. `python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py tests/test_m3_guvi.py tests/test_m4_zenclass_tasks.py`
3. `python3 tests/e2e/test_runner.py --all`
4. Static check for zero mock evaluate shims in `drivers/zenclass_projects_driver.py`.

## Deliverables
- Deliver structured handoff report in `/Users/deesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m5_1/handoff.md` following the 5-part Handoff Protocol (Observation, Logic Chain, Caveats, Conclusion, Verification Method).
- Send a completion message to the parent orchestrator via `send_message`.
