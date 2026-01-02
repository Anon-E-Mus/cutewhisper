"""
Text Injection Module - Pastes transcribed text into active window
With clipboard preservation and automatic fallback
"""

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
        Initialize text injector

        Args:
            use_clipboard: If True, use clipboard+paste. If False, use typing.
            preserve_clipboard: If True, restore previous clipboard after paste.
        """
        self.use_clipboard = use_clipboard
        self.preserve_clipboard = preserve_clipboard
        self.clipboard_timeout = 5  # seconds

        # Safety: Disable pyautogui fail-safe
        pyautogui.FAILSAFE = False

        logger.info(f"TextInjector initialized (clipboard={use_clipboard}, preserve={preserve_clipboard})")

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
            logger.debug("No text to paste")
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
        """
        Paste using clipboard + Ctrl+V with optional clipboard preservation

        Args:
            text: Text to paste

        Returns:
            True if successful
        """
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

            logger.debug("Text pasted successfully")
            return True

        except Exception as e:
            logger.error(f"Clipboard paste failed: {e}")
            # Restore clipboard on error
            if old_clipboard:
                try:
                    self._copy_to_clipboard(old_clipboard)
                except:
                    pass
            return False

    def _type_text(self, text: str) -> bool:
        """
        Fallback: Type text character by character

        Args:
            text: Text to type

        Returns:
            True if successful
        """
        try:
            # Add a small delay for better reliability
            pyautogui.write(text, interval=0.01)
            logger.debug("Text typed successfully")
            return True
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False

    def _get_clipboard(self) -> str:
        """
        Get current clipboard content with timeout

        Returns:
            Clipboard text or empty string
        """
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
        """
        Windows clipboard operations with retry

        Args:
            text: Text to copy to clipboard
        """
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
