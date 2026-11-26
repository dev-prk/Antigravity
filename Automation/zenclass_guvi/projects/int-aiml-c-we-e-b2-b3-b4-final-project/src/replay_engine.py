"""Ball-by-Ball Match Replay Engine, Live Scorecard Reconstructor & MCP-Style SQL Tools."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from aws.glue_etl_job import DB_PATH, RAW_JSON_DIR, run_glue_style_etl


class MatchReplayEngine:
    """Maintains ball-by-ball replay cursors and computes live scorecards, strike rates & partnerships."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        if not self.db_path.exists():
            run_glue_style_etl(raw_dir=RAW_JSON_DIR, db_path=self.db_path)
        self.cursors: Dict[str, int] = {}

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def list_matches(self) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT match_id, match_date, event_name, team1, team2, venue, city, winner FROM matches ORDER BY match_date DESC, match_id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def total_deliveries(self, match_id: str) -> int:
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM deliveries WHERE match_id = ?", (match_id,)).fetchone()
        return int(row["cnt"]) if row else 0

    def set_cursor(self, match_id: str, seq_index: int) -> int:
        total = self.total_deliveries(match_id)
        clamped = max(1, min(int(seq_index), total))
        self.cursors[match_id] = clamped
        return clamped

    def advance(self, match_id: str, steps: int = 1) -> int:
        cur = self.cursors.get(match_id, 0)
        return self.set_cursor(match_id, cur + max(1, int(steps)))

    def get_delivery(self, match_id: str, seq_index: int) -> Dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM deliveries WHERE match_id = ? AND seq_index = ?",
                (match_id, int(seq_index)),
            ).fetchone()
        if not row:
            raise KeyError(f"Delivery seq_index={seq_index} not found in match {match_id}")
        return dict(row)

    def get_live_state(self, match_id: str, seq_index: Optional[int] = None) -> Dict[str, Any]:
        seq = int(seq_index if seq_index is not None else self.cursors.get(match_id, 1))
        with self.connect() as conn:
            m_row = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
            if not m_row:
                raise KeyError(f"Match {match_id} not found")
            match_meta = dict(m_row)
            df = pd.read_sql_query(
                "SELECT * FROM deliveries WHERE match_id = ? AND seq_index <= ? ORDER BY seq_index ASC",
                conn,
                params=(match_id, seq),
            )

        if df.empty:
            raise ValueError(f"No deliveries found for match {match_id}")

        latest = df.iloc[-1].to_dict()
        curr_inn = int(latest["innings_num"])
        inn_df = df[df["innings_num"] == curr_inn]

        score_runs = int(inn_df["runs_total"].sum())
        wickets = int(inn_df["is_wicket"].sum())
        legal_balls = int((~inn_df["extras_type"].fillna("").str.contains("wides|noballs")).sum())
        overs_str = f"{legal_balls // 6}.{legal_balls % 6}"
        crr = round(score_runs / max(legal_balls / 6.0, 1 / 6.0), 2)

        target_runs = None
        rrr = None
        runs_needed = None
        balls_remaining = max(0, 120 - legal_balls)
        if curr_inn == 2:
            inn1_runs = int(df[df["innings_num"] == 1]["runs_total"].sum())
            target_runs = inn1_runs + 1
            runs_needed = max(0, target_runs - score_runs)
            rrr = round(runs_needed / max(balls_remaining / 6.0, 1 / 6.0), 2) if balls_remaining > 0 else 0.0

        # Active batter & non-striker stats
        batter_stats = self.tool_get_batter_stats(match_id, str(latest["batter"]), curr_inn, seq)
        non_striker_stats = self.tool_get_batter_stats(match_id, str(latest["non_striker"]), curr_inn, seq)
        bowler_stats = self.tool_get_bowler_stats(match_id, str(latest["bowler"]), curr_inn, seq)

        # Current unbroken partnership since last wicket
        wkt_indices = inn_df.index[inn_df["is_wicket"] == 1].tolist()
        since_wkt_df = inn_df.loc[wkt_indices[-1] + 1:] if wkt_indices else inn_df
        part_runs = int(since_wkt_df["runs_total"].sum())
        part_balls = int((~since_wkt_df["extras_type"].fillna("").str.contains("wides")).sum())

        # Over-by-over worm progression
        worm = (
            df.groupby(["innings_num", "batting_team", "over_num"], as_index=False)["runs_total"]
            .sum()
            .sort_values(["innings_num", "over_num"])
        )
        worm["cumulative_runs"] = worm.groupby("innings_num")["runs_total"].cumsum()

        return {
            "match_meta": match_meta,
            "seq_index": seq,
            "total_match_deliveries": self.total_deliveries(match_id),
            "innings_num": curr_inn,
            "batting_team": latest["batting_team"],
            "bowling_team": latest["bowling_team"],
            "score": f"{score_runs}/{wickets}",
            "score_runs": score_runs,
            "wickets": wickets,
            "overs": overs_str,
            "current_run_rate": crr,
            "target": target_runs,
            "runs_needed": runs_needed,
            "balls_remaining": balls_remaining,
            "required_run_rate": rrr,
            "latest_delivery": latest,
            "striker": batter_stats,
            "non_striker": non_striker_stats,
            "bowler": bowler_stats,
            "current_partnership": {"runs": part_runs, "balls": part_balls},
            "over_worm": worm.to_dict(orient="records"),
        }

    # ------------------------------------------------------------------
    # MCP-Style Analytical SQL Tools Over Stats Database
    # ------------------------------------------------------------------
    def tool_get_batter_stats(self, match_id: str, batter: str, innings_num: int, up_to_seq: int) -> Dict[str, Any]:
        with self.connect() as conn:
            df = pd.read_sql_query(
                """
                SELECT runs_batter, extras_type FROM deliveries
                WHERE match_id = ? AND innings_num = ? AND batter = ? AND seq_index <= ?
                """,
                conn,
                params=(match_id, innings_num, batter, up_to_seq),
            )
        runs = int(df["runs_batter"].sum()) if not df.empty else 0
        balls = int((~df["extras_type"].fillna("").str.contains("wides")).sum()) if not df.empty else 0
        fours = int((df["runs_batter"] == 4).sum()) if not df.empty else 0
        sixes = int((df["runs_batter"] == 6).sum()) if not df.empty else 0
        sr = round((runs / balls) * 100.0, 1) if balls > 0 else 0.0
        return {"name": batter, "runs": runs, "balls": balls, "fours": fours, "sixes": sixes, "strike_rate": sr}

    def tool_get_bowler_stats(self, match_id: str, bowler: str, innings_num: int, up_to_seq: int) -> Dict[str, Any]:
        with self.connect() as conn:
            df = pd.read_sql_query(
                """
                SELECT runs_batter, runs_extras, extras_type, is_wicket, wicket_kind FROM deliveries
                WHERE match_id = ? AND innings_num = ? AND bowler = ? AND seq_index <= ?
                """,
                conn,
                params=(match_id, innings_num, bowler, up_to_seq),
            )
        if df.empty:
            return {"name": bowler, "overs": "0.0", "runs_conceded": 0, "wickets": 0, "economy": 0.0}
        legal = int((~df["extras_type"].fillna("").str.contains("wides|noballs")).sum())
        byes_legbyes = df["extras_type"].fillna("").str.contains("byes|legbyes")
        conceded = int(df["runs_batter"].sum() + df.loc[~byes_legbyes, "runs_extras"].sum())
        bowler_wkts = int(((df["is_wicket"] == 1) & (~df["wicket_kind"].fillna("").isin(["run out", "retired hurt"]))).sum())
        econ = round(conceded / max(legal / 6.0, 1 / 6.0), 2)
        return {
            "name": bowler,
            "overs": f"{legal // 6}.{legal % 6}",
            "runs_conceded": conceded,
            "wickets": bowler_wkts,
            "economy": econ,
        }

    def tool_top_performers(self, match_id: str, up_to_seq: int) -> Dict[str, Any]:
        with self.connect() as conn:
            top_bat = pd.read_sql_query(
                """
                SELECT batter, batting_team, SUM(runs_batter) AS runs,
                       SUM(CASE WHEN COALESCE(extras_type, '') NOT LIKE '%wides%' THEN 1 ELSE 0 END) AS balls,
                       SUM(CASE WHEN runs_batter = 4 THEN 1 ELSE 0 END) AS fours,
                       SUM(CASE WHEN runs_batter = 6 THEN 1 ELSE 0 END) AS sixes
                FROM deliveries WHERE match_id = ? AND seq_index <= ?
                GROUP BY batter, batting_team ORDER BY runs DESC, balls ASC LIMIT 5
                """,
                conn,
                params=(match_id, up_to_seq),
            )
            top_bowl = pd.read_sql_query(
                """
                SELECT bowler, bowling_team,
                       SUM(CASE WHEN is_wicket = 1 AND COALESCE(wicket_kind, '') NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) AS wickets,
                       SUM(runs_total) AS runs_conceded,
                       COUNT(*) AS deliveries_bowled
                FROM deliveries WHERE match_id = ? AND seq_index <= ?
                GROUP BY bowler, bowling_team ORDER BY wickets DESC, runs_conceded ASC LIMIT 5
                """,
                conn,
                params=(match_id, up_to_seq),
            )
        return {
            "top_batters": top_bat.to_dict(orient="records"),
            "top_bowlers": top_bowl.to_dict(orient="records"),
        }

    def tool_query_readonly_sql(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cleaned = sql.strip()
        if not cleaned.upper().startswith(("SELECT", "WITH")):
            raise ValueError("Only read-only SELECT queries are permitted on the stats DB.")
        with self.connect() as conn:
            return pd.read_sql_query(cleaned, conn, params=params).to_dict(orient="records")
