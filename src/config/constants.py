"""Application constants used throughout the bot."""


class ConversationState:
    """Enumeration of conversation states."""
    LANGUAGE_SELECTION = 0
    MAIN_MENU = 1
    AWAITING_TEXT = 2
    AWAITING_SPEED = 3
    CONTINUOUS_MODE = 4
    BATCH_MODE = 5


class UserTier:
    """User subscription tiers."""
    FREE = "free"
    PREMIUM = "premium"


class LanguageCode:
    """Supported language codes."""
    ENGLISH = "en"
    PERSIAN = "fa"
    DEFAULT = ENGLISH


class TTSProvider:
    """Text-to-speech service providers."""
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"
    DEFAULT = GTTS
