import json
import os
from config import Config
from utils.logger import bot_logger


class Locale:
    """Localization manager for loading and retrieving translated text."""

    _cache = {}

    @classmethod
    def get_text(cls, language_code: str, key: str, **kwargs) -> str:
        """
        Retrieve localized text by key, supporting nested keys and formatting.

        Args:
            language_code (str): Language code, e.g., 'en' or 'fa'.
            key (str): Dot-separated key for nested translations, e.g., 'menu.main.welcome'.
            **kwargs: Optional variables for string formatting.

        Returns:
            str: Localized and formatted text, or key in brackets if not found.
        """
        if language_code not in cls._cache:
            cls._load_language(language_code)

        translations = cls._cache.get(language_code, {})

        # Navigate nested keys
        value = translations
        for k in key.split('.'):
            if isinstance(value, dict):
                value = value.get(k, {})
            else:
                value = ""

        if isinstance(value, str):
            text = value.replace('\\n', '\n')
            if kwargs:
                try:
                    return text.format(**kwargs)
                except KeyError:
                    return text
            return text

        return f"[{key}]"

    @classmethod
    def _load_language(cls, language_code: str):
        """Load a language JSON file into cache."""
        file_path = os.path.join(Config.LOCALES_DIR, f"{language_code}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._cache[language_code] = json.load(f)
        except FileNotFoundError:
            cls._cache[language_code] = {}
            bot_logger.warning(f"Language file not found: {file_path}")
        except json.JSONDecodeError as e:
            cls._cache[language_code] = {}
            bot_logger.error(f"Error parsing language file {file_path}: {e}")
