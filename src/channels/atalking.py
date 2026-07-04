import asyncio
from fastapi import APIRouter, BackgroundTasks, Form
from fastapi.responses import PlainTextResponse

from src.engine.claim import extract_claim
from src.engine.match import match_claim
from src.privacy import hash_phone

router = APIRouter(prefix="/webhook")

# --- SMS ---

SMS_WELCOME = (
    "Hakiki Bot: Tuma madai yoyote ya kisiasa hapa na tutakuambia kama kuna ushahidi "
    "katika rekodi za umma. Mfano: 'CDF Changamwe imeibwa'"
)


@router.post("/sms")
async def sms_webhook(
    from_: str = Form("", alias="from"),
    to: str = Form(""),
    text: str = Form(""),
    date: str = Form(""),
    id: str = Form(""),
):
    """Africa's Talking SMS callback. Returns empty — we reply via AT API."""
    if not text.strip():
        return PlainTextResponse("")

    if text.strip().lower() in ("hi", "hello", "habari", "sasa", "help"):
        _send_sms(from_, SMS_WELCOME)
        return PlainTextResponse("")

    claim = await asyncio.to_thread(extract_claim, text)

    if not claim:
        _send_sms(from_, "Hakiki: Sikupata madai yanayoweza kuthibitishwa. Jaribu kutuma madai maalum kuhusu serikali au siasa.")
        return PlainTextResponse("")

    matches = await asyncio.to_thread(match_claim, claim)
    verdict = _sms_verdict(claim, matches)
    _send_sms(from_, verdict)

    return PlainTextResponse("")


def _sms_verdict(claim: str, matches: dict) -> str:
    """Short SMS-friendly verdict (160 chars target, 320 max)."""
    seed = matches.get("seed_match")
    fc = matches.get("factcheck_match")

    if seed:
        msg = f"Hakiki: Madai '{claim[:50]}' - Tumepata rekodi ya {seed['source']}"
        if seed.get("url"):
            msg += f". Thibitisha: {seed['url']}"
        return msg[:320]
    elif fc:
        msg = f"Hakiki: Madai '{claim[:50]}' - Rating: {fc['rating']} ({fc['publisher']})"
        if fc.get("url"):
            msg += f". {fc['url']}"
        return msg[:320]
    else:
        return f"Hakiki: Madai '{claim[:60]}' - HAIJATHIBITISHWA. Hatukupata ushahidi katika rekodi za umma. Kuwa mwangalifu usisambaze."


def _send_sms(to: str, message: str):
    """Send SMS via Africa's Talking."""
    import africastalking
    from src.config import AT_USERNAME, AT_API_KEY

    if not AT_USERNAME or not AT_API_KEY:
        print(f"[AT SMS] Missing credentials: username={AT_USERNAME!r}")
        return

    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
    try:
        resp = sms.send(message, [to])
        print(f"[AT SMS] Sent to {hash_phone(to)}: {resp.get('SMSMessageData', {}).get('Message', '')}")
    except Exception as e:
        print(f"[AT SMS] Error for {hash_phone(to)}: {e}")


# --- USSD ---

USSD_MENU = {
    "start": (
        "CON Karibu Hakiki Bot\n"
        "1. Angalia madai\n"
        "2. Maelezo kuhusu Hakiki\n"
        "3. Msaada"
    ),
    "info": (
        "END Hakiki ni bot ya kuthibitisha habari za kisiasa Kenya. "
        "Tunatumia rekodi za umma (NG-CDF, Auditor-General) na fact-check databases."
    ),
    "help": (
        "END Chagua '1' kisha andika madai unayotaka kuangalia. "
        "Mfano: 'CDF Changamwe imeibwa' au 'Ruto amejenga hospitali'."
    ),
}


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
async def ussd_webhook(
    sessionId: str = Form(""),
    serviceCode: str = Form(""),
    phoneNumber: str = Form(""),
    text: str = Form(""),
    background_tasks: BackgroundTasks = None,
):
    """Africa's Talking USSD callback. CON = continue session, END = close."""
    parts = text.split("*") if text else []

    if not text:
        return PlainTextResponse(USSD_MENU["start"])

    choice = parts[0]

    if choice == "1":
        if len(parts) == 1:
            return PlainTextResponse("CON Andika madai unayotaka kuangalia:")

        user_claim = "*".join(parts[1:])
        background_tasks.add_task(_process_ussd_claim, user_claim, phoneNumber)
        return PlainTextResponse("END Tumeipokea. Utapata majibu kwa SMS hivi karibuni.")

    elif choice == "2":
        return PlainTextResponse(USSD_MENU["info"])

    elif choice == "3":
        return PlainTextResponse(USSD_MENU["help"])

    else:
        return PlainTextResponse("END Chaguo batili. Jaribu tena.")
