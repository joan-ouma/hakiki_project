import asyncio
from fastapi import APIRouter, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.engine.media import download_media, score_image
from src.engine.verdict import compose_verdict
from src.cache import check_cache, save_to_cache

router = APIRouter(prefix="/webhook")


@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
):
    resp = MessagingResponse()

    # Handle media (image) if attached
    media_result = None
    if NumMedia > 0 and MediaUrl0:
        is_image = MediaContentType0 and "image" in MediaContentType0
        if is_image:
            try:
                media_bytes, ct = await asyncio.to_thread(download_media, MediaUrl0)
                cached = check_cache(media_bytes)
                if cached:
                    media_result = cached
                else:
                    media_result = await asyncio.to_thread(score_image, media_bytes, ct)
                    if media_result and not media_result.get("error"):
                        save_to_cache(media_bytes, media_result)
            except Exception as e:
                media_result = {"error": f"Could not process image: {e}", "score": None}

    # Handle text claim
    claim = None
    matches = None
    if Body.strip():
        claim = await asyncio.to_thread(extract_claim, Body)
        if claim:
            matches = await asyncio.to_thread(match_claim, claim)

    # Need at least a claim or media to respond
    if not claim and not media_result:
        resp.message(
            "Please send a claim or forward a message (with or without an image) for me to check."
        )
        return Response(content=str(resp), media_type="text/xml")

    verdict = compose_verdict(claim, matches, media_result)
    resp.message(verdict)

    return Response(content=str(resp), media_type="text/xml")
