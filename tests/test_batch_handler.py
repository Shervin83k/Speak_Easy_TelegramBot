import pytest
from handlers.batch_handler import BatchHandler
from config import Config


@pytest.mark.asyncio
async def test_start_batch_mode(fake_update_and_context):
    """
    Test that starting batch mode sets the correct state and sends a reply.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("start batch")
    context = FakeContext()

    handler = BatchHandler()
    state = await handler.start_batch_mode(update, context)

    assert state == Config.BATCH_MODE
    update.effective_message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_batch_input_simple_text(fake_update_and_context, monkeypatch):
    """
    Test processing simple multi-line batch input.
    Mocks TTS output to avoid real file generation.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("line1\nline2\nline3")
    context = FakeContext()

    handler = BatchHandler()

    # Mock TTS output to a fake file path
    monkeypatch.setattr(
        handler.tts_service,
        "convert_text_to_speech",
        lambda text, speed=1.0: "/tmp/fake_audio.mp3"
    )

    # Mock open to avoid actual file operations
    monkeypatch.setattr("builtins.open", lambda *a, **k: open(__file__, "rb"))

    state = await handler.handle_batch_input(update, context)

    # Should return to main menu (StartHandler.main_menu returns an int normally)
    assert isinstance(state, int)
    assert update.effective_message.reply_text.call_count >= 2


@pytest.mark.asyncio
async def test_batch_rejects_over_max_size(fake_update_and_context):
    """
    Test that batch input exceeding MAX_BATCH_SIZE is rejected
    and user stays in batch mode.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("\n".join([f"text{i}" for i in range(Config.MAX_BATCH_SIZE + 5)]))
    context = FakeContext()

    handler = BatchHandler()
    state = await handler.handle_batch_input(update, context)

    assert state == Config.BATCH_MODE
    update.effective_message.reply_text.assert_called()


@pytest.mark.asyncio
async def test_batch_back_button(fake_update_and_context):
    """
    Test that sending 'Back' exits batch mode and returns main menu state.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("Back")
    context = FakeContext()

    handler = BatchHandler()
    state = await handler.handle_batch_input(update, context)

    assert isinstance(state, int)  # Back returns main menu state
