import json
import os
import pytest
from config import Config

REQUIRED_KEYS = [
    "menu.main.welcome",
    "audio.generating",
    "text_input.prompt",
    "batch.prompt",
    "batch.max_size",
    "errors.unexpected"
]

def _load_locale(lang: str) -> dict:
    """Load locale JSON file for a given language."""
    path = os.path.join(Config.LOCALES_DIR, f"{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _has_dotted_key(d: dict, key: str) -> bool:
    """Check if a nested dotted key exists in a dictionary."""
    current = d
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return True

def test_locale_top_level_keys_exist():
    """Ensure top-level locale sections exist in all languages."""
    en = _load_locale("en")
    fa = _load_locale("fa")

    top_keys = ["menu", "audio", "text_input", "batch", "errors"]
    for key in top_keys:
        assert key in en, f"Missing top-level key '{key}' in English locale"
        assert key in fa, f"Missing top-level key '{key}' in Persian locale"

def test_required_keys_present_in_all_locales():
    """Ensure required dotted keys exist in all locales."""
    for lang in ["en", "fa"]:
        locale = _load_locale(lang)
        for key in REQUIRED_KEYS:
            assert _has_dotted_key(locale, key), f"Missing key '{key}' in {lang} locale"
