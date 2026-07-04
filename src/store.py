import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "hakiki.db"


def _conn():
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    return db


def init_db():
    db = _conn()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS seed_records (
            id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            constituency TEXT,
            project TEXT,
            details TEXT,
            url TEXT
        );
        CREATE TABLE IF NOT EXISTS media_cache (
            fingerprint TEXT PRIMARY KEY,
            verdict_json TEXT NOT NULL
        );
    """)
    db.close()


def get_cached_verdict(fingerprint: str) -> dict | None:
    db = _conn()
    row = db.execute(
        "SELECT verdict_json FROM media_cache WHERE fingerprint = ?", (fingerprint,)
    ).fetchone()
    db.close()
    if row:
        return json.loads(row[0])
    return None


def store_verdict(fingerprint: str, verdict: dict):
    db = _conn()
    db.execute(
        "INSERT OR REPLACE INTO media_cache (fingerprint, verdict_json) VALUES (?, ?)",
        (fingerprint, json.dumps(verdict)),
    )
    db.commit()
    db.close()
