# API Reference

## Endpoints

### GET /health

Health check.

**Response:** `{"status": "ok"}`

---

### POST /webhook/whatsapp

Twilio WhatsApp webhook. Accepts form-encoded data, returns TwiML XML.

**Form fields:**
| Field | Type | Description |
|-------|------|-------------|
| `Body` | string | Message text |
| `From` | string | Sender (e.g. `whatsapp:+254...`) |
| `NumMedia` | int | Number of media attachments |
| `MediaUrl0` | string | URL of first media attachment |
| `MediaContentType0` | string | MIME type of first attachment |

**Supported inputs:**
- Text claims (English, Swahili, Sheng)
- Images (AI-detection scoring)
- Voice notes (transcription + claim check)
- Social media links (TikTok, X, Facebook, Instagram)

**Response:** `text/xml` TwiML

---

### POST /webhook/sms

Africa's Talking SMS callback. Returns empty — replies sent via AT API.

**Form fields:**
| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Sender phone number |
| `to` | string | Shortcode/number |
| `text` | string | SMS body |
| `date` | string | Timestamp |
| `id` | string | Message ID |

**Response:** Empty 200

---

### POST /webhook/ussd

Africa's Talking USSD callback. Returns `CON` (continue) or `END` (close session).

**Form fields:**
| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | string | USSD session ID |
| `serviceCode` | string | USSD code dialed |
| `phoneNumber` | string | User's phone |
| `text` | string | Accumulated input (e.g. `1*CDF imeibwa`) |

**USSD Menu:**
```
1. Angalia madai (Check a claim)
2. Maelezo kuhusu Hakiki (About)
3. Msaada (Help)
```

**Response:** Plain text prefixed with `CON` or `END`

---

## External Services

| Service | Purpose | Endpoint |
|---------|---------|----------|
| DeepSeek | Claim extraction, fact-checking, verdict generation | `api.deepseek.com` |
| Hugging Face | Image AI-detection (`umm-maybe/AI-image-detector`) | `router.huggingface.co` |
| Groq | Audio transcription (Whisper large-v3, Swahili) | `api.groq.com` |
| Firecrawl | Social media link scraping | `api.firecrawl.dev` |
| Twilio | WhatsApp messaging | `api.twilio.com` |
| Africa's Talking | SMS + USSD | `api.africastalking.com` |
