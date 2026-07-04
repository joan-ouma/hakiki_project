import os
import requests
from src.store import search_seed_records

def match_claim(claim: str):
    """
    Matches an extracted claim against local SQLite data and Google Fact Check API.
    Returns the best matching source or None if unverified.
    """
    if not claim or claim == "NO CLAIM FOUND" or claim == "ERROR_EXTRACTING_CLAIM":
        return None
        
    # 1. Check local seed database
    db_results = search_seed_records(claim)
    if db_results:
        # For MVP, just return the first hit
        best_match = db_results[0]
        return {
            "source_type": "local_db",
            "title": best_match["title"],
            "url": best_match["url"],
            "content_snippet": best_match["content"]
        }
        
    # 2. Check Google Fact Check API
    google_api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
    if google_api_key:
        try:
            url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={claim}&key={google_api_key}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if "claims" in data and len(data["claims"]) > 0:
                best_claim = data["claims"][0]
                review = best_claim.get("claimReview", [{}])[0]
                return {
                    "source_type": "google_fact_check",
                    "title": review.get("title", best_claim.get("text")),
                    "url": review.get("url"),
                    "content_snippet": review.get("textualRating", "No rating found")
                }
        except Exception as e:
            print(f"Google Fact Check API error: {e}")
            
    return None
