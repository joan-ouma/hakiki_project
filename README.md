# Hakiki

> Built during the **Democracy & AI Hackathon** — July 4th, 2026
> Hosted by **Mozilla Foundation** & **KamiLimu**

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| Addy Mutuiri| Backend Engineer | [@Addy](https://github.com/mutuiris) |
| Joan Ouma| Full-Stack Developer | [@Joan](https://github.com/joan-ouma)


**Team Name:** T004
**University:** Addy - Kenyatta University
                Joan - Jomo Kenyatta University
                

---

## Problem & User

### Problem Statement
First time Generation Z voters aged 18 - 29 in Kenya, especially those who consume political
narratives on TikTok, encounter a high volume of unverified, AI altered media. With internet
subscriptions exceeding 40 million, TikTok has secured a 30.3% share of the local market. The 2025
Reuters Institute Digital News Report indicates that while 38% of Kenyans turn to TikTok for news,
55% of users acknowledge the platform as a primary channel for circulating deceptive and misleading
content.


### Target User

<!-- Who specifically are you building for? Be as concrete as possible. -->

| Dimension | Detail |
|-----------|--------|
| **Primary user** | [e.g. A smallholder farmer in Migori County who uses WhatsApp daily] |
| **Tech comfort** | [e.g. Comfortable with WhatsApp voice notes and text; no email] |
| **Language** | [e.g. Swahili, Sheng, Dholuo — not English] |
| **Current workflow** | [e.g. Hears about projects from local radio or baraza, has no way to verify] |

### The Specific Gap

<!-- What exists today? What's the precise gap your solution fills? -->

1. **What's already there:** [e.g. International Budget Partnership Kenya's County Budget Transparency Survey; Auditor-General audit reports]
2. **Why it falls short:** [e.g. Published as 200+ page English PDFs; require desktop browser, stable internet, and advanced literacy]
3. **The gap we fill:** [e.g. Real-time, simplified Swahili/Sheng summaries delivered on WhatsApp — no PDFs, no English, no desktop required]

### Why It Matters

<!-- Connect this to democratic participation. -->

> [e.g. When rural citizens can't track county spending, projects stall, funds divert, and the accountability loop between citizen and government breaks. Closing this information gap restores a basic democratic feedback mechanism: informed citizens can ask better questions, demand answers, and vote accordingly.]

---

## Run Instructions

### Prerequisites

- Python 3.10+
- [Add any other dependencies: Node.js, Docker, API keys, etc.]

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/[org]/[repo].git
cd [repo]

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run the project
python src/main.py
```

---

## 📁 Project Structure

```
.
├── README.md                   ← You are here
├── docs/
│   └── problem-statement.md    ← Detailed problem breakdown
├── src/
│   └── main.py                 ← Entry point
├── notebooks/
│   └── exploration.ipynb       ← Experiments & prototyping
├── data/
│   └── .gitkeep                ← Sample / reference data
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## Approach & Architecture

<!--
Briefly describe your approach. What technologies are you using?
Include a simple diagram (ASCII or link) if helpful.

Examples:
- "We use Retrieval-Augmented Generation (RAG) to query county budget PDFs…"
- "We cross-validate enrolment data against capitation flows using…"
-->

```
[User] → [WhatsApp / Web App] → [Backend / API] → [LLM / RAG Pipeline] → [Response]
```

---

## License

MIT © T004, 2026

---
