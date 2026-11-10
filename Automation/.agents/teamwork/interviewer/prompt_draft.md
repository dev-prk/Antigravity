Filter and solve all Medium and Hard difficulty practice questions on Guvi CodeKata in headless background mode using Python, verifying solutions against platform test cases and persisting execution state.

Working directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
Integrity mode: development

## Reference Material
- Target platform: Guvi CodeKata (`https://www.guvi.in/code-kata/`)
- Credentials: devsh.pareek@gmail.com / Dev@99#$%esh
- Existing codebase: `drivers/guvi_driver.py`, `solver/code_generator.py`, `solver/extractor.py`, `core/browser.py`, `config.py`, `data/automation_state.db`

## Verification Resources
- Guvi CodeKata platform test suites and submission feedback
- Existing pytest test suites in `tests/`
- SQLite tracking database at `data/automation_state.db`

## Requirements

### R1. Headless Background Execution
Run browser automation entirely in background headless mode (`headless=True`) using the existing browser context manager and Guvi credentials, ensuring no visible browser windows open and desktop activities remain undisturbed.

### R2. Difficulty Filtering and Problem Solving
Identify and filter all Medium and Hard difficulty practice questions on Guvi CodeKata, extract problem descriptions and constraints, generate valid Python 3 solutions, and submit them to the platform.

### R3. Failure Handling and Retries
If a problem fails platform test cases, retry generating and submitting up to 3 times per problem before recording failure details in the state database and proceeding to the next question.

### R4. Persistent State Management
Record every problem's status (success, failure, or retry count), test case outputs, and execution timestamps in SQLite `data/automation_state.db`.

## Acceptance Criteria

### Execution & Stealth
- [ ] Browser automation executes completely in headless mode without visible UI windows interfering with the user's desktop session.

### Coverage & Submission
- [ ] All Medium and Hard difficulty practice questions on Guvi CodeKata are filtered and attempted.
- [ ] Solutions generated in Python 3 pass platform test cases and receive successful submission confirmation.
- [ ] Problems failing after 3 attempts are flagged as failed in the database without halting the overall automation run.

### State Tracking & Verification
- [ ] Each attempted problem's status, attempt count, test results, and timestamp are recorded in `data/automation_state.db`.
- [ ] Existing pytest test suites in `tests/` pass without regressions.