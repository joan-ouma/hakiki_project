import os
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import pipeline

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    print("Error: HF_API_KEY not found in .env")
    exit(1)

# Log in using the token for any gated models
login(token=HF_API_KEY)

try:
    print("Loading Swahili Whisper model locally...")
    # Loading just the tokenizer/config to test network/auth, rather than the whole 1GB model right now
    from transformers import AutoConfig
    config = AutoConfig.from_pretrained("PaschalK/whisper-swahili-small")
    print("Whisper Swahili config loaded successfully!")
    
    print("Loading ViT classifier config locally...")
    config2 = AutoConfig.from_pretrained("dima806/deepfake_vs_real_image_detection")
    print("ViT config loaded successfully!")
    
    print("\nPhase 0 Test passed (Local Transformers Fallback).")
except Exception as e:
    print(f"Error loading models: {e}")
