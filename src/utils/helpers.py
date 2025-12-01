"""Helper functions for the bot."""
import re
from datetime import datetime

class Helpers:
    """Collection of general helper functions."""

    @staticmethod
    def format_timestamp(timestamp: datetime = None) -> str:
        """Format a datetime object as a string."""
        if timestamp is None:
            timestamp = datetime.now()
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Convert seconds to human-readable duration."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds_left = seconds % 60
            return f"{minutes}m {seconds_left}s" if seconds_left else f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds_left = seconds % 60
            parts = [f"{hours}h"] if hours else []
            if minutes: parts.append(f"{minutes}m")
            if seconds_left: parts.append(f"{seconds_left}s")
            return " ".join(parts)

    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text and add ellipsis if too long."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def count_characters(text: str) -> dict:
        """Count characters, words, lines, and non-space characters."""
        lines = text.count('\n') + 1
        words = len(text.split())
        characters = len(text)
        non_space_chars = len(text.replace(' ', ''))
        return {
            'lines': lines,
            'words': words,
            'characters': characters,
            'non_space_chars': non_space_chars
        }

    @staticmethod
    def is_persian_text(text: str) -> bool:
        """Detect if text is primarily Persian/Arabic."""
        if not text:
            return False
        persian_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
        persian_chars = len(re.findall(persian_pattern, text))
        total_chars = len(re.sub(r'\s', '', text))
        if total_chars == 0:
            return False
        return (persian_chars / total_chars) > 0.3  # 30% threshold

    @staticmethod
    def estimate_speech_duration(text: str, speed: float = 1.0) -> int:
        """
        Estimate speech duration (seconds) based on text and speed.
        Assumes average speaking rate of 150 words/min (≈2.5 words/sec).
        """
        words = len(text.split())
        base_duration = words / 2.5
        if speed <= 0:
            speed = 1.0
        return int(base_duration / speed)
