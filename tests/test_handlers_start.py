import pytest
from handlers.start_handler import StartHandler
from config import Config

@pytest.mark.asyncio
async def test_start_handler_starts_language_selection(fake_update_and_context):
    """
    Test that /start command triggers language selection state.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("/start")
    context = FakeContext()
    handler = StartHandler()

    # Call start handler
    state = await handler.start(update, context)

    # Assert correct state returned
    assert state == Config.LANGUAGE_SELECTION, "StartHandler should return LANGUAGE_SELECTION state"
    update.effective_message.reply_text.assert_called()
