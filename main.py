#!/usr/bin/env python3
"""
CuteWhisper - Windows Local Dictation Tool

A privacy-focused dictation tool that transcribes speech to text locally
using Whisper. Press and hold Ctrl+Space to record, release to transcribe.

Author: CuteWhisper Team
Version: 1.0.0
"""

from audio.recorder import AudioRecorder
from stt.whisper_wrapper import WhisperTranscriber
from injection.text_paster import TextInjector
from hotkey.hotkey_manager import HotkeyManager
from config.settings import Config
from utils.logger import setup_logging
from utils.cleanup import cleanup_old_temp_files
from utils.history_manager import HistoryManager
from ui.audio_visualizer import AudioVisualizerWindow
from ui.toast_notifier import ToastNotificationManager
from ui.tray_icon import TrayIcon
from ui.settings_window import SettingsWindow
from ui.history_window import HistoryWindow
import argparse
import os
import sys
import atexit
import tkinter as tk
from pathlib import Path

# Setup logging
logger = setup_logging()


class CuteWhisper:
    """Main CuteWhisper application"""

    def __init__(self, config_path=None):
        """
        Initialize CuteWhisper application

        Args:
            config_path: Optional path to custom config file
        """
        logger.info("Initializing CuteWhisper...")

        # Load configuration
        self.config = Config(config_path)

        # Clean up old temp files on startup
        cleanup_old_temp_files()

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

        # Log GPU status
        if self.config.get('whisper.device') == 'cuda':
            logger.info("Using CUDA GPU acceleration")
            print("[GPU] CUDA enabled - transcription will be faster!")
        else:
            logger.info("Using CPU for transcription")
            print("[CPU] GPU not enabled - transcription will be slower")

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

        # Initialize UI components
        # Create main hidden tkinter window for event loop
        self.root_window = tk.Tk()
        self.root_window.withdraw()  # Hide the main window

        self.visualizer = AudioVisualizerWindow()
        self.visualizer.root = self.root_window  # Pass root to visualizer

        self.notifier = ToastNotificationManager()
        self.history = HistoryManager()
        self.tray = TrayIcon(self)

        # Register cleanup on exit
        atexit.register(self.cleanup)

        # Track temp files for cleanup
        self.temp_files = []

        logger.info("CuteWhisper initialized successfully")

    def start_dictation(self):
        """Start recording audio"""
        if self.recorder.is_recording():
            logger.warning("Already recording, ignoring start request")
            return

        try:
            logger.info("Starting dictation...")
            print("\n[MIC] Recording... (hold Ctrl+Space)")

            # Show audio visualizer
            self.visualizer.show()

            # REMOVED: Toast notification for recording started (visualizer is enough feedback)

            # Start recording with audio callback for visualizer
            self.recorder.start_recording(audio_callback_func=self.visualizer.update_audio_level)

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            print(f"[X] Error: Could not start recording: {e}")
            self.visualizer.hide()  # Hide visualizer on error

    def stop_dictation(self):
        """Stop recording and transcribe"""
        if not self.recorder.is_recording():
            logger.warning("Not recording, ignoring stop request")
            return

        try:
            logger.info("Stopping dictation...")
            print("\n[STOP] Processing...")

            # Hide audio visualizer
            self.visualizer.hide()

            # Stop recording and get audio path
            audio_path = self.recorder.stop_recording()

            if not audio_path:
                print("[X] No audio recorded")
                return

            # Track for cleanup
            self.temp_files.append(audio_path)

            # Transcribe
            logger.info(f"Transcribing: {audio_path}")
            print("[AI] Transcribing...")

            result = self.transcriber.transcribe(
                audio_path,
                language=self.config.get('whisper.language', 'auto')
            )

            text = result.get('text', '').strip()
            if not text:
                print("[!] No speech detected")
                logger.info("No speech detected in audio")
                return

            # Display result
            print(f"\n[TEXT] {text}")
            logger.info(f"Transcription: {text[:50]}...")

            # Save to history
            duration = result.get('duration', 0)
            language = result.get('language', 'en')
            self.history.add_transcription(text, language=language, duration=duration, audio_file=audio_path)

            # Paste text
            if self.injector.paste_text(text):
                print("[OK] Text inserted!")
                logger.info("Text successfully injected")

                # REMOVED: Toast notification for completion (too intrusive)
                # Users can check history instead
            else:
                print("[X] Failed to insert text")
                logger.error("Text injection failed")

            # Cleanup temp file
            self._cleanup_file(audio_path)

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            print(f"[X] Error: {e}")
            self.visualizer.hide()
            self.notifier.show_error(str(e))

        except RuntimeError as e:
            logger.error(f"Transcription error: {e}")
            print(f"[X] Transcription failed: {e}")
            self.visualizer.hide()
            self.notifier.show_error(f"Transcription failed: {e}")

        except Exception as e:
            logger.error(f"Unexpected error during dictation: {e}", exc_info=True)
            print(f"[X] Unexpected error: {e}")
            self.visualizer.hide()
            self.notifier.show_error(f"Unexpected error: {e}")

    def _cleanup_file(self, file_path):
        """
        Safely remove a temp file

        Args:
            file_path: Path to file to remove
        """
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

    def schedule_settings_open(self):
        """Schedule settings window open in main thread"""
        # For thread-safe GUI updates
        self.open_settings()

    def open_settings(self):
        """Open settings window"""
        # Check if already open
        if hasattr(self, 'settings_window') and self.settings_window and hasattr(self.settings_window, 'window') and self.settings_window.window:
            try:
                self.settings_window.window.lift()
                self.settings_window.window.focus()
                return
            except:
                # Window was closed, create new one
                self.settings_window = None

        # Create new settings window
        self.settings_window = SettingsWindow(
            self.config,
            parent=self.root_window,
            on_save_callback=self.on_settings_changed
        )

        # Set up cleanup when window closes
        self.settings_window.show()

    def open_history(self):
        """Open transcription history window"""
        HistoryWindow(
            self.history,
            parent=self.root_window
        ).show()

    def on_settings_changed(self):
        """Called when settings are saved"""
        logger.info("Settings changed")
        # Check if hotkey changed
        new_hotkey = self.config.get('hotkey.toggle')
        if new_hotkey != self.hotkey_manager.hotkey_str:
            logger.info("Hotkey changed - restart required")
            self.notifier.show_error("Hotkey changed. Please restart CuteWhisper.")


    def run(self):
        """Start listening for hotkeys"""
        try:
            print("\n" + "="*50)
            print("  CuteWhisper - Local Dictation Tool")
            print("="*50)

            hotkey = self.config.get('hotkey.toggle', 'ctrl+space')
            model = self.config.get('whisper.model_size', 'base')
            clipboard = self.config.get('ui.preserve_clipboard', True)

            print(f"\nConfiguration:")
            print(f"  Model: {model}")
            print(f"  Hotkey: {hotkey} (press and hold to record)")
            print(f"  Clipboard preservation: {clipboard}")

            print(f"\nReady! Close the window or right-click tray icon to quit.\n")

            # Start hotkey listener
            self.hotkey_manager.start()

            # Start system tray icon
            self.tray.start()

            # Start tkinter event loop (this blocks)
            try:
                self.root_window.mainloop()
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                logger.info("Interrupted by user")
            finally:
                self.hotkey_manager.stop()
                self.tray.stop()
                self.cleanup()

        except Exception as e:
            logger.error(f"Error in run loop: {e}", exc_info=True)
            print(f"\n[X] Error: {e}")
            self.cleanup()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CuteWhisper - Windows Local Dictation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default config
  python main.py --config custom.yaml    # Use custom config
  python main.py --version          # Show version
        """
    )

    parser.add_argument(
        '--config', '-c',
        help="Path to config file (default: config/user_config.yaml)"
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='CuteWhisper 1.0.0'
    )

    args = parser.parse_args()

    try:
        app = CuteWhisper(config_path=args.config)
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\n[X] Fatal error: {e}")
        print("\nPlease check the logs for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
