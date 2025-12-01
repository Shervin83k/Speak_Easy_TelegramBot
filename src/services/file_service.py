"""File handling service for temporary audio files."""

import os
import uuid
from datetime import datetime, timedelta
from config import Config
from utils.logger import bot_logger


class FileService:
    """Handles creation, storage, and cleanup of audio files."""

    @staticmethod
    def generate_filename() -> str:
        """Generate a unique filename for an audio file."""
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"audio_{timestamp}_{unique_id}.mp3"

    @staticmethod
    def get_file_path(filename: str) -> str:
        """Get full path for a given filename."""
        return os.path.join(Config.TEMP_AUDIO_DIR, filename)

    @staticmethod
    def save_audio_file(audio_data: bytes, filename: str) -> str:
        """
        Save audio data to a file.

        Args:
            audio_data (bytes): Audio content to save.
            filename (str): Target filename.

        Returns:
            str: Full path of the saved file.
        """
        try:
            file_path = FileService.get_file_path(filename)
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            return file_path
        except Exception as e:
            bot_logger.error(f"Failed to save audio file '{filename}': {e}")
            raise

    @staticmethod
    def delete_file(file_path: str):
        """Delete a file if it exists."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                bot_logger.debug(f"Deleted file: {file_path}")
        except Exception as e:
            bot_logger.error(f"Failed to delete file '{file_path}': {e}")

    @staticmethod
    def cleanup_old_files(hours_old: int = 1):
        """
        Remove files older than the specified number of hours.

        Args:
            hours_old (int): Age threshold in hours. Defaults to 1.
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            deleted_count = 0

            for filename in os.listdir(Config.TEMP_AUDIO_DIR):
                file_path = os.path.join(Config.TEMP_AUDIO_DIR, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1

            if deleted_count > 0:
                bot_logger.info(f"Cleaned up {deleted_count} old audio files")
        except Exception as e:
            bot_logger.error(f"Error cleaning up old files: {e}")
