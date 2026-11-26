"""FastAPI Real-Time Prediction Microservice for Rapido Intelligent Mobility."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.modeling import load_or_train_bundle, predict_single_ride

app = FastAPI(title="Rapido Intelligent Mobility Prediction API", version="1.0.0")


class RidePredictionRequest(BaseModel):
    city: str = "Bangalore"
    vehicle_type: str = "Bike"
    day_of_week: str = "Friday"
    hour_of_day: int = Field(default=18, ge=0, le=23)
    is_weekend: int = Field(default=0, ge=0, le=1)
    ride_distance_km: float = Field(default=8.5, gt=0.1)
    estimated_ride_time_min: float = Field(default=28.0, gt=0.5)
    base_fare: float = Field(default=95.0, gt=1.0)
    surge_multiplier: float = Field(default=1.3, ge=1.0, le=5.0)
    traffic_level: str = "High"
    weather_condition: str = "Clear"
    demand_level: str = "High"
    Customer_Loyalty_Score: float = 75.0
    Driver_Reliability_Score: float = 82.0
    cancellation_rate: float = 0.10
    delay_rate: float = 0.06
    acceptance_rate: float = 0.85
    avg_pickup_delay_min: float = 3.0


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Rapido Mobility ML Engine"}


@app.get("/metrics")
def get_metrics():
    bundle = load_or_train_bundle()
    return bundle["metrics"]


@app.post("/predict/ride")
def predict_ride(req: RidePredictionRequest):
    bundle = load_or_train_bundle()
    return predict_single_ride(req.model_dump(), bundle=bundle)
