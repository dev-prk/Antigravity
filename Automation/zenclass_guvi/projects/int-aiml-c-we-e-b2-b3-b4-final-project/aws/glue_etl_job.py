"""AWS S3 Raw Cricsheet Ingestion & AWS Glue ETL Flattening Pipeline (with Local SQLite/Parquet Support)."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_JSON_DIR = BASE_DIR / "data" / "raw_cricsheet"
PARQUET_DIR = BASE_DIR / "data" / "parquet"
DB_PATH = BASE_DIR / "data" / "cricket_stats.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def upload_raw_json_to_s3(raw_dir: Path = RAW_JSON_DIR, bucket: Optional[str] = None, prefix: str = "raw/cricsheet/") -> Dict[str, Any]:
    """Uploads raw Cricsheet JSON files to S3 when AWS credentials & bucket are configured (never hardcodes keys)."""
    s3_bucket = bucket or os.getenv("CRICSHEET_S3_BUCKET", "")
    files = sorted(raw_dir.glob("*.json"))
    if not s3_bucket:
        return {"mode": "local_staging", "files_ready": len(files), "bucket": None}

    import boto3  # Imported lazily when AWS S3 is active
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
    for fp in files:
        s3.upload_file(str(fp), s3_bucket, f"{prefix.rstrip('/')}/{fp.name}")
    return {"mode": "aws_s3", "files_uploaded": len(files), "bucket": s3_bucket}


def flatten_cricsheet_match(json_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Flattens a single nested Cricsheet ball-by-ball JSON into matches, players, deliveries, and partnerships."""
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    info = payload.get("info", {})
    match_id = json_path.stem
    teams = info.get("teams", ["Team A", "Team B"])
    outcome = info.get("outcome", {})
    by_dict = outcome.get("by", {})

    match_row = {
        "match_id": match_id,
        "match_date": (info.get("dates") or ["Unknown"])[0],
        "event_name": (info.get("event") or {}).get("name", "T20 League"),
        "team1": teams[0] if len(teams) > 0 else "Team A",
        "team2": teams[1] if len(teams) > 1 else "Team B",
        "venue": info.get("venue", "Unknown Venue"),
        "city": info.get("city", "Unknown City"),
        "toss_winner": (info.get("toss") or {}).get("winner", ""),
        "toss_decision": (info.get("toss") or {}).get("decision", ""),
        "winner": outcome.get("winner", outcome.get("result", "No Result")),
        "win_by_runs": int(by_dict.get("runs", 0)),
        "win_by_wickets": int(by_dict.get("wickets", 0)),
        "player_of_match": ", ".join(info.get("player_of_match", [])),
        "overs_limit": int(info.get("overs", 20)),
    }

    registry = (info.get("registry") or {}).get("people", {})
    player_rows: List[Dict[str, Any]] = []
    for team_name, roster in (info.get("players") or {}).items():
        for p_name in roster:
            pkey = hashlib.md5(f"{match_id}:{team_name}:{p_name}".encode("utf-8")).hexdigest()[:16]
            player_rows.append({
                "player_key": pkey,
                "match_id": match_id,
                "team_name": team_name,
                "player_name": p_name,
                "registry_id": registry.get(p_name, ""),
            })

    delivery_rows: List[Dict[str, Any]] = []
    partnership_rows: List[Dict[str, Any]] = []
    seq_idx = 0

    for inn_idx, innings in enumerate(payload.get("innings", []), start=1):
        batting_team = innings.get("team", teams[0])
        bowling_team = teams[1] if batting_team == teams[0] and len(teams) > 1 else teams[0]

        wkt_num = 1
        part_runs = 0
        part_balls = 0
        part_pair: Optional[Tuple[str, str]] = None

        for over_block in innings.get("overs", []):
            over_num = int(over_block.get("over", 0))
            for ball_idx, deliv in enumerate(over_block.get("deliveries", []), start=1):
                seq_idx += 1
                batter = str(deliv.get("batter", "Unknown"))
                bowler = str(deliv.get("bowler", "Unknown"))
                non_striker = str(deliv.get("non_striker", "Unknown"))
                runs_obj = deliv.get("runs", {})
                r_bat = int(runs_obj.get("batter", 0))
                r_ext = int(runs_obj.get("extras", 0))
                r_tot = int(runs_obj.get("total", r_bat + r_ext))

                extras_dict = deliv.get("extras", {})
                extras_type = ",".join(sorted(extras_dict.keys())) if extras_dict else None

                wickets = deliv.get("wickets", [])
                is_wkt = 1 if wickets else 0
                w_kind = wickets[0].get("kind") if wickets else None
                p_out = wickets[0].get("player_out") if wickets else None
                fielders = (
                    ", ".join(f.get("name", "") for f in wickets[0].get("fielders", []) if isinstance(f, dict))
                    if wickets
                    else None
                )

                delivery_rows.append({
                    "delivery_id": f"{match_id}-I{inn_idx}-O{over_num:02d}-B{ball_idx:02d}-{seq_idx:04d}",
                    "match_id": match_id,
                    "innings_num": inn_idx,
                    "batting_team": batting_team,
                    "bowling_team": bowling_team,
                    "over_num": over_num,
                    "ball_num": ball_idx,
                    "seq_index": seq_idx,
                    "batter": batter,
                    "bowler": bowler,
                    "non_striker": non_striker,
                    "runs_batter": r_bat,
                    "runs_extras": r_ext,
                    "runs_total": r_tot,
                    "extras_type": extras_type,
                    "is_wicket": is_wkt,
                    "wicket_kind": w_kind,
                    "player_out": p_out,
                    "fielders": fielders,
                })

                if part_pair is None:
                    part_pair = (batter, non_striker)
                part_runs += r_tot
                if "wides" not in (extras_dict or {}):
                    part_balls += 1

                if is_wkt:
                    partnership_rows.append({
                        "partnership_id": f"{match_id}-I{inn_idx}-P{wkt_num:02d}",
                        "match_id": match_id,
                        "innings_num": inn_idx,
                        "batting_team": batting_team,
                        "wicket_number": wkt_num,
                        "batter_1": part_pair[0],
                        "batter_2": part_pair[1],
                        "runs_scored": part_runs,
                        "balls_faced": part_balls,
                    })
                    wkt_num += 1
                    part_runs = 0
                    part_balls = 0
                    part_pair = None

        if part_pair is not None and (part_runs > 0 or part_balls > 0):
            partnership_rows.append({
                "partnership_id": f"{match_id}-I{inn_idx}-P{wkt_num:02d}",
                "match_id": match_id,
                "innings_num": inn_idx,
                "batting_team": batting_team,
                "wicket_number": wkt_num,
                "batter_1": part_pair[0],
                "batter_2": part_pair[1],
                "runs_scored": part_runs,
                "balls_faced": part_balls,
            })

    return match_row, player_rows, delivery_rows, partnership_rows


def run_glue_style_etl(
    raw_dir: Path = RAW_JSON_DIR,
    db_path: Path = DB_PATH,
    parquet_dir: Path = PARQUET_DIR,
) -> Dict[str, int]:
    """Executes complete ETL: JSON -> Relational Tables (RDS Postgres / SQLite) + Parquet Analytics Store."""
    json_files = sorted(raw_dir.glob("*.json"))
    matches, players, deliveries, partnerships = [], [], [], []
    for jf in json_files:
        m, pl, dl, pt = flatten_cricsheet_match(jf)
        matches.append(m)
        players.extend(pl)
        deliveries.extend(dl)
        partnerships.extend(pt)

    df_m = pd.DataFrame(matches)
    df_pl = pd.DataFrame(players)
    df_dl = pd.DataFrame(deliveries)
    df_pt = pd.DataFrame(partnerships)

    parquet_dir.mkdir(parents=True, exist_ok=True)
    df_m.to_parquet(parquet_dir / "matches.parquet", index=False)
    df_pl.to_parquet(parquet_dir / "players.parquet", index=False)
    df_dl.to_parquet(parquet_dir / "deliveries.parquet", index=False)
    df_pt.to_parquet(parquet_dir / "partnerships.parquet", index=False)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(schema_sql)
        df_m.to_sql("matches", conn, if_exists="replace", index=False)
        df_pl.to_sql("players", conn, if_exists="replace", index=False)
        df_dl.to_sql("deliveries", conn, if_exists="replace", index=False)
        df_pt.to_sql("partnerships", conn, if_exists="replace", index=False)
        conn.executescript(schema_sql)  # Re-ensure indexes
        conn.commit()

    return {
        "matches": len(df_m),
        "players": len(df_pl),
        "deliveries": len(df_dl),
        "partnerships": len(df_pt),
    }
