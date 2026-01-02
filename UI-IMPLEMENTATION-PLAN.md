# UI Implementation Plan — CuteWhisper

**Version:** 1.0
**Created:** 2025-01-02
**Status:** Planning Phase

---

## Table of Contents

1. [Overview](#overview)
2. [UI Components](#ui-components)
3. [Phase 1: Visual Recording Indicator](#phase-1-visual-recording-indicator)
4. [Phase 2: System Tray Icon](#phase-2-system-tray-icon)
5. [Phase 3: Settings Window](#phase-3-settings-window)
6. [Phase 4: Toast Notifications](#phase-4-toast-notifications)
7. [Phase 5: Optional Status Dashboard](#phase-5-optional-status-dashboard)
8. [Implementation Priority](#implementation-priority)
9. [Technical Decisions](#technical-decisions)

---

## Overview

CuteWhisper currently runs as a background console application with minimal visual feedback. This plan adds comprehensive UI components to improve user experience and provide real-time feedback.

### Current State
- ✅ Core dictation works
- ✅ Hotkey listener active
- ❌ No visual feedback during recording
- ❌ No GUI for settings
- ❌ No system tray presence
- ❌ Console-only output

### Goals
- **Visual Feedback**: Clear indication when recording is active
- **Easy Configuration**: GUI for changing settings
- **Always Available**: System tray icon for quick access
- **Status Updates**: Toast notifications for important events
- **Professional Polish**: Production-ready appearance

---

## UI Components

### 1. Recording Indicator
**Purpose:** Visual feedback when recording is active
**Type:** Floating overlay window
**Priority:** HIGH (User requested)

### 2. System Tray Icon
**Purpose:** Always-present icon with menu
**Type:** Windows system tray
**Priority:** HIGH

### 3. Settings Window
**Purpose:** GUI for configuration
**Type:** Modal window
**Priority:** MEDIUM

### 4. Toast Notifications
**Purpose:** Status updates
**Type:** Windows toast notifications
**Priority:** MEDIUM

### 5. Status Dashboard (Optional)
**Purpose:** Advanced status view
**Type:** Main window with statistics
**Priority:** LOW

---

## Phase 1: Visual Recording Indicator

**Goal:** Provide clear visual feedback when recording is active

### Design Options

#### Option A: Floating Window (RECOMMENDED)
A small, always-on-top window that appears when recording starts.

**Visual Design:**
```
┌─────────────────────────┐
│  🔴 Recording... 0:05   │  ← Shows recording duration
│  [●]                    │  ← Pulsing red circle
└─────────────────────────┘
```

**Features:**
- Shows when recording is active
- Displays recording duration (seconds)
- Pulsing red circle animation
- Semi-transparent background
- Positioned in top-right corner
- Auto-hides after transcription completes

**Pros:**
- Always visible during recording
- Clear status indication
- Minimal distraction
- Easy to implement with tkinter

**Cons:**
- Might obscure content (make semi-transparent)
- Appears/disappears (can be surprising)

#### Option B: LED Indicator (Alternative)
Small colored dot that changes state:
- Gray = Idle
- Red = Recording
- Green = Processing

**Implementation:**
```python
# ui/recording_indicator.py
import tkinter as tk
import threading
import time

class RecordingIndicator:
    """Floating recording indicator with timer"""

    def __init__(self):
        self.window = None
        self.label = None
        self.start_time = None
        self.update_thread = None
        self.running = False

    def show(self):
        """Show recording indicator"""
        if self.window:
            return  # Already showing

        self.window = tk.Tk()
        self.window.title("Recording")

        # Remove window decorations (optional)
        self.window.overrideredirect(True)

        # Make always on top
        self.window.attributes('-topmost', True)

        # Make semi-transparent (80% opacity)
        self.window.attributes('-alpha', 0.8)

        # Position in top-right corner
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"200x60+{screen_width-220}+10")

        # Create content
        self.label = tk.Label(
            self.window,
            text="● Recording...",
            bg="#FF0000",  # Red background
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.label.pack(fill='both', expand=True)

        # Start timer
        self.start_time = time.time()
        self.running = True

        # Start update thread
        self.update_thread = threading.Thread(
            target=self._update_timer,
            daemon=True
        )
        self.update_thread.start()

        self.window.update()

    def _update_timer(self):
        """Update recording time every second"""
        while self.running:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60

            if self.label:
                self.label.config(
                    text=f"● Recording {minutes:02d}:{seconds:02d}"
                )

            time.sleep(1)

    def hide(self):
        """Hide recording indicator"""
        self.running = False

        if self.window:
            self.window.destroy()
            self.window = None
            self.label = None
```

**Usage in main.py:**
```python
# In __init__
self.indicator = RecordingIndicator()

# In start_dictation()
self.indicator.show()

# In stop_dictation()
self.indicator.hide()
```

---

### Enhanced Version with Animation

**Add pulsing effect:**

```python
def _animate(self):
    """Animate pulsing effect"""
    alpha_values = [0.6, 0.8, 1.0, 0.8, 0.6]  # Pulse sequence
    index = 0

    while self.running:
        if self.window and self.label:
            # Pulse background color
            self.window.attributes('-alpha', alpha_values[index % len(alpha_values)])
            index += 1
            time.sleep(0.5)
```

---

## Phase 2: System Tray Icon

**Goal:** Provide always-accessible icon with menu

### Design

**Icon Design:**
- Use microphone emoji 🎤 or create custom icon
- Blue background with white microphone
- 16x16 or 32x32 pixels

**Menu Options:**
```
Right-click menu:
├── Start Dictation
├── Settings...
├── ──────────────
├── Status: Idle
├── Model: base
├── ──────────────
├── View Logs
├── About
├── ──────────────
└── Quit
```

### Implementation

**File:** `ui/tray_icon.py`

```python
import pystray
from PIL import Image, ImageDraw, ImageFont
import threading
import sys
import os

class TrayIcon:
    """System tray icon with menu"""

    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False
        self.menu_items = {}

    def create_icon_image(self, size=64):
        """Create simple microphone icon"""
        # Create image with transparent background
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw circle (blue background)
        margin = 4
        draw.ellipse(
            [margin, margin, size-margin, size-margin],
            fill='#4A90E2'  # Blue
        )

        # Draw microphone (simple representation)
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
        threading.Thread(
            target=self.app.start_dictation,
            daemon=True
        ).start()

    def on_settings(self):
        """Menu action: Open settings"""
        self.app.open_settings()

    def on_logs(self):
        """Menu action: View logs"""
        os.startfile('logs/cutewhisper.log')

    def on_about(self):
        """Menu action: About"""
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showinfo(
            "About CuteWhisper",
            "CuteWhisper v1.0\n\n"
            "A privacy-focused local dictation tool\n"
            "using OpenAI's Whisper model.\n\n"
            "Press Ctrl+Space to dictate!"
        )
        root.destroy()

    def on_quit(self):
        """Menu action: Quit"""
        self.running = False
        self.app.cleanup()
        self.icon.stop()
        sys.exit(0)

    def create_menu(self):
        """Create tray menu"""
        return pystray.Menu(
            pystray.MenuItem("Start Dictation", self.on_dictate),
            pystray.MenuItem("Settings...", self.on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("View Logs", self.on_logs),
            pystray.MenuItem("About", self.on_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

    def update_status(self, status_text):
        """Update tooltip status"""
        if self.icon:
            self.icon.title = f"CuteWhisper - {status_text}"

    def run(self):
        """Start tray icon"""
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
            self.icon.run()

        except Exception as e:
            print(f"Tray icon error: {e}")

    def stop(self):
        """Stop tray icon"""
        self.running = False
        if self.icon:
            self.icon.stop()
```

**Integration in main.py:**
```python
# In __init__
self.tray = TrayIcon(self)

# Run in separate thread
import threading
tray_thread = threading.Thread(
    target=self.tray.run,
    daemon=True
)
tray_thread.start()

# Update status when recording
def start_dictation(self):
    self.tray.update_status("Recording...")
    # ... rest of code

def stop_dictation(self):
    self.tray.update_status("Ready")
    # ... rest of code
```

---

## Phase 3: Settings Window

**Goal:** Provide GUI for configuration

### Design

**Layout:**
```
┌─────────────────────────────────────────┐
│ CuteWhisper Settings              [_][□][X] │
├─────────────────────────────────────────┤
│                                         │
│ Hotkeys                                 │
│ ┌─────────────────────────────────┐   │
│ │ Toggle: [ctrl+space          ]   │   │
│ └─────────────────────────────────┘   │
│                                         │
│ Audio Settings                          │
│ ┌─────────────────────────────────┐   │
│ │ Sample Rate: [16000         ▼]   │   │
│ │ Channels:    [Mono (1)      ▼]   │   │
│ └─────────────────────────────────┘   │
│                                         │
│ Whisper Model                           │
│ ┌─────────────────────────────────┐   │
│ │ Model:      [base           ▼]   │   │
│ │ Language:   [Auto-detect    ▼]   │   │
│ │ Device:     [CPU            ▼]   │   │
│ └─────────────────────────────────┘   │
│                                         │
│ Text Injection                          │
│ ┌─────────────────────────────────┐   │
│ │ ☑ Use clipboard                 │   │
│ │ ☑ Preserve clipboard            │   │
│ │ ☐ Show notifications             │   │
│ └─────────────────────────────────┘   │
│                                         │
│ Model Information                      │
│ ┌─────────────────────────────────┐   │
│ │ Current: base (~74MB)            │   │
│ │ Status:  ✓ Loaded               │   │
│ │ [Change Model...]               │   │
│ └─────────────────────────────────┘   │
│                                         │
│         [Save] [Cancel] [Apply]         │
└─────────────────────────────────────────┘
```

### Implementation

**File:** `ui/settings_window.py`

```python
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class SettingsWindow:
    """Settings configuration window"""

    def __init__(self, config, on_save_callback=None):
        """
        Initialize settings window

        Args:
            config: Config object
            on_save_callback: Function to call when settings are saved
        """
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = None
        self.variables = {}

    def show(self):
        """Show settings window"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Tk()
        self.window.title("CuteWhisper Settings")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        # Make modal (blocks main window)
        self.window.transient(self.window.master)
        self.window.grab_set()

        self.create_widgets()

        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create all widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: General
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        self.create_general_tab(general_frame)

        # Tab 2: Audio
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Audio")
        self.create_audio_tab(audio_frame)

        # Tab 3: Model
        model_frame = ttk.Frame(notebook)
        notebook.add(model_frame, text="Model")
        self.create_model_tab(model_frame)

        # Buttons at bottom
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.close).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Apply", command=self.apply).pack(side='right', padx=5)

    def create_general_tab(self, parent):
        """Create general settings tab"""
        frame = ttk.LabelFrame(parent, text="Hotkey", padding=10)
        frame.pack(fill='x', padx=10, pady=10)

        # Hotkey
        ttk.Label(frame, text="Toggle Recording:").grid(row=0, column=0, sticky='w', pady=5)
        hotkey_var = tk.StringVar(value=self.config.get('hotkey.toggle'))
        ttk.Entry(frame, textvariable=hotkey_var, width=20).grid(row=0, column=1, sticky='w', pady=5)
        self.variables['hotkey.toggle'] = hotkey_var

        # Text injection options
        frame2 = ttk.LabelFrame(parent, text="Text Injection", padding=10)
        frame2.pack(fill='x', padx=10, pady=10)

        use_clipboard = tk.BooleanVar(value=self.config.get('ui.use_clipboard'))
        preserve_clipboard = tk.BooleanVar(value=self.config.get('ui.preserve_clipboard'))

        ttk.Checkbutton(frame2, text="Use clipboard (faster)", variable=use_clipboard).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Checkbutton(frame2, text="Preserve clipboard after paste", variable=preserve_clipboard).grid(row=1, column=0, sticky='w', pady=5)

        self.variables['ui.use_clipboard'] = use_clipboard
        self.variables['ui.preserve_clipboard'] = preserve_clipboard

    def create_audio_tab(self, parent):
        """Create audio settings tab"""
        frame = ttk.LabelFrame(parent, text="Audio Settings", padding=10)
        frame.pack(fill='x', padx=10, pady=10)

        # Sample rate
        ttk.Label(frame, text="Sample Rate:").grid(row=0, column=0, sticky='w', pady=5)
        sample_rate_var = tk.StringVar(value=str(self.config.get('audio.sample_rate')))
        sample_rate_combo = ttk.Combobox(frame, textvariable=sample_rate_var, values=['16000', '22050', '44100'], width=15, state='readonly')
        sample_rate_combo.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['audio.sample_rate'] = sample_rate_var

        # Channels
        ttk.Label(frame, text="Channels:").grid(row=1, column=0, sticky='w', pady=5)
        channels_var = tk.StringVar(value=str(self.config.get('audio.channels')))
        channels_combo = ttk.Combobox(frame, textvariable=channels_var, values=['1 (Mono)', '2 (Stereo)'], width=15, state='readonly')
        channels_combo.grid(row=1, column=1, sticky='w', pady=5)
        self.variables['audio.channels'] = channels_var

        # Info text
        info_label = ttk.Label(parent, text="Note: 16000 Hz Mono is recommended for Whisper", foreground='gray')
        info_label.pack(padx=10, pady=5)

    def create_model_tab(self, parent):
        """Create model settings tab"""
        frame = ttk.LabelFrame(parent, text="Whisper Model", padding=10)
        frame.pack(fill='x', padx=10, pady=10)

        # Model size
        ttk.Label(frame, text="Model Size:").grid(row=0, column=0, sticky='w', pady=5)
        model_var = tk.StringVar(value=self.config.get('whisper.model_size'))
        model_combo = ttk.Combobox(frame, textvariable=model_var, values=['tiny', 'base', 'small', 'medium', 'large'], width=15, state='readonly')
        model_combo.grid(row=0, column=1, sticky='w', pady=5)

        # Model info
        model_info = {
            'tiny': '~39MB - Fastest, good for testing',
            'base': '~74MB - Good balance (recommended)',
            'small': '~244MB - Better accuracy',
            'medium': '~769MB - Excellent accuracy',
            'large': '~1.5GB - Best accuracy, slowest'
        }

        info_label = ttk.Label(frame, text=model_info.get(model_var.get(), ''), foreground='gray')
        info_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=5)

        # Update info when model changes
        def on_model_change(*args):
            info_label.config(text=model_info.get(model_var.get(), ''))
        model_var.trace('w', on_model_change)

        self.variables['whisper.model_size'] = model_var

        # Language
        lang_frame = ttk.LabelFrame(parent, text="Language", padding=10)
        lang_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(lang_frame, text="Detection:").grid(row=0, column=0, sticky='w', pady=5)
        lang_var = tk.StringVar(value=self.config.get('whisper.language'))
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var,
                                   values=['Auto-detect', 'English', 'Spanish', 'French', 'German'],
                                   width=20, state='readonly')
        lang_combo.grid(row=0, column=1, sticky='w', pady=5)
        self.variables['whisper.language'] = lang_var

    def save(self):
        """Save settings and close"""
        self.apply_settings()
        self.close()

    def apply(self):
        """Apply settings without closing"""
        self.apply_settings()
        messagebox.showinfo("Settings", "Settings applied successfully!")

    def apply_settings(self):
        """Apply settings to config"""
        # Update config object
        try:
            # Hotkey
            self.config.set('hotkey.toggle', self.variables['hotkey.toggle'].get())

            # UI settings
            self.config.set('ui.use_clipboard', self.variables['ui.use_clipboard'].get())
            self.config.set('ui.preserve_clipboard', self.variables['ui.preserve_clipboard'].get())

            # Audio
            self.config.set('audio.sample_rate', int(self.variables['audio.sample_rate'].get()))
            channels = self.variables['audio.channels'].get()
            self.config.set('audio.channels', int(channels[0]))

            # Whisper
            self.config.set('whisper.model_size', self.variables['whisper.model_size'].get())

            lang = self.variables['whisper.language'].get()
            lang_map = {
                'Auto-detect': 'auto',
                'English': 'en',
                'Spanish': 'es',
                'French': 'fr',
                'German': 'de'
            }
            self.config.set('whisper.language', lang_map.get(lang, 'auto'))

            # Save to file
            self.config.save_config()

            # Call callback
            if self.on_save_callback:
                self.on_save_callback()

            logger.info("Settings saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            logger.error(f"Failed to save settings: {e}")

    def close(self):
        """Close settings window"""
        if self.window:
            self.window.destroy()
            self.window = None
```

---

## Phase 4: Toast Notifications

**Goal:** Show status updates

### Implementation

**Option A: Windows Toast Notifications (Recommended)**

```python
# ui/toast_notifier.py
from win10toast import ToastNotifier

class ToastNotifier:
    """Windows toast notifications"""

    def __init__(self):
        self.toaster = ToastNotifier()

    def show_recording_started(self):
        """Show recording started notification"""
        self.toaster.show_toast(
            "CuteWhisper",
            "Recording started... Release Ctrl+Space to transcribe",
            duration=3,
            icon_path=None  # Add icon later
        )

    def show_recording_complete(self, text_preview):
        """Show recording complete notification"""
        self.toaster.show_toast(
            "CuteWhisper",
            f"Text inserted: {text_preview[:50]}...",
            duration=3
        )

    def show_error(self, error_message):
        """Show error notification"""
        self.toaster.show_toast(
            "CuteWhisper Error",
            error_message,
            duration=5
        )
```

**Option B: Simple Notification Window (Fallback)**

```python
# ui/notification_window.py
import tkinter as tk
import threading
import time

class NotificationWindow:
    """Simple popup notification"""

    def show(self, title, message, duration=3):
        """Show notification"""
        def _show():
            window = tk.Tk()
            window.title(title)

            # Make always on top
            window.attributes('-topmost', True)

            # Remove decorations
            window.overrideredirect(True)

            # Position at top center
            screen_width = window.winfo_screenwidth()
            window.geometry(f"300x60+{(screen_width-300)//2}+10")

            # Content
            label = tk.Label(
                window,
                text=message,
                bg="#333333",
                fg="white",
                font=("Arial", 10),
                padx=20,
                pady=10
            )
            label.pack()

            window.update()

            # Auto-close after duration
            time.sleep(duration)
            window.destroy()

        threading.Thread(target=_show, daemon=True).start()
```

---

## Phase 5: Optional Status Dashboard

**Goal:** Advanced status view (OPTIONAL, low priority)

### Design

**Features:**
- Current status (Idle/Recording/Processing)
- Statistics (total recordings, total characters)
- Recent dictations list
- Quick actions (Start dictation, Open settings)
- Model info and performance metrics

```
┌─────────────────────────────────────────┐
│ CuteWhisper Dashboard                   │
├─────────────────────────────────────────┤
│                                         │
│ Status: [●] Ready                       │
│                                         │
│ Statistics                              │
│ Total Recordings: 42                    │
│ Total Characters: 15,234                │
│                                         │
│ Recent Dictations                       │
│ • "Hello world" (2s ago)               │
│ • "Testing microphone" (5m ago)        │
│                                         │
│ [Start Dictation]  [Settings]          │
│                                         │
└─────────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1 (MUST HAVE - Do First)
1. **Visual Recording Indicator** - User needs to know it's working
   - Time: 1-2 hours
   - Impact: HIGH
   - Complexity: LOW

2. **System Tray Icon** - Make app always accessible
   - Time: 2-3 hours
   - Impact: HIGH
   - Complexity: MEDIUM

### Phase 2 (SHOULD HAVE - Do Next)
3. **Toast Notifications** - Better feedback
   - Time: 1 hour
   - Impact: MEDIUM
   - Complexity: LOW

4. **Settings Window** - Easy configuration
   - Time: 3-4 hours
   - Impact: HIGH
   - Complexity: MEDIUM

### Phase 3 (NICE TO HAVE - Do Later)
5. **Status Dashboard** - Advanced users
   - Time: 4-6 hours
   - Impact: LOW
   - Complexity: HIGH

---

## Technical Decisions

### UI Framework Choice: Tkinter

**Why Tkinter?**
- Built into Python (no extra dependencies)
- Lightweight
- Cross-platform
- Sufficient for simple UIs
- Easy to implement

**Alternatives Considered:**
- **PyQt5/PySide6**: More powerful, but large dependency
- **Kivy**: Overkill for simple UI
- **Custom HTML/CSS**: Too complex for this use case

### Architecture

```
ui/
├── __init__.py
├── recording_indicator.py    # Phase 1
├── tray_icon.py              # Phase 2
├── toast_notifier.py         # Phase 4
├── settings_window.py        # Phase 3
└── status_dashboard.py       # Phase 5 (optional)
```

### Integration with Main App

```python
# In main.py

from ui.recording_indicator import RecordingIndicator
from ui.tray_icon import TrayIcon
from ui.toast_notifier import ToastNotifier
from ui.settings_window import SettingsWindow

class CuteWhisper:
    def __init__(self):
        # ... existing init ...

        # UI components
        self.indicator = RecordingIndicator()
        self.tray = TrayIcon(self)
        self.notifier = ToastNotifier()

        # Start tray icon in background
        threading.Thread(target=self.tray.run, daemon=True).start()

    def start_dictation(self):
        self.indicator.show()
        self.tray.update_status("Recording...")
        self.notifier.show_recording_started()
        # ... existing code ...

    def stop_dictation(self):
        self.indicator.hide()
        self.tray.update_status("Ready")
        # ... existing code ...
        self.notifier.show_recording_complete(text[:50])

    def open_settings(self):
        """Open settings window"""
        SettingsWindow(self.config, on_save_callback=self.on_settings_changed).show()

    def on_settings_changed(self):
        """Called when settings are saved"""
        logger.info("Settings changed, reinitializing components")
        # Reinitialize components if needed
```

---

## Success Criteria

### Phase 1 Success
- [ ] Recording indicator appears when Ctrl+Space is pressed
- [ ] Timer shows elapsed time during recording
- [ ] Indicator disappears after transcription
- [ ] No interference with dictation

### Phase 2 Success
- [ ] System tray icon visible in notification area
- [ ] Right-click menu works
- [ ] Can start dictation from menu
- [ ] Can open settings from menu
- [ ] Can quit from menu

### Phase 3 Success
- [ ] Settings window opens
- [ ] All settings are editable
- [ ] Save button persists changes
- [ ] Changes take effect immediately

---

## Next Steps

1. **Start with Recording Indicator** (Phase 1)
   - Implement floating window
   - Add timer
   - Test with dictation

2. **Add System Tray** (Phase 2)
   - Create icon
   - Build menu
   - Test menu actions

3. **Implement Settings** (Phase 3)
   - Design layout
   - Add all controls
   - Test save/load

4. **Add Notifications** (Phase 4)
   - Implement toast/notifications
   - Add to workflow

5. **Polish** (Phase 5)
   - Status dashboard (optional)
   - Better icons
   - Animations

---

## Dependencies

```txt
# Add to requirements.txt
pystray>=0.19.5      # System tray
Pillow>=10.0.0       # Image handling (already there)
win10toast>=0.6      # Toast notifications (optional)
```

---

**Status:** PLANNING - Ready for implementation
**Estimated Total Time:** 8-12 hours for all phases
**Priority:** Implement Phase 1 & 2 first for maximum user value

---

**End of UI Implementation Plan**
