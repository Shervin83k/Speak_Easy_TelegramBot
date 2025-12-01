import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path)

# Add project root to Python path
sys.path.insert(0, str(project_root))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import Config
from utils.logger import bot_logger
from handlers.start_handler import StartHandler
from handlers.text_handler import TextHandler
from handlers.audio_handler import AudioHandler
from handlers.error_handler import ErrorHandler
from services.file_service import FileService

class TextToSpeechBot:
    """Telegram TTS Bot."""

    def __init__(self):
        self.application: Application | None = None
        self.start_handler = StartHandler()
        self.text_handler = TextHandler()
        self.audio_handler = AudioHandler()

    def setup_handlers(self):
        """Setup conversation and command handlers."""
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start_handler.start),
                CommandHandler('language', self.start_handler._ask_language),
            ],
            states=self._get_states(),
            fallbacks=self._get_fallbacks(),
        )

        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('help', self.start_handler.help_command))
        self.application.add_handler(CommandHandler('cancel', self.start_handler.cancel))
        self.application.add_error_handler(ErrorHandler.error_handler)

    def _get_states(self) -> dict:
        """Define conversation states for the bot."""
        return {
            Config.LANGUAGE_SELECTION: [
                MessageHandler(filters.TEXT, self.start_handler.handle_language_selection)
            ],
            Config.MAIN_MENU: [
                MessageHandler(filters.TEXT, self.start_handler.handle_main_menu)
            ],
            Config.AWAITING_TEXT: [
                MessageHandler(
                    filters.TEXT | filters.Document.ALL | filters.PHOTO,
                    self.text_handler.handle_text_input
                )
            ],
            Config.AWAITING_SPEED: [
                MessageHandler(filters.TEXT, self.audio_handler.handle_speed_selection)
            ],
            Config.CONTINUOUS_MODE: [
                MessageHandler(filters.TEXT, self.audio_handler.handle_continuous_mode)
            ],
        }

    def _get_fallbacks(self) -> list:
        """Define fallback commands."""
        return [
            CommandHandler('cancel', self.start_handler.cancel),
            CommandHandler('start', self.start_handler.start)
        ]

    async def post_init(self, application: Application):
        """Run on bot startup."""
        try:
            FileService.cleanup_old_files()
        except Exception as e:
            bot_logger.warning(f"Initial file cleanup failed: {e}")
        bot_logger.info("Bot initialized successfully")

    async def post_stop(self, application: Application):
        """Run on bot shutdown."""
        bot_logger.info("Bot shutting down")
        FileService.cleanup_old_files(0)

    def run(self):
        """Start the bot polling."""
        try:
            Config.validate_setup()
            self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
            self.setup_handlers()

            self.application.post_init = self.post_init
            self.application.post_stop = self.post_stop

            bot_logger.info("Starting bot polling...")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            bot_logger.critical(f"Failed to start bot: {e}")
            raise

def main():
    bot = TextToSpeechBot()
    bot.run()

if __name__ == '__main__':
    main()
