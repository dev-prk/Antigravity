# Original User Request

## Initial Request — 2026-11-10T14:28:43Z

Automate the completion of all pending Guvi CodeKata problems, ZenClass tasks, and ZenClass projects using a visible foreground browser session and the user's provided credentials, maintaining persistent task execution state and progress reports.

Working directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
Integrity mode: development

## Reference Material
- Guvi CodeKata: https://www.guvi.in/code-kata/
- ZenClass Tasks: https://v2.zenclass.in/tasks
- ZenClass Projects: https://v2.zenclass.in/projects
- Credentials: devsh.pareek@gmail.com / Dev@99#$%esh

## Requirements

### R1. Foreground Platform Authentication and Interaction
- Authenticate to Guvi and ZenClass using the provided credentials via a visible foreground browser window (headed mode) so execution can be monitored in real time.
- Never fabricate completion or attempt to bypass authentication, CAPTCHA, access controls, or assessment restrictions; immediately halt and prompt the user when human intervention (such as CAPTCHA or OTP verification) is required.

### R2. Autonomous Problem and Task Completion
- Discover and complete all pending and uncompleted items across Guvi CodeKata, ZenClass tasks, and ZenClass projects.
- Solve programming problems and technical tasks directly, validating answers against platform test cases and submission feedback before finalizing submission.
- For ZenClass projects requiring external repository creation or deployed application URLs, prepare all solution code locally and pause to prompt the user for repository hosting or deployment links.

### R3. Persistent State Management and Progress Reporting
- Maintain a persistent state tracking file across executions recording platform, task identifier, task category, status, attempt count, result, timestamp, failure reason, and next action.
- Produce a summary report providing total discovered, total completed, total pending, total blocked, success rate, time spent, and errors requiring human intervention.

## Acceptance Criteria

### Platform Automation & Execution
- [ ] Browser session runs visibly in the foreground throughout execution.
- [ ] All discoverable pending items across Guvi CodeKata, ZenClass tasks, and ZenClass projects are either completed and submitted or marked blocked with a recorded reason.
- [ ] Encountering CAPTCHA, OTP, or identity-sensitive assessment restrictions halts execution and prompts for human participation without fabricating results or attempting unauthorized bypass.
- [ ] For projects requiring external repository hosting or live deployment URLs, solution code is prepared locally and execution pauses with an explicit prompt for human input.

### State & Verification
- [ ] Successful completion of each task is verified through positive submission feedback from the platform UI.
- [ ] A persistent state tracking file records each item's platform, identifier, category, status, attempt count, result, timestamp, failure reason, and next action.
- [ ] A summary report is generated detailing total discovered, total completed, total pending, total blocked, overall success rate, time spent, and issues requiring human intervention.
