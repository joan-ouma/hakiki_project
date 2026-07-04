import re
import sqlite3
from openai import OpenAI
from src.store import DB_PATH
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

FACTCHECK_PROMPT = """You are a Kenyan political fact-checker. Given a claim, assess it based on your knowledge of Kenyan politics, government projects, budgets, and public records.

Return a JSON object with exactly these fields:
- "rating": one of "True", "Mostly True", "Misleading", "Mostly False", "False", "Unverifiable"
- "confidence": a number 0-100 (how confident you are)
- "explanation": one sentence explaining your rating (in simple English)
- "source_hint": what type of source could verify this (e.g. "NG-CDF records", "Kenya Gazette", "IEBC data", "Budget statement")

Rules:
- If you genuinely don't know, use "Unverifiable" with low confidence
- Never fabricate specific figures or dates you're unsure about
- For claims about specific KSH amounts or project details, lean toward "Unverifiable" unless you're very certain
- Return ONLY the JSON, no markdown formatting"""


STOPWORDS = {"that", "this", "with", "from", "have", "been", "will", "they",
             "their", "there", "what", "when", "where", "which", "about",
             "would", "could", "should", "much", "many", "some", "into",
             "also", "than", "then", "very", "just", "more", "most", "does",
             "kenya", "government", "built", "build", "made", "make", "said",
             "year", "years", "million", "billion", "money", "county"}


def match_seed_db(claim: str) -> dict | None:
    """Keyword match against seed records. Requires 2+ meaningful word hits."""
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    words = [w for w in re.findall(r'[a-z]+', claim.lower()) if len(w) > 3 and w not in STOPWORDS]
    if len(words) < 2:
        db.close()
        return None

    # ponytail: OR-based LIKE search, upgrade to FTS5 if this gets slow
    conditions = " OR ".join(["(LOWER(project) LIKE ? OR LOWER(details) LIKE ? OR LOWER(constituency) LIKE ?)"] * len(words))
    params = []
    for w in words:
        params.extend([f"%{w}%"] * 3)

    rows = db.execute(
        f"SELECT * FROM seed_records WHERE {conditions}", params
    ).fetchall()
    db.close()

    if not rows:
        return None

    # Score by number of keyword hits — pick best match
    best, best_score = None, 0
    for row in rows:
        text = f"{row['project']} {row['details']} {row['constituency']}".lower()
        score = sum(1 for w in words if w in text)
        if score > best_score:
            best, best_score = row, score

    # Require at least 2 word hits to avoid loose matches
    if best_score < 2:
        return None

    return {
        "source": best["source"],
        "constituency": best["constituency"],
        "project": best["project"],
        "details": best["details"],
        "url": best["url"],
    }


def match_ai_factcheck(claim: str) -> dict | None:
    """Use DeepSeek to assess claim plausibility."""
    try:
        response = _client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": FACTCHECK_PROMPT},
                {"role": "user", "content": claim},
            ],
            max_tokens=200,
            temperature=0.2,
            timeout=10,
        )
        import json
        text = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        data = json.loads(text)
        return {
            "rating": data.get("rating", "Unverifiable"),
            "confidence": data.get("confidence", 0),
            "explanation": data.get("explanation", ""),
            "source_hint": data.get("source_hint", ""),
            "publisher": "Hakiki",
            "url": "",
        }
    except Exception:
        return None


def match_claim(claim: str) -> dict:
    """Try seed DB first, then AI fact-check as secondary analysis."""
    seed = match_seed_db(claim)
    factcheck = match_ai_factcheck(claim)
    return {"seed_match": seed, "factcheck_match": factcheck}
