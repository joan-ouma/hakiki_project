"""Tests for src.engine.media — image scoring and audio transcription (mocked HTTP)."""
from unittest.mock import patch, MagicMock
from src.engine.media import score_image, transcribe_audio


def test_score_image_returns_error_without_token():
    with patch("src.engine.media.HF_API_TOKEN", ""):
        result = score_image(b"fake image bytes")
    assert result["error"] is not None
    assert result["score"] is None


def test_score_image_parses_hf_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"label": "artificial", "score": 0.92},
        {"label": "human", "score": 0.08},
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("src.engine.media.HF_API_TOKEN", "test-token"), \
         patch("src.engine.media.httpx.post", return_value=mock_response):
        result = score_image(b"fake image bytes")

    assert result["ai_probability"] == 0.92
    assert result["label"] == "likely AI-generated"


def test_score_image_low_ai_score():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"label": "artificial", "score": 0.1},
        {"label": "human", "score": 0.9},
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("src.engine.media.HF_API_TOKEN", "test-token"), \
         patch("src.engine.media.httpx.post", return_value=mock_response):
        result = score_image(b"fake image")

    assert result["ai_probability"] == 0.1
    assert result["label"] == "likely authentic"


def test_score_image_inconclusive():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"label": "artificial", "score": 0.5},
        {"label": "human", "score": 0.5},
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("src.engine.media.HF_API_TOKEN", "test-token"), \
         patch("src.engine.media.httpx.post", return_value=mock_response):
        result = score_image(b"fake image")

    assert result["label"] == "inconclusive"


def test_transcribe_audio_returns_none_without_key():
    with patch("src.engine.media.GROQ_API_KEY", ""):
        result = transcribe_audio(b"fake audio")
    assert result is None


def test_transcribe_audio_returns_text():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "Ruto amejenga hospitali"}
    mock_response.raise_for_status = MagicMock()

    with patch("src.engine.media.GROQ_API_KEY", "test-key"), \
         patch("src.engine.media.httpx.post", return_value=mock_response):
        result = transcribe_audio(b"fake audio", "audio/ogg")

    assert result == "Ruto amejenga hospitali"


def test_transcribe_audio_returns_none_on_error():
    with patch("src.engine.media.GROQ_API_KEY", "test-key"), \
         patch("src.engine.media.httpx.post", side_effect=Exception("timeout")):
        result = transcribe_audio(b"fake audio")

    assert result is None
