# Dispatch Assignment: Milestone 4 Explorer 1 (`explorer_m4_1`)

**Timestamp**: 2026-11-10T17:25:00Z  
**Role**: ZenClass Auth & Session Explorer (`teamwork_explorer`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_1`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Milestone**: Milestone 4 — ZenClass Tasks Driver  

---

## 1. Context & Objective
Design the authentication and session management architecture for ZenClass (`https://v2.zenclass.in/login`) for `drivers/zenclass_tasks_driver.py` and `drivers/base_driver.py`.

Requirements:
- Foreground visible browser authentication (`HEADLESS=False`) using credentials `devsh.pareek@gmail.com` / `Dev@99#$%esh`.
- Form selectors:
  - Email: `.email-input input[placeholder="Enter your mail"]`
  - Password: `.password-input input[placeholder="Enter your password "]` (note exact trailing space)
  - Sign in: `.sign-in-btn-container button.primary-btn.sign-in-pad` ("Sign in")
- MFA / OTP guardrail detection: check for `.login-mfa-active` and `.login-mfa-wrapper`. Must halt and delegate to `core/hitl_handler.py` without attempting bypass.
- Session persistence & multi-tier recovery:
  - `localStorage.getItem("authToken")`
  - Cookie persistence (`document.cookie` / Playwright `storage_state.json`)
  - Fast-path verification: probe `/dashboard` or `/tasks` for active session before re-entering credentials.

Read:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/handoff.md`
4. `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/base_driver.py`

Deliverable:
Write technical blueprint to:
`/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_1/handoff.md`
Message orchestrator `cbd0649b-f648-4724-a244-a22a5102ccc4` upon completion.
