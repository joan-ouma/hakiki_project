"""
One-off seed script: scrapes public Kenyan government data via Firecrawl,
parses it, and loads into SQLite.

Sources:
- NG-CDF allocations and disbursements
- Auditor-General reports
- IEBC (election/politician data)
- Kenya Open Data / budget portals
- Kenyan news outlets (Nation, Standard) for verified project coverage

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

# Broader set of sources
SOURCES = {
    "NG-CDF": [
        "https://ngcdf.go.ke/allocations/",
        "https://ngcdf.go.ke/disbursement/",
        "https://ngcdf.go.ke/ngcdf-key-achievements/",
    ],
    "Auditor-General": [
        "https://www.oagkenya.go.ke/reports/",
        "https://www.oagkenya.go.ke/county-reports/",
    ],
    "Budget": [
        "https://www.treasury.go.ke/budget/",
        "https://www.opendata.go.ke/datasets/",
    ],
    "Finance-Bill": [
        "https://www.parliament.go.ke/the-national-assembly/house-business/bills",
        "https://www.treasury.go.ke/tax-policy/",
    ],
    "Parliament": [
        "https://www.parliament.go.ke/the-national-assembly/house-business/hansard",
    ],
    "Health": [
        "https://www.health.go.ke/",
    ],
    "IEBC": [
        "https://www.iebc.or.ke/registration/",
    ],
    "News-Nation": [
        "https://nation.africa/kenya/news/politics",
        "https://nation.africa/kenya/counties",
    ],
    "News-Standard": [
        "https://www.standardmedia.co.ke/politics",
    ],
}


def scrape_url(app: Firecrawl, url: str, label: str) -> dict | None:
    """Scrape a single URL via Firecrawl."""
    print(f"[{label}] Scraping: {url}")
    try:
        doc = app.scrape(url, formats=["markdown"])
        content = doc.markdown or ""
        if content and len(content) > 100:
            safe_name = re.sub(r'[^\w]', '_', url)[:80]
            (SEED_DIR / f"{safe_name}.md").write_text(content)
            print(f"  -> {len(content)} chars")
            return {"url": url, "content": content, "source": label}
        else:
            print(f"  -> too short or empty, skipping")
    except Exception as e:
        print(f"  -> ERROR: {e}")
    return None


def parse_ngcdf(content: str, url: str) -> list[dict]:
    """Extract constituency allocation records from NG-CDF pages."""
    records = []

    # Pattern 1: Allocation table rows
    pattern = re.compile(r'\|\s*\d+\.\s*\|\s*(\w+?)(?:Allocations|Disbursement)', re.IGNORECASE)
    for match in pattern.finditer(content):
        name = match.group(1)
        constituency = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        records.append({
            "source": "NG-CDF",
            "constituency": constituency,
            "project": f"NG-CDF Allocation - {constituency}",
            "details": f"Constituency with NG-CDF allocation records. Verify amounts at official portal.",
            "url": url,
        })

    # Pattern 2: Financial figures in text (e.g. "KSH 50,000,000" or "Ksh. 50M")
    money_pattern = re.compile(r'(KS[Hh]\.?\s*[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?)', re.IGNORECASE)
    lines = content.split("\n")
    for line in lines:
        money_matches = money_pattern.findall(line)
        if money_matches and len(line) > 30 and len(line) < 500:
            # Skip header/nav lines
            if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie", "subscribe"]):
                continue
            records.append({
                "source": "NG-CDF",
                "constituency": "",
                "project": line.strip()[:200],
                "details": line.strip(),
                "url": url,
            })

    # Pattern 3: Achievement/project mentions
    project_keywords = ["school", "hospital", "borehole", "road", "bridge", "water", "classroom", "dispensary", "polytechnic"]
    for line in lines:
        line_lower = line.strip().lower()
        if any(kw in line_lower for kw in project_keywords) and len(line.strip()) > 30 and len(line.strip()) < 500:
            if any(skip in line_lower for skip in ["menu", "nav", "footer", "cookie"]):
                continue
            records.append({
                "source": "NG-CDF",
                "constituency": "",
                "project": line.strip()[:200],
                "details": line.strip(),
                "url": url,
            })

    return records


def parse_auditor_general(content: str, url: str) -> list[dict]:
    """Extract audit findings and irregularities."""
    records = []
    keywords = ["audit", "finding", "irregularity", "expenditure", "misuse",
                "unaccounted", "loss", "wastage", "procurement", "pending bill",
                "county government", "national government"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 30 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie", "facebook", "twitter"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "Auditor-General",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_budget(content: str, url: str) -> list[dict]:
    """Extract budget/treasury data."""
    records = []
    keywords = ["allocation", "budget", "expenditure", "revenue", "deficit",
                "ministry", "county", "fiscal", "appropriation"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 30 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "National Treasury",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_news(content: str, url: str, source_label: str) -> list[dict]:
    """Extract political/project news claims."""
    records = []
    keywords = ["cdf", "constituency", "mp ", "governor", "senator", "president",
                "ruto", "raila", "gachagua", "kindiki", "million", "billion",
                "hospital", "school", "road", "water", "project", "tender",
                "corruption", "arrested", "charged", "audit"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 40 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie", "subscribe", "advertisement"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": source_label,
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_iebc(content: str, url: str) -> list[dict]:
    """Extract election/registration data."""
    records = []
    keywords = ["registered voter", "polling station", "constituency", "ward",
                "election", "candidate", "nomination"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 20 or len(line) > 500:
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "IEBC",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_finance_bill(content: str, url: str) -> list[dict]:
    """Extract finance bill provisions and tax changes."""
    records = []
    keywords = ["tax", "vat", "excise", "levy", "duty", "income tax", "finance bill",
                "amendment", "repeal", "propose", "impose", "exempt", "rate",
                "housing levy", "shif", "nssf", "paye"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 30 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "Finance Bill",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_parliament(content: str, url: str) -> list[dict]:
    """Extract parliamentary hansard mentions."""
    records = []
    keywords = ["motion", "bill", "debate", "vote", "resolution", "committee",
                "mp ", "hon.", "speaker", "petition", "amendment"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 30 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "Parliament Hansard",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


def parse_health(content: str, url: str) -> list[dict]:
    """Extract health ministry data."""
    records = []
    keywords = ["hospital", "health", "uhc", "sha", "nhif", "clinic", "vaccine",
                "doctor", "nurse", "medical", "facility", "patient"]
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 30 or len(line) > 500:
            continue
        if any(skip in line.lower() for skip in ["menu", "nav", "footer", "cookie"]):
            continue
        if any(kw in line.lower() for kw in keywords):
            records.append({
                "source": "Ministry of Health",
                "constituency": "",
                "project": line[:200],
                "details": line,
                "url": url,
            })

    return records


PARSERS = {
    "NG-CDF": parse_ngcdf,
    "Auditor-General": parse_auditor_general,
    "Budget": parse_budget,
    "Finance-Bill": parse_finance_bill,
    "Parliament": parse_parliament,
    "Health": parse_health,
    "IEBC": parse_iebc,
    "News-Nation": lambda c, u: parse_news(c, u, "Daily Nation"),
    "News-Standard": lambda c, u: parse_news(c, u, "The Standard"),
}


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

    # Clear old data and reload
    db.execute("DELETE FROM seed_records")
    db.executemany(
        "INSERT INTO seed_records (source, constituency, project, details, url) VALUES (?, ?, ?, ?, ?)",
        [(r.get("source", ""), r.get("constituency", ""), r.get("project", ""),
          r.get("details", ""), r.get("url", "")) for r in records],
    )
    db.commit()
    print(f"[DB] Loaded {len(records)} records into {DB_PATH}")
    db.close()


DOCS_DIR = Path(__file__).parent.parent.parent / "data"


def load_pdfs() -> list[dict]:
    """Load PDF files from data/docs/ using PyPDF2 and parse into records."""
    records = []
    if not DOCS_DIR.exists():
        return records

    try:
        import PyPDF2
    except ImportError:
        print("[PDF] PyPDF2 not installed, skipping PDF loading. Run: pip install PyPDF2")
        return records

    for pdf_path in DOCS_DIR.glob("*.pdf"):
        print(f"[PDF] Loading: {pdf_path.name}")
        try:
            reader = PyPDF2.PdfReader(str(pdf_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            # Derive source from filename (e.g. "finance_bill_2024.pdf" -> "Finance Bill 2024")
            source = pdf_path.stem.replace("_", " ").replace("-", " ").title()

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line or len(line) < 30 or len(line) > 500:
                    continue
                # Skip obvious junk
                if any(skip in line.lower() for skip in ["page ", "table of contents", "....."]):
                    continue
                records.append({
                    "source": source,
                    "constituency": "",
                    "project": line[:200],
                    "details": line,
                    "url": f"file://{pdf_path.name}",
                })
            print(f"  -> {len([r for r in records if r['url'].endswith(pdf_path.name)])} lines from {pdf_path.name}")
        except Exception as e:
            print(f"  -> ERROR: {e}")

    return records


def main():
    all_records = []

    # Load PDFs first (no API key needed)
    pdf_records = load_pdfs()
    all_records.extend(pdf_records)

    # Scrape web sources if Firecrawl key available
    if FIRECRAWL_API_KEY:
        app = Firecrawl(api_key=FIRECRAWL_API_KEY)

        for label, urls in SOURCES.items():
            parser = PARSERS.get(label)
            if not parser:
                continue

            for url in urls:
                page = scrape_url(app, url, label)
                if page:
                    records = parser(page["content"], page["url"])
                    all_records.extend(records)
                    print(f"  -> parsed {len(records)} records")
    else:
        print("[WARN] No FIRECRAWL_API_KEY — skipping web scraping, using PDFs only")

    # Deduplicate by (source, project)
    seen = set()
    deduped = []
    for r in all_records:
        key = (r["source"], r["project"][:100])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    if not deduped:
        print("[WARN] No records found. Add PDFs to data/docs/ or set FIRECRAWL_API_KEY.")
        return

    load_to_db(deduped)
    print(f"[DONE] {len(deduped)} unique records (from {len(all_records)} total)")


if __name__ == "__main__":
    main()
