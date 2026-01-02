# Project Plan — Windows Local Dictation Tool (Superwhisper-like)

## Goal

Build a **Windows desktop dictation tool** that allows:
- Global hotkey activation
- Local, offline speech-to-text
- Automatic insertion of text into the currently focused text field
- No cloud, no accounts, no subscriptions

---

## Core Principles

- Local-first (privacy)
- One-shot dictation (not streaming initially)
- Stateless (no history required)
- OS-level text injection
- Minimal UI
- Fast iteration

---

## System Architecture (High Level)

[ Global Hotkey ]
↓
[ Audio Capture ]
↓
[ Speech-to-Text (Whisper) ]
↓
[ Optional Cleanup (Local LLM) ]
↓
[ Text Injection (Clipboard + Paste) ]

yaml
Copy code

---

## Tech Stack

### Language
- Python (fast iteration)
- Optional later rewrite in Rust / C++

### Speech-to-Text
- whisper.cpp (CLI-based, CPU friendly)
- OR faster-whisper (Python, GPU-accelerated)

### Hotkeys & Input
- AutoHotkey v2 (recommended)
- OR Python `keyboard` library

### Audio Capture
- PyAudio or `sounddevice`
- Record WAV to temp file

### Text Injection
- Clipboard + simulated Ctrl+V (most reliable on Windows)

---

## Phased Build Plan

---

### Phase 1 — MVP (Core Dictation)
**Time:** 1–2 days

**Features**
- Global hotkey (start/stop recording)
- Microphone audio capture
- Local Whisper transcription
- Paste text into focused field

**Tasks**
1. Set up whisper.cpp binary
2. Record mic audio → WAV
3. Run Whisper transcription
4. Capture transcription output
5. Copy text to clipboard
6. Simulate paste

**Success Criteria**
- Dictates into browser, Notepad, VS Code
- End-to-end latency < 5 seconds

---

### Phase 2 — UX & Stability
**Time:** ~1 day

**Features**
- System tray icon
- Visual recording indicator
- Error handling
- Configurable settings

**Tasks**
- Tray application
- Hotkey configuration
- Microphone selection
- Whisper model selection

---

### Phase 3 — Performance & Accuracy
**Time:** ~1 day

**Features**
- GPU support (optional)
- Faster transcription
- Reduced startup latency

**Tasks**
- Integrate faster-whisper (optional)
- Cache model in memory
- Optimize audio handling

---

### Phase 4 — “Super” Enhancements (Optional)
**Time:** 1–2 days

**Features**
- Local LLM cleanup / formatting
- Language auto-detect
- Command phrases (“new paragraph”, “bullet point”)

**Tasks**
- Integrate Ollama or LM Studio
- Prompt templates
- Toggle cleanup on/off

---

### Phase 5 — Packaging & Polish
**Time:** 0.5–1 day

**Features**
- Single executable
- Auto-start on boot
- Simple settings UI

**Tasks**
- PyInstaller packaging
- Config persistence
- README documentation

---

## Project Structure

superdictate/
├── main.py
├── audio/
│ └── recorder.py
├── stt/
│ └── whisper_runner.py
├── inject/
│ └── paste.py
├── hotkey/
│ └── hotkey.ahk
├── config.yaml
└── assets/

yaml
Copy code

---

## Key Design Decisions

### Clipboard vs Keystroke Typing
- Clipboard paste is faster and more reliable
- Works in ~95% of applications

### One-Shot Dictation First
- Much simpler than streaming
- Matches common Superwhisper usage
- Streaming can be added later

### AutoHotkey Choice
- Windows-native
- Stable global hotkeys
- Reliable input injection

---

## Risks & Mitigations

| Risk | Mitigation |
|----|-----------|
| Mic permission issues | Use WASAPI default |
| Paste blocked in app | Manual paste fallback |
| High CPU usage | Smaller Whisper model |
| Antivirus false positives | Code signing later |

---

## Definition of Done (MVP)

- Hotkey → speak → release → text appears
- Fully local/offline
- Stable across apps
- <5 second latency

---

## Next Steps (Choose One)

1. Select STT engine (whisper.cpp vs faster-whisper)
2. AutoHotkey script (ready to paste)
3. Python MVP code skeleton
4. Windows audio capture implementation
5. Packaging into a single EXE