import anthropic
import os

def extract_claim(text: str) -> str:
    """
    Extracts a discrete, checkable claim from raw text (handling Sheng/Swahili).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback for when API key is missing (e.g. testing tracer bullet without Anthropic key)
        return "Fallback Claim: " + text.strip()

    client = anthropic.Anthropic(api_key=api_key, timeout=10.0)
    
    prompt = f"""
You are a fact-checking assistant for Kenya's 2027 elections.
Extract the core, checkable factual claim from the following message, translating it to clean English if it contains Sheng or Swahili.
If there are no factual claims, return "NO CLAIM FOUND". Do not include any other conversational text.

Message: "{text}"
    """
    
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Anthropic API error: {e}")
        return "ERROR_EXTRACTING_CLAIM"
