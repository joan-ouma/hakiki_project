import httpx
from src.config import HF_API_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

# ponytail: using umm-maybe/AI-image-detector on HF Inference API
# swap to local transformers if this model goes offline
HF_MODEL = "umm-maybe/AI-image-detector"
HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def download_media(media_url: str) -> bytes:
    """Download media from Twilio (requires basic auth)."""
    r = httpx.get(
        media_url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        follow_redirects=True,
        timeout=30,
    )
    r.raise_for_status()
    return r.content


def score_image(image_bytes: bytes) -> dict:
    """Score image for AI-generation/manipulation via HF Inference API."""
    if not HF_API_TOKEN:
        return {"error": "No HF_API_TOKEN configured", "score": None}

    try:
        r = httpx.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            content=image_bytes,
            timeout=30,
        )
        r.raise_for_status()
        results = r.json()
    except Exception as e:
        return {"error": str(e), "score": None}

    # Results come as [{"label": "artificial", "score": 0.9}, {"label": "human", "score": 0.1}]
    if isinstance(results, list):
        scores = {item["label"]: item["score"] for item in results}
        ai_score = scores.get("artificial", scores.get("ai", 0))
        return {
            "ai_probability": round(ai_score, 3),
            "label": "likely AI-generated" if ai_score > 0.7 else "likely authentic" if ai_score < 0.3 else "inconclusive",
            "raw": scores,
        }

    return {"error": "Unexpected response format", "score": None, "raw": results}
