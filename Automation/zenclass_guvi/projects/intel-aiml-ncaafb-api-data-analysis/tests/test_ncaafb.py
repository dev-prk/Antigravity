"""Automated test suite for NCAAFB Sports Analytics Platform."""

from pathlib import Path
import pytest

from src.analytics import ANALYTICAL_SQL_QUERIES, run_named_query
from src.api_client import SportradarNCAAFClient, ingest_live_or_seed
from src.database import NCAAFBDatabase


@pytest.fixture()
def populated_db(tmp_path: Path) -> NCAAFBDatabase:
    db = NCAAFBDatabase(db_path=tmp_path / "test_ncaafb.db")
    ingest_live_or_seed(db, force_reseed=True)
    return db


def test_all_eight_required_tables_populated(populated_db: NCAAFBDatabase) -> None:
    counts = populated_db.table_counts()
    for required_table in [
        "Teams",
        "Venues",
        "Conferences",
        "Seasons",
        "Players",
        "Player_Statistics",
        "Rankings",
        "Coaches",
        "Schedules",
    ]:
        assert counts[required_table] > 0, f"Table {required_table} should not be empty"
    assert counts["Seasons"] >= 3
    assert counts["Teams"] >= 16


def test_foreign_key_integrity_and_readonly_guard(populated_db: NCAAFBDatabase) -> None:
    with populated_db.connect() as conn:
        fk_errors = conn.execute("PRAGMA foreign_key_check;").fetchall()
        assert fk_errors == []

    with pytest.raises(ValueError):
        populated_db.query_df("DROP TABLE Teams;")


def test_all_spec_analytical_queries_return_rows(populated_db: NCAAFBDatabase) -> None:
    for title in ANALYTICAL_SQL_QUERIES:
        df = run_named_query(populated_db, title)
        assert not df.empty, f"Query '{title}' returned 0 rows"


def test_sportradar_client_requires_key_cleanly(tmp_path: Path) -> None:
    client = SportradarNCAAFClient(api_key="", cache_dir=tmp_path / "cache")
    assert not client.is_configured
    with pytest.raises(RuntimeError):
        client.fetch_seasons()
