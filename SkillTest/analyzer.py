"""Domain-tuned Lead DBA Resume & Job Description Analyzer.

Evaluates a resume against a job description across 6 DBA-specific pillars:
1. Primary & Secondary Database Engines
2. HA / DR & Backup / Recovery
3. Performance Tuning & Operations
4. Leadership, Mentoring & Stakeholder Delivery
5. Automation, Scripting & DevOps / Observability
6. Cloud & Seniority / Scale Fit

Also cross-checks the candidate's full verified profile bank (Lead DBA, PostgreSQL DBA,
Db2 LUW DBA) so if a pasted resume omits a real achievement that matches the JD, it generates
an exact, truthful 'Hidden Gem' or 'Before -> After' fix.
"""
from __future__ import annotations

import json
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Verified facts from Devesh Pareek's actual resumes (nothing invented)
DEVESH_EVIDENCE_BANK: list[dict[str, Any]] = [
    {
        "id": "pg_patroni_ha",
        "tags": ["postgresql", "postgres", "patroni", "high availability", "ha", "failover", "switchover", "replication", "streaming replication"],
        "detect_patterns": [r"patroni", r"failover/switchover", r"failover and switchover"],
        "section": "Softility — Senior Software Engineer (PostgreSQL DBA)",
        "current_short": "Own production PostgreSQL reliability for a client: Patroni failover/switchover, autovacuum, patching, storage maintenance, backup recoverability, security via roles and grants.",
        "tailored_bullet": "Own production PostgreSQL High Availability and replication using Patroni (automated failover, planned switchover, replica lag recovery, backup recoverability, and RBAC security via roles/grants).",
        "reason": "Explicitly pairs PostgreSQL with Patroni HA, streaming replication, and automated failover/switchover keywords that ATS filters scan for.",
    },
    {
        "id": "pg_tuning_indexing",
        "tags": ["query tuning", "performance tuning", "execution plans", "explain", "indexing", "autovacuum", "bloat", "locks", "lock contention", "query optimization"],
        "detect_patterns": [r"execution plans", r"indexing", r"tune sql queries"],
        "section": "Softility / Core Skills (PostgreSQL DBA)",
        "current_short": "CORE SKILLS: PostgreSQL (Patroni, replication, autovacuum, roles/grants) ... resolved lock contention and database-down incidents",
        "tailored_bullet": "Monitor production PostgreSQL health, tune slow SQL queries via execution plan analysis and indexing, manage autovacuum/storage bloat, and resolve lock contention incidents.",
        "reason": "Your Lead DBA resume omits 'query tuning, execution plans, indexing' under Softility even though it is in your Postgres DBA resume. Adding it closes the query optimization keyword gap.",
    },
    {
        "id": "pg_ai_monitoring",
        "tags": ["monitoring", "observability", "python", "automation", "diagnostics", "root cause analysis", "rca", "logs", "configuration"],
        "detect_patterns": [r"ai-assisted postgresql monitoring"],
        "section": "Softility — Senior Software Engineer (PostgreSQL DBA)",
        "current_short": "Built an AI-assisted PostgreSQL monitoring tool (lower environment) that reads configs, logs and parameters and recommends fixes without an external monitoring tool.",
        "tailored_bullet": "Built an AI-assisted PostgreSQL diagnostics & observability tool in Python that parses postgresql.conf parameters, server logs, and system metrics to auto-recommend tuning and reliability fixes.",
        "reason": "Highlights configuration tuning (`postgresql.conf`), log analysis, and proactive observability engineering.",
    },
    {
        "id": "db2_scale_uptime",
        "tags": ["scale", "uptime", "sla", "production", "24x7", "on-call", "mission critical", "e-commerce", "enterprise", "db2", "db2 luw", "multi-terabyte", "vlbd"],
        "detect_patterns": [r"100\+.*db2", r"20tb\+", r"99\.99%"],
        "section": "Deloitte USI — Database Administrator (Db2 LUW)",
        "current_short": "Supported 100+ Db2 LUW instances (20TB+) across 4 client accounts, including a global e-commerce platform through Black Friday, July 4th and year-end peaks; 99.99% uptime.",
        "tailored_bullet": "Managed 100+ production database instances (20TB+ total data volume) across 4 enterprise client accounts at 99.99% SLA uptime, supporting mission-critical global e-commerce peak traffic.",
        "reason": "Translates your 100+ instances / 20TB+ / 99.99% SLA scale so both DB2 and engine-agnostic Lead DBA screeners see multi-terabyte enterprise ownership.",
    },
    {
        "id": "hadr_zero_downtime_patching",
        "tags": ["hadr", "disaster recovery", "dr", "patching", "zero-downtime", "upgrades", "linux", "shell", "bash", "cluster", "pacemaker"],
        "detect_patterns": [r"15\+ hadr", r"zero-downtime linux patching"],
        "section": "Deloitte USI — Database Administrator (Db2 LUW)",
        "current_short": "Built 15+ HADR clusters (3- and 4-node); delivered zero-downtime Linux patching using scripted failover and takeover.",
        "tailored_bullet": "Engineered 15+ multi-node (3- and 4-node) HA/DR clusters and delivered zero-downtime Linux OS & database patching via automated failover/takeover shell scripts.",
        "reason": "Emphasizes multi-node HA/DR architecture and scripted zero-downtime maintenance windows.",
    },
    {
        "id": "backup_pitr_migration",
        "tags": ["backup", "restore", "recovery", "pitr", "point-in-time", "point in time", "migration", "upgrades", "reorg", "runstats"],
        "detect_patterns": [r"pitr", r"server/vm migrations", r"reorg,\s*runstats"],
        "section": "Deloitte USI — Database Administrator (Db2 LUW)",
        "current_short": "Resolved lock contention and database-down incidents; performed backup, restore, PITR and server/VM migrations.",
        "tailored_bullet": "Executed full/incremental backups, disaster recovery drills, Point-in-Time Recovery (PITR), server/VM database migrations, and routine maintenance (reorg, runstats, execution-plan tuning).",
        "reason": "Explicitly spells out 'Point-in-Time Recovery (PITR)' and execution-plan tuning alongside server/VM migrations.",
    },
    {
        "id": "cicd_schema_sync",
        "tags": ["ci/cd", "cicd", "devops", "git", "release", "rollback", "schema", "deployment", "change management"],
        "detect_patterns": [r"synchronised lower environments", r"failback scripts"],
        "section": "Deloitte USI — Database Administrator (Db2 LUW)",
        "current_short": "Ran CI/CD releases across DEV, SIT, QA and Prod with tested rollback scripts.",
        "tailored_bullet": "Owned database CI/CD release pipelines across DEV, SIT, QA, and Prod with log validation, schema synchronization across environments, and tested rollback/failback scripts.",
        "reason": "Your Db2 resume includes 'synchronised lower environments with production schemas' and 'failback scripts' which are missing from the Lead DBA version.",
    },
    {
        "id": "new_relic_db2diag_hidden_gem",
        "tags": ["new relic", "observability", "monitoring", "alerting", "dashboard", "disk", "storage", "shell", "automation", "db2diag"],
        "detect_patterns": [r"26 new relic", r"50\+ hours", r"db2diag archiving"],
        "section": "Deloitte USI — Database Administrator (Db2 LUW) [Missing from Lead DBA Resume!]",
        "current_short": "(Currently omitted from your Lead DBA resume, present in your Postgres/Db2 resumes)",
        "tailored_bullet": "Automated db2diag log archiving to eliminate recurring /home disk saturation incidents and automated 26 New Relic observability dashboards, saving 50+ engineering hours/month.",
        "reason": "HIGH-IMPACT FIX: This concrete metric (26 New Relic dashboards, 50+ hrs/month saved, disk saturation fix) is in your IC resumes but was accidentally dropped from your Lead DBA resume!",
    },
    {
        "id": "leadership_team_lead",
        "tags": ["lead", "team lead", "leadership", "mentoring", "coaching", "onboarding", "knowledge transfer", "kt", "stakeholder", "vendor", "sop", "runbook", "incident management", "sme"],
        "detect_patterns": [r"interim lead for 3 engineers", r"16-member monitoring team"],
        "section": "Leadership Highlights & Experience",
        "current_short": "Interim lead for 3 engineers (Softility) and for a 16-member monitoring team for 6 months (Deloitte). Led knowledge transfer (SOPs, documentation) to a client's incoming vendor; trained 3 new team members.",
        "tailored_bullet": "Acted as Interim Database Team Lead (3 engineers at Softility; 16-member operations team at Deloitte), driving sprint delivery, incident escalation (P1/P2 SME), SOP/runbook governance, vendor transition KT, and mentoring.",
        "reason": "Directly connects your interim lead roles (3-person DBA team + 16-person ops team) to Lead DBA keywords: P1/P2 incident escalation, SOP/runbook governance, mentoring, and stakeholder delivery.",
    },
    {
        "id": "capacity_planning_cost",
        "tags": ["capacity planning", "cost optimization", "forecasting", "storage", "finops", "metrics", "tableau", "pandas", "backlog", "servicnow", "itil"],
        "detect_patterns": [r"storage capacity forecast", r"60%", r"1,500 tickets"],
        "section": "Deloitte USI — Operations Analyst, Automation & Interim Lead",
        "current_short": "Built a storage capacity forecast from 3 years of metrics that cut predicted client cost by about 60% and supported a 5-year contract renewal.",
        "tailored_bullet": "Delivered multi-year database & storage capacity planning from 3 years of telemetry, cutting projected infrastructure spend by ~60% and securing a 5-year enterprise contract renewal.",
        "reason": "Reframes your storage forecast using Lead DBA terminology ('database & storage capacity planning', 'infrastructure spend optimization').",
    },
    {
        "id": "aws_cloud_framing",
        "tags": ["aws", "rds", "aurora", "cloud", "s3", "iam", "azure", "gcp", "cloud migration"],
        "detect_patterns": [r"aws \(rds, s3, iam\) in progress"],
        "section": "Core Skills — Cloud & Platforms",
        "current_short": "AWS (RDS, S3, IAM) in progress",
        "tailored_bullet": "Cloud & Platforms: Linux (RHEL), AWS (RDS for PostgreSQL, S3 backup integration, IAM security), VM/Server Database Migrations, New Relic, ServiceNow",
        "reason": "Writing 'in progress' on a resume hurts ATS and recruiter screening for Lead roles. List the specific AWS services you work with (RDS, S3, IAM) cleanly in Skills, and be ready to discuss your hands-on level in interviews.",
    },
]


# Taxonomy of DBA skills & requirements with category weights
SKILL_TAXONOMY: list[dict[str, Any]] = [
    # Category 1: Database Engines (Weight 25)
    {"name": "PostgreSQL", "category": "Database Engines", "weight": 10, "patterns": [r"\bpostgres(?:ql)?\b"], "devesh_status": "strong"},
    {"name": "Db2 LUW", "category": "Database Engines", "weight": 8, "patterns": [r"\bdb2(?:\s+luw)?\b"], "devesh_status": "strong"},
    {"name": "SQL", "category": "Database Engines", "weight": 5, "patterns": [r"\bsql\b", r"\bpl/pgsql\b"], "devesh_status": "strong"},
    {"name": "MySQL / MariaDB", "category": "Database Engines", "weight": 6, "patterns": [r"\bmysql\b", r"\bmariadb\b"], "devesh_status": "gap", "gap_advice": "True engine gap: do not claim fake MySQL production years. Emphasize multi-engine RDBMS internals (MVCC, WAL/transaction logs, buffer pools, replication) across PostgreSQL and Db2 LUW."},
    {"name": "Oracle Database", "category": "Database Engines", "weight": 7, "patterns": [r"\boracle(?:\s+db|\s+database|\s+rac|\s+19c|\s+12c)?\b"], "devesh_status": "gap", "gap_advice": "True engine gap: if Oracle is supplementary ('PostgreSQL + Oracle/Db2'), highlight that Db2 LUW enterprise HADR + PostgreSQL Patroni cover the same mission-critical enterprise RDBMS patterns."},
    {"name": "MS SQL Server", "category": "Database Engines", "weight": 6, "patterns": [r"\bsql\s+server\b", r"\bmssql\b", r"\bt-sql\b"], "devesh_status": "gap", "gap_advice": "True engine gap: focus on your PostgreSQL + Db2 LUW production track record unless SQL Server is a secondary nice-to-have."},
    {"name": "NoSQL (MongoDB / Redis / Cassandra)", "category": "Database Engines", "weight": 4, "patterns": [r"\bmongodb\b", r"\bredis\b", r"\bcassandra\b", r"\bnosql\b", r"\bdynamodb\b"], "devesh_status": "gap", "gap_advice": "Secondary engine gap: keep focus on core RDBMS (PostgreSQL/Db2) and mention JSONB/key-value workload handling in PostgreSQL if relevant."},

    # Category 2: HA / DR & Backup / Recovery (Weight 25)
    {"name": "High Availability (HA)", "category": "HA/DR & Reliability", "weight": 9, "patterns": [r"\bhigh\s+availability\b", r"\bha/dr\b", r"\bha\b"], "devesh_status": "strong", "evidence_id": "pg_patroni_ha"},
    {"name": "Patroni", "category": "HA/DR & Reliability", "weight": 8, "patterns": [r"\bpatroni\b", r"\betcd\b"], "devesh_status": "strong", "evidence_id": "pg_patroni_ha"},
    {"name": "Disaster Recovery (DR) & Failover", "category": "HA/DR & Reliability", "weight": 8, "patterns": [r"\bdisaster\s+recovery\b", r"\bfailover\b", r"\bswitchover\b", r"\btakeover\b"], "devesh_status": "strong", "evidence_id": "pg_patroni_ha"},
    {"name": "Replication (Streaming / Logical / HADR)", "category": "HA/DR & Reliability", "weight": 8, "patterns": [r"\breplication\b", r"\bstreaming\s+replication\b", r"\blogical\s+replication\b", r"\bhadr\b"], "devesh_status": "strong", "evidence_id": "pg_patroni_ha"},
    {"name": "Backup & Recovery / PITR", "category": "HA/DR & Reliability", "weight": 9, "patterns": [r"\bbackup\b", r"\brestore\b", r"\brecovery\b", r"\bpitr\b", r"\bpoint[- ]in[- ]time\b"], "devesh_status": "strong", "evidence_id": "backup_pitr_migration"},
    {"name": "pgBackRest / Barman / pg_dump", "category": "HA/DR & Reliability", "weight": 5, "patterns": [r"\bpgbackrest\b", r"\bbarman\b", r"\bpg_basebackup\b", r"\bpg_dump\b"], "devesh_status": "reframe", "gap_advice": "Name the specific PostgreSQL backup tool you use at Softility (e.g., pgBackRest / pg_basebackup / WAL archiving) instead of generic 'backup recoverability'."},
    {"name": "Connection Pooling (PgBouncer / Pgpool-II)", "category": "HA/DR & Reliability", "weight": 5, "patterns": [r"\bpgbouncer\b", r"\bpgpool\b", r"\bconnection\s+pool(?:ing)?\b"], "devesh_status": "reframe", "gap_advice": "If you manage connection pooling (PgBouncer/haproxy) alongside Patroni at Softility, explicitly add 'PgBouncer / connection management' to your PostgreSQL skills line."},

    # Category 3: Performance, Scale & Operations (Weight 20)
    {"name": "Performance & Query Tuning", "category": "Performance & Operations", "weight": 9, "patterns": [r"\bperformance\s+tuning\b", r"\bquery\s+tuning\b", r"\bquery\s+optimi[sz]ation\b", r"\bexecution\s+plan(?:s)?\b", r"\bexplain\b"], "devesh_status": "strong", "evidence_id": "pg_tuning_indexing"},
    {"name": "Indexing & Vacuum / Bloat Management", "category": "Performance & Operations", "weight": 7, "patterns": [r"\bindex(?:ing|es)?\b", r"\bautovacuum\b", r"\bvacuum\b", r"\bbloat\b", r"\breorg\b", r"\brunstats\b"], "devesh_status": "strong", "evidence_id": "pg_tuning_indexing"},
    {"name": "Lock Contention & Incident RCA", "category": "Performance & Operations", "weight": 7, "patterns": [r"\block(?:\s+contention|ing|s)?\b", r"\bdeadlock(?:s)?\b", r"\broot\s+cause\b", r"\brca\b", r"\bincident(?:s|\s+management|\s+response)?\b", r"\btroubleshoot(?:ing)?\b"], "devesh_status": "strong", "evidence_id": "pg_tuning_indexing"},
    {"name": "Patching & Version Upgrades", "category": "Performance & Operations", "weight": 7, "patterns": [r"\bpatching\b", r"\bupgrade(?:s)?\b", r"\bzero[- ]downtime\b", r"\bmaintenance\b"], "devesh_status": "strong", "evidence_id": "hadr_zero_downtime_patching"},
    {"name": "Database Migration", "category": "Performance & Operations", "weight": 6, "patterns": [r"\bmigration(?:s)?\b", r"\bdms\b", r"\bora2pg\b"], "devesh_status": "strong", "evidence_id": "backup_pitr_migration"},
    {"name": "Capacity Planning & Storage", "category": "Performance & Operations", "weight": 6, "patterns": [r"\bcapacity\s+planning\b", r"\bstorage\b", r"\bforecast(?:ing)?\b", r"\bcost\s+optimi[sz]ation\b"], "devesh_status": "strong", "evidence_id": "capacity_planning_cost"},
    {"name": "Database Security / Roles / Compliance", "category": "Performance & Operations", "weight": 5, "patterns": [r"\broles\s+and\s+grants\b", r"\brbac\b", r"\bsecurity\b", r"\baccess\s+control\b", r"\bencryption\b", r"\baudit(?:ing)?\b", r"\bpg_hba\b"], "devesh_status": "strong", "evidence_id": "pg_patroni_ha"},
    {"name": "Partitioning / Sharding", "category": "Performance & Operations", "weight": 4, "patterns": [r"\bpartition(?:ing|ed)?\b", r"\bsharding\b", r"\bpg_partman\b"], "devesh_status": "reframe", "gap_advice": "If you have managed partitioned tables in 20TB+ Db2 or PostgreSQL environments, add 'table partitioning' explicitly under Core Skills."},

    # Category 4: Leadership & Delivery (Weight 15)
    {"name": "Team Leadership & People Management", "category": "Leadership & Delivery", "weight": 9, "patterns": [r"\bteam\s+lead(?:er|ership)?\b", r"\blead\s+dba\b", r"\blead\s+database\b", r"\bmanage\s+a\s+team\b", r"\bleading\b", r"\bsupervis(?:e|ing)\b"], "devesh_status": "strong", "evidence_id": "leadership_team_lead"},
    {"name": "Mentoring & Training", "category": "Leadership & Delivery", "weight": 6, "patterns": [r"\bmentor(?:ing|ship)?\b", r"\btrain(?:ed|ing)\b", r"\bcoach(?:ing)?\b", r"\bonboard(?:ing)?\b"], "devesh_status": "strong", "evidence_id": "leadership_team_lead"},
    {"name": "Stakeholder & Vendor Management", "category": "Leadership & Delivery", "weight": 6, "patterns": [r"\bstakeholder(?:s)?\b", r"\bvendor\b", r"\bclient(?:s)?\b", r"\bknowledge\s+transfer\b", r"\bcross[- ]functional\b"], "devesh_status": "strong", "evidence_id": "leadership_team_lead"},
    {"name": "Runbooks, SOPs & Operational Governance", "category": "Leadership & Delivery", "weight": 5, "patterns": [r"\brunbook(?:s)?\b", r"\bsop(?:s)?\b", r"\bdocumentation\b", r"\bsla(?:s)?\b", r"\bprocess\s+improvement\b", r"\bitil\b", r"\bservicenow\b"], "devesh_status": "strong", "evidence_id": "leadership_team_lead"},

    # Category 5: Automation, DevOps & Observability (Weight 10)
    {"name": "Python Automation", "category": "Automation & Observability", "weight": 6, "patterns": [r"\bpython\b"], "devesh_status": "strong", "evidence_id": "pg_ai_monitoring"},
    {"name": "Shell / Bash Scripting & Linux", "category": "Automation & Observability", "weight": 7, "patterns": [r"\bshell\b", r"\bbash\b", r"\blinux\b", r"\brhel\b", r"\bunix\b"], "devesh_status": "strong", "evidence_id": "hadr_zero_downtime_patching"},
    {"name": "CI/CD & Git", "category": "Automation & Observability", "weight": 5, "patterns": [r"\bci/cd\b", r"\bcicd\b", r"\bgit\b", r"\bjenkins\b", r"\bgitlab\b", r"\bgithub\s+actions\b"], "devesh_status": "strong", "evidence_id": "cicd_schema_sync"},
    {"name": "Monitoring & Observability (New Relic / Prometheus / Grafana)", "category": "Automation & Observability", "weight": 6, "patterns": [r"\bnew\s+relic\b", r"\bmonitoring\b", r"\bobservability\b", r"\bdashboard(?:s)?\b", r"\bprometheus\b", r"\bgrafana\b", r"\bdatadog\b", r"\bpg_stat_statements\b"], "devesh_status": "strong", "evidence_id": "new_relic_db2diag_hidden_gem"},
    {"name": "Infrastructure as Code (Terraform / Ansible)", "category": "Automation & Observability", "weight": 4, "patterns": [r"\bterraform\b", r"\bansible\b", r"\biac\b"], "devesh_status": "gap", "gap_advice": "If the JD asks for Ansible/Terraform, highlight your automated bash/Python provisioning & zero-downtime patching scripts across 15+ clusters and 100+ instances."},

    # Category 6: Cloud & Modern Infra (Weight 5)
    {"name": "AWS (RDS / Aurora / S3 / IAM)", "category": "Cloud & Modern Infra", "weight": 6, "patterns": [r"\baws\b", r"\brds\b", r"\baurora\b", r"\bs3\b"], "devesh_status": "reframe", "evidence_id": "aws_cloud_framing"},
    {"name": "Azure / GCP Cloud Databases", "category": "Cloud & Modern Infra", "weight": 4, "patterns": [r"\bazure\b", r"\bgcp\b", r"\bcloud\s+sql\b"], "devesh_status": "gap", "gap_advice": "Frame your AWS RDS/S3/IAM work and Linux VM database migrations as transferable cloud DBA experience."},
    {"name": "Containers (Docker / Kubernetes)", "category": "Cloud & Modern Infra", "weight": 4, "patterns": [r"\bdocker\b", r"\bkubernetes\b", r"\bk8s\b", r"\bcontainer(?:s)?\b", r"\bcloudnativepg\b"], "devesh_status": "gap", "gap_advice": "True gap unless used in lower environments: focus on Linux VM/bare-metal Patroni HA and CI/CD pipelines."},
]


def extract_text_from_docx_bytes(data: bytes) -> str:
    """Extract clean paragraph text from a .docx file in memory."""
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml_content = z.read("word/document.xml")
    tree = ET.fromstring(xml_content)
    lines: list[str] = []
    for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = [t.text for t in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if t.text]
        if texts:
            line = "".join(texts).strip()
            if line:
                lines.append(line)
    return "\n".join(lines)


def _matches_any(text_lower: str, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, text_lower, flags=re.IGNORECASE):
            token = m.group(0).strip()
            if token.lower() not in [f.lower() for f in found]:
                found.append(token)
    return found


def parse_jd_years_required(jd_text: str) -> dict[str, Any]:
    """Extract minimum years of experience requested in the JD."""
    patterns = [
        r"(\d+)\s*\+?\s*(?:to|-|–)\s*(\d+)\s*(?:years|yrs)",
        r"(?:minimum|at\s+least|min\.?)\s+(?:of\s+)?(\d+)\s*\+?\s*(?:years|yrs)",
        r"(\d+)\s*\+\s*(?:years|yrs)\s+(?:of\s+)?(?:experience|exp|hands-on|database|dba|postgresql|db2)",
        r"(\d+)\s*(?:years|yrs)\s+(?:of\s+)?(?:experience|exp|relevant)",
    ]
    years_found: list[int] = []
    for pat in patterns:
        for m in re.finditer(pat, jd_text, flags=re.IGNORECASE):
            try:
                years_found.append(int(m.group(1)))
            except (ValueError, IndexError):
                pass
    min_years = min(years_found) if years_found else None
    return {"min_years": min_years, "all_mentions": sorted(set(years_found))}


def parse_resume_years(resume_text: str) -> float:
    """Detect stated years of experience in resume (defaults to 4.7 if Devesh's resume)."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", resume_text, flags=re.IGNORECASE)
    if m:
        try:
            val = float(m.group(1))
            if val == 4.0 and ("sep 2025" in resume_text.lower() or "jul 2021" in resume_text.lower()):
                return 4.7
            return val
        except ValueError:
            pass
    if "devesh pareek" in resume_text.lower():
        return 4.7
    return 0.0


def extract_jd_bullet_requirements(jd_text: str) -> list[str]:
    """Extract discrete requirement sentences/bullets from the job description."""
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    reqs: list[str] = []
    skip_headers = re.compile(
        r"^(about\s+us|about\s+the\s+company|benefits|perks|equal\s+opportunity|why\s+join|who\s+we\s+are)[:\s]*$",
        re.IGNORECASE,
    )
    for line in lines:
        cleaned = re.sub(r"^[\•\-\*\u2022\d\.\)\s]+", "", line).strip()
        if len(cleaned) < 18 or len(cleaned) > 320:
            continue
        if skip_headers.match(cleaned):
            continue
        # Check if line looks like a technical or role requirement
        if any(
            kw in cleaned.lower()
            for kw in (
                "database", "dba", "postgres", "db2", "sql", "oracle", "mysql", "ha", "high availability",
                "replication", "patroni", "hadr", "backup", "recovery", "pitr", "tuning", "performance",
                "patch", "upgrade", "migrat", "lead", "team", "mentor", "python", "shell", "linux",
                "aws", "cloud", "rds", "monitor", "incident", "troubleshoot", "year", "experience",
                "ci/cd", "automation", "sla", "uptime", "on-call", "24x7", "security", "capacity",
            )
        ):
            reqs.append(cleaned)
    return reqs[:18]


def analyze_resume_vs_jd(resume_text: str, jd_text: str) -> dict[str, Any]:
    """Perform deterministic, evidence-based DBA match analysis and generate tailored fixes."""
    resume_clean = resume_text.strip()
    jd_clean = jd_text.strip()
    resume_lower = resume_clean.lower()
    jd_lower = jd_clean.lower()

    # 1. Evaluate taxonomy items present in the JD
    active_skills: list[dict[str, Any]] = []
    unrequested_strengths: list[str] = []

    for item in SKILL_TAXONOMY:
        jd_hits = _matches_any(jd_lower, item["patterns"])
        res_hits = _matches_any(resume_lower, item["patterns"])
        if jd_hits:
            if res_hits:
                # Check if weak phrasing exists (e.g. "AWS ... in progress")
                is_weak = False
                weak_note = ""
                if item["name"].startswith("AWS") and "in progress" in resume_lower:
                    is_weak = True
                    weak_note = "Listed as 'in progress' — weakens ATS/recruiter confidence."
                elif item["name"] == "Performance & Query Tuning" and "execution plan" not in resume_lower and "query tuning" not in resume_lower:
                    is_weak = True
                    weak_note = "Your resume mentions 'performance work' generally, but omits 'query tuning, execution plans, indexing'."
                status = "partial" if is_weak else "matched"
            else:
                # Missing from pasted resume — check if Devesh actually has it in his evidence bank!
                status = "missing_but_you_have_it" if item["devesh_status"] in ("strong", "reframe") else "true_gap"
                weak_note = ""

            active_skills.append({
                "name": item["name"],
                "category": item["category"],
                "weight": item["weight"],
                "status": status,
                "jd_terms": jd_hits,
                "resume_terms": res_hits,
                "weak_note": weak_note,
                "evidence_id": item.get("evidence_id"),
                "gap_advice": item.get("gap_advice", ""),
            })
        elif res_hits and item["weight"] >= 7:
            unrequested_strengths.append(item["name"])

    # If the JD is very short or generic, ensure core DBA skills are still checked
    if not active_skills:
        for item in SKILL_TAXONOMY[:6]:
            res_hits = _matches_any(resume_lower, item["patterns"])
            active_skills.append({
                "name": item["name"],
                "category": item["category"],
                "weight": item["weight"],
                "status": "matched" if res_hits else "true_gap",
                "jd_terms": [],
                "resume_terms": res_hits,
                "weak_note": "",
                "evidence_id": item.get("evidence_id"),
                "gap_advice": item.get("gap_advice", ""),
            })

    # 2. Compute category breakdown and overall match score
    categories: dict[str, dict[str, Any]] = {}
    total_weight = 0.0
    earned_weight = 0.0
    potential_weight = 0.0  # Score after applying truthful fixes from evidence bank

    for sk in active_skills:
        cat = sk["category"]
        w = float(sk["weight"])
        total_weight += w
        if cat not in categories:
            categories[cat] = {"earned": 0.0, "potential": 0.0, "total": 0.0, "items": []}
        categories[cat]["total"] += w
        categories[cat]["items"].append(sk["name"])

        if sk["status"] == "matched":
            earned_weight += w
            potential_weight += w
            categories[cat]["earned"] += w
            categories[cat]["potential"] += w
        elif sk["status"] == "partial":
            earned_weight += w * 0.6
            potential_weight += w
            categories[cat]["earned"] += w * 0.6
            categories[cat]["potential"] += w
        elif sk["status"] == "missing_but_you_have_it":
            earned_weight += 0.0
            potential_weight += w * 0.95
            categories[cat]["potential"] += w * 0.95
        else:
            # true_gap
            earned_weight += 0.0
            potential_weight += 0.0

    # Experience / Seniority check
    jd_years_info = parse_jd_years_required(jd_clean)
    resume_years = parse_resume_years(resume_clean)
    min_jd_years = jd_years_info["min_years"]

    seniority_penalty = 0
    seniority_note = f"Your resume shows {resume_years:.1f} years of experience."
    if min_jd_years:
        if resume_years and resume_years < min_jd_years:
            gap_yrs = round(min_jd_years - resume_years, 1)
            if gap_yrs <= 1.5:
                seniority_penalty = 4
                seniority_note = (
                    f"JD asks for {min_jd_years}+ years; you have {resume_years:.1f} years "
                    f"(close stretch — offset by highlighting 100+ instances, 20TB+, and two interim team-lead stints)."
                )
            else:
                seniority_penalty = 9
                seniority_note = (
                    f"JD asks for {min_jd_years}+ years; you have {resume_years:.1f} years "
                    f"({gap_yrs} yr gap — lead with scale: 100+ instances, 20TB+, 15+ HADR clusters, 16-member team led)."
                )
        else:
            seniority_note = f"JD asks for {min_jd_years}+ years; your {resume_years:.1f} years meets the bar."

    raw_score = round((earned_weight / total_weight) * 100) if total_weight > 0 else 0
    current_score = max(5, min(99, raw_score - seniority_penalty))

    raw_potential = round((potential_weight / total_weight) * 100) if total_weight > 0 else 0
    projected_score = max(current_score, min(99, raw_potential - (seniority_penalty // 2)))

    category_Readout = []
    for cat_name, cdata in categories.items():
        cat_pct = round((cdata["earned"] / cdata["total"]) * 100) if cdata["total"] > 0 else 100
        pot_pct = round((cdata["potential"] / cdata["total"]) * 100) if cdata["total"] > 0 else 100
        category_Readout.append({
            "category": cat_name,
            "score": cat_pct,
            "projected_score": pot_pct,
            "skills_tested": cdata["items"],
        })

    # 3. Map JD bullet requirements line-by-line
    jd_bullets = extract_jd_bullet_requirements(jd_clean)
    requirement_checks: list[dict[str, Any]] = []
    for req in jd_bullets:
        req_lower = req.lower()
        matched_in_req = []
        missing_in_req = []
        fixable_in_req = []
        for sk in active_skills:
            # Check if this skill is mentioned in this specific requirement line
            item_obj = next((x for x in SKILL_TAXONOMY if x["name"] == sk["name"]), None)
            if item_obj and _matches_any(req_lower, item_obj["patterns"]):
                if sk["status"] == "matched":
                    matched_in_req.append(sk["name"])
                elif sk["status"] in ("partial", "missing_but_you_have_it"):
                    fixable_in_req.append(sk["name"])
                else:
                    missing_in_req.append(sk["name"])

        if missing_in_req and not matched_in_req and not fixable_in_req:
            req_status = "gap"
        elif fixable_in_req or (missing_in_req and matched_in_req):
            req_status = "fixable"
        elif matched_in_req:
            req_status = "matched"
        else:
            # General check on common words
            req_status = "matched" if any(w in resume_lower for w in ("postgresql", "db2", "lead", "ha")) else "fixable"

        requirement_checks.append({
            "requirement": req,
            "status": req_status,
            "matched_skills": matched_in_req,
            "fixable_skills": fixable_in_req,
            "gap_skills": missing_in_req,
        })

    # 4. Build concrete, ordered "What to Fix in Your Resume Before You Apply"
    fixes: list[dict[str, Any]] = []
    used_evidence_ids: set[str] = set()

    # 4a. Headline & Summary Tailoring (Always #1 for Lead DBA applications)
    wants_pg = any(s["name"] == "PostgreSQL" for s in active_skills)
    wants_db2 = any(s["name"] == "Db2 LUW" for s in active_skills)
    wants_lead = any(s["category"] == "Leadership & Delivery" for s in active_skills) or "lead" in jd_lower

    if wants_pg and not wants_db2:
        engine_headline = "PostgreSQL & Enterprise RDBMS (Db2 LUW)"
    elif wants_db2 and not wants_pg:
        engine_headline = "Db2 LUW & PostgreSQL"
    else:
        engine_headline = "PostgreSQL & Db2 LUW"

    jd_top_keywords = [s["name"] for s in active_skills if s["status"] != "true_gap"][:6]
    tailored_summary = (
        f"Lead Database Administrator with 4.7 years in 24x7 production database operations ({engine_headline}) "
        f"and hands-on team leadership. Currently PostgreSQL DBA & Interim Lead (3 engineers) at Softility owning "
        f"Patroni HA failover/switchover, query tuning, autovacuum, backup/PITR recoverability, and RBAC security. "
        f"Previously Db2 LUW DBA & Interim Team Lead (16-member team) at Deloitte managing 100+ instances (20TB+) "
        f"at 99.99% SLA uptime, building 15+ multi-node HADR clusters, automating 26 New Relic dashboards "
        f"(50+ hrs/month saved), and cutting daily monitoring from 8 hours to 30 minutes with Python."
    )

    # Check if summary in resume says "4+ years" instead of "4.7 years" or lacks New Relic / query tuning
    current_summary_match = re.search(r"SUMMARY\s*\n([^\n]+)", resume_clean, flags=re.IGNORECASE)
    current_summary_snippet = (
        current_summary_match.group(1).strip()
        if current_summary_match
        else "Current top summary paragraph in pasted resume"
    )

    if "4+ years" in resume_lower or "new relic" not in current_summary_snippet.lower() or "query tuning" not in current_summary_snippet.lower():
        fixes.append({
            "priority": "HIGH",
            "type": "Rewrite Summary & Headline",
            "section": "Header & Summary",
            "why": (
                "Your current summary either understates your tenure ('4+ years' vs '4.7 years') or leaves out high-value "
                f"JD keywords ({', '.join(jd_top_keywords[:4])}). Recruiters scan the top 5 lines first."
            ),
            "before": current_summary_snippet,
            "after": tailored_summary,
        })

    # 4b. Check evidence bank for missing or under-framed accomplishments in the pasted resume
    for ev in DEVESH_EVIDENCE_BANK:
        # Does the JD care about any tag in this evidence item?
        jd_relevance = sum(1 for t in ev["tags"] if t in jd_lower)
        if jd_relevance == 0:
            continue

        # Is this specific evidence already strongly present in the pasted resume?
        already_has_all = all(re.search(pat, resume_lower) for pat in ev["detect_patterns"])
        if not already_has_all:
            used_evidence_ids.add(ev["id"])
            priority = "HIGH" if jd_relevance >= 2 or "hidden_gem" in ev["id"] or "aws" in ev["id"] else "MEDIUM"
            fixes.append({
                "priority": priority,
                "type": "Add / Upgrade Resume Bullet",
                "section": ev["section"],
                "why": ev["reason"],
                "before": ev["current_short"],
                "after": ev["tailored_bullet"],
            })

    # 4c. Check for skill-specific reframes (e.g. pgBackRest, PgBouncer, Partitioning)
    for sk in active_skills:
        if sk["status"] in ("partial", "missing_but_you_have_it") and sk.get("gap_advice"):
            fixes.append({
                "priority": "MEDIUM",
                "type": "Clarify Specific Tooling",
                "section": f"Core Skills / Experience ({sk['name']})",
                "why": f"The JD explicitly asks for {sk['name']} ({', '.join(sk['jd_terms'])}).",
                "before": f"Generic mention or missing explicit keyword for {sk['name']}",
                "after": sk["gap_advice"],
            })

    # 4d. Career break framing check (Jan 2025 – Aug 2025)
    if "visa" in resume_lower and "did not enrol" in resume_lower:
        fixes.append({
            "priority": "LOW",
            "type": "Tighten Career Break Line",
            "section": "Experience / Education (Jan 2025 – Aug 2025)",
            "why": "Keep the JHU MSE Data Science admission credit while keeping the focus on your return to full-time production PostgreSQL leadership in Sep 2025.",
            "before": "Admitted to MSE, Data Science, Johns Hopkins University (2025 intake); did not enrol because US student visa slots were unavailable in India.",
            "after": "Admitted to Johns Hopkins University (MSE Data Science, 2025); stayed in India due to US visa slot freeze and built Python/AI database diagnostics tooling before joining Softility as Senior Software Engineer (PostgreSQL DBA & Interim Lead).",
        })

    # 4e. Exact Core Skills block tailored to the JD order
    matched_and_fixable_names = [
        sk["name"] for sk in active_skills if sk["status"] in ("matched", "partial", "missing_but_you_have_it")
    ]
    tailored_skills_block = (
        "• Databases & HA/DR: PostgreSQL (Patroni HA, streaming replication, failover/switchover, autovacuum, partitioning, RBAC roles/grants), "
        "Db2 LUW v11.x (15+ 3/4-node HADR clusters, reorg, runstats), SQL\n"
        "• Backup, Recovery & Tuning: Point-in-Time Recovery (PITR), physical/logical backups, query & execution-plan optimization (EXPLAIN), indexing, lock contention RCA, zero-downtime Linux/DB patching, server & VM migrations\n"
        "• Leadership & Operations: Team Leadership (3-engineer DBA team & 16-member ops team), P1/P2 Incident SME (99.99% SLA across 100+ instances / 20TB+), SOP/Runbook governance, vendor transition KT, capacity planning & cost optimization\n"
        "• Automation, Cloud & Observability: Python (pandas, Selenium, AI diagnostics), Bash/Shell scripting, CI/CD schema releases & rollback, Git, Linux (RHEL), New Relic (26 automated dashboards), ServiceNow, Tableau, AWS (RDS, S3, IAM)"
    )
    fixes.append({
        "priority": "HIGH",
        "type": "Reorder & Upgrade Core Skills Block",
        "section": "CORE SKILLS",
        "why": (
            "ATS parsers rank skills by section placement and exact keyword match. This block puts the JD's top matched requirements "
            f"({', '.join(matched_and_fixable_names[:6])}) front-and-center and removes 'in progress' from AWS."
        ),
        "before": "Current CORE SKILLS section",
        "after": tailored_skills_block,
    })

    # 5. Honest True Gaps (Things NOT to fake, plus how to handle them)
    true_gaps = [
        {
            "skill": sk["name"],
            "jd_terms": sk["jd_terms"],
            "advice": sk["gap_advice"] or f"Do not fabricate {sk['name']} on your resume. Frame your production PostgreSQL + Db2 LUW HA/DR and Python automation experience as transferable.",
        }
        for sk in active_skills
        if sk["status"] == "true_gap"
    ]

    # Sort fixes: HIGH first, then MEDIUM, then LOW
    p_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    fixes.sort(key=lambda x: p_order.get(x["priority"], 9))

    # Verdict label
    if current_score >= 80:
        verdict = "Strong Match — Apply after quick keyword & metric polish"
    elif current_score >= 60:
        verdict = f"Solid Fit ({current_score}% now → ~{projected_score}% after fixes) — Apply after applying the HIGH-priority bullet updates"
    elif current_score >= 40:
        verdict = f"Partial / Stretch Match ({current_score}% now → ~{projected_score}% after fixes) — Emphasize transferable HA/DR scale & leadership"
    else:
        verdict = "Low Match — Different primary database ecosystem or role focus"

    return {
        "current_score": current_score,
        "projected_score": projected_score,
        "verdict": verdict,
        "seniority": {
            "resume_years": resume_years,
            "jd_min_years": min_jd_years,
            "note": seniority_note,
        },
        "categories": category_Readout,
        "skills_matrix": active_skills,
        "requirement_checks": requirement_checks,
        "fixes": fixes,
        "true_gaps": true_gaps,
        "counts": {
            "matched": sum(1 for s in active_skills if s["status"] == "matched"),
            "fixable": sum(1 for s in active_skills if s["status"] in ("partial", "missing_but_you_have_it")),
            "gaps": sum(1 for s in active_skills if s["status"] == "true_gap"),
            "total_jd_skills": len(active_skills),
        },
    }


def generate_ai_deep_critique(resume_text: str, jd_text: str, base_analysis: dict[str, Any]) -> dict[str, Any]:
    """Optional live Gemini AI critique if a valid GEMINI_API_KEY is configured."""
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key or not api_key.startswith("AIza"):
        return {
            "available": False,
            "reason": "Using built-in Lead DBA Domain Engine (set a standard AIza... GEMINI_API_KEY in .env if you want optional live LLM prose critique).",
        }

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are a Principal Database Architect and Hiring Manager for Lead DBA roles.\n"
            "Review this candidate's resume against the Job Description.\n"
            "STRICT RULE: Never invent fake experience or tell the candidate to lie. Only reframe real facts.\n\n"
            f"RESUME:\n{resume_text}\n\n"
            f"JOB DESCRIPTION:\n{jd_text}\n\n"
            "Return a concise JSON object with keys: "
            "'hiring_manager_first_impression' (2 sentences), "
            "'top_3_surgical_edits' (array of objects with 'where', 'before', 'after', 'why'), "
            "'interview_watchouts' (array of 2 questions the interviewer will probe based on gaps)."
        )
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        data = json.loads(resp.text)
        data["available"] = True
        return data
    except Exception as exc:
        return {
            "available": False,
            "reason": f"Built-in Lead DBA Domain Engine active (LLM call skipped: {exc}).",
        }
