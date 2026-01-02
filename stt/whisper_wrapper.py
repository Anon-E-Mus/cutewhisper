"""
Whisper Speech-to-Text Wrapper - Transcribes audio using Whisper models
Uses OpenAI Whisper library for better Python 3.14 compatibility
"""

import whisper
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Transcribe audio using Whisper"""

    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initialize Whisper transcriber

        Args:
            model_size: tiny, base, small, medium, large
            device: cpu or cuda (not used in OpenAI Whisper, auto-detected)
            compute_type: int8 (cpu), float16 (gpu) - not used in OpenAI Whisper
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self.model_loaded = False
        self.load_model()

    def load_model(self):
        """Load Whisper model with error handling and progress tracking"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            print(f"Loading Whisper model '{self.model_size}'...")
            print("If this is your first time, the model will be downloaded (may take a while)")

            # OpenAI Whisper downloads models to ~/.cache/whisper or models/ if specified
            # Model will download automatically on first use
            self.model = whisper.load_model(self.model_size)

            self.model_loaded = True
            logger.info(f"Model loaded successfully: {self.model_size}")
            print(f"[OK] Model '{self.model_size}' loaded and ready!")

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model_loaded = False
            raise RuntimeError(f"Could not load Whisper model: {e}")

    def transcribe(self, audio_path: str, language: str = "auto") -> dict:
        """
        Transcribe audio file

        Args:
            audio_path: Path to WAV file
            language: 'auto' for auto-detect or 'en', 'es', etc.

        Returns:
            {
                'text': 'Transcribed text',
                'language': 'en',
                'duration': 3.5
            }

        Raises:
            ValueError: If audio file doesn't exist
            RuntimeError: If model not loaded or transcription fails
        """
        if not self.model_loaded:
            raise RuntimeError("Whisper model not loaded")

        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        try:
            logger.info(f"Transcribing: {audio_path}")

            # Transcribe with language detection if needed
            # OpenAI Whisper uses None for auto-detect
            lang = None if language == "auto" else language

            result = self.model.transcribe(
                str(audio_file),
                language=lang,
                fp16=False  # Use float32 for better compatibility
            )

            text = result.get('text', '').strip()
            detected_lang = result.get('language', 'unknown')

            # Calculate duration from audio file
            import wave
            with wave.open(str(audio_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)

            output = {
                'text': text,
                'language': detected_lang,
                'duration': duration
            }

            logger.info(f"Transcription complete: {len(text)} chars, language: {detected_lang}")
            return output

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription error: {e}")

    def unload_model(self):
        """Free model memory (optional, for large models)"""
        if self.model:
            del self.model
            self.model = None
            self.model_loaded = False
            logger.info("Model unloaded from memory")
