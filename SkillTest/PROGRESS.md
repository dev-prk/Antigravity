# SkillTest — Lead DBA Resume & JD Matcher

## Brief
1. **Ask:** Build a small local web app in `~/Documents/Antigravity/SkillTest` where the user pastes their resume and a job description, and it tells them how well they match and exactly what to fix in their resume before applying (specifically for Lead DBA applications).
2. **Must-haves:**
   - "small local web app"
   - "where I paste my resume and a job description"
   - "tells me how well I match"
   - "and exactly what to fix in my resume before I apply"
   - "Put it in ~/Documents/Antigravity/SkillTest"
   - "I want to actually use this for my Lead DBA applications"
3. **Done test:** Open the local web app in a browser, load or paste a real resume (including Devesh's actual Lead DBA / Postgres / Db2 resumes) and two different real Lead DBA job descriptions, click analyze, and see: (a) an evidence-based match breakdown across DBA dimensions (DB engines, HA/DR & reliability, scale/operations, leadership/team management, automation/cloud, experience/seniority), (b) exact requirement-by-requirement matched vs. missing/weak points, and (c) concrete, truthful before → after bullet/summary/skills edits ready to copy-paste without inventing fake experience. Also test empty/bad input to verify validation.
4. **Expert gap:**
   - Generic keyword counters fail on DBA roles because ATS and hiring managers distinguish **Primary DB Engine** (PostgreSQL vs Db2 LUW vs Oracle/MySQL/MSSQL), **HA/DR stack** (Patroni, HADR, streaming replication, Pacemaker, PGD, pgBackRest, Barman, PITR), **Scale metrics** (instance count, TB size, uptime SLA, peak traffic), **Leadership proof** (team size led, mentoring, vendor transitions, incident SME, stakeholder management), and **Truthfulness constraint** (never tell a candidate to fabricate 8 years of Oracle if they have 4.7 years of Postgres + Db2; distinguish *Reframe existing experience*, *Surface from your other profile/resume*, and *True gap — address via framing/cover note*).
   - Pre-loading Devesh's real profiles (`Lead DBA`, `PostgreSQL DBA`, `Db2 LUW DBA` from his workspace) as 1-click presets alongside free paste + `.docx`/`.txt` upload makes the tool immediately usable for his actual Lead DBA applications.
   - Reliable dual engine: deterministic domain-tuned DBA ATS & requirement parser (instant, works offline) + optional live Gemini AI deep rewrite (`GEMINI_API_KEY` from `.env`) when available.
5. **Smallest version:** FastAPI + single-page HTML/JS frontend served locally, with deterministic DBA domain analyzer + live Gemini AI deep-tailoring integration, pre-loaded with Devesh's real Lead DBA resume presets and sample Lead DBA JDs, plus copy-ready bullet/headline/skills fixes.
6. **Not building:** Multi-user auth, external job board scrapers, database persistence servers, paid SaaS wrappers, or bloated React build pipelines.
7. **Unknowns:**
   - *Assume:* Single-command Python FastAPI app (`uvicorn`) using the existing Python 3.12 + `google-genai` setup and pre-loaded with Devesh's real Lead DBA resume text as a convenient default button (while keeping the paste textarea and `.docx` upload front-and-center).

## Status
- [x] Brief written in `PROGRESS.md`
- [ ] Build backend analyzer (`analyzer.py` + `app.py`)
- [ ] Build frontend UI (`static/index.html`)
- [ ] Verify end-to-end with real Lead DBA JDs and browser inspection
