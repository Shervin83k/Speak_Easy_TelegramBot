from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from utils.logger import bot_logger
from services.tts_service import TTSService
from services.file_service import FileService
from models.user_session import UserSession
from locales import Locale


class BatchHandler:
    """Handles batch text-to-speech operations."""

    def __init__(self):
        self.tts_service = TTSService()
        self.user_session = UserSession()
        self.locale = Locale()

    async def start_batch_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Prompt user to enter multiple texts for batch processing."""
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        prompt_text = self.locale.get_text(language, "batch.prompt")
        max_size_text = self.locale.get_text(language, "batch.max_size", max_batch=Config.MAX_BATCH_SIZE)

        keyboard = [["Back"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"{prompt_text}\n\n{max_size_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return Config.BATCH_MODE

    async def handle_batch_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process user input for batch TTS generation."""
        user = update.effective_user
        language = context.user_data.get("language", Config.DEFAULT_LANGUAGE)

        if update.message.text == "Back":
            from handlers.start_handler import StartHandler
            return await StartHandler().show_main_menu(update, context, user.id)

        texts = await self._extract_batch_texts(update)
        if not texts:
            error_text = self.locale.get_text(language, "errors.unexpected")
            await update.message.reply_text(error_text)
            return Config.BATCH_MODE

        if len(texts) > Config.MAX_BATCH_SIZE:
            error_text = self.locale.get_text(language, "batch.max_size", max_batch=Config.MAX_BATCH_SIZE)
            await update.message.reply_text(error_text)
            return Config.BATCH_MODE

        success_count, failed_count = 0, 0

        for i, text in enumerate(texts, 1):
            if len(text) > Config.MAX_BATCH_TEXT_LENGTH:
                failed_count += 1
                continue

            processing_text = self.locale.get_text(language, "batch.processing", current=i, total=len(texts))
            progress_msg = await update.message.reply_text(processing_text)

            try:
                audio_file_path = self.tts_service.convert_text_to_speech(text, Config.DEFAULT_SPEED)

                with open(audio_file_path, "rb") as audio_file:
                    await update.message.reply_audio(
                        audio=audio_file,
                        title=f"Batch Audio {i}",
                        performer="SpeechBot",
                        caption=f"Text {i}/{len(texts)}",
                    )

                FileService.delete_file(audio_file_path)
                success_count += 1

            except Exception as e:
                bot_logger.error(f"Batch processing failed for text {i}: {e}")
                failed_count += 1

            await progress_msg.delete()

        completed_text = self.locale.get_text(
            language, "batch.completed", success=success_count, failed=failed_count
        )
        await update.message.reply_text(completed_text)

        from handlers.start_handler import StartHandler
        return await StartHandler().show_main_menu(update, context, user.id)

    async def _extract_batch_texts(self, update: Update) -> list:
        """Extract texts from message or uploaded file for batch processing."""
        if update.message.text:
            texts = [text.strip() for text in update.message.text.split("\n") if text.strip()]
            return [text for text in texts if len(text) <= Config.MAX_BATCH_TEXT_LENGTH]

        if update.message.document:
            return await self._handle_batch_file_upload(update)

        return []

    async def _handle_batch_file_upload(self, update: Update) -> list:
        """Handle uploaded text file for batch TTS."""
        document = update.message.document
        if document.mime_type == "text/plain" or document.file_name.endswith(".txt"):
            try:
                file = await document.get_file()
                file_path = f"temp_batch_{document.file_id}.txt"
                await file.download_to_drive(file_path)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                import os
                os.remove(file_path)

                texts = [text.strip() for text in content.split("\n") if text.strip()]
                return [text for text in texts if len(text) <= Config.MAX_BATCH_TEXT_LENGTH]

            except Exception as e:
                bot_logger.error(f"Batch file upload error: {e}")

        return []
