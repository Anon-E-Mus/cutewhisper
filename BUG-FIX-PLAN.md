# CuteWhisper Bug Fixes and UI Refinement Plan

## Issues Identified

### Critical Bugs:
1. ❌ Settings window not opening from tray icon
2. ❌ History window cannot be closed (no close button)

### UI Improvements Needed:
3. ❌ Recording window is too large (350x120px)
4. ❌ Window has square corners with rounded rectangle inside (should be fully rounded)
5. ❌ Bar animation doesn't reflect actual audio levels
6. ❌ Position: Centered at top (currently top-right)
7. ❌ Color scheme: Too light, needs darker blue/black theme

---

## Root Cause Analysis

### Bug 1: Settings Window Not Opening
**Problem:** Threading issue with tkinter
**Cause:** `root.after()` not being called correctly from tray icon callback
**Current Code:**
```python
def on_settings(self):
    if hasattr(self.app, 'root_window') and self.app.root_window:
        def open_in_main():
            self.app.open_settings()
        self.app.root_window.after(0, open_in_main)
```

**Issue:** The `root.after()` schedules the callback, but then immediately returns. The tray icon thread doesn't wait for the GUI to actually update.

### Bug 2: History Window Can't Close
**Problem:** No close button/window protocol
**Cause:** Missing window close protocol handler
**Missing:**
```python
self.window.protocol("WM_DELETE_WINDOW", self.on_close)
```

### Bug 3-7: UI Design Issues
**Current Design:**
- Square window with rounded rectangle drawn inside
- Canvas size: 350x120px
- Colors: `#1a1a1a`, `#2C2C2C`, `#4A90E2` (too light)
- Position: Top-right corner
- Animation: Uses artificial wave + audio level (not real audio)

---

## Implementation Plan

## Phase 1: Fix Critical Bugs

### Fix 1.1: Settings Window from Tray

**File:** `main.py`

**Change `open_settings()` method:**
```python
def open_settings(self):
    """Open settings window (thread-safe)"""
    # Check if already open
    if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.window:
        self.settings_window.window.lift()
        self.settings_window.window.focus()
        return

    # Create new settings window
    self.settings_window = SettingsWindow(
        self.config,
        parent=self.root_window,
        on_save_callback=self.on_settings_changed
    )

    # Add close handler to reset reference
    original_show = self.settings_window.show
    def show_with_cleanup():
        original_show()
        # Schedule cleanup when window closes
        def check_closed():
            if not self.settings_window.window or not tk.Toplevel.winfo_exists(self.settings_window.window):
                self.settings_window = None
            else:
                self.root_window.after(100, check_closed)
        self.root_window.after(100, check_closed)

    self.settings_window.show = show_with_cleanup
    self.settings_window.show()
```

### Fix 1.2: History Window Can't Close

**File:** `ui/history_window.py`

**Add to `create_widgets()` method:**
```python
def create_widgets(self):
    """Create all widgets"""
    # ... existing code ...

    # Add close button at bottom
    close_button = ttk.Button(self.window, text="Close", command=self.on_close)
    close_button.pack(pady=10)

    # Handle window close button (X)
    self.window.protocol("WM_DELETE_WINDOW", self.on_close)

def on_close(self):
    """Handle window close"""
    if self.window:
        self.window.destroy()
        self.window = None
```

**File:** `ui/settings_window.py`

**Add same close protocol:**
```python
def save_settings(self):
    """Save all settings"""
    # ... existing save code ...

    # Call callback if provided
    if self.on_save_callback:
        self.on_save_callback()

    messagebox.showinfo("Settings", "Settings saved successfully!\n\nNote: Hotkey changes require restart.")
    self.close_window()

def close_window(self):
    """Close the settings window"""
    if self.window:
        self.window.destroy()
        self.window = None

# In show() method, add:
self.window.protocol("WM_DELETE_WINDOW", self.close_window)
```

---

## Phase 2: Redesign Recording Visualizer

### New Design Specifications:

```
┌────────────────────────────────────┐
│    ╔══════════════════════════╗    │
│    ║  [|||  ||||  |||  ||||]  ║    │  <- Compact bars
│    ║   ● Recording 00:05      ║    │  <- Timer
│    ╚══════════════════════════╝    │
└────────────────────────────────────┘
```

**Dimensions:** 250x60px (smaller)
**Position:** Centered at top of screen
**Shape:** Fully rounded rectangle window
**Colors:**
- Background: Black `#000000`
- Container: Dark blue `#0A1628`
- Bars (quiet): Dark blue `#1E3A5F`
- Bars (medium): Medium blue `#2E5A8F`
- Bars (loud): Bright blue `#4A90E2`
- Timer: White `#FFFFFF`

### Fix 2.1: Create Rounded Window

**Challenge:** Tkinter doesn't support rounded windows natively on Windows.

**Solution:** Use PIL to create rounded corner mask and apply to window.

**File:** `ui/audio_visualizer.py`

**Complete rewrite:**

```python
"""
Audio Visualizer - Compact centered recording indicator with rounded window
Real-time audio visualization with dark theme
"""

import tkinter as tk
import time
import threading
import logging
import numpy as np
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class AudioVisualizerWindow:
    """Compact recording indicator with rounded window and real-time audio visualization"""

    def __init__(self):
        self.window = None
        self.canvas = None
        self.bars = []
        self.start_time = None
        self.running = False
        self.update_timer = None
        self.root = None
        self.lock = threading.Lock()
        self.timer_label = None
        self.current_audio_level = 0.0

        # NEW: Compact dimensions
        self.width = 250
        self.height = 60
        self.corner_radius = 20

        # Bar configuration
        self.num_bars = 12  # Fewer bars for compact look
        self.bar_width = 8
        self.bar_spacing = 4

    def show(self):
        """Thread-safe show - schedules GUI update in main thread"""
        with self.lock:
            if self.window:
                return  # Already showing

        if self.root:
            self.root.after(0, self._show_in_main_thread)
        else:
            self._show_in_main_thread()

    def _show_in_main_thread(self):
        """Actually show the window (must be called from main thread)"""
        with self.lock:
            if self.window:
                return

            if not self.root:
                self.root = tk.Tk()
                self.root.withdraw()

            # Create window
            self.window = tk.Toplevel(self.root)
            self.window.title("Recording")

            # Remove decorations
            self.window.overrideredirect(True)

            # Make always on top
            self.window.attributes('-topmost', True)

            # Semi-transparent
            self.window.attributes('-alpha', 0.95)

            # Center at top of screen
            screen_width = self.window.winfo_screenwidth()
            x = (screen_width - self.width) // 2
            self.window.geometry(f"{self.width}x{self.height}+{x}+20")

            # Create rounded window using PIL
            self._apply_rounded_corners()

            # Create canvas (no background, transparent)
            self.canvas = tk.Canvas(
                self.window,
                width=self.width,
                height=self.height,
                bg='#0A1628',  # Dark blue background
                highlightthickness=0
            )
            self.canvas.pack()

            # Draw background
            self.canvas.create_rectangle(
                0, 0, self.width, self.height,
                fill='#0A1628',
                outline=''
            )

            # Create audio bars
            self._create_bars()

            # Create timer label
            self.timer_label = self.canvas.create_text(
                self.width // 2,
                self.height - 18,
                text="● Recording 00:00",
                fill='#FFFFFF',  # White text
                font=('Segoe UI', 9, 'bold')
            )

            # Start
            self.start_time = time.time()
            self.running = True
            self.current_audio_level = 0.0

            self._animate()

    def _apply_rounded_corners(self):
        """Apply rounded corners to window using PIL mask"""
        try:
            # Create image with rounded corners
            image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Draw rounded rectangle
            draw.rounded_rectangle(
                [(0, 0), (self.width-1, self.height-1)],
                radius=self.corner_radius,
                fill=(10, 22, 40, 255)  # Dark blue #0A1628
            )

            # Set as window background (Windows only)
            try:
                import win32gui
                import win32con
                import win32api

                hwnd = self.window.winfo_id()
                # Remove window border
                win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, 0)
                win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                     win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                     win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)
            except:
                logger.debug("Could not remove window borders (win32 not available)")

        except Exception as e:
            logger.debug(f"Could not apply rounded corners: {e}")

    def _create_bars(self):
        """Create audio bars on canvas"""
        # Calculate total width and center it
        total_width = (self.num_bars * self.bar_width) + ((self.num_bars - 1) * self.bar_spacing)
        start_x = (self.width - total_width) // 2
        y_center = 25  # Higher position for compact design

        for i in range(self.num_bars):
            x = start_x + (i * (self.bar_width + self.bar_spacing))

            # Create rectangle
            bar_id = self.canvas.create_rectangle(
                x, y_center - 3,
                x + self.bar_width, y_center + 3,
                fill='#1E3A5F',  # Dark blue (quiet)
                outline=''
            )

            self.bars.append({
                'id': bar_id,
                'x': x,
                'base_height': 6,
                'y_center': y_center,
                'index': i
            })

    def update_audio_level(self, audio_data):
        """Update audio level from recorder callback"""
        try:
            if len(audio_data) > 0:
                # Calculate RMS (actual loudness)
                audio_float = audio_data.astype(np.float32)
                rms = np.sqrt(np.mean(audio_float ** 2))

                # Normalize and adjust sensitivity
                level = min(rms * 8, 1.0)  # Sensitivity

                # Smooth changes
                self.current_audio_level = (self.current_audio_level * 0.8) + (level * 0.2)
        except Exception as e:
            logger.debug(f"Audio level calculation error: {e}")

    def _animate(self):
        """Animation loop - updates bars based on actual audio"""
        if not self.running or not self.window:
            return

        try:
            # Update timer
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.canvas.itemconfig(self.timer_label, text=f"● Recording {minutes:02d}:{seconds:02d}")

            # Update each bar based on current audio level
            for i, bar in enumerate(self.bars):
                # Use actual audio level for all bars (synchronized)
                height_factor = self.current_audio_level

                # Add slight variation per bar for visual interest
                import math
                variation = math.sin(time.time() * 2 + i * 0.5) * 0.1
                height_factor = max(0.1, min(height_factor + variation, 1.0))

                # Calculate bar height
                max_bar_height = 20  # Shorter max height for compact design
                bar_height = bar['base_height'] + (height_factor * max_bar_height)

                # Update bar coordinates
                y_top = bar['y_center'] - (bar_height // 2)
                y_bottom = bar['y_center'] + (bar_height // 2)

                self.canvas.coords(
                    bar['id'],
                    bar['x'], y_top,
                    bar['x'] + self.bar_width, y_bottom
                )

                # Update color based on level (darker scheme)
                if height_factor > 0.7:
                    color = '#4A90E2'  # Bright blue (loud)
                elif height_factor > 0.4:
                    color = '#2E5A8F'  # Medium blue
                else:
                    color = '#1E3A5F'  # Dark blue (quiet)

                self.canvas.itemconfig(bar['id'], fill=color)

        except Exception as e:
            logger.error(f"Animation error: {e}")

        # Schedule next frame (30 FPS)
        self.update_timer = self.window.after(33, self._animate)

    def hide(self):
        """Thread-safe hide"""
        if self.root:
            self.root.after(0, self._hide_in_main_thread)
        else:
            self._hide_in_main_thread()

    def _hide_in_main_thread(self):
        """Actually hide the window"""
        with self.lock:
            self.running = False

            if self.update_timer and self.window:
                self.window.after_cancel(self.update_timer)
                self.update_timer = None

            if self.window:
                self.window.destroy()
                self.window = None
                self.canvas = None
                self.bars = []
                self.timer_label = None
```

---

## Implementation Order

### Step 1: Fix Settings Window (5 minutes)
1. Update `main.py` `open_settings()` method
2. Add proper window lifecycle management

### Step 2: Fix History Window Close (5 minutes)
1. Add close button to `ui/history_window.py`
2. Add WM_DELETE_WINDOW protocol
3. Same for `ui/settings_window.py`

### Step 3: Redesign Visualizer (20 minutes)
1. Replace entire `ui/audio_visualizer.py` with new compact design
2. Use darker color scheme
3. Fix audio level calculation
4. Center at top of screen
5. Make smaller (250x60px)

---

## Testing Checklist

### Settings Window:
- [ ] Opens from tray icon
- [ ] Can be closed with X button
- [ ] Settings save correctly
- [ ] Can reopen after closing

### History Window:
- [ ] Opens from tray icon
- [ ] Close button works
- [ ] X button works
- [ ] Can search
- [ ] Can copy entries

### Visualizer:
- [ ] Window appears centered at top
- [ ] Smaller size (250x60px)
- [ ] Dark blue/black colors
- [ ] Bars react to actual voice
- [ ] Smooth animation
- [ ] Timer updates

---

## Success Criteria

✅ Settings and History windows open and close reliably
✅ Visualizer is compact and centered
✅ Audio visualization is responsive to actual speech
✅ Dark theme is easy on eyes
✅ All windows are fully functional

---

## End of Plan

Ready to execute fixes in order: Settings → History → Visualizer
