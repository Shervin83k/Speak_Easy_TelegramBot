import pytest
from config import Config

def test_telegram_token_can_be_overridden(monkeypatch):
    """
    Ensure TELEGRAM_TOKEN can be set and read correctly.
    """
    monkeypatch.setattr(Config, "TELEGRAM_TOKEN", "TEST_TOKEN")
    assert Config.TELEGRAM_TOKEN == "TEST_TOKEN"
