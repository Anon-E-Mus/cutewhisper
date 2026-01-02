"""
Audio Recorder Module - Captures microphone audio to WAV files
Thread-safe implementation with proper float32 to int16 conversion
"""

import threading
import sounddevice as sd
import numpy as np
from pathlib import Path
import wave
import tempfile
import time
import logging

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Record audio from default microphone (thread-safe)"""

    def __init__(self, sample_rate=16000, channels=1, device=None):
        """
        Initialize audio recorder

        Args:
            sample_rate: Whisper prefers 16kHz
            channels: Mono audio (1) or stereo (2)
            device: Audio device index or name (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device  # CRITICAL: Store device
        self.recording = False
        self.frames = []
        self.lock = threading.Lock()  # Thread safety
        self.stream = None
        self.audio_callback_func = None  # For visualizer

        logger.info(f"AudioRecorder initialized: {sample_rate}Hz, {channels} channels, device={device}")

    def start_recording(self, audio_callback_func=None):
        """
        Start capturing audio in background thread

        Args:
            audio_callback_func: Optional callback function(indata) for real-time audio visualization
        """
        with self.lock:
            if self.recording:
                logger.warning("Already recording, ignoring start request")
                return

            self.recording = True
            self.frames = []
            self.audio_callback_func = audio_callback_func

            def audio_callback(indata, frames, time_info, status):
                """Called for each audio block"""
                if status:
                    logger.warning(f"Audio callback status: {status}")

                # CRITICAL FIX: sounddevice returns float32 by default
                # Store as-is, convert to int16 when saving
                with self.lock:
                    self.frames.append(indata.copy())

                # Notify visualizer if callback provided
                if self.audio_callback_func:
                    try:
                        self.audio_callback_func(indata.copy())
                    except Exception as e:
                        logger.debug(f"Audio callback error: {e}")

            try:
                # Build stream parameters
                stream_params = {
                    'samplerate': self.sample_rate,
                    'channels': self.channels,
                    'dtype': np.float32,
                    'callback': audio_callback
                }

                # CRITICAL FIX: Add device if specified
                if self.device is not None:
                    # Try to find device by name or index
                    devices = sd.query_devices()

                    # Check if device is an index (int)
                    if isinstance(self.device, int):
                        # Validate index exists
                        if 0 <= self.device < len(devices):
                            stream_params['device'] = self.device
                            logger.info(f"Using device index: {self.device} ({devices[self.device]['name']})")
                        else:
                            logger.warning(f"Device index {self.device} out of range, using default")
                    else:
                        # Device is a name string, find index
                        device_found = False
                        for i, dev in enumerate(devices):
                            if dev['name'] == self.device and dev['max_input_channels'] > 0:
                                stream_params['device'] = i
                                logger.info(f"Using device: {dev['name']} (index {i})")
                                device_found = True
                                break

                        if not device_found:
                            logger.warning(f"Device '{self.device}' not found, using default")

                self.stream = sd.InputStream(**stream_params)
                self.stream.start()
                logger.info("Recording started")

            except Exception as e:
                logger.error(f"Failed to start recording: {e}")
                self.recording = False
                raise

    def stop_recording(self) -> str:
        """
        Stop recording and save to temporary WAV file

        Returns:
            Path to saved WAV file, or None if failed
        """
        with self.lock:
            if not self.recording:
                logger.warning("Not recording, cannot stop")
                return None

            self.recording = False

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

        logger.info("Recording stopped, saving to file...")

        # Save audio to temp file
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        # CRITICAL FIX: Now that time is imported, this works
        timestamp = tempfile.gettempprefix() + str(int(time.time()))
        output_path = temp_dir / f"recording_{timestamp}.wav"

        try:
            with self.lock:
                if not self.frames:
                    logger.warning("No audio frames recorded")
                    return None

                # CRITICAL FIX: Concatenate and convert float32 to int16
                audio_data = np.concatenate(self.frames, axis=0)

                # Convert from float32 [-1.0, 1.0] to int16 [-32768, 32767]
                # This is required for WAV file format
                audio_data_int16 = (audio_data * 32767).astype(np.int16)

            # Save as WAV file with proper int16 data
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit = 2 bytes
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data_int16.tobytes())

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Audio saved to {output_path} ({file_size_mb:.2f} MB)")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None

    def is_recording(self) -> bool:
        """Check if currently recording (thread-safe)"""
        with self.lock:
            return self.recording

    def cleanup(self):
        """Clean up resources"""
        logger.debug("Cleaning up AudioRecorder")
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.warning(f"Error closing stream: {e}")
            self.stream = None
        self.frames = []
        self.recording = False
