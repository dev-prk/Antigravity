"""43-Column Data Cleaning, Coordinate Validation, Categorization, SQLite Export & EDA Report Engine."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.data_generator import ensure_sample_raw_csv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FULL_CSV = BASE_DIR / "data" / "Traffic_Violations.csv"
DEFAULT_SAMPLE_CSV = BASE_DIR / "data" / "traffic_violations_sample_raw.csv"
DEFAULT_DB_PATH = BASE_DIR / "data" / "traffic_insights.db"
DEFAULT_REPORT_PATH = BASE_DIR / "reports" / "EDA_REPORT.md"

BOOLEAN_COLS = [
    "Accident", "Belts", "Personal Injury", "Property Damage", "Fatal",
    "Commercial License", "HAZMAT", "Commercial Vehicle", "Alcohol",
    "Work Zone", "Search Conducted", "Contributed To Accident",
]

GEOLOC_REGEX = re.compile(r"\(\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)")


def categorize_violation(description: Any) -> str:
    txt = str(description or "").upper()
    if any(k in txt for k in ("SPEED", "MPH", "EXCEEDING")):
        return "Speeding"
    if any(k in txt for k in ("STOP SIGN", "TRAFFIC CONTROL", "RED SIGNAL", "FLASHING")):
        return "Traffic Signal / Stop Sign"
    if any(k in txt for k in ("ALCOHOL", "INFLUENCE", "IMPAIRED", "DUI")):
        return "DUI / Alcohol"
    if any(k in txt for k in ("TELEPHONE", "TEXT", "HANDHELD", "ELECTRONIC")):
        return "Distracted Driving"
    if any(k in txt for k in ("SEAT BELT", "CHILD SAFETY", "SECURED")):
        return "Seatbelt / Restraint"
    if any(k in txt for k in ("UNINSURED", "REGISTRATION", "LICENSE", "SUSPENDED")):
        return "License / Registration / Insurance"
    if any(k in txt for k in ("HEADLIGHT", "TAILLIGHT", "WINDOW TINT", "EQUIPMENT", "BRAKE")):
        return "Equipment / SERO"
    if any(k in txt for k in ("NEGLIGENT", "RECKLESS", "CARELESS", "AGGRESSIVE")):
        return "Reckless / Negligent Driving"
    return "Other Traffic Violation"


def _parse_geolocation_series(geoloc: pd.Series) -> Tuple[pd.Series, pd.Series]:
    extracted = geoloc.fillna("").astype(str).str.extract(GEOLOC_REGEX)
    g_lat = pd.to_numeric(extracted[0], errors="coerce")
    g_lon = pd.to_numeric(extracted[1], errors="coerce")
    return g_lat, g_lon


def clean_traffic_dataframe(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Cleans all 43 Traffic Violations columns, recovers coordinates, normalizes booleans, and derives time features."""
    df = raw_df.copy()
    initial_rows = len(df)
    exact_dupes = int(df.duplicated().sum())
    if exact_dupes:
        df = df.drop_duplicates().reset_index(drop=True)

    # Track multi-charge stops sharing the same SeqID
    seq_counts = df["SeqID"].value_counts()
    df["Charges_In_Stop"] = df["SeqID"].map(seq_counts).fillna(1).astype(int)
    df["Is_Multi_Charge_Stop"] = df["Charges_In_Stop"] > 1

    # Parse inconsistent Date Of Stop & Time Of Stop
    parsed_date = pd.to_datetime(df["Date Of Stop"], format="mixed", errors="coerce")
    parsed_time = pd.to_timedelta(df["Time Of Stop"].astype(str), errors="coerce")
    df["Stop_Datetime"] = parsed_date + parsed_time.fillna(pd.Timedelta(0))
    df["Year_Of_Stop"] = parsed_date.dt.year
    df["Month_Name"] = parsed_date.dt.month_name()
    df["Month_Num"] = parsed_date.dt.month
    df["Day_Of_Week"] = parsed_date.dt.day_name()
    df["Hour_Of_Stop"] = (parsed_time.dt.total_seconds() // 3600).fillna(0).astype(int).clip(0, 23)
    df["Is_Weekend"] = parsed_date.dt.dayofweek.isin([5, 6])

    # Validate Latitude & Longitude (US continental bounds: Lat 24..50, Lon -125..-66; replace 0 with NaN)
    lat = pd.to_numeric(df["Latitude"], errors="coerce")
    lon = pd.to_numeric(df["Longitude"], errors="coerce")
    lat = lat.where((lat >= 24.0) & (lat <= 50.0), np.nan)
    lon = lon.where((lon >= -125.0) & (lon <= -66.0), np.nan)

    recovered_coords = 0
    if "Geolocation" in df.columns:
        g_lat, g_lon = _parse_geolocation_series(df["Geolocation"])
        g_lat = g_lat.where((g_lat >= 24.0) & (g_lat <= 50.0), np.nan)
        g_lon = g_lon.where((g_lon >= -125.0) & (g_lon <= -66.0), np.nan)
        missing_before = int(lat.isna().sum())
        lat = lat.fillna(g_lat)
        lon = lon.fillna(g_lon)
        recovered_coords = missing_before - int(lat.isna().sum())
        df = df.drop(columns=["Geolocation"])

    df["Latitude"] = lat
    df["Longitude"] = lon

    # Normalize all 12 boolean columns to 0/1 integers
    bool_map = {"YES": 1, "Y": 1, "TRUE": 1, "1": 1, "NO": 0, "N": 0, "FALSE": 0, "0": 0}
    for col in BOOLEAN_COLS:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(bool_map)
                .fillna(0)
                .astype(int)
            )

    # Normalize Vehicle Year (valid window: 1960 - 2025)
    v_year = pd.to_numeric(df["Year"], errors="coerce")
    invalid_years = int(((v_year < 1960) | (v_year > 2025)).sum())
    df["Year"] = v_year.where((v_year >= 1960) & (v_year <= 2025), np.nan)

    # Normalize string attributes
    for text_col in ["Agency", "SubAgency", "Location", "Make", "Model", "Color", "Violation Type", "Race", "Gender", "Driver City", "Driver State", "DL State", "VehicleType", "Arrest Type"]:
        if text_col in df.columns:
            df[text_col] = df[text_col].fillna("UNKNOWN").astype(str).str.strip()
            if text_col in ("Make", "Model", "Color", "Location", "Race", "Gender", "Driver City", "Driver State", "DL State"):
                df[text_col] = df[text_col].str.upper()

    # Handle search-related columns cleanly when Search Conducted == 0
    for s_col in ["Search Disposition", "Search Reason", "Search Type", "Search Arrest Reason"]:
        if s_col in df.columns:
            df[s_col] = np.where(
                df["Search Conducted"] == 0,
                "Not Applicable",
                df[s_col].fillna("Unspecified").astype(str).str.strip(),
            )
    if "Article" in df.columns:
        df["Article"] = df["Article"].fillna("Not Applicable (SERO)").astype(str).str.strip()

    df["Violation_Category"] = df["Description"].map(categorize_violation)

    audit = {
        "initial_rows": initial_rows,
        "cleaned_rows": len(df),
        "exact_duplicates_removed": exact_dupes,
        "unique_seq_ids": int(df["SeqID"].nunique()),
        "multi_charge_rows": int(df["Is_Multi_Charge_Stop"].sum()),
        "coordinates_recovered_from_geolocation": recovered_coords,
        "valid_coordinates_pct": round(float(df["Latitude"].notna().mean() * 100), 2),
        "invalid_vehicle_years_sanitized": invalid_years,
    }
    return df, audit


def run_pipeline(
    csv_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
    report_path: Optional[Path] = None,
    chunksize: int = 100_000,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Streams full or sample CSV in memory-safe chunks, writes indexed SQLite DB, and exports EDA report."""
    source_csv = Path(csv_path) if csv_path else (DEFAULT_FULL_CSV if DEFAULT_FULL_CSV.exists() else ensure_sample_raw_csv(DEFAULT_SAMPLE_CSV))
    target_db = Path(db_path) if db_path else DEFAULT_DB_PATH
    target_report = Path(report_path) if report_path else DEFAULT_REPORT_PATH
    target_db.parent.mkdir(parents=True, exist_ok=True)
    target_report.parent.mkdir(parents=True, exist_ok=True)

    cleaned_chunks = []
    combined_audit: Dict[str, Any] = {
        "source_csv": str(source_csv.name),
        "initial_rows": 0,
        "cleaned_rows": 0,
        "exact_duplicates_removed": 0,
        "coordinates_recovered_from_geolocation": 0,
        "invalid_vehicle_years_sanitized": 0,
    }

    for chunk in pd.read_csv(source_csv, chunksize=chunksize, low_memory=False):
        c_df, c_audit = clean_traffic_dataframe(chunk)
        cleaned_chunks.append(c_df)
        for k in ("initial_rows", "cleaned_rows", "exact_duplicates_removed", "coordinates_recovered_from_geolocation", "invalid_vehicle_years_sanitized"):
            combined_audit[k] += c_audit[k]

    full_df = pd.concat(cleaned_chunks, ignore_index=True)
    combined_audit["unique_seq_ids"] = int(full_df["SeqID"].nunique())
    combined_audit["multi_charge_rows"] = int((full_df["SeqID"].duplicated(keep=False)).sum())
    combined_audit["valid_coordinates_pct"] = round(float(full_df["Latitude"].notna().mean() * 100), 2)

    with sqlite3.connect(str(target_db)) as conn:
        full_df.to_sql("traffic_violations", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tv_cat ON traffic_violations(Violation_Category);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tv_sub ON traffic_violations(SubAgency);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tv_hour ON traffic_violations(Hour_Of_Stop);")
        conn.commit()

    _write_eda_report(full_df, combined_audit, target_report)
    return full_df, combined_audit


def _write_eda_report(df: pd.DataFrame, audit: Dict[str, Any], report_path: Path) -> None:
    top_cats = df["Violation_Category"].value_counts().head(5)
    top_zones = df["Location"].value_counts().head(5)
    top_makes = df["Make"].value_counts().head(5)
    acc_rate = df["Accident"].mean() * 100
    alc_acc_rate = df.loc[df["Alcohol"] == 1, "Accident"].mean() * 100 if (df["Alcohol"] == 1).any() else 0.0

    lines = [
        "# Traffic Violations Insight System — Automated EDA & Data Quality Report",
        "",
        "## 1. Data Cleaning & Audit Summary",
        f"- **Source File**: `{audit['source_csv']}`",
        f"- **Raw Records Processed**: `{audit['initial_rows']:,}`",
        f"- **Cleaned Records**: `{audit['cleaned_rows']:,}` (`{audit['unique_seq_ids']:,}` unique `SeqID` traffic stops)",
        f"- **Multi-Charge Rows Flagged**: `{audit['multi_charge_rows']:,}`",
        f"- **Coordinates Recovered from `Geolocation`**: `{audit['coordinates_recovered_from_geolocation']:,}` (`{audit['valid_coordinates_pct']}%` valid US coordinates)",
        f"- **Out-of-Bounds Vehicle Years Sanitized (`<1960` or `>2025`)**: `{audit['invalid_vehicle_years_sanitized']:,}`",
        "",
        "## 2. Top Violation Categories",
        *[f"- **{cat}**: `{cnt:,}` (`{cnt/len(df)*100:.1f}%`)" for cat, cnt in top_cats.items()],
        "",
        "## 3. High-Risk Corridors & Hotspots",
        *[f"- **{loc}**: `{cnt:,}` stops" for loc, cnt in top_zones.items()],
        "",
        "## 4. Safety & Accident Risk Insights",
        f"- **Overall Accident-Linked Violations**: `{acc_rate:.2f}%`",
        f"- **Accident Rate When Alcohol Involved**: `{alc_acc_rate:.2f}%`",
        f"- **Top Vehicle Makes Stopped**: {', '.join(f'{m} ({c:,})' for m, c in top_makes.items())}",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
