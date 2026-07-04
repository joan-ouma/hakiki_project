from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter(prefix="/webhook")


@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
):
    # ponytail: Phase 1 tracer bullet — hardcoded verdict, swap for engine call in Phase 3+
    resp = MessagingResponse()
    resp.message(
        "Hakiki received your message. Verdict: [placeholder]. "
        "Source: demo mode."
    )
    return str(resp)
