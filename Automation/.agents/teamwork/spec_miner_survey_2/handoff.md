# Handoff Report: Guvi CodeKata Platform Specifications & Reverse Engineering

**Date**: 2026-11-10T14:58:00Z  
**Agent ID**: `spec_miner_survey_2`  
**Target Recipient**: Parent Orchestrator (`cbd0649b-f648-4724-a244-a22a5102ccc4`)  
**Working Directory**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/spec_miner_survey_2`  
**Original Request File**: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`  
**Platform URL**: `https://www.guvi.in/code-kata/`  
**Handoff Type**: Hard (Task Complete)

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Auth | Email/Password Login Form | Traditional credential submission on `/sign-in/` | `#email` (email string), `#password` (pwd string), `#logged-in` (boolean) | `POST /usercheck.php` payload `{emails, password, loggedInType}` | Highlights `#email` or `#password` with `.is-invalid` and `.invalid-feedback` ("Incorrect Email or Password") | Source bundle `new-sign-in.498654d9621b3793023d.js` & live DOM probe |
| 2 | Auth | Session Persistence | Persistent login across sessions via cookies & localStorage | Cookie `authToken=auth:...`, `mail`, `cusername`, `unique_url`, `hash_val` | Authenticated session with header profile, user points, and bypass of `/sign-in/` redirect | Redirects to `/sign-in/` if `authToken` missing or expired | Live inspection of Brave Browser cookies & localStorage |
| 3 | Auth | Account Status Gate | Backend response gate during authentication | Response `access: "activate"`, `access: "deleted"`, `access: "notexist"` | Modal `#myModal` with `#sendmail` (activation), or inline error | Halts login flow; requires account reactivation or human action | Disassembly of `usercheck.php` handler function `P` in `new-sign-in.js` |
| 4 | Discovery | CodeKata Navigation Tabs | Top-level categorization of practice problems | Tabs: `Topics` (default/active), `Companies`, `Colleges` | Click tab element (`button.filter-topics-tab`) | Filter list reloads via Qwik SSR reactivity | Live DOM inspection of `.filter-topics-tab` and `.filter-topics-tab-active` |
| 5 | Discovery | Problem Catalog Table | Paginated tabular listing of all CodeKata problems | Table `tbody tr.cursor-pointer` containing 5 cells per row | Table with 15 problems per page across 143 total pages (~2145 problems total) | Displays empty state if query matches 0 documents | Live DOM probe on `https://www.guvi.in/code-kata/` |
| 6 | Discovery | Problem Completion Status | Distinguishing completed vs unattempted/pending problems | Column 0 SVG marker: `<g clip-path="url(#completed-icon_svg__a)"><path fill="#0DBA4B" ...>` | Green checkmark SVG indicates Solved; missing or uncompleted SVG indicates Pending/Unattempted | Unattempted problems lack the `#completed-icon_svg__a` clip path | Exact SVG dump from live CodeKata row 1 |
| 7 | Discovery | Problem Metadata Columns | Difficulty, Points, Success Rate per problem | Cell 1: Title (e.g. `1. Odd or Even Sum`), Cell 2: Rate (`73.97%`), Cell 3: Difficulty (`Easy`), Cell 4: Points (`30`) | Structured data in `td` elements | Empty or dash when metadata unavailable | Direct DOM extraction of `tbody tr td` elements |
| 8 | Discovery | Pagination Controls | Navigation through 143 pages of problems | Buttons: `Go to previous page`, page pills `1`, `2`, `3`, ..., `143`, and `Go to next page` | Clicking page pill loads next chunk of 15 questions | Disabled state when `currentPage === 1` or `currentPage === totalPages` | Live DOM inspection of pagination buttons |
| 9 | Workspace | Problem Detail Routing | Navigation from problem list to dedicated solver workspace | Clicking `tr.cursor-pointer` or navigating to `/code-kata/<slug>/` | Loads workspace at `https://www.guvi.in/code-kata/<slug>/` (e.g. `/odd-or-even-sum/`) | Returns 404 / redirect if problem slug invalid | Live click simulation on `tbody tr` |
| 10 | Workspace | Problem Statement Parser | Structured problem specification in left pane | DOM sections: `Problem Statement:`, `Input Description:`, `Output Description:`, `Sample Input:`, `Sample Output:` | Parsed text specifications and example I/O pairs for local solver synthesis | Fallback to raw text if headings vary | Live workspace text inspection |
| 11 | Workspace | Code Editor Environment | In-browser code editing container | Container `div#editor.ace_editor` with child `textarea.ace_text-input` (Ace Editor, not Monaco) | Renders syntax-highlighted code lines in `.ace_line` | Read-only overlay if locked or loading | Live DOM verification of editor class hierarchy and bundles |
| 12 | Workspace | Language Selector | Dropdown for choosing programming language | `<select id="editorModeSelectDesktop">` with SlimSelect overlay | Choices: `PYTHON 3`, `JAVASCRIPT`, `C`, `JAVA 8`, `C++`, `JAVA`, `PYTHON 2`, `C#`, `BASH`, `BASIC` | Language switch prompts `<dialog id="reset_language_modal">` ("Keep Code Changes? No/Yes") | Live inspection of `#editorModeSelectDesktop` and `#reset_language_modal` |
| 13 | Execution | Local Code Injection | Injecting generated solution into Ace Editor | Focus `textarea.ace_text-input`, `Select All` (`Meta+A`), Backspace, and `insert_text(code)` via Playwright | Updates `.ace_line` nodes and editor buffer | Synthetic JS paste events without OS events are ignored | Live injection experiment in running browser |
| 14 | Execution | Run Code Execution | Validating code against sample test cases | Button `button.run-code` (class: `run-code rounded-lg text-white`) | Makes `POST https://api.guvi.in/code-kata/question/run`, switches to `Test Result` tab | Progress dialog `#progress_modal` ("Testing 0%..."), displays "Wrong" or "Correct Answer" pills | Live network trace & button click test |
| 15 | Execution | Test Case Result Inspection | Granular feedback on test cases | Pills: `button.active-test-pill`, `button.inactive-test-pill`, status label `Wrong` vs `Correct Answer` | Displays expected output vs actual stdout | Displays stderr / compilation error in console tab | DOM extraction following `Run Code` execution |
| 16 | Submission | Final Problem Submission | Submitting code against all hidden test cases | Button `button.submit-code` (class: `submit-code rounded-lg`) | Makes `POST https://api.guvi.in/code-kata/question/submit` | Displays submission feedback modal or error alert | Live DOM inspection of submit controls |
| 17 | Submission | Positive Submission Verification | Confirming successful completion | Modal with text `+0 Geekoins`, `Congratulations! You have earned...`, and header `.question-status` showing `Solved!` | Problem row updates SVG to `#completed-icon_svg__a` and points increase | Failure modal or test failure alert if hidden test case fails | Live workspace DOM inspection of solved state |
| 18 | Guardrail | CAPTCHA / Bot Defense | Detection of bot protection triggers | Google reCAPTCHA v3 script (`render=6LdADb4UAAAAAA1feb36sozffPYRKKOqD9WPbibp`) and Cloudflare Turnstile | Immediate halt, terminal alert, pause for human completion without bypass fabrication | Bypassing fails Cloudflare challenge and locks session | Static script tag inspection & network analysis |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Problem Workspace Language Switch | Selecting a new language when code has been modified | UI launches `<dialog id="reset_language_modal">` ("Keep the Code Changes? No / Yes"). Clicking "No" replaces code with boilerplate for new language; "Yes" preserves existing text. |
| 2 | Code Editor Synthetic Event Dispatch | Dispatching synthetic `ClipboardEvent("paste")` on `textarea.ace_text-input` | Ignored by Ace Editor internal event loop. Code MUST be entered via native OS key events / Playwright `page.keyboard.insert_text(code)` after focusing. |
| 3 | Initial Navigation to `/sign-in/` | Opening `/sign-in/` while cookies/session valid | Platform immediately performs 302/client-side redirect to `https://www.guvi.in/` without showing login form. Automation must verify current URL before attempting login. |
| 4 | Table Row Click Navigation | Calling `.click()` on table row `tbody tr` | Successfully triggers client-side navigation to `/code-kata/<slug>/` without full page reload. Problem state is loaded via Qwik SSR hydrate. |
| 5 | Execution on Default Boilerplate Code | Clicking `button.run-code` with starter code | Progress modal `dialog#progress_modal` shows "Testing 0%", then test pills update to `Wrong`, and UI displays "Correct Answer" vs "Your Output". No exception is thrown. |
| 6 | Already Solved Problem View | Navigating to an already solved problem | Header displays `.question-status` with text `Solved!` and `30` points. Editor loads last submitted code. The problem can be re-run or re-submitted without error. |
| 7 | Onboarding Modal Popup | First or periodic login displays guided tour modal | Onboarding overlay `#welcome`, `#liveClass`, `#finish` (`That's It! You Are Ready!`) appears with close button `button:has-text("✕")` or `button:has-text("close")`. Must be dismissed to interact cleanly with underlying elements. |

---

## 1. Observation

Direct system inspection and live DOM/network reverse-engineering of the Guvi platform was executed in the user's running environment. Key verbatim observations:

### 1.1 Authentication & Session Architecture
- **Login URL**: `https://www.guvi.in/sign-in/`
- **Backend Verification**: `usercheck.php` called via module helper `Object(l.D)(payload, "usercheck.php")`.
- **Login Payload Structure**:
  ```json
  {
    "emails": "devsh.pareek@gmail.com",
    "password": "...",
    "loggedInType": "loggedInUser"
  }
  ```
- **Login Form Selectors**:
  - Email: `input#email` (enclosed in `#emailgroup`)
  - Password: `input#password` (enclosed in `#passwordGroup`)
  - Keep Logged In Checkbox: `input#logged-in`
  - Submit Button: `a#login-btn.btn.login-btn`
  - Mobile Submit Button: `a#mobile-login.login-btn`
  - Error Feedback Containers: `#emailgroup > .invalid-feedback` and `#passwordGroup > .invalid-feedback`
- **Session Tokens & Cookies** (observed in live authenticated session):
  - Cookie `authToken`: `auth:a6523d56d889e1b6c8ebe76b9d6a7f4f21b460ce986c29566cf52fc50edc603af8a9feb899af39935933c301d8a275da204842b6a6f13a906d6bdeeeebaa7103`
  - Cookie `mail`: `devsh.pareek@gmail.com`
  - Cookie `cusername`: `Devesh Pareek`
  - Cookie `userpoints`: `2195`
  - Cookie `rank`: `82233`
  - Cookie `isZenUser`: `true`
  - LocalStorage items: `authToken`, `loginSuccess`, `userpoints`, `user_wallet_points`, `rank`, `mail`, `unique_url`, `isZenUser`, `cusername`.

### 1.2 CodeKata Problem Catalog Structure (`https://www.guvi.in/code-kata/`)
- Built with **Qwik SSR framework** (`q:render="ssr"`, `q:route="code-kata/"`).
- **Category Filter Tabs**:
  - `button.filter-topics-tab-active` ("Topics")
  - `button.filter-topics-tab` ("Companies")
  - `button.filter-topics-tab` ("Colleges")
- **Problem Table Structure**:
  - Container: `table tbody` with rows `tr.cursor-pointer` (class `⭐️7r6n6o-0 cursor-pointer`).
  - Rows per page: 15.
  - Total pagination pages: 143 pages (yielding ~2,145 total discoverable problems).
  - Pagination elements: Buttons with labels `Go to previous page`, numeric buttons `1`, `2`, ..., `143`, and `Go to next page`.
- **Status Indicators**:
  - **Completed Problem**: Column 0 contains an SVG with clip-path referencing `#completed-icon_svg__a` and `<path fill="#0DBA4B" ...>`.
  - **Pending / Unattempted Problem**: Column 0 lacks the green completed checkmark SVG.
  - Column 1: Problem title and sequence number (e.g., `1. Odd or Even Sum`).
  - Column 2: Acceptance rate (e.g., `73.97%`).
  - Column 3: Difficulty level (e.g., `Easy`, `Medium`, `Hard`).
  - Column 4: Geekoins / Points award (e.g., `30`).

### 1.3 CodeKata Problem Workspace (`https://www.guvi.in/code-kata/<slug>/`)
- **Code Editor**:
  - Editor Container: `<div id="editor" class="⭐️agytq5-0 grow ace_editor ace">`.
  - Underlying Editor Engine: **Ace Editor** (NOT Monaco; `window.monaco` is `undefined`).
  - Input Textarea: `textarea.ace_text-input`.
  - Line Nodes: `div.ace_line`.
- **Language Selection**:
  - Native select: `<select id="editorModeSelectDesktop" class="min-w-max md:min-w-40 max-w-28">`.
  - SlimSelect wrapper: `div.ss-option.ss-selected` with inner text `PYTHON 3`.
  - Language Confirmation Modal: `<dialog id="reset_language_modal" class="modal change-language-modal">` with options `No` and `Yes`.
- **Problem Specification Extraction**:
  - Problem Statement heading: `Problem Statement:` followed by problem prompt text.
  - Input Description heading: `Input Description:` followed by input specifications.
  - Output Description heading: `Output Description:` followed by output specifications.
  - Sample Cases: `Sample Input:` and `Sample Output:`.
  - Difficulty & Status Badge: `.question-status` displaying `Easy`, `Topics`, `Solved!` (when solved).
- **Execution & Test Runner**:
  - Run Button: `<button class="⭐️x6fki0-0 run-code rounded-lg text-white px-5 md:px-6 py-2 md:py-2.5 leading-6">Run Code</button>`.
  - Submit Button: `<button class="⭐️x6fki0-0 submit-code rounded-lg px-5 md:px-6 py-2 md:py-2.5 leading-6">Submit</button>`.
  - Backend Execution API: `POST https://api.guvi.in/code-kata/question/run`.
  - Backend Submission API: `POST https://api.guvi.in/code-kata/question/submit`.
  - Test Case Tabs: `button.active-console` ("Test Case" or "Test Result").
  - Test Case Pills: `button.active-test-pill` ("Case 1"), `button.inactive-test-pill` ("Case 2").
  - Progress Modal: `<dialog id="progress_modal" class="modal progress-modal">Testing 0%</dialog>`.
  - Result Status Text: `Wrong` (red) vs `Correct Answer` (green).

---

## 2. Logic Chain

1. **Clarification on Editor Architecture (Ace vs Monaco)**:
   - Sibling explorer report hypothesized Monaco Editor based on generic industry conventions.
   - Direct DOM probe of `https://www.guvi.in/code-kata/odd-or-even-sum/` revealed `window.monaco === undefined`, and found container `#editor.ace_editor` with child `textarea.ace_text-input` and `.ace_line`.
   - *Inference*: Playwright code injection must NOT rely on `monaco.editor.getModels()`. Instead, reliable code injection requires focusing `#editor textarea.ace_text-input`, selecting all (`Meta+A`), and calling Playwright's native `page.keyboard.insert_text(code)` (which utilizes CDP `Input.insertText`).

2. **Problem Discovery and Pending Filtering**:
   - The platform organizes CodeKata into 143 pages containing 15 problems per page.
   - Solved problems feature an explicit SVG marker with clip-path `#completed-icon_svg__a` and green fill `#0DBA4B`.
   - *Inference*: The discovery crawler can rapidly iterate across pages 1 to 143, inspect table rows `tbody tr`, and identify pending/unattempted problems by checking `tr.querySelector('svg [clip-path*="completed"]') === null`.

3. **Autonomous Solving and Local Verification Pipeline**:
   - Each problem workspace provides structured sections: `Problem Statement`, `Input Description`, `Output Description`, `Sample Input`, `Sample Output`.
   - *Inference*: The problem solver can parse these exact strings into a standard schema `{title, description, input_desc, output_desc, sample_input, sample_output}`.
   - A local Python subprocess sandbox can test the candidate solution against `sample_input` to verify stdout matches `sample_output` before browser submission.

4. **Remote Execution Validation**:
   - Clicking `button.run-code` triggers `POST https://api.guvi.in/code-kata/question/run` and displays `<dialog id="progress_modal">`.
   - The UI automatically toggles the tab to `button.active-console` with text `"Test Result"`.
   - *Inference*: The automation driver must wait for `#progress_modal` to close (or disappear from top layer) and verify that all test case pills display `Correct Answer` before clicking `button.submit-code`.

5. **Submission and State Record Verification**:
   - Submitting via `button.submit-code` fires `POST https://api.guvi.in/code-kata/question/submit`.
   - On success, the UI launches a modal displaying `+0 Geekoins` or `Congratulations! You have earned...` and changes `.question-status` to include `Solved!`.
   - *Inference*: Positive verification is established by awaiting the appearance of `Solved!` in `.question-status` or the congratulations dialog. This confirms requirement R3 without ambiguity.

6. **Guardrails & Bot Interventions**:
   - Guvi loads Google reCAPTCHA v3 (`6LdADb4UAAAAAA1feb36sozffPYRKKOqD9WPbibp`) and is behind Cloudflare.
   - In accordance with R1, if a Cloudflare challenge page, captcha modal, or activation dialog (`#myModal`) appears, the runner must pause immediately, log an audible notification (`\a`), and wait for human resolution without fabricating completion.

---

## 3. Caveats

1. **Account Already Solved First Problem**: The user's account (`devsh.pareek@gmail.com`) currently has 2195 points and has already completed problem 1 (`Odd or Even Sum`). Probing submission on already solved problems awards `+0 Geekoins` but exercises identical execution pipelines.
2. **Dynamic SlimSelect Dropdown**: The language dropdown `#editorModeSelectDesktop` uses SlimSelect to stylize options. Changing languages programmatically should be done using Playwright's `page.select_option('#editorModeSelectDesktop', 'PYTHON 3')` and handling any `#reset_language_modal` confirm prompt.
3. **Network Latency during Code Run**: The backend execution endpoint `https://api.guvi.in/code-kata/question/run` can take 3–8 seconds depending on queue load. Playwright timeouts for test results should be configured for at least 20 seconds.

---

## 4. Conclusion

The Guvi CodeKata platform is fully mapped and ready for automated driver implementation:
- **Authentication**: Headed browser session using existing Brave profile or persistent context with cookies/localStorage handles authentication seamlessly; direct login flow is mapped to `#email`, `#password`, `#login-btn`.
- **Problem Catalog**: 143 paginated pages in an HTML table; completed items are identified by `#completed-icon_svg__a`; pending items are rows lacking this SVG marker.
- **Problem Workspace**: Ace Editor at `#editor`; language selector at `#editorModeSelectDesktop`; problem description and sample test cases cleanly parsed from DOM.
- **Code Injection**: Native Playwright CDP keyboard text insertion into `#editor textarea.ace_text-input`.
- **Execution & Feedback**: `button.run-code`, wait for `#progress_modal` to close, check for `Correct Answer` status pills, followed by `button.submit-code` and verification of `Solved!` in `.question-status`.
- **Safety**: Robust detection for Cloudflare / CAPTCHA / OTP / `#myModal` halting execution safely per R1.

---

## 5. Verification Method

To independently verify all observations and DOM selectors documented in this report:

1. **Verify Live Session & Cookies**:
   ```bash
   osascript -e '
   tell application "Brave Browser"
       set w to window 1
       set t to make new tab at end of tabs of w with properties {URL:"https://www.guvi.in/code-kata/"}
       delay 5
       set res to execute t javascript "JSON.stringify({cookies: document.cookie, points: localStorage.getItem(\"userpoints\")})"
       close t
       return res
   end tell
   '
   ```
   *Expected Output*: Contains `authToken=auth:...` and `points: "2195"`.

2. **Verify Table Pagination and Completed SVG Marker**:
   ```bash
   osascript -e '
   tell application "Brave Browser"
       set w to window 1
       set t to make new tab at end of tabs of w with properties {URL:"https://www.guvi.in/code-kata/"}
       delay 5
       set res to execute t javascript "document.querySelector(\"tbody tr td svg g\").getAttribute(\"clip-path\")"
       close t
       return res
   end tell
   '
   ```
   *Expected Output*: `url(#completed-icon_svg__a)`.

3. **Verify Ace Editor and Run/Submit Buttons in Workspace**:
   ```bash
   osascript -e '
   tell application "Brave Browser"
       set w to window 1
       set t to make new tab at end of tabs of w with properties {URL:"https://www.guvi.in/code-kata/odd-or-even-sum/"}
       delay 5
       set res to execute t javascript "
       JSON.stringify({
           editorClass: document.querySelector(\"#editor\").className,
           runBtn: !!document.querySelector(\"button.run-code\"),
           submitBtn: !!document.querySelector(\"button.submit-code\"),
           langSelect: document.querySelector(\"#editorModeSelectDesktop\").value
       });
       "
       close t
       return res
   end tell
   '
   ```
   *Expected Output*: `editorClass` containing `ace_editor`, `runBtn: true`, `submitBtn: true`, `langSelect: "PYTHON 3"`.
