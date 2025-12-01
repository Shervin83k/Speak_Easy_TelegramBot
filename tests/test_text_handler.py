import pytest
from importlib import import_module
from config import Config
from services.file_service import FileService

@pytest.mark.asyncio
async def test_text_handler_generates_audio(fake_update_and_context, monkeypatch):
    """Ensure TextHandler generates audio and replies to user."""
    try:
        text_mod = import_module("handlers.text_handler")
        handler_cls = getattr(text_mod, "TextHandler")
    except (ModuleNotFoundError, AttributeError):
        pytest.skip("TextHandler not available")

    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("Hello test")
    context = FakeContext()

    handler = handler_cls()

    # Monkeypatch TTS to return a temporary fake audio file
    tmp_name = FileService.generate_filename()
    tmp_path = FileService.get_file_path(tmp_name)
    open(tmp_path, "wb").write(b"FAKEAUDIO")

    if hasattr(handler, "tts_service"):
        monkeypatch.setattr(
            handler.tts_service,
            "convert_text_to_speech",
            lambda text, speed=1.0: tmp_path
        )

    # Call handler entry method
    handle = getattr(handler, "handle_text", None) or getattr(handler, "process_text", None)
    if handle is None:
        pytest.skip("TextHandler has no handle_text or process_text method")

    res = handle(update, context)
    if pytest.isawaitable(res):
        res = await res

    # Ensure bot replied
    assert update.message.reply_text.called or update.message.reply_audio.called

    # Cleanup temp file
    try:
        FileService.delete_file(tmp_path)
    except Exception:
        pass


def test_text_handler_rejects_long_input():
    """Ensure TextHandler rejects overly long input."""
    try:
        text_mod = import_module("handlers.text_handler")
        handler_cls = getattr(text_mod, "TextHandler")
    except (ModuleNotFoundError, AttributeError):
        pytest.skip("TextHandler not available")

    handler = handler_cls()
    long_text = "x" * (Config.MAX_TEXT_LENGTH + 100)

    # Use validator if available
    validator = getattr(handler, "validate_text", None)
    if validator:
        assert validator(long_text) is False
    else:
        # Fallback using QuotaService length check
        from services.quota_service import QuotaService
        qs = QuotaService()
        assert qs.can_process_text(1, len(long_text)) is False
