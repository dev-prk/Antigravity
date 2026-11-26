# Sports Analytics on NCAAFB Data Using Real-Time API Feeds

End-to-end NCAA Football data engineering, relational SQL analytics, and Streamlit visualization platform integrating **Sportradar NCAAFB v7 API** feeds into a normalized 8-table relational database.

## Architecture

```
Sportradar NCAAFB v7 API (/seasons, /schedule, /rankings, /roster, /profile)
        │  (Rate-limit backoff + JSON response cache + verified FBS reference fallback)
        ▼
  Python ETL Layer (src/api_client.py)
        │
        ▼
  Normalized Relational SQLite Warehouse (sql/schema.sql)
  ├── Conferences        ├── Seasons           ├── Rankings (AP Top 25)
  ├── Venues             ├── Players           ├── Coaches
  ├── Teams              ├── Player_Statistics └── Schedules
        │
        ▼
  7-Page Interactive Streamlit Dashboard (app.py) + SQL Analytics Engine (src/analytics.py)
```

## Features
- **8 Normalized Relational SQL Tables (+ Schedules)** with primary keys, foreign-key constraints, and query indexes (`sql/schema.sql`).
- **Live Sportradar API Client (`src/api_client.py`)** supporting `/seasons`, `/schedule`, `/rankings/weekly`, `/teams/{id}/full_roster`, and `/players/{id}/profile` with automatic rate-limit handling (`1 QPS` trial compliance), local caching, and immediate multi-season FBS seed data (`2022–2024`) when `SPORTRADAR_API_KEY` is omitted.
- **7 Streamlit Modules (`app.py`):**
  1. Home Dashboard (KPIs, top-5 ranked teams, conference championship distribution)
  2. Teams Explorer (Conference/State/Text filters + live Team Roster viewer)
  3. Players Explorer (Position/Eligibility/Status filters + multi-season rushing/receiving progression)
  4. Season & Schedule Viewer (3+ seasons schedule, scores, stadium attendance)
  5. Rankings Table (AP Poll weekly rankings, rank movement deltas, poll points trajectory)
  6. Venue Directory (Interactive US stadium map, playing surface & roof-type filters)
  7. Coaches & SQL Insights (Coaching staff directory + all 6 analytical SQL queries with CSV export)

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

Optional live API sync:
```bash
export SPORTRADAR_API_KEY="your_key_here"
streamlit run app.py
```
