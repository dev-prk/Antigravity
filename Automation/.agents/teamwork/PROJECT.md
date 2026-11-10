# Project: Know Me (Stage 1) — Devesh Pareek Career Profile

## Architecture
- Source Inputs: Existing resume directory (`/Users/devesh/Documents/Resume`) + 8 Job Portals via Brave
- Intermediate Snapshots: `~/resume/profile_backup.md`
- Core Deliverables: `~/resume/master_profile.md`, `~/resume/targets.md`
- Gate Deliverable: Gate 1 Summary & Proposed Target Roles / Seniority (HALTED FOR USER APPROVAL)

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Ingest Existing Resume | Extract all history from `/Users/devesh/Documents/Resume` | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Extract 8 Portals | Extract profiles from Talent500, Instahyre, Naukri, Indeed, Foundit, Glassdoor, LinkedIn, Turing into `profile_backup.md` | M2 | ORIGINAL_REQUEST §R1 |
| 3 | Consolidate Master Profile | Build `master_profile.md` with dates, >=2 achievements per employer, flag conflicts | M3 | ORIGINAL_REQUEST §R1 |
| 4 | Capture Target Criteria | Build `targets.md` with roles, locations, compensation, notice period, exclusions | M3 | ORIGINAL_REQUEST §R1 |
| 5 | Gate 1 Review & Proposal | Formulate 2-3 target roles/seniority, audit integrity, pause for approval | M4 | ORIGINAL_REQUEST §R2 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Resume Materials Ingestion | Read `/Users/devesh/Documents/Resume` and extract career records | none | DONE (conv: fc28e610-771a-402c-aa12-120486b83d85) |
| 2 | M2: Portal Profiles Extraction | Brave extraction across 8 portals into `~/resume/profile_backup.md` | none | DONE (conv: f7dbf6bf-0212-4f02-b611-9ba471568204) |
| 3 | M3: Consolidation | Create `~/resume/master_profile.md` and `~/resume/targets.md` | M1, M2 | DONE (conv: f9a979bc-ee47-49c2-b4ee-47eba0480f80) |
| 4 | M4: Gate 1 Verification & Pause | Review, Audit, Propose 2-3 target roles & seniority, halt at Gate 1 | M3 | DONE (Gate Result: PASS, Halted at Gate 1) |

## Code Layout / Artifacts
- `/Users/devesh/resume/profile_backup.md` — Portal profile snapshots (DONE)
- `/Users/devesh/resume/master_profile.md` — Master profile with verified career achievements & dates (DONE)
- `/Users/devesh/resume/targets.md` — Target search criteria & compensation expectations (DONE)
- `/Users/devesh/Documents/Antigravity/Automation/.agents/teamwork/` — Coordination metadata
