"""Data Cleaning, Relational SQL Ingestion & Feature Engineering for Rapido Mobility Insights."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "rapido_mobility.db"


def load_raw_tables(data_dir: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    d = Path(data_dir) if data_dir else DATA_DIR
    return {
        "bookings": pd.read_csv(d / "bookings.csv"),
        "customers": pd.read_csv(d / "customers.csv"),
        "drivers": pd.read_csv(d / "drivers.csv"),
        "location_demand": pd.read_csv(d / "location_demand.csv"),
        "time_features": pd.read_csv(d / "time_features.csv"),
    }


def engineer_features(tables: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cleans tables, builds Driver_Reliability_Score & Customer_Loyalty_Score, and enriches bookings
    with all spec-required features without leaking post-trip fields into pre-trip predictors.
    """
    bookings = tables["bookings"].copy()
    customers = tables["customers"].copy()
    drivers = tables["drivers"].copy()
    loc_demand = tables["location_demand"].copy()
    time_feat = tables["time_features"].copy()

    # Customer_Loyalty_Score (0..100 composite)
    max_bookings = max(float(customers["total_bookings"].max()), 1.0)
    max_signup = max(float(customers["customer_signup_days_ago"].max()), 1.0)
    customers["Customer_Loyalty_Score"] = (
        0.40 * (1.0 - customers["cancellation_rate"].clip(0, 1))
        + 0.25 * (customers["avg_customer_rating"].clip(1, 5) / 5.0)
        + 0.20 * (customers["total_bookings"] / max_bookings)
        + 0.15 * (customers["customer_signup_days_ago"] / max_signup)
    ).round(4) * 100.0

    # Driver_Reliability_Score (0..100 composite)
    max_exp = max(float(drivers["driver_experience_years"].max()), 1.0)
    drivers["Driver_Reliability_Score"] = (
        0.35 * drivers["acceptance_rate"].clip(0, 1)
        + 0.35 * (1.0 - drivers["delay_rate"].clip(0, 1))
        + 0.20 * (drivers["avg_driver_rating"].clip(1, 5) / 5.0)
        + 0.10 * (drivers["driver_experience_years"] / max_exp)
    ).round(4) * 100.0

    # Parse booking datetime & temporal hour slice for joining time_features
    bookings["booking_datetime"] = pd.to_datetime(
        bookings["booking_date"].astype(str) + " " + bookings["booking_time"].astype(str),
        errors="coerce",
    )
    bookings["booking_hour_key"] = bookings["booking_datetime"].dt.floor("h").astype(str)
    time_dedup = time_feat.drop_duplicates(subset=["datetime"])[["datetime", "is_holiday", "peak_time_flag", "season"]]

    merged = (
        bookings.merge(
            customers[["customer_id", "customer_age", "customer_signup_days_ago", "total_bookings", "cancellation_rate", "avg_customer_rating", "Customer_Loyalty_Score", "customer_cancel_flag"]],
            on="customer_id",
            how="left",
        )
        .merge(
            drivers[["driver_id", "driver_age", "driver_experience_years", "acceptance_rate", "delay_rate", "avg_driver_rating", "avg_pickup_delay_min", "Driver_Reliability_Score", "driver_delay_flag"]],
            on="driver_id",
            how="left",
        )
        .merge(
            loc_demand[["city", "pickup_location", "hour_of_day", "vehicle_type", "total_requests", "avg_wait_time_min", "demand_level"]],
            on=["city", "pickup_location", "hour_of_day", "vehicle_type"],
            how="left",
        )
        .merge(
            time_dedup,
            left_on="booking_hour_key",
            right_on="datetime",
            how="left",
        )
    )

    dist_safe = merged["ride_distance_km"].clip(lower=0.2)
    est_min_safe = merged["estimated_ride_time_min"].clip(lower=1.0)

    # Required Spec Engineered Features
    merged["Fare_per_KM"] = (merged["booking_value"] / dist_safe).round(2)
    merged["Fare_per_Min"] = (merged["booking_value"] / est_min_safe).round(2)
    merged["Base_Fare_per_KM"] = (merged["base_fare"] / dist_safe).round(2)
    merged["Est_Min_per_KM"] = (merged["estimated_ride_time_min"] / dist_safe).round(2)
    merged["Rush_Hour_Flag"] = merged["hour_of_day"].isin([8, 9, 10, 17, 18, 19, 20]).astype(int)
    merged["Long_Distance_Flag"] = (merged["ride_distance_km"] >= 12.0).astype(int)
    merged["City_Pair"] = merged["city"].astype(str) + ":" + merged["pickup_location"].astype(str) + "->" + merged["drop_location"].astype(str)

    # Clean post-trip nulls without leaking into pre-trip features
    merged["incomplete_ride_reason"] = merged["incomplete_ride_reason"].fillna("Not Incomplete")
    merged["demand_level"] = merged["demand_level"].fillna("Medium")
    merged["season"] = merged["season"].fillna("Winter")
    merged["is_holiday"] = merged["is_holiday"].fillna(0).astype(int)
    merged["peak_time_flag"] = merged["peak_time_flag"].fillna(merged["Rush_Hour_Flag"]).astype(int)
    merged["total_requests"] = merged["total_requests"].fillna(merged["total_requests"].median())
    merged["avg_wait_time_min"] = merged["avg_wait_time_min"].fillna(merged["avg_wait_time_min"].median())

    return merged, customers, drivers


def build_sqlite_warehouse(tables: Dict[str, pd.DataFrame], db_path: Optional[Path] = None) -> Path:
    target = Path(db_path) if db_path else DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(target)) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bk_city_hour ON bookings(city, hour_of_day);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bk_status ON bookings(booking_status);")
        conn.commit()
    return target
