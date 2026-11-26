"""Automated tests for 43-column Traffic Violations cleaning, geolocation recovery & SQLite pipeline."""

from pathlib import Path
import pandas as pd

from src.data_generator import RAW_COLUMNS_43, ensure_sample_raw_csv
from src.preprocessing import BOOLEAN_COLS, clean_traffic_dataframe, run_pipeline


def test_sample_generator_has_all_43_documented_columns(tmp_path: Path) -> None:
    csv_file = ensure_sample_raw_csv(tmp_path / "raw_traffic.csv", n_rows=400)
    raw_df = pd.read_csv(csv_file)
    assert list(raw_df.columns) == RAW_COLUMNS_43
    assert len(raw_df) == 400


def test_cleaning_recovers_geolocation_normalizes_booleans_and_years(tmp_path: Path) -> None:
    csv_file = ensure_sample_raw_csv(tmp_path / "raw_traffic.csv", n_rows=500)
    raw_df = pd.read_csv(csv_file)
    cleaned, audit = clean_traffic_dataframe(raw_df)

    assert "Geolocation" not in cleaned.columns
    assert audit["coordinates_recovered_from_geolocation"] > 0
    assert audit["invalid_vehicle_years_sanitized"] > 0

    valid_years = cleaned["Year"].dropna()
    assert ((valid_years >= 1960) & (valid_years <= 2025)).all()

    valid_lats = cleaned["Latitude"].dropna()
    assert ((valid_lats >= 24.0) & (valid_lats <= 50.0)).all()

    for col in BOOLEAN_COLS:
        assert set(cleaned[col].unique()).issubset({0, 1})


def test_end_to_end_pipeline_exports_sqlite_and_eda_report(tmp_path: Path) -> None:
    csv_file = ensure_sample_raw_csv(tmp_path / "raw_traffic.csv", n_rows=600)
    db_file = tmp_path / "traffic.db"
    report_file = tmp_path / "EDA_REPORT.md"

    df, audit = run_pipeline(csv_path=csv_file, db_path=db_file, report_path=report_file, chunksize=250)
    assert len(df) == 600
    assert db_file.exists()
    assert report_file.exists()
    assert "Top Violation Categories" in report_file.read_text(encoding="utf-8")
