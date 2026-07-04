# Architecture

## System Overview

Hakiki is a multi-channel fact-checking bot that verifies political claims against public records and detects AI-manipulated media. It operates through WhatsApp, SMS, and USSD — meeting users where they already are.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  WhatsApp   │     │     SMS     │     │    USSD     │
│   (Twilio)  │     │ (Africa's   │     │ (Africa's   │
│             │     │  Talking)   │     │  Talking)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   FastAPI   │
                    │   Server    │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
     │   Claim     │ │  Media  │ │   Gender    │
     │   Engine    │ │ Engine  │ │  Detection  │
     └──────┬──────┘ └────┬────┘ └─────────────┘
            │              │
     ┌──────▼──────┐ ┌────▼────┐
     │  Matching   │ │   HF    │
     │ (Seed DB +  │ │ Image   │
     │  AI Check)  │ │ Scoring │
     └──────┬──────┘ └────┬────┘
            │              │
     ┌──────▼──────┐ ┌────▼────┐
     │  Verdict    │ │  Groq   │
     │ Composition │ │ Whisper │
     └─────────────┘ └─────────┘
```

## Directory Structure

```
src/
├── main.py              # FastAPI app, router registration, lifespan
├── config.py            # Environment variable loading
├── store.py             # SQLite DB operations
├── cache.py             # Media fingerprint caching
├── privacy.py           # Phone number hashing (PII protection)
├── channels/
│   ├── whatsapp.py      # Twilio WhatsApp webhook
│   └── atalking.py      # Africa's Talking SMS + USSD webhooks
├── engine/
│   ├── claim.py         # AI claim extraction from text
│   ├── match.py         # Seed DB keyword match + AI fact-check
│   ├── verdict.py       # User-facing verdict composition
│   ├── media.py         # Image AI-detection, audio transcription
│   ├── links.py         # Social media link detection + scraping
│   └── gender.py        # Gendered disinformation detection
├── scripts/
│   └── seed.py          # One-off data scraper + PDF loader
└── tests/
    ├── test_cache.py
    ├── test_claim.py
    ├── test_endpoints.py
    ├── test_gender.py
    ├── test_links.py
    ├── test_match.py
    ├── test_media.py
    ├── test_privacy.py
    ├── test_store.py
    └── test_verdict.py
```

## Data Flow

1. User sends message via WhatsApp/SMS/USSD
2. Channel webhook receives and routes the request
3. If media: download → score for AI manipulation → cache result
4. If voice: transcribe via Groq Whisper (background task)
5. If social link: scrape via Firecrawl for content
6. Extract verifiable claim from text (DeepSeek)
7. Check for gendered disinformation patterns
8. Match claim against seed database (public records)
9. Run AI fact-check for broader assessment
10. Compose verdict with source attribution
11. Return response in user's language

## Key Design Decisions

- **Stateless processing** — no user sessions stored, no PII persisted
- **Background tasks** — voice notes and USSD claims processed async to avoid timeouts
- **Multi-source verification** — seed DB (hard data) + AI assessment (broad coverage)
- **Language flexibility** — AI summary matches user's input language (English/Swahili/Sheng)
- **Privacy by design** — phone numbers hashed before any logging
