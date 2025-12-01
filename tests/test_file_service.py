import os
import pytest
from services.file_service import FileService
from config import Config

@pytest.mark.asyncio
def test_file_service_basic(tmp_path, monkeypatch):
    """
    Test basic FileService operations:
        - generate filename
        - save audio file
        - delete audio file
    """

    # Redirect temp directory to tmp_path
    monkeypatch.setattr(Config, "TEMP_AUDIO_DIR", tmp_path)
    monkeypatch.setattr(Config, "AUDIO_TEMP_DIR", tmp_path)

    # Generate unique filename
    filename = FileService.generate_filename()
    sample_data = b"hello123"

    # Save audio file
    path = FileService.save_audio_file(sample_data, filename)
    assert os.path.exists(path), "File should be saved successfully"

    # Delete file
    FileService.delete_file(path)
    assert not os.path.exists(path), "File should be deleted successfully"
