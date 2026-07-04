"""Tests for src.engine.gender — gendered disinformation detection."""
from src.engine.gender import detect_gendered_disinfo


def test_detects_slay_queen():
    result = detect_gendered_disinfo("She is just a slay queen, not a leader")
    assert result is not None
    assert result["flagged"] is True


def test_detects_swahili_slur():
    result = detect_gendered_disinfo("Huyu ni malaya tu, hawezi kuongoza")
    assert result is not None
    assert result["flagged"] is True


def test_detects_emotional_framing():
    result = detect_gendered_disinfo("Martha Karua is too aggressive to be deputy president")
    assert result is not None
    assert result["targets_known_politician"] is True


def test_detects_kitchen_trope():
    result = detect_gendered_disinfo("Go back to kitchen mama, politics is for men")
    assert result is not None


def test_detects_sex_tape_disinfo():
    result = detect_gendered_disinfo("Have you seen the leaked video of Waiguru?")
    assert result is not None
    assert result["targets_known_politician"] is True


def test_clean_political_text_returns_none():
    result = detect_gendered_disinfo("CDF Changamwe has allocated 50 million for roads")
    assert result is None


def test_legitimate_criticism_not_flagged():
    result = detect_gendered_disinfo("The governor failed to deliver on her campaign promises about water projects")
    assert result is None
