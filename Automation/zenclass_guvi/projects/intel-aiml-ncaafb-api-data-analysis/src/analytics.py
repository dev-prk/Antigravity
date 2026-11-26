"""Pre-built SQL Analytics Queries satisfying all GUVI NCAAFB specification questions."""

from __future__ import annotations

from typing import Dict, Tuple
import pandas as pd

from src.database import NCAAFBDatabase


ANALYTICAL_SQL_QUERIES: Dict[str, Tuple[str, str]] = {
    "1. Top-5 Ranked Teams Across Seasons": (
        "Ranks programs by best average poll rank and cumulative poll points across all tracked seasons.",
        """
        SELECT
            t.market || ' ' || t.name AS team_name,
            c.alias AS conference,
            COUNT(DISTINCT r.season_id) AS seasons_ranked,
            ROUND(AVG(r.rank), 2) AS avg_poll_rank,
            MIN(r.rank) AS peak_rank,
            SUM(r.points) AS total_poll_points,
            SUM(r.fp_votes) AS total_first_place_votes
        FROM Rankings r
        JOIN Teams t ON r.team_id = t.team_id
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        GROUP BY t.team_id
        ORDER BY avg_poll_rank ASC, total_poll_points DESC
        LIMIT 5;
        """,
    ),
    "2. Average Ranking Points per Team by Season": (
        "Computes season-by-season average AP Poll points, wins, and best rank per program.",
        """
        SELECT
            s.year AS season_year,
            t.market || ' ' || t.name AS team_name,
            c.alias AS conference,
            ROUND(AVG(r.points), 1) AS avg_poll_points,
            MIN(r.rank) AS best_rank,
            MAX(r.wins) AS season_wins,
            MAX(r.losses) AS season_losses
        FROM Rankings r
        JOIN Seasons s ON r.season_id = s.season_id
        JOIN Teams t ON r.team_id = t.team_id
        LEFT JOIN Conferences c ON t.conference_id = c.conference_id
        GROUP BY s.year, t.team_id
        ORDER BY s.year DESC, avg_poll_points DESC;
        """,
    ),
    "3. First-Place Votes Distribution Across Weeks": (
        "Tracks weekly AP Top-25 first-place votes earned by top contenders.",
        """
        SELECT
            s.year AS season_year,
            r.week,
            t.market || ' ' || t.name AS team_name,
            r.rank,
            r.fp_votes AS first_place_votes,
            r.points
        FROM Rankings r
        JOIN Seasons s ON r.season_id = s.season_id
        JOIN Teams t ON r.team_id = t.team_id
        WHERE r.fp_votes > 0
        ORDER BY s.year DESC, r.week ASC, r.fp_votes DESC;
        """,
    ),
    "4. Multi-Season Players Remaining on the Same Team": (
        "Identifies loyal multi-season contributors on the same roster and aggregates career production.",
        """
        SELECT
            p.first_name || ' ' || p.last_name AS player_name,
            p.position,
            p.eligibility,
            t.market || ' ' || t.name AS team_name,
            COUNT(DISTINCT ps.season_id) AS seasons_on_team,
            SUM(ps.games_played) AS career_games,
            SUM(ps.rushing_yards) AS career_rushing_yards,
            SUM(ps.receiving_yards) AS career_receiving_yards,
            SUM(ps.rushing_touchdowns + ps.receiving_touchdowns) AS total_touchdowns
        FROM Player_Statistics ps
        JOIN Players p ON ps.player_id = p.player_id
        JOIN Teams t ON ps.team_id = t.team_id
        GROUP BY ps.player_id, ps.team_id
        HAVING COUNT(DISTINCT ps.season_id) >= 2
        ORDER BY seasons_on_team DESC, (career_rushing_yards + career_receiving_yards) DESC
        LIMIT 25;
        """,
    ),
    "5. Player Position & Eligibility Distribution by Conference": (
        "Summarizes roster composition across positions and conferences.",
        """
        SELECT
            c.alias AS conference,
            p.position,
            COUNT(p.player_id) AS player_count,
            ROUND(AVG(p.height), 1) AS avg_height_in,
            ROUND(AVG(p.weight), 1) AS avg_weight_lbs
        FROM Players p
        JOIN Teams t ON p.team_id = t.team_id
        JOIN Conferences c ON t.conference_id = c.conference_id
        GROUP BY c.alias, p.position
        ORDER BY c.alias ASC, player_count DESC;
        """,
    ),
    "6. Venue Surface, Roof Type & Conference Capacity Comparison": (
        "Compares stadium capacity and playing surfaces across conferences.",
        """
        SELECT
            c.name AS conference_name,
            v.surface,
            v.roof_type,
            COUNT(v.venue_id) AS stadium_count,
            ROUND(AVG(v.capacity), 0) AS avg_capacity,
            MAX(v.capacity) AS max_capacity
        FROM Teams t
        JOIN Venues v ON t.venue_id = v.venue_id
        JOIN Conferences c ON t.conference_id = c.conference_id
        GROUP BY c.name, v.surface, v.roof_type
        ORDER BY avg_capacity DESC;
        """,
    ),
}


def run_named_query(db: NCAAFBDatabase, query_title: str) -> pd.DataFrame:
    if query_title not in ANALYTICAL_SQL_QUERIES:
        raise KeyError(f"Unknown analytical query: {query_title}")
    _, sql = ANALYTICAL_SQL_QUERIES[query_title]
    return db.query_df(sql)
