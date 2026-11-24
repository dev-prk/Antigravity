"""FastAPI backend for the PostgreSQL EXPLAIN (ANALYZE) & Query Tuning Advisor."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from explain_analyzer import analyze_explain_and_query

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="PostgreSQL EXPLAIN (ANALYZE) & Query Tuning Advisor")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


PRESET_SCENARIOS: dict[str, dict[str, str]] = {
    "seq_scan_external_sort": {
        "title": "Ticket #1: Slow Order History API (Seq Scan + 49MB External Disk Sort + Deep OFFSET)",
        "category": "Indexing · work_mem · Keyset Pagination",
        "difficulty": "Lead DBA Core",
        "sql": """SELECT id, customer_id, total_amount, created_at
FROM orders o
WHERE o.tenant_id = 42
  AND o.status = 'PAID'
ORDER BY o.created_at DESC
LIMIT 50 OFFSET 50000;""",
        "explain": """Limit  (cost=184520.45..184520.58 rows=50 width=148) (actual time=1428.412..1428.445 rows=50 loops=1)
  Buffers: shared hit=4210 read=98450, temp read=12450 written=12455
  ->  Sort  (cost=184395.45..186895.45 rows=1000000 width=148) (actual time=1412.110..1425.890 rows=50050 loops=1)
        Sort Key: created_at DESC
        Sort Method: external merge  Disk: 49800kB
        Buffers: shared hit=4210 read=98450, temp read=12450 written=12455
        ->  Seq Scan on orders o  (cost=0.00..115160.00 rows=1000000 width=148) (actual time=0.045..960.230 rows=420000 loops=1)
              Filter: ((tenant_id = 42) AND ((status)::text = 'PAID'::text))
              Rows Removed by Filter: 4580000
              Buffers: shared hit=4210 read=98450
Planning Time: 0.420 ms
Execution Time: 1435.820 ms""",
    },
    "bad_stats_nested_loop": {
        "title": "Ticket #2: P1 Checkout Spike (240x Row Underestimate Driving 12,000 Nested Loop Probes)",
        "category": "Planner Statistics · Nested Loop vs Hash Join · Missing FK Index",
        "difficulty": "Lead DBA Core",
        "sql": """SELECT c.id, c.region, c.tier, i.invoice_number, i.amount_cents
FROM customers c
JOIN invoices i ON i.customer_id = c.id
WHERE c.region = 'APAC'
  AND c.tier = 'ENTERPRISE'
  AND i.billing_state = 'UNPAID';""",
        "explain": """Nested Loop  (cost=0.43..4825.60 rows=45 width=96) (actual time=0.310..2840.650 rows=18420 loops=1)
  Buffers: shared hit=142000 read=318400
  ->  Index Scan using idx_customers_region on customers c  (cost=0.43..124.50 rows=50 width=44) (actual time=0.040..18.420 rows=12000 loops=1)
        Index Cond: ((region)::text = 'APAC'::text)
        Filter: ((tier)::text = 'ENTERPRISE'::text)
        Rows Removed by Filter: 34000
        Buffers: shared hit=1200 read=410
  ->  Seq Scan on invoices i  (cost=0.00..94.00 rows=2 width=52) (actual time=0.012..0.234 rows=2 loops=12000)
        Filter: ((customer_id = c.id) AND ((billing_state)::text = 'UNPAID'::text))
        Rows Removed by Filter: 4850
        Buffers: shared hit=140800 read=317990
Planning Time: 0.610 ms
Execution Time: 2846.190 ms""",
    },
    "correlated_subplan_sargable": {
        "title": "Ticket #3: Reporting Timeout (Correlated SubPlan x8,500 Loops + Non-Sargable DATE_TRUNC)",
        "category": "Query Rewrite · Sargability · Functional Filter",
        "difficulty": "Senior / Lead Interview",
        "sql": """SELECT a.account_id,
       a.company_name,
       (SELECT COUNT(*) FROM audit_events e WHERE e.account_id = a.account_id AND e.severity = 'HIGH') AS high_alerts
FROM accounts a
WHERE date_trunc('day', a.updated_at) = '2026-11-01 00:00:00'
  AND a.account_id NOT IN (SELECT account_id FROM suspended_accounts);""",
        "explain": """Seq Scan on accounts a  (cost=0.00..412890.00 rows=8500 width=72) (actual time=1.240..3412.880 rows=8500 loops=1)
  Filter: ((NOT (hashed SubPlan 2)) AND (date_trunc('day'::text, updated_at) = '2026-11-01 00:00:00'::timestamp without time zone))
  Rows Removed by Filter: 941500
  Buffers: shared hit=910200 read=84500
  SubPlan 1
    ->  Aggregate  (cost=48.10..48.11 rows=1 width=8) (actual time=0.365..0.365 rows=1 loops=8500)
          Buffers: shared hit=850000 read=42000
          ->  Seq Scan on audit_events e  (cost=0.00..48.00 rows=4 width=0) (actual time=0.015..0.358 rows=6 loops=8500)
                Filter: ((account_id = a.account_id) AND ((severity)::text = 'HIGH'::text))
                Rows Removed by Filter: 2400
                Buffers: shared hit=850000 read=42000
  SubPlan 2
    ->  Seq Scan on suspended_accounts  (cost=0.00..24.00 rows=1400 width=8) (actual time=0.010..0.190 rows=1400 loops=1)
          Buffers: shared hit=10
Planning Time: 0.540 ms
Execution Time: 3418.450 ms""",
    },
    "lossy_bitmap_leading_wildcard": {
        "title": "Ticket #4: Customer Search Degradation (Lossy Bitmap Heap Scan + Leading Wildcard ILIKE)",
        "category": "work_mem Lossy Pages · pg_trgm GIN · Autovacuum Visibility Map",
        "difficulty": "Lead DBA Deep Dive",
        "sql": """SELECT id, email, full_name, phone, last_login_at
FROM user_profiles u
WHERE u.org_id = 108
  AND u.email ILIKE '%@enterprise-client.com';""",
        "explain": """Bitmap Heap Scan on user_profiles u  (cost=412.80..48920.50 rows=4200 width=112) (actual time=38.400..842.150 rows=3850 loops=1)
  Recheck Cond: (org_id = 108)
  Rows Removed by Index Recheck: 1420000
  Filter: ((email)::text ~~* '%@enterprise-client.com'::text)
  Rows Removed by Filter: 286150
  Heap Blocks: exact=4120 lossy=28450
  Buffers: shared hit=8120 read=24450
  ->  Bitmap Index Scan on idx_user_profiles_org_id  (cost=0.00..411.75 rows=290000 width=0) (actual time=24.110..24.110 rows=290000 loops=1)
        Index Cond: (org_id = 108)
        Buffers: shared hit=795
Planning Time: 0.310 ms
Execution Time: 845.600 ms""",
    },
    "healthy_index_only_scan": {
        "title": "Ticket #5 (Contrast Check): Already-Optimized Index Only Scan (0.06 ms)",
        "category": "Healthy Baseline · Zero Spills · Avoid Over-Indexing",
        "difficulty": "Contrast Verification",
        "sql": """SELECT id, email
FROM users u
WHERE u.email = 'devesh.pareek@example.com';""",
        "explain": """Index Only Scan using idx_users_email_covering on users u  (cost=0.43..4.45 rows=1 width=36) (actual time=0.028..0.031 rows=1 loops=1)
  Index Cond: (email = 'devesh.pareek@example.com'::text)
  Heap Fetches: 0
  Buffers: shared hit=4
Planning Time: 0.085 ms
Execution Time: 0.055 ms""",
    },
}


class ExplainAnalyzeRequest(BaseModel):
    explain_text: str
    sql_text: str = ""


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/presets")
def get_presets() -> JSONResponse:
    return JSONResponse({"scenarios": PRESET_SCENARIOS})


@app.post("/api/analyze")
def analyze_plan(req: ExplainAnalyzeRequest) -> JSONResponse:
    explain_raw = (req.explain_text or "").strip()
    sql_raw = (req.sql_text or "").strip()

    if len(explain_raw) < 15:
        raise HTTPException(
            status_code=422,
            detail="Please paste a PostgreSQL EXPLAIN or EXPLAIN (ANALYZE, BUFFERS) output before running diagnosis.",
        )

    try:
        result: dict[str, Any] = analyze_explain_and_query(explain_raw, sql_raw)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse EXPLAIN output: {exc}") from exc

    return JSONResponse(result)
