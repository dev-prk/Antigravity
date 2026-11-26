"""Interactive Streamlit Dashboard for Traffic Violations Insight System."""

from __future__ import annotations

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

from src.preprocessing import DEFAULT_DB_PATH, DEFAULT_REPORT_PATH, run_pipeline

st.set_page_config(
    page_title="Traffic Violations Insight System",
    page_icon="🚓",
    layout="wide",
)


@st.cache_data(show_spinner="Cleaning & indexing Traffic Violations dataset...")
def load_cleaned_data():
    df, audit = run_pipeline()
    return df, audit


df, audit = load_cleaned_data()

st.sidebar.title("🚓 Traffic Filters")
st.sidebar.caption(f"Indexed {len(df):,} violations ({audit['unique_seq_ids']:,} unique stops)")

min_dt = pd.to_datetime(df["Stop_Datetime"]).min().date()
max_dt = pd.to_datetime(df["Stop_Datetime"]).max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)

sub_sel = st.sidebar.multiselect("District / SubAgency", sorted(df["SubAgency"].unique()), default=sorted(df["SubAgency"].unique()))
cat_sel = st.sidebar.multiselect("Violation Category", sorted(df["Violation_Category"].unique()), default=sorted(df["Violation_Category"].unique()))
veh_sel = st.sidebar.multiselect("Vehicle Type", sorted(df["VehicleType"].unique()), default=sorted(df["VehicleType"].unique()))
gender_sel = st.sidebar.multiselect("Driver Gender", sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique()))
race_sel = st.sidebar.multiselect("Driver Race", sorted(df["Race"].unique()), default=sorted(df["Race"].unique()))
dedup_stops = st.sidebar.checkbox("Deduplicate Multi-Charge Stops (1 row per SeqID)", value=False)

filtered = df[
    df["SubAgency"].isin(sub_sel)
    & df["Violation_Category"].isin(cat_sel)
    & df["VehicleType"].isin(veh_sel)
    & df["Gender"].isin(gender_sel)
    & df["Race"].isin(race_sel)
].copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered = filtered[(pd.to_datetime(filtered["Stop_Datetime"]) >= d_start) & (pd.to_datetime(filtered["Stop_Datetime"]) < d_end)]

if dedup_stops:
    filtered = filtered.drop_duplicates(subset=["SeqID"])

st.title("🚓 Traffic Violations Insight System: EDA, Cleaning & Interactive Dashboard")
st.markdown("Actionable road-safety intelligence, corridor hotspot detection, temporal trends, and patrol resource analytics.")

# KPI Summary Row
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Violations", f"{len(filtered):,}")
k2.metric("Accident-Linked", f"{int(filtered['Accident'].sum()):,}", f"{filtered['Accident'].mean()*100:.1f}%" if len(filtered) else "0%")
k3.metric("Alcohol-Involved", f"{int(filtered['Alcohol'].sum()):,}")
k4.metric("Top High-Risk Corridor", filtered["Location"].mode().iloc[0][:24] if not filtered.empty else "N/A")
k5.metric("Top Vehicle Make", filtered["Make"].mode().iloc[0] if not filtered.empty else "N/A")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Geographic Hotspots",
    "⏰ Temporal & Violation Trends",
    "🚗 Vehicles, Demographics & Searches",
    "🧹 Data Quality & Multi-Charge Audit",
    "🗄️ SQL Analytics Workbench",
])

with tab1:
    geo_df = filtered.dropna(subset=["Latitude", "Longitude"]).head(4000)
    if not geo_df.empty:
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                geo_df,
                lat="Latitude",
                lon="Longitude",
                color="Violation_Category",
                hover_name="Location",
                hover_data=["SubAgency", "Violation Type", "Make", "Model", "Accident"],
                zoom=9.6,
                height=520,
                map_style="open-street-map",
                title="Traffic Violation Coordinates & Corridor Hotspots",
            )
        else:
            fig_map = px.scatter_mapbox(
                geo_df,
                lat="Latitude",
                lon="Longitude",
                color="Violation_Category",
                hover_name="Location",
                hover_data=["SubAgency", "Violation Type", "Make", "Model", "Accident"],
                zoom=9.6,
                height=520,
                mapbox_style="open-street-map",
                title="Traffic Violation Coordinates & Corridor Hotspots",
            )
        st.plotly_chart(fig_map, use_container_width=True)

    loc_counts = filtered.groupby("Location", as_index=False).agg(
        total_stops=("SeqID", "count"),
        accidents=("Accident", "sum"),
        alcohol_cases=("Alcohol", "sum"),
    ).sort_values("total_stops", ascending=False).head(10)
    st.subheader("Top 10 High-Risk Corridors")
    st.dataframe(loc_counts, use_container_width=True, hide_index=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        cat_counts = filtered["Violation_Category"].value_counts().reset_index()
        cat_counts.columns = ["Violation_Category", "Count"]
        st.plotly_chart(
            px.bar(cat_counts, x="Count", y="Violation_Category", orientation="h", color="Violation_Category", title="Violations by Normalized Category"),
            use_container_width=True,
        )
    with c2:
        heat = filtered.groupby(["Day_Of_Week", "Hour_Of_Stop"]).size().reset_index(name="Stops")
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        fig_heat = px.density_heatmap(
            heat,
            x="Hour_Of_Stop",
            y="Day_Of_Week",
            z="Stops",
            category_orders={"Day_Of_Week": day_order},
            color_continuous_scale="YlOrRd",
            title="Enforcement Volume Heatmap (Hour of Day × Day of Week)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    monthly = (
        filtered.assign(YearMonth=pd.to_datetime(filtered["Stop_Datetime"]).dt.to_period("M").astype(str))
        .groupby("YearMonth", as_index=False)
        .agg(Violations=("SeqID", "count"), Accidents=("Accident", "sum"))
        .sort_values("YearMonth")
    )
    st.plotly_chart(px.line(monthly, x="YearMonth", y=["Violations", "Accidents"], markers=True, title="Monthly Violations & Accident Trend"), use_container_width=True)

with tab3:
    v1, v2 = st.columns(2)
    with v1:
        top_mm = (
            filtered.assign(Make_Model=filtered["Make"] + " " + filtered["Model"])
            ["Make_Model"].value_counts().head(12).reset_index()
        )
        top_mm.columns = ["Make_Model", "Count"]
        st.plotly_chart(px.bar(top_mm, x="Make_Model", y="Count", color="Count", title="Top 12 Vehicle Makes & Models Involved"), use_container_width=True)
    with v2:
        demo = filtered.groupby(["Race", "Violation Type"], as_index=False).size()
        st.plotly_chart(px.bar(demo, x="Race", y="size", color="Violation Type", barmode="group", title="Outcome Breakdown Across Driver Demographics"), use_container_width=True)

    sev_df = pd.DataFrame({
        "Safety Indicator": ["Accident", "Property Damage", "Personal Injury", "Fatal", "Belts Citation", "Alcohol", "Search Conducted"],
        "Incidents": [
            int(filtered["Accident"].sum()),
            int(filtered["Property Damage"].sum()),
            int(filtered["Personal Injury"].sum()),
            int(filtered["Fatal"].sum()),
            int(filtered["Belts"].sum()),
            int(filtered["Alcohol"].sum()),
            int(filtered["Search Conducted"].sum()),
        ],
    })
    st.plotly_chart(px.bar(sev_df, x="Safety Indicator", y="Incidents", color="Safety Indicator", title="Incident Severity & Search Breakdown"), use_container_width=True)

with tab4:
    st.subheader("43-Column Cleaning & Quality Verification Summary")
    st.json(audit)
    if DEFAULT_REPORT_PATH.exists():
        st.markdown(DEFAULT_REPORT_PATH.read_text(encoding="utf-8"))

with tab5:
    st.subheader("SQLite Analytical Query Runner (`traffic_violations` table)")
    preset_sql = st.selectbox(
        "Select Analytical SQL Query",
        [
            "SELECT SubAgency, COUNT(*) AS total_violations, SUM(Accident) AS accidents, ROUND(AVG(Accident)*100, 2) AS accident_pct FROM traffic_violations GROUP BY SubAgency ORDER BY total_violations DESC;",
            "SELECT Violation_Category, SUM(\"Personal Injury\") AS injuries, SUM(\"Property Damage\") AS prop_damage, COUNT(*) AS total FROM traffic_violations GROUP BY Violation_Category ORDER BY injuries DESC;",
            "SELECT SeqID, COUNT(*) AS charges_count, GROUP_CONCAT(Violation_Category, ' | ') AS violation_mix FROM traffic_violations GROUP BY SeqID HAVING charges_count > 1 ORDER BY charges_count DESC LIMIT 20;",
        ],
    )
    sql_text = st.text_area("SQL Query (Read-Only SELECT)", value=preset_sql, height=100)
    if sql_text.strip().upper().startswith("SELECT"):
        with sqlite3.connect(str(DEFAULT_DB_PATH)) as conn:
            q_df = pd.read_sql_query(sql_text, conn)
        st.dataframe(q_df, use_container_width=True, hide_index=True)
    else:
        st.error("Only SELECT queries are permitted.")
