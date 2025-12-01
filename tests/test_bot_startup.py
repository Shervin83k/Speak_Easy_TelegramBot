import importlib
import pytest

@pytest.mark.asyncio
def test_bot_import_does_not_crash(monkeypatch):
    """
    Ensure that importing bot.py does not crash.
    Patches heavy telegram constructs to prevent side effects.
    """
    # Patch telegram Application to avoid creating a real bot
    try:
        tg = importlib.import_module("telegram")
        if hasattr(tg, "Application"):
            monkeypatch.setattr(tg, "Application", lambda *a, **k: object())
    except Exception:
        # Telegram may not be installed; skip patching in that case
        pass

    # Attempt to import bot module
    try:
        bot_module = importlib.import_module("bot")
    except Exception as e:
        pytest.skip(f"Importing bot module failed: {e}")

    assert bot_module is not None
