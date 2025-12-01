"""
Config module - exports constants as Config
"""

import os
from pathlib import Path
from .constants import *


# Base directory (TTV_bot version2 folder)
BASE_DIR = Path(__file__).parent.parent.parent


class Config:
    """Configuration class that wraps constants and ensures directories exist."""

    # ====== PATHS ======
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    AUDIO_TEMP_DIR = DATA_DIR / "temp_audio"
    TEMP_AUDIO_DIR = AUDIO_TEMP_DIR  # Alias for compatibility
    LOCALES_DIR = BASE_DIR / "src" / "locales"
    DATABASE_PATH = DATA_DIR / "bot_data.db"

    # Ensure directories exist
    LOGS_DIR.mkdir(exist_ok=True, parents=True)
    AUDIO_TEMP_DIR.mkdir(exist_ok=True, parents=True)
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    # ====== BATCH SETTINGS ======
    MAX_BATCH_SIZE = 10
    MAX_BATCH_TEXT_LENGTH = 1000

    # ====== AUDIO SETTINGS ======
    DEFAULT_SPEED = 1.0

    # ====== RATE LIMITING ======
    RATE_LIMIT_PER_MINUTE = 20

    # ====== QUOTAS ======
    DAILY_QUOTA_FREE = 5
    DAILY_QUOTA_PREMIUM = 100

    # ====== TEXT LIMITS ======
    MAX_TEXT_LENGTH = 5000
    MIN_TEXT_LENGTH = 1

    # ====== CONVERSATION STATES ======
    LANGUAGE_SELECTION = ConversationState.LANGUAGE_SELECTION
    MAIN_MENU = ConversationState.MAIN_MENU
    AWAITING_TEXT = ConversationState.AWAITING_TEXT
    AWAITING_SPEED = ConversationState.AWAITING_SPEED
    CONTINUOUS_MODE = ConversationState.CONTINUOUS_MODE
    BATCH_MODE = ConversationState.BATCH_MODE

    # ====== USER TIERS ======
    FREE = UserTier.FREE
    PREMIUM = UserTier.PREMIUM

    # ====== LANGUAGES ======
    ENGLISH = LanguageCode.ENGLISH
    PERSIAN = LanguageCode.PERSIAN
    DEFAULT_LANGUAGE = LanguageCode.DEFAULT

    # ====== TTS PROVIDERS ======
    GTTS = TTSProvider.GTTS
    PYTTSX3 = TTSProvider.PYTTSX3
    DEFAULT_PROVIDER = TTSProvider.DEFAULT

    # ====== FILE SETTINGS ======
    AUDIO_TEMP_MAX_AGE = 24  # hours

    # ====== TELEGRAM ======
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    # ====== CACHE SETTINGS ======
    ENABLE_AUDIO_CACHING = False
    AUDIO_CACHE_TTL_HOURS = 24

    @staticmethod
    def validate_setup():
        """Validate that required setup is complete."""
        if not Config.TELEGRAM_TOKEN:
            raise ValueError("Environment variable TELEGRAM_BOT_TOKEN is not set")
