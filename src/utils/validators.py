import re

class TextValidator:
    """Advanced text validation and sanitization for TTS."""

    PERSIAN_PATTERN = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    )

    SUSPICIOUS_PATTERNS = [
        re.compile(r'<script.*?>.*?</script>', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
    ]

    def is_valid_text(self, text: str) -> bool:
        """Validate text for TTS processing."""
        if not text or not text.strip():
            return False

        cleaned = text.strip()

        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.search(cleaned):
                return False

        # Must contain at least one alphanumeric character
        if not any(char.isalnum() for char in cleaned):
            return False

        return True

    def sanitize_text(self, text: str) -> str:
        """Remove potentially dangerous content from text."""
        sanitized = text or ""

        for pattern in self.SUSPICIOUS_PATTERNS:
            sanitized = pattern.sub('', sanitized)

        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    def is_persian_text(self, text: str) -> bool:
        """Detect if text is primarily Persian/Arabic."""
        if not text:
            return False

        # Remove English letters and numbers
        non_english_text = re.sub(r'[a-zA-Z0-9\s]', '', text)
        if not non_english_text:
            return False

        persian_chars = len(self.PERSIAN_PATTERN.findall(non_english_text))
        total_chars = len(non_english_text)

        return (persian_chars / total_chars) > 0.3

    def is_mostly_english(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text is mostly English letters."""
        if not text:
            return True

        english_count = len(re.findall(r'[a-zA-Z]', text))
        total_letters = len(re.findall(r'[^\s\d\W]', text))  # All letters excluding digits/punctuation

        if total_letters == 0:
            return True

        return (english_count / total_letters) >= threshold
