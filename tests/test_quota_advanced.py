import pytest
from config import Config
from services.quota_service import QuotaService
from models.user_session import UserSession

@pytest.mark.asyncio
def test_quota_status_percentage(monkeypatch, tmp_path):
    """
    Test that usage increments correctly and percentage used is calculated.
    """
    # Redirect database to a temp path
    monkeypatch.setattr(Config, "DATABASE_PATH", tmp_path / "quota_test.db")

    user_session = UserSession()
    quota_service = QuotaService()
    user_id = 42

    # Ensure starting at 0 usage
    assert user_session.get_daily_usage(user_id) == 0

    # Increment usage twice
    user_session.increment_usage(user_id)
    user_session.increment_usage(user_id)

    # Get quota status
    status = quota_service.get_quota_status(user_id)

    assert status["used"] == 2
    assert status["total"] == Config.DAILY_QUOTA_FREE
    assert 0 <= status["percentage_used"] <= 100
    assert status["remaining"] == Config.DAILY_QUOTA_FREE - 2

def test_free_quota_behavior():
    """
    Verify free-tier quota behaves as expected.
    """
    quota_service = QuotaService()
    user_id = 9999

    has_quota, remaining, total = quota_service.check_quota(user_id)

    assert total == Config.DAILY_QUOTA_FREE
    assert has_quota is True or remaining == 0
    assert remaining <= total
