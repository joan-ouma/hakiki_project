from openai import OpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SYSTEM_PROMPT = """You are a Kenyan fact-check assistant. Given a forwarded message (which may be in English, Swahili, Sheng, or a mix), extract the single most specific, checkable factual claim.

Rules:
- Return ONLY the claim as a short, clear sentence in English.
- If the message contains no checkable factual claim (just opinions, greetings, questions), reply exactly: NO_CLAIM
- Do not add commentary, disclaimers, or explanations.
- Focus on claims about politicians, government projects (especially NG-CDF), budgets, or public spending."""


def extract_claim(text: str) -> str | None:
    response = _client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        max_tokens=150,
        temperature=0.1,
    )
    result = response.choices[0].message.content.strip()
    if result == "NO_CLAIM":
        return None
    return result
