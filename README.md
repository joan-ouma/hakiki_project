# Hakiki — The Truth Engine for Kenya's 2027 Elections

> Built during the **Democracy & AI Hackathon** — July 4th, 2026
> Hosted by **Mozilla Foundation** & **KamiLimu**

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| Addy Mutuiri| Backend Engineer | [@Addy](https://github.com/mutuiris) |
| Joan Ouma| Full-Stack Developer | [@joan-ouma](https://github.com/joan-ouma) |

**Team Name:** T004  
**University:** Addy - Kenyatta University, Joan - Jomo Kenyatta University  

---

## Problem & User

### Problem Statement
First-time Generation Z voters aged 18 - 29 in Kenya, especially those who consume political narratives on TikTok and WhatsApp, encounter a high volume of unverified, AI-altered media. While 38% of Kenyans turn to TikTok for news, 55% of users acknowledge the platform as a primary channel for circulating deceptive and misleading content. When political claims and media go viral, citizens have no immediate, accessible way to verify them against official public records.

### Target User

| Dimension | Detail |
|-----------|--------|
| **Primary user** | Gen Z digital natives (WhatsApp/TikTok) and rural citizens (SMS/USSD) |
| **Tech comfort** | Very comfortable with forwarding WhatsApp voice notes and text, or dialing USSD codes. |
| **Language** | Swahili, Sheng, and English |
| **Current workflow** | Hears a rumor on a WhatsApp group or TikTok share, but has no way to fact-check it instantly. |

### The Specific Gap

1. **What's already there:** The Auditor-General publishes detailed NG-CDF audit reports, and organizations track budget transparency.
2. **Why it falls short:** These reports are 200+ page English PDFs hidden on government websites. They require desktop browsers, data bundles, and advanced literacy to parse.
3. **The gap we fill:** Hakiki provides a real-time, zero-data-bundle (SMS/USSD) and rich-media (WhatsApp) chatbot. You forward a claim or video, and Hakiki extracts the facts using LLMs, checks them against a scraped database of real Auditor-General findings, and analyzes media for AI manipulation—all in seconds.

### Why It Matters
When citizens cannot verify claims about constituency spending, accountability dies. By bringing fact-checking directly to the chat apps Kenyans already use every day, we close the information gap, enabling voters to demand answers and participate effectively in the 2027 democratic process.

---

## 🚀 Run Instructions

### Prerequisites
- Python 3.10+
- Ngrok (for testing webhooks)
- API Keys: Twilio, Africa's Talking, DeepSeek, Groq, Firecrawl, Google Fact Check Tools.

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/joan-ouma/hakiki_project.git
cd hakiki_project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Open .env and add your API keys!

# 4. Seed the Database
# Uses Firecrawl and DeepSeek to scrape real Auditor-General news into SQLite.
PYTHONPATH=. python3 scripts/seed.py

# 5. Run the FastAPI Server
uvicorn src.main:app --reload

# 6. Expose to the Internet (in a new terminal)
ngrok http 8000
```
*(Copy the Ngrok URL and set it as your webhook in the Twilio and Africa's Talking consoles!)*

---

## 📁 Project Structure

```
.
├── README.md                   ← You are here
├── src/
│   ├── main.py                 ← FastAPI entry point & Routers
│   ├── config.py               ← Environment variable loader
│   ├── privacy.py              ← Zero-PII stripping & hashing
│   ├── cache.py                ← Media hashing & caching
│   ├── store.py                ← SQLite DB schema logic
│   ├── channels/               
│   │   ├── whatsapp.py         ← Twilio WhatsApp webhook logic
│   └── engine/
│       ├── claim.py            ← DeepSeek claim extraction
│       ├── match.py            ← DB & Google Fact Check matching
│       ├── media.py            ← Groq Whisper & HF ViT inference
│       └── verdict.py          ← Symmetric confidence gating
├── scripts/
│   ├── seed.py                 ← Live Firecrawl NG-CDF scraper
├── data/
│   └── hakiki.db               ← Zero-PII local cache & fact database
└── requirements.txt            
```

---

## 🧠 Architecture & Tech Stack

Hakiki is built as a highly modular, async-first fact-checking engine designed to directly address the technical and ethical constraints of the Kenyan 2027 elections.

### 1. Model Specifics & Design Pivots
*   **Audio Transcription (Groq Whisper):** We initially explored local open-weights models (`PaschalK/whisper-swahili-small`) but encountered integration difficulties and unacceptable inaccuracies with heavy dialects. We pivoted to **Groq's API running `whisper-large-v3`** (an open-weights model). This guarantees lightning-fast transcription capable of handling Swahili and Sheng at the speed required for a real-time WhatsApp bot.
*   **Visual Deepfakes (Hugging Face ViT):** For visual media, we utilize the local Hugging Face model `dima806/deepfake_vs_real_image_detection`. This is a Vision Transformer (ViT) fine-tuned on the "Hard Fake vs Real Faces" dataset, allowing us to detect synthetic alterations directly on our own infrastructure.
*   **Fact Extraction (DeepSeek):** We utilize `deepseek-chat` for LLM reasoning to translate Sheng/Swahili conversational text into concrete, search-ready factual claims.

### 2. Data Layer
`scripts/seed.py` uses Firecrawl to pull live Auditor-General reports directly from Kenyan government and news sites. It uses DeepSeek to intelligently extract the core findings into a local SQLite DB for instant offline matching.

### 3. Responsible Computing: Specific Privacy Mechanisms
To protect vulnerable voters and civic activists from state surveillance, Hakiki implements **Zero-PII Processing by design**. 
*   **Mechanism:** Our `privacy.py` script acts as a middleware gateway. It uses strict RegEx to instantly scrub and salt-hash all phone numbers (`[REDACTED_PHONE]`) *in-memory* before any AI processing or logging occurs. 
*   **Impact:** Absolutely zero personal metadata is written to disk or sent to external inference APIs.

```mermaid
graph TD
  User[User (WhatsApp/SMS)] --> API[FastAPI Webhook]
  API --> Privacy[Zero-PII Filter]
  Privacy --> Media[Groq Whisper / HF ViT]
  Privacy --> Extract[DeepSeek Claim Extraction]
  Media --> Match
  Extract --> Match[Local DB / Google Fact Check]
  Match --> Verdict[Symmetric Confidence Gating]
  Verdict --> User
```

---

## License

MIT © T004, 2026
