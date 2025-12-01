# tests/test_user_session_quota.py
from models.user_session import UserSession
from services.quota_service import QuotaService
from config import Config

def test_quota_tracking():
    """Verify that user session usage increments and quota checks work correctly."""
    us = UserSession()
    user_id = 999

    # Initial usage should be zero
    assert us.get_daily_usage(user_id) == 0

    # Increment usage
    us.increment_usage(user_id)
    assert us.get_daily_usage(user_id) == 1

    # Check quota
    qs = QuotaService()
    has_quota, remaining, total = qs.check_quota(user_id)

    assert total == Config.DAILY_QUOTA_FREE
    assert remaining == total - 1
