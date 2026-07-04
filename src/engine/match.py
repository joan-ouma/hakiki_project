import sqlite3
import httpx
from src.store import DB_PATH
from src.config import GOOGLE_FACTCHECK_API_KEY


def match_seed_db(claim: str) -> dict | None:
    """Simple keyword match against seed records."""
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    words = [w for w in claim.lower().split() if len(w) > 3]
    if not words:
        db.close()
        return None

    # ponytail: OR-based LIKE search, upgrade to FTS5 if this gets slow
    conditions = " OR ".join(["(LOWER(project) LIKE ? OR LOWER(details) LIKE ? OR LOWER(constituency) LIKE ?)"] * len(words))
    params = []
    for w in words:
        params.extend([f"%{w}%"] * 3)

    row = db.execute(
        f"SELECT * FROM seed_records WHERE {conditions} LIMIT 1", params
    ).fetchone()
    db.close()

    if row:
        return {
            "source": row["source"],
            "constituency": row["constituency"],
            "project": row["project"],
            "details": row["details"],
            "url": row["url"],
        }
    return None


def match_factcheck_api(claim: str) -> dict | None:
    """Query Google Fact Check Tools API."""
    if not GOOGLE_FACTCHECK_API_KEY:
        return None

    try:
        r = httpx.get(
            "https://factchecktools.googleapis.com/v1alpha1/claims:search",
            params={"query": claim, "key": GOOGLE_FACTCHECK_API_KEY, "languageCode": "en"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, Exception):
        return None

    claims = data.get("claims", [])
    if not claims:
        return None

    top = claims[0]
    review = top.get("claimReview", [{}])[0]
    return {
        "claim_text": top.get("text", ""),
        "claimant": top.get("claimant", "Unknown"),
        "rating": review.get("textualRating", "Unknown"),
        "publisher": review.get("publisher", {}).get("name", "Unknown"),
        "url": review.get("url", ""),
    }


def match_claim(claim: str) -> dict:
    """Try seed DB first, then Google Fact Check API as fallback."""
    seed = match_seed_db(claim)
    factcheck = match_factcheck_api(claim)
    return {"seed_match": seed, "factcheck_match": factcheck}
