"""Tests for src.privacy — phone hashing and PII stripping."""
from src.privacy import hash_phone, strip_pii


def test_hash_phone_is_deterministic():
    assert hash_phone("+254712345678") == hash_phone("+254712345678")


def test_hash_phone_different_numbers_differ():
    assert hash_phone("+254712345678") != hash_phone("+254700000000")


def test_hash_phone_returns_16_char_hex():
    result = hash_phone("+254712345678")
    assert len(result) == 16
    assert all(c in "0123456789abcdef" for c in result)


def test_strip_pii_hashes_from_field():
    payload = {"From": "whatsapp:+254712345678", "Body": "hello"}
    result = strip_pii(payload)
    assert result["From"] != "whatsapp:+254712345678"
    assert result["Body"] == "hello"


def test_strip_pii_leaves_other_fields():
    payload = {"Body": "test", "NumMedia": "0"}
    result = strip_pii(payload)
    assert result == payload
