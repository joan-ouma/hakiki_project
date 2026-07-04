from openai import OpenAI
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.engine.gender import detect_gendered_disinfo

_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

SUMMARY_PROMPT = """You are Hakiki, an independent Kenyan fact-check bot. Given a claim and source data, write a brief verdict (3-4 sentences max) that:
1. States what the claim says
2. Says what the NAMED SOURCE shows — always say "According to [source name]..." or "Kulingana na [source name]..." NOT "rekodi zetu" or "our data"
3. Tells the user what to conclude

Rules:
- Match the user's language: if the claim is in English, reply in English. If in Swahili, reply in Swahili. If mixed (Sheng/code-switched), respond in the same casual mix — like a Kenyan would text
- Be direct — no hedging or academic language
- Always name the specific source (e.g. "According to NG-CDF records...", "Kulingana na Finance Bill 2024...", "Per IEBC data...", "Kulingana na Auditor-General report...")
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
        parts.append(f'I heard: "{transcription}"')
        parts.append("")

    if claim:
        parts.append(f'Claim: "{claim}"')
        parts.append("")

    # Check for gendered disinformation
    source_text = claim or transcription or ""
    gender_flag = detect_gendered_disinfo(source_text)
    if gender_flag:
        parts.append("WARNING — GENDERED DISINFORMATION:")
        parts.append("This message contains language targeting a female politician based on gender.")
        parts.append("Research shows such attacks are used systematically to suppress women's political participation.")
        parts.append("Don't share — this is a form of disinformation that harms democracy.")
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
                parts.append(f"Verify here: {seed['url']}")

            if fc:
                rating = fc.get("rating", "")
                confidence = fc.get("confidence", 0)
                explanation = fc.get("explanation", "")
                source_hint = fc.get("source_hint", "")
                parts.append(f"Rating: {rating} ({confidence}% confidence)")
                if explanation:
                    parts.append(f"Reason: {explanation}")
                if source_hint:
                    parts.append(f"Verify with: {source_hint}")

        else:
            parts.append("UNVERIFIED")
            parts.append("We could not find this claim in any public record.")
            parts.append("")
            parts.append("This does NOT mean it's false — it means we can't confirm or deny it right now. Be careful before sharing.")

        parts.append("")

    if media_result:
        if media_result.get("error"):
            parts.append("We couldn't analyze this image right now. Try again later.")
        else:
            prob = media_result.get("ai_probability", 0)
            if prob > 0.7:
                parts.append(f"WARNING: This image appears to be AI-generated ({prob:.0%} confidence).")
                parts.append("Do not share as evidence of a real event.")
                parts.append("")
                parts.append("Remember: AI images (deepfakes) are widely used to manipulate elections. Anyone can create a fake image in seconds.")
            elif prob < 0.3:
                parts.append(f"This image appears authentic ({1-prob:.0%} confidence).")
                parts.append("No signs of AI manipulation detected.")
            else:
                parts.append("We can't say for sure if this image is real or AI-generated.")
                parts.append("Verify with other sources before sharing.")
                parts.append("")
                parts.append("Note: Deepfake technology can create fake images and audio. Don't trust images or video alone — look for the original source.")
        parts.append("")

    parts.append("— Hakiki Bot | Forward any suspicious message to be checked")
    return "\n".join(parts)
