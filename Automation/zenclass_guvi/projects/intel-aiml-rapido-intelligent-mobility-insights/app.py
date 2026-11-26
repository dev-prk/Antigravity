"""Interactive Streamlit Dashboard for Rapido: Intelligent Mobility Insights."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_pipeline import build_sqlite_warehouse, engineer_features, load_raw_tables
from src.modeling import load_or_train_bundle, predict_single_ride

st.set_page_config(
    page_title="Rapido Intelligent Mobility Insights",
    page_icon="🛵",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading 100k Rapido bookings & trained 4-model ML suite...")
def init_system():
    tables = load_raw_tables()
    build_sqlite_warehouse(tables)
    merged, customers, drivers = engineer_features(tables)
    bundle = load_or_train_bundle()
    return merged, customers, drivers, bundle


merged, customers, drivers, bundle = init_system()
metrics = bundle["metrics"]

st.sidebar.title("🛵 Rapido Mobility AI")
city_sel = st.sidebar.multiselect("Filter City", sorted(merged["city"].unique()), default=sorted(merged["city"].unique()))
veh_sel = st.sidebar.multiselect("Vehicle Type", sorted(merged["vehicle_type"].unique()), default=sorted(merged["vehicle_type"].unique()))
view_df = merged[merged["city"].isin(city_sel) & merged["vehicle_type"].isin(veh_sel)]

st.title("🛵 Rapido: Intelligent Mobility Insights — Ride Patterns, Cancellations & Fare Forecasting")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Bookings", f"{len(view_df):,}")
k2.metric("Completion Rate", f"{(view_df['booking_status']=='Completed').mean()*100:.1f}%")
k3.metric("Cancellation Rate", f"{(view_df['booking_status']=='Cancelled').mean()*100:.1f}%")
k4.metric("Outcome Model Acc", f"{metrics['ride_outcome_model']['accuracy']*100:.1f}%")
k5.metric("Fare Model R²", f"{metrics['fare_prediction_model']['r2']:.4f}")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 EDA & Cancellation Heatmaps",
    "🤖 4-Model Evaluation & Feature Importance",
    "⚡ Pre-Booking Ride & Fare Simulator",
    "🚗 Driver Reliability & Allocation Strategy",
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        hourly = view_df.groupby(["hour_of_day", "booking_status"], as_index=False).size()
        st.plotly_chart(
            px.bar(hourly, x="hour_of_day", y="size", color="booking_status", title="Hourly Ride Volume & Outcome Breakdown"),
            use_container_width=True,
        )
    with c2:
        city_heat = (
            view_df.assign(is_cancelled=(view_df["booking_status"] == "Cancelled").astype(int))
            .groupby(["city", "traffic_level"], as_index=False)["is_cancelled"]
            .mean()
        )
        city_heat["cancel_pct"] = (city_heat["is_cancelled"] * 100).round(2)
        st.plotly_chart(
            px.density_heatmap(city_heat, x="traffic_level", y="city", z="cancel_pct", color_continuous_scale="Reds", title="Cancellation Rate (%) Heatmap: City × Traffic Level"),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        sample_scatter = view_df.sample(n=min(2500, len(view_df)), random_state=42)
        st.plotly_chart(
            px.scatter(sample_scatter, x="ride_distance_km", y="booking_value", color="vehicle_type", opacity=0.6, title="Ride Distance (KM) vs Dynamic Booking Value (₹)"),
            use_container_width=True,
        )
    with c4:
        weather_cancel = (
            view_df.assign(is_cancelled=(view_df["booking_status"] == "Cancelled").astype(int))
            .groupby("weather_condition", as_index=False)["is_cancelled"]
            .mean()
        )
        weather_cancel["cancel_pct"] = (weather_cancel["is_cancelled"] * 100).round(2)
        st.plotly_chart(
            px.bar(weather_cancel, x="weather_condition", y="cancel_pct", color="cancel_pct", title="Weather Condition vs Cancellation %"),
            use_container_width=True,
        )

with tab2:
    st.subheader("Unified Performance Across All 4 Required ML Models (80/20 Holdout Test Split)")
    summary_rows = [
        {
            "Model": "1. Ride Outcome Prediction (Multi-Class)",
            "Primary Metric": f"Accuracy: {metrics['ride_outcome_model']['accuracy']*100:.2f}%",
            "Secondary Metric": f"F1: {metrics['ride_outcome_model']['f1_weighted']:.4f} | AUC: {metrics['ride_outcome_model']['roc_auc_ovr']:.4f}",
        },
        {
            "Model": "2. Dynamic Fare Forecasting (Regression)",
            "Primary Metric": f"RMSE: ₹{metrics['fare_prediction_model']['rmse']:.2f} ({metrics['fare_prediction_model']['rmse_pct_of_mean_fare']:.2f}% of mean)",
            "Secondary Metric": f"MAE: ₹{metrics['fare_prediction_model']['mae']:.2f} | R²: {metrics['fare_prediction_model']['r2']:.4f} | Within ±10%: {metrics['fare_prediction_model']['within_10pct_accuracy']:.1f}%",
        },
        {
            "Model": "3. Customer Cancellation Risk (Binary)",
            "Primary Metric": f"Accuracy: {metrics['customer_cancellation_model']['accuracy']*100:.2f}%",
            "Secondary Metric": f"F1: {metrics['customer_cancellation_model']['f1_score']:.4f} | ROC-AUC: {metrics['customer_cancellation_model']['roc_auc']:.4f}",
        },
        {
            "Model": "4. Driver Delay Prediction (Binary)",
            "Primary Metric": f"Accuracy: {metrics['driver_delay_model']['accuracy']*100:.2f}%",
            "Secondary Metric": f"F1: {metrics['driver_delay_model']['f1_score']:.4f} | ROC-AUC: {metrics['driver_delay_model']['roc_auc']:.4f}",
        },
    ]
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    m1, m2 = st.columns(2)
    with m1:
        imp_df = pd.DataFrame(metrics["ride_outcome_model"]["top_features"])
        st.plotly_chart(px.bar(imp_df, x="importance", y="feature", orientation="h", title="Top Permutation Feature Importances (Ride Outcome)"), use_container_width=True)
    with m2:
        cm_df = pd.DataFrame(
            metrics["ride_outcome_model"]["confusion_matrix"],
            index=metrics["ride_outcome_model"]["classes"],
            columns=metrics["ride_outcome_model"]["classes"],
        )
        st.plotly_chart(px.imshow(cm_df, text_auto=True, color_continuous_scale="Blues", title="Ride Outcome Confusion Matrix"), use_container_width=True)

with tab3:
    st.subheader("⚡ Real-Time Pre-Booking Outcome, Dynamic Fare & Intervention Simulator")
    s1, s2, s3, s4 = st.columns(4)
    sim_city = s1.selectbox("City", sorted(merged["city"].unique()))
    sim_veh = s2.selectbox("Vehicle", sorted(merged["vehicle_type"].unique()))
    sim_traffic = s3.selectbox("Traffic Level", ["Low", "Medium", "High", "Very High"])
    sim_weather = s4.selectbox("Weather", sorted(merged["weather_condition"].unique()))

    s5, s6, s7, s8 = st.columns(4)
    sim_dist = s5.slider("Distance (KM)", 1.0, 35.0, 9.5, 0.5)
    sim_hour = s6.slider("Hour of Day", 0, 23, 18)
    sim_surge = s7.slider("Surge Multiplier", 1.0, 2.5, 1.3, 0.1)
    sim_drv_rel = s8.slider("Driver Reliability Score", 20.0, 100.0, 80.0, 1.0)

    pred = predict_single_ride(
        {
            "city": sim_city,
            "vehicle_type": sim_veh,
            "hour_of_day": sim_hour,
            "ride_distance_km": sim_dist,
            "estimated_ride_time_min": round(sim_dist * (4.8 if sim_traffic in ("High", "Very High") else 3.2), 1),
            "base_fare": round(30.0 + sim_dist * (9.5 if sim_veh == "Bike" else (13.5 if sim_veh == "Auto" else 18.5)), 2),
            "surge_multiplier": sim_surge,
            "traffic_level": sim_traffic,
            "weather_condition": sim_weather,
            "Driver_Reliability_Score": sim_drv_rel,
            "delay_rate": round(max(0.0, (100.0 - sim_drv_rel) / 180.0), 3),
        },
        bundle=bundle,
    )
    r1, r2, r3 = st.columns(3)
    r1.metric("Predicted Ride Outcome", pred["predicted_outcome"])
    r2.metric("Forecasted Dynamic Fare", f"₹{pred['predicted_fare_inr']:.2f}")
    r3.metric("Cancellation Risk", f"{pred['outcome_probabilities'].get('Cancelled', 0)*100:.1f}%")
    st.info(f"**Recommended Operational Action:** {pred['operational_intervention']}")
    st.json(pred["outcome_probabilities"])

with tab4:
    st.subheader("Driver Reliability Tiering & Peak Cancellation Windows")
    peak_windows = (
        view_df.assign(is_cancelled=(view_df["booking_status"] == "Cancelled").astype(int))
        .groupby(["city", "hour_of_day"], as_index=False)
        .agg(total_rides=("booking_id", "count"), cancellation_rate=("is_cancelled", "mean"))
        .sort_values("cancellation_rate", ascending=False)
        .head(12)
    )
    peak_windows["cancellation_rate"] = (peak_windows["cancellation_rate"] * 100).round(2)
    st.markdown("#### Top Peak Cancellation City-Hour Windows (Target for 20% Cancellation Reduction)")
    st.dataframe(peak_windows, use_container_width=True, hide_index=True)

    st.markdown("#### Top Reliability-Scored Drivers for Priority Dispatch")
    st.dataframe(
        drivers.sort_values("Driver_Reliability_Score", ascending=False).head(15)[
            ["driver_id", "driver_city", "vehicle_type", "driver_experience_years", "acceptance_rate", "delay_rate", "avg_driver_rating", "Driver_Reliability_Score"]
        ],
        use_container_width=True,
        hide_index=True,
    )
