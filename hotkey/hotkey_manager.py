"""
Hotkey Manager - Global hotkey listener with press-and-hold pattern
Uses pynput for cross-platform hotkey support (no admin required)
"""

from pynput import keyboard
from pynput.keyboard import Key
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
        Initialize hotkey manager

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

        logger.info(f"HotkeyManager initialized with hotkey: {hotkey_str}")

    def _convert_to_pynput_format(self, hotkey_str: str) -> str:
        """
        Convert config format to pynput format

        Args:
            hotkey_str: Config format like 'ctrl+space'

        Returns:
            Pynput format like '<ctrl>+<space>'
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
        """
        Handle key press events

        Args:
            key: Pressed key
        """
        try:
            # Track Ctrl state
            if key in [Key.ctrl_l, Key.ctrl_r, Key.ctrl]:
                self.ctrl_pressed = True
                logger.debug("Ctrl pressed")

            # Track Space state
            if key == Key.space:
                self.space_pressed = True
                logger.debug("Space pressed")

            # Check if both Ctrl and Space are pressed
            if self.ctrl_pressed and self.space_pressed:
                # Start recording in a separate thread to avoid blocking
                logger.debug("Hotkey triggered: Starting dictation")
                threading.Thread(target=self.start_callback, daemon=True).start()

        except Exception as e:
            logger.error(f"Hotkey press error: {e}")

    def _on_release(self, key):
        """
        Handle key release events

        Args:
            key: Released key
        """
        try:
            # Track Ctrl state
            if key in [Key.ctrl_l, Key.ctrl_r, Key.ctrl]:
                self.ctrl_pressed = False
                logger.debug("Ctrl released")

            # Track Space state
            if key == Key.space:
                if self.space_pressed:  # If space was being held
                    self.space_pressed = False
                    # Stop recording and transcribe
                    logger.debug("Hotkey released: Stopping dictation")
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
            print(f"\n[HOTKEY] {pynput_format}")
            print("  Press and hold to record, release to transcribe")

        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise

    def listen(self):
        """
        Start listening for hotkeys (blocks forever)

        This is the main entry point for the hotkey system
        """
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
