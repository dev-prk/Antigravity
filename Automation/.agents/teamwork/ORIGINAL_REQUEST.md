# Original User Request

## Initial Request — 2026-11-10T11:51:00Z

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
