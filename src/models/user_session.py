import sqlite3
from datetime import date
from config import Config


class UserSession:
    """Manages user session data and daily usage tracking using SQLite."""

    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Create the users table if it does not exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'en',
                    tier TEXT DEFAULT 'free',
                    daily_usage INTEGER DEFAULT 0,
                    last_reset_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_user_language(self, user_id: int) -> str:
        """Retrieve the preferred language of a user."""
        cursor = self.conn.execute(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else Config.DEFAULT_LANGUAGE

    def set_user_language(self, user_id: int, language: str):
        """Set or update the preferred language for a user."""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO users (user_id, language) 
                VALUES (?, ?)
            """, (user_id, language))

    def get_daily_usage(self, user_id: int) -> int:
        """Get the user's daily usage, resetting if needed."""
        self._reset_daily_usage_if_needed(user_id)
        cursor = self.conn.execute(
            "SELECT daily_usage FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0

    def increment_usage(self, user_id: int):
        """Increment the user's daily usage by 1."""
        self._reset_daily_usage_if_needed(user_id)
        with self.conn:
            self.conn.execute("""
                INSERT INTO users (user_id, daily_usage, last_reset_date)
                VALUES (?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET 
                    daily_usage = daily_usage + 1
            """, (user_id, date.today()))

    def _reset_daily_usage_if_needed(self, user_id: int):
        """Reset daily usage if the last reset date is not today."""
        cursor = self.conn.execute(
            "SELECT last_reset_date FROM users WHERE user_id = ?", (user_id,)
        )
        result = cursor.fetchone()
        if result and result[0] != str(date.today()):
            with self.conn:
                self.conn.execute("""
                    UPDATE users
                    SET daily_usage = 0, last_reset_date = ?
                    WHERE user_id = ?
                """, (date.today(), user_id))

    def get_remaining_quota(self, user_id: int) -> int:
        """Return the remaining daily quota for the user."""
        usage = self.get_daily_usage(user_id)
        quota = Config.DAILY_QUOTA_FREE  # Free tier default
        return max(0, quota - usage)
