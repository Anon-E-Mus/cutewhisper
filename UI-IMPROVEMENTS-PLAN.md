# CuteWhisper UI Improvements - Implementation Plan

## Overview

This plan details the implementation of major UI improvements including:
1. **Audio Visualizer Recording UI** - Rounded rectangle with real-time sound wave visualization
2. **Transcription History** - Store and view all transcriptions
3. **Fix Settings Window** - Ensure it opens from tray icon
4. **Remove Toast Notifications** - No longer show for each completion

---

## Problem Analysis

### Current Issues:
1. ❌ Settings window doesn't open from tray icon (threading issue)
2. ❌ Recording UI is basic (just text timer)
3. ❌ No history feature - transcriptions are lost
4. ❌ Toast notifications are intrusive

### Root Causes:
- Settings window called from non-main thread (tray icon callback)
- No audio level visualization
- No history persistence
- Toast notifications shown on every completion

---

## Phase 1: Audio Visualizer Recording UI

### Design Specifications:
```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║  [||||||||   |||||||   |||]  ║  │ <- Sound wave bars
│  ║     Recording 00:05           ║  │ <- Timer text
│  ╚═══════════════════════════════╝  │
└─────────────────────────────────────┘
```

### Features:
- **Rounded corners** (border-radius effect)
- **Semi-transparent** dark background
- **Animated sound wave bars** (10-15 vertical bars)
- **Bars animate based on real-time audio levels**
- **Timer display** below the wave
- **Always on top** in top-right corner

### Technical Implementation:

#### File: `ui/audio_visualizer.py`

**Key Components:**

1. **Canvas-based Drawing:**
```python
# Create canvas with rounded rectangle
canvas = tk.Canvas(window, width=300, height=100, bg='#2C2C2C', highlightthickness=0)
canvas.pack()

# Draw rounded rectangle
canvas.create_rounded_rectangle(10, 10, 290, 90, radius=15, fill='#3C3C3C', outline='#4A90E2')
```

2. **Sound Wave Bars:**
```python
class AudioBar:
    def __init__(self, x, width, canvas):
        self.x = x
        self.width = width
        self.canvas = canvas
        self.height = 10  # Initial height
        self.rect_id = canvas.create_rectangle(
            x, 50, x + width, 60,
            fill='#4A90E2', outline=''
        )

    def update(self, audio_level):
        """Update bar height based on audio level (0.0 to 1.0)"""
        max_height = 60
        new_height = 10 + (audio_level * max_height)
        self.canvas.coords(
            self.rect_id,
            self.x, 50 - new_height//2,
            self.x + self.width, 50 + new_height//2
        )
```

3. **Audio Level Detection:**
```python
def get_audio_level(audio_data):
    """Calculate audio level from PCM data"""
    # RMS (Root Mean Square) for loudness
    rms = np.sqrt(np.mean(audio_data**2))
    # Normalize to 0.0 - 1.0
    return min(rms * 10, 1.0)  # Adjust sensitivity
```

4. **Integration with AudioRecorder:**
```python
# In audio/recorder.py, add callback parameter
def start_recording(self, on_audio_callback=None):
    """Start recording with optional audio level callback"""
    self.on_audio_callback = on_audio_callback

    def audio_callback(indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")

        # Store audio data
        audio_queue.put(indata.copy())

        # Notify visualizer if callback provided
        if self.on_audio_callback:
            self.on_audio_callback(indata.copy())
```

### Implementation Steps:

1. **Create `ui/audio_visualizer.py`** with:
   - `AudioVisualizerWindow` class
   - Canvas for drawing
   - Animated bar system
   - Audio level calculation
   - Thread-safe updates using `after()`

2. **Modify `audio/recorder.py`** to:
   - Add `on_audio_callback` parameter
   - Call callback with audio chunks
   - Maintain thread safety

3. **Update `main.py`** to:
   - Use `AudioVisualizerWindow` instead of `RecordingIndicator`
   - Pass audio callback to recorder
   - Handle thread-safe UI updates

---

## Phase 2: Transcription History

### Design Specifications:

#### History Window:
```
┌────────────────────────────────────────────┐
│  Transcription History          [_] [□] [X] │
├────────────────────────────────────────────┤
│  [Search...................]         [Clear]│
├────────────────────────────────────────────┤
│  Date/Time              Text               │
│  ──────────────────────────────────────    │
│  2025-01-02 14:32   Hello world...         │
│  2025-01-02 14:35   This is a test...      │
│  2025-01-02 14:40   Another one...         │
│                                             │
│            [Export] [Delete] [Copy]        │
└────────────────────────────────────────────┘
```

### Features:
- **Save all transcriptions** to SQLite database
- **Search** by text content
- **Filter** by date range
- **Copy** individual entries to clipboard
- **Export** all to text file
- **Delete** entries
- **Accessible** from tray menu

### Technical Implementation:

#### File: `utils/history_manager.py`

```python
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class HistoryManager:
    """Manage transcription history"""

    def __init__(self, db_path='data/transcriptions.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                text TEXT NOT NULL,
                language TEXT,
                duration REAL,
                audio_file TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_transcription(self, text, language='en', duration=None, audio_file=None):
        """Add a transcription to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transcriptions (timestamp, text, language, duration, audio_file)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), text, language, duration, audio_file))
        conn.commit()
        conn.close()

    def get_all(self, limit=None, search=None):
        """Retrieve all transcriptions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if search:
            cursor.execute('''
                SELECT * FROM transcriptions
                WHERE text LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{search}%', limit))
        else:
            cursor.execute('''
                SELECT * FROM transcriptions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        results = cursor.fetchall()
        conn.close()
        return results

    def delete(self, id):
        """Delete a transcription"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transcriptions WHERE id = ?', (id,))
        conn.commit()
        conn.close()

    def clear_all(self):
        """Clear all history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transcriptions')
        conn.commit()
        conn.close()

    def export_to_file(self, output_path):
        """Export history to text file"""
        results = self.get_all()
        with open(output_path, 'w', encoding='utf-8') as f:
            for row in results:
                id, timestamp, text, language, duration, audio_file = row
                f.write(f"[{timestamp}] ({language})\n{text}\n\n")
```

#### File: `ui/history_window.py`

```python
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading

class HistoryWindow:
    """Transcription history viewer"""

    def __init__(self, history_manager, parent=None):
        self.history_manager = history_manager
        self.parent = parent
        self.window = None

    def show(self):
        """Show history window"""
        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()

        self.window.title("Transcription History")
        self.window.geometry("800x600")

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        """Create all widgets"""
        # Search bar
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)

        ttk.Button(search_frame, text="Clear History", command=self.clear_history).pack(side='right')

        # Treeview for list
        columns = ('timestamp', 'text', 'language')
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings', height=20)

        self.tree.heading('timestamp', text='Date/Time')
        self.tree.heading('text', text='Transcription')
        self.tree.heading('language', text='Lang')

        self.tree.column('timestamp', width=150)
        self.tree.column('text', width=500)
        self.tree.column('language', width=80)

        scrollbar = ttk.Scrollbar(self.window, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Copy Selected", command=self.copy_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export All", command=self.export_all).pack(side='left', padx=5)

    def load_history(self, search=None):
        """Load history into treeview"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load from database
        results = self.history_manager.get_all(limit=100, search=search)

        for row in results:
            id, timestamp, text, language, duration, audio_file = row
            # Format timestamp
            dt = timestamp.split('T')
            date = dt[0]
            time_str = dt[1].split('.')[0] if len(dt) > 1 else ''

            # Truncate text for display
            display_text = text[:100] + '...' if len(text) > 100 else text

            self.tree.insert('', 'end', values=(f'{date} {time_str}', display_text, language), tags=(str(id),))

    def on_search(self, event):
        """Handle search"""
        search_text = self.search_var.get()
        self.load_history(search=search_text if search_text else None)

    def copy_selected(self):
        """Copy selected text to clipboard"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        id = tags[0]

        # Get full text from database
        results = self.history_manager.get_all()
        for row in results:
            if str(row[0]) == id:
                text = row[2]
                self.window.clipboard_clear()
                self.window.clipboard_append(text)
                messagebox.showinfo("Copied", "Text copied to clipboard")
                break

    def delete_selected(self):
        """Delete selected entry"""
        selection = self.tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirm Delete", "Delete selected entry?"):
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            id = tags[0]

            self.history_manager.delete(id)
            self.load_history()

    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm Clear", "Clear all transcription history?"):
            self.history_manager.clear_all()
            self.load_history()

    def export_all(self):
        """Export all history to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            self.history_manager.export_to_file(file_path)
            messagebox.showinfo("Export", f"History exported to {file_path}")
```

---

## Phase 3: Fix Settings Window

### Problem:
Settings window doesn't open from tray icon because tray callback runs in non-main thread.

### Solution:

#### File: `ui/tray_icon.py` (Modify)

```python
def on_settings(self):
    """Menu action: Open settings"""
    logger.info("Tray: Settings requested")

    # Use root.after() to schedule in main thread
    if hasattr(self.app, 'root_window') and self.app.root_window:
        # Schedule GUI update in main thread
        def open_in_main():
            self.app.open_settings()
        self.app.root_window.after(0, open_in_main)
    else:
        # Fallback
        self.app.open_settings()
```

#### File: `main.py` (Verify)

```python
def open_settings(self):
    """Open settings window (must be called from main thread)"""
    # This should already be called from main thread via root.after()
    if not hasattr(self, 'settings_window') or not self.settings_window:
        self.settings_window = SettingsWindow(
            self.config,
            parent=self.root_window,
            on_save_callback=self.on_settings_changed
        )

    self.settings_window.show()
```

---

## Phase 4: Remove Toast Notifications

### Current Behavior:
- Toast shown on "Recording started"
- Toast shown on "Text inserted"

### Desired Behavior:
- Only show toast on **errors**
- No toast for normal completion
- User can check history instead

### Implementation:

#### File: `main.py` (Modify)

```python
def stop_dictation(self):
    """Stop recording and transcribe"""
    # ... existing code ...

    # REMOVE this line:
    # self.notifier.show_recording_complete(text)

    # Keep only error notifications
    if error:
        self.notifier.show_error(error_message)
```

#### File: `main.py` (Start dictation)

```python
def start_dictation(self):
    """Start recording audio"""
    # ... existing code ...

    # OPTIONAL: Remove this too if you want no recording notification
    # self.notifier.show_recording_started()

    # Or keep only recording started, remove completion
```

---

## Implementation Order

### Step 1: Fix Critical Bug (Settings Window)
1. Modify `ui/tray_icon.py` `on_settings()` method
2. Test settings opens from tray
3. **Estimated time: 5 minutes**

### Step 2: Audio Visualizer UI
1. Create `ui/audio_visualizer.py`
2. Modify `audio/recorder.py` to add audio callback
3. Update `main.py` to use visualizer
4. Test recording with visualization
5. **Estimated time: 30 minutes**

### Step 3: Transcription History
1. Create `utils/history_manager.py`
2. Create `ui/history_window.py`
3. Update `main.py` to save to history
4. Add "History" to tray menu
5. Test history saving/viewing
6. **Estimated time: 40 minutes**

### Step 4: Remove Toast Notifications
1. Remove `show_recording_complete()` calls
2. Optionally remove `show_recording_started()`
3. Test that only errors show notifications
4. **Estimated time: 5 minutes**

---

## Testing Checklist

### Settings Window:
- [ ] Opens from tray icon right-click
- [ ] Settings save correctly
- [ ] Window closes and reopens
- [ ] Changes apply after save

### Audio Visualizer:
- [ ] Visualizer appears on Ctrl+Space
- [ ] Bars animate based on audio input
- [ ] Rounded corners visible
- [ ] Timer displays correctly
- [ ] Disappears on release
- [ ] No crashes or threading errors

### Transcription History:
- [ ] All transcriptions saved to database
- [ ] History window opens from tray
- [ ] Search works
- [ ] Copy to clipboard works
- [ ] Delete entry works
- [ ] Clear all works
- [ ] Export to file works
- [ ] Database file created in `data/` folder

### Notifications:
- [ ] No toast on successful transcription
- [ ] No toast on recording start (optional)
- [ ] Toast still shows on errors

---

## Success Criteria

### Phase 1 (Settings Fix):
- Settings window opens reliably from tray icon
- No threading errors

### Phase 2 (Visualizer):
- Recording UI is visually appealing with animated wave
- Bars respond to voice in real-time
- Smooth animation without lag

### Phase 3 (History):
- All transcriptions are preserved
- Easy to search and view history
- Export/copy functionality works

### Phase 4 (Notifications):
- Only error notifications appear
- User experience is less intrusive

---

## End of Plan

**Next Step:** Execute implementation starting with Phase 1 (Settings Fix) and proceed through all phases.
