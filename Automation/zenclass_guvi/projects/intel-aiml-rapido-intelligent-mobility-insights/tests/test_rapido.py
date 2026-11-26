"""Automated test suite for Rapido Intelligent Mobility Insights."""

from fastapi.testclient import TestClient

from api import app
from src.data_pipeline import engineer_features, load_raw_tables
from src.modeling import BOOKING_NUMERIC_COLS, load_or_train_bundle, predict_single_ride, train_all_models


def test_feature_engineering_and_zero_post_trip_leakage() -> None:
    tables = load_raw_tables()
    merged, customers, drivers = engineer_features(tables)

    for col in [
        "Fare_per_KM",
        "Fare_per_Min",
        "Rush_Hour_Flag",
        "Long_Distance_Flag",
        "City_Pair",
        "Driver_Reliability_Score",
        "Customer_Loyalty_Score",
    ]:
        assert col in merged.columns

    # Ensure post-trip columns are never used as pre-trip model features
    assert "actual_ride_time_min" not in BOOKING_NUMERIC_COLS
    assert "incomplete_ride_reason" not in BOOKING_NUMERIC_COLS


def test_all_four_models_train_and_predict_valid_outputs() -> None:
    bundle = load_or_train_bundle()
    metrics = bundle["metrics"]

    assert set(metrics.keys()) == {
        "ride_outcome_model",
        "fare_prediction_model",
        "customer_cancellation_model",
        "driver_delay_model",
    }
    assert metrics["fare_prediction_model"]["r2"] > 0.85
    assert metrics["customer_cancellation_model"]["accuracy"] > 0.80
    assert metrics["driver_delay_model"]["roc_auc"] > 0.75

    pred = predict_single_ride({"city": "Mumbai", "vehicle_type": "Cab", "ride_distance_km": 14.0}, bundle=bundle)
    assert pred["predicted_outcome"] in {"Completed", "Cancelled", "Incomplete"}
    assert pred["predicted_fare_inr"] > 0


def test_fastapi_endpoints() -> None:
    client = TestClient(app)
    h = client.get("/health")
    assert h.status_code == 200

    p = client.post("/predict/ride", json={"city": "Bangalore", "vehicle_type": "Auto", "ride_distance_km": 7.2})
    assert p.status_code == 200
    body = p.json()
    assert "predicted_fare_inr" in body
    assert "operational_intervention" in body
