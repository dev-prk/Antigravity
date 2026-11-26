# Traffic Violations Insight System: EDA, Cleaning & Interactive Streamlit Dashboard

Chunked Python + SQLite data cleaning, exploratory data analysis, and Streamlit visual analytics system over the **43-column Montgomery County Traffic Violations** schema.

## Architecture

```
Raw Traffic_Violations.csv (43 Columns, Chunked Reader 100k rows/batch)
        │
        ▼
  43-Column Sanitization & Feature Pipeline (src/preprocessing.py)
  ├── SeqID multi-charge stop detection & exact deduplication
  ├── Mixed Date/Time parsing → Stop_Datetime, Hour, Weekday, Weekend
  ├── US Lat/Lon validation (0 → NaN) + fallback recovery from Geolocation
  ├── Normalization of all 12 Yes/No boolean flags & Vehicle Year (1960–2025)
  └── Violation categorization + Search disposition consistency rules
        │
        ├──► Indexed SQLite Database (data/traffic_insights.db)
        ├──► Automated Markdown Report (reports/EDA_REPORT.md)
        └──► Interactive Streamlit Dashboard (app.py)
```

## Key Capabilities
- **Memory-Safe Chunked Processing**: Handles both the full 1M-row (`839 MB`) `data/Traffic_Violations.csv` via `chunksize=100_000` and automatically generates a realistic 12,000-row 43-column raw sample when the full file is not present locally.
- **Interactive Dashboard (`app.py`)**: Sidebar filters across Date Range, District/SubAgency, Violation Category, Vehicle Type, Gender, Race, and Multi-Charge `SeqID` deduplication; OpenStreetMap corridor hotspot map; Hour × Weekday heatmap; demographic & vehicle charts; and live SQL workbench.

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
```
