Filter and solve all Medium and Hard difficulty practice questions on Guvi CodeKata in headless background mode, submitting verified solutions and recording persistent state.

Working directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
Integrity mode: [OPEN: Which integrity restrictions apply?]

## Reference Material
- Target platform: Guvi CodeKata (`https://www.guvi.in/code-kata/`)
- Credentials: devsh.pareek@gmail.com / Dev@99#$%esh
- Existing codebase: `drivers/guvi_driver.py`, `solver/code_generator.py`, `solver/extractor.py`, `core/browser.py`, `config.py`, `data/automation_state.db`

## Requirements

### R1. Headless Background Execution
Run the browser automation entirely in background headless mode (`headless=True`) using the existing browser context manager and credentials, ensuring no visible browser windows or disruptions to ongoing user desktop work.

### R2. Medium and Hard Problem Solving
Discover and filter all Medium and Hard difficulty practice questions on Guvi CodeKata, extract statements and test cases, generate solutions [OPEN: Target programming language], verify them against platform test cases, and submit verified solutions.

### R3. Persistent State Tracking
Record problem statuses, execution attempts, test results, and timestamps in SQLite `data/automation_state.db` [OPEN: Failure handling policy].

## Acceptance Criteria

### Execution Mode
- [ ] Browser automation executes in headless background mode without opening foreground browser windows or interrupting user activities.

### Problem Solving & Platform Verification
- [ ] Guvi CodeKata catalog is filtered to locate all Medium and Hard difficulty practice questions.
- [ ] Generated solutions pass platform test cases and are successfully submitted for each processed question.
- [ ] Each question's progress, outcome, and execution metrics are recorded in `data/automation_state.db`.
