-- Normalized Relational SQL Schema for NCAAFB Analytics Platform (8 Core Spec Tables + Schedules)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Conferences (
    conference_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    alias TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Venues (
    venue_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'USA',
    zip TEXT,
    address TEXT,
    capacity INTEGER CHECK (capacity >= 0),
    surface TEXT,
    roof_type TEXT,
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS Teams (
    team_id TEXT PRIMARY KEY,
    market TEXT NOT NULL,
    name TEXT NOT NULL,
    alias TEXT NOT NULL,
    founded INTEGER,
    mascot TEXT,
    fight_song TEXT,
    championships_won INTEGER DEFAULT 0,
    conference_id TEXT,
    division_id TEXT,
    venue_id TEXT,
    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id),
    FOREIGN KEY (venue_id) REFERENCES Venues(venue_id)
);

CREATE TABLE IF NOT EXISTS Seasons (
    season_id TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL,
    type_code TEXT NOT NULL DEFAULT 'REG'
);

CREATE TABLE IF NOT EXISTS Players (
    player_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    abbr_name TEXT,
    birth_place TEXT,
    position TEXT NOT NULL,
    height INTEGER,
    weight INTEGER,
    status TEXT NOT NULL DEFAULT 'ACT',
    eligibility TEXT,
    team_id TEXT NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

CREATE TABLE IF NOT EXISTS Player_Statistics (
    stat_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    team_id TEXT NOT NULL,
    season_id TEXT NOT NULL,
    games_played INTEGER DEFAULT 0,
    games_started INTEGER DEFAULT 0,
    rushing_yards INTEGER DEFAULT 0,
    rushing_touchdowns INTEGER DEFAULT 0,
    receiving_yards INTEGER DEFAULT 0,
    receiving_touchdowns INTEGER DEFAULT 0,
    kick_return_yards INTEGER DEFAULT 0,
    fumbles INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (season_id) REFERENCES Seasons(season_id)
);

CREATE TABLE IF NOT EXISTS Rankings (
    ranking_id TEXT PRIMARY KEY,
    poll_id TEXT NOT NULL,
    poll_name TEXT NOT NULL,
    season_id TEXT NOT NULL,
    week INTEGER NOT NULL,
    effective_time TEXT,
    team_id TEXT NOT NULL,
    rank INTEGER NOT NULL,
    prev_rank INTEGER,
    points INTEGER DEFAULT 0,
    fp_votes INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    FOREIGN KEY (season_id) REFERENCES Seasons(season_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

CREATE TABLE IF NOT EXISTS Coaches (
    coach_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL,
    team_id TEXT NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

CREATE TABLE IF NOT EXISTS Schedules (
    game_id TEXT PRIMARY KEY,
    season_id TEXT NOT NULL,
    week INTEGER NOT NULL,
    scheduled_date TEXT NOT NULL,
    home_team_id TEXT NOT NULL,
    away_team_id TEXT NOT NULL,
    venue_id TEXT,
    home_points INTEGER,
    away_points INTEGER,
    status TEXT NOT NULL DEFAULT 'closed',
    attendance INTEGER,
    FOREIGN KEY (season_id) REFERENCES Seasons(season_id),
    FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES Venues(venue_id)
);

CREATE INDEX IF NOT EXISTS idx_teams_conf ON Teams(conference_id);
CREATE INDEX IF NOT EXISTS idx_players_team ON Players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_pos ON Players(position);
CREATE INDEX IF NOT EXISTS idx_stats_player_season ON Player_Statistics(player_id, season_id);
CREATE INDEX IF NOT EXISTS idx_rankings_season_week ON Rankings(season_id, week);
CREATE INDEX IF NOT EXISTS idx_schedules_season ON Schedules(season_id, week);
