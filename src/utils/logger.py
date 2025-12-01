import logging
import os
import re
from config import Config

class SecurityFilter(logging.Filter):
    """Filter sensitive information from logs."""

    BOT_TOKEN_PATTERN = re.compile(r'\d{10}:[A-Za-z0-9_-]{35}')
    TOKEN_PATTERN = re.compile(r'token[\'"]?\s*[:=]\s*[\'"]?[^\s]+', re.IGNORECASE)

    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)
        return True

    def _sanitize(self, message: str) -> str:
        message = self.BOT_TOKEN_PATTERN.sub('[BOT_TOKEN]', message)
        message = self.TOKEN_PATTERN.sub('token=[REDACTED]', message)
        return message


class ColorFormatter(logging.Formatter):
    """Formatter for colored console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Create and return a logger with file and colored console handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Avoid duplicate handlers

    logger.setLevel(level)
    logger.addFilter(SecurityFilter())

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Formatter
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    console_formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handlers
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


# Global loggers
bot_logger = setup_logger('bot', os.path.join(Config.LOGS_DIR, 'bot.log'), logging.DEBUG)
admin_logger = setup_logger('admin', os.path.join(Config.LOGS_DIR, 'admin.log'), logging.INFO)
