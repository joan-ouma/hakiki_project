from openai import OpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SUMMARY_PROMPT = """You are Hakiki, an independent Kenyan fact-check bot. Given a claim and source data, write a brief verdict (3-4 sentences max) that:
1. States what the claim says
2. Says what the NAMED SOURCE shows — always say "Kulingana na [source name]..." NOT "rekodi zetu" or "data yetu"
3. Tells the user what to conclude

Rules:
- Write in simple English mixed with Swahili where natural (like a Kenyan would text)
- Be direct — no hedging or academic language
- Always name the specific source (e.g. "Kulingana na NG-CDF...", "Kulingana na Kenya Finance Bill 2024...", "Kulingana na IEBC records...", "Kulingana na Auditor-General report...")
- Sources can be anything public: government budgets, finance bills, IEBC data, health records, Kenya Gazette, parliamentary Hansard, audit reports, treasury data — cite whatever is relevant
- Never fabricate information not in the source data
- Never say "our data" or "our records" — you are an independent checker pointing to public sources
- End with a clear recommendation: share, don't share, or verify further"""


def _generate_summary(claim: str, source_data: dict, source_type: str) -> str:
    """Use DeepSeek to generate a contextual summary from claim + source."""
    context = f"Source type: {source_type}\n"
    for k, v in source_data.items():
        if v and k != "raw":
            context += f"{k}: {v}\n"

    try:
        response = _client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": f"Claim: {claim}\n\nSource data:\n{context}"},
            ],
            max_tokens=200,
            temperature=0.3,
            timeout=10,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def compose_verdict(claim: str | None, matches: dict | None, media_result: dict | None = None, transcription: str | None = None) -> str:
    """Compose a user-friendly sourced verdict with AI-generated summary."""
    parts = []

    if transcription:
        parts.append(f'Nilisikia: "{transcription}"')
        parts.append("")

    if claim:
        parts.append(f'Madai: "{claim}"')
        parts.append("")

    if matches:
        seed = matches.get("seed_match")
        fc = matches.get("factcheck_match")

        if seed or fc:
            source_for_summary = seed if seed else fc
            source_type = "Public Government Record" if seed else "Hakiki Fact-Check"
            summary = _generate_summary(claim or "", source_for_summary or {}, source_type)

            if summary:
                parts.append(summary)
                parts.append("")

            if seed and seed.get("url"):
                parts.append(f"Thibitisha hapa: {seed['url']}")

            if fc:
                rating = fc.get("rating", "")
                confidence = fc.get("confidence", 0)
                explanation = fc.get("explanation", "")
                source_hint = fc.get("source_hint", "")
                parts.append(f"Tathmini: {rating} ({confidence}% uhakika)")
                if explanation:
                    parts.append(f"Sababu: {explanation}")
                if source_hint:
                    parts.append(f"Chanzo cha kuthibitisha: {source_hint}")

        else:
            parts.append("HAIJATHIBITISHWA")
            parts.append("Hatukupata madai haya katika rekodi yoyote ya umma.")
            parts.append("")
            parts.append("Hii HAIMAANISHI ni uongo — inamaanisha hatuwezi kuthibitisha au kukanusha kwa sasa. Kuwa mwangalifu kabla ya kusambaza.")

        parts.append("")

    if media_result:
        if media_result.get("error"):
            parts.append("Hatukuweza kuchunguza picha hii kwa sasa. Jaribu tena baadaye.")
        else:
            prob = media_result.get("ai_probability", 0)
            if prob > 0.7:
                parts.append(f"Picha hii inaonekana kutengenezwa na AI ({prob:.0%} uhakika).")
                parts.append("Usisambaze kama ushahidi wa tukio halisi.")
            elif prob < 0.3:
                parts.append(f"Picha hii inaonekana ni halisi ({1-prob:.0%} uhakika).")
                parts.append("Hakuna dalili za kuhaririwa na AI.")
            else:
                parts.append("Hatuwezi kusema kwa uhakika kama picha hii ni halisi au ya AI.")
                parts.append("Thibitisha na vyanzo vingine kabla ya kusambaza.")
        parts.append("")

    parts.append("— Hakiki Bot | Forward ujumbe wowote wa kushuku ukaguliwe")
    return "\n".join(parts)
