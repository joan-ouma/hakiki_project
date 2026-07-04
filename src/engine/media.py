import httpx
from src.config import HF_API_TOKEN, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

# ponytail: using umm-maybe/AI-image-detector on HF Inference API
# swap to local transformers if this model goes offline
HF_MODEL = "umm-maybe/AI-image-detector"
HF_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"


def download_media(media_url: str) -> tuple[bytes, str]:
    """Download media from Twilio — follow redirect to CDN. Returns (bytes, content_type)."""
    r = httpx.get(
        media_url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        follow_redirects=False,
        timeout=30,
    )
    if r.status_code in (301, 302, 307, 308) and "location" in r.headers:
        r = httpx.get(r.headers["location"], timeout=30)
    elif r.status_code == 200:
        return r.content, r.headers.get("content-type", "image/jpeg")
    else:
        r.raise_for_status()
    r.raise_for_status()
    return r.content, r.headers.get("content-type", "image/jpeg")


def score_image(image_bytes: bytes, content_type: str = "image/jpeg") -> dict:
    """Score image for AI-generation/manipulation via HF Inference API."""
    if not HF_API_TOKEN:
        return {"error": "No HF_API_TOKEN configured", "score": None}

    try:
        r = httpx.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_API_TOKEN}", "Content-Type": content_type},
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
