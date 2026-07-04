"""Tests for src.engine.claim — claim extraction (mocked AI calls)."""
from unittest.mock import patch, MagicMock
from src.engine.claim import extract_claim


def _mock_response(content):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch("src.engine.claim._client")
def test_extract_claim_returns_claim(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response(
        "Ruto built a hospital in Nairobi in 2024."
    )
    result = extract_claim("Ruto amejenga hospitali Nairobi")
    assert result == "Ruto built a hospital in Nairobi in 2024."


@patch("src.engine.claim._client")
def test_extract_claim_returns_none_for_no_claim(mock_client):
    mock_client.chat.completions.create.return_value = _mock_response("NO_CLAIM")
    result = extract_claim("habari yako?")
    assert result is None


@patch("src.engine.claim._client")
def test_extract_claim_returns_none_on_exception(mock_client):
    mock_client.chat.completions.create.side_effect = Exception("timeout")
    result = extract_claim("some text")
    assert result is None
