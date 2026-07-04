"""Tests for src.store — SQLite DB operations."""
import json
from src.store import init_db, get_cached_verdict, store_verdict


def test_init_db_creates_tables():
    init_db()
    from src.store import _conn
    db = _conn()
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    db.close()
    table_names = [t[0] for t in tables]
    assert "seed_records" in table_names
    assert "media_cache" in table_names


def test_store_and_get_verdict():
    fp = "test_fingerprint_abc123"
    verdict = {"rating": "True", "confidence": 90}
    store_verdict(fp, verdict)

    result = get_cached_verdict(fp)
    assert result == verdict


def test_get_cached_verdict_returns_none_for_missing():
    result = get_cached_verdict("nonexistent_fingerprint_xyz")
    assert result is None


def test_store_verdict_overwrites_existing():
    fp = "test_overwrite_fp"
    store_verdict(fp, {"v": 1})
    store_verdict(fp, {"v": 2})
    result = get_cached_verdict(fp)
    assert result == {"v": 2}
