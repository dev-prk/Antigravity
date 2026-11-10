# Dispatch Log

## 2026-11-10T11:51:47Z

The user requests a team of 4 roles (/teamwork delegates): 1. RESEARCHER (reads profiles, researches market and ATS; files only, no browser), 2. RESUME WRITER (builds one resume per job; files only, no browser), 3. RESUME QA (checks every resume; never the same agent as Writer), 4. BROWSER OPERATOR (the only agent allowed to control Brave; edits profiles, finds jobs, applies). Get Devesh Pareek the best possible interviews by running Stage 1 (Know Me): extract current profiles across 8 job portals, ingest existing resume materials, consolidate into a single master profile, capture target criteria, and pause at Gate 1 with proposed target roles and seniority.

Working directory: ~/resume
Integrity mode: development

## Verification Resources
- Existing resume materials directory: `/Users/devesh/Documents/Resume`
- Target portals (logged in on Brave):
  - Talent500: https://talent500.com/jobs/
  - Instahyre: https://www.instahyre.com/candidate/opportunities/?matching=true
  - Naukri: https://www.naukri.com/mnjuser/homepage
  - Indeed India: https://in.indeed.com/
  - Foundit: https://www.foundit.in/seeker/profile
  - Glassdoor India: https://www.glassdoor.co.in/Community/index.htm
  - LinkedIn: https://www.linkedin.com/feed/
  - Turing: https://work.turing.com/jobs

## Requirements

### R1. Profile Extraction and Baseline Consolidation (Stage 1)
- The Browser Operator extracts current profile content across the 8 specified portals using Brave. The Researcher reads existing resume documents in `/Users/devesh/Documents/Resume`.
- Save raw snapshots of each of the 8 profiles in `profile_backup.md`.
- Consolidate all background details into `master_profile.md`. Every employer entry must include dates and at least 2 verifiable achievements. Flag any conflicting information across sources.
- Query the user for target criteria (target roles, location/remote preference, minimum salary, notice period, current/expected CTC, roles to avoid) and record responses in `targets.md`.

### R2. Gate 1 Review and Hold
- Formulate 2-3 proposed target roles and corresponding seniority levels based on `master_profile.md`.
- Halt execution at Gate 1 and present the proposed target roles and seniority to the user, waiting for explicit user approval before proceeding to any subsequent stage.

### R3. Operational Constraints and Guardrails
- Truthfulness: Never invent or inflate skills, titles, dates, metrics, employers, or degrees. Rely strictly on verified data in `master_profile.md`. If required details are missing, skip or prompt the user.
- LinkedIn safety: Absolutely NO direct messages, InMails, or connection requests.
- Escalation halts: Immediately stop and prompt the user upon encountering CAPTCHA, OTP, login prompts (do not attempt to log in), passwords, payment requests, or unfamiliar site features.
- Concurrency & roles: Maximum 3 agents active concurrently. Parallel execution is permitted only for research and file drafting; all browser interactions must be sequential and executed exclusively by the Browser Operator.

## Acceptance Criteria

### Deliverables
- [ ] `profile_backup.md` is created in `~/resume/` containing extracted snapshots for all 8 portals.
- [ ] `master_profile.md` is created in `~/resume/` consolidating resume documents from `/Users/devesh/Documents/Resume` and portal snapshots, with chronological dates and >= 2 achievements per employer, with any discrepancies flagged.
- [ ] `targets.md` is created in `~/resume/` capturing target roles, locations, compensation ranges, notice period, and exclusions.
- [ ] Gate 1 summary proposing 2-3 target roles and seniority is displayed to the user and execution halts awaiting user confirmation.

### Safety and Compliance
- [ ] No messages, InMails, or connection requests sent on LinkedIn.
- [ ] No automated login attempts or credential submissions occurred when encountering authentication, CAPTCHA, or OTP challenges.
- [ ] All career details in `master_profile.md` directly trace to provided resume documents or portal profiles with no invented metrics or titles.

## 2026-11-10T12:05:35Z

URGENT USER DIRECTIVE FOR BROWSER OPERATOR:
"use the same browser session instead of launching new window again and again. use tab if you have to"

Please immediately instruct the Browser Operator (`worker_m2_1` or any active/future browser subagent) to reuse the SAME existing browser session/window and open/reuse tabs within it rather than spawning new browser windows or sessions repeatedly. Ensure this directive is enforced across all browser operations.


## 2026-11-10T14:29:53Z

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

---
### Orchestrator Context & Instructions
- Identity: Project Orchestrator
- Working directory: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/orchestrator/
- Original request file: /Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md
- Project workspace directory: /Users/devesh/Documents/Antigravity/Automation/zenclass_guvi
- Maintain your progress.md and BRIEFING.md in your working directory.
- Decompose the task and dispatch to specialized worker subagents.
- Report completion back to me when done.
