"""Service for managing user quotas."""

from models.user_session import UserSession
from config import Config
from datetime import datetime, date

class QuotaService:
    """Manage and track user usage quotas."""

    def __init__(self):
        self.user_session = UserSession()

    def check_quota(self, user_id: int) -> tuple[bool, int, int]:
        """
        Check if the user has remaining quota for the day.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            Tuple[bool, int, int]: (has_quota, remaining_quota, total_quota)
        """
        usage = self.user_session.get_daily_usage(user_id)
        total_quota = Config.DAILY_QUOTA_FREE
        remaining = max(0, total_quota - usage)
        has_quota = remaining > 0
        return has_quota, remaining, total_quota

    def can_process_text(self, user_id: int, text_length: int) -> bool:
        """
        Determine if the user can process a text of given length.

        Args:
            user_id (int): Telegram user ID.
            text_length (int): Length of the text to process.

        Returns:
            bool: True if allowed, False otherwise.
        """
        if text_length > Config.MAX_TEXT_LENGTH:
            return False
        has_quota, _, _ = self.check_quota(user_id)
        return has_quota

    def increment_usage(self, user_id: int):
        """
        Increment user's daily usage count by 1.

        Args:
            user_id (int): Telegram user ID.
        """
        self.user_session.increment_usage(user_id)

    def get_quota_status(self, user_id: int) -> dict:
        """
        Get detailed quota status for a user.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            dict: Quota information including remaining, used, percentage, and reset time.
        """
        has_quota, remaining, total = self.check_quota(user_id)
        return {
            'has_quota': has_quota,
            'remaining': remaining,
            'total': total,
            'used': total - remaining,
            'percentage_used': ((total - remaining) / total * 100) if total > 0 else 0,
            'reset_time': '00:00 UTC'  # Daily reset time
        }
