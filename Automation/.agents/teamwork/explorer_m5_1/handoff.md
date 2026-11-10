# Milestone 5 Architectural Blueprint & Discovery Report
## ZenClass Projects Driver & 5-Stage Human-in-the-Loop Lifecycle

**Date**: 2026-11-10T18:11:00Z  
**Author**: Explorer Agent (`explorer_m5_1`)  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m5_1`  
**Milestone**: Milestone 5 — ZenClass Projects Driver & R2 HITL  
**Target Files**:
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/zenclass_projects_driver.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/__init__.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/main.py`
- `/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/tests/test_m5_zenclass_projects.py`

---

## 1. Observation

Direct reverse-engineering and disassembly of the ZenClass production bundles (`1033.06eaf4ae4a25779ae700.js`, `716.07f3819f6343ad61a2cc.js`, `6581.a6715b3f05eeecc02b8f.js`, `6265.6e85c90355dd1ad153c2.js`, and `main.js`) in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/`, combined with inspection of `tests/e2e/harness/dom_fixtures.py` and `tests/e2e/tier4_workloads/test_w03_zenclass_projects_hitl_e2e.py`, yield exact empirical DOM structures, API contracts, and lifecycle patterns:

### 1.1 Route & Catalog Architecture (`https://v2.zenclass.in/projects`)
- **Route**: `/projects` (component lazy loaded via Webpack module `31033` in `1033.js`).
- **Student View Container**: `<div class="studentweb-view StudentTasksHome">` mounts `<div class="projectCardcontainer-main"><div class="row commonTaskContainer">`.
- **Kanban Columns (`col-lg-4 col-md-4 column`)**:
  1. **Active Projects**:
     - Header: `.status-container.active-Project-heading` (or `.active-projects-heading`, `.active-Project-heading`). Title displays `"Active Projects"` or `"Active Capstone"` depending on `courseKey`.
     - Counter: `.active-Project-count.common-count-container`.
     - Card Container: `.droppable-col`.
     - Card Element: `.itemactive-Project#individual-card` (or `.itemactive-Project`, attribute `data-project-id="proj-xxx"`).
  2. **Pending Projects**:
     - Header: `.status-container.pending-Project-heading` (or `.pending-projects-heading`). Title displays `"Pending Projects"` or `"Pending Capstone"`.
     - Counter: `.pending-Project-count.common-count-container`.
     - Card Element: `.itempending-Project#individual-card` (or `.itempending-Project`).
  3. **Completed Projects**:
     - Header: `.status-container.completed-Project-heading` (or `.completed-projects-heading`). Title displays `"Completed Projects"` or `"Completed Capstone"`.
     - Counter: `.completed-Project-count.common-count-container`.
     - Card Element: `.itemcompleted-Project#individual-card` (or `.itemcompleted-Project`).

### 1.2 Card Sub-Elements & Badges (`716.js` Module 73135)
- **Title**: `.Project-name-and-mark .project-name` (e.g., `"Full Stack E-Commerce Platform"`).
- **Redo Tag**: `.redo-label-container .redo-text` (renders `"Redo"` when revisions are requested; card wrapper adopts class `.common-project-redo-card` instead of `.common-padding`).
- **Category / Course**: `.project-card-course-name .project-card-course-name-wrapper`.
- **Tags**: `.languages-container .language-tag-container .language-tags .common-tags` (up to 3 tags displayed, e.g. `React`, `Node.js`, `MongoDB`).
  - Overflow tags: `.common-tags.additional-tag` displays `+N`, with onHover tooltip `.floting-tags .language-tags-float .common-tags`.
- **Score / Marks**: `.score-container .common-score-text`.
  - Evaluated >= 40%: `.common-score-text.score-value-green-text-project` (e.g. `"8/10"`).
  - Evaluated < 40%: `.common-score-text.score-value-red-text-project` (e.g. `"2/10"`).
  - Unevaluated: `.common-score-text.score-value-gray-text-project` (`"--/10"`).
- **Deadline / Timing Remaining**: `.timing-container .hours-value-text` (e.g., `"48 hrs"`, `"Deadline Exceed"`).

### 1.3 Action Buttons on Cards (`.student-project-footer .common-right-btn`)
- **View Button**: `.view-project-container` containing `.view-project-icon` and `.view-project-text` (`.project-unredo-task` or `.project-redo-task` with label `"View"`). Clicking triggers `setOpenViewTaskModal(true)`.
- **Submit Button**: `.primary-outlined-submit-btn` with inner text `"Submit"`. Present on Active/Pending unsubmitted cards.
- **Re-submit Button**: `.primary-outlined-submit-btn` with inner text `"Re-submit"`. Present on cards with `redo=true`.
- **Edit Button**: `.student-project-btn.student-project-edit-btn` with inner text `"Edit"`. Present on completed/submitted cards awaiting evaluation.
- **Report Button**: `.project-Report-btn` with inner text `"Report"`. Present on cards with `isEvaluated=true`.
- **Attend (External Quizzes / Assessments)**: As observed on tasks board, any card with `"Attend"` routes to third-party assessment portals and must be marked `BLOCKED` with `result=AWAITING_INPUT` pursuant to R1/R2.

### 1.4 Project Detail Modal Architecture (`6265.js` Module 27009)
- **Shared Component**: Projects reuses the exact same detail modal component as Tasks: `.student-view-task-main-container`.
- **Extracted Fields**:
  - Project Title: `.view-task-top-name .view-task-name`
  - Tags: `.view-task-tags-deails-div .tags-wrapper .common-tags`
  - Problem Statement / Content / Rubrics: `.view-task-text-editor-div .view-task-content-container` (dangerouslySetInnerHTML from `projectContent`)
  - Attachment Link: `a[href*='instruction'], a:has-text('Download Instruction')`
- **Modal Dismissal**: `.view-task-back-btn-container, button:has-text('✕'), .common-popup-close-icon-container, p.fs-24`.

### 1.5 Dynamic Submission Modal Architecture (`6581.js` Module 36976)
- **Shared Component**: Projects reuses the identical dynamic submission modal as Tasks: `.submit-form-container-web`.
- **Module 41486 13-Field Mapping Table**:
  - `"frontEnd_Deployed_Url"` $\leftrightarrow$ `"Frontend Deployed URL"`
  - `"backEnd_Deployed_Url"` $\leftrightarrow$ `"Backend Deployed URL"`
  - `"frontEnd_SourceCode"` $\leftrightarrow$ `"Frontend Source code"`
  - `"backEnd_SourceCode"` $\leftrightarrow$ `"Backend Source code"`
  - `"github_Url"` $\leftrightarrow$ `"Github URL"`
  - `"submission_Url"` $\leftrightarrow$ `"Submission URL"`
  - `"g-drive_Url"` $\leftrightarrow$ `"G-Drive URL"`
  - `"linkedin_post_Url"` $\leftrightarrow$ `"LinkedIn Post URL"`
  - `"document_Url"` $\leftrightarrow$ `"Document URL"`
  - `"figma_Url"` $\leftrightarrow$ `"Figma URL"`
  - `"figma_prototype_Url"` $\leftrightarrow$ `"Figma Prototype URL"`
  - `"dribble_Url"` $\leftrightarrow$ `"Dribble URL"`
  - `"behance_Url"` $\leftrightarrow$ `"Behance URL"`
- **Input Fields**: `.submit-form-title-textField-wrapper` with label `.form-label-text` and input `input[placeholder="Enter Link"], input.url-input, input[type="text"]`.
- **URL Validation**: Pre-validated with `ZENCLASS_URL_REGEX = re.compile(r"^(ftp|http|https)://[^ \"]+$")`.
- **Modal Submit Button**: `.form-submit-container button.primary-btn` (or `button:has-text("Submit")`, `button:has-text("Re-submit")`).
- **Backend Endpoints**:
  - Initial Submission: `POST /projects/submit-project` with body `{ submissionId: "...", submission: { ... } }`
  - Revision / Resubmission: `POST /projects/re-submit-project` with body `{ submissionId: "...", submission: { ... } }`
- **UI Confirmation**: Success modal `.sucess-popup-main-container, .success-popup-container, #feedback-modal` matching `re.compile(r"(?:Project|Task) Submitted (?:Suc+e+ss+fully|successfully)", re.IGNORECASE)` within a 2.0s auto-dismiss window.

---

## 2. Logic Chain

1. **Unified Platform Component Reuse**:
   - *Observation*: Disassembly of `716.js` reveals that `A.A` (Module 36976 submission modal) and `N.A` (Module 27009 detail view modal) are imported and rendered for projects identically to tasks in `8152.js`.
   - *Logic*: `ZenClassProjectsDriver` can directly leverage the proven selector structures and normalization dictionary (`LABEL_TO_FIELD_KEY`, `ZENCLASS_TASK_FIELD_MAP`) already established and hardened in Milestone 4, eliminating duplicate discovery overhead while preserving 100% platform fidelity.

2. **Strict Adherence to Requirement R2 (Human-in-the-Loop Protocol)**:
   - *Observation*: `ORIGINAL_REQUEST.md` §R2 explicitly dictates: *"For ZenClass projects requiring external repository creation or deployed application URLs, prepare all solution code locally and pause to prompt the user for repository hosting or deployment links."*
   - *Logic*: An automated driver cannot and must not attempt unauthorized creation of public GitHub repositories or Vercel/Netlify cloud hosting accounts. Instead, it must follow an explicit 5-stage pipeline:
     1. **Discovery & Rubric Extraction**: Parse title, category, rubrics, and determine required deliverable links from modal fields.
     2. **Local Code Synthesis**: Generate complete, runnable frontend and backend code, `package.json`, configuration files, and `README.md` in `projects/<slug>/`.
     3. **Local Build Verification**: Validate project directory structure, package manifests, and code health.
     4. **Interactive Human Pause**: Update state to `TaskStatus.BLOCKED` / `TaskResult.AWAITING_INPUT`, emit audible terminal bell (`\a`), and invoke `HitlHandler.request_project_links(...)` displaying local path and requesting repository/deployment URLs.
     5. **Submission & Positive Verification**: Populate user-supplied links into `.submit-form-container-web`, trigger submit, and verify positive confirmation (`.sucess-popup-main-container`).

3. **State Persistence and 9 Mandatory R3 Fields**:
   - *Observation*: Requirement R3 requires persistent SQLite state recording platform, identifier, category, status, attempt count, result, timestamp, failure reason, and next action.
   - *Logic*: `ZenClassProjectsDriver` must persist projects with `platform="zenclass_projects"`, `task_category="Project"`, recording transition states (`in_progress` -> `blocked` (during HITL pause) -> `completed` (upon UI confirmation) or `failed`).

4. **Zero Mock Evaluate Shims & Test Isolation**:
   - *Observation*: In Milestone 4, static analysis verified zero mock evaluate shims in `zenclass_tasks_driver.py` and 100% `autospec=True` on `@patch`.
   - *Logic*: `ZenClassProjectsDriver` and `tests/test_m5_zenclass_projects.py` must maintain identical standards, avoiding mock evaluate shims and ensuring Playwright CDP native interactions.

---

## 3. Caveats

- **No Unauthorized Cloud/Git API Side Effects**: In accordance with Requirement R1/R2, no automated Git account creation or external server provisioning is attempted. The runner pauses cleanly and awaits user input.
- **External Assessments ("Attend")**: If any external exam card appears on `/projects`, it is marked `BLOCKED` with reason `"External assessment requires interactive test session"` rather than fabricating completion.

---

## 4. Conclusion & Architectural Design

`ZenClassProjectsDriver` should be implemented in `zenclass_guvi/drivers/zenclass_projects_driver.py` extending `BaseDriver`.

### 4.1 Class Hierarchy and Data Structures

```python
# zenclass_guvi/drivers/zenclass_projects_driver.py

from __future__ import annotations
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import config
from core.browser import BrowserManager
from core.state_manager import StateManager, TaskStatus, TaskPlatform, TaskResult
from core.hitl_handler import HitlHandler, GuardrailType
from core.reporter import SummaryReporter
from drivers.base_driver import (
    BaseDriver,
    DriverError,
    AuthenticationError,
    GuardrailBlockedError,
    ElementNotFoundError,
)
from drivers.zenclass_tasks_driver import (
    ZenClassAuthenticationError,
    ZenClassMFABlockedError,
    ZENCLASS_TASK_FIELD_MAP,
    LABEL_TO_FIELD_KEY,
    ZENCLASS_URL_REGEX,
)

logger = logging.getLogger("drivers.zenclass_projects")

ZENCLASS_PROJECT_CONFIRMATION_REGEX = re.compile(
    r"(?:Project|Task) Submitted (?:Suc+e+ss+fully|successfully)", re.IGNORECASE
)

class ZenClassProjectError(DriverError):
    """Raised for fatal project discovery, synthesis, or submission errors."""
    pass

@dataclass
class DiscoveredProject:
    """Represents a project parsed from the ZenClass Projects Kanban board."""
    project_id: str
    title: str
    column: str  # "active", "pending", "completed"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    score: Optional[str] = None
    deadline: Optional[str] = None
    is_redo: bool = False
    action_type: str = "NONE"  # "SUBMIT", "RESUBMIT", "EDIT", "REPORT", "ATTEND", "NONE"
    raw_element: Any = None
```

### 4.2 Comprehensive Selectors Specification

```python
class ZenClassProjectsDriver(BaseDriver):
    """
    Autonomous platform driver for ZenClass Projects (https://v2.zenclass.in/projects).
    Implements 5-stage lifecycle: Discovery -> Local Synthesis -> Local Build Test -> HITL Pause -> Submit.
    """

    # Page Container & Header Selectors
    SEL_PAGE_CONTAINER = ".projectCardcontainer-main, .commonTaskContainer"
    SEL_BOARD_ROW = ".row.commonTaskContainer, .commonTaskContainer"
    SEL_PAGE_TITLE = ".task-page-title, .fs-24"
    SEL_BATCH_SELECT = ".batch-select-value, .MuiSelect-select"

    # Kanban Column Selectors
    SEL_COLUMN_ACTIVE = ".col-lg-4.col-md-4.column:has(.active-Project-heading), .active-Project-heading, .active-projects-heading"
    SEL_COLUMN_PENDING = ".col-lg-4.col-md-4.column:has(.pending-Project-heading), .pending-Project-heading, .pending-projects-heading"
    SEL_COLUMN_COMPLETED = ".col-lg-4.col-md-4.column:has(.completed-Project-heading), .completed-Project-heading, .completed-projects-heading"

    # Project Card Selectors
    SEL_CARD_ACTIVE = ".itemactive-Project#individual-card, .itemactive-Project, .itemactive-projects#individual-card"
    SEL_CARD_PENDING = ".itempending-Project#individual-card, .itempending-Project, .itempending-projects#individual-card"
    SEL_CARD_COMPLETED = ".itemcompleted-Project#individual-card, .itemcompleted-Project, .itemcompleted-projects#individual-card"

    # Card Sub-Elements
    SEL_CARD_TITLE = ".Project-name-and-mark .project-name, .project-name"
    SEL_CARD_REDO_TAG = ".redo-label-container .redo-text, .redo-text"
    SEL_CARD_COURSE = ".project-card-course-name .project-card-course-name-wrapper, .project-card-course-name"
    SEL_CARD_TAGS = ".languages-container .language-tag-container .language-tags .common-tags, .common-tags"
    SEL_CARD_SCORE = ".score-container .common-score-text, .common-score-text"
    SEL_CARD_DEADLINE = ".timing-container .hours-value-text, .project-hours-value-text, .hours-value-text"

    # Card Action Buttons
    SEL_BTN_VIEW = ".view-project-container, .view-task-icon, .view-project-text"
    SEL_BTN_SUBMIT = ".primary-outlined-submit-btn"
    SEL_BTN_EDIT = ".student-project-btn.student-project-edit-btn, .student-project-edit-btn"
    SEL_BTN_REPORT = ".project-Report-btn, .project-report-btn"

    # Project Detail Modal (Module 27009)
    SEL_MODAL_DETAIL = ".student-view-task-main-container"
    SEL_DETAIL_TITLE = ".view-task-top-name .view-task-name, .view-task-name"
    SEL_DETAIL_TAGS = ".view-task-tags-deails-div .tags-wrapper .common-tags, .common-tags"
    SEL_DETAIL_CONTENT = ".view-task-text-editor-div .view-task-content-container, .view-task-content-container"
    SEL_DETAIL_ATTACHMENT = "a[href*='instruction'], a:has-text('Download Instruction')"
    SEL_DETAIL_CLOSE_BTN = ".view-task-back-btn-container, button:has-text('✕'), .common-popup-close-icon-container, p.fs-24"

    # Dynamic 13-Field Submission Modal (Module 36976 / 41486)
    SEL_MODAL_SUBMIT = ".submit-form-container-web"
    SEL_SUBMIT_FIELD_WRAPPER = ".submit-form-title-textField-wrapper"
    SEL_SUBMIT_FIELD_LABEL = ".form-label-text"
    SEL_SUBMIT_FIELD_INPUT = "input[placeholder='Enter Link'], input.url-input, input[type='text']"
    SEL_SUBMIT_VALIDATION_ERR = ".validation-error-text"
    SEL_SUBMIT_CONFIRM_BTN = ".form-submit-container button.primary-btn, .form-submit-container button, button.submit-modal-btn"
    SEL_SUBMIT_MODAL_CLOSE = ".submit-form-container-web .common-popup-close-icon-container, button:has-text('✕')"

    # UI Positive Confirmation Popup (Module 84188)
    SEL_SUCCESS_POPUP = ".sucess-popup-main-container, .success-popup-container, #feedback-modal, .confirmation-modal"
    SEL_SUCCESS_TEXT = ".sucess-popup-text-container, .success-text, .modal-message"
    SEL_ERROR_POPUP = ".error-popup-main-container, .error-popup-icon"
```

### 4.3 Core Methods Specification

1. **Authentication & Session (Reused / Adapted from BaseDriver & Tasks Driver)**:
   - `ensure_authenticated() -> bool`: 4-tier recovery cascade checking active DOM, `localStorage.getItem("authToken")`, probe navigation to `/projects`, and credential fallback.
   - `check_guardrails() -> bool`: Detects `.login-mfa-active` and delegates to `HitlHandler`.

2. **Stage 1: Discovery & Catalog Parsing**:
   - `navigate_to_projects() -> None`: Navigates to `config.ZENCLASS_PROJECTS_URL` and waits for `.projectCardcontainer-main`.
   - `discover_projects() -> List[DiscoveredProject]`: Iterates across Active, Pending, Completed columns, parsing all card fields and batch-recording discovered items into `StateManager` (`platform="zenclass_projects"`, `task_category="Project"`).
   - `classify_project_action(card_element, is_redo: bool, column: str) -> Tuple[TaskStatus, TaskResult, str]`: Classifies cards into `PENDING`, `REDO`, `COMPLETED`, or `BLOCKED` (for external assessments).
   - `extract_project_details(project: DiscoveredProject) -> Dict[str, Any]`: Clicks `.view-project-container`, extracts HTML problem statement and requirements, and closes modal cleanly.

3. **Stage 2: Local Code Synthesis (Requirement R2 / Feature 17)**:
   - `synthesize_project_solution(project: DiscoveredProject, details: Dict[str, Any]) -> Path`:
     Creates `zenclass_guvi/projects/<project_slug>/` containing:
     - `frontend/` (or `client/`): `package.json`, `index.html`, `src/App.jsx` or vanilla JS structure.
     - `backend/` (or `server/`): `package.json`, `server.js` or `app.py` with standard REST endpoints.
     - `README.md`: Project title, description, architecture, local installation, test commands, and deployment guide.
     - Configs: `.gitignore`, `vercel.json` / `netlify.toml`.

4. **Stage 3: Local Build & Verification (Feature 18)**:
   - `verify_local_project_build(project_dir: Path) -> bool`:
     Checks for required directory structure, valid JSON in `package.json`, non-empty `README.md`, and clean syntax.

5. **Stage 4: Interactive Human Pause Protocol (Requirement R2 / Feature 19)**:
   - `acquire_project_links(project: DiscoveredProject, project_dir: Path, required_fields: List[str], user_inputs: Optional[Dict[str, str]] = None) -> Dict[str, str]`:
     - Updates `StateManager` status to `TaskStatus.BLOCKED` / `TaskResult.AWAITING_INPUT`, failure reason `"Human-in-the-loop input required"`, next action `"prompt_user"`.
     - Calls `self.hitl_handler.request_project_links(...)` passing project title, ID, local directory path, and required fields.
     - Validates URLs against `ZENCLASS_URL_REGEX`.
     - Updates `StateManager` status back to `TaskStatus.IN_PROGRESS`.

6. **Stage 5: Dynamic Modal Submission & Verification (Feature 20)**:
   - `submit_project(project: DiscoveredProject, links: Dict[str, str]) -> bool`:
     - Opens submission modal by clicking `.primary-outlined-submit-btn` or `.student-project-edit-btn`.
     - Locates `.submit-form-title-textField-wrapper` elements, maps labels to canonical keys via `LABEL_TO_FIELD_KEY`.
     - Types validated URLs into input fields.
     - Clicks modal submit button.
     - Verifies `.sucess-popup-main-container` confirmation text with `ZENCLASS_PROJECT_CONFIRMATION_REGEX`.
     - Updates `StateManager` status to `TaskStatus.COMPLETED` / `TaskResult.SUBMITTED` with duration and URL metadata.

7. **Pipeline Orchestrator**:
   - `run_projects_pipeline(limit: Optional[int] = None, project_id: Optional[str] = None) -> Dict[str, int]`:
     Orchestrates the entire 5-stage lifecycle across all actionable projects, logging progress and exporting state.

---

## 5. Verification Method

To independently verify this architectural blueprint and test suite when implemented:

1. **Verify Static Compliance (Zero Mock Evaluate Shims)**:
   ```bash
   python3 -c "
   import re
   from pathlib import Path
   content = Path('/Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/drivers/zenclass_projects_driver.py').read_text()
   assert not re.findall(r'isinstance\([^,]+evaluate,\s*(?:MagicMock|Mock)\)', content)
   assert not re.findall(r'unittest\.mock', content)
   print('AUDIT PASSED: Zero mock evaluate shims in zenclass_projects_driver.py')
   "
   ```

2. **Execute Milestone 5 Unit Test Suite**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m unittest -v tests/test_m5_zenclass_projects.py
   ```

3. **Execute E2E Projects Workload Simulation**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 tests/e2e/test_runner.py --tier 4
   ```

4. **Execute Full Suite Regression**:
   ```bash
   cd /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
   python3 -m unittest discover tests/ "test_m*.py"
   python3 tests/e2e/test_runner.py --all
   ```
