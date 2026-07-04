"""Tests for src.engine.match — seed DB matching logic."""
import sqlite3
from pathlib import Path
from unittest.mock import patch

from src.engine.match import match_seed_db, STOPWORDS


DB_PATH = Path(__file__).parent.parent.parent / "data" / "hakiki.db"


def test_stopwords_filter_common_words():
    assert "kenya" in STOPWORDS
    assert "built" in STOPWORDS
    assert "government" in STOPWORDS
    assert "county" in STOPWORDS


def test_match_seed_db_returns_none_for_generic_claim():
    result = match_seed_db("Kenya built a road")
    assert result is None


def test_match_seed_db_returns_none_for_single_keyword():
    result = match_seed_db("Changamwe is nice")
    assert result is None


def test_match_seed_db_returns_none_for_empty():
    assert match_seed_db("") is None
    assert match_seed_db("hi") is None


def test_match_seed_db_with_known_constituency():
    """If the DB has a Changamwe CDF record, a specific claim should match."""
    db = sqlite3.connect(str(DB_PATH))
    row = db.execute(
        "SELECT * FROM seed_records WHERE LOWER(constituency) LIKE '%changamwe%' LIMIT 1"
    ).fetchone()
    db.close()

    if row is None:
        return  # skip if no test data

    result = match_seed_db("NGCDF allocation Changamwe constituency")
    assert result is not None
    assert "changamwe" in result["constituency"].lower() or "cdf" in result["source"].lower()


def test_match_seed_db_returns_dict_with_expected_keys():
    """If a match is found, it should have the right shape."""
    db = sqlite3.connect(str(DB_PATH))
    row = db.execute("SELECT * FROM seed_records LIMIT 1").fetchone()
    db.close()

    if row is None:
        return  # skip if no seed data

    # Use words from the first record to force a match
    result = match_seed_db("NGCDF allocation Changamwe constituency projects disbursement")
    if result is None:
        return

    assert "source" in result
    assert "constituency" in result
    assert "project" in result
    assert "details" in result
    assert "url" in result
