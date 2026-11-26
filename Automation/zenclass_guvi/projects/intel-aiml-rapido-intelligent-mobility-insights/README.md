# Rapido: Intelligent Mobility Insights — Ride Patterns, Cancellations & Fare Forecasting

End-to-end mobility analytics, relational SQL warehouse, 4-model ML decision engine (`GridSearchCV` tuned), FastAPI prediction microservice, and Streamlit operational dashboard trained on the **100,000-row Rapido multi-table dataset**.

## Architecture

```
bookings.csv (100k) + customers.csv (10k) + drivers.csv (5k) + location_demand.csv + time_features.csv
        │
        ▼
  Relational Ingestion & Feature Pipeline (src/data_pipeline.py)
  ├── SQLite Warehouse (data/rapido_mobility.db)
  └── Engineered Signals: Fare_per_KM, Fare_per_Min, Rush_Hour_Flag, Long_Distance_Flag,
      City_Pair, Driver_Reliability_Score, Customer_Loyalty_Score (strictly leakage-free)
        │
        ▼
  4-Model Tuned ML Suite (src/modeling.py — 80/20 Holdout + GridSearchCV)
  ├── 1. Ride Outcome Classifier (Completed / Cancelled / Incomplete)
  ├── 2. Dynamic Fare Regressor (RMSE, MAE, R², ±10% accuracy)
  ├── 3. Customer Cancellation Risk Classifier
  └── 4. Driver Delay Classifier
        │
        ├──► FastAPI Inference Service (api.py: /health, /metrics, /predict/ride)
        └──► Interactive Streamlit Dashboard (app.py)
```

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
# Optional FastAPI server:
uvicorn api:app --reload --port 8003
```
