Use a team with the following roles requested by the user: 1. RESEARCHER (reads profiles, researches market and ATS; files only, no browser), 2. RESUME WRITER (builds one resume per job; files only, no browser), 3. RESUME QA (checks every resume; never the same agent as Writer), 4. BROWSER OPERATOR (the only agent allowed to control Brave; edits profiles, finds jobs, applies). Get Devesh Pareek the best possible interviews: optimize job-portal profiles, then apply to well-matched jobs with a custom ATS-safe resume per job, starting immediately with Stage 1 only.

Working directory: [OPEN: Working directory path, default ~/resume]
Integrity mode: [OPEN: Integrity mode: development | demo | benchmark]
[OPEN: The team must NOT restrictions if any chosen]

## Requirements

### R1. Stage 1 Profile Extraction and Baseline Consolidation
- The Browser Operator extracts current profile content across the 8 specified portals (Talent500, Instahyre, Naukri, Indeed India, Foundit, Glassdoor India, LinkedIn, Turing) using Brave.
- The Researcher reviews existing resume materials ([OPEN: Path to existing resume file]) and portal data.
- Save raw snapshots of all 8 profiles into `profile_backup.md`.
- Consolidate all background details into `master_profile.md`. Every employer entry must include dates and at least 2 verifiable achievements. Flag any conflicting information across sources.
- Query the user for target criteria (target roles, location/remote preference, minimum salary, notice period, current/expected CTC, roles to avoid) and save entries in `targets.md`.

### R2. Gate 1 Presentation and Hold
- Formulate 2-3 proposed target roles and corresponding seniority levels based on `master_profile.md`.
- Halt execution at Gate 1 and present the proposed target roles to the user, waiting for explicit user approval before any subsequent stage can begin.

### R3. Operational Constraints and Guardrails
- Truthfulness: Never invent, extrapolate, or inflate skills, titles, dates, metrics, employers, or degrees. Use only verified facts from `master_profile.md`.
- LinkedIn restriction: Absolutely NO direct messages, InMails, or connection requests.
- Escalation halts: Immediately stop and prompt the user upon encountering CAPTCHA, OTP, login prompts, passwords, payments, or unfamiliar portal features.
- Concurrency & handoffs: Maximum 3 agents active concurrently. Browser actions must be strictly sequential (Operator only).

## Verification Resources
[OPEN: Verification resources or test suites]

## Acceptance Criteria

### Baseline Deliverables
- [ ] `profile_backup.md` is populated with raw profile text extracted from each of the 8 specified job portals.
- [ ] `master_profile.md` contains structured employment history where every employer has chronological dates and at least 2 achievements, with any discrepancies explicitly flagged.
- [ ] `targets.md` captures target roles, locations, compensation ranges, notice period, and exclusions.
- [ ] Gate 1 summary proposing 2-3 target roles and seniority is displayed to the user and execution halts awaiting OK.

### Safety and Compliance
- [ ] No LinkedIn messages, InMails, or connection requests were initiated.
- [ ] No unconfirmed or unapproved credentials or form submissions occurred when encountering authentication or verification challenges.
