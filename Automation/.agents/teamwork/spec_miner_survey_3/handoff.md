# Handoff Report: ZenClass Tasks and Projects Platform Specifications

**Date**: 2026-11-10T14:48:00Z  
**Author**: Spec Miner (spec_miner_survey_3)  
**Target Recipient**: Parent Orchestrator (Conversation ID: cbd0649b-f648-4724-a244-a22a5102ccc4)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3`  
**Reference Document**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`

---

## 1. Observation

Direct reverse-engineering and static disassembly of ZenClass production frontend bundles (`https://v2.zenclass.in/`) were conducted. Key source artifacts analyzed:
- Bundle index: `https://v2.zenclass.in/main.3431ef4b4163061fe942.js` (2.0 MB)
- Login chunk: `2586.a6a9de77739f3e953367.js` (26 KB)
- Tasks chunks: `8152.94b8155533b052e42f20.js` (156 KB), `1885.37c95e6e404454a92b47.js` (63 KB), `6581.a6715b3f05eeecc02b8f.js` (14 KB), `6265.6e85c90355dd1ad153c2.js` (13 KB), `582.8cf174435d59b34acf47.js` (24 KB)
- Projects chunks: `1033.06eaf4ae4a25779ae700.js` (10 KB), `716.07f3819f6343ad61a2cc.js` (72 KB)

### 1.1 Authentication & Session Handling
- **Application URL**: `https://v2.zenclass.in/login` (React SPA mounted at `<div id="root">`).
- **Backend Base URL**: `https://api-v2.zenclass.in` (mapped to symbol `r.BG`).
- **Direct Login POST Endpoint**: `POST https://api-v2.zenclass.in/login/` with body `{ email, password, device: "web" }`.
- **Form Selectors**:
  - Email container: `.email-input` containing Material UI TextField (`input[placeholder="Enter your mail"]`).
  - Password container: `.password-input` containing Material UI TextField (`input[placeholder="Enter your password "]` — note exact trailing space).
  - Password visibility toggle: `button[aria-label="toggle password visibility"]`.
  - Remember Me checkbox: `.radio-input-container input[type="checkbox"]`.
  - Sign-in Button: `.sign-in-btn-container button.primary-btn.sign-in-pad` with inner text `"Sign in"`.
- **Session & Token Storage**:
  - `localStorage.setItem("authToken", JSON.stringify(authToken))`
  - `localStorage.setItem("zenUserMail", ...)`
  - `localStorage.setItem("zenUserPass", ...)` (if Remember Me checked)
  - `localStorage.setItem("userRole", ...)`
  - `localStorage.setItem("userCourse", ...)`
  - `localStorage.setItem("h", ...)` (user hash)
  - Cookie fallback: `document.cookie` contains `authToken=...`.
  - Expiry check: `(new Date).getTime() <= n.expiry` (if expired, token is removed and user is redirected to `/login`).
  - Post-login navigation: User is automatically routed to `/dashboard`.
- **Authentication Error Messages**:
  - `"Email required!"`
  - `"*Incorrect email!"`
  - `"Password required!"`
  - `"Email and password required!"`
  - `"*Incorrect email or password!"`
  - `"Account disabled. Contact Coordinator."`
- **MFA / OTP Guardrail**:
  - Login response can return challenge action `"mfaRequired"`.
  - When triggered, UI adds class `login-mfa-wrapper` and `login-mfa-active` to `.login-content-wrapper` and renders challenge component `g.A` with `email` and `challenge`.
  - The automation runner MUST detect this class and halt immediately to let the human complete MFA/OTP without attempting unauthorized bypass.

### 1.2 ZenClass Tasks Platform (`https://v2.zenclass.in/tasks`)
- **Route**: `/tasks` (component lazy loaded via module `18152`).
- **Page Layout**:
  - Header: Sticky top bar with page title (`Task` or `Assignment` depending on course type) and batch dropdown (`.batch-select-value`).
  - Container: `.row.commonTaskContainer` partitioned into 3 Kanban columns:
    1. **Active Tasks**: Header `.active-tasks-heading`, item counter `.active-tasks-count`, task cards `.itemactive-tasks#individual-card`.
    2. **Pending Tasks**: Header `.pending-tasks-heading`, item counter `.pending-tasks-count`, task cards `.itempending-tasks#individual-card`.
    3. **Completed Tasks**: Header `.completed-tasks-heading`, item counter `.completed-tasks-count`, task cards `.itemcompleted-tasks#individual-card`.
- **Task Card Structure**:
  - Name: `.Task-name-and-mark .task-name` (e.g., "Day 1: JS Basics").
  - Redo tag: `.redo-label-container .redo-text` (displays "Redo" when resubmission is requested).
  - Course/Session: `.task-card-course-name .task-card-course-name-wrapper`.
  - Tags: `.language-tag-container .language-tags .common-tags` (e.g., JavaScript, HTML, CSS).
  - Score/Evaluation: `.score-container .common-score-text` (e.g. `8/10`, styled green if score >= 40%, red if < 40%, or `--/10` if unevaluated).
  - Remaining time: `.timing-container .hours-value-text` (shows countdown to deadline).
- **Task Actions & Modals**:
  - **View Task**: Clicking `.view-task-container` opens `.student-view-task-main-container`.
    - Title: `.view-task-name`
    - Tags: `.view-task-tags-deails-div .tags-wrapper`
    - Problem Statement / Instructions: Rendered HTML inside `.view-task-content-container` (from `taskContents`).
    - Attachment: `a` tag with text `"📎 Download Instruction"`.
  - **Submit Button**:
    - Unsubmitted active/pending task: `.primary-outlined-submit-btn` with label `"Submit"`.
    - Redo task: `.primary-outlined-submit-btn` with label `"Re-submit"`.
    - Submitted but unevaluated: `.student-task-btn.student-task-edit-btn` with label `"Edit"`.
    - Evaluated: `.project-Report-btn` with label `"Report"` or `"View Report"`.
    - Quiz/HYREX: `.primary-outlined-submit-btn` with label `"Attend"`.
- **Dynamic Task Submission Schema (Module 41486)**:
  - Form container: `.submit-form-container-web` inside common modal.
  - Form fields map from task `submission` object keys:
    - `"frontEnd_Deployed_Url"` $\leftrightarrow$ "Frontend Deployed URL"
    - `"backEnd_Deployed_Url"` $\leftrightarrow$ "Backend Deployed URL"
    - `"frontEnd_SourceCode"` $\leftrightarrow$ "Frontend Source code"
    - `"backEnd_SourceCode"` $\leftrightarrow$ "Backend Source code"
    - `"github_Url"` $\leftrightarrow$ "Github URL"
    - `"g-drive_Url"` $\leftrightarrow$ "G-Drive URL"
    - `"submission_Url"` $\leftrightarrow$ "Submission URL"
    - `"linkedin_post_Url"` $\leftrightarrow$ "LinkedIn Post URL"
    - `"document_Url"` $\leftrightarrow$ "Document URL"
    - `"figma_Url"` $\leftrightarrow$ "Figma URL"
    - `"figma_prototype_Url"` $\leftrightarrow$ "Figma Prototype URL"
    - `"dribble_Url"` $\leftrightarrow$ "Dribble URL"
    - `"behance_Url"` $\leftrightarrow$ "Behance URL"
  - Input field selector: `.submit-form-title-textField-wrapper input[placeholder="Enter Link"]`.
  - Field label selector: `.submit-form-title-textField-wrapper .form-label-text`.
  - Validation: Regex `/^(ftp|http|https):\/\/[^ "]+$/`. If invalid, displays `.validation-error-text` with `"<Field Name> is not valid"`.
  - Submit Button: `.form-submit-container button.primary-btn` ("Submit" or "Re-submit").
  - API Submission Endpoint: `POST https://api-v2.zenclass.in/task/task-submit` or `POST https://api-v2.zenclass.in/task/task-resubmit`.
  - Confirmation Indicator: Success popup modal with text `"Task Submitted Suceessfully"` (or `"Task Submitted Successfully"`).

### 1.3 ZenClass Projects Platform (`https://v2.zenclass.in/projects`)
- **Route**: `/projects` (component lazy loaded via module `31033`).
- **Page Layout**:
  - Sticky header with page title (`Project` or `Capstone`) and batch dropdown.
  - Container: `.projectCardcontainer-main .commonTaskContainer` partitioned into 3 columns:
    1. **Active Projects**: Header `.active-Project-heading`, item counter `.active-Project-count`, project cards `.itemactive-Project#individual-card`.
    2. **Pending Projects**: Header `.pending-Project-heading`, item counter `.pending-Project-count`, project cards `.itempending-Project#individual-card`.
    3. **Completed Projects**: Header `.completed-Project-heading`, item counter `.completed-Project-count`, project cards `.itemcompleted-Project#individual-card`.
- **Project Card Structure**:
  - Title: `.Project-name-and-mark .project-name`.
  - Redo label: `.redo-label-container .redo-text` ("Redo").
  - Tags: `.language-tag-container .language-tags`.
  - View Button: Opens project specification and requirements modal.
  - Submit Button: `.primary-outlined-submit-btn` ("Submit" or "Re-submit").
- **API Endpoints**:
  - Fetch projects: `GET https://api-v2.zenclass.in/projects/get-project-student`
  - Submit project: `POST https://api-v2.zenclass.in/projects/submit-project`
  - Resubmit project: `POST https://api-v2.zenclass.in/projects/re-submit-project`
  - Submission payload: `{ submissionId: "<id>", submission: { <key>: "<url>" } }`.

---

## 2. Logic Chain

1. **Authentication Flow (R1)**:
   - Observation 1.1 reveals the login form is rendered at `/login` with distinct Material UI fields. The token is persisted in `localStorage` under key `"authToken"` with an expiry timestamp.
   - Therefore, a headed browser session can authenticate once using credentials `devsh.pareek@gmail.com` / `Dev@99#$%esh`, confirm arrival on `/dashboard`, and reuse the session state via stored browser cookies/localStorage across executions.
   - If an MFA or OTP challenge appears (`.login-mfa-active` / `"mfaRequired"`), the automation runner cannot and must not guess OTP codes; it must emit a prominent audio/terminal prompt and pause execution until the user manually authenticates in the open browser window.

2. **Tasks Life Cycle Discovery & Submission**:
   - Observation 1.2 shows that tasks are categorized cleanly into `Active`, `Pending`, and `Completed`.
   - Any task in `Active` or `Pending` with a "Submit" or "Re-submit" button is actionable.
   - Opening the task view modal reveals the full HTML task instructions (`.view-task-content-container`).
   - Clicking "Submit" opens a dynamic submission form. The form presents 1 to 4 URL inputs depending on what the task author specified (e.g. `github_Url`, `frontEnd_Deployed_Url`).
   - Once valid URLs are entered and submitted, the platform displays the confirmation popup `"Task Submitted Suceessfully"`, providing unambiguous positive confirmation before persisting the completion record.

3. **Requirement R2 Human Pause Protocol & Local Solution Generation**:
   - ZenClass projects require external GitHub repository URLs and deployed web application URLs (e.g. Netlify/Vercel/Render).
   - Autonomous creation of third-party public cloud accounts or external git repos without user permission violates R1/R2 and integrity rules.
   - Therefore, the runner must follow an explicit 5-stage protocol:
     1. **Discovery & Parsing**: The runner parses the project title, description, rubric, and required deliverable URLs.
     2. **Local Code Synthesis**: The runner generates full, clean, production-quality project source code inside the local workspace:
        `zenclass_guvi/projects/<project_slug>/`
        containing:
        - Complete frontend (e.g. React/HTML5/CSS3/JS)
        - Complete backend (if fullstack / REST API required)
        - `README.md` with setup, local run, and deployment instructions
        - Build and configuration files (`package.json`, `.gitignore`, `netlify.toml` / `vercel.json`)
     3. **Local Test & Verification**: The runner executes local build/lint/test commands to verify the solution runs cleanly without syntax errors or broken dependencies.
     4. **Interactive Human Pause**: The runner cleanly suspends foreground execution and prints an actionable prompt:
        ```text
        ================================================================================
        [HUMAN PAUSE REQUIRED - ZENCLASS PROJECT SUBMISSION]
        Project Name: <Project Title>
        Project ID:   <Submission ID>
        Local Code:   /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi/projects/<project_slug>/

        Instructions:
        1. Create a GitHub repository with the code from the path above.
        2. Deploy the frontend to Netlify/Vercel and/or backend to Render.
        3. Enter the requested links below:

        GitHub URL:
        Frontend Deployed URL:
        ================================================================================
        ```
     5. **Submission & Verification**: Upon receiving user-supplied URLs via CLI input or config, the runner resumes the foreground browser, enters the URLs into `.submit-form-container-web`, clicks Submit, and verifies the success popup modal.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Auth | Email/Password Login | Form login on v2.zenclass.in | Email (`devsh.pareek@gmail.com`), Password | `authToken` in localStorage, cookie, redirect to `/dashboard` | Displays inline helper error `"Email required!"` or `"*Incorrect email or password!"` | Reverse engineering `2586.js` |
| 2 | Auth | Remember Me Persistence | Retains login credentials in local storage | Checkbox click | `zenUserPass`, `zenUserMail` stored | None | Disassembly of `2586.js` |
| 3 | Auth | MFA / OTP Challenge Guardrail | Step-up auth verification | OTP / Authenticator code | `mfaTrustToken`, session initiation | UI adds `.login-mfa-active`; runner must pause for human intervention | Disassembly of `2586.js` |
| 4 | Tasks | Task Category Discovery | Kanban board listing active, pending, completed tasks | Batch selection ID | 3 task arrays: `activeTasks`, `pendingTasks`, `completedTask` | Shows `.no-tasks-message` ("No Active Tasks", "Yet to Complete") | Analysis of `15415` / `582.js` |
| 5 | Tasks | Task Detail Modal Extraction | View problem statement and attached resources | Click `.view-task-container` | Modal `.student-view-task-main-container` with rendered HTML problem content | Displays `"Text Editor"` if content is null | Disassembly of `27009` / `6265.js` |
| 6 | Tasks | Dynamic Field Submission Modal | Submission popup with required URLs | Click `.primary-outlined-submit-btn` | Dynamic inputs for `github_Url`, `frontEnd_Deployed_Url`, etc. | Displays `"<Field> is not valid"` if regex fails | Disassembly of `36976` / `6581.js` |
| 7 | Tasks | Positive Submission Verification | Visual confirmation of task submission | Click Submit in modal | Success toast/popup: `"Task Submitted Suceessfully"` | Error snackbar if network or payload failure | Disassembly of `39580` & `15415` |
| 8 | Tasks | Resubmission / Redo Workflow | Submitting tasks flagged for revision | Redo task card (`.redo-text`) | Opens submission modal pre-cleared for updated links; sends to `/task/task-resubmit` | Validated identically to initial submission | Disassembly of `582.js` & `6581.js` |
| 9 | Tasks | Evaluation Score Parsing | Read marks awarded by instructors | Completed card render | Score string e.g. `8/10`, styled green (>=40%) or red (<40%) | Displays `--/10` if unevaluated | Disassembly of `582.js` |
| 10 | Projects | Project Category Discovery | Capstone/Project listing across lifecycle | Batch selection | 3 project arrays: `activeProjects`, `pendingProjects`, `completedProjects` | Shows empty state if no projects assigned | Disassembly of `31033` / `1033.js` |
| 11 | Projects | Project Detail & Rubric Extraction | View project guidelines and deliverables | Click project card view | Modal with guidelines and required URL types | None | Disassembly of `73135` / `716.js` |
| 12 | Projects | Local Code Generation & Pause Protocol | Synthesis of solution code locally + human prompt | Project specification | Local project directory with source code, tests, and CLI pause prompt | If user cancels, execution halts without falsifying data | Requirement R2 specification |
| 13 | Projects | Project Submission & Verification | Submitting repository & deployment URLs | Human-provided URLs | `POST /projects/submit-project` payload + UI success confirmation popup | Inline field validation or error toast | Disassembly of `73135` / `716.js` |
| 14 | State | Persistent Execution State (R3) | Track tasks and projects across runs | Task ID, platform, status, attempts, URLs | JSON state file tracking discovered, pending, completed, blocked | Atomic file write on each lifecycle step | Architecture specification |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Login | Trailing space in password placeholder | Selector `input[placeholder="Enter your password "]` requires exact match; generic `input[type="password"]` is more resilient |
| 2 | Login | MFA Challenge Triggered | UI adds class `.login-mfa-active` and renders challenge component. Automated form submission fails unless paused for user |
| 3 | Tasks | Spelling Typo in Success Popup | UI populates popup with `"Task Submitted Suceessfully"` (double 'e', single 's'); text match must account for exact string or partial match |
| 4 | Tasks | HYREX / Quiz / PET Tasks in Tasks Column | Tasks board includes automated quizzes with button `"Attend"`; these redirect to external assessment links rather than URL submission modals |
| 5 | Tasks | Multiple Dynamic URLs | A task may require 1 link (e.g. GitHub URL only) or multiple (e.g. Frontend Deployed + Backend Deployed + Frontend Source + Backend Source) |
| 6 | Tasks | Malformed URL Format | Regex `/^(ftp|http|https):\/\/[^ "]+$/` blocks submission and displays red validation error text; runner must validate URL format before submitting |
| 7 | Projects | Resubmission Requested (Redo) | Card displays `.redo-text` and sends to `/projects/re-submit-project` instead of `/projects/submit-project` |
| 8 | Projects | External Account Creation Block | Automation cannot create external GitHub or Netlify accounts; cleanly pauses foreground runner and prompts user for external deployment links |
| 9 | Batch Selection | Multi-Batch Enrollment | Students enrolled in multiple courses or batches see batch dropdown `.batch-select-value`; active batch must be explicitly detected and selected |

---

## 5. Caveats

- Probing was performed via deep reverse-engineering and source inspection of the live ZenClass single-page application bundle rather than active automated browser execution, as integrity rules mandate no automated state changes or spurious submissions during surveying.
- Quizzes and HYREX tests appearing in the Tasks feed require external test-taking engines and are marked out-of-scope for standard URL-based task completion; they should be flagged with an explicit status (`BLOCKED_EXTERNAL_ASSESSMENT`).

---

## 6. Conclusion

ZenClass Tasks and Projects platforms have been completely reverse-engineered and mapped into rigorous, reproducible specifications:
1. **Authentication**: Fully specified with exact DOM selectors, `localStorage` token schema, and explicit detection of MFA/OTP guardrails (`.login-mfa-active`).
2. **Tasks Platform**: Fully specified Kanban architecture (`Active`, `Pending`, `Completed`), task inspection modal, dynamic URL submission fields (Module 41486), and positive completion verification.
3. **Projects Platform**: Fully specified project lifecycle, external repository requirements, clean local project synthesis structure (`zenclass_guvi/projects/<project_slug>/`), and an interactive human pause protocol adhering strictly to Requirement R2.
4. **State & Reporting**: Direct schema definitions for persistent state tracking (Requirement R3).

---

## 7. Verification Method

To verify these specifications independently:
1. Inspect the extracted bundle modules in the working directory:
   ```bash
   grep -n "frontEnd_Deployed_Url" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/main.js
   grep -n "Task Submitted Suceessfully" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/8152.94b8155533b052e42f20.js
   grep -n "login-mfa-active" /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/raw_js/2586.a6a9de77739f3e953367.js
   ```
2. Inspect the handoff report at `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_3/handoff.md`.
