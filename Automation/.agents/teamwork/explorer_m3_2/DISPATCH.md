## 2026-11-10T16:03:46Z
You are explorer_m3_2, an exploration subagent.

## Working Directory
Your working directory is: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_2`
Write all notes, research, and your final handoff report (`handoff.md`) inside this directory.

## Authoritative Inputs
1. You MUST read the authoritative user request at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. Read the master project blueprint and interface contracts at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. Read the survey findings from Guvi spec miner at:
   `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_2/handoff.md`
4. Inspect the verified solver package in:
   `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/solver/`

## Mission: Blueprint Guvi CodeKata Catalog Crawler & Problem Solving Pipeline in `drivers/guvi_driver.py`
Milestone 3 requires building the autonomous catalog discovery, pending problem filtering, and execution pipeline.

Investigate and produce concrete, production-ready blueprints for:
1. **Catalog Crawler & Pending Filter**:
   - URL: `https://www.guvi.in/code-kata/`
   - Pagination structure: 143 pages, 15 problems per page (~2,145 total).
   - Problem table parsing: Row selectors, column 0 status icon.
   - Status detection:
     - Completed icon: SVG `#completed-icon_svg__a` (`fill="#0DBA4B"`). If present, problem is already solved.
     - Pending: If `#completed-icon_svg__a` is absent, the problem is uncompleted/pending.
   - Extract problem metadata: Title, slug, URL (`/code-kata/<slug>`), category.
   - Batch recording into SQLite `StateManager`: `batch_record_tasks`.
2. **Workspace Problem Solving Pipeline (`solve_problem`)**:
   - Navigate to `/code-kata/<slug>`
   - Security challenge check: `hitl.check_and_handle_guardrails(page)`
   - Extract problem: `solver.extractor.extract_problem_spec(page)`
   - Synthesize code: `solver.code_generator.generate_solution(spec)`
   - Local validation: `solver.test_runner.test_solution(sol.code, spec.sample_cases)`
   - If local test fails: Record failure in StateManager, halt or update attempt count.
   - If local test passes:
     - Inject into Ace Editor: `solver.ace_adapter.inject_code(page, sol.code)`
     - Run Code button: Click `#run-code-button` / `button.run-code` / `button:has-text("Run Code")`, wait for test run execution feedback.
     - Submit Code button: Click `#submit-code-button` / `button.submit-code` / `button:has-text("Submit")`, wait for submission response.
     - Verification: Confirm positive submission feedback (`Solved!`, score badge, modal confirmation).
     - State tracking: Record `status="COMPLETED"`, `result="PASSED"`, attempt count, timestamp.
3. **Pipeline Orchestrator (`run_pipeline`)**:
   - Complete lifecycle: `login()` -> `discover_pending_problems(limit)` -> loop over pending `solve_problem()` -> `reporter.generate_markdown_report()`.

Write your full blueprint and design in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m3_2/handoff.md`.
Send a completion message back to parent when done.
