from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger
from utils.validators import TextValidator
from models.user_session import UserSession
from locales import Locale
import os


class TextHandler:
    """Handles user text input, validation, and TTS preparation."""

    def __init__(self):
        self.validator = TextValidator()
        self.user_session = UserSession()
        self.locale = Locale()

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Validate user text input and prompt for TTS speed."""
        user = update.effective_user
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        # Check quota
        remaining = self.user_session.get_remaining_quota(user.id)
        if remaining <= 0:
            quota_text = self.locale.get_text(
                language, "quota.exceeded",
                used=self.user_session.get_daily_usage(user.id),
                total=Config.DAILY_QUOTA_FREE
            )
            await update.message.reply_text(quota_text)
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        # Extract text
        text = await self._extract_text(update)
        if not text:
            error_text = self.locale.get_text(language, "text_input.invalid")
            await update.message.reply_text(error_text)
            return Config.AWAITING_TEXT

        # Validate text length
        if len(text) > Config.MAX_TEXT_LENGTH:
            error_text = self.locale.get_text(
                language, "text_input.too_long",
                current=len(text), max=Config.MAX_TEXT_LENGTH
            )
            await update.message.reply_text(error_text)
            return Config.AWAITING_TEXT

        # Validate text content
        if not self.validator.is_valid_text(text):
            error_text = self.locale.get_text(language, "text_input.invalid")
            await update.message.reply_text(error_text)
            return Config.AWAITING_TEXT

        # Reject Persian/Arabic text
        if self.validator.is_persian_text(text):
            if language == "fa":
                error_msg = (
                    "❌ متاسفانه پشتیبانی از متن فارسی در حال حاضر امکان‌پذیر نیست.\n\n"
                    "⚠️ **محدودیت فنی:**\n"
                    "• سرویس تبدیل متن به گفتار فعلاً فقط از انگلیسی پشتیبانی می‌کند\n"
                    "• متن‌های فارسی قابل پردازش نیستند\n\n"
                    "لطفاً متن انگلیسی ارسال کنید."
                )
            else:
                error_msg = (
                    "❌ Persian/Arabic text is not currently supported.\n\n"
                    "⚠️ **Technical Limitation:**\n"
                    "• The TTS service only supports English text\n"
                    "• Persian/Arabic characters cannot be processed\n\n"
                    "Please send English text only."
                )
            await update.message.reply_text(error_msg, parse_mode="Markdown")
            return Config.AWAITING_TEXT

        # Ensure text is mostly English
        if not self._is_mostly_english(text):
            error_msg = (
                "❌ متن حاوی کاراکترهای غیر انگلیسی است. لطفاً فقط متن انگلیسی ارسال کنید."
                if language == "fa" else
                "❌ Text contains non-English characters. Please send English text only."
            )
            await update.message.reply_text(error_msg)
            return Config.AWAITING_TEXT

        # Store text and prompt for speed
        context.user_data["text_to_process"] = text
        self.user_session.increment_usage(user.id)

        received_text = self.locale.get_text(language, "text_input.received", char_count=len(text))
        choose_speed = self.locale.get_text(language, "text_input.choose_speed")

        keyboard = [
            ["0.5x", "1.0x", "1.5x"],
            ["2.0x", "بازگشت"] if language == "fa" else ["2.0x", "Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(f"{received_text}\n{choose_speed}", reply_markup=reply_markup)
        bot_logger.info(f"User {user.id} submitted English text ({len(text)} chars)")

        return Config.AWAITING_SPEED

    def _is_mostly_english(self, text: str) -> bool:
        """Check if the majority of alphabetic characters are English letters."""
        if not text:
            return False

        english_chars = sum(1 for char in text if 'a' <= char.lower() <= 'z')
        total_alpha = sum(1 for char in text if char.isalpha())
        if total_alpha == 0:
            return True  # Allow numbers/punctuation
        return (english_chars / total_alpha) >= 0.8

    async def _extract_text(self, update: Update) -> str:
        """Extract text from message, document, or caption."""
        if update.message.text and not update.message.text.startswith("/"):
            return update.message.text.strip()
        elif update.message.document:
            return await self._handle_file_upload(update)
        elif update.message.photo and update.message.caption:
            return update.message.caption.strip()
        return ""

    async def _handle_file_upload(self, update: Update) -> str:
        """Handle plain text file uploads and return content."""
        document = update.message.document
        if document.mime_type == "text/plain" or document.file_name.endswith(".txt"):
            try:
                file = await document.get_file()
                file_path = f"temp_{document.file_id}.txt"
                await file.download_to_drive(file_path)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                os.remove(file_path)
                return content

            except Exception as e:
                bot_logger.error(f"File upload error: {e}")

        return ""
