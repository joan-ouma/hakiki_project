from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

from src.privacy import strip_pii, hash_phone_number
from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.engine.verdict import compose_verdict

router = APIRouter()

@router.post("/sms")
def sms_webhook(
    phoneNumber: str = Form(...),
    text: str = Form(...)
):
    """
    Handles incoming Africa's Talking SMS messages.
    """
    hashed_user = hash_phone_number(phoneNumber)
    clean_text = strip_pii(text)
    
    claim = extract_claim(clean_text)
    match = match_claim(claim)
    
    # Media score is None since SMS cannot carry media
    reply_text = compose_verdict(claim, match, media_score=None)
    
    # Africa's Talking SMS just expects a 200 OK or basic string, but usually 
    # replies are sent via their REST API. However, some AT configs allow responding directly.
    # To be safe and demo-ready without complex REST API outbound, we'll return PlainText.
    return PlainTextResponse(reply_text)

async def _process_ussd_claim(user_claim: str, phone: str):
    """Background: extract claim, match, send verdict via SMS."""
    try:
        claim = extract_claim(user_claim)
        if not claim:
            _send_sms(phone, "Hakiki: Sikupata madai yanayoweza kuthibitishwa. Jaribu madai maalum kuhusu serikali au siasa.")
            return
        matches = match_claim(claim)
        verdict = _sms_verdict(claim, matches)
        _send_sms(phone, verdict)
    except Exception as e:
        print(f"[USSD] Background error for {hash_phone(phone)}: {e}")
        _send_sms(phone, "Hakiki: Samahani, huduma haipatikani kwa sasa. Jaribu tena baadaye.")


@router.post("/ussd")
def ussd_webhook(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(...)
):
    """
    Handles incoming Africa's Talking USSD sessions.
    """
    hashed_user = hash_phone_number(phoneNumber)
    
    # AT USSD text comes as a chain of inputs separated by '*'. 
    # E.g. "1*2*Claim"
    inputs = text.split('*') if text else []
    
    if len(inputs) == 0 or inputs[0] == "":
        # Initial menu
        response = "CON Welcome to Hakiki Fact Check.\n"
        response += "Please type the claim you want to verify:\n"
    else:
        # We assume the last input is the claim they typed.
        user_input = inputs[-1]
        clean_input = strip_pii(user_input)
        
        claim = extract_claim(clean_input)
        match = match_claim(claim)
        reply_text = compose_verdict(claim, match, media_score=None)
        
        # End session
        response = f"END {reply_text}"
        
    return PlainTextResponse(response)
