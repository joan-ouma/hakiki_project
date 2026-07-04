from fastapi import APIRouter, Request, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import requests

from src.privacy import strip_pii, hash_phone_number
from src.cache import generate_media_hash, check_media_cache, save_media_cache
from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.engine.media import process_audio, process_image
from src.engine.verdict import compose_verdict

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(default=""),
    NumMedia: int = Form(default=0)
):
    """
    Handles incoming Twilio WhatsApp messages.
    """
    # 1. Privacy Filter
    hashed_user = hash_phone_number(From)
    clean_body = strip_pii(Body)
    
    media_score = None
    extracted_text = clean_body
    
    # 2. Handle Media if present
    if NumMedia > 0:
        # Twilio sends MediaUrl0, MediaContentType0 etc.
        form_data = await request.form()
        media_url = form_data.get("MediaUrl0")
        media_type = form_data.get("MediaContentType0", "")
        
        if media_url:
            # Download media into memory
            try:
                media_resp = requests.get(media_url, timeout=10)
                media_bytes = media_resp.content
                media_hash = generate_media_hash(media_bytes)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading media: {e}")
                media_bytes = None
                media_hash = None
            
            # 3. Check Cache
            cached = None
            if media_hash:
                cached = check_media_cache(media_hash)
                
            if cached:
                if cached["media_type"] == "audio":
                    extracted_text = cached.get("transcription", "") + " " + clean_body
                elif cached["media_type"] == "image":
                    media_score = cached.get("verdict_score")
            else:
                # 4. Process new media
                if media_type.startswith("audio/"):
                    transcription = await process_audio(media_bytes)
                    extracted_text = transcription + " " + clean_body
                    save_media_cache(media_hash, "audio", transcription=transcription)
                elif media_type.startswith("image/"):
                    result = await process_image(media_bytes)
                    media_score = result.get("fake_probability")
                    save_media_cache(media_hash, "image", verdict_score=media_score)
                    
    # 5. Extract and Match Claim
    claim = extract_claim(extracted_text)
    match = match_claim(claim)
    
    # 6. Compose Verdict
    reply_text = compose_verdict(claim, match, media_score)
    
    # Twilio expects TwiML XML response
    response = MessagingResponse()
    response.message(reply_text)
    
    return Response(content=str(response), media_type="application/xml")
