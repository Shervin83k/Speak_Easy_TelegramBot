from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger
from models.user_session import UserSession


class LanguageHandler:
    """Handles user language selection and updates user preferences."""

    def __init__(self):
        self.user_session = UserSession()

    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Prompt user to select a language."""
        keyboard = [
            ["🇺🇸 English", "🇮🇷 فارسی"],
            ["Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🌐 Please choose your language / لطفا زبان خود را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return Config.LANGUAGE_SELECTION

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user language selection and update preferences."""
        user_input = update.message.text
        user_id = update.effective_user.id

        if user_input == "🇺🇸 English":
            language = "en"
            message = "✅ Language changed to English"
        elif user_input == "🇮🇷 فارسی":
            language = "fa"
            message = "✅ زبان به فارسی تغییر یافت"
        elif user_input == "Back":
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user_id)
        else:
            await update.message.reply_text("⚠ Please select a valid option.")
            return Config.LANGUAGE_SELECTION

        self.user_session.set_user_language(user_id, language)
        context.user_data["language"] = language

        await update.message.reply_text(message)
        from handlers.start_handler import StartHandler
        return await StartHandler().show_main_menu(update, context, user_id)
