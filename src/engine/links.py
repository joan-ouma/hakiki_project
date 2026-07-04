import re
import httpx
from src.config import FIRECRAWL_API_KEY

SOCIAL_LINK_PATTERN = re.compile(
    r'https?://(?:vm\.tiktok\.com|www\.tiktok\.com|x\.com|twitter\.com|fb\.watch|www\.facebook\.com|www\.instagram\.com)/\S+',
    re.IGNORECASE,
)


def extract_link(text: str) -> str | None:
    """Find a social media link in the message text."""
    match = SOCIAL_LINK_PATTERN.search(text)
    return match.group(0) if match else None


def scrape_link_content(url: str) -> str | None:
    """Scrape caption/text content from a social media link via Firecrawl."""
    if not FIRECRAWL_API_KEY:
        return None

    try:
        from firecrawl.client import Firecrawl
        app = Firecrawl(api_key=FIRECRAWL_API_KEY)
        doc = app.scrape(url, formats=["markdown"])
        content = doc.markdown or ""
        if len(content) < 20:
            return None
        # Return first 1000 chars — enough for claim extraction
        return content[:1000]
    except Exception:
        return None
