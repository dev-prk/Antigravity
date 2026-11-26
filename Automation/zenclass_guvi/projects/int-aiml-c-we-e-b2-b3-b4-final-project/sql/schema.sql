-- PostgreSQL (Amazon RDS) / SQLite Compatible DDL for Cricsheet Cricket Analytics
CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    match_date TEXT,
    event_name TEXT,
    team1 TEXT NOT NULL,
    team2 TEXT NOT NULL,
    venue TEXT,
    city TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    win_by_runs INTEGER DEFAULT 0,
    win_by_wickets INTEGER DEFAULT 0,
    player_of_match TEXT,
    overs_limit INTEGER DEFAULT 20
);

CREATE TABLE IF NOT EXISTS players (
    player_key TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    team_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    registry_id TEXT
);

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    innings_num INTEGER NOT NULL,
    batting_team TEXT NOT NULL,
    bowling_team TEXT NOT NULL,
    over_num INTEGER NOT NULL,
    ball_num INTEGER NOT NULL,
    seq_index INTEGER NOT NULL,
    batter TEXT NOT NULL,
    bowler TEXT NOT NULL,
    non_striker TEXT NOT NULL,
    runs_batter INTEGER NOT NULL DEFAULT 0,
    runs_extras INTEGER NOT NULL DEFAULT 0,
    runs_total INTEGER NOT NULL DEFAULT 0,
    extras_type TEXT,
    is_wicket INTEGER NOT NULL DEFAULT 0,
    wicket_kind TEXT,
    player_out TEXT,
    fielders TEXT
);

CREATE TABLE IF NOT EXISTS partnerships (
    partnership_id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL,
    innings_num INTEGER NOT NULL,
    batting_team TEXT NOT NULL,
    wicket_number INTEGER NOT NULL,
    batter_1 TEXT NOT NULL,
    batter_2 TEXT NOT NULL,
    runs_scored INTEGER NOT NULL DEFAULT 0,
    balls_faced INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_deliv_match_seq ON deliveries(match_id, seq_index);
CREATE INDEX IF NOT EXISTS idx_deliv_batter ON deliveries(match_id, batter);
CREATE INDEX IF NOT EXISTS idx_deliv_bowler ON deliveries(match_id, bowler);
CREATE INDEX IF NOT EXISTS idx_part_match ON partnerships(match_id, innings_num);
