import io
import tempfile
import os
from gtts import gTTS
from pydub import AudioSegment
from utils.logger import bot_logger
from services.file_service import FileService
from utils.validators import TextValidator

class TTSService:
    """Text-to-Speech service using gTTS and pydub for speed adjustments."""

    def __init__(self):
        self.validator = TextValidator()

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        return 'fa' if self.validator.is_persian_text(text) else 'en'

    def adjust_audio_speed(self, audio_data: bytes, speed: float) -> bytes:
        """
        Adjust audio speed using pydub.

        Args:
            audio_data: Raw MP3 audio bytes.
            speed: Speed multiplier (0.5 to 3.0).

        Returns:
            Adjusted MP3 audio bytes.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as output_file:
                output_path = output_file.name

            audio = AudioSegment.from_mp3(input_path)

            if speed != 1.0:
                # Change frame rate to adjust speed while preserving pitch
                new_frame_rate = int(audio.frame_rate * speed)
                adjusted_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
                adjusted_audio = adjusted_audio.set_frame_rate(audio.frame_rate)
            else:
                adjusted_audio = audio

            adjusted_audio.export(
                output_path,
                format="mp3",
                bitrate="64k",
                parameters=["-ac", "1"]  # Mono audio for smaller files
            )

            with open(output_path, 'rb') as f:
                adjusted_data = f.read()

            # Cleanup temp files
            os.unlink(input_path)
            os.unlink(output_path)

            bot_logger.debug(f"Audio speed adjusted to {speed}x")
            return adjusted_data

        except Exception as e:
            bot_logger.error(f"Speed adjustment failed: {e}")
            return audio_data  # fallback to original audio

    def convert_text_to_speech(self, text: str, speed: float = 1.0) -> str:
        """
        Convert text to speech and optionally adjust speed.

        Args:
            text: Input text to convert.
            speed: Speed multiplier (0.5 to 3.0).

        Returns:
            File path of generated MP3 audio.

        Raises:
            Exception: If TTS generation fails.
        """
        try:
            bot_logger.info(f"Converting text ({len(text)} chars) at {speed}x speed")

            language = self.detect_language(text)
            lang_code = 'fa' if language == 'fa' else 'en'

            # Determine gTTS slow parameter
            slow = lang_code == 'en' and speed < 0.8

            tts = gTTS(text=text, lang=lang_code, slow=slow, lang_check=False)

            # Generate audio to buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            raw_audio = audio_buffer.read()

            # Adjust speed if necessary
            if speed != 1.0 and not (lang_code == 'fa' and speed < 0.8):
                raw_audio = self.adjust_audio_speed(raw_audio, speed)

            # Save audio to file
            filename = FileService.generate_filename()
            file_path = FileService.save_audio_file(raw_audio, filename)

            bot_logger.info(f"✅ Audio generated successfully ({language})")
            return file_path

        except Exception as e:
            bot_logger.error(f"TTS conversion failed: {e}")
            raise Exception(f"Failed to generate audio: {str(e)[:100]}")
