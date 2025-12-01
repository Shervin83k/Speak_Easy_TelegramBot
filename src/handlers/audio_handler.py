from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger
from services.tts_service import TTSService
from services.file_service import FileService
from models.user_session import UserSession
from locales import Locale


class AudioHandler:
    """Handles audio generation and user interactions for TTS."""

    def __init__(self):
        self.tts_service = TTSService()
        self.user_session = UserSession()
        self.locale = Locale()

    async def handle_speed_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle speed selection and generate audio."""
        user = update.effective_user
        user_input = update.message.text
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        bot_logger.info(f"User {user.id} selected speed: {user_input}")

        if user_input in ("Back", "بازگشت"):
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        speed = await self._parse_speed_input(update, user_input, context, language)
        if speed is None:
            return Config.AWAITING_SPEED

        text = context.user_data.get("text_to_process")
        if not text:
            error_text = self.locale.get_text(language, "errors.unexpected")
            await update.message.reply_text(error_text)
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        context.user_data["last_speed"] = speed
        success = await self._generate_and_send_audio(
            update, context, text, speed, user.id, language
        )

        if success:
            keyboard = (
                [["🔄 ادامه", "🛑 توقف"]] if language == "fa" else [["🔄 Continue", "🛑 Stop"]]
            )
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            next_action_text = self.locale.get_text(language, "continuous_mode.next_action")
            await update.message.reply_text(next_action_text, reply_markup=reply_markup)
            return Config.CONTINUOUS_MODE
        else:
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

    async def handle_continuous_mode(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle continuous mode operations."""
        user_input = update.message.text
        user = update.effective_user
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        bot_logger.info(f"User {user.id} in continuous mode: {user_input}")

        if user_input in ("🛑 Stop", "🛑 توقف"):
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        if user_input in ("🔄 Continue", "🔄 ادامه"):
            send_next_text = self.locale.get_text(language, "continuous_mode.send_next")
            await update.message.reply_text(send_next_text, reply_markup=ReplyKeyboardRemove())
            return Config.AWAITING_TEXT

        text = update.message.text
        if not text or text.startswith("/"):
            invalid_input_text = self.locale.get_text(language, "continuous_mode.invalid_input")
            keyboard = (
                [["🔄 ادامه", "🛑 توقف"]] if language == "fa" else [["🔄 Continue", "🛑 Stop"]]
            )
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(invalid_input_text, reply_markup=reply_markup)
            return Config.CONTINUOUS_MODE

        if len(text) > Config.MAX_TEXT_LENGTH:
            error_text = self.locale.get_text(
                language, "text_input.too_long", current=len(text), max=Config.MAX_TEXT_LENGTH
            )
            await update.message.reply_text(error_text)
            return Config.CONTINUOUS_MODE

        remaining = self.user_session.get_remaining_quota(user.id)
        if remaining <= 0:
            quota_text = self.locale.get_text(
                language,
                "quota.exceeded",
                used=self.user_session.get_daily_usage(user.id),
                total=Config.DAILY_QUOTA_FREE,
            )
            await update.message.reply_text(quota_text)
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        speed = context.user_data.get("last_speed", Config.DEFAULT_SPEED)
        self.user_session.increment_usage(user.id)

        success = await self._generate_and_send_audio(update, context, text, speed, user.id, language)

        if success:
            keyboard = (
                [["🔄 ادامه", "🛑 توقف"]] if language == "fa" else [["🔄 Continue", "🛑 Stop"]]
            )
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            next_action_text = self.locale.get_text(language, "continuous_mode.next_action")
            await update.message.reply_text(next_action_text, reply_markup=reply_markup)

        return Config.CONTINUOUS_MODE

    async def _parse_speed_input(
        self, update: Update, user_input: str, context: ContextTypes.DEFAULT_TYPE, language: str
    ) -> float:
        """Parse and validate speed input from user."""
        bot_logger.debug(f"Parsing speed input: {user_input}, language: {language}")

        if user_input in ("Back", "بازگشت"):
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, update.effective_user.id)

        speed_mapping = {
            "en": {"0.5x": 0.5, "1.0x": 1.0, "1.5x": 1.5, "2.0x": 2.0, "Back": "back"},
            "fa": {"0.5x": 0.5, "1.0x": 1.0, "1.5x": 1.5, "2.0x": 2.0, "بازگشت": "back"},
        }

        mapping = speed_mapping.get(language, speed_mapping["en"])

        if user_input in mapping:
            speed_value = mapping[user_input]
            if speed_value == "back":
                from handlers.start_handler import StartHandler
                return await StartHandler().show_main_menu(update, context, update.effective_user.id)
            bot_logger.debug(f"Speed parsed: {speed_value}")
            return speed_value

        # Invalid input, prompt user again
        keyboard = (
            [["0.5x", "1.0x", "1.5x"], ["2.0x", "بازگشت"]]
            if language == "fa"
            else [["0.5x", "1.0x", "1.5x"], ["2.0x", "Back"]]
        )
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        select_text = self.locale.get_text(language, "speed.select")
        await update.message.reply_text(select_text, reply_markup=reply_markup)
        return None

    async def _generate_and_send_audio(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        speed: float,
        user_id: int,
        language: str,
    ) -> bool:
        """Generate audio and send to user. Returns success status."""
        try:
            generating_text = self.locale.get_text(language, "audio.generating")
            if generating_text == "[audio.generating]":
                generating_text = (
                    "🔄 Generating audio..." if language == "en" else "🔄 در حال تولید صوت..."
                )

            bot_logger.info(f"Starting audio generation for user {user_id}, text length: {len(text)}")
            progress_msg = await update.message.reply_text(generating_text)

            audio_file_path = self.tts_service.convert_text_to_speech(text, speed)

            sending_text = self.locale.get_text(language, "audio.sending")
            if sending_text == "[audio.sending]":
                sending_text = "📤 Sending audio..." if language == "en" else "📤 در حال ارسال صوت..."

            await progress_msg.edit_text(sending_text)

            caption_text = self.locale.get_text(language, "audio.caption", speed=speed, length=len(text))
            if caption_text == "[audio.caption]":
                caption_text = f"Speed: {speed}x | Characters: {len(text)}"

            with open(audio_file_path, "rb") as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title="Text-to-Speech Audio",
                    performer="SpeechBot",
                    caption=caption_text,
                )

            await progress_msg.delete()
            FileService.delete_file(audio_file_path)

            success_text = self.locale.get_text(language, "audio.success")
            if success_text == "[audio.success]":
                success_text = "✅ Audio sent successfully!" if language == "en" else "✅ صوت با موفقیت ارسال شد!"

            await update.message.reply_text(success_text)
            bot_logger.info(
                f"✅ Audio successfully delivered to user {user_id} (speed: {speed}x, length: {len(text)} chars)"
            )

            return True

        except Exception as e:
            bot_logger.error(f"❌ Audio generation failed for user {user_id}: {str(e)[:100]}")

            try:
                await progress_msg.delete()
            except Exception:
                pass

            failed_text = self.locale.get_text(language, "audio.failed")
            if failed_text == "[audio.failed]":
                failed_text = (
                    "❌ Failed to generate audio. Please try different text."
                    if language == "en"
                    else "❌ تولید صوت ناموفق بود. لطفا متن دیگری امتحان کنید."
                )
            await update.message.reply_text(failed_text)

            if "audio_file_path" in locals():
                try:
                    FileService.delete_file(audio_file_path)
                except Exception as cleanup_error:
                    bot_logger.warning(f"Failed to cleanup audio file: {cleanup_error}")

            return False
