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
        # We use a known public source discussing NG-CDF audit reports to get real context.
        # Firecrawl will extract the markdown.
        url_to_scrape = "https://www.tuko.co.ke/politics/493208-auditor-general-nancy-gathungu-exposes-sh-10b-ng-cdf-funds-unaccounted-for/"
        
        print(f"Scraping data from {url_to_scrape}...")
        scrape_result = app.scrape_url(url_to_scrape)
        
        # Firecrawl results might be a string, dict, or Document object
        if isinstance(scrape_result, str):
            content = scrape_result
        elif isinstance(scrape_result, dict):
            content = scrape_result.get('markdown', '') or scrape_result.get('content', '')
        else:
            # It's a Document object in newer SDKs
            content = getattr(scrape_result, 'markdown', '') or getattr(scrape_result, 'content', '')
        
        if not content:
            print("Warning: Scrape returned empty content. No data seeded.")
            return
            
        print("Scrape successful. Extracting real facts using DeepSeek...")
        
        # Use DeepSeek to extract the core facts from the scraped article
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            print("Warning: DEEPSEEK_API_KEY not found. Inserting raw markdown.")
            fact_summary = content[:500] + "..."
        else:
            from openai import OpenAI
            client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com", timeout=20.0)
            prompt = f"""
            Extract the main factual findings regarding the NG-CDF audit from the following scraped news article.
            Format as a short, factual summary. Do not make up any information.
            
            Article: {content[:4000]}
            """
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200
            )
            fact_summary = response.choices[0].message.content.strip()
            
        insert_seed_record(
            source_type="news-audit",
            title="Auditor-General Findings on NG-CDF",
            content=fact_summary,
            url=url_to_scrape
        )
        print("Scrape and DB insertion completed successfully with real data!")
        
    except Exception as e:
        print(f"Error during scrape: {e}")
        
if __name__ == "__main__":
    scrape_and_seed()
