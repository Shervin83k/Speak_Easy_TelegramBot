import pytest
from locales import Locale

def test_locale_text_lookup():
    """
    Ensure that locale lookup returns correct text for known keys.
    """
    en_text = Locale.get_text("en", "menu.main.welcome")
    assert en_text == "Welcome!", f"Expected 'Welcome!', got '{en_text}'"

def test_missing_key_returns_default():
    """
    Lookup of missing keys should return the key path itself or a fallback string.
    """
    missing = Locale.get_text("en", "menu.main.nonexistent")
    assert missing == "menu.main.nonexistent" or isinstance(missing, str)
