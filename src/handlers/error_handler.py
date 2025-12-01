from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import bot_logger
from locales import Locale


class ErrorHandler:
    """Handles unexpected errors during bot execution."""

    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors and notify the user with a friendly message."""
        try:
            user_id = update.effective_user.id if update and update.effective_user else "Unknown"
            bot_logger.error(f"Error for user {user_id}: {context.error}")

            if update and update.effective_message:
                locale = Locale()
                language = context.user_data.get("language", "en")
                error_text = locale.get_text(language, "errors.unexpected")
                await update.effective_message.reply_text(error_text)

        except Exception as e:
            bot_logger.critical(f"Error in error handler: {e}")
