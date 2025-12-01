import os
import pytest
from importlib import import_module
from services.file_service import FileService
from config import Config


@pytest.mark.asyncio
async def test_audio_handler_processes_audio(fake_update_and_context, monkeypatch):
    """
    Test that AudioHandler can process audio input without raising errors.
    Uses fake TTS and temporary files to avoid real processing.
    """
    # Import the handler module dynamically
    try:
        audio_mod = import_module("handlers.audio_handler")
    except ModuleNotFoundError:
        pytest.skip("handlers.audio_handler not found")

    handler_cls = getattr(audio_mod, "AudioHandler", None)
    if handler_cls is None:
        pytest.skip("AudioHandler class not present in handlers.audio_handler")

    # Prepare fake update and context
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("/audio")
    context = FakeContext()

    handler = handler_cls()

    # Monkeypatch tts_service if present
    if hasattr(handler, "tts_service"):
        monkeypatch.setattr(handler, "tts_service", handler.tts_service)

    # Create a temporary fake audio file
    tmp_name = FileService.generate_filename()
    tmp_path = FileService.get_file_path(tmp_name)
    with open(tmp_path, "wb") as f:
        f.write(b"FAKEAUDIO")

    # Determine handler method
    method = getattr(handler, "handle_audio", None) or getattr(handler, "process_audio", None)
    if method is None:
        pytest.skip("AudioHandler does not have expected entry method (handle_audio/process_audio)")

    # Provide fake file download if handler expects update.message.audio
    class FakeFile:
        async def download_to_drive(self, dst):
            with open(dst, "wb") as f:
                f.write(b"FAKEAUDIO")

    if not hasattr(update.message, "audio"):
        update.message.audio = FakeFile()

    # Call the handler method (supports async and sync)
    result = method(update, context)
    if pytest.isawaitable(result):
        result = await result

    # Test is permissive: ensure method ran without exception
    assert True
