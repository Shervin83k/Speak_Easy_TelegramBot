"""Cache service for audio files."""
import os
import hashlib
from datetime import datetime, timedelta
from config import Config
from utils.logger import bot_logger


class CacheService:
    """Handles caching of generated audio files for reuse."""

    def __init__(self):
        self.cache_dir = os.path.join(Config.TEMP_AUDIO_DIR, 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, text: str, speed: float, language: str = 'en') -> str:
        """Generate a unique cache key based on text, speed, and language."""
        content = f"{text}_{speed}_{language}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def get_cached_audio(self, text: str, speed: float, language: str = 'en') -> str | None:
        """
        Retrieve cached audio file if it exists and is within TTL.

        Returns:
            str | None: Path to cached file or None if not found/fresh.
        """
        cache_key = self._generate_cache_key(text, speed, language)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")

        if os.path.exists(cache_file):
            file_time = datetime.fromtimestamp(os.path.getctime(cache_file))
            if datetime.now() - file_time < timedelta(hours=Config.AUDIO_CACHE_TTL_HOURS):
                bot_logger.debug(f"Cache hit for key: {cache_key[:8]}")
                return cache_file
            else:
                # Remove stale cache
                os.remove(cache_file)
                bot_logger.debug(f"Removed stale cache file: {cache_file}")

        return None

    def cache_audio(self, text: str, speed: float, audio_data: bytes, language: str = 'en'):
        """
        Save audio data to cache.

        Args:
            text (str): Original text.
            speed (float): TTS speed.
            audio_data (bytes): Audio file content.
            language (str): Language code.
        """
        if not Config.ENABLE_AUDIO_CACHING:
            return

        cache_key = self._generate_cache_key(text, speed, language)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")

        try:
            with open(cache_file, 'wb') as f:
                f.write(audio_data)
            bot_logger.debug(f"Cached audio for key: {cache_key[:8]}")
        except Exception as e:
            bot_logger.warning(f"Failed to cache audio: {e}")

    def cleanup_old_cache(self):
        """Delete cache files older than TTL to free up space."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=Config.AUDIO_CACHE_TTL_HOURS)
            removed_count = 0

            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        removed_count += 1

            if removed_count > 0:
                bot_logger.info(f"Cleaned up {removed_count} old cache files")

        except Exception as e:
            bot_logger.error(f"Cache cleanup error: {e}")
