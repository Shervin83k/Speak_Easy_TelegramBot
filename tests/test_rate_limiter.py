import pytest
import time
from middleware.rate_limiter import RateLimiter

class DummyUser:
    def __init__(self, user_id):
        self.id = user_id

class DummyMessage:
    text = "hello"

class DummyUpdate:
    def __init__(self, user_id=1):
        self.effective_user = DummyUser(user_id)
        self.message = DummyMessage()
        self.effective_message = self.message

class DummyContext:
    user_data = {}

@pytest.mark.asyncio
async def test_allows_first_n_messages():
    """Ensure first 20 messages are allowed per user."""
    limiter = RateLimiter()
    update = DummyUpdate(1)
    context = DummyContext()

    for _ in range(20):
        assert await limiter.check_rate_limit(update, context) is True

@pytest.mark.asyncio
async def test_blocks_after_limit():
    """Ensure messages beyond the limit are blocked."""
    limiter = RateLimiter()
    update = DummyUpdate(7)
    context = DummyContext()

    for _ in range(20):
        await limiter.check_rate_limit(update, context)

    assert await limiter.check_rate_limit(update, context) is False

@pytest.mark.asyncio
async def test_user_isolation():
    """Ensure one user's rate limit does not affect another user."""
    limiter = RateLimiter()
    context = DummyContext()

    # User 10 hits limit
    for _ in range(20):
        await limiter.check_rate_limit(DummyUpdate(10), context)
    assert await limiter.check_rate_limit(DummyUpdate(10), context) is False

    # User 99 should still be allowed
    assert await limiter.check_rate_limit(DummyUpdate(99), context) is True

@pytest.mark.asyncio
async def test_reset_after_time(monkeypatch):
    """Ensure rate limit resets after 60+ seconds."""
    limiter = RateLimiter()
    update = DummyUpdate(33)
    context = DummyContext()

    for _ in range(20):
        await limiter.check_rate_limit(update, context)

    # Monkeypatch time to simulate passage of 61 seconds
    original_time = time.time()
    monkeypatch.setattr(time, "time", lambda: original_time + 61)

    assert await limiter.check_rate_limit(update, context) is True
