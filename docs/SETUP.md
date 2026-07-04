# Setup Guide

## Prerequisites

- Python 3.11+
- A Twilio account (WhatsApp Sandbox)
- An Africa's Talking account (Sandbox)
- API keys for: DeepSeek, Hugging Face, Groq, Firecrawl

## Installation

```bash
git clone https://github.com/your-username/hakiki_project.git
cd hakiki_project
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

Required variables:

| Variable | Purpose | Get it from |
|----------|---------|-------------|
| `TWILIO_ACCOUNT_SID` | WhatsApp messaging | twilio.com/console |
| `TWILIO_AUTH_TOKEN` | WhatsApp auth | twilio.com/console |
| `TWILIO_WHATSAPP_NUMBER` | Sandbox number | Default: `whatsapp:+14155238886` |
| `DEEPSEEK_API_KEY` | Claim extraction + fact-checking | platform.deepseek.com |
| `HF_API_TOKEN` | Image AI-detection | huggingface.co/settings/tokens |
| `GROQ_API_KEY` | Voice transcription (Whisper) | console.groq.com |
| `FIRECRAWL_API_KEY` | Social media link scraping | firecrawl.dev |
| `AT_USERNAME` | Africa's Talking SMS/USSD | africastalking.com |
| `AT_API_KEY` | Africa's Talking auth | africastalking.com |

## Running

```bash
# Start the server
uvicorn src.main:app --reload --port 8000

# Expose locally for webhooks (separate terminal)
ngrok http 8000
```

## Webhook Configuration

### Twilio (WhatsApp)
1. Go to Twilio Console → Messaging → WhatsApp Sandbox
2. Set webhook URL: `https://your-ngrok.ngrok.io/webhook/whatsapp`
3. Method: POST

### Africa's Talking (SMS/USSD)
1. Go to AT Sandbox → SMS → Callback URL
2. Set: `https://your-ngrok.ngrok.io/webhook/sms`
3. For USSD: Sandbox → USSD → Callback URL
4. Set: `https://your-ngrok.ngrok.io/webhook/ussd`

## Seeding the Database

Load public records into the local database:

```bash
# Scrape web sources (requires FIRECRAWL_API_KEY)
python3 -m src.scripts.seed

# Or just load PDFs from data/ folder (no API key needed)
# Drop .pdf files in data/ then run:
python3 -m src.scripts.seed
```

## Running Tests

```bash
python3 -m pytest src/tests/ -v
```

## Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```
