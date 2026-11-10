# Dispatch Assignment: Milestone 4 Explorer 2 (`explorer_m4_2`)

**Timestamp**: 2026-11-10T17:25:00Z  
**Role**: ZenClass Tasks Crawler & Submission Pipeline Explorer (`teamwork_explorer`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Milestone**: Milestone 4 — ZenClass Tasks Driver  

---

## 1. Context & Objective
Design the task discovery, Kanban board parsing, dynamic 13-field modal submission, and platform verification pipeline for ZenClass Tasks (`https://v2.zenclass.in/tasks`).

Requirements:
- Kanban board discovery:
  - Active tasks: `.itemactive-tasks#individual-card`
  - Pending tasks: `.itempending-tasks#individual-card`
  - Completed tasks: `.itemcompleted-tasks#individual-card`
  - Task name, course/session, score, tags, and deadline parsing.
- Task detail & problem extraction:
  - Clicking `.view-task-container` opens `.student-view-task-main-container`.
  - Extract `.view-task-name` and problem content `.view-task-content-container`.
- Dynamic 13-field modal submission (Module 41486):
  - Modal container: `.submit-form-container-web`
  - 13 possible fields mapping:
    - `"frontEnd_Deployed_Url"`, `"backEnd_Deployed_Url"`, `"frontEnd_SourceCode"`, `"backEnd_SourceCode"`, `"github_Url"`, `"g-drive_Url"`, `"submission_Url"`, `"linkedin_post_Url"`, `"document_Url"`, `"figma_Url"`, `"figma_prototype_Url"`, `"dribble_Url"`, `"behance_Url"`.
  - Field inputs: `.submit-form-title-textField-wrapper input[placeholder="Enter Link"]`.
  - URL validation: `/^(ftp|http|https):\/\/[^ "]+$/`.
  - Submit button: `.form-submit-container button.primary-btn`.
- Platform UI verification:
  - Detect positive UI confirmation popup containing `"Task Submitted Suceessfully"` or `"Task Submitted Successfully"`.
- State tracking & persistence:
  - Record each discovered/submitted task in SQLite `StateManager` with platform="zenclass_tasks", category="Task", status, attempts, timestamp, result.
- Clean design: ZERO mock evaluate shims in production code. All interactions through genuine Playwright calls.

Read:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/handoff.md`
4. `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/base_driver.py`
5. `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/guvi_driver.py`

Deliverable:
Write technical blueprint to:
`/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2/handoff.md`
Message orchestrator `cbd0649b-f648-4724-a244-a22a5102ccc4` upon completion.


## 2026-11-10T17:23:06Z
Received from orchestrator `cbd0649b-f648-4724-a244-a22a5102ccc4`:
You are `explorer_m4_2`, ZenClass Tasks Crawler & Submission Pipeline Explorer for Milestone 4.
Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2
Assignment: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2/DISPATCH.md

Read:
1. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md
2. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md
3. /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/handoff.md
4. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/base_driver.py
5. /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/guvi_driver.py

Tasks:
Design the task discovery, Kanban board parsing, dynamic 13-field modal submission, and platform verification pipeline for ZenClass Tasks (`https://v2.zenclass.in/tasks`):
- Kanban board columns (Active, Pending, Completed) card extraction.
- Task detail modal (`.student-view-task-main-container`).
- Dynamic 13-field modal mapping (Module 41486) with regex URL validation.
- Platform UI confirmation popup detection (`Task Submitted Suceessfully` / `Task Submitted Successfully`).
- SQLite StateManager persistence across attempts.
- Zero mock evaluate shims in production code.

Write your report to:
/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2/handoff.md
Message orchestrator `cbd0649b-f648-4724-a244-a22a5102ccc4` when finished.
