"""Interactive 7-Page Streamlit Platform for NCAAFB Sports Analytics."""

from __future__ import annotations

import os
import plotly.express as px
import streamlit as st

from src.analytics import ANALYTICAL_SQL_QUERIES, run_named_query
from src.api_client import ingest_live_or_seed
from src.database import NCAAFBDatabase

st.set_page_config(
    page_title="NCAAFB Sports Analytics Platform",
    page_icon="🏈",
    layout="wide",
)


@st.cache_resource
def get_db() -> NCAAFBDatabase:
    db = NCAAFBDatabase()
    ingest_live_or_seed(db)
    return db


db = get_db()

st.sidebar.title("🏈 NCAAFB Analytics")
st.sidebar.caption("Real-Time Sportradar API + Relational SQL Engine")

page = st.sidebar.radio(
    "Navigate Module",
    [
        "1. Home Dashboard",
        "2. Teams Explorer",
        "3. Players Explorer",
        "4. Season & Schedule Viewer",
        "5. Rankings Table (AP Poll)",
        "6. Venue Directory",
        "7. Coaches & SQL Insights",
    ],
)

with st.sidebar.expander("🔌 Sportradar API Sync"):
    api_key_input = st.text_input(
        "SPORTRADAR_API_KEY",
        value=os.getenv("SPORTRADAR_API_KEY", ""),
        type="password",
        help="Optional: Enter a live Sportradar NCAAFB v7 key to refresh directly from live endpoints.",
    )
    if st.button("Sync / Refresh Database", use_container_width=True):
        result = ingest_live_or_seed(db, api_key=api_key_input or None, force_reseed=True)
        st.success(f"Synced ({result['source']})")

counts = db.table_counts()

if page == "1. Home Dashboard":
    st.title("🏈 NCAA Football Real-Time Sports Analytics Platform")
    st.markdown(
        "Unified relational SQL warehouse and interactive exploration suite over NCAAFB **Teams, Venues, "
        "Conferences, Seasons, Schedules, Players, Multi-Season Statistics, Weekly Poll Rankings, and Coaches**."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("FBS Teams", counts["Teams"])
    c2.metric("Active Players", counts["Players"])
    c3.metric("Seasons Tracked", counts["Seasons"])
    c4.metric("Ranking Snapshots", counts["Rankings"])
    c5.metric("Scheduled Matchups", counts["Schedules"])

    col_a, col_b = st.columns(2)
    with col_a:
        top5 = run_named_query(db, "1. Top-5 Ranked Teams Across Seasons")
        fig = px.bar(
            top5,
            x="team_name",
            y="total_poll_points",
            color="conference",
            text="avg_poll_rank",
            title="Top-5 FBS Programs by Cumulative AP Poll Points (Label = Avg Rank)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        conf_df = db.query_df(
            """
            SELECT c.alias AS conference, COUNT(t.team_id) AS teams, SUM(t.championships_won) AS championships
            FROM Teams t JOIN Conferences c ON t.conference_id = c.conference_id
            GROUP BY c.alias ORDER BY championships DESC
            """
        )
        fig2 = px.pie(conf_df, names="conference", values="championships", hole=0.4, title="National Championships Share by Conference")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Normalized SQL Warehouse Inventory (8 Core Spec Tables + Schedules)")
    st.dataframe(
        [{"Table Name": k, "Row Count": v} for k, v in counts.items()],
        use_container_width=True,
        hide_index=True,
    )

elif page == "2. Teams Explorer":
    st.title("🏟️ Teams Explorer & Roster Viewer")
    teams_df = db.query_df(
        """
        SELECT t.team_id, t.market, t.name, t.alias, t.founded, t.mascot, t.fight_song,
               t.championships_won, c.alias AS conference, t.division_id,
               v.name AS stadium, v.city, v.state, v.capacity
        FROM Teams t
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        LEFT JOIN Venues v ON t.venue_id = v.venue_id
        ORDER BY t.championships_won DESC, t.market ASC
        """
    )
    f1, f2, f3 = st.columns(3)
    conf_sel = f1.multiselect("Conference", sorted(teams_df["conference"].dropna().unique()), default=sorted(teams_df["conference"].dropna().unique()))
    state_sel = f2.multiselect("State", sorted(teams_df["state"].dropna().unique()))
    search_q = f3.text_input("Search Team / Mascot")

    filtered = teams_df[teams_df["conference"].isin(conf_sel)]
    if state_sel:
        filtered = filtered[filtered["state"].isin(state_sel)]
    if search_q:
        mask = filtered["market"].str.contains(search_q, case=False) | filtered["name"].str.contains(search_q, case=False) | filtered["mascot"].str.contains(search_q, case=False)
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    if not filtered.empty:
        selected_team = st.selectbox(
            "Inspect Full Team Roster",
            options=filtered["team_id"].tolist(),
            format_func=lambda tid: f"{filtered.loc[filtered['team_id']==tid, 'market'].iloc[0]} {filtered.loc[filtered['team_id']==tid, 'name'].iloc[0]}",
        )
        roster_df = db.query_df(
            """
            SELECT player_id, first_name || ' ' || last_name AS full_name, position, eligibility,
                   status, height AS height_in, weight AS weight_lbs, birth_place
            FROM Players WHERE team_id = ? ORDER BY position, last_name
            """,
            (selected_team,),
        )
        st.subheader(f"Active Roster ({len(roster_df)} Players)")
        st.dataframe(roster_df, use_container_width=True, hide_index=True)

elif page == "3. Players Explorer":
    st.title("🏃 Players Explorer & Multi-Season Performance")
    players_df = db.query_df(
        """
        SELECT p.player_id, p.first_name || ' ' || p.last_name AS player_name, p.position,
               p.eligibility, p.status, p.height, p.weight, p.birth_place,
               t.market || ' ' || t.name AS team_name, c.alias AS conference,
               COALESCE(SUM(ps.games_played), 0) AS career_games,
               COALESCE(SUM(ps.rushing_yards), 0) AS rushing_yards,
               COALESCE(SUM(ps.rushing_touchdowns), 0) AS rushing_tds,
               COALESCE(SUM(ps.receiving_yards), 0) AS receiving_yards,
               COALESCE(SUM(ps.receiving_touchdowns), 0) AS receiving_tds,
               COALESCE(SUM(ps.kick_return_yards), 0) AS kick_return_yards,
               COALESCE(SUM(ps.fumbles), 0) AS fumbles
        FROM Players p
        JOIN Teams t ON p.team_id = t.team_id
        JOIN Conferences c ON t.conference_id = c.conference_id
        LEFT JOIN Player_Statistics ps ON p.player_id = ps.player_id
        GROUP BY p.player_id
        ORDER BY (rushing_yards + receiving_yards) DESC
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    pos_filter = c1.multiselect("Position", sorted(players_df["position"].unique()), default=["QB", "RB", "WR", "TE"])
    elig_filter = c2.multiselect("Eligibility", sorted(players_df["eligibility"].unique()), default=sorted(players_df["eligibility"].unique()))
    status_filter = c3.multiselect("Status", sorted(players_df["status"].unique()), default=sorted(players_df["status"].unique()))
    name_q = c4.text_input("Player Search")

    view = players_df[
        players_df["position"].isin(pos_filter or players_df["position"].unique())
        & players_df["eligibility"].isin(elig_filter or players_df["eligibility"].unique())
        & players_df["status"].isin(status_filter or players_df["status"].unique())
    ]
    if name_q:
        view = view[view["player_name"].str.contains(name_q, case=False)]

    st.dataframe(view, use_container_width=True, hide_index=True)

    if not view.empty:
        sel_pid = st.selectbox(
            "Select Player for Season-by-Season Progression",
            options=view["player_id"].tolist(),
            format_func=lambda pid: f"{view.loc[view['player_id']==pid, 'player_name'].iloc[0]} ({view.loc[view['player_id']==pid, 'position'].iloc[0]} - {view.loc[view['player_id']==pid, 'team_name'].iloc[0]})",
        )
        p_stats = db.query_df(
            """
            SELECT s.year AS season, ps.games_played, ps.games_started,
                   ps.rushing_yards, ps.rushing_touchdowns, ps.receiving_yards,
                   ps.receiving_touchdowns, ps.kick_return_yards, ps.fumbles
            FROM Player_Statistics ps JOIN Seasons s ON ps.season_id = s.season_id
            WHERE ps.player_id = ? ORDER BY s.year ASC
            """,
            (sel_pid,),
        )
        st.plotly_chart(
            px.bar(p_stats, x="season", y=["rushing_yards", "receiving_yards", "kick_return_yards"], barmode="group", title="Multi-Season Yardage Breakdown"),
            use_container_width=True,
        )

elif page == "4. Season & Schedule Viewer":
    st.title("📅 Multi-Season Schedule & Matchup Results")
    seasons_df = db.query_df("SELECT * FROM Seasons ORDER BY year DESC")
    st.dataframe(seasons_df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    year_sel = c1.selectbox("Season Year", seasons_df["year"].tolist())
    week_opts = db.query_df(
        "SELECT DISTINCT sc.week FROM Schedules sc JOIN Seasons s ON sc.season_id = s.season_id WHERE s.year = ? ORDER BY sc.week",
        (int(year_sel),),
    )["week"].tolist()
    week_sel = c2.multiselect("Week Filter", week_opts, default=week_opts)

    sched_df = db.query_df(
        """
        SELECT sc.week, sc.scheduled_date,
               ht.market || ' ' || ht.name AS home_team,
               sc.home_points,
               at.market || ' ' || at.name AS away_team,
               sc.away_points,
               v.name AS stadium, v.city || ', ' || v.state AS location,
               sc.attendance, sc.status
        FROM Schedules sc
        JOIN Seasons s ON sc.season_id = s.season_id
        JOIN Teams ht ON sc.home_team_id = ht.team_id
        JOIN Teams at ON sc.away_team_id = at.team_id
        LEFT JOIN Venues v ON sc.venue_id = v.venue_id
        WHERE s.year = ?
        ORDER BY sc.week ASC, sc.attendance DESC
        """,
        (int(year_sel),),
    )
    if week_sel:
        sched_df = sched_df[sched_df["week"].isin(week_sel)]
    st.dataframe(sched_df, use_container_width=True, hide_index=True)

elif page == "5. Rankings Table (AP Poll)":
    st.title("🏆 Weekly AP Top-25 Poll Rankings & Trends")
    seasons_df = db.query_df("SELECT year FROM Seasons ORDER BY year DESC")
    col1, col2 = st.columns(2)
    yr = col1.selectbox("Select Season", seasons_df["year"].tolist())
    wk_list = db.query_df(
        "SELECT DISTINCT r.week FROM Rankings r JOIN Seasons s ON r.season_id = s.season_id WHERE s.year = ? ORDER BY r.week DESC",
        (int(yr),),
    )["week"].tolist()
    wk = col2.selectbox("Select Poll Week", wk_list)

    rnk_df = db.query_df(
        """
        SELECT r.rank, r.prev_rank,
               CASE WHEN r.prev_rank IS NULL THEN 'NEW'
                    WHEN r.prev_rank > r.rank THEN '+' || CAST(r.prev_rank - r.rank AS TEXT)
                    WHEN r.prev_rank < r.rank THEN CAST(r.prev_rank - r.rank AS TEXT)
                    ELSE '0' END AS movement,
               t.market || ' ' || t.name AS team_name,
               c.alias AS conference,
               r.wins || '-' || r.losses AS record,
               r.points, r.fp_votes AS first_place_votes
        FROM Rankings r
        JOIN Seasons s ON r.season_id = s.season_id
        JOIN Teams t ON r.team_id = t.team_id
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        WHERE s.year = ? AND r.week = ?
        ORDER BY r.rank ASC
        """,
        (int(yr), int(wk)),
    )
    st.dataframe(rnk_df, use_container_width=True, hide_index=True)

    trend_df = db.query_df(
        """
        SELECT r.week, t.market || ' ' || t.name AS team_name, r.rank, r.points
        FROM Rankings r
        JOIN Seasons s ON r.season_id = s.season_id
        JOIN Teams t ON r.team_id = t.team_id
        WHERE s.year = ? AND r.rank <= 8
        ORDER BY r.week ASC
        """,
        (int(yr),),
    )
    fig = px.line(trend_df, x="week", y="points", color="team_name", markers=True, title=f"{yr} Weekly Poll Points Trajectory (Top Contenders)")
    st.plotly_chart(fig, use_container_width=True)

elif page == "6. Venue Directory":
    st.title("🗺️ NCAAFB Stadium & Venue Directory")
    venues_df = db.query_df(
        """
        SELECT v.venue_id, v.name AS stadium_name, t.market || ' ' || t.name AS home_team,
               c.alias AS conference, v.city, v.state, v.capacity, v.surface, v.roof_type,
               v.latitude, v.longitude
        FROM Venues v
        LEFT JOIN Teams t ON t.venue_id = v.venue_id
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        ORDER BY v.capacity DESC
        """
    )
    c1, c2 = st.columns(2)
    surf_sel = c1.multiselect("Playing Surface", sorted(venues_df["surface"].unique()), default=sorted(venues_df["surface"].unique()))
    roof_sel = c2.multiselect("Roof Type", sorted(venues_df["roof_type"].unique()), default=sorted(venues_df["roof_type"].unique()))
    v_filtered = venues_df[venues_df["surface"].isin(surf_sel) & venues_df["roof_type"].isin(roof_sel)]

    fig_map = px.scatter_geo(
        v_filtered,
        lat="latitude",
        lon="longitude",
        size="capacity",
        color="conference",
        hover_name="stadium_name",
        hover_data=["home_team", "city", "state", "capacity", "surface", "roof_type"],
        scope="usa",
        title="FBS Stadiums Across the United States (Sized by Capacity)",
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.dataframe(v_filtered, use_container_width=True, hide_index=True)

elif page == "7. Coaches & SQL Insights":
    st.title("📋 Coaching Staff Directory & Analytical SQL Workbench")
    coaches_df = db.query_df(
        """
        SELECT co.coach_id, co.full_name, co.position, t.market || ' ' || t.name AS team_name, c.alias AS conference
        FROM Coaches co
        JOIN Teams t ON co.team_id = t.team_id
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        ORDER BY CASE WHEN co.position='Head Coach' THEN 0 ELSE 1 END, t.market ASC
        """
    )
    pos_f = st.multiselect("Coach Role Filter", sorted(coaches_df["position"].unique()), default=["Head Coach"])
    st.dataframe(coaches_df[coaches_df["position"].isin(pos_f or coaches_df["position"].unique())], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🔎 Pre-Built Analytical SQL Queries (GUVI Spec Questions)")
    q_choice = st.selectbox("Select Analytical Question", list(ANALYTICAL_SQL_QUERIES.keys()))
    desc, raw_sql = ANALYTICAL_SQL_QUERIES[q_choice]
    st.caption(desc)
    with st.expander("View SQL Query", expanded=False):
        st.code(raw_sql.strip(), language="sql")
    res_df = run_named_query(db, q_choice)
    st.dataframe(res_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Query Result CSV",
        data=res_df.to_csv(index=False).encode("utf-8"),
        file_name="ncaafb_query_result.csv",
        mime="text/csv",
    )
