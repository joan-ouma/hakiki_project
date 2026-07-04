import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    print("Error: HF_API_KEY not found in .env")
    exit(1)

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def test_whisper():
    print("Testing Whisper Swahili (ilabafrica/whisper-swahili)...")
    API_URL = "https://api-inference.huggingface.co/models/ilabafrica/whisper-swahili"
    # Sending a tiny empty audio file or some dummy bytes just to see if the model loads/responds
    dummy_data = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    response = requests.post(API_URL, headers=headers, data=dummy_data)
    print("Response:", response.status_code, response.json())

def test_vit():
    print("\nTesting ViT Real-vs-Fake Image Classifier (dima806/deepfake_vs_real_image_detection)...")
    # A known deepfake detection model on HF
    API_URL = "https://api-inference.huggingface.co/models/dima806/deepfake_vs_real_image_detection"
    # Dummy 1x1 black pixel PNG
    dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    response = requests.post(API_URL, headers=headers, data=dummy_image)
    print("Response:", response.status_code, response.json())

if __name__ == "__main__":
    test_whisper()
    test_vit()
