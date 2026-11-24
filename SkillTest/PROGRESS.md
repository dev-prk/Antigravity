# SkillTest — PostgreSQL EXPLAIN (ANALYZE) & Query Tuning Advisor

## Brief
1. **Ask:** Build a small local web tool in `~/Documents/Antigravity/SkillTest` where the user pastes a PostgreSQL `EXPLAIN (ANALYZE)` output and the SQL query, and it tells them what's slow, why, and exactly what to change (index, rewrite, setting) for Lead DBA interview practice and real tickets.
2. **Must-haves:**
   - "small local web tool"
   - "paste a PostgreSQL EXPLAIN (ANALYZE) output and the query"
   - "tells me what's slow, why, and exactly what to change (index, rewrite, setting)"
   - "Put it in ~/Documents/Antigravity/SkillTest"
   - "practise for Lead DBA interviews and on real tickets"
3. **Done test:** Open the local web app in the browser, paste or load a slow `EXPLAIN (ANALYZE, BUFFERS)` plan and SQL query, click Analyze, and see: (a) the exact bottleneck node(s) ranked by self/exclusive time with parent-child plan tree timing & buffer metrics, (b) plain-English root cause ("why it's slow"), and (c) concrete, copy-ready fixes categorized into **Index DDL** (`CREATE INDEX CONCURRENTLY ...` derived from the actual table/columns in the plan & query), **Query Rewrite** (before/after SQL tailored to the query), and **PostgreSQL Settings / Maintenance** (`SET work_mem`, `ANALYZE`, `random_page_cost`, etc.), plus an Interactive Lead DBA Interview Practice mode (hide findings first so the user can diagnose the plan themselves, then reveal the Lead DBA model answer). Contrast-test against a fast already-indexed query (~0.2ms Index Only Scan) to confirm it reports the query is already healthy rather than inventing fake index recommendations, and test malformed/empty input.
4. **Expert gap:**
   - **Inclusive vs. Exclusive (Self) Time & Loop Multipliers:** In PostgreSQL `EXPLAIN ANALYZE`, `actual time=start..end` is *per-loop average* and *inclusive of child nodes*. True node duration is `end * actual_loops`, and true **self (exclusive) time** is `(node_end * node_loops) - sum(child_end * child_loops)`. A Lead DBA tool must calculate exclusive time accurately so a top-level `Limit` or `Nested Loop` isn't blamed when its inner child scan or sort is doing 98% of the work.
   - **Format coverage:** Real tickets have Text `EXPLAIN (ANALYZE, BUFFERS)` output (sometimes with `VERBOSE` or `SETTINGS`) or JSON `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`. The parser must accept both text and JSON plans, as well as bare `EXPLAIN` (cost-only without `ANALYZE`, flagging that runtime actuals aren't present).
   - **Buffers & I/O math:** 1 PostgreSQL block = 8 KiB. `Buffers: shared hit=X read=Y temp read=Z written=W` must be converted to actual MiB/GiB read from disk or spilled to temp files so a DBA can quantify I/O pressure immediately.
   - **Dynamic DDL & SQL extraction from actual input:** Never show canned advice. Parse the actual relation name, alias, `Filter:`, `Index Cond:`, `Recheck Cond:`, `Hash Cond:`, `Join Filter:`, `Sort Key:`, `Order By`, and SQL query AST/clauses to synthesize exact `CREATE INDEX CONCURRENTLY idx_<table>_<cols> ON <table> (...)` (including covering `INCLUDE (...)`, partial `WHERE ...`, or functional `LOWER(...)` / date range adjustments), exact SQL rewrites (`NOT IN` -> `NOT EXISTS`, non-sargable function wrapper -> range predicate, `OFFSET` pagination -> keyset pagination, CTE materialization / correlated subquery -> window or join), and exact `postgresql.conf` / session commands (`work_mem` sized to `Sort Method: external merge Disk: XkB`, `ANALYZE <table>`, `CREATE STATISTICS`, `random_page_cost`, `effective_cache_size`, `max_parallel_workers_per_gather`).
   - **Lead DBA Interview Practice Mode:** A toggleable "Interview Practice Mode" that lets the user inspect the plan + query first, write their own diagnosis, and then reveal the Lead DBA scorecard & talking points (covering production rollout safety like `CONCURRENTLY`, `lock_timeout`, write amplification, and verification via `pg_stat_statements`).
5. **Smallest version:** FastAPI backend (`app.py` + `explain_analyzer.py`) serving a single-page local web UI (`static/index.html`) on `http://127.0.0.1:8765`, with realistic production ticket presets and interview practice toggle.
6. **Not building:** External cloud telemetry agents, mandatory live Postgres connection requirement to paste a plan, heavy frontend build steps, or fake keyword scorers.
7. **Unknowns:**
   - *Assume:* Host at `~/Documents/Antigravity/SkillTest` on port `8765` (replacing the earlier app in `SkillTest` per user's explicit instruction "Put it in ~/Documents/Antigravity/SkillTest"). No external API key is required for core analysis.

## Progress
- [x] Write brief in `PROGRESS.md`
- [ ] Build `explain_analyzer.py` (PostgreSQL Text & JSON EXPLAIN parser, exclusive-time & buffer calculator, SQL correlate & diagnosis engine)
- [ ] Test `explain_analyzer.py` via CLI on multiple real plans (slow seq scan/external sort, bad row estimate nested loop, correlated subquery / non-sargable filter, fast healthy index-only scan, malformed input)
- [ ] Update `app.py` and `static/index.html`
- [ ] Verify end-to-end in the live browser
