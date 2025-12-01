from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from config import Config
from utils.logger import bot_logger
from models.user_session import UserSession
from locales import Locale


class StartHandler:
    """Handles the start flow and main menu interactions of the bot."""

    def __init__(self):
        self.user_session = UserSession()
        self.locale = Locale()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start command handler. Clears data and prompts language selection."""
        user = update.effective_user
        user_id = user.id

        context.user_data.clear()
        bot_logger.info(f"User {user_id} started bot")

        await self._ask_language(update)
        return Config.LANGUAGE_SELECTION

    async def _ask_language(self, update: Update):
        """Prompt the user to select a language."""
        keyboard = [["🇺🇸 English", "🇮🇷 فارسی"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            "🌐 Please choose your language / لطفا زبان خود را انتخاب کنید:",
            reply_markup=reply_markup
        )

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the user's language selection and update preferences."""
        user_input = update.message.text
        user_id = update.effective_user.id

        if user_input == "🇺🇸 English":
            language = "en"
            message = "✅ Language changed to English"
        elif user_input == "🇮🇷 فارسی":
            language = "fa"
            message = "✅ زبان به فارسی تغییر یافت"
        else:
            await update.message.reply_text("⚠ Please select a valid option.")
            return Config.LANGUAGE_SELECTION

        self.user_session.set_user_language(user_id, language)
        context.user_data["language"] = language

        await update.message.reply_text(message)
        return await self.show_main_menu(update, context, user_id)

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> int:
        """Display the main menu based on user's language."""
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        if language == "fa":
            keyboard = [
                ["🎤 تبدیل متن"],
                ["❓ راهنما", "🌐 تغییر زبان"]
            ]
        else:
            keyboard = [
                ["🎤 Convert Text"],
                ["❓ Help", "🌐 Change Language"]
            ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        welcome_text = self.locale.get_text(language, "menu.main.welcome")

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
        return Config.MAIN_MENU

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle main menu button actions."""
        user_input = update.message.text
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        if language == "fa":
            button_mapping = {
                "🎤 تبدیل متن": "convert_text",
                "❓ راهنما": "help",
                "🌐 تغییر زبان": "change_language"
            }
        else:
            button_mapping = {
                "🎤 Convert Text": "convert_text",
                "❓ Help": "help",
                "🌐 Change Language": "change_language"
            }

        action = button_mapping.get(user_input)

        if action == "convert_text":
            prompt = self.locale.get_text(language, "text_input.prompt")
            await update.message.reply_text(prompt, reply_markup=ReplyKeyboardRemove())
            return Config.AWAITING_TEXT

        elif action == "change_language":
            await self._ask_language(update)
            return Config.LANGUAGE_SELECTION

        elif action == "help":
            await self.help_command(update, context)
            return Config.MAIN_MENU

        else:
            error_text = self.locale.get_text(language, "errors.unexpected")
            await update.message.reply_text(error_text)
            return Config.MAIN_MENU

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show localized help message to the user."""
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        try:
            help_title = self.locale.get_text(language, "help.title")
            help_features = self.locale.get_text(language, "help.features")
            help_commands = self.locale.get_text(language, "help.commands")
            help_text = f"{help_title}\n\n{help_features}\n\n{help_commands}"
            await update.message.reply_text(help_text, parse_mode="Markdown")

        except Exception as e:
            bot_logger.error(f"Error getting help text for language {language}: {e}")
            fallback_text = (
                "🤖 *Text-to-Speech Bot Help*\n\n"
                "✨ *Features:*\n• Convert text to audio\n• Multiple speed options (0.5x to 2.0x)\n"
                "• Support for English and Persian\n• Daily usage limits\n\n"
                "🛠 *Commands:*\n/start - Restart bot\n/help - Show help\n"
                "/cancel - Cancel operation\n/language - Change language"
            )
            await update.message.reply_text(fallback_text, parse_mode="Markdown")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel current operation and clear user data."""
        context.user_data.clear()
        await update.message.reply_text(
            "Operation cancelled. Use /start to begin again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
