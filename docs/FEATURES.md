# Features

## Multi-Channel Access

| Channel | Platform | Target User | Requirements |
|---------|----------|-------------|--------------|
| WhatsApp | Twilio Sandbox | Smartphone users (Gen Z) | Internet + WhatsApp |
| SMS | Africa's Talking | Basic phone users | Cellular network |
| USSD | Africa's Talking | Feature phone users (rural) | Cellular network, no internet |

## Core Capabilities

### 1. Claim Extraction
- Accepts text in English, Swahili, Sheng, or code-switched
- Extracts the most specific, verifiable factual claim
- Covers: politics, government projects, health, elections, security, ethnic claims

### 2. Fact Verification
- **Seed Database**: Keyword matching against scraped public records (NG-CDF, Auditor-General, Treasury, IEBC, Parliament, Health Ministry)
- **AI Fact-Check**: Broader assessment with confidence rating and source hints
- **PDF Loading**: Drop any PDF (finance bills, reports) into `data/` for instant searchability

### 3. AI-Generated Image Detection
- Scores images using Hugging Face's AI-image-detector model
- Returns probability (0-1) of AI generation
- Caches results by SHA256 fingerprint to avoid re-processing
- Includes digital literacy education in responses

### 4. Voice Note Analysis
- Transcribes audio via Groq Whisper (optimized for Swahili)
- Extracts claims from transcription
- Runs full verification pipeline
- Processed as background task to avoid Twilio timeout

### 5. Social Media Link Checking
- Detects TikTok, X (Twitter), Facebook, Instagram URLs
- Scrapes content via Firecrawl
- Extracts and verifies claims from scraped text
- Fallback: asks user for caption if scraping fails

### 6. Gendered Disinformation Detection
- Flags messages containing gendered attack patterns
- Detects: body-shaming, sexual slurs, emotional framing, kitchen tropes
- Recognizes attacks against known Kenyan female politicians
- Warns users that such content is systematic political suppression

### 7. Digital Literacy Nudges
- Educates users about deepfakes when AI-generated images are detected
- Explains the "liar's dividend" concept in simple language
- Encourages verification from original sources

## Privacy

- No phone numbers stored in any database
- All logging uses SHA256-hashed identifiers
- No PII in server logs
- No user sessions or conversation history retained

## Language Support

- Input: English, Swahili, Sheng, code-switched
- Output: Matches user's language automatically
- Static labels in English for universal readability
- AI-generated summaries in user's input language
