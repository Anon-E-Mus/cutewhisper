"""
System Tray Icon - Background icon with menu
Proper thread management for non-daemon operation
"""

import threading
import sys
import logging

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None
    PYSTRAY_AVAILABLE = False

logger = logging.getLogger(__name__)


class TrayIcon:
    """System tray icon with proper thread management"""

    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False
        self.thread = None

        if not PYSTRAY_AVAILABLE:
            logger.warning("pystray not installed - tray icon disabled")

    def create_icon_image(self, size=64):
        """Create simple microphone icon"""
        if not Image or not ImageDraw:
            return None

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
        try:
            self.app.start_dictation()
        except Exception as e:
            logger.error(f"Failed to start dictation from tray: {e}")

    def on_settings(self):
        """Menu action: Open settings"""
        logger.info("Tray: Settings requested")

        # CRITICAL FIX: Use root.after() to schedule in main thread
        if hasattr(self.app, 'root_window') and self.app.root_window:
            # Schedule GUI update in main thread
            def open_in_main():
                self.app.open_settings()
            self.app.root_window.after(0, open_in_main)
        else:
            # Fallback
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
        if not PYSTRAY_AVAILABLE:
            return None

        return pystray.Menu(
            pystray.MenuItem("Start Dictation", self.on_dictate),
            pystray.MenuItem("History...", self.on_history),
            pystray.MenuItem("Settings...", self.on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

    def on_history(self):
        """Menu action: Open history"""
        logger.info("Tray: History requested")

        # Schedule GUI update in main thread
        if hasattr(self.app, 'root_window') and self.app.root_window:
            def open_in_main():
                self.app.open_history()
            self.app.root_window.after(0, open_in_main)
        else:
            # Fallback
            self.app.open_history()

    def update_status(self, status_text):
        """Update tooltip status"""
        if self.icon:
            self.icon.title = f"CuteWhisper - {status_text}"

    def run(self):
        """Start tray icon (blocks)"""
        if not PYSTRAY_AVAILABLE:
            logger.warning("Tray icon not available - skipping")
            return

        try:
            image = self.create_icon_image()
            if not image:
                logger.error("Failed to create tray icon image")
                return

            menu = self.create_menu()
            if not menu:
                logger.error("Failed to create tray menu")
                return

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
        if not PYSTRAY_AVAILABLE:
            logger.warning("Tray icon not available - skipping start")
            return

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
