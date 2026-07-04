"""Tests for API endpoints — no external API calls, mocked AI."""
from unittest.mock import patch, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app

pytestmark = pytest.mark.anyio


@pytest.fixture
def transport():
    return ASGITransport(app=app)


async def test_health(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_whatsapp_webhook_greeting_returns_twiml(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/whatsapp",
            data={"From": "whatsapp:+254700000000", "Body": "hi", "NumMedia": "0"},
        )
    assert resp.status_code == 200
    assert "text/xml" in resp.headers.get("content-type", "")
    assert "<Response>" in resp.text


async def test_whatsapp_webhook_claim_returns_twiml(transport):
    with patch("src.channels.whatsapp.extract_claim", return_value="Test claim"), \
         patch("src.channels.whatsapp.match_claim", return_value={"seed_match": None, "factcheck_match": None}), \
         patch("src.channels.whatsapp.compose_verdict", return_value="Test verdict"):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/webhook/whatsapp",
                data={"From": "whatsapp:+254700000000", "Body": "CDF Changamwe stolen", "NumMedia": "0"},
            )
    assert resp.status_code == 200
    assert "text/xml" in resp.headers.get("content-type", "")


async def test_sms_webhook_greeting(transport):
    with patch("src.channels.atalking._send_sms") as mock_send:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/webhook/sms",
                data={"from": "+254700000000", "to": "12345", "text": "hello", "date": "", "id": "1"},
            )
    assert resp.status_code == 200
    assert resp.text == ""
    mock_send.assert_called_once()


async def test_sms_webhook_empty_text(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/sms",
            data={"from": "+254700000000", "to": "12345", "text": "", "date": "", "id": "1"},
        )
    assert resp.status_code == 200
    assert resp.text == ""


async def test_ussd_returns_menu(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/ussd",
            data={"sessionId": "s1", "serviceCode": "*384*123#", "phoneNumber": "+254700000000", "text": ""},
        )
    assert resp.status_code == 200
    assert resp.text.startswith("CON")
    assert "Angalia madai" in resp.text


async def test_ussd_option_2_info(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/ussd",
            data={"sessionId": "s1", "serviceCode": "*384*123#", "phoneNumber": "+254700000000", "text": "2"},
        )
    assert resp.status_code == 200
    assert resp.text.startswith("END")
    assert "Hakiki" in resp.text


async def test_ussd_option_3_help(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/ussd",
            data={"sessionId": "s1", "serviceCode": "*384*123#", "phoneNumber": "+254700000000", "text": "3"},
        )
    assert resp.status_code == 200
    assert resp.text.startswith("END")
    assert "Mfano" in resp.text


async def test_ussd_invalid_choice(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/webhook/ussd",
            data={"sessionId": "s1", "serviceCode": "*384*123#", "phoneNumber": "+254700000000", "text": "9"},
        )
    assert resp.status_code == 200
    assert resp.text.startswith("END")


async def test_ussd_claim_sends_sms(transport):
    with patch("src.channels.atalking.extract_claim", return_value="Test claim"), \
         patch("src.channels.atalking.match_claim", return_value={"seed_match": None, "factcheck_match": None}), \
         patch("src.channels.atalking._send_sms") as mock_sms:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/webhook/ussd",
                data={"sessionId": "s1", "serviceCode": "*384*123#", "phoneNumber": "+254700000000", "text": "1*CDF imeibwa"},
            )
    assert resp.status_code == 200
    assert "SMS" in resp.text
    mock_sms.assert_called_once()
