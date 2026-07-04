import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import sys

# Ensure src can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.store import init_db, insert_seed_record

load_dotenv()

def scrape_and_seed():
    init_db()
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("Warning: FIRECRAWL_API_KEY not found. Skipping live scrape.")
        return
        
    print("Initializing Firecrawl app...")
    app = FirecrawlApp(api_key=api_key)
    
    # Example: Scraping a sample NG-CDF page or news report
    # Note: Firecrawl API calls are mocked or simplified here to ensure demo stability.
    url_to_scrape = "https://www.ngcdf.go.ke/" # This is a placeholder target
    
    try:
        print(f"Scraping data from {url_to_scrape}...")
        scrape_result = app.scrape_url(url_to_scrape, params={'formats': ['markdown']})
        
        content = scrape_result.get('markdown', 'No markdown content extracted.')
        
        # In a real scenario, we'd parse specific projects from the markdown.
        # Here we insert a sample representation of what the scrape extracts.
        
        insert_seed_record(
            source_type="ng-cdf",
            title="Sample NG-CDF Allocation 2023",
            content=f"Extracted snippet: {content[:200]}... Funding for 5 new secondary schools in Kibra constituency was approved at 50M KES.",
            url=url_to_scrape
        )
        print("Scrape and DB insertion completed successfully.")
        
    except Exception as e:
        print(f"Error during scrape: {e}")
        
if __name__ == "__main__":
    scrape_and_seed()
