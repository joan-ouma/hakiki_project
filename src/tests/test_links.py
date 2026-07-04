"""Tests for src.engine.links — social media link detection."""
from src.engine.links import extract_link


def test_extract_tiktok_link():
    text = "Look at this https://vm.tiktok.com/ZMrY1234/ ni uongo"
    assert extract_link(text) == "https://vm.tiktok.com/ZMrY1234/"


def test_extract_tiktok_www():
    text = "check https://www.tiktok.com/@user/video/123456 hii"
    result = extract_link(text)
    assert result is not None
    assert "tiktok.com" in result


def test_extract_x_link():
    text = "Alishare hii https://x.com/user/status/12345678"
    result = extract_link(text)
    assert result is not None
    assert "x.com" in result


def test_extract_twitter_link():
    text = "see https://twitter.com/user/status/9999"
    result = extract_link(text)
    assert "twitter.com" in result


def test_extract_facebook_link():
    text = "https://www.facebook.com/watch?v=123 is fake"
    result = extract_link(text)
    assert "facebook.com" in result


def test_extract_instagram_link():
    text = "Watch https://www.instagram.com/reel/ABC123/"
    result = extract_link(text)
    assert "instagram.com" in result


def test_no_link_returns_none():
    assert extract_link("Habari yako? CDF imeibwa") is None


def test_non_social_link_returns_none():
    assert extract_link("visit https://www.google.com/search") is None
