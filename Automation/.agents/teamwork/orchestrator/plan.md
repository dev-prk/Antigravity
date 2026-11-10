# Stage 1 (Know Me) Execution Plan

## Objective
Extract current profile content across 8 job portals, ingest existing resume materials from `/Users/devesh/Documents/Resume`, consolidate into a single master profile and target criteria in `~/resume/`, and halt at Gate 1 with proposed target roles and seniority.

## Roles
1. **Researcher** (teamwork_explorer): Reads profiles and resume documents in `/Users/devesh/Documents/Resume`. Files only, no browser.
2. **Browser Operator** (teamwork_worker): Controls Brave. Extracts profiles across the 8 portals into `profile_backup.md`. Sequential browser execution only.
3. **Consolidator / Resume Writer** (teamwork_worker): Consolidates baseline and portal profiles into `master_profile.md` (chronological, >= 2 achievements per employer, flags conflicts) and `targets.md`. Files only.
4. **Reviewer & Auditor** (teamwork_reviewer & teamwork_auditor): Verifies integrity, truthfulness (no hallucinations or fabrications), and checks against requirements.

## Milestones & Execution Steps
1. **Step 1: Parallel Ingestion & Portal Extraction**
   - Agent 1 (Researcher / teamwork_explorer): Read all files in `/Users/devesh/Documents/Resume` and extract career chronology, achievements, skills, and metrics.
   - Agent 2 (Browser Operator / teamwork_worker): Access Brave, visit 8 portals (Talent500, Instahyre, Naukri, Indeed India, Foundit, Glassdoor India, LinkedIn, Turing), extract profile snapshots, and write `~/resume/profile_backup.md`.
   - Concurrency: 2 active agents (<= 3 limit).
2. **Step 2: Profile & Targets Consolidation**
   - Agent 3 (Worker / teamwork_worker): Read Researcher report and `profile_backup.md`. Write `~/resume/master_profile.md` and `~/resume/targets.md`.
3. **Step 3: Verification & Integrity Forensics**
   - Reviewer (teamwork_reviewer) & Auditor (teamwork_auditor): Check requirements, traceability, discrepancies, and safety.
4. **Step 4: Gate 1 Presentation & Hold**
   - Formulate 2-3 proposed target roles and seniority levels based on `master_profile.md`.
   - Present findings, deliverables, and Gate 1 proposal to user. Halt and await explicit user confirmation.
