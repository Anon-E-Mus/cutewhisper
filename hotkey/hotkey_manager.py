"""
Hotkey Manager - Global hotkey listener with press-and-hold pattern
Uses pynput for cross-platform hotkey support (no admin required)
Dynamic hotkey configuration - supports any modifier + key combination
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

    Pattern: Press configured hotkey to start recording, release to stop and transcribe
    Supports dynamic hotkey configuration (e.g., 'ctrl+space', 'alt+shift+r', etc.)
    """

    def __init__(self, start_callback, stop_callback, hotkey_str='ctrl+space', recorder=None):
        """
        Initialize hotkey manager

        Args:
            start_callback: Function to call when hotkey is pressed
            stop_callback: Function to call when hotkey is released
            hotkey_str: Hotkey string in config format (e.g., 'ctrl+space')
            recorder: AudioRecorder instance (optional, for checking recording state)
        """
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.hotkey_str = hotkey_str
        self.recorder = recorder  # For checking if recording is in progress
        self.listener = None

        # CRITICAL FIX: Track whether hotkey combination was activated
        # This prevents the stop detection bug where modifiers are released before action key
        self.hotkey_was_active = False

        # Parse the hotkey configuration
        self.modifier_keys = []  # List of required modifiers
        self.action_key = None   # The main key to trigger
        self.pressed_modifiers = set()  # Track currently pressed modifiers

        # Thread spam prevention
        self.start_in_progress = False
        self.stop_in_progress = False

        # Parse and validate hotkey
        self._parse_hotkey_config()

        logger.info(f"HotkeyManager initialized with hotkey: {hotkey_str}")

    def _validate_hotkey_format(self, hotkey_str: str) -> bool:
        """
        Validate hotkey format

        Args:
            hotkey_str: Hotkey string to validate

        Returns:
            True if valid, False otherwise
        """
        if not hotkey_str or not isinstance(hotkey_str, str):
            return False

        parts = hotkey_str.lower().replace(' ', '').split('+')

        # Need at least 2 parts (modifier + key)
        if len(parts) < 2:
            return False

        # Check for empty parts (e.g., "ctrl++")
        if any(not p for p in parts):
            return False

        # Validate known modifiers
        valid_modifiers = ['ctrl', 'control', 'ctrl_l', 'ctrl_r',
                          'alt', 'alt_l', 'alt_r',
                          'shift', 'shift_l', 'shift_r',
                          'cmd', 'win', 'windows', 'meta']

        # Last part should be the action key (not a modifier)
        action_key = parts[-1]

        # Check if all parts except the last are valid modifiers
        for part in parts[:-1]:
            if part not in valid_modifiers:
                return False

        # CRITICAL FIX: Validate action key
        valid_special_keys = ['space', 'tab', 'enter', 'return', 'escape',
                             'up', 'down', 'left', 'right',
                             'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']

        # Check if action key is valid
        if action_key in valid_special_keys:
            return True

        # Check if it's a single alphanumeric character
        if len(action_key) == 1 and action_key.isalnum():
            return True

        return False

    def _parse_hotkey_config(self):
        """
        Parse the hotkey string into required modifiers and action key

        Example: 'ctrl+shift+space' -> modifiers=['ctrl', 'shift'], action_key='space'
        """
        # Validate and use default if invalid
        if not self._validate_hotkey_format(self.hotkey_str):
            logger.warning(f"Invalid hotkey: '{self.hotkey_str}', using default 'ctrl+space'")
            self.hotkey_str = 'ctrl+space'

        parts = self.hotkey_str.lower().replace(' ', '').split('+')

        # Last part is the action key
        self.action_key = parts[-1]

        # Everything before the last part are modifiers
        self.modifier_keys = parts[:-1]

        # Map modifier names to pynput Keys
        self.modifier_key_map = {
            'ctrl': [Key.ctrl_l, Key.ctrl_r, Key.ctrl],
            'control': [Key.ctrl_l, Key.ctrl_r, Key.ctrl],
            'ctrl_l': [Key.ctrl_l],
            'ctrl_r': [Key.ctrl_r],
            'alt': [Key.alt_l, Key.alt_r, Key.alt],
            'alt_l': [Key.alt_l],
            'alt_r': [Key.alt_r],
            'shift': [Key.shift_l, Key.shift_r, Key.shift],
            'shift_l': [Key.shift_l],
            'shift_r': [Key.shift_r],
            'cmd': [Key.cmd, Key.cmd_l, Key.cmd_r],
            'win': [Key.cmd, Key.cmd_l, Key.cmd_r],
            'windows': [Key.cmd, Key.cmd_l, Key.cmd_r],
            'meta': [Key.cmd, Key.cmd_l, Key.cmd_r],
        }

        # CRITICAL FIX: Complete action key mapping
        self.action_key_map = {
            # Special keys
            'space': Key.space,
            'tab': Key.tab,
            'enter': Key.enter,
            'return': Key.enter,
            'escape': Key.esc,
            'esc': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            # Function keys
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }

        logger.info(f"Parsed hotkey: modifiers={self.modifier_keys}, action={self.action_key}")

    def _convert_to_pynput_format(self, hotkey_str: str) -> str:
        """
        Convert config format to pynput format for display

        Args:
            hotkey_str: Config format like 'ctrl+space'

        Returns:
            Pynput format like '<ctrl>+<space>'
        """
        # Validate the hotkey format first
        if not self._validate_hotkey_format(hotkey_str):
            logger.warning(f"Invalid hotkey format: '{hotkey_str}', using default 'ctrl+space'")
            hotkey_str = 'ctrl+space'

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
            elif part in ['tab', 'enter', 'return', 'esc', 'escape']:
                formatted_parts.append(f'<{part}>')
            elif part.startswith('f'):
                formatted_parts.append(f'<{part}>')
            elif part in ['up', 'down', 'left', 'right']:
                formatted_parts.append(f'<{part}>')
            else:
                # Regular character keys
                formatted_parts.append(part)

        return '+'.join(formatted_parts)

    def _wrapped_start(self):
        """Wrapped start callback with flag to prevent concurrent execution"""
        try:
            self.start_callback()
        finally:
            self.start_in_progress = False

    def _wrapped_stop(self):
        """Wrapped stop callback with flag to prevent concurrent execution"""
        try:
            self.stop_callback()
        finally:
            self.stop_in_progress = False

    def _on_press(self, key):
        """
        Handle key press events - checks if configured hotkey combination is pressed
        """
        try:
            # Check if this key is one of our required modifiers
            for modifier in self.modifier_keys:
                if modifier in self.modifier_key_map:
                    if key in self.modifier_key_map[modifier]:
                        self.pressed_modifiers.add(modifier)
                        logger.debug(f"Modifier pressed: {modifier}, pressed: {self.pressed_modifiers}")
                        break

            # Check if action key is pressed
            action_key_match = False
            if self.action_key in self.action_key_map:
                # Special key (space, tab, etc.)
                if key == self.action_key_map[self.action_key]:
                    action_key_match = True
            else:
                # Regular character key - CRITICAL FIX: Support any alphanumeric
                if hasattr(key, 'char') and key.char and key.char.lower() == self.action_key:
                    action_key_match = True

            if action_key_match:
                logger.debug(f"Action key pressed: {self.action_key}")

            # Check if all required modifiers are pressed AND action key is pressed
            modifiers_pressed = all(m in self.pressed_modifiers for m in self.modifier_keys)

            if modifiers_pressed and action_key_match:
                # CRITICAL FIX: Set flag when hotkey is activated
                self.hotkey_was_active = True

                if not self.start_in_progress:
                    self.start_in_progress = True
                    logger.info(f"Hotkey triggered: {'+'.join(self.modifier_keys + [self.action_key])}")
                    threading.Thread(target=self._wrapped_start, daemon=True).start()
                else:
                    logger.debug("Start already in progress, ignoring")

        except Exception as e:
            logger.error(f"Hotkey press error: {e}")

    def _on_release(self, key):
        """
        Handle key release events - tracks when keys are released
        """
        try:
            # Check if this key is one of our required modifiers
            for modifier in self.modifier_keys:
                if modifier in self.modifier_key_map:
                    if key in self.modifier_key_map[modifier]:
                        self.pressed_modifiers.discard(modifier)
                        logger.debug(f"Modifier released: {modifier}, pressed: {self.pressed_modifiers}")
                        break

            # Check if action key is released
            action_key_released = False
            if self.action_key in self.action_key_map:
                if key == self.action_key_map[self.action_key]:
                    action_key_released = True
            else:
                # Regular character key
                if hasattr(key, 'char') and key.char and key.char.lower() == self.action_key:
                    action_key_released = True

            if action_key_released:
                # CRITICAL FIX: Use flag instead of checking current modifier state
                # This fixes the bug where releasing modifiers before action key prevents stop
                if self.hotkey_was_active:
                    self.hotkey_was_active = False  # Reset flag

                    if not self.stop_in_progress:
                        self.stop_in_progress = True
                        logger.info("Hotkey released: Stopping dictation")
                        threading.Thread(target=self._wrapped_stop, daemon=True).start()
                    else:
                        logger.debug("Stop already in progress, ignoring")

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

    def reload_hotkey(self, new_hotkey_str: str):
        """
        Reload hotkey configuration without restarting

        Args:
            new_hotkey_str: New hotkey string (e.g., 'ctrl+shift+space')

        Note: This stops the current listener and starts a new one
        """
        # CRITICAL FIX: Check if recording is in progress
        if self.recorder and hasattr(self.recorder, 'is_recording') and self.recorder.is_recording():
            logger.warning("Cannot change hotkey while recording")
            raise RuntimeError(
                "Cannot change hotkey while recording. "
                "Please stop recording first, then change the hotkey."
            )

        logger.info(f"Reloading hotkey: '{self.hotkey_str}' -> '{new_hotkey_str}'")

        # Stop current listener
        if self.listener:
            self.listener.stop()

        # Reset state
        self.pressed_modifiers.clear()
        self.hotkey_was_active = False
        self.start_in_progress = False
        self.stop_in_progress = False

        # Update hotkey string
        self.hotkey_str = new_hotkey_str

        # Parse new configuration
        self._parse_hotkey_config()

        # Restart listener
        self.listener = None  # Force new listener creation
        self.start()

        logger.info("Hotkey reloaded successfully")
