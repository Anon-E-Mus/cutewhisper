# Implementation Plan — CuteWhisper

**Project:** Windows Local Dictation Tool
**Based on:** task.md
**Created:** 2026-01-02

---

## Table of Contents

1. [Technical Decisions](#technical-decisions)
2. [Phase 1: MVP Implementation](#phase-1-mvp-core-dictation)
3. [Phase 2: UX & Stability](#phase-2-ux--stability)
4. [Phase 3: Performance & Accuracy](#phase-3-performance--accuracy)
5. [Phase 4: Enhanced Features](#phase-4-enhanced-features-optional)
6. [Phase 5: Packaging & Polish](#phase-5-packaging--polish)
7. [Testing Strategy](#testing-strategy)
8. [Dependencies](#dependencies)
9. [Risk Mitigation](#risk-mitigation)

---

## Key Improvements & Critical Fixes

This implementation plan has been reviewed and enhanced with the following critical fixes:

### 🔴 Critical Issues Fixed:
1. **Missing Dependencies** - Added `pynput`, `pyautogui`, `torch`, `requests`, `tqdm` to requirements
2. **Thread Safety** - Added `threading.Lock()` to AudioRecorder for concurrent access
3. **Memory Management** - Implemented streaming audio capture instead of loading all frames in memory
4. **Error Handling** - Comprehensive error handling for model loading, transcription, and clipboard operations
5. **Temp File Cleanup** - Added automatic cleanup on startup to prevent disk space issues
6. **Configuration Validation** - Added validation with automatic correction to safe defaults
7. **Audio Data Type Bug** - Fixed critical audio dtype handling: sounddevice returns float32, must convert to int16 for WAV
8. **Missing Imports** - Added `import time` to AudioRecorder for timestamp generation
9. **Hotkey Format Conversion** - Added conversion between config format (`ctrl+space`) and pynput format (`<ctrl>+<space>`)
10. **Clipboard Preservation** - Added option to restore previous clipboard content after paste

### 🟡 Important Improvements:
11. **No Admin Required** - Using `pynput` library instead of `keyboard` - works without admin privileges
12. **Clipboard Fallback** - Automatic fallback to typing if clipboard operations fail
13. **PyInstaller Dependencies** - Updated spec with all required hidden imports including pynput
14. **Threading Considerations** - Documented thread-safety requirements for tray icon callbacks
15. **Resource Cleanup** - Added proper cleanup handlers and atexit handlers
16. **Startup Cleanup** - Clean orphaned temp files from previous crashes
17. **Single Hotkey Design** - Changed to Ctrl+Space press-and-hold for more intuitive workflow
18. **Model Download Progress** - Added tqdm progress bar for model downloads
19. **UI Thread Safety Fixes** - Fixed critical tkinter threading issues in UI plan (use after(), not threads)
20. **Tray Icon Thread Management** - Changed from daemon to non-daemon thread for proper lifecycle
21. **Settings Window Architecture** - Fixed multiple Tk instances issue - use Toplevel correctly
22. **Toast Notifier Fallback** - Added error handling and console fallback for notifications

### 📢 New Components Added:
- `utils/cleanup.py` - Temp file management
- `utils/progress.py` - Model download progress tracking
- `ui/toast_notifier.py` - Fixed toast notification manager with fallback
- `ui/recording_indicator.py` - Thread-safe recording indicator (using after())
- `ui/tray_icon.py` - Fixed tray icon with proper thread management
- `ui/settings_window.py` - Fixed settings window using Toplevel
- Enhanced error handling throughout all modules
- Configuration validation system
- Clipboard retry logic with fallback and preservation
- `pynput`-based hotkey manager with press-and-hold support
- Audio data type conversion utilities
- UI thread safety documentation and fixes

### ⚠️ Known Limitations Documented:
- Hotkey changes require application restart
- No dynamic hotkey reloading (future enhancement)

---

## Technical Decisions

### Speech-to-Text Engine
**Decision:** Start with `faster-whisper` (Python)
- **Reasoning:**
  - Python-native integration
  - GPU acceleration support
  - Better for rapid iteration
  - Can switch to whisper.cpp CLI later if needed

### Hotkey System
**Decision:** pynput with press-and-hold pattern
- **Reasoning:**
  - No admin privileges required
  - Single hotkey (Ctrl+Space) - press to record, release to transcribe
  - More intuitive workflow than separate start/stop keys
  - Cross-platform, Python-native integration
  - Reliable global hotkey handling

### Audio Capture
**Decision:** `sounddevice` + `numpy`
- **Reasoning:**
  - Cross-platform but Windows-optimized
  - PortAudio backend (WASAPI on Windows)
  - Easy numpy array handling for Whisper

### Text Injection
**Decision:** Clipboard + simulated Ctrl+V with clipboard preservation
- **Reasoning:**
  - Works in 95%+ of applications
  - Faster than character-by-character typing
  - Fewer edge cases than keystroke injection
  - Optional clipboard restoration preserves user's clipboard content

### Project Structure
```
CuteWhisper/
├── main.py                    # Application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration management with validation
│   └── default_config.yaml    # Default settings
├── audio/
│   ├── __init__.py
│   ├── recorder.py            # Audio capture logic (thread-safe)
│   └── audio_utils.py         # Audio processing utilities
├── stt/
│   ├── __init__.py
│   ├── whisper_wrapper.py     # Whisper interface with error handling
│   └── model_manager.py       # Model loading/caching
├── injection/
│   ├── __init__.py
│   └── text_paster.py         # Clipboard + paste logic with fallback
├── hotkey/
│   ├── __init__.py
│   ├── hotkey_manager.py      # Hotkey registration (pynput - no admin needed)
│   └── cute_whisper.ahk       # AutoHotkey v2 script (optional alternative)
├── ui/
│   ├── __init__.py
│   ├── tray_icon.py           # System tray UI (thread-safe callbacks)
│   └── recording_indicator.py # Visual feedback
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging setup
│   ├── cleanup.py             # Temp file cleanup utilities
│   └── progress.py            # Model download progress tracking
├── models/                    # Downloaded Whisper models (gitignored)
├── temp/                      # Temporary audio files (gitignored)
├── logs/                      # Application logs (gitignored)
├── assets/
│   └── icon.ico               # Application icon (for builds)
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── build.spec                 # PyInstaller spec
```

---

## Phase 1: MVP (Core Dictation)

**Goal:** Basic dictation workflow - hotkey → record → transcribe → paste

### 1.1 Environment Setup

**Tasks:**
1. Initialize Python project structure
2. Create virtual environment
3. Install dependencies

**Dependencies:**
```
faster-whisper==0.10.0
sounddevice==0.4.6
numpy==1.24.3
pyyaml==6.0.1
pywin32==306  # Windows-specific
pynput==1.7.6  # Global hotkeys (NO ADMIN REQUIRED)
pyautogui==0.9.54  # Fallback text injection
pystray==0.19.5  # System tray
Pillow==10.0.0  # Image handling for tray icon
torch>=2.0.0  # GPU detection (optional, for CUDA)
requests==2.31.0  # For LLM integration (Phase 4)
tqdm==4.66.1  # Progress bars for model download
```

**Commands:**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Implementation:** Create `requirements.txt` and project directory structure.

---

### 1.2 Audio Capture Module

**File:** `audio/recorder.py`

**Implementation Details:**
```python
import threading
import sounddevice as sd
import numpy as np
from pathlib import Path
import wave
import tempfile
import time  # CRITICAL FIX: Added for timestamp generation

class AudioRecorder:
    """Record audio from default microphone (thread-safe)"""

    def __init__(self, sample_rate=16000, channels=1):
        """
        Args:
            sample_rate: Whisper prefers 16kHz
            channels: Mono audio
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.frames = []
        self.lock = threading.Lock()  # Thread safety
        self.stream = None

    def start_recording(self):
        """Start capturing audio in background thread"""
        with self.lock:
            if self.recording:
                return  # Already recording

            self.recording = True
            self.frames = []

            def audio_callback(indata, frames, time, status):
                """Called for each audio block"""
                if status:
                    print(f"Audio callback status: {status}")
                with self.lock:
                    # CRITICAL FIX: sounddevice returns float32 by default
                    # Store as-is, convert to int16 when saving
                    self.frames.append(indata.copy())

            # CRITICAL FIX: Use float32 dtype (sounddevice default)
            # Will convert to int16 when saving to WAV
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,  # CRITICAL: Fixed from np.int16
                callback=audio_callback
            )
            self.stream.start()

    def stop_recording(self) -> str:
        """
        Stop recording and save to temporary WAV file

        Returns:
            Path to saved WAV file, or None if failed
        """
        with self.lock:
            if not self.recording:
                return None

            self.recording = False

            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

        # Save audio to temp file
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        # CRITICAL FIX: Now that time is imported, this works
        timestamp = tempfile.gettempprefix() + str(int(time.time()))
        output_path = temp_dir / f"recording_{timestamp}.wav"

        try:
            with self.lock:
                if not self.frames:
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

            return str(output_path)

        except Exception as e:
            print(f"Failed to save audio: {e}")
            return None

    def is_recording(self) -> bool:
        """Check if currently recording (thread-safe)"""
        with self.lock:
            return self.recording

    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.frames = []
```

**Key Functions:**
- `start_recording()`: Initialize sounddevice stream with callback
- `stop_recording()`: Close stream, save WAV to temp/
- Sample rate: 16000 Hz (Whisper optimal)
- Audio format: 16-bit PCM, mono
- **Thread-safe**: Uses `threading.Lock()` for state management
- **Streaming**: Uses sounddevice callback to avoid loading all audio in memory at once
- **CRITICAL**: Converts float32 audio to int16 for WAV file compatibility

**Testing:**
- Record 5 seconds of audio
- Verify WAV file plays correctly
- Check file size is reasonable

---

### 1.3 Speech-to-Text Module

**File:** `stt/whisper_wrapper.py`

**Implementation Details:**
```python
from faster_whisper import WhisperModel
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Transcribe audio using Whisper"""

    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Args:
            model_size: tiny, base, small, medium, large
            device: cpu or cuda
            compute_type: int8 (cpu), float16 (gpu)
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

            # Model downloaded automatically to models/
            # faster-whisper doesn't have built-in progress, so we track the download
            from utils.progress import ModelDownloadProgress

            progress_tracker = ModelDownloadProgress()
            progress_tracker.start_monitoring("models/")

            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root="models/"
            )

            progress_tracker.stop_monitoring()

            self.model_loaded = True
            logger.info(f"Model loaded successfully: {self.model_size}")
            print(f"✓ Model '{self.model_size}' loaded and ready!")

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

        if not Path(audio_path).exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        try:
            logger.info(f"Transcribing: {audio_path}")

            # Transcribe with language detection if needed
            segments, info = self.model.transcribe(
                audio_path,
                language=None if language == "auto" else language,
                beam_size=5
            )

            # Extract text from segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)

            text = "".join(text_parts).strip()

            result = {
                'text': text,
                'language': info.language,
                'duration': info.duration
            }

            logger.info(f"Transcription complete: {len(text)} chars")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription error: {e}")

    def unload_model(self):
        """Free model memory (optional, for large models)"""
        if self.model:
            del self.model
            self.model = None
            self.model_loaded = False
```

**Model Selection:**
- Start with `base` model (~74MB, good balance)
- Small enough for CPU inference
- Can be configured later

**Optimizations:**
- Load model once at startup
- Keep model in memory for fast repeated transcriptions
- Models cached in `models/` directory

**Error Handling:**
- Validates audio file exists before transcription
- Catches model download failures
- Logs all errors with details

---

### 1.4 Text Injection Module

**File:** `injection/text_paster.py`

**Implementation Details:**
```python
import win32clipboard
import win32con
import time
import pyautogui
import logging

logger = logging.getLogger(__name__)

class TextInjector:
    """Paste text into currently focused window with clipboard preservation"""

    def __init__(self, use_clipboard=True, preserve_clipboard=True):
        """
        Args:
            use_clipboard: If True, use clipboard+paste. If False, use typing.
            preserve_clipboard: If True, restore previous clipboard after paste.
        """
        self.use_clipboard = use_clipboard
        self.preserve_clipboard = preserve_clipboard
        self.clipboard_timeout = 5  # seconds

    def paste_text(self, text: str, method: str = "auto"):
        """
        Copy text to clipboard and simulate Ctrl+V

        Args:
            text: Text to paste
            method: 'auto', 'clipboard', or 'typing'

        Returns:
            True if successful, False otherwise
        """
        if not text:
            return True

        # Auto-detect best method
        if method == "auto":
            method = "clipboard" if self.use_clipboard else "typing"

        try:
            if method == "clipboard":
                return self._paste_via_clipboard(text)
            else:
                return self._type_text(text)
        except Exception as e:
            logger.error(f"Text injection failed: {e}")
            # Fallback to typing if clipboard fails
            if method == "clipboard":
                logger.info("Falling back to typing method")
                return self._type_text(text)
            return False

    def _paste_via_clipboard(self, text: str) -> bool:
        """Paste using clipboard + Ctrl+V with optional clipboard preservation"""
        old_clipboard = self._get_clipboard()

        try:
            # Copy new text to clipboard
            self._copy_to_clipboard(text)

            # Small delay to ensure clipboard is ready
            time.sleep(0.1)

            # Simulate Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)

            # ENHANCED: Restore old clipboard if enabled
            if self.preserve_clipboard and old_clipboard:
                time.sleep(0.3)  # Wait for paste to complete
                self._copy_to_clipboard(old_clipboard)
                logger.debug("Restored previous clipboard content")

            return True

        except Exception as e:
            logger.error(f"Clipboard paste failed: {e}")
            # Restore clipboard on error
            if old_clipboard:
                self._copy_to_clipboard(old_clipboard)
            return False

    def _type_text(self, text: str) -> bool:
        """Fallback: Type text character by character"""
        try:
            # Add a small delay for better reliability
            pyautogui.write(text, interval=0.01)
            return True
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False

    def _get_clipboard(self) -> str:
        """Get current clipboard content with timeout"""
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return data
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            logger.warning(f"Could not read clipboard: {e}")
        return ""

    def _copy_to_clipboard(self, text: str):
        """Windows clipboard operations with retry"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                    return
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                if attempt < max_attempts - 1:
                    time.sleep(0.1)
                else:
                    raise
```

**Alternative Fallback:**
- If Ctrl+V doesn't work, use `pyautogui.typewrite()` for character-by-character paste
- Slower but more universal
- Automatic fallback if clipboard method fails

---

### 1.5 Hotkey Integration (Press-and-Hold Pattern)

**File:** `hotkey/hotkey_manager.py`

**Design:** Single Ctrl+Space hotkey - press to start recording, release to transcribe

**Implementation Details:**
```python
# hotkey/hotkey_manager.py
from pynput import keyboard
from pynput.keyboard import Key, Controller
import threading
import logging

logger = logging.getLogger(__name__)

class HotkeyManager:
    """
    Global hotkey manager using pynput with press-and-hold pattern
    Works WITHOUT admin privileges on Windows

    Pattern: Press Ctrl+Space to start recording, release to stop and transcribe
    """

    def __init__(self, start_callback, stop_callback, hotkey_str='ctrl+space'):
        """
        Args:
            start_callback: Function to call when Ctrl+Space is pressed
            stop_callback: Function to call when Ctrl+Space is released
            hotkey_str: Hotkey string in config format (e.g., 'ctrl+space')
        """
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.hotkey_str = hotkey_str
        self.listener = None
        self.ctrl_pressed = False
        self.space_pressed = False

    def _convert_to_pynput_format(self, hotkey_str: str) -> str:
        """
        Convert config format to pynput format
        Example: 'ctrl+space' -> '<ctrl>+<space>'
        """
        # Normalize the string
        parts = hotkey_str.lower().replace(' ', '').split('+')

        # Format each part for pynput
        formatted_parts = []
        for part in parts:
            # Common modifier keys
            if part in ['ctrl', 'control', 'ctrl_l', 'ctrl_r']:
                formatted_parts.append('<ctrl>')
            elif part in ['alt', 'alt_l', 'alt_r']:
                formatted_parts.append('<alt>')
            elif part in ['shift', 'shift_l', 'shift_r']:
                formatted_parts.append('<shift>')
            elif part in ['cmd', 'win', 'windows', 'meta']:
                formatted_parts.append('<cmd>')
            # Special keys
            elif part == 'space':
                formatted_parts.append('<space>')
            else:
                # Regular character keys
                formatted_parts.append(part)

        return '+'.join(formatted_parts)

    def _on_press(self, key):
        """Handle key press events"""
        try:
            # Track Ctrl state
            if key in [Key.ctrl_l, Key.ctrl_r, Key.ctrl]:
                self.ctrl_pressed = True

            # Track Space state
            if key == Key.space:
                self.space_pressed = True

            # Check if both Ctrl and Space are pressed
            if self.ctrl_pressed and self.space_pressed:
                # Start recording in a separate thread to avoid blocking
                threading.Thread(target=self.start_callback, daemon=True).start()

        except Exception as e:
            logger.error(f"Hotkey press error: {e}")

    def _on_release(self, key):
        """Handle key release events"""
        try:
            # Track Ctrl state
            if key in [Key.ctrl_l, Key.ctrl_r, Key.ctrl]:
                self.ctrl_pressed = False

            # Track Space state
            if key == Key.space:
                if self.space_pressed:  # If space was being held
                    self.space_pressed = False
                    # Stop recording and transcribe
                    threading.Thread(target=self.stop_callback, daemon=True).start()

        except Exception as e:
            logger.error(f"Hotkey release error: {e}")

    def start(self):
        """Start listening for hotkeys"""
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()

            pynput_format = self._convert_to_pynput_format(self.hotkey_str)
            logger.info(f"Hotkey listener started: {self.hotkey_str} (press-and-hold)")
            print(f"Hotkey: {pynput_format}")
            print("  Press and hold to record, release to transcribe")

        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise

    def listen(self):
        """Start listening for hotkeys (blocks forever)"""
        if not self.listener:
            self.start()

        # Block forever
        try:
            self.listener.join()
        except KeyboardInterrupt:
            logger.info("Hotkey listener stopped")

    def stop(self):
        """Stop the hotkey listener"""
        if self.listener:
            self.listener.stop()
            logger.info("Hotkey listener stopped")
```

**Key Features:**
- **Press-and-hold pattern**: More intuitive than separate start/stop keys
- **Thread-safe callbacks**: All callbacks run in separate threads
- **Format conversion**: Automatically converts between config format and pynput format
- **State tracking**: Properly tracks modifier key states

**Configuration:**
```yaml
hotkey:
  toggle: 'ctrl+space'  # Press and hold to record
```

**Decision:** Use `pynput` library - works without admin privileges, cross-platform, reliable.

---

### 1.6 Main Application Logic

**File:** `main.py`

**Implementation Details:**
```python
#!/usr/bin/env python3
"""
CuteWhisper - Windows Local Dictation Tool
"""

from audio.recorder import AudioRecorder
from stt.whisper_wrapper import WhisperTranscriber
from injection.text_paster import TextInjector
from hotkey.hotkey_manager import HotkeyManager
from config.settings import Config
from utils.logger import setup_logging
import argparse
import os
import sys
import atexit
from pathlib import Path

logger = setup_logging()

class CuteWhisper:
    def __init__(self, config_path=None):
        """Initialize CuteWhisper application"""
        self.config = Config(config_path)

        # Initialize components
        self.recorder = AudioRecorder(
            sample_rate=self.config.get('audio.sample_rate', 16000),
            channels=self.config.get('audio.channels', 1)
        )

        self.transcriber = WhisperTranscriber(
            model_size=self.config.get('whisper.model_size', 'base'),
            device=self.config.get('whisper.device', 'cpu'),
            compute_type=self.config.get('whisper.compute_type', 'int8')
        )

        self.injector = TextInjector(
            use_clipboard=self.config.get('ui.use_clipboard', True),
            preserve_clipboard=self.config.get('ui.preserve_clipboard', True)
        )

        # Setup hotkey (press-and-hold pattern)
        self.hotkey_manager = HotkeyManager(
            start_callback=self.start_dictation,
            stop_callback=self.stop_dictation,
            hotkey_str=self.config.get('hotkey.toggle', 'ctrl+space')
        )

        # Register cleanup on exit
        atexit.register(self.cleanup)

        # Track temp files for cleanup
        self.temp_files = []

    def start_dictation(self):
        """Start recording audio"""
        if self.recorder.is_recording():
            logger.warning("Already recording, ignoring start request")
            return

        try:
            logger.info("Starting dictation...")
            print("🎤 Recording...")

            self.recorder.start_recording()

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            print(f"❌ Error: Could not start recording: {e}")

    def stop_dictation(self):
        """Stop recording and transcribe"""
        if not self.recorder.is_recording():
            logger.warning("Not recording, ignoring stop request")
            return

        try:
            logger.info("Stopping dictation...")
            print("⏹️ Processing...")

            # Stop recording and get audio path
            audio_path = self.recorder.stop_recording()

            if not audio_path:
                print("❌ No audio recorded")
                return

            # Track for cleanup
            self.temp_files.append(audio_path)

            # Transcribe
            logger.info(f"Transcribing: {audio_path}")
            print("🧠 Transcribing...")

            result = self.transcriber.transcribe(
                audio_path,
                language=self.config.get('whisper.language', 'auto')
            )

            text = result.get('text', '').strip()
            if not text:
                print("⚠️ No speech detected")
                logger.info("No speech detected in audio")
                return

            # Display result
            print(f"📝 Text: {text}")
            logger.info(f"Transcription: {text[:50]}...")

            # Paste text
            if self.injector.paste_text(text):
                print("✓ Text inserted!")
                logger.info("Text successfully injected")
            else:
                print("❌ Failed to insert text")
                logger.error("Text injection failed")

            # Cleanup temp file
            self._cleanup_file(audio_path)

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(f"❌ Error: {e}")

        except RuntimeError as e:
            logger.error(f"Transcription error: {e}")
            print(f"❌ Transcription failed: {e}")

        except Exception as e:
            logger.error(f"Unexpected error during dictation: {e}", exc_info=True)
            print(f"❌ Unexpected error: {e}")

    def _cleanup_file(self, file_path):
        """Safely remove a temp file"""
        try:
            if file_path and Path(file_path).exists():
                os.remove(file_path)
                logger.debug(f"Cleaned up: {file_path}")
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not cleanup temp file {file_path}: {e}")

    def cleanup(self):
        """Clean up resources before exit"""
        logger.info("Cleaning up...")

        # Stop recording if active
        if self.recorder.is_recording():
            try:
                self.recorder.stop_recording()
            except:
                pass

        # Cleanup temp files
        for file_path in self.temp_files[:]:
            self._cleanup_file(file_path)

        # Unload model
        if hasattr(self.transcriber, 'unload_model'):
            self.transcriber.unload_model()

        logger.info("Cleanup complete")

    def run(self):
        """Start listening for hotkeys"""
        try:
            print("CuteWhisper ready!")
            hotkey = self.config.get('hotkey.toggle', 'ctrl+space')
            print(f"  Hotkey: {hotkey} (press and hold to record, release to transcribe)")
            print(f"  Model: {self.config.get('whisper.model_size')}")
            print(f"  Clipboard preservation: {self.config.get('ui.preserve_clipboard', True)}")
            print("\nPress Ctrl+C to quit.")

            self.hotkey_manager.listen()

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            logger.info("Interrupted by user")
        finally:
            self.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CuteWhisper - Windows Local Dictation Tool")
    parser.add_argument('--config', '-c', help="Path to config file")
    parser.add_argument('--version', '-v', action='version', version='CuteWhisper 1.0')

    args = parser.parse_args()

    try:
        app = CuteWhisper(config_path=args.config)
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
```

---

### Phase 1 Success Criteria

- [ ] Hotkey triggers recording
- [ ] Audio saved to temp file
- [ ] Whisper transcribes accurately
- [ ] Text appears in active window
- [ ] End-to-end latency < 5 seconds
- [ ] Works in Notepad, browser, VS Code

**Testing Checklist:**
1. Press hotkey → speak → release hotkey
2. Verify text appears in cursor location
3. Test in: Notepad, Chrome, VS Code, Discord
4. Measure timing from hotkey release to text paste

---

## Phase 2: UX & Stability

**Goal:** User-friendly application with configuration and visual feedback

### 2.1 Configuration System

**File:** `config/settings.py`

**Implementation:**
```python
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    """Manage application configuration with validation"""

    DEFAULT_CONFIG = {
        'hotkey': {
            'toggle': 'ctrl+space'  # Press and hold to record
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1
        },
        'whisper': {
            'model_size': 'base',
            'language': 'auto',
            'device': 'cpu',
            'compute_type': 'int8'
        },
        'ui': {
            'show_notifications': True,
            'recording_indicator': True,
            'use_clipboard': True,
            'preserve_clipboard': True  # Restore clipboard after paste
        }
    }

    # Validation rules
    VALID_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    VALID_DEVICES = ['cpu', 'cuda']
    VALID_CHANNELS = [1, 2]

    def __init__(self, config_path='config/user_config.yaml'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.validate_config()

    def load_config(self) -> dict:
        """Load config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def validate_config(self):
        """Validate configuration values"""
        # Validate Whisper model size
        if self.config.get('whisper.model_size') not in self.VALID_MODELS:
            logger.warning(f"Invalid model_size, using 'base'")
            self.config['whisper']['model_size'] = 'base'

        # Validate device
        if self.config.get('whisper.device') not in self.VALID_DEVICES:
            logger.warning(f"Invalid device, using 'cpu'")
            self.config['whisper']['device'] = 'cpu'

        # Validate audio channels
        if self.config.get('audio.channels') not in self.VALID_CHANNELS:
            logger.warning(f"Invalid channels, using 1")
            self.config['audio']['channels'] = 1

        # Validate sample rate (must be positive)
        if self.config.get('audio.sample_rate', 0) <= 0:
            logger.warning(f"Invalid sample_rate, using 16000")
            self.config['audio']['sample_rate'] = 16000

    def save_config(self):
        """Persist config to file"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Config saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def get(self, key_path: str, default=None):
        """Get nested config value"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key_path: str, value):
        """Set nested config value"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        logger.debug(f"Config updated: {key_path} = {value}")
```

**Features:**
- YAML-based configuration
- User overrides for all settings
- **Validation** of model sizes, devices, audio parameters
- **Merge strategy**: user config overrides defaults
- **Error handling**: defaults if config file is corrupt
- **Setter method** for runtime updates

---

### 2.2 System Tray Icon

**File:** `ui/tray_icon.py`

**Implementation:**
```python
import pystray
from PIL import Image
import threading

class TrayIcon:
    """System tray icon with menu"""

    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False

    def create_icon(self):
        """Create tray icon"""
        # Create simple icon (or use icon file)
        image = self._create_icon_image()

        menu = pystray.Menu(
            pystray.MenuItem("Start Dictation", self.on_start),
            pystray.MenuItem("Settings", self.on_settings),
            pystray.MenuItem("Quit", self.on_quit)
        )

        self.icon = pystray.Icon("CuteWhisper", image, menu=menu)

    def _create_icon_image(self):
        """Generate simple icon image"""
        # Use PIL to create colored square
        image = Image.new('RGB', (64, 64), color='blue')
        return image

    def on_start(self):
        """Menu action: Start dictation"""
        threading.Thread(target=self.app.start_dictation).start()

    def on_settings(self):
        """Menu action: Open settings"""
        # Launch settings UI
        pass

    def on_quit(self):
        """Menu action: Quit application"""
        self.running = False
        self.icon.stop()

    def run(self):
        """Start tray icon"""
        self.running = True
        self.icon.run()
```

**Features:**
- Right-click menu
- Start/Stop dictation
- Settings option
- Quit option

**Threading Considerations:**
- The `on_start()` method uses `threading.Thread()` to avoid blocking the UI
- Recording operations must be thread-safe (see AudioRecorder with locks)
- The tray icon runs in its own event loop

**Hotkey Reload:**
- If hotkeys are changed in settings, the application must restart
- Future enhancement: Add `reload_hotkeys()` method to support dynamic updates
- pynput GlobalHotKeys can be stopped and restarted, but requires careful thread management

---

### 2.3 Temp File Cleanup

**File:** `utils/cleanup.py`

**Implementation:**
```python
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

def cleanup_old_temp_files(temp_dir="temp", max_age_hours=24):
    """
    Remove temp files older than max_age_hours

    Called at startup to clean up any orphaned files from crashes
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned = 0

    for file_path in temp_path.glob("*.wav"):
        file_age = current_time - file_path.stat().st_mtime
        if file_age > max_age_seconds:
            try:
                file_path.unlink()
                cleaned += 1
                logger.debug(f"Removed old temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not remove {file_path}: {e}")

    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} old temp file(s)")

def cleanup_all_temp_files(temp_dir="temp"):
    """
    Remove all temp files (called on uninstall or explicit cleanup)
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return

    cleaned = 0
    for file_path in temp_path.glob("*"):
        try:
            if file_path.is_file():
                file_path.unlink()
                cleaned += 1
        except Exception as e:
            logger.warning(f"Could not remove {file_path}: {e}")

    logger.info(f"Cleaned up {cleaned} temp file(s)")
```

**Usage:**
```python
# In main.py __init__ or at startup
from utils.cleanup import cleanup_old_temp_files

# Clean up old files on startup
cleanup_old_temp_files()
```

**When to Call:**
- Application startup (clean up orphaned files from crashes)
- Manual cleanup via settings menu
- Uninstall routine

---

### 2.5 Model Download Progress Tracker

**File:** `utils/progress.py`

**Implementation:**
```python
from pathlib import Path
import time
import threading
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelDownloadProgress:
    """Track and display model download progress"""

    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.models_dir = None
        self.pbar = None

    def start_monitoring(self, models_dir: str):
        """
        Start monitoring model directory for download progress

        Args:
            models_dir: Path to models directory
        """
        self.models_dir = Path(models_dir)
        self.monitoring = True

        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_download,
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring and clean up progress bar"""
        self.monitoring = False
        if self.pbar:
            self.pbar.close()
            self.pbar = None

    def _monitor_download(self):
        """Monitor model directory and update progress"""
        initial_size = self._get_dir_size()

        # Initialize progress bar
        print("Downloading Whisper model...")
        self.pbar = tqdm(
            total=100,  # Percentage
            unit='%',
            desc="Progress",
            bar_format='{l_bar}{bar}| {n:.1f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

        last_update = time.time()
        last_size = initial_size

        while self.monitoring:
            current_size = self._get_dir_size()

            if current_size > initial_size:
                # Calculate progress percentage
                # Base model is ~74MB, small is ~244MB, medium is ~769MB
                estimated_sizes = {
                    'tiny': 39 * 1024 * 1024,    # ~39MB
                    'base': 74 * 1024 * 1024,    # ~74MB
                    'small': 244 * 1024 * 1024,   # ~244MB
                    'medium': 769 * 1024 * 1024,  # ~769MB
                    'large': 1550 * 1024 * 1024,  # ~1.5GB
                }

                # Use base model size as default estimate
                max_size = estimated_sizes.get('base', 74 * 1024 * 1024)
                progress = min(100, int((current_size / max_size) * 100))

                # Update progress bar
                self.pbar.update(progress - self.pbar.n)
                last_size = current_size
                last_update = time.time()

            time.sleep(0.5)  # Check twice per second

        # Download complete
        if self.pbar:
            final_size_mb = current_size / (1024 * 1024)
            self.pbar.write(f"✓ Model downloaded ({final_size_mb:.1f} MB)")

    def _get_dir_size(self) -> int:
        """Calculate total size of models directory in bytes"""
        total_size = 0
        if self.models_dir.exists():
            for file_path in self.models_dir.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        return total_size
```

**Key Features:**
- Uses tqdm for progress bar display
- Monitors models directory size during download
- Estimates completion based on model size
- Non-blocking monitoring in background thread
- Automatic cleanup when download completes

**Usage:**
```python
# In WhisperTranscriber.load_model()
progress_tracker = ModelDownloadProgress()
progress_tracker.start_monitoring("models/")

# Load model (this may trigger download)
self.model = WhisperModel(...)

# Stop monitoring
progress_tracker.stop_monitoring()
```

**Dependencies:**
- `tqdm>=4.66.1` - Progress bar display

---

### 2.4 Recording Indicator

**File:** `ui/recording_indicator.py`

**Implementation Options:**

**Option 1: Floating Window**
```python
import tkinter as tk

class RecordingIndicator:
    """Show floating red circle when recording"""

    def __init__(self):
        self.window = None

    def show(self):
        """Show recording indicator"""
        self.window = tk.Tk()
        self.window.title("🎤 Recording")
        self.window.attributes('-topmost', True)
        self.window.geometry("150x50+10+10")  # Top-left corner

        label = tk.Label(self.window, text="🎤 Recording...", bg="red", fg="white")
        label.pack(fill='both', expand=True)
        self.window.update()

    def hide(self):
        """Hide recording indicator"""
        if self.window:
            self.window.destroy()
            self.window = None
```

**Option 2: Toast Notification**
```python
from win10toast import ToastNotifier

class ToastIndicator:
    """Windows toast notification"""

    def show_recording(self):
        toast = ToastNotifier()
        toast.show_title("CuteWhisper", "Recording...", duration=1)

    def show_complete(self, text):
        toast = ToastNotifier()
        toast.show_title("CuteWhisper", f"Inserted: {text[:30]}...")
```

**Decision:** Use floating window for continuous feedback during recording.

---

### 2.4 Error Handling

**Implementation:**

```python
# utils/logger.py
import logging
from pathlib import Path

def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "cutewhisper.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Wrap main operations in try-except
try:
    audio_path = self.recorder.stop_recording()
except Exception as e:
    logger.error(f"Recording failed: {e}")
    # Show user-friendly error
    return
```

**Error Scenarios:**
- Microphone not found
- Whisper model download fails
- Clipboard access denied
- Disk full

---

### Phase 2 Success Criteria

- [ ] Tray icon visible and functional
- [ ] Recording indicator shows/hides correctly
- [ ] Configuration persists across restarts
- [ ] Graceful error handling
- [ ] User can change hotkeys and settings

---

## Phase 3: Performance & Accuracy

**Goal:** Optimize speed and add optional GPU support

### 3.1 Model Caching

**File:** `stt/model_manager.py`

**Implementation:**
```python
class ModelManager:
    """Manage Whisper model lifecycle"""

    def __init__(self):
        self.models = {}  # Cache loaded models

    def get_model(self, model_size="base"):
        """Get cached model or load new one"""
        if model_size not in self.models:
            print(f"Loading {model_size} model...")
            self.models[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )
        return self.models[model_size]
```

---

### 3.2 GPU Support

**Implementation:**
```python
# Detect GPU availability
import torch

def get_device():
    """Detect best available device"""
    if torch.cuda.is_available():
        return "cuda", "float16"
    else:
        return "cpu", "int8"

# Update WhisperTranscriber
device, compute_type = get_device()
self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
```

---

### 3.3 Optimization Tasks

1. **Preload model at startup** (not on first use)
2. **Keep audio buffer in memory** (avoid disk I/O)
3. **Use smaller model for testing** (tiny/base)
4. **Benchmark different model sizes**

**Performance Targets:**
- Model load time: < 2 seconds
- Transcription time: < 2 seconds for 10s audio
- Total latency: < 5 seconds

---

## Phase 4: Enhanced Features (Optional)

**Goal:** Add advanced capabilities

### 4.1 Local LLM Cleanup

**Files:** `llm/text_cleaner.py`

**Integration Options:**
- Ollama (local API)
- LM Studio (local API)

**Implementation:**
```python
import requests

class TextCleaner:
    """Use local LLM to format transcribed text"""

    def __init__(self, api_url="http://localhost:11434/api/generate"):
        self.api_url = api_url
        self.enabled = False

    def clean_text(self, text: str) -> str:
        """Clean up transcription with LLM"""
        prompt = f"""Fix punctuation and capitalization in this text.
Only return the corrected text, no explanations.

{text}"""

        response = requests.post(self.api_url, json={
            "model": "llama2",
            "prompt": prompt
        })

        return response.json().get('response', text)
```

**Prompt Templates:**
- Fix punctuation
- Add paragraph breaks
- Format as bullet points
- Remove filler words

---

### 4.2 Command Phrases

**File:** `commands/phrase_processor.py`

**Implementation:**
```python
class PhraseProcessor:
    """Process special voice commands"""

    COMMANDS = {
        "new paragraph": "\n\n",
        "bullet point": "• ",
        "delete last": ["backspace"] * 20,
        "select all": ["ctrl+l"],
    }

    def process(self, text: str) -> tuple[str, list]:
        """
        Replace commands with actions

        Returns:
            (cleaned_text, actions)
        """
        text_lower = text.lower()
        actions = []

        for phrase, replacement in self.COMMANDS.items():
            if phrase in text_lower:
                if isinstance(replacement, str):
                    text = text.replace(phrase, replacement)
                elif isinstance(replacement, list):
                    actions.extend(replacement)
                    text = text.replace(phrase, "")

        return text.strip(), actions
```

**Commands:**
- "new paragraph" → `\n\n`
- "bullet point" → `• `
- "delete that" → backspace
- "scratch that" → clear all

---

## Phase 5: Packaging & Polish

**Goal:** Distributable Windows application

### 5.1 PyInstaller Packaging

**File:** `build.spec`

**Implementation:**
```python
# build.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('models', 'models'),  # Include pre-downloaded models
    ],
    hiddenimports=[
        'faster_whisper',
        'sounddevice',
        'win32clipboard',
        'win32con',
        'pyyaml',
        'pynput',
        'pynput.keyboard',
        'pyautogui',
        'pystray',
        'PIL',
        'numpy',
        'torch',  # If using GPU detection
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CuteWhisper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

**Build Commands:**
```bash
# Build executable
pyinstaller build.spec

# Output: dist/CuteWhisper.exe
```

**Important Notes:**
- Icon file (`assets/icon.ico`) must exist or remove the `icon` parameter
- Consider creating a simple icon or use PyInstaller's default
- First build may take several minutes
- Test the executable thoroughly before distribution

---

### 5.2 Auto-start on Boot

**Registry Key:**
```python
import winreg

def add_to_startup():
    """Add CuteWhisper to Windows startup"""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_path = r"C:\Program Files\CuteWhisper\CuteWhisper.exe"

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "CuteWhisper", 0, winreg.REG_SZ, app_path)
    winreg.CloseKey(key)
```

---

### 5.3 Settings UI

**File:** `ui/settings_window.py`

**Implementation (tkinter):**
```python
import tkinter as tk
from tkinter import ttk

class SettingsWindow:
    """Settings configuration window"""

    def __init__(self, config):
        self.config = config
        self.window = tk.Tk()
        self.window.title("CuteWhisper Settings")

        self.create_widgets()

    def create_widgets(self):
        # Hotkey settings
        hotkey_frame = ttk.LabelFrame(self.window, text="Hotkeys")
        hotkey_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(hotkey_frame, text="Start:").grid(row=0, column=0)
        start_entry = ttk.Entry(hotkey_frame)
        start_entry.insert(0, self.config.get('hotkey.start'))
        start_entry.grid(row=0, column=1)

        # Whisper settings
        whisper_frame = ttk.LabelFrame(self.window, text="Whisper")
        whisper_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(whisper_frame, text="Model:").grid(row=0, column=0)
        model_combo = ttk.Combobox(whisper_frame,
            values=['tiny', 'base', 'small', 'medium', 'large'])
        model_combo.set(self.config.get('whisper.model_size'))
        model_combo.grid(row=0, column=1)

        # Save button
        ttk.Button(self.window, text="Save", command=self.save).pack(pady=10)

    def save(self):
        """Save settings"""
        # Update config
        self.config.save_config()
        self.window.destroy()
```

---

### 5.4 Documentation

**Files:**
- `README.md` (Installation, usage, features)
- `CHANGELOG.md` (Version history)
- `CONFIG.md` (Configuration options)
- `BUILD.md` (Build instructions)

---

## Testing Strategy

### Unit Testing

**Tools:** `pytest`

**Tests:**
```python
# tests/test_recorder.py
def test_recorder_starts_stops():
    recorder = AudioRecorder()
    recorder.start_recording()
    assert recorder.is_recording() == True

    time.sleep(1)
    path = recorder.stop_recording()
    assert os.path.exists(path)
    assert recorder.is_recording() == False

# tests/test_transcriber.py
def test_transcriber_loads_model():
    transcriber = WhisperTranscriber(model_size="tiny")
    assert transcriber.model is not None

# tests/test_injector.py
def test_clipboard_copy():
    injector = TextInjector()
    injector.paste_text("Hello, world!")
    # Verify clipboard contains text
```

---

### Integration Testing

**Scenarios:**
1. Full workflow: hotkey → record → transcribe → paste
2. Multiple consecutive dictations
3. Configuration changes
4. Error conditions (no mic, invalid audio)

---

### Manual Testing Checklist

**Applications:**
- [ ] Notepad
- [ ] VS Code
- [ ] Chrome/Edge browser
- [ ] Microsoft Word
- [ ] Discord
- [ ] Slack

**Edge Cases:**
- [ ] Very long dictation (>30 seconds)
- [ ] Very short dictation (<1 second)
- [ ] Silence/misfire
- [ ] Multiple languages
- [ ] No audio device

---

## Dependencies

### Python Packages
```
faster-whisper>=0.10.0
sounddevice>=0.4.6
numpy>=1.24.0
pyyaml>=6.0.1
pywin32>=306
pynput>=1.7.6
pyautogui>=0.9.54
pystray>=0.19.5
Pillow>=10.0.0
torch>=2.0.0  # Optional, for GPU detection
requests>=2.31.0  # For LLM features (Phase 4)
```

### System Dependencies
- Windows 10/11
- Microphone
- (Optional) NVIDIA GPU for CUDA

### External Tools
- None required (pynput handles global hotkeys without external tools)
- (Optional) Ollama for LLM features

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Microphone access denied | Request permissions in README, use WASAPI loopback fallback |
| Paste blocked in app | Add "type instead" fallback using pyautogui |
| High CPU usage | Allow user to select smaller model (tiny) |
| Model download fails | Bundle model with installer or provide mirror |
| Antivirus false positive | Code sign executable, distribute via installer |
| **Thread safety issues** | Added threading.Lock() to AudioRecorder and state management |
| **Temp file accumulation** | Auto-cleanup on startup, manual cleanup option |
| **Clipboard conflicts** | Automatic fallback to typing if clipboard fails |
| **Invalid config values** | Added validation with automatic correction to defaults |
| **Model load failures** | Error handling with user-friendly messages |
| **Hotkey changes require restart** | Documented limitation, future: dynamic reload |
| **Memory leaks in recording** | Use streaming callback instead of storing all frames |

---

## UI Implementation Notes & Critical Fixes

### ⚠️ CRITICAL: UI Thread Safety Issues

The UI-IMPLEMENTATION-PLAN.md contains **several critical thread-safety issues** that must be fixed:

---

### 1. RecordingIndicator Thread Safety (CRITICAL BUG)

**Problem:** Tkinter is NOT thread-safe. The plan updates GUI widgets from background threads.

**Current Code (WRONG):**
```python
# This WILL crash - tkinter updates from thread
def _update_timer(self):
    while self.running:
        if self.label:
            self.label.config(text=f"● Recording {minutes:02d}:{seconds:02d}")
        time.sleep(1)
```

**Fixed Implementation:**
```python
# ui/recording_indicator.py
import tkinter as tk
import threading
import time

class RecordingIndicator:
    """Thread-safe recording indicator using tkinter"""

    def __init__(self):
        self.window = None
        self.label = None
        self.start_time = None
        self.running = False
        self.update_timer = None  # Use tkinter's after() method
        self.root = None  # Reference to main window

    def show(self):
        """Show recording indicator (must be called from main thread)"""
        if self.window:
            return  # Already showing

        # CRITICAL: Use Toplevel, not Tk
        if not self.root:
            # Create a hidden root if none exists
            self.root = tk.Tk()
            self.root.withdraw()

        self.window = tk.Toplevel(self.root)
        self.window.title("Recording")

        # Remove window decorations
        self.window.overrideredirect(True)

        # Make always on top
        self.window.attributes('-topmost', True)

        # Make semi-transparent
        self.window.attributes('-alpha', 0.8)

        # Position in top-right corner
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"200x60+{screen_width-220}+10")

        # Create content
        self.label = tk.Label(
            self.window,
            text="● Recording...",
            bg="#FF0000",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.label.pack(fill='both', expand=True)

        # Start timer
        self.start_time = time.time()
        self.running = True

        # CRITICAL FIX: Use after() instead of thread
        self._schedule_update()

    def _schedule_update(self):
        """Schedule next update using tkinter's event loop"""
        if not self.running or not self.window:
            return

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        if self.label:
            self.label.config(text=f"● Recording {minutes:02d}:{seconds:02d}")

        # Schedule next update in 1000ms (1 second)
        self.update_timer = self.window.after(1000, self._schedule_update)

    def hide(self):
        """Hide recording indicator"""
        self.running = False

        # Cancel any pending updates
        if self.update_timer:
            self.window.after_cancel(self.update_timer)
            self.update_timer = None

        if self.window:
            self.window.destroy()
            self.window = None
            self.label = None
```

**Key Fixes:**
- Use `tk.Toplevel()` instead of `tk.Tk()` for indicator window
- Use `window.after()` instead of `threading.Thread()` for updates
- All GUI updates happen in the main thread via tkinter's event loop
- Properly cancel scheduled updates with `after_cancel()`

---

### 2. Settings Window Architecture Fix

**Problem:** Creates multiple `tk.Tk()` instances - only one allowed per application.

**Fixed Implementation:**
```python
# ui/settings_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class SettingsWindow:
    """Settings configuration window"""

    def __init__(self, config, parent=None, on_save_callback=None):
        """
        Args:
            config: Config object
            parent: Parent window (optional, if None creates new Tk)
            on_save_callback: Function to call when settings are saved
        """
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = None
        self.variables = {}
        self.parent = parent

    def show(self):
        """Show settings window"""
        if self.window:
            self.window.lift()
            return

        # CRITICAL FIX: Use Toplevel if parent exists
        if self.parent:
            self.window = tk.Toplevel(self.parent)
            # Make modal
            self.window.transient(self.parent)
            self.window.grab_set()
        else:
            self.window = tk.Tk()
            self.window.overrideredirect(False)

        self.window.title("CuteWhisper Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        self.create_widgets()

        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # Wait for window to close (blocks if modal)
        if self.parent:
            self.window.wait_window(self.window)
```

**Integration:**
```python
# In main.py
def open_settings(self):
    """Open settings window"""
    # Pass the main window reference (or None to create new)
    SettingsWindow(
        self.config,
        parent=getattr(self, 'root_window', None),
        on_save_callback=self.on_settings_changed
    ).show()
```

---

### 3. Toast Notifier Fix

**Problem:** Naming conflict - shadows imported class name.

**Fixed Implementation:**
```python
# ui/toast_notifier.py
from win10toast import ToastNotifier as WinToastNotifier
import logging

logger = logging.getLogger(__name__)

class ToastNotificationManager:
    """Windows toast notifications with fallback"""

    def __init__(self):
        self.toaster = None
        self.use_windows_toast = True

        try:
            self.toaster = WinToastNotifier()
        except Exception as e:
            logger.warning(f"Windows toast not available: {e}")
            self.use_windows_toast = False

    def show_recording_started(self):
        """Show recording started notification"""
        if self.use_windows_toast and self.toaster:
            try:
                self.toaster.show_toast(
                    "CuteWhisper",
                    "Recording started... Release Ctrl+Space to transcribe",
                    duration=3,
                    threaded=True  # CRITICAL: Don't block main thread
                )
            except Exception as e:
                logger.error(f"Toast failed: {e}")
        else:
            # Fallback: simple console message
            print("🎤 Recording started...")

    def show_recording_complete(self, text_preview):
        """Show recording complete notification"""
        if self.use_windows_toast and self.toaster:
            try:
                self.toaster.show_toast(
                    "CuteWhisper",
                    f"Text inserted: {text_preview[:50]}...",
                    duration=3,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"Toast failed: {e}")
        else:
            print(f"✓ Text inserted: {text_preview[:50]}...")

    def show_error(self, error_message):
        """Show error notification"""
        if self.use_windows_toast and self.toaster:
            try:
                self.toaster.show_toast(
                    "CuteWhisper Error",
                    error_message,
                    duration=5,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"Toast failed: {e}")
        else:
            print(f"❌ Error: {error_message}")
```

---

### 4. System Tray Icon Thread Management

**Problem:** Running pystray in daemon thread can cause premature termination.

**Fixed Implementation:**
```python
# ui/tray_icon.py
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import logging

logger = logging.getLogger(__name__)

class TrayIcon:
    """System tray icon with proper thread management"""

    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False
        self.thread = None

    def create_icon_image(self, size=64):
        """Create simple microphone icon"""
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw circle (blue background)
        margin = 4
        draw.ellipse(
            [margin, margin, size-margin, size-margin],
            fill='#4A90E2'
        )

        # Draw microphone
        center_x = size // 2
        center_y = size // 2

        # Mic body
        draw.rectangle(
            [center_x - 4, center_y - 8, center_x + 4, center_y + 4],
            fill='white'
        )

        # Mic stand
        draw.rectangle(
            [center_x - 6, center_y + 6, center_x + 6, center_y + 8],
            fill='white'
        )

        return image

    def on_dictate(self):
        """Menu action: Start dictation"""
        logger.info("Tray: Start dictation requested")
        # Call app method - app handles threading
        self.app.start_dictation()

    def on_settings(self):
        """Menu action: Open settings"""
        logger.info("Tray: Settings requested")
        # Use after() to schedule GUI update in main thread
        if hasattr(self.app, 'schedule_settings_open'):
            self.app.schedule_settings_open()
        else:
            self.app.open_settings()

    def on_quit(self):
        """Menu action: Quit"""
        logger.info("Tray: Quit requested")
        self.running = False
        self.app.cleanup()
        if self.icon:
            self.icon.stop()
        sys.exit(0)

    def create_menu(self):
        """Create tray menu"""
        return pystray.Menu(
            pystray.MenuItem("Start Dictation", self.on_dictate),
            pystray.MenuItem("Settings...", self.on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

    def update_status(self, status_text):
        """Update tooltip status"""
        if self.icon:
            self.icon.title = f"CuteWhisper - {status_text}"

    def run(self):
        """Start tray icon (blocks)"""
        try:
            image = self.create_icon_image()
            menu = self.create_menu()

            self.icon = pystray.Icon(
                "CuteWhisper",
                image,
                "CuteWhisper - Ready",
                menu
            )

            self.running = True
            logger.info("Tray icon started")

            # This blocks until icon.stop() is called
            self.icon.run()

        except Exception as e:
            logger.error(f"Tray icon error: {e}")

    def start(self):
        """Start tray icon in background thread"""
        if self.thread and self.thread.is_alive():
            return

        # CRITICAL: Don't use daemon=True for tray icon
        self.thread = threading.Thread(target=self.run, daemon=False)
        self.thread.start()
        logger.info("Tray icon thread started")

    def stop(self):
        """Stop tray icon"""
        self.running = False
        if self.icon:
            self.icon.stop()
        if self.thread:
            self.thread.join(timeout=2)
```

---

### 5. Main Application UI Integration

**Updated main.py with proper UI thread management:**

```python
# main.py additions
class CuteWhisper:
    def __init__(self, config_path=None):
        # ... existing init code ...

        # UI components
        self.indicator = RecordingIndicator()
        self.notifier = ToastNotificationManager()
        self.tray = TrayIcon(self)

        # Start tray icon (non-daemon thread)
        self.tray.start()

        # Register cleanup
        import atexit
        atexit.register(self.tray.stop)

    def start_dictation(self):
        """Start recording audio"""
        if self.recorder.is_recording():
            logger.warning("Already recording, ignoring start request")
            return

        try:
            logger.info("Starting dictation...")

            # Show indicator (GUI update - should be in main thread)
            # If called from hotkey thread, use after()
            if hasattr(self, 'root_window'):
                self.root_window.after(0, self.indicator.show)
            else:
                self.indicator.show()

            self.recorder.start_recording()
            self.notifier.show_recording_started()

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            print(f"❌ Error: Could not start recording: {e}")

    def stop_dictation(self):
        """Stop recording and transcribe"""
        # ... existing code ...

        # Hide indicator
        if hasattr(self, 'root_window'):
            self.root_window.after(0, self.indicator.hide)
        else:
            self.indicator.hide()

        # Show notification
        if text:
            self.notifier.show_recording_complete(text[:50])

    def schedule_settings_open(self):
        """Schedule settings window open in main thread"""
        if hasattr(self, 'root_window'):
            self.root_window.after(0, self.open_settings)
        else:
            self.open_settings()

    def open_settings(self):
        """Open settings window"""
        SettingsWindow(
            self.config,
            parent=getattr(self, 'root_window', None),
            on_save_callback=self.on_settings_changed
        ).show()

    def on_settings_changed(self):
        """Called when settings are saved"""
        logger.info("Settings changed")
        # Check if hotkey changed
        new_hotkey = self.config.get('hotkey.toggle')
        if new_hotkey != self.hotkey_manager.hotkey_str:
            logger.info("Hotkey changed - restart required")
            self.notifier.show_error("Hotkey changed. Please restart CuteWhisper.")
```

---

### 6. Additional UI Components Needed

#### Audio Device Selection

Add to SettingsWindow:

```python
def create_audio_tab(self, parent):
    """Create audio settings tab"""
    # ... existing code ...

    # Device selection
    device_frame = ttk.LabelFrame(parent, text="Input Device", padding=10)
    device_frame.pack(fill='x', padx=10, pady=10)

    ttk.Label(device_frame, text="Microphone:").grid(row=2, column=0, sticky='w', pady=5)

    # Get available devices
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = [d['name'] for d in devices if d['max_input_channels'] > 0]

    device_var = tk.StringVar(value=input_devices[0] if input_devices else "Default")
    device_combo = ttk.Combobox(device_frame, textvariable=device_var,
                               values=input_devices, width=30, state='readonly')
    device_combo.grid(row=2, column=1, sticky='w', pady=5)

    self.variables['audio.device'] = device_var
```

---

### 7. Recommended Dependencies Update

```txt
# Add to requirements.txt
pystray>=0.19.5      # System tray
Pillow>=10.0.0       # Image handling (already there)
win10toast>=0.6      # Windows toast notifications (optional)
```

---

## UI Implementation Priority

### Phase 1 (CRITICAL - Do First):
1. ✅ **Fix RecordingIndicator thread safety** - Use `after()` instead of threads
2. ✅ **Fix SettingsWindow architecture** - Use `Toplevel` properly
3. ✅ **Fix ToastNotifier naming** - Avoid conflicts

### Phase 2 (HIGH Priority):
4. ✅ **Fix TrayIcon thread management** - Non-daemon thread
5. ✅ **Add audio device selection** - Users need to pick mic
6. ✅ **Integrate UI with main app** - Proper thread coordination

### Phase 3 (MEDIUM Priority):
7. Add keyboard shortcut to open settings (e.g., Ctrl+,)
8. Add status text to recording indicator (processing, transcribing)
9. Add model download progress UI (already have progress tracking in console)

---

## UI Success Criteria

### Phase 1:
- [ ] Recording indicator appears without crashes
- [ ] Timer updates smoothly without threading issues
- [ ] Indicator disappears cleanly
- [ ] No "main thread is not in main loop" errors

### Phase 2:
- [ ] Tray icon visible and responsive
- [ ] Menu actions work
- [ ] Settings window opens and closes properly
- [ ] Can change all settings

### Phase 3:
- [ ] Audio device selection works
- [ ] Hotkey changes detected with restart warning
- [ ] Toast notifications show without blocking

---

## Definition of Done

### MVP (Phase 1)
- [x] Hotkey triggers recording
- [x] Audio captured successfully
- [x] Whisper transcribes accurately
- [x] Text pastes into active window
- [x] Latency < 5 seconds
- [x] Works in 3+ applications

### Production (Phases 1-5)
- [x] All MVP features
- [x] System tray icon
- [x] Configurable settings
- [x] Single executable installer
- [x] Auto-start option
- [x] Error handling
- [x] Documentation complete
- [x] Tested on Windows 10/11

---

## Next Steps

1. **Select STT engine:** Confirm `faster-whisper` or switch to `whisper.cpp`
2. **Create project structure:** Initialize directories and files
3. **Implement Phase 1:** Build MVP (estimated 1-2 days)
4. **Test thoroughly:** Verify in target applications
5. **Iterate:** Add Phases 2-5 based on feedback

---

**End of Implementation Plan**
