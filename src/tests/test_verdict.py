"""Tests for src.engine.verdict — verdict composition."""
from unittest.mock import patch
from src.engine.verdict import compose_verdict


@patch("src.engine.verdict._generate_summary", return_value="")
def test_verdict_with_no_matches(mock_summary):
    result = compose_verdict("Ruto built a hospital", {"seed_match": None, "factcheck_match": None})
    assert "UNVERIFIED" in result
    assert "Hakiki Bot" in result


@patch("src.engine.verdict._generate_summary", return_value="According to NG-CDF records, no such project exists.")
def test_verdict_with_seed_match(mock_summary):
    seed = {"source": "NG-CDF", "url": "https://ngcdf.go.ke/test", "constituency": "Changamwe", "project": "Test", "details": "Test"}
    result = compose_verdict("CDF Changamwe", {"seed_match": seed, "factcheck_match": None})
    assert "According to NG-CDF" in result
    assert "https://ngcdf.go.ke/test" in result


@patch("src.engine.verdict._generate_summary", return_value="")
def test_verdict_with_factcheck(mock_summary):
    fc = {"rating": "False", "confidence": 85, "explanation": "No evidence", "source_hint": "Budget data", "publisher": "Hakiki", "url": ""}
    result = compose_verdict("Fake claim", {"seed_match": None, "factcheck_match": fc})
    assert "False" in result
    assert "85%" in result


def test_verdict_with_media_high_ai():
    media = {"ai_probability": 0.9}
    result = compose_verdict(None, None, media_result=media)
    assert "AI-generated" in result
    assert "Do not share" in result


def test_verdict_with_media_authentic():
    media = {"ai_probability": 0.1}
    result = compose_verdict(None, None, media_result=media)
    assert "authentic" in result


def test_verdict_with_media_inconclusive():
    media = {"ai_probability": 0.5}
    result = compose_verdict(None, None, media_result=media)
    assert "can't say for sure" in result


def test_verdict_with_media_error():
    media = {"error": "Could not download"}
    result = compose_verdict(None, None, media_result=media)
    assert "couldn't analyze" in result


def test_verdict_with_transcription():
    result = compose_verdict("Test claim", {"seed_match": None, "factcheck_match": None}, transcription="nimesema hivi")
    assert 'I heard: "nimesema hivi"' in result


def test_verdict_never_exposes_model_name():
    """Verdict should never contain DeepSeek or model names."""
    fc = {"rating": "True", "confidence": 90, "explanation": "Confirmed", "source_hint": "NG-CDF", "publisher": "Hakiki", "url": ""}
    with patch("src.engine.verdict._generate_summary", return_value="Confirmed by Hakiki analysis"):
        result = compose_verdict("test", {"seed_match": None, "factcheck_match": fc})
    assert "deepseek" not in result.lower()
    assert "openai" not in result.lower()
