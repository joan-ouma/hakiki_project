import os
from openai import OpenAI

def extract_claim(text: str) -> str:
    """
    Extracts a discrete, checkable claim from raw text (handling Sheng/Swahili).
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # Fallback for when API key is missing
        return "Fallback Claim: " + text.strip()

    # Configure the OpenAI client to hit DeepSeek's base URL
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=10.0)
    
    prompt = f"""
You are a fact-checking assistant for Kenya's 2027 elections.
Extract the core, checkable factual claim from the following message, translating it to clean English if it contains Sheng or Swahili.
If there are no factual claims, return "NO CLAIM FOUND". Do not include any other conversational text.

Message: "{text}"
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return "ERROR_EXTRACTING_CLAIM"
