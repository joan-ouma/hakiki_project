import asyncio
from fastapi import APIRouter, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.engine.claim import extract_claim

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
    else:
        resp.message(
            f"Claim detected:\n\"{claim}\"\n\n"
            "Verification engine coming soon. Source matching not yet wired."
        )

    return Response(content=str(resp), media_type="text/xml")
