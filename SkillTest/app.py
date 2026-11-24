"""FastAPI server for the Lead DBA Resume & JD Matcher local web app."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from analyzer import (
    analyze_resume_vs_jd,
    extract_text_from_docx_bytes,
    generate_ai_deep_critique,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Lead DBA Resume & JD Matcher")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Paths to Devesh's real resumes on disk so presets load his genuine up-to-date text
RESUME_PATHS: dict[str, Path] = {
    "lead_dba": Path("/Users/devesh/Documents/Antigravity/Automation/job-profiles/Devesh_Pareek_Lead_DBA_Resume.docx"),
    "postgres_dba": Path("/Users/devesh/Documents/Resume/Devesh_Pareek_Resume_Postgres_DBA.docx"),
    "db2_dba": Path("/Users/devesh/Documents/Resume/Devesh_Pareek_Resume_Db2_DBA.docx"),
}

FALLBACK_LEAD_RESUME = """Devesh Pareek
Lead Database Administrator · PostgreSQL & Db2 LUW
Hyderabad, India | +91 7815887659 | devsh.pareek@gmail.com | linkedin.com/in/devesh-pareek

SUMMARY
Database engineer with 4.7 years in production database operations and repeated team-lead responsibility. Currently a PostgreSQL DBA and interim lead for 3 engineers at Softility; previously a Db2 LUW DBA at Deloitte supporting 100+ instances (20TB+) at 99.99% uptime, and interim lead of a 16-member monitoring team. Combines hands-on HA/DR, recovery and performance work with delivery ownership, vendor transitions, mentoring and automation that removes repeat operational work.

LEADERSHIP HIGHLIGHTS
• Interim lead for 3 engineers (Softility) and for a 16-member monitoring team for 6 months (Deloitte).
• Led knowledge transfer (SOPs, documentation) to a client's incoming vendor; trained 3 new team members.
• Trusted SME for incidents by client DBAs with 15+ years of experience, across up to 4 concurrent accounts.
• Automation adopted by a 17-person team: daily monitoring cut from about 8 hours to 30 minutes.

CORE SKILLS
• Databases: PostgreSQL (Patroni, replication, autovacuum, roles/grants), Db2 LUW v11.x (HADR 3/4-node, reorg, runstats), SQL
• Reliability: HA/DR, failover/takeover, backup/restore/PITR, zero-downtime patching, upgrades, server/VM migrations, RCA
• Leadership: team leadership, delivery and process improvement, stakeholder management, vendor transition, mentoring
• Automation & tools: Python (pandas, Selenium), shell, runbooks, CI/CD, Git, Linux, New Relic, ServiceNow, Tableau; AWS (RDS, S3, IAM) in progress

EXPERIENCE
Softility, Hyderabad — Senior Software Engineer (PostgreSQL DBA), Interim Lead | Sep 2025 – Present
• Own production PostgreSQL reliability for a client: Patroni failover/switchover, autovacuum, patching, storage maintenance, backup recoverability, security via roles and grants.
• Interim lead for 3 engineers; work with leadership and team leads on process optimisation and delivery.
• Built an AI-assisted PostgreSQL monitoring tool (lower environment) that reads configs, logs and parameters and recommends fixes without an external monitoring tool.

Deloitte USI, Hyderabad — Analyst, Database Administrator (Db2 LUW) | Jan 2023 – Dec 2024
• Supported 100+ Db2 LUW instances (20TB+) across 4 client accounts, including a global e-commerce platform through Black Friday, July 4th and year-end peaks; 99.99% uptime.
• Built 15+ HADR clusters (3- and 4-node); delivered zero-downtime Linux patching using scripted failover and takeover.
• Resolved lock contention and database-down incidents; performed backup, restore, PITR and server/VM migrations.
• Ran CI/CD releases across DEV, SIT, QA and Prod with tested rollback scripts.
• Trained 3 new team members and led knowledge transfer to the client's incoming vendor.

Deloitte USI, Hyderabad — Operations Analyst, Automation and Interim Team Lead | Jul 2021 – Dec 2022
• Interim lead of a 16-member monitoring team for 6 months.
• Python (Selenium, Outlook) automation cut daily monitoring from about 8 hours to 30 minutes; adopted by the 17-person team.
• Cleared about 1,500 tickets from a 5,000-ticket backlog using pandas and Tableau.
• Built a storage capacity forecast from 3 years of metrics that cut predicted client cost by about 60% and supported a 5-year contract renewal.

Career break — independent AI and data automation projects (Python) | Jan 2025 – Aug 2025

EDUCATION
B.Tech, Computer Science and Engineering — SRM Institute of Science and Technology | 2017 – 2021 | 85.6%
Admitted to MSE, Data Science, Johns Hopkins University (2025 intake); did not enrol because US student visa slots were unavailable in India."""

SAMPLE_JDS: dict[str, dict[str, str]] = {
    "pg_lead": {
        "title": "Lead PostgreSQL DBA (Patroni HA, Cloud & Team Lead)",
        "text": """Role: Lead Database Administrator (PostgreSQL)
Location: Hyderabad / Bengaluru (Hybrid)
Experience: 5+ Years

About the Role:
We are seeking a hands-on Lead PostgreSQL DBA to lead a pod of 3–5 database engineers and own reliability, High Availability, performance tuning, and automation across our production PostgreSQL estate.

Key Responsibilities & Requirements:
• 5+ years of production Database Administration experience with strong expertise in PostgreSQL (v14/15/16) and enterprise RDBMS (such as Db2 LUW or Oracle).
• Proven hands-on experience designing and operating PostgreSQL High Availability clusters using Patroni, streaming & logical replication, PgBouncer connection pooling, and automated failover/switchover.
• Own backup and recovery strategy including Point-in-Time Recovery (PITR), pgBackRest / Barman, disaster recovery drills, and zero-downtime patching/upgrades.
• Deep expertise in SQL query optimization, execution plan analysis (EXPLAIN ANALYZE), indexing strategies, table partitioning, autovacuum tuning, bloat remediation, and resolving lock contention.
• Lead and mentor junior DBAs, act as P1/P2 incident escalation SME, enforce SOPs and operational runbooks, and coordinate database CI/CD schema releases across DEV, QA, and Production.
• Build operational automation using Python and Bash/Shell scripting on Linux (RHEL), and maintain monitoring/observability dashboards in New Relic, Prometheus, or Grafana.
• Working knowledge of AWS database services (RDS for PostgreSQL, Aurora, S3 backup storage, IAM) and capacity planning / cost optimization.""",
    },
    "enterprise_multi_db_lead": {
        "title": "Database Operations Lead — Enterprise RDBMS (Db2 LUW / PostgreSQL)",
        "text": """Role: Database Operations Lead (Db2 LUW & PostgreSQL)
Location: Hyderabad / Pune
Experience: 4–7 Years

Responsibilities:
• Lead a 24x7 production database operations team supporting 100+ multi-terabyte (15TB+) database instances across enterprise and e-commerce accounts at 99.99% SLA uptime.
• Architect and maintain multi-node Db2 LUW v11.x HADR clusters and PostgreSQL Patroni replication topologies.
• Execute zero-downtime Linux OS and database patching via scripted failover/takeover, server/VM database migrations, and Point-in-Time Recovery (PITR).
• Troubleshoot complex database-down incidents, deadlocks, lock contention, transaction log saturation, and query slowdowns using db2diag, reorg, runstats, and execution plans.
• Drive team leadership: onboard and train team members, manage vendor transitions and knowledge transfer (KT), maintain runbooks/SOPs, and handle stakeholder communication.
• Automate repetitive DBA and monitoring tasks with Python and Shell scripts, integrate with ServiceNow and New Relic observability, and deliver storage capacity planning.""",
    },
    "cloud_sre_stretch": {
        "title": "Principal Cloud DBA — Oracle RAC, MySQL & Kubernetes (Stretch/Gap Test)",
        "text": """Role: Principal Cloud Database Engineer (Oracle, MySQL & Kubernetes)
Experience: 8+ Years

Requirements:
• 8+ years administering Oracle 19c RAC, Oracle Data Guard, GoldenGate, and MySQL InnoDB Cluster in high-throughput fintech environments.
• Deploy and manage containerized databases on Kubernetes using CloudNativePG and Helm charts.
• Provision cloud infrastructure on AWS and Azure using Terraform and Ansible Infrastructure-as-Code (IaC).
• Handle PostgreSQL replication, backup/PITR, Python/Bash automation, and production incident management.""",
    },
}


def load_resume_preset(key: str) -> str:
    path = RESUME_PATHS.get(key)
    if path and path.exists():
        try:
            return extract_text_from_docx_bytes(path.read_bytes())
        except Exception:
            pass
    return FALLBACK_LEAD_RESUME


class AnalyzeRequest(BaseModel):
    resume_text: str
    jd_text: str
    include_ai: bool = False


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/presets")
def get_presets() -> JSONResponse:
    return JSONResponse({
        "resumes": {
            "lead_dba": {
                "label": "Devesh — Lead DBA Resume (.docx)",
                "text": load_resume_preset("lead_dba"),
            },
            "postgres_dba": {
                "label": "Devesh — PostgreSQL DBA Resume (.docx)",
                "text": load_resume_preset("postgres_dba"),
            },
            "db2_dba": {
                "label": "Devesh — Db2 LUW DBA Resume (.docx)",
                "text": load_resume_preset("db2_dba"),
            },
        },
        "jds": SAMPLE_JDS,
    })


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)) -> JSONResponse:
    filename = (file.filename or "").lower()
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if filename.endswith(".docx"):
        try:
            text = extract_text_from_docx_bytes(raw)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse .docx file: {exc}") from exc
    elif filename.endswith((".txt", ".md")):
        text = raw.decode("utf-8", errors="replace")
    else:
        raise HTTPException(status_code=400, detail="Please upload a .docx, .txt, or .md resume file (or paste text directly).")

    return JSONResponse({"filename": file.filename, "text": text})


@app.post("/api/analyze")
def analyze_endpoint(req: AnalyzeRequest) -> JSONResponse:
    resume = (req.resume_text or "").strip()
    jd = (req.jd_text or "").strip()

    if len(resume) < 40:
        raise HTTPException(
            status_code=422,
            detail="Please paste a complete resume (at least a few lines of skills and experience) before analyzing.",
        )
    if len(jd) < 40:
        raise HTTPException(
            status_code=422,
            detail="Please paste a complete Job Description (at least a few requirements) before analyzing.",
        )

    result: dict[str, Any] = analyze_resume_vs_jd(resume, jd)
    if req.include_ai:
        result["ai_critique"] = generate_ai_deep_critique(resume, jd, result)
    return JSONResponse(result)
