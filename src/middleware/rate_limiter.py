import time
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import bot_logger


class RateLimiter:
    """Simple per-user rate limiter using a 1-minute sliding window."""

    def __init__(self):
        self.user_requests = {}

    async def check_rate_limit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Check if the user has exceeded the allowed request rate.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Telegram context object.

        Returns:
            bool: True if under the rate limit, False if exceeded.
        """
        user_id = update.effective_user.id
        current_time = time.time()

        if user_id not in self.user_requests:
            self.user_requests[user_id] = []

        # Remove requests older than 60 seconds
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < 60
        ]

        # Check against limit (consider using Config.RATE_LIMIT_PER_MINUTE)
        if len(self.user_requests[user_id]) >= 20:
            bot_logger.warning(f"Rate limit exceeded for user {user_id}")
            return False

        # Record current request
        self.user_requests[user_id].append(current_time)
        return True
