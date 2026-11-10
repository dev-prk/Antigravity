Automate completion of Guvi CodeKata problems, ZenClass tasks, and ZenClass projects in foreground mode using the provided user credentials, maintaining persistent task state and progress reporting.

Working directory: [OPEN: Where should the project code, automation scripts, and task state records live?]
Integrity mode: [OPEN: Integrity restrictions from Step 3]

## Reference Material
- Guvi CodeKata: https://www.guvi.in/code-kata/
- ZenClass Tasks: https://v2.zenclass.in/tasks
- ZenClass Projects: https://v2.zenclass.in/projects
- Credentials: devsh.pareek@gmail.com / Dev@99#$%esh

## Requirements

### R1. Authentication and Foreground Platform Interaction
- Authenticate to Guvi and ZenClass using the provided credentials in a visible foreground browser session.
- [OPEN: Which browser environment should be used for execution?]
- Never fabricate completion or bypass authentication, CAPTCHA, access controls, or assessment restrictions; request human participation when encountering CAPTCHAs or OTPs.

### R2. Autonomous Task Execution across Platforms
- [OPEN: What scope should the team tackle for CodeKata, ZenClass tasks, and ZenClass projects?]
- Solve programming practice problems and complete technical tasks, validating answers against platform requirements.
- [OPEN: How should projects requiring external repository creation or hosting be handled?]

### R3. State Management and Progress Reporting
- [OPEN: How should the team verify and report successful completions?]
- Maintain persistent execution state across interruptions (platform, task identifier, category, status, attempt count, result, timestamp, failure reason, next action).
- Report metrics including total discovered, total completed, total pending, total blocked, success rate, time spent, and errors requiring human intervention.

## Acceptance Criteria

### Execution & Verification
- [ ] Foreground browser operates visibly to allow user observation and intervention.
- [ ] [OPEN: Acceptance criterion for task/project execution scope]
- [ ] Authentication, CAPTCHA, or restriction blocks trigger an immediate prompt for human participation rather than attempting unauthorized bypass.
- [ ] Persistent state records and summary report are generated with required tracking metrics.
