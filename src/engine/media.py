import asyncio
import os
import torch
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# We load the pipelines lazily to avoid heavy initialization on import.
whisper_pipeline = None
vit_pipeline = None

def _load_whisper():
    global whisper_pipeline
    if whisper_pipeline is None:
        print("Loading Whisper Swahili locally...")
        device = 0 if torch.cuda.is_available() else -1
        # Using the iLabAfrica model confirmed in Phase 0
        whisper_pipeline = pipeline(
            "automatic-speech-recognition", 
            model="PaschalK/whisper-swahili-small",
            device=device,
            use_auth_token=os.getenv("HF_API_KEY")
        )
    return whisper_pipeline

def _load_vit():
    global vit_pipeline
    if vit_pipeline is None:
        print("Loading ViT Deepfake Classifier locally...")
        device = 0 if torch.cuda.is_available() else -1
        vit_pipeline = pipeline(
            "image-classification", 
            model="dima806/deepfake_vs_real_image_detection",
            device=device,
            use_auth_token=os.getenv("HF_API_KEY")
        )
    return vit_pipeline

def _process_audio_sync(audio_bytes: bytes) -> str:
    """Synchronous function to transcribe audio via Whisper."""
    pipe = _load_whisper()
    # The pipeline can accept a dict or just bytes if it supports it, 
    # but usually expects a file path or numpy array. 
    # For robust production, write bytes to a temp file first.
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        result = pipe(tmp_path)
        return result.get("text", "")
    except Exception as e:
        print(f"Whisper inference error: {e}")
        return ""
    finally:
        os.remove(tmp_path)

def _process_image_sync(image_bytes: bytes) -> dict:
    """Synchronous function to score image via ViT."""
    pipe = _load_vit()
    from PIL import Image
    import io
    
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = pipe(image)
        # results format: [{'score': 0.99, 'label': 'fake'}, ...]
        # Find the fake score
        fake_score = 0.0
        for r in results:
            if r["label"].lower() == "fake":
                fake_score = r["score"]
        
        return {"fake_probability": fake_score}
    except Exception as e:
        print(f"ViT inference error: {e}")
        return {"fake_probability": 0.0}

async def process_audio(audio_bytes: bytes) -> str:
    """Async wrapper to run inference in a threadpool."""
    return await asyncio.to_thread(_process_audio_sync, audio_bytes)

async def process_image(image_bytes: bytes) -> dict:
    """Async wrapper to run inference in a threadpool."""
    return await asyncio.to_thread(_process_image_sync, image_bytes)
