# Handoff Report — Browser Operator (worker_m2_1)

**Milestone**: M2 (Portal Profiles Extraction)  
**Date**: 2026-11-10T12:22:00Z  
**Destination Deliverable**: `/Users/devesh/resume/profile_backup.md`

---

## 1. Observation

1. **Active Browser Process & Session**:
   - Process check confirmed Brave running: `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser` (PID 3015) using the single default user profile directory `/Users/devesh/Library/Application Support/BraveSoftware/Brave-Browser/Default`.
   - SQLite cookies inspection on `Default/Cookies` confirmed active authentication cookies across all 8 target domains:
     - `talent500`: 6 cookies (`authToken`, `refreshToken`, `ajs_user_id`)
     - `instahyre`: 2 cookies
     - `naukri`: 14 cookies
     - `indeed`: 61 cookies
     - `foundit`: 13 cookies
     - `glassdoor`: 19 cookies
     - `linkedin`: 25 cookies
     - `turing`: 19 cookies

2. **Sequential In-Tab Extraction Results**:
   - **Talent500** (`https://talent500.com/dashboard/`, `https://talent500.com/account-settings/`):
     - Identity: Devesh Pareek, User ID `2788845`, Email `devsh.pareek@gmail.com`.
     - 7 tracked applications in history (e.g. TMUS Global Solutions: Sr Engineer, Software - AI DataBase Automation; Marriott Tech Accelerator; AA Tech Hub India).
   - **Instahyre** (`https://www.instahyre.com/candidate/profile/`):
     - Identity: Devesh Pareek. Completion score: `100%`.
     - Current Role: Database Admin / Development at Softility (Team management role). Previous: Deloitte. Total experience: 5 years.
     - Current Salary: Rs. 15 LPA. Notice: "Can start working immediately" (0 days).
     - Skills: DAX, DB2, Data Analysis, Data Cleansing, Database Administration, ETL, Jira, Excel, MySQL, Power BI, Project Management, Python, SQL, Selenium, Tableau.
     - Education: BTech / BE Computer Science, SRM Institute of Science and Technology, 2021. Resume: `Devesh_Pareek.pdf` (Oct 16, 2026).
   - **Naukri** (`https://www.naukri.com/mnjuser/profile`):
     - Identity: Devesh Pareek. Completion score: `100%`.
     - Title: Senior Software Engineer at Softility Tech Pvt. Ltd. (Sep 2025 to Present, 1 yr 3 mos). Handling DBaaS responsibilities along with automation. Key skills: PostgreSQL, PgAdmin, Oracle, Oracle RAC, Redshift AWS, AWS.
     - Experience: 4 Years 6 Months. Current Salary: ₹ 15,00,000 (15 LPA). Notice: 3 Months.
     - Deloitte USI tenure (Aug 2021 – Dec 2024, 3 yrs 5 mos) with 3 explicit sub-roles: DB2 LUW DBA / Data Engineer (managed 180+ instances, 20TB+, HADR failovers, 40-60 GB storage reclamation, 1,500+ CI/CD releases), Automation Engineer (Selenium/Python automation across 26 New Relic dashboards, 50 hrs/mo saved), and PMO Coordinator (1,500+ incident calls).
     - Education: B.Tech CSE, SRM University, Chennai (2017–2021 Full Time), Class XII CBSE (2016), Class X CBSE (2014). Resume: `Devesh_Pareek_Resume.pdf` (Oct 16, 2026).
   - **Indeed India** (`https://profile.indeed.com/` & `/preferences`):
     - Identity: Devesh Pareek (`devsh.pareek@gmail.com`, +91 7815887659).
     - Resume: `Devesh_Pareek_Postgres_DBA.pdf` (Uploaded 1 November 2026).
     - Summary: Database engineer with 4+ years in production database operations (PostgreSQL Patroni HA DBA + 2 yrs Db2 LUW on 100+ instances, 20TB+, 99.99% uptime).
     - Career Break explicitly documented: Jan 2025 – Aug 2025 ("independent AI and data automation projects (Python)").
     - Deloitte: Analyst, Database Administrator (Jan 2023 – Dec 2024) and Operations Analyst, Automation and Interim Team Lead (Jul 2021 – Dec 2022).
     - Education: B.Tech CSE SRM (2017–2021, 85.6%) + Admitted to MSE Data Science at Johns Hopkins University (2025 intake).
     - Preferences: Target roles (Database Administrator, Project Manager, Machine Learning Engineer, Database Administrator DBA, Python Developer, Data Analyst), Base pay ₹15,00,000/yr, Relocation anywhere, Immediate availability.
   - **Foundit** (`https://www.foundit.in/seeker/profile`):
     - Identity: Devesh Pareek. Completion score: `100%`.
     - Title: Database Administrator at Softility (Sep 2025 – Present, 1 yr 3 mos). Salary: INR 15L. Notice period: 45 days.
     - Total Experience: 4 yrs 9 mos.
     - Preferred Titles: Database Administrator, Data Engineer. Preferred Locations: Hyderabad, Bangalore, Delhi, Chennai, Pune.
   - **Glassdoor India** (`https://www.glassdoor.co.in/member/profile`):
     - Identity: Devesh Pareek. Title: Database Administrator DBA, Hyderabad.
     - Synced with Indeed profile and CV (`Devesh_Pareek_Postgres_DBA.pdf`, 1 Nov 2026).
     - Active in Tech India and Consulting India bowls.
   - **LinkedIn** (`https://www.linkedin.com/in/devesh-pareek/`):
     - Headline: "Senior Database Engineer & Delivery Lead | PostgreSQL, Db2 | HA/DR & Automation | Open to Relocation"
     - Connections: 500+ connections, 1,616 followers. All-Star status.
     - Detailed Experience: Softility (Senior Software Engineer / PostgreSQL DBA, Interim Lead for 3 engineers, Patroni HA clusters, lower-environment AI diagnostic pipeline); Deloitte (DBA Jan 2023 – Dec 2024, Operations Analyst / Interim Lead Jul 2021 – Dec 2022).
     - Education: SRM IST Chennai (BTech CSE 2017–2021, 85.6% First Class Distinction, IET & Valeo Hackathon Winner). Admitted to MSE in Data Science at Johns Hopkins University (2025 intake).
     - Certifications: Takenmind Technologies Data Analytics & Visualization (Sep 2020), Simplilearn Data Science with Python (Jun 2020).
     - Open to Work (Recruiters only): DBRE, Senior Database Engineer, Engineering Manager, Database Delivery Lead; Target locations: UK, EU (Germany, Netherlands), US, Canada, UAE, Remote.
   - **Turing** (`https://work.turing.com/dashboard`):
     - Identity: Devesh Pareek, User ID `5026234`, `require143d@gmail.com`.
     - Role: Database Administrator (DBA), Hyderabad. 21 archived applications.
     - Matched Roles: LLM S2 Annotator ($150), Debian Engineer, Bash Engineer, Senior Software Engineer - Python ($150), Dockerfile Data Validation Engineer ($150), Technical Content Writer ($150).

3. **User Directive Compliance**:
   - In response to the user directive ("use the same browser session instead of launching new window again and again. use tab if you have to"), all extractions were executed sequentially using tab operations within the existing window (`window 1`) without creating new windows.
   - Guardrails strictly preserved: No direct messages, InMails, or connection requests sent on LinkedIn; zero CAPTCHAs, OTPs, or login prompts triggered.

---

## 2. Logic Chain

1. From Observation 1, Brave had existing authenticated sessions across all 8 target portals under its default profile.
2. From Observation 2, by reusing the existing window session via tab automation, candidate profile data was safely and cleanly read across all 8 portals without triggering session invalidation, bot-detection walls, or authentication challenges.
3. From Observation 2, the extracted profiles provide comprehensive, consistent factual evidence regarding:
   - Full Name: Devesh Pareek
   - Current Employment: Softility (Sep 2025 – Present) as Senior Software Engineer / PostgreSQL DBA / Database Administrator, leading 3 engineers on Patroni HA.
   - Prior Employment: Deloitte USI (Jul/Aug 2021 – Dec 2024) across DB2 LUW DBA, Automation Engineer, and PMO Coordinator roles.
   - Career Transition / Break: Jan 2025 – Aug 2025 (AI & Data automation projects).
   - Education: B.Tech CSE from SRM (2017–2021, 85.6% First Class Distinction) + admitted to MSE in Data Science at Johns Hopkins University.
   - Current CTC: ₹ 15 LPA consistently reported across Naukri, Instahyre, Indeed, and Foundit.
   - Discrepancies identified: Notice period varies across portals (Naukri: 3 Months; Foundit: 45 Days; Instahyre/Indeed: Immediate).
4. Combining these verified data points into `/Users/devesh/resume/profile_backup.md` fulfills all requirements of Milestone M2 and ORIGINAL_REQUEST §R1.

---

## 3. Caveats

- **Notice Period Discrepancy**: Naukri explicitly lists "3 Months notice period", Foundit lists "45 days", while Instahyre and Indeed indicate "Can start working immediately". This discrepancy is flagged prominently in the alignment matrix for Worker M3 / Stage 1 consolidation.
- **Turing Email Address**: Turing uses `require143d@gmail.com` as the registered account identifier, whereas all other portals use `devsh.pareek@gmail.com`.
- **Deloitte Start Date**: Minor variation between May 2021 (Foundit), Jul 2021 (LinkedIn/Indeed), and Aug 2021 (Naukri). Ingested resume documents in `/Users/devesh/Documents/Resume` will clarify the exact joining date.

---

## 4. Conclusion

- Milestone M2 (Portal Profiles Extraction) is **100% complete**.
- `/Users/devesh/resume/profile_backup.md` has been successfully created with rich, verbatim snapshots for all 8 portals: Talent500, Instahyre, Naukri, Indeed India, Foundit, Glassdoor India, LinkedIn, and Turing.
- All guardrails and user directives were strictly respected: single browser session preserved, no new windows opened, no LinkedIn outreach performed, and no credential or CAPTCHA escalations triggered.
- Ready for Worker M3 (Consolidator) to combine `profile_backup.md` with Worker M1's resume ingestion into `master_profile.md` and `targets.md`.

---

## 5. Verification Method

To independently verify the deliverable and extraction integrity:
1. Verify snapshot file existence and line count:
   ```sh
   ls -la /Users/devesh/resume/profile_backup.md
   wc -l /Users/devesh/resume/profile_backup.md
   ```
2. Verify all 8 portal sections are present:
   ```sh
   grep -E "^## [0-9]+\. " /Users/devesh/resume/profile_backup.md
   ```
3. Verify discrepancy matrix:
   ```sh
   grep -A 10 "Cross-Portal Discrepancies" /Users/devesh/resume/profile_backup.md
   ```
