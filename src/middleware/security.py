"""Security middleware for Telegram bot."""
import re
from telegram import Update
from telegram.ext import ContextTypes


class SecurityMiddleware:
    """Middleware for sanitizing input, validating filenames, and rate limiting."""

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Remove potentially dangerous content from input text.

        Args:
            text (str): User input text.

        Returns:
            str: Sanitized text.
        """
        if not text:
            return text

        # Remove HTML/JS tags
        sanitized = re.sub(r'<[^>]*>', '', text)

        # Remove suspicious patterns
        suspicious_patterns = [
            r'javascript:', r'vbscript:', r'on\w+=',
            r'data:', r'alert\(', r'eval\(', r'expression\('
        ]
        for pattern in suspicious_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate uploaded filename to prevent security issues.

        Args:
            filename (str): Name of the uploaded file.

        Returns:
            bool: True if filename is safe, False otherwise.
        """
        if not filename:
            return False

        allowed_extensions = ['.txt', '.text']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return False

        if '..' in filename or '/' in filename or '\\' in filename:
            return False

        return len(filename) <= 255

    @staticmethod
    async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Basic per-user rate limiting.

        Args:
            update (Update): Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): Telegram context object.

        Returns:
            bool: True if under limit, False if exceeded.
        """
        user_id = update.effective_user.id

        if 'request_count' not in context.user_data:
            context.user_data['request_count'] = 0
            context.user_data['request_time'] = update.message.date.timestamp()

        current_time = update.message.date.timestamp()
        if current_time - context.user_data['request_time'] > 60:
            context.user_data['request_count'] = 0
            context.user_data['request_time'] = current_time

        context.user_data['request_count'] += 1

        return context.user_data['request_count'] <= 20
