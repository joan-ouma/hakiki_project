"""
One-off seed script: scrapes NG-CDF and Auditor-General data via Firecrawl,
parses it, and loads into SQLite.

Usage: python3 -m src.scripts.seed
"""

import json
import sqlite3
import re
from pathlib import Path

from firecrawl.client import Firecrawl
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = Path(__file__).parent.parent.parent / "data" / "hakiki.db"
SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"
SEED_DIR.mkdir(parents=True, exist_ok=True)

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

# NG-CDF project listing pages
NGCDF_URLS = [
    "https://ngcdf.go.ke/allocations/",
    "https://ngcdf.go.ke/projects/",
]

# Auditor-General reports
OAG_URLS = [
    "https://www.oagkenya.go.ke/reports/",
]


def scrape_urls(urls: list[str], label: str) -> list[dict]:
    """Scrape a list of URLs via Firecrawl, return raw markdown content."""
    if not FIRECRAWL_API_KEY:
        print(f"[WARN] No FIRECRAWL_API_KEY — skipping {label}")
        return []

    app = Firecrawl(api_key=FIRECRAWL_API_KEY)
    results = []

    for url in urls:
        print(f"[{label}] Scraping: {url}")
        try:
            doc = app.scrape(url, formats=["markdown"])
            content = doc.markdown or ""
            if content:
                results.append({"url": url, "content": content, "source": label})
                # Save raw for debugging
                safe_name = re.sub(r'[^\w]', '_', url)[:80]
                (SEED_DIR / f"{safe_name}.md").write_text(content)
                print(f"  -> {len(content)} chars")
            else:
                print(f"  -> empty response, skipping")
        except Exception as e:
            print(f"  -> ERROR: {e}")

    return results


def parse_ngcdf(content: str, url: str) -> list[dict]:
    """Extract constituency allocation records from scraped NG-CDF markdown."""
    records = []
    # Match rows like: | 1. | ChangamweAllocations
    pattern = re.compile(r'\|\s*\d+\.\s*\|\s*(\w+?)Allocations', re.IGNORECASE)

    for match in pattern.finditer(content):
        name = match.group(1)
        # Split camelCase: "LungaLunga" -> "Lunga Lunga"
        constituency = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        records.append({
            "source": "NG-CDF",
            "constituency": constituency,
            "project": f"NG-CDF Allocation - {constituency}",
            "details": f"Constituency with NG-CDF allocation records available",
            "url": f"https://ngcdf.go.ke/allocations/",
        })

    return records


def parse_oag(content: str, url: str) -> list[dict]:
    """Extract audit findings from scraped OAG markdown."""
    records = []
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("-"):
            continue
        if any(kw in line.lower() for kw in ["audit", "finding", "irregularity", "expenditure", "misuse"]):
            records.append({
                "source": "Auditor-General",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def load_to_db(records: list[dict]):
    """Insert parsed records into SQLite."""
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS seed_records (
            id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            constituency TEXT,
            project TEXT,
            details TEXT,
            url TEXT
        );
    """)

    db.executemany(
        "INSERT INTO seed_records (source, constituency, project, details, url) VALUES (?, ?, ?, ?, ?)",
        [(r.get("source", ""), r.get("constituency", ""), r.get("project", ""),
          r.get("details", ""), r.get("url", "")) for r in records],
    )
    db.commit()
    print(f"[DB] Loaded {len(records)} records into {DB_PATH}")
    db.close()


def main():
    all_records = []

    # Scrape NG-CDF
    ngcdf_pages = scrape_urls(NGCDF_URLS, "NG-CDF")
    for page in ngcdf_pages:
        all_records.extend(parse_ngcdf(page["content"], page["url"]))

    # Scrape Auditor-General
    oag_pages = scrape_urls(OAG_URLS, "OAG")
    for page in oag_pages:
        all_records.extend(parse_oag(page["content"], page["url"]))

    if not all_records:
        print("[WARN] No records scraped. Check FIRECRAWL_API_KEY and URLs.")
        return

    load_to_db(all_records)
    print(f"[DONE] Total records: {len(all_records)}")


if __name__ == "__main__":
    main()
