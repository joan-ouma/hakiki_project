from openai import OpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SYSTEM_PROMPT = """You are a Kenyan election fact-check assistant (2027 cycle). Given a forwarded message (which may be in English, Swahili, Sheng, or code-switched), extract the single most specific, verifiable factual claim.

Scope — extract claims about:
- Government projects: NG-CDF allocations, roads, hospitals, schools, water projects
- Public spending: budgets, tenders, misuse of funds
- Politicians: statements attributed to them, their voting records, their wealth
- Election process: voter registration, polling stations, IEBC decisions
- Public health: disease outbreaks, vaccine claims, hospital capacity
- Tribal/ethnic claims: population statistics, land ownership, employment quotas
- Security: crime statistics, police operations, military deployment

Rules:
- Return ONLY the extracted claim as one clear sentence in English.
- If the original is in Swahili/Sheng, translate the claim to English.
- If the message contains no verifiable factual claim (greetings, opinions, questions, jokes), reply exactly: NO_CLAIM
- Do not add commentary or explanation.
- Pick the most specific, checkable claim if multiple are present."""


def extract_claim(text: str) -> str | None:
    try:
        response = _client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=150,
            temperature=0.1,
            timeout=12,
        )
    except Exception:
        return None
    result = response.choices[0].message.content.strip()
    if result == "NO_CLAIM":
        return None
    return result
