import pytest
from middleware.security import SecurityMiddleware

def test_sanitize_input_removes_tags():
    """Ensure dangerous HTML/JS is stripped from input."""
    input_text = "<script>alert(1)</script> hello <b>bold</b>"
    sanitized = SecurityMiddleware.sanitize_input(input_text)
    # No script tags or angle brackets
    assert "<" not in sanitized
    assert "script" not in sanitized

def test_validate_filename_accepts_only_safe_txt_files():
    """Validate that filenames are safe and correctly constrained."""
    valid_filename = "notes.txt"
    invalid_filename_traversal = "../secrets.txt"
    invalid_filename_wrong_ext = "image.png"
    invalid_filename_too_long = "a" * 300 + ".txt"

    assert SecurityMiddleware.validate_filename(valid_filename) is True
    assert SecurityMiddleware.validate_filename(invalid_filename_traversal) is False
    assert SecurityMiddleware.validate_filename(invalid_filename_wrong_ext) is False
    assert SecurityMiddleware.validate_filename(invalid_filename_too_long) is False
