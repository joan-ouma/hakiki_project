import asyncio
from fastapi import APIRouter, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.engine.verdict import compose_verdict

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

    if not Body.strip():
        resp.message("Please send a claim or forward a message for me to check.")
        return Response(content=str(resp), media_type="text/xml")

    claim = await asyncio.to_thread(extract_claim, Body)

    if claim is None:
        resp.message(
            "I couldn't find a checkable factual claim in that message. "
            "Try forwarding a specific claim about a politician, project, or budget."
        )
        return Response(content=str(resp), media_type="text/xml")

    matches = await asyncio.to_thread(match_claim, claim)
    verdict = compose_verdict(claim, matches)
    resp.message(verdict)

    return Response(content=str(resp), media_type="text/xml")
