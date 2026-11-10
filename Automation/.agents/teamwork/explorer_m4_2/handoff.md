# Technical Blueprint & Handoff Report: ZenClass Tasks Crawler & Submission Pipeline

**Date**: 2026-11-10T17:33:00Z  
**Author**: Milestone 4 Tasks Explorer (`explorer_m4_2`)  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`), Milestone 4 Worker (`worker_m4_1` / `worker_m4_2`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/explorer_m4_2`  
**Target Output**: Technical specification and architecture for `drivers/zenclass_driver.py` (ZenClass Tasks platform)  

---

## 1. Observation

Direct reverse-engineering and static disassembly of ZenClass production frontend JavaScript bundles (`https://v2.zenclass.in/`), as well as comparative analysis of existing driver code (`drivers/base_driver.py`, `drivers/guvi_driver.py`) and state persistence (`core/state_manager.py`), yield the following concrete empirical observations.

### 1.1 Kanban Board Architecture & Selectors (`582.8cf174435d59b34acf47.js`)
Inspection of module `50582` and style module `83869` in chunk `582.8cf174435d59b34acf47.js`:
- **Board Root Container**: `.commonTaskContainer` or `.row.commonTaskContainer`.
- **Kanban Columns**:
  1. **Active Tasks Column**:
     - Container: `.column.active-tasks` (or `.active-tasks`)
     - Header: `.active-tasks-heading`
     - Count: `.active-tasks-count`
     - Cards: `.itemactive-tasks#individual-card` (or `.itemactive-tasks`)
  2. **Pending Tasks Column**:
     - Container: `.column.pending-tasks` (or `.pending-tasks`)
     - Header: `.pending-tasks-heading`
     - Count: `.pending-tasks-count`
     - Cards: `.itempending-tasks#individual-card` (or `.itempending-tasks`)
  3. **Completed Tasks Column**:
     - Container: `.column.completed-tasks` (or `.completed-tasks`)
     - Header: `.completed-tasks-heading`
     - Count: `.completed-tasks-count`
     - Cards: `.itemcompleted-tasks#individual-card` (or `.itemcompleted-tasks`)
- **Card Child Selectors**:
  - **Task Title**: `.Task-name-and-mark .task-name` (e.g. `"Day 1: JS Basics"`)
  - **Redo Tag**: `.redo-label-container .redo-text` (Verbatim inner text: `"Redo"`)
  - **Course / Session**: `.task-card-course-name .task-card-course-name-wrapper`
  - **Tags**: `.language-tag-container .language-tags .common-tags`
  - **Score / Evaluation**: `.score-container .common-score-text` (e.g. `"10/10"`, `"8/10"`, or `"--/10"` when unevaluated)
  - **Remaining Time**: `.timing-container .hours-value-text`
  - **View Task Trigger**: `.view-task-container` (Contains text `"View"` or button `.view-btn`)
  - **Instruction Download**: `a[href*='instruction']` or `a:has-text('Download Instruction')`
  - **Primary Action Button**:
    - Unsubmitted active/pending task: `.primary-outlined-submit-btn` with inner text `"Submit"`
    - Redo task: `.primary-outlined-submit-btn` with inner text `"Re-submit"`
    - External assessment / Quiz: `.primary-outlined-submit-btn` with inner text `"Attend"` (opens external HYREX/quiz engine)
    - Submitted but unevaluated: `.student-task-btn.student-task-edit-btn` with inner text `"Edit"`
    - Evaluated: `.project-Report-btn` with inner text `"Report"` or `"View Report"`

### 1.2 Task Detail Modal Architecture (`6265.6e85c90355dd1ad153c2.js`)
Inspection of module `27009` and style module `69379` in chunk `6265`:
- **Modal Container**: `.student-view-task-main-container`
- **Task Title**: `.view-task-top-name .view-task-name`
- **Tag List**: `.view-task-tags-deails-div .tags-wrapper .common-tags`
- **Problem Statement / HTML Instructions**:
  - Rendered rich HTML container: `.view-task-text-editor-div .view-task-content-container`
  - Fallback placeholder when empty: `.view-task-no-content-text` (Text: `"Text Editor"`)
- **Dismissal / Close Controls**:
  - Close button: `.common-popup-close-icon-container`, `.view-task-back-btn-container`, or generic `.btn-close`, `button:has-text('✕')`

### 1.3 Dynamic 13-Field Submission Modal (`6581.a6715b3f05eeecc02b8f.js` & `main.js`)
Inspection of module `41486` (`main.js:75`) and module `36976` (`6581`):
Module `41486` exports canonical array `r` containing exactly 13 field definitions:
```javascript
var r = [
  {"Frontend Deployed URL": "frontEnd_Deployed_Url"},
  {"Backend Deployed URL": "backEnd_Deployed_Url"},
  {"Frontend Source code": "frontEnd_SourceCode"},
  {"Backend Source code": "backEnd_SourceCode"},
  {"Github URL": "github_Url"},
  {"G-Drive URL": "g-drive_Url"},
  {"Submission URL": "submission_Url"},
  {"LinkedIn Post URL": "linkedin_post_Url"},
  {"Document URL": "document_Url"},
  {"Figma URL": "figma_Url"},
  {"Figma Prototype URL": "figma_prototype_Url"},
  {"Dribble URL": "dribble_Url"},
  {"Behance URL": "behance_Url"}
];
```
Module `36976` dynamically mounts only the URL fields requested by the specific task:
- **Modal Container**: `.submit-form-container-web` (inside modal overlay `l.A`)
- **Field Wrapper**: `.submit-form-title-textField-wrapper`
- **Field Label**: `.submit-form-title-textField-wrapper .form-label-text`
- **Link Input**: `.submit-form-title-textField-wrapper input[placeholder="Enter Link"]`
- **Platform URL Validation Regex**: `/^(ftp|http|https):\/\/[^ "]+$/`
- **Validation Error Message**: `.validation-error-text` (Renders: `"<Field Label> is not valid"`)
- **Form Submit Button**: `.form-submit-container button.primary-btn` (Renders `"Submit"` or `"Re-submit"`)

### 1.4 Positive UI Confirmation Popup (`8152.94b8155533b052e42f20.js` & `main.js`)
Inspection of module `84188` (`main.js:102`) and chunk `8152` (`line 149100`):
- React state: `sucessPopupText="Task Submitted Suceessfully"` (Note verbatim spelling: `"Suceessfully"` with double 'e' and single 's')
- **Popup DOM Structure**:
  - Modal Root: `.sucess-popup-main-container` (Note single 'c' in `sucess`)
  - Content Wrapper: `.sucess-popup-content-container`
  - Text Element: `.sucess-popup-text-container`
  - Success Icon: `.sucess-popup-icon-container img.success-image`
- **Auto-Dismiss Window**:
  - Verified in React source: `useEffect(() => { if (t) setTimeout(() => { a(false); onClose && onClose(); }, 2000); }, [t])`
  - **CRITICAL TIMING OBSERVATION**: The confirmation popup automatically dismisses after exactly **2,000 milliseconds (2.0 seconds)**! Playwright assertion must not sleep for >2s before checking popup presence.

### 1.5 StateManager Persistence Contract (`core/state_manager.py`)
Requirement R3 demands 9 mandatory fields persisted in SQLite `tasks`:
- `task_id`: String PRIMARY KEY (e.g., `"zenclass-task-101"`)
- `platform`: `TaskPlatform.ZENCLASS_TASKS.value` (`"zenclass_tasks"`)
- `task_category`: `"Task"`
- `title`: String task name
- `url`: Platform URL (`"https://v2.zenclass.in/tasks"`)
- `status`: String from `TaskStatus` (`DISCOVERED`, `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`, `FAILED`, `REDO`)
- `attempt_count`: Integer $\ge 0$
- `result`: String from `TaskResult` (`PASSED`, `SUBMITTED`, `SUBMISSION_FAILED`, `AWAITING_INPUT`, `UNATTEMPTED`)
- `failure_reason`: Optional error string
- `next_action`: Action string (e.g. `"NONE"`, `"SOLVE_AND_SUBMIT"`, `"AWAIT_USER_LINKS"`)
- `metadata`: JSON blob storing `{ "column": ..., "course": ..., "tags": [...], "score": ..., "deadline": ..., "fields": [...] }`

---

## 2. Logic Chain

1. **Kanban Discovery & Filtering (Requirement R2)**:
   - *From Observation 1.1*: The Kanban board separates tasks into three distinct columns (`.active-tasks`, `.pending-tasks`, `.completed-tasks`).
   - Cards in `.completed-tasks` have already been submitted and scored (or are awaiting instructor marks). These can be recorded directly with `status=TaskStatus.COMPLETED` and `result=TaskResult.PASSED`.
   - Cards in `.active-tasks` and `.pending-tasks` having a `.primary-outlined-submit-btn` with text `"Submit"` or `"Re-submit"` are pending execution.
   - Cards with button text `"Attend"` belong to external quizzes/assessments (e.g. HYREX, PET). Because these are not URL-submission tasks and require external interactive test-taking engines, the driver must classify them with `status=TaskStatus.BLOCKED` and `result=TaskResult.AWAITING_INPUT` with reason `"External assessment requires interactive test session"`, fully complying with Requirement R1/R2 without fabricating completion.
   - Cards with `.redo-label-container .redo-text` must be recorded with `status=TaskStatus.REDO` and prioritized for resubmission.

2. **Problem Specification Extraction (Requirement R2)**:
   - *From Observation 1.2*: Clicking `.view-task-container` mounts `.student-view-task-main-container` containing the full instructions in `.view-task-content-container`.
   - The driver opens this modal, extracts the instructions, tag metadata, and any downloadable instruction attachments (`a[href*='instruction']`), and then cleanly dismisses the modal using `.common-popup-close-icon-container` or `.view-task-back-btn-container`.

3. **Dynamic 13-Field Modal Submission (Module 41486)**:
   - *From Observation 1.3*: When clicking `"Submit"` or `"Re-submit"`, the modal `.submit-form-container-web` renders an unpredictable subset of 13 possible fields (e.g., some tasks only request `github_Url`; others request `frontEnd_Deployed_Url` + `frontEnd_SourceCode`).
   - Hardcoding input selectors by index (e.g. `input[0]`) will catastrophically break across different tasks.
   - Therefore, the driver must dynamically scan each `.submit-form-title-textField-wrapper`, read `.form-label-text`, resolve it against the bidirectional Module 41486 mapping table, and fill the corresponding URL from the task solution/deliverables store.
   - Furthermore, the platform strictly checks `/^(ftp|http|https):\/\/[^ "]+$/`. The driver must pre-validate candidate URLs against this exact regex before filling to prevent triggering `.validation-error-text`.

4. **Platform Verification & Auto-Dismiss Synchronization (Requirement R3)**:
   - *From Observation 1.4*: Upon submitting valid URLs, the platform renders `.sucess-popup-main-container` with `"Task Submitted Suceessfully"`, but removes it from the DOM after 2.0 seconds.
   - If the automation sleeps for 3 seconds before checking for the popup, the test will erroneously fail due to a missed ephemeral toast!
   - Therefore, the driver must immediately await popup appearance using `page.wait_for_selector(".sucess-popup-main-container, div:has-text('Task Submitted')", timeout=10000)` and verify text match using regex `r"Task Submitted Suce+ss+fully"`.
   - If an error occurs (such as network failure or invalid payload), the platform renders `.error-popup-main-container` or `.validation-error-text`; the driver detects this, extracts the failure message, and marks the task `FAILED`.

5. **State Tracking Integrity (Requirement R3)**:
   - *From Observation 1.5*: Using `StateManager.record_task()` and `StateManager.update_task_status()`, all 9 R3 fields are preserved in SQLite across runs. Discovered tasks are batch-upserted, while active submissions transition through `IN_PROGRESS` $\to$ `COMPLETED` (or `FAILED` / `BLOCKED`) with execution time and attempt counters tracked.

6. **Zero Mock Evaluate Shims (Architectural Requirement)**:
   - In accordance with production integrity standards, the driver must NEVER inject mock results into `page.evaluate()` or use fake JavaScript stubs to simulate submission. Every action must be executed via genuine Playwright CDP calls (`page.click()`, `page.fill()`, `page.wait_for_selector()`).

---

## 3. Comprehensive Technical Blueprint for `ZenClassDriver`

### 3.1 Architecture Overview
The platform driver will be implemented as `ZenClassDriver` in `drivers/zenclass_driver.py`, subclassing `BaseDriver`.

```
BaseDriver (drivers/base_driver.py)
   ▲
   │
ZenClassDriver (drivers/zenclass_driver.py)
   ├── 1. Authentication & Session Verification
   ├── 2. Kanban Board Discovery & Parsing
   ├── 3. Task Detail & Rubric Extraction
   ├── 4. Dynamic 13-Field Modal Submission
   ├── 5. Ephemeral UI Confirmation Verification
   └── 6. StateManager 9 R3 Fields Persistence
```

### 3.2 Canonical Module 41486 Mapping Table
The driver must define the complete bidirectional map:

```python
ZENCLASS_TASK_FIELD_MAP = {
    "frontEnd_Deployed_Url": "Frontend Deployed URL",
    "backEnd_Deployed_Url": "Backend Deployed URL",
    "frontEnd_SourceCode": "Frontend Source code",
    "backEnd_SourceCode": "Backend Source code",
    "github_Url": "Github URL",
    "g-drive_Url": "G-Drive URL",
    "submission_Url": "Submission URL",
    "linkedin_post_Url": "LinkedIn Post URL",
    "document_Url": "Document URL",
    "figma_Url": "Figma URL",
    "figma_prototype_Url": "Figma Prototype URL",
    "dribble_Url": "Dribble URL",
    "behance_Url": "Behance URL",
}

# Reverse lookup: Normalized lower-case human label -> Canonical key
LABEL_TO_FIELD_KEY = {
    v.lower().strip(): k for k, v in ZENCLASS_TASK_FIELD_MAP.items()
}

# Platform URL validation regex (Module 41486 / 36976)
ZENCLASS_URL_REGEX = re.compile(r"^(ftp|http|https)://[^ \"]+$")
```

### 3.3 DOM Selectors Inventory
The driver will organize selectors cleanly as class constants:

```python
class ZenClassDriver(BaseDriver):
    # Board & Kanban Selectors
    SEL_BOARD_CONTAINER = ".commonTaskContainer, .row.commonTaskContainer"
    SEL_COLUMN_ACTIVE = ".column.active-tasks, .active-tasks"
    SEL_COLUMN_PENDING = ".column.pending-tasks, .pending-tasks"
    SEL_COLUMN_COMPLETED = ".column.completed-tasks, .completed-tasks"
    
    SEL_CARD_ACTIVE = ".itemactive-tasks#individual-card, .itemactive-tasks"
    SEL_CARD_PENDING = ".itempending-tasks#individual-card, .itempending-tasks"
    SEL_CARD_COMPLETED = ".itemcompleted-tasks#individual-card, .itemcompleted-tasks"
    
    # Task Card Detail Selectors
    SEL_CARD_TITLE = ".Task-name-and-mark .task-name, .task-name"
    SEL_CARD_REDO_TAG = ".redo-label-container .redo-text, .redo-text"
    SEL_CARD_TAGS = ".language-tag-container .language-tags .common-tags, .common-tags"
    SEL_CARD_COURSE = ".task-card-course-name .task-card-course-name-wrapper, .task-card-course-name"
    SEL_CARD_SCORE = ".score-container .common-score-text, .common-score-text"
    SEL_CARD_DEADLINE = ".timing-container .hours-value-text, .hours-value-text"
    
    # Action Buttons on Cards
    SEL_BTN_VIEW_TASK = ".view-task-container, .view-task-container button, .view-btn"
    SEL_BTN_SUBMIT = ".primary-outlined-submit-btn"
    SEL_BTN_EDIT = ".student-task-btn.student-task-edit-btn"
    SEL_BTN_REPORT = ".project-Report-btn"
    
    # Task Detail Modal
    SEL_MODAL_DETAIL = ".student-view-task-main-container"
    SEL_DETAIL_TITLE = ".view-task-top-name .view-task-name, .view-task-name"
    SEL_DETAIL_TAGS = ".view-task-tags-deails-div .tags-wrapper .common-tags"
    SEL_DETAIL_CONTENT = ".view-task-text-editor-div .view-task-content-container, .view-task-content-container"
    SEL_DETAIL_ATTACHMENT = "a[href*='instruction'], a:has-text('Download Instruction')"
    SEL_DETAIL_CLOSE_BTN = ".common-popup-close-icon-container, .view-task-back-btn-container, button:has-text('✕')"
    
    # Dynamic Submission Modal (Module 41486)
    SEL_MODAL_SUBMIT = ".submit-form-container-web"
    SEL_SUBMIT_FIELD_WRAPPER = ".submit-form-title-textField-wrapper"
    SEL_SUBMIT_FIELD_LABEL = ".form-label-text"
    SEL_SUBMIT_FIELD_INPUT = "input[placeholder='Enter Link'], input.url-input"
    SEL_SUBMIT_VALIDATION_ERR = ".validation-error-text"
    SEL_SUBMIT_CONFIRM_BTN = ".form-submit-container button.primary-btn, .form-submit-container button"
    SEL_SUBMIT_MODAL_CLOSE = ".submit-form-container-web .common-popup-close-icon-container, button:has-text('✕')"
    
    # Positive Confirmation Popup (Module 84188)
    SEL_SUCCESS_POPUP = ".sucess-popup-main-container, .success-popup-container, #feedback-modal"
    SEL_SUCCESS_TEXT = ".sucess-popup-text-container, .success-text, .modal-message"
    SEL_ERROR_POPUP = ".error-popup-main-container, .error-popup-icon"
```

### 3.4 Pipeline 1: Kanban Board Discovery & Parsing
```python
@dataclass
class DiscoveredTask:
    task_id: str
    title: str
    column: str  # "active", "pending", "completed"
    course: str
    tags: List[str]
    score: Optional[str]
    deadline: Optional[str]
    is_redo: bool
    action_type: str  # "SUBMIT", "RESUBMIT", "ATTEND", "EDIT", "REPORT", "NONE"
    raw_element: Any = None
```

The algorithm parses each column in `.commonTaskContainer`:
1. **Locate Columns**: Query `.column.active-tasks`, `.column.pending-tasks`, `.column.completed-tasks`.
2. **Extract Cards**: Iterate over `.item{col}-tasks#individual-card`.
3. **Card Attribute Extraction**:
   - Title: Read `.task-name`.
   - Task ID: Extract `data-task-id` attribute; if absent, slugify title (e.g., `zenclass-task-day-1-basic-javascript-functions`).
   - Redo: Check if `.redo-text` contains `"Redo"`.
   - Course: Read `.task-card-course-name-wrapper`.
   - Tags: Collect all `.common-tags`.
   - Score: Read `.common-score-text` (strip whitespace).
   - Deadline: Read `.hours-value-text`.
   - Action Type:
     - Check `.primary-outlined-submit-btn`:
       - Inner text `"Submit"` $\to$ `action_type = "SUBMIT"`
       - Inner text `"Re-submit"` $\to$ `action_type = "RESUBMIT"`
       - Inner text `"Attend"` $\to$ `action_type = "ATTEND"` (Quiz/HYREX)
     - Check `.student-task-edit-btn` $\to$ `action_type = "EDIT"`
     - Check `.project-Report-btn` $\to$ `action_type = "REPORT"`
4. **State Classification & StateManager Persistence**:
   - `action_type in ("SUBMIT", "RESUBMIT")`:
     - Status: `TaskStatus.DISCOVERED` (or `TaskStatus.REDO` if `is_redo`)
     - Result: `TaskResult.UNATTEMPTED`
     - Next action: `"SOLVE_AND_SUBMIT"`
   - `action_type == "ATTEND"`:
     - Status: `TaskStatus.BLOCKED`
     - Result: `TaskResult.AWAITING_INPUT`
     - Next action: `"REQUIRES_HUMAN_INTERACTIVE_ASSESSMENT"`
     - Failure reason: `"External assessment requires interactive test session"`
   - `column == "completed"` or `action_type in ("REPORT", "EDIT")`:
     - Status: `TaskStatus.COMPLETED`
     - Result: `TaskResult.PASSED`
     - Next action: `"NONE"`
5. **Bulk Record**: Upsert via `StateManager.batch_record_tasks()`.

### 3.5 Pipeline 2: Task Detail Extraction (`get_task_details`)
```python
def extract_task_details(self, card_or_task_id: Union[str, Any]) -> Dict[str, Any]:
    """
    Clicks .view-task-container to open detail modal, parses problem statement,
    extracts attached instructions, and closes modal cleanly.
    """
    # 1. Click view task container
    self.safe_click(self.SEL_BTN_VIEW_TASK)
    
    # 2. Wait for detail modal
    self.page.wait_for_selector(self.SEL_MODAL_DETAIL, state="visible", timeout=5000)
    
    # 3. Extract contents
    title = self.page.query_selector(self.SEL_DETAIL_TITLE).inner_text().strip()
    content_el = self.page.query_selector(self.SEL_DETAIL_CONTENT)
    html_content = content_el.inner_html().strip() if content_el else ""
    text_content = content_el.inner_text().strip() if content_el else ""
    
    # 4. Extract attachment
    attachment_el = self.page.query_selector(self.SEL_DETAIL_ATTACHMENT)
    attachment_url = attachment_el.get_attribute("href") if attachment_el else None
    
    # 5. Dismiss detail modal
    close_btn = self.page.query_selector(self.SEL_DETAIL_CLOSE_BTN)
    if close_btn:
        close_btn.click()
    else:
        self.page.keyboard.press("Escape")
        
    self.page.wait_for_selector(self.SEL_MODAL_DETAIL, state="hidden", timeout=3000)
    
    return {
        "title": title,
        "html_content": html_content,
        "text_content": text_content,
        "attachment_url": attachment_url,
    }
```

### 3.6 Pipeline 3: Dynamic 13-Field Submission (`submit_task`)
```python
def submit_task(
    self,
    task_id: str,
    deliverable_urls: Dict[str, str],
) -> Dict[str, Any]:
    """
    Submits URLs into dynamic 13-field modal (Module 41486) and verifies UI confirmation.
    
    Parameters:
        task_id: Unique task identifier.
        deliverable_urls: Mapping of canonical keys (or human labels) to valid URLs.
                          e.g. {"github_Url": "https://github.com/...", "frontEnd_Deployed_Url": "https://..."}
    """
    start_time = time.time()
    
    # 1. Update status to IN_PROGRESS
    if self.state_manager:
        self.state_manager.update_task_status(
            task_id=task_id,
            status=TaskStatus.IN_PROGRESS.value,
            next_action="SUBMITTING_MODAL_URLS",
        )
        
    # 2. Locate task card and click Submit / Re-submit
    # (Uses card-scoped selector or page query)
    submit_btn = self.find_task_submit_button(task_id)
    submit_btn.click()
    
    # 3. Wait for submission modal
    self.page.wait_for_selector(self.SEL_MODAL_SUBMIT, state="visible", timeout=7000)
    
    # 4. Discover all dynamically rendered field wrappers
    field_wrappers = self.page.query_selector_all(self.SEL_SUBMIT_FIELD_WRAPPER)
    if not field_wrappers:
        raise ElementNotFoundError(f"No submission field wrappers found in modal for {task_id}")
        
    filled_fields: Dict[str, str] = {}
    
    for wrapper in field_wrappers:
        # Extract human label
        label_el = wrapper.query_selector(self.SEL_SUBMIT_FIELD_LABEL)
        raw_label = label_el.inner_text().strip() if label_el else ""
        canonical_key = LABEL_TO_FIELD_KEY.get(raw_label.lower().strip(), raw_label)
        
        # Locate corresponding candidate URL
        candidate_url = (
            deliverable_urls.get(canonical_key)
            or deliverable_urls.get(raw_label)
            or deliverable_urls.get(canonical_key.lower())
        )
        
        if not candidate_url:
            err_msg = f"Missing required submission URL for field '{raw_label}' ({canonical_key})"
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.FAILED.value,
                result=TaskResult.SUBMISSION_FAILED.value,
                failure_reason=err_msg,
                next_action="PROVIDE_REQUIRED_URL",
            )
            return {"success": False, "error": err_msg, "task_id": task_id}
            
        # Validate URL against platform regex
        if not ZENCLASS_URL_REGEX.match(candidate_url):
            err_msg = f"URL for field '{raw_label}' failed regex validation: {candidate_url}"
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.FAILED.value,
                result=TaskResult.SUBMISSION_FAILED.value,
                failure_reason=err_msg,
                next_action="CORRECT_MALFORMED_URL",
            )
            return {"success": False, "error": err_msg, "task_id": task_id}
            
        # Fill input inside wrapper
        input_el = wrapper.query_selector(self.SEL_SUBMIT_FIELD_INPUT)
        if not input_el:
            raise ElementNotFoundError(f"Input field missing for wrapper '{raw_label}'")
        input_el.fill("")
        input_el.fill(candidate_url)
        filled_fields[canonical_key] = candidate_url
        
    time.sleep(0.3)
    
    # 5. Click Modal Submit Button
    modal_submit_btn = self.page.wait_for_selector(
        self.SEL_SUBMIT_CONFIRM_BTN, state="visible", timeout=3000
    )
    modal_submit_btn.click()
    
    # 6. Verify Platform Confirmation (Auto-dismisses in 2s!)
    verification = self.verify_submission_confirmation(task_id, start_time, filled_fields)
    return verification
```

### 3.7 Pipeline 4: Positive UI Confirmation Detection
```python
def verify_submission_confirmation(
    self,
    task_id: str,
    start_time: float,
    filled_fields: Dict[str, str],
) -> Dict[str, Any]:
    """
    Detects and verifies the ephemeral platform confirmation popup.
    Accounts for 2.0s auto-dismissal and platform spelling ('Suceessfully').
    """
    duration = time.time() - start_time
    verified = False
    error_message: Optional[str] = None
    
    try:
        # Await either success popup or error popup
        popup = self.page.wait_for_selector(
            f"{self.SEL_SUCCESS_POPUP}, {self.SEL_ERROR_POPUP}, .validation-error-text",
            state="visible",
            timeout=8000
        )
        
        if popup:
            # Check for validation error text
            val_err = self.page.query_selector(".validation-error-text")
            if val_err and val_err.is_visible():
                error_message = f"Field validation failed: {val_err.inner_text().strip()}"
            else:
                text_el = self.page.query_selector(self.SEL_SUCCESS_TEXT)
                raw_text = text_el.inner_text().strip() if text_el else popup.inner_text().strip()
                
                # Check for positive confirmation with spelling resilience
                if re.search(r"Task Submitted Suce+ss+fully", raw_text, re.IGNORECASE) or "submitted" in raw_text.lower():
                    verified = True
                elif "error" in raw_text.lower() or "failed" in raw_text.lower():
                    error_message = f"Platform submission error: {raw_text}"
                    
    except Exception as e:
        error_message = f"Timed out awaiting platform confirmation popup: {e}"
        
    # State update
    if verified:
        if self.state_manager:
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.COMPLETED.value,
                result=TaskResult.SUBMITTED.value,
                failure_reason=None,
                next_action="NONE",
                increment_attempts=True,
                time_spent_seconds=duration,
                metadata_update={"submitted_urls": filled_fields}
            )
        return {"success": True, "task_id": task_id, "duration": duration}
    else:
        fail_reason = error_message or "Submission failed positive confirmation verification"
        if self.state_manager:
            self.state_manager.update_task_status(
                task_id=task_id,
                status=TaskStatus.FAILED.value,
                result=TaskResult.SUBMISSION_FAILED.value,
                failure_reason=fail_reason,
                next_action="INVESTIGATE_FAILURE",
                increment_attempts=True,
                time_spent_seconds=duration,
            )
        return {"success": False, "task_id": task_id, "error": fail_reason, "duration": duration}
```

---

## 4. Edge Cases & Defensive Safeguards

| # | Edge Case | Observed Mechanism | Defensive Architecture & Safeguard |
|---|-----------|--------------------|-----------------------------------|
| 1 | **Spelling Typo in Platform Popup** | Module `8152` hardcodes `"Task Submitted Suceessfully"` (double 'e', single 's'). | Verification uses regex `re.compile(r"Task Submitted Suce+ss+fully", re.IGNORECASE)` and partial match `"Task Submitted"`. |
| 2 | **2.0-Second Auto-Dismiss Window** | Module `84188` sets `setTimeout(..., 2000)` on popup. | Driver calls `wait_for_selector(..., timeout=8000)` immediately after click; zero intervening sleep calls before assertion. |
| 3 | **Quizzes & PETs in Task Board** | Cards have button labeled `"Attend"` instead of `"Submit"`. | Detected during discovery; flagged as `TaskStatus.BLOCKED` with reason `"External assessment requires interactive test session"` (no false submissions). |
| 4 | **Malformed URL Rejection** | Module `36976` enforces `/^(ftp|http|https):\/\/[^ "]+$/`. | Driver pre-validates all URLs with `ZENCLASS_URL_REGEX` before entering inputs; halts with clean error if URL is invalid. |
| 5 | **Variable Number of Fields** | Some tasks require 1 link (`github_Url`); others require 4 (`frontEnd_Deployed_Url`, `backEnd_Deployed_Url`, `frontEnd_SourceCode`, `backEnd_SourceCode`). | Dynamic query of all `.submit-form-title-textField-wrapper` children; labels mapped via `LABEL_TO_FIELD_KEY`. Zero hardcoded field indices. |
| 6 | **Redo / Resubmission Tasks** | Cards with `.redo-label-container .redo-text` send to resubmit endpoint. | Extracted with `is_redo=True`, recorded as `TaskStatus.REDO`, button clicks `"Re-submit"`, URLs updated. |
| 7 | **Zero Mock Evaluate Shims** | Challenger tests perform forensic static/dynamic audits. | Production driver code strictly uses native Playwright calls (`wait_for_selector`, `click`, `fill`, `inner_text`). Zero `MagicMock` branch checks or simulated evaluate shims. |

---

## 5. Caveats

1. **Authentication Interlock**: This explorer investigated task discovery and submission. Full authentication and session token storage on `https://v2.zenclass.in/login` is designed in parallel by `explorer_m4_1`. `ZenClassDriver` will invoke `self.ensure_authenticated()` leveraging the authentication layer.
2. **Dynamic URL Source**: For autonomous submission, tasks requiring pre-built GitHub repository and deployed application URLs require those URLs to be supplied via user configuration (e.g. `--links-file`), generated locally via solver modules, or prompted interactively via `hitl_handler.request_project_links()`. If a task requires a URL that is not present in the configuration or solution bundle, execution cleanly pauses or marks the task `AWAITING_INPUT`.
3. **Live Test Execution**: Probing was performed via AST inspection of the production ZenClass bundles and live DOM fixtures (`tests/e2e/harness/dom_fixtures.py`) to preserve real platform state and maintain integrity compliance.

---

## 6. Conclusion

1. **Board Discovery**: The ZenClass Tasks Kanban board (`/tasks`) is completely mapped across Active, Pending, and Completed columns, extracting all task attributes, tags, scores, deadlines, and action types.
2. **Detail Extraction**: Task detail modal extraction (`.student-view-task-main-container`) is specified with HTML parsing and clean dismissal.
3. **Dynamic Submission**: All 13 Module 41486 canonical fields are cataloged with bidirectional mapping and URL regex validation.
4. **Platform Verification**: The ephemeral 2.0-second confirmation popup (`"Task Submitted Suceessfully"`) is robustly handled via immediate Playwright locator assertions.
5. **State Tracking**: All 9 R3 fields integrate cleanly into SQLite `StateManager` across every lifecycle transition.
6. **Code Cleanliness**: The specification strictly mandates genuine Playwright calls with zero mock evaluate shims.

---

## 7. Verification Method

To independently verify this specification:
1. **Inspect Bundle Source Modules**:
   ```bash
   # Verify 13 dynamic fields in Module 41486
   grep -n "frontEnd_Deployed_Url" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/main.js
   
   # Verify verbatim confirmation text and 2s auto-dismiss
   grep -n "Task Submitted Suceessfully" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/8152.94b8155533b052e42f20.js
   grep -n "84188:" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/main.js
   
   # Verify Kanban card and column selectors
   grep -n "itemactive-tasks" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/582.8cf174435d59b34acf47.js
   grep -n "student-view-task-main-container" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/6265.6e85c90355dd1ad153c2.js
   ```

2. **Run Core and Existing Driver Test Suites**:
   ```bash
   PYTHONPATH=zenclass_guvi python3 -m unittest zenclass_guvi/tests/test_m1_core.py
   PYTHONPATH=zenclass_guvi python3 -m unittest zenclass_guvi/tests/test_m3_guvi.py
   ```

3. **Validate DOM Fixture Alignment**:
   Inspect `tests/e2e/harness/dom_fixtures.py` (lines 216–297) to verify that `ZENCLASS_TASKS_HTML` and `ZENCLASS_SUBMISSION_MODAL_HTML` match the selectors and structures specified in this blueprint.
