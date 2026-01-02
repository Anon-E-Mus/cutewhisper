"""
Toast Notifier - Windows toast notifications with fallback
"""

import logging

try:
    from win10toast import ToastNotifier as WinToastNotifier
    WIN_TOAST_AVAILABLE = True
except ImportError:
    WinToastNotifier = None
    WIN_TOAST_AVAILABLE = False

logger = logging.getLogger(__name__)


class ToastNotificationManager:
    """Windows toast notifications with fallback"""

    def __init__(self):
        self.toaster = None
        self.use_windows_toast = True

        if WIN_TOAST_AVAILABLE:
            try:
                self.toaster = WinToastNotifier()
                logger.info("Windows toast notifications enabled")
            except Exception as e:
                logger.warning(f"Windows toast not available: {e}")
                self.use_windows_toast = False
        else:
            logger.warning("win10toast not installed - using console fallback")
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
            print("[MIC] Recording started...")

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
            print(f"[OK] Text inserted: {text_preview[:50]}...")

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
            print(f"[X] Error: {error_message}")
