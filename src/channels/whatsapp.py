import asyncio
from fastapi import APIRouter, Form, BackgroundTasks
from fastapi.responses import Response
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse

from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.engine.media import download_media, score_image, transcribe_audio
from src.engine.links import extract_link, scrape_link_content
from src.engine.verdict import compose_verdict
from src.cache import check_cache, save_to_cache
from src.privacy import hash_phone
from src.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER

router = APIRouter(prefix="/webhook")

WELCOME_MSG = """Habari! Mimi ni *Hakiki Bot* — msaidizi wako wa kuthibitisha habari.

Ninaweza kukusaidia:
• Angalia madai kuhusu siasa, miradi ya serikali, au matumizi ya pesa za umma
• Chunguza picha kama ni AI-generated au halisi
• Sikiliza voice note na kuangalia ukweli wa madai
• Angalia TikTok, X (Twitter), au Facebook links kama zina ukweli

*Jinsi ya kutumia:*
1. Forward message yoyote unayoishuku
2. Share TikTok video hapa moja kwa moja
3. Tuma picha unayotaka kuchunguza
4. Tuma voice note na madai

Jaribu sasa — share TikTok au forward ujumbe wowote wa kisiasa!"""

NO_CLAIM_MSG = """Sikupata madai yanayoweza kuthibitishwa katika ujumbe huo.

Jaribu kutuma:
• "Ruto amejenga hospitali Nairobi kwa pesa za CDF"
• "MP wa Changamwe ameiba milioni 50"
• Picha ya poster ya kisiasa
• Voice note yenye madai

Naweza kuangalia madai kuhusu serikali, siasa, miradi, na matumizi ya pesa za umma."""

_twilio = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def _send_message(to: str, body: str):
    """Send a WhatsApp message via Twilio REST API."""
    _twilio.messages.create(from_=TWILIO_WHATSAPP_NUMBER, to=to, body=body)


async def _process_voice(media_bytes: bytes, ct: str, sender: str):
    """Background: transcribe voice note, extract claim, send verdict."""
    transcribed_text = await asyncio.to_thread(transcribe_audio, media_bytes, ct)

    if not transcribed_text:
        _send_message(sender, "I couldn't understand that voice note. Try sending a clearer recording or type your claim.")
        return

    claim = await asyncio.to_thread(extract_claim, transcribed_text)

    if not claim:
        _send_message(sender, f"I heard: \"{transcribed_text}\"\n\nBut I couldn't find a checkable claim. Try a specific claim about a politician or government project.")
        return

    matches = await asyncio.to_thread(match_claim, claim)
    verdict = compose_verdict(claim, matches, None, transcribed_text)
    _send_message(sender, verdict)


@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    background_tasks: BackgroundTasks = None,
):
    resp = MessagingResponse()
    print(f"[WA] Request from {hash_phone(From)}: media={NumMedia}, body_len={len(Body)}")

    try:
        media_result = None
        is_voice = NumMedia > 0 and MediaContentType0 and ("audio" in MediaContentType0 or "ogg" in MediaContentType0)

        # Welcome/help flow
        if Body.strip().lower() in ("hi", "hello", "hey", "habari", "sasa", "niaje", "help", "menu"):
            resp.message(WELCOME_MSG)
            return Response(content=str(resp), media_type="text/xml")

        if NumMedia > 0 and MediaUrl0 and MediaContentType0:
            try:
                media_bytes, ct = await asyncio.to_thread(download_media, MediaUrl0)
            except Exception:
                resp.message("Hatukuweza kupakua faili yako. Tafadhali jaribu kutuma tena.")
                return Response(content=str(resp), media_type="text/xml")

            if is_voice:
                background_tasks.add_task(_process_voice, media_bytes, ct, From)
                resp.message("Nimepokea voice note yako. Naisikiliza na kuangalia — nitajibu hivi karibuni.")
                return Response(content=str(resp), media_type="text/xml")

            elif "image" in MediaContentType0:
                cached = check_cache(media_bytes)
                if cached:
                    media_result = cached
                else:
                    media_result = await asyncio.to_thread(score_image, media_bytes, ct)
                    if media_result and not media_result.get("error"):
                        save_to_cache(media_bytes, media_result)

            elif "video" in MediaContentType0:
                if not Body.strip():
                    resp.message(
                        "Nimepokea video yako. Kwa sasa siwezi kuchunguza video moja kwa moja.\n\n"
                        "Tafadhali niambie: ni madai gani katika video hii unayotaka niangalie? "
                        "Andika kwa maneno yako au copy caption."
                    )
                    return Response(content=str(resp), media_type="text/xml")

        # Text claim — check for social media links first
        text_input = Body.strip() or ""
        claim = None
        matches = None
        if text_input:
            link = extract_link(text_input)
            if link:
                try:
                    scraped = await asyncio.to_thread(scrape_link_content, link)
                except Exception:
                    scraped = None

                if scraped:
                    text_input = scraped
                else:
                    remaining = text_input.replace(link, "").strip()
                    if remaining:
                        text_input = remaining
                    else:
                        resp.message(
                            "Nimepokea link lakini siwezi kuisoma kwa sasa. "
                            "Tafadhali copy-paste maneno/caption ya video hiyo hapa, "
                            "ama eleza madai yaliyomo kwa maneno yako."
                        )
                        return Response(content=str(resp), media_type="text/xml")

            try:
                claim = await asyncio.to_thread(extract_claim, text_input)
            except Exception:
                resp.message("Huduma ya uchambuzi haipatikani kwa sasa. Tafadhali jaribu tena baadaye.")
                return Response(content=str(resp), media_type="text/xml")

            if claim:
                try:
                    matches = await asyncio.to_thread(match_claim, claim)
                except Exception:
                    matches = {"seed_match": None, "factcheck_match": None}

        if not claim and not media_result:
            resp.message(NO_CLAIM_MSG)
            return Response(content=str(resp), media_type="text/xml")

        verdict = compose_verdict(claim, matches, media_result)
        resp.message(verdict)

    except Exception as e:
        print(f"[WA] Unexpected error: {type(e).__name__}: {e}")
        resp.message("Samahani, kuna tatizo la mfumo. Tafadhali jaribu tena baada ya dakika moja.")

    return Response(content=str(resp), media_type="text/xml")
