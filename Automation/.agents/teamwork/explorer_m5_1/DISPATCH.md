## 2026-11-10T18:03:22Z
You are an exploration agent for Milestone 5 (ZenClass Projects Driver & Platform Automation).

## Identity & Context
- Identity: M5 Explorer 1 Projects Platform Discovery & Submission Design
- Parent Orchestrator ID: cbd0649b-f648-4724-a244-a22a5102ccc4
- Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m5_1
- Project workspace directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
- Read references before starting:
  - /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md
  - /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md
  - /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m4_1/handoff.md
  - /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/zenclass_tasks_driver.py

## Mission & Scope
Investigate the platform-level architecture for ZenClass Projects (`https://v2.zenclass.in/projects`):
1. Project catalog discovery: DOM hierarchy, card layout (Kanban columns: Active, Pending, Completed, or list view), card selectors, badges (score, deadline, status, tags).
2. Action buttons and classification: "Submit", "Re-submit", "View", "Edit", "Report", "Attend" (if any).
3. Project Detail Extraction: project title, project ID, description, problem statement, requirements, deliverables, rubrics, tags.
4. Submission Modal Architecture:
   - Triggering selector (e.g., clicking card or action button).
   - Modal container selector.
   - Input fields: Frontend Deployed URL, Frontend Source Code (GitHub), Backend Deployed URL, Backend Source Code, Comments/Notes.
   - Modal submission button and confirmation popup (`.sucess-popup-main-container`).
5. Design the class structure and methods for `ZenClassProjectsDriver(BaseDriver)` in `drivers/zenclass_projects_driver.py`.
6. Deliver a structured architectural blueprint in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m5_1/handoff.md`.
7. Send a completion message to the parent orchestrator when done.
