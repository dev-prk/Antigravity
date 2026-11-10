# Dispatch Assignment: Milestone 4 Implementation Worker (`worker_m4_1`)

**Timestamp**: 2026-11-10T17:35:00Z  
**Role**: Implementation Worker (`teamwork_worker`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m4_1`  
**Parent Orchestrator**: `cbd0649b-f648-4724-a244-a22a5102ccc4`  
**Milestone**: Milestone 4 — ZenClass Tasks Driver  

---

## 1. Context & Mandatory Anti-Cheating Warning

You are tasked with implementing the complete ZenClass Tasks driver (`drivers/zenclass_tasks_driver.py`), CLI integration (`main.py`), and a comprehensive unit test suite (`tests/test_m4_zenclass_tasks.py`).

> **MANDATORY INTEGRITY WARNING**:
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

---

## 2. Exclusive Write Ownership

You have exclusive write ownership of:
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/zenclass_tasks_driver.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/__init__.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/main.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/test_m4_zenclass_tasks.py`

Do NOT modify existing files outside these paths.

---

## 3. Reference Material & Inputs

Read the following before starting implementation:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_1/handoff.md` (Auth & session architecture)
4. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2/handoff.md` (Kanban crawler, dynamic 13-field modal, confirmation)
5. `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/base_driver.py`
6. `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/guvi_driver.py`

---

## 4. Implementation Requirements

### 4.1 `drivers/zenclass_tasks_driver.py` (`ZenClassTasksDriver` subclassing `BaseDriver`):
1. **Authentication & Session Lifecycle**:
   - `login(email: Optional[str] = None, password: Optional[str] = None) -> bool`:
     - Selectors: `.email-input input[placeholder="Enter your mail"]`, `.password-input input[placeholder="Enter your password "]` (verbatim trailing space!), `.sign-in-btn-container button.primary-btn.sign-in-pad`.
     - Error checking: `.invalid-feedback`, helper texts.
     - MFA Detection: `.login-mfa-active`, `.login-mfa-wrapper` -> triggers `self.check_guardrails()` for HITL pause.
     - Token Storage: reads `localStorage.getItem("authToken")` and cookies, saves session state to `data/storage_state.json`.
   - `ensure_authenticated(force_relogin: bool = False) -> bool`:
     - 4-tier recovery cascade: Fast-path URL/DOM anchor check -> Token expiry check (`(new Date).getTime() <= expiry`) -> Page probe -> Credential login fallback.
   - `get_auth_token() -> Optional[str]`

2. **Kanban Board Discovery (`discover_tasks`)**:
   - URL: `https://v2.zenclass.in/tasks`
   - Parses Kanban columns: `.active-tasks`, `.pending-tasks`, `.completed-tasks`.
   - Card selectors: `.itemactive-tasks#individual-card`, `.itempending-tasks#individual-card`, `.itemcompleted-tasks#individual-card`.
   - Card attribute extraction: title, tags, course, score, deadline, redo label.
   - Action buttons: `"Submit"`, `"Re-submit"`, `"Attend"` (external quiz -> marked BLOCKED), `"Edit"`, `"Report"`.
   - Persistence: Batch upsert into SQLite `StateManager` with `platform="zenclass_tasks"`, `category="Task"`, and 9 mandatory R3 fields.

3. **Task Detail Extraction (`get_task_details`)**:
   - Clicks `.view-task-container`.
   - Waits for `.student-view-task-main-container`.
   - Extracts title, rich HTML problem content (`.view-task-content-container`), and attachment links.
   - Cleanly dismisses detail modal via `.common-popup-close-icon-container` or `Escape`.

4. **Dynamic 13-Field Submission (`submit_task`)**:
   - Clicks `"Submit"` or `"Re-submit"`.
   - Waits for `.submit-form-container-web`.
   - Dynamic 13-field mapping table (Module 41486):
     `frontEnd_Deployed_Url`, `backEnd_Deployed_Url`, `frontEnd_SourceCode`, `backEnd_SourceCode`, `github_Url`, `g-drive_Url`, `submission_Url`, `linkedin_post_Url`, `document_Url`, `figma_Url`, `figma_prototype_Url`, `dribble_Url`, `behance_Url`.
   - Validates candidate URLs using regex `r"^(ftp|http|https)://[^ \"]+$"`.
   - Dynamically scans all `.submit-form-title-textField-wrapper`, matches `.form-label-text` to canonical field keys, and fills inputs.
   - Clicks modal submit button `.form-submit-container button.primary-btn`.

5. **UI Confirmation & State Verification (`verify_submission_confirmation`)**:
   - Waits for confirmation popup: `.sucess-popup-main-container, .success-popup-container`.
   - Verifies text match against `r"Task Submitted Suce+ss+fully"` (handling platform spelling `"Suceessfully"` and 2.0s auto-dismissal window).
   - Updates `StateManager` status to `COMPLETED`, `result="SUBMITTED"`, or records failure reason on error.

6. **Full Automation Orchestration (`run_task_pipeline`)**:
   - High-level orchestrator method: ensures auth, discovers pending tasks, processes each pending task, updates state, and returns summary stats.

7. **Strict Code Cleanliness**:
   - ZERO mock evaluate shims in production code. `page.evaluate()` is permitted ONLY for read-only browser state queries (e.g. `localStorage.getItem('authToken')` and dropdown values).

### 4.2 `main.py` CLI Integration:
- Expose `run-zenclass-tasks` (and alias `run-zenclass`) in CLI arguments.
- Wire to `ZenClassTasksDriver`.

### 4.3 `tests/test_m4_zenclass_tasks.py`:
- Comprehensive unit test suite covering:
  - Selector definitions & Module 41486 mapping table
  - Login success, credential failure, and MFA guardrail trigger
  - 4-tier session recovery cascade
  - Kanban board discovery (Active, Pending, Completed, Redo, and "Attend" quiz classification)
  - Task detail modal extraction and dismissal
  - Dynamic 13-field modal mapping & regex URL validation
  - Submission confirmation popup verification (ephemeral 2.0s and spelling resilience)
  - SQLite StateManager persistence and 9 R3 fields
  - Zero mock evaluate shims static verification
  - All `@patch` calls enforce `autospec=True`

---

## 5. Required Verification Commands

Execute and record exact results in your `handoff.md`:
1. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest -v tests/test_m4_zenclass_tasks.py`
2. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 -m unittest tests/test_m1_core.py tests/test_m2_solver.py tests/test_m3_guvi.py`
3. `cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi && python3 tests/e2e/test_runner.py --all`
4. Static check confirming zero mock evaluate shims in `drivers/zenclass_tasks_driver.py`.

---

## 6. Deliverable

Write your final handoff report to:
`/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m4_1/handoff.md`
Message the parent orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`) upon completion.
