"""
Recording Indicator - Floating window showing recording status
Thread-safe implementation using tkinter's event loop
Fixed race condition with showing_flag
"""

import tkinter as tk
import time
import logging
import threading

logger = logging.getLogger(__name__)


class RecordingIndicator:
    """Thread-safe recording indicator using tkinter"""

    def __init__(self):
        self.window = None
        self.label = None
        self.start_time = None
        self.running = False
        self.update_timer = None  # Use tkinter's after() method
        self.root = None  # Reference to main window
        self.lock = threading.Lock()
        self.showing_flag = False  # CRITICAL FIX: Prevent race condition

    def show(self):
        """Thread-safe show - schedules GUI update in main thread"""
        with self.lock:
            # CRITICAL FIX: Check flag FIRST, before any scheduling
            if self.showing_flag or self.window:
                return  # Already showing or scheduled to show

            # Mark as showing BEFORE releasing lock
            self.showing_flag = True

        # Schedule the show in the main thread (outside lock)
        if self.root:
            self.root.after(0, self._show_in_main_thread)
        else:
            self._show_in_main_thread()

    def _show_in_main_thread(self):
        """Actually show the window (must be called from main thread)"""
        with self.lock:
            # Double-check flag and window
            if self.window:
                self.showing_flag = False  # Reset flag
                return  # Already created

            # Create root if needed
            if not self.root:
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

            # Note: showing_flag remains True since window is now visible

        # Start updates (outside lock)
        self._schedule_update()

    def _schedule_update(self):
        """Schedule next update using tkinter's event loop"""
        # CRITICAL FIX: Check window state with lock
        with self.lock:
            if not self.running or not self.window:
                return

        # Outside lock - safe to access window
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        if self.label:
            self.label.config(text=f"● Recording {minutes:02d}:{seconds:02d}")

        # Schedule next update in 1000ms (1 second)
        if self.window:
            self.update_timer = self.window.after(1000, self._schedule_update)

    def hide(self):
        """Thread-safe hide - schedules GUI update in main thread"""
        # CRITICAL FIX: Add lock for thread safety
        with self.lock:
            if self.showing_flag == False and self.window is None:
                return  # Already hidden

        # Schedule the hide in the main thread
        if self.root:
            self.root.after(0, self._hide_in_main_thread)
        else:
            # No root means no window, nothing to hide
            logger.debug("No root window, skipping hide")

    def _hide_in_main_thread(self):
        """Actually hide the window (must be called from main thread)"""
        with self.lock:
            self.running = False
            self.showing_flag = False  # CRITICAL: Reset flag

            # Cancel any pending updates
            if self.update_timer and self.window:
                self.window.after_cancel(self.update_timer)
                self.update_timer = None

            if self.window:
                self.window.destroy()
                self.window = None
                self.label = None
