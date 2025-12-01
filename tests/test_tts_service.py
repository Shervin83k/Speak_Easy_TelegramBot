import os
from services.tts_service import TTSService
from services.file_service import FileService

def test_tts_generates_audio():
    """Ensure TTSService generates a valid audio file."""
    tts = TTSService()
    
    # Generate audio from text
    path = tts.convert_text_to_speech("hello world")

    # Assertions
    assert os.path.exists(path), "Audio file was not created"
    assert os.path.getsize(path) > 0, "Audio file is empty"

    # Cleanup
    FileService.delete_file(path)
