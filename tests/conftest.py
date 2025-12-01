import sys
import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock

# Add /src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

# Import AFTER path fix
from config import Config


@pytest.fixture(autouse=True)
def patch_config_token(monkeypatch):
    """
    Provide a stable test token for all tests.
    No environment variables needed.
    """
    monkeypatch.setattr(Config, "TELEGRAM_TOKEN", "TEST_TOKEN")
    yield


@pytest.fixture(autouse=True)
def isolate_paths(tmp_path, monkeypatch):
    """
    Redirect all Config paths to a temporary test folder.
    Creates minimal folder structure and locale files.
    """
    base = tmp_path / "project"
    data = base / "data"
    logs = base / "logs"
    audio = data / "temp_audio"
    locales = base / "locales"

    # Create directories
    for folder in [base, data, logs, audio, locales]:
        folder.mkdir(parents=True, exist_ok=True)

    # Minimal locale files
    en = {
        "menu": {"main": {"welcome": "Welcome!"}},
        "text_input": {"prompt": "Send text", "received": "Received {char_count} chars"},
        "audio": {"generating": "Generating", "sending": "Sending", "success": "Success"}
    }
    fa = {"menu": {"main": {"welcome": "خوش آمدید"}}}

    (locales / "en.json").write_text(json.dumps(en), encoding="utf-8")
    (locales / "fa.json").write_text(json.dumps(fa), encoding="utf-8")

    # Patch Config paths
    monkeypatch.setattr(Config, "BASE_DIR", base)
    monkeypatch.setattr(Config, "DATA_DIR", data)
    monkeypatch.setattr(Config, "LOGS_DIR", logs)
    monkeypatch.setattr(Config, "AUDIO_TEMP_DIR", audio)
    monkeypatch.setattr(Config, "TEMP_AUDIO_DIR", audio)
    monkeypatch.setattr(Config, "LOCALES_DIR", locales)
    monkeypatch.setattr(Config, "DATABASE_PATH", data / "bot_test.db")

    yield


@pytest.fixture(autouse=True)
def mock_audio_libs(monkeypatch):
    """
    Mock gTTS and pydub for offline testing (no internet or ffmpeg needed).
    """

    class DummyGTTS:
        def __init__(self, text, lang="en", slow=False, lang_check=True):
            self.text = text

        def write_to_fp(self, fp):
            fp.write(b"FAKE_MP3_" + self.text.encode())

    monkeypatch.setattr("gtts.gTTS", DummyGTTS, raising=False)

    class DummyAudio:
        @classmethod
        def from_mp3(cls, path):
            return cls()

        def export(self, out, format="mp3"):
            with open(out, "wb") as f:
                f.write(b"FAKE_AUDIO")
            return True

    monkeypatch.setattr("pydub.AudioSegment", DummyAudio, raising=False)
    yield


@pytest.fixture
def fake_update_and_context():
    """Provide fake Telegram update and context objects for testing."""

    class FakeMessage:
        def __init__(self, text=""):
            self.text = text
            self.reply_text = AsyncMock()
            self.reply_audio = AsyncMock()

    class FakeUser:
        id = 12345

    class FakeUpdate:
        def __init__(self, text="/start"):
            self.effective_user = FakeUser()
            self.message = FakeMessage(text)
            self.effective_message = self.message

    class FakeContext:
        def __init__(self):
            self.user_data = {}
            self.job_queue = None

    return FakeUpdate, FakeContext
