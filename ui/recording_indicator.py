"""
Recording Indicator - Floating window showing recording status
Thread-safe implementation using tkinter's event loop
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

    def show(self):
        """Thread-safe show - schedules GUI update in main thread"""
        with self.lock:
            if self.window:
                return  # Already showing

        # Schedule the show in the main thread using root
        if self.root:
            self.root.after(0, self._show_in_main_thread)
        else:
            # Fallback: create root and show
            self._show_in_main_thread()

    def _show_in_main_thread(self):
        """Actually show the window (must be called from main thread)"""
        with self.lock:
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
        """Thread-safe hide - schedules GUI update in main thread"""
        # Schedule the hide in the main thread
        if self.root:
            self.root.after(0, self._hide_in_main_thread)
        else:
            # Fallback
            self._hide_in_main_thread()

    def _hide_in_main_thread(self):
        """Actually hide the window (must be called from main thread)"""
        with self.lock:
            self.running = False

            # Cancel any pending updates
            if self.update_timer and self.window:
                self.window.after_cancel(self.update_timer)
                self.update_timer = None

            if self.window:
                self.window.destroy()
                self.window = None
                self.label = None

