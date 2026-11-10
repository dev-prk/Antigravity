# DISPATCH — Worker M2 (Browser Operator)

## Task Objective
Extract current profile content across 8 job portals using Brave and compile raw profile snapshots into `/Users/devesh/resume/profile_backup.md`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Target Portals
1. Talent500: https://talent500.com/jobs/
2. Instahyre: https://www.instahyre.com/candidate/opportunities/?matching=true
3. Naukri: https://www.naukri.com/mnjuser/homepage
4. Indeed India: https://in.indeed.com/
5. Foundit: https://www.foundit.in/seeker/profile
6. Glassdoor India: https://www.glassdoor.co.in/Community/index.htm
7. LinkedIn: https://www.linkedin.com/feed/
8. Turing: https://work.turing.com/jobs

## Scope & Instructions
1. Ensure `/Users/devesh/resume/` directory exists.
2. Control Brave browser sequentially to inspect the logged-in candidate profile for each of the 8 portals above.
3. For each portal, extract:
   - Full name, headline/title, location
   - Summary / Bio
   - Complete work experience (employer, title, start/end dates, key bullets/achievements)
   - Skills listed and assessments/certifications
   - Education details
   - Stated preferences: target role, target CTC, notice period, preferred locations (if available)
   - Profile completion score or status
4. Compile all raw snapshot content into `/Users/devesh/resume/profile_backup.md`, formatted clearly with a dedicated section for each portal.
5. Write your detailed handoff in `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1/handoff.md`.

## Strict Guardrails & Safety
- **LinkedIn safety**: Absolutely NO direct messages, InMails, or connection requests.
- **Escalation halts**: Immediately stop and report if you encounter CAPTCHA, OTP, login prompts (do NOT attempt to enter credentials or bypass), passwords, payment requests, or unfamiliar site features.
- Browser interactions MUST be sequential.
- Read `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md` and `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md` before starting.

## 2026-11-10T11:54:36Z
You are Browser Operator (worker_m2_1).
Your working directory is: `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1/`.
You MUST read:
1. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/ORIGINAL_REQUEST.md`
2. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/PROJECT.md`
3. `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1/DISPATCH.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your task:
Control Brave browser to extract current profile content across the 8 specified job portals:
1. Talent500: https://talent500.com/jobs/
2. Instahyre: https://www.instahyre.com/candidate/opportunities/?matching=true
3. Naukri: https://www.naukri.com/mnjuser/homepage
4. Indeed India: https://in.indeed.com/
5. Foundit: https://www.foundit.in/seeker/profile
6. Glassdoor India: https://www.glassdoor.co.in/Community/index.htm
7. LinkedIn: https://www.linkedin.com/feed/
8. Turing: https://work.turing.com/jobs

Make sure `/Users/devesh/resume/` exists.
Extract profile snapshots for each portal (name, headline, bio, experience with dates & achievements, skills, education, target role/compensation preferences).
Write the consolidated raw snapshot to `/Users/devesh/resume/profile_backup.md` with clearly demarcated sections for each portal.
Write your handoff report to `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/worker_m2_1/handoff.md`.

STRICT CONSTRAINTS & GUARDRAILS:
- You are the ONLY agent permitted to control Brave. All browser interactions must be sequential.
- LinkedIn safety: Absolutely NO direct messages, InMails, or connection requests.
- Escalation halts: Immediately stop and report if you encounter CAPTCHA, OTP, login prompts (do not attempt to log in), passwords, payment requests, or unfamiliar site features.
When finished, notify me with send_message.
