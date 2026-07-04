"""Tests for src.cache — media fingerprinting and cache lookup."""
from unittest.mock import patch
from src.cache import fingerprint, check_cache, save_to_cache


def test_fingerprint_is_sha256():
    result = fingerprint(b"test data")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_fingerprint_same_input_same_output():
    assert fingerprint(b"hello") == fingerprint(b"hello")


def test_fingerprint_different_input_different_output():
    assert fingerprint(b"hello") != fingerprint(b"world")


def test_check_cache_returns_none_for_unknown():
    result = check_cache(b"never-seen-before-data-xyz-12345")
    assert result is None


def test_save_and_retrieve_cache():
    data = b"unique-test-media-bytes-for-cache-test"
    verdict = {"ai_probability": 0.85, "label": "likely AI-generated"}

    save_to_cache(data, verdict)
    result = check_cache(data)

    assert result is not None
    assert result["ai_probability"] == 0.85
    assert result["label"] == "likely AI-generated"
