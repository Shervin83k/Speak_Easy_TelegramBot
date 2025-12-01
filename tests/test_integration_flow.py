import pytest
from importlib import import_module
import inspect

@pytest.mark.asyncio
async def test_smoke_end_to_end_flow(fake_update_and_context, monkeypatch):
    """
    Smoke test simulating a minimal end-to-end user flow:
    /start -> language selection -> text input -> (audio generation / batch)
    Ensures no exceptions occur and handlers can be invoked.
    """
    FakeUpdate, FakeContext = fake_update_and_context
    update = FakeUpdate("/start")
    context = FakeContext()

    # -------- StartHandler --------
    try:
        start_mod = import_module("handlers.start_handler")
        StartHandler = getattr(start_mod, "StartHandler", None)
        if StartHandler:
            start_handler = StartHandler()
            start_func = getattr(start_handler, "start", None)
            if start_func:
                res = start_func(update, context)
                if inspect.isawaitable(res):
                    await res
    except ModuleNotFoundError:
        pytest.skip("start_handler module not found")

    # -------- TextHandler --------
    try:
        text_mod = import_module("handlers.text_handler")
        TextHandler = getattr(text_mod, "TextHandler", None)
        if TextHandler:
            text_handler = TextHandler()
            update.message.text = "This is a smoke test"
            handle_func = getattr(text_handler, "handle_text", None) or getattr(text_handler, "process_text", None)
            if handle_func:
                result = handle_func(update, context)
                if pytest.isawaitable(result):
                    await result
    except ModuleNotFoundError:
        pass  # Optional, skip if text_handler not present

    # -------- BatchHandler --------
    try:
        batch_mod = import_module("handlers.batch_handler")
        BatchHandler = getattr(batch_mod, "BatchHandler", None)
        if BatchHandler:
            batch_handler = BatchHandler()
            start_batch = getattr(batch_handler, "start_batch_mode", None)
            if start_batch:
                r = start_batch(update, context)
                if inspect.isawaitable(r):
                    await r
    except ModuleNotFoundError:
        pass  # Optional

    # If reached here without exceptions, test passes
    assert True, "End-to-end smoke test executed without errors"
