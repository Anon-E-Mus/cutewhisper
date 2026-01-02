# CuteWhisper

A privacy-focused, local dictation tool for Windows that transcribes speech to text using OpenAI's Whisper model. No internet connection required, no accounts, no subscriptions.

## Features

- **🎤 Press-and-Hold Dictation**: Hold your hotkey to record, release to transcribe
- **🔄 Dynamic Model Switching**: Change Whisper models in Settings without restarting (tiny → large in real-time!)
- **🔒 100% Local**: All processing happens on your machine
- **⚡ Fast**: Base model transcribes in ~2 seconds
- **🎨 Beautiful Visual Interface**: Real-time audio visualization with video playback
- **⚙️ GUI Settings**: Easy-to-use settings window with all options
- **📋 Clipboard Preservation**: Optionally restores your clipboard after pasting
- **🎯 Accurate**: Uses OpenAI's Whisper model for high-quality transcription
- **💻 Cross-App**: Works in Notepad, VS Code, browsers, Discord, and more
- **🔧 Highly Configurable**: Customize hotkey, model, audio device, and more
- **🚀 GPU Acceleration**: Optional CUDA support for 5-10x faster transcription
- **📜 History Tracking**: Built-in transcription history with search and export

## Recent Updates

### Dynamic Model Reloading & UI Improvements (January 2025)
- ✅ **Dynamic model switching** - Change Whisper models in Settings without restarting!
  - See file sizes before selecting: tiny (39 MB), base (74 MB), small (244 MB), medium (769 MB), large (1.5 GB)
  - Automatic reload with progress messages
  - Memory freed when switching to smaller models
- ✅ **Fixed toast notification crashes** - Graceful fallback to console messages if win10toast fails in bundled exe
- ✅ **Model sizes in dropdown** - Users can see download size before selecting model
- ✅ **Enhanced reload messages** - Shows before/after model sizes and loading progress

### Fixed Executable Build Issues (January 2025)
- ✅ **Fixed Whisper transcription in exe** - Whisper assets (mel_filters.npz, tiktoken files) now properly bundled
- ✅ **Fixed video/animation in exe** - Audio visualizer video now loads correctly
- ✅ **Fixed PyTorch dependency** - Removed `unittest` from excludes (required by PyTorch)
- ✅ **Updated build documentation** - Added comprehensive troubleshooting and build instructions
- ✅ **Added AGPLv3 license** - Updated to AGPLv3 for network deployment compliance

**See [CHANGELOG.md](CHANGELOG.md) for detailed version history and all recent fixes.**

## Quick Start

### Option 1: Standalone Executable (Recommended - No Python Required)

1. **Download** the latest `CuteWhisper-Windows.zip`
2. **Extract** to any folder
3. **Run** `CuteWhisper.exe`
4. **Start dictating**:
   - Press and hold **Ctrl+Space** (default hotkey)
   - Speak
   - Release to transcribe
   - Text appears in your active window!

**First run will download the Whisper model (~74MB).**

### Option 2: From Source

#### Prerequisites

- Windows 10/11
- Python 3.8 or higher (3.10 recommended for best compatibility)
- Microphone

#### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run CuteWhisper**:
   ```bash
   python main.py
   ```

5. **Start dictating**:
   - Press and hold **Ctrl+Space**
   - Speak
   - Release to transcribe
   - Text appears in your active window!

### Building Your Own Executable

**Quick Build Commands:**

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build the executable
pyinstaller CuteWhisper.spec --clean

# 3. Copy required files to dist folder
# Copy config files
xcopy config dist\config /E /I /Y

# Copy assets folder (for video animation)
xcopy assets dist\assets /E /I /Y

# 4. Run the executable
cd dist
CuteWhisper.exe
```

**For detailed build instructions, troubleshooting, and advanced options, see [BUILD.md](BUILD.md).**

## Configuration

CuteWhisper includes a built-in settings window (right-click tray icon → Settings). You can also customize by editing `config/user_config.yaml`:

```yaml
hotkey:
  toggle: 'ctrl+space'  # Change hotkey (supports: ctrl+alt+r, shift+space, etc.)

audio:
  sample_rate: 16000
  channels: 1
  device: null  # Leave null for default, or specify microphone name

whisper:
  model_size: 'base'  # Options: tiny, base, small, medium, large
  language: 'auto'    # Auto-detect or specify: en, es, fr, de, etc.
  device: 'cpu'       # Use 'cuda' if you have NVIDIA GPU
  compute_type: 'int8'

ui:
  use_clipboard: true
  preserve_clipboard: true  # Restore clipboard after paste
```

## Model Sizes

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| tiny | 39 MB | ⚡⚡⚡ | Good | Quick notes, testing |
| base | 74 MB | ⚡⚡ | Very Good | **Recommended for most users** |
| small | 244 MB | ⚡ | Excellent | Better accuracy |
| medium | 769 MB | ⚡ | Excellent | Multiple languages |
| large | 1.5 GB | 🐌 | Best | Highest accuracy |

## GPU Acceleration (CUDA)

CuteWhisper supports NVIDIA GPU acceleration for 5-10x faster transcription!

### Option 1: Auto-Install (In-App)

1. Open Settings (right-click tray icon → Settings)
2. Go to the **Whisper** tab
3. Click **"Install PyTorch with CUDA"** button
4. Wait for installation (~2GB download)
5. Restart CuteWhisper
6. Enable **"Use GPU acceleration"** checkbox

### Option 2: Manual Installation

If the in-app installer doesn't work, install PyTorch with CUDA manually:

1. **Check your CUDA version**:
   ```bash
   nvidia-smi
   ```

2. **Visit the official PyTorch website** for installation instructions:
   🔗 **[PyTorch - Get Started](https://pytorch.org/get-started/locally/)**

3. **Select your configuration** and run the provided pip command

4. **Restart CuteWhisper** and enable GPU in settings

**Supported CUDA versions**: 11.8, 12.1, 12.4

## Usage Examples

### In Notepad
```
1. Open Notepad
2. Press and hold Ctrl+Space
3. Speak: "Hello world, this is a test of CuteWhisper"
4. Release Ctrl+Space
5. Text appears automatically!
```

### In VS Code
```
1. Open a code file
2. Place cursor where you want to add a comment
3. Hold Ctrl+Space, speak, release
4. Comment is added automatically
```

### In Discord/Slack
```
1. Click in message input box
2. Hold Ctrl+Space, speak your message, release
3. Text is pasted, press Enter to send
```

## Troubleshooting

### "No module named 'whisper'"
```bash
pip install openai-whisper
```

### "CUDA not available" errors
- Verify PyTorch with CUDA is installed: `python -c "import torch; print(torch.cuda.is_available())"`
- If False, reinstall PyTorch with CUDA support (see GPU section above)
- Make sure you have compatible NVIDIA drivers installed

### "Microphone not found"
- Check your microphone is connected
- Open Settings → Audio tab to select correct microphone
- Set it as the default recording device in Windows Sound Settings
- Restart CuteWhisper

### "Text not appearing"
- Make sure the target application window is focused
- Try clicking in the text field before dictating
- If clipboard doesn't work, CuteWhisper automatically falls back to typing

### "Transcription is slow"
- Enable GPU acceleration (see GPU section above)
- Try a smaller model (`tiny` or `base`)
- Force language selection for faster processing

### Model Download Takes Forever
- First run requires downloading the model (~74MB for base)
- Progress bar shows download status
- Models are cached after download

### Hotkey Not Working
- Open Settings to verify your hotkey configuration
- Hotkey changes take effect immediately (no restart needed)
- Make sure your hotkey doesn't conflict with other applications

### Executable Issues

**Exe crashes with "ModuleNotFoundError: No module named 'unittest'"**
- This is a PyTorch dependency issue. Rebuild the exe with the updated spec file
- See BUILD.md for the fix

**Exe runs but transcription fails**
- Make sure you're using the latest build with Whisper assets bundled
- Check that `whisper/assets` folder exists in the same directory as the exe
- Rebuild using the updated spec file (see BUILD.md)

**Animation not showing in exe**
- Copy the `assets/` folder to the `dist/` folder after building
- Make sure `cute_cat.mp4` exists in `dist/assets/`
- See BUILD.md for detailed instructions

## Project Structure

```
CuteWhisper/
├── main.py                      # Application entry point
├── CuteWhisper.spec             # PyInstaller specification (includes critical fixes)
├── audio/
│   └── recorder.py              # Audio capture with device selection
├── stt/
│   └── whisper_wrapper.py       # OpenAI Whisper transcription
├── injection/
│   └── text_paster.py           # Text injection with clipboard preservation
├── hotkey/
│   └── hotkey_manager.py        # Dynamic hotkey listener
├── config/
│   ├── settings.py              # Configuration management
│   └── default_config.yaml      # Default settings
├── ui/
│   ├── audio_visualizer.py      # Real-time audio visualization
│   ├── recording_indicator.py   # Recording status window
│   ├── settings_window.py       # GUI settings window
│   ├── history_window.py        # Transcription history viewer
│   ├── toast_notifier.py        # Windows toast notifications
│   └── tray_icon.py             # System tray integration
├── utils/
│   ├── logger.py                # Logging setup
│   ├── cleanup.py               # Temp file cleanup
│   └── history_manager.py       # Transcription history database
├── assets/
│   └── cute_cat.mp4             # Visualizer video playback
├── data/
│   └── transcriptions.db        # SQLite database for history
├── models/                      # Downloaded Whisper models
├── temp/                        # Temporary audio files
└── logs/                        # Application logs
```

## Performance

### CPU (Intel i5, 8GB RAM)
- **Model load**: 2-3 seconds (one-time at startup)
- **Transcription**: 1-2 seconds for 10 seconds of audio
- **Total latency**: ~3-5 seconds from release to paste

### GPU (NVIDIA RTX 3060, CUDA 11.8)
- **Model load**: 1-2 seconds
- **Transcription**: 0.2-0.5 seconds for 10 seconds of audio
- **Total latency**: ~1-2 seconds from release to paste
- **Speedup**: 5-10x faster than CPU

## Advanced Usage

### Dynamic Hotkey Configuration

Hotkeys can be changed on-the-fly through the Settings window:

**Supported formats:**
- `ctrl+space` - Default
- `alt+shift+r` - Custom combination
- `ctrl+alt+d` - Multiple modifiers
- `win+a` - Windows key

**Special keys supported:**
- Letters: a-z
- Numbers: 0-9
- Special: space, tab, enter, escape
- Arrows: up, down, left, right
- Function keys: f1-f12

Changes apply immediately without restart!

### Audio Device Selection

If you have multiple microphones:
1. Open Settings → Audio tab
2. Select your microphone from the dropdown
3. Save settings
4. **Restart required** for device changes to take effect

### Language Selection

Force a specific language for faster, more accurate transcription:

```yaml
whisper:
  language: 'en'  # Force English (faster, more accurate)
```

Supported languages: auto, en, es, fr, de, it, pt, zh, ja, ko, and more.

### Transcription History

Access your dictation history:
1. Right-click tray icon
2. Select **"History"**
3. View, search, copy, or export past transcriptions

History is stored in `data/transcriptions.db` (SQLite database)

## Requirements

### Core Dependencies
- **openai-whisper** >= 20231117 - OpenAI's speech recognition model
- **sounddevice** >= 0.4.6 - Audio capture
- **torch** >= 2.0.0 - PyTorch (CPU version by default)
- **pywin32** >= 306 - Windows API bindings
- **pynput** >= 1.7.6 - Global hotkey listener
- **pyautogui** >= 0.9.54 - Text injection fallback
- **pystray** >= 0.19.5 - System tray icon
- **Pillow** >= 10.0.0 - Image processing
- **opencv-python** >= 4.8.0 - Video playback for visualizer
- **PyYAML** >= 6.0 - Configuration management

### Optional Dependencies
- **PyTorch with CUDA** - GPU acceleration (see GPU section above)

## Limitations

- **Windows only** (tested on Windows 10/11)
- **Python compatibility**: Works with Python 3.8-3.13
  - **Note**: PyTorch CUDA is NOT available for Python 3.13+
  - Use Python 3.10-3.12 for GPU support
- Requires online connection for initial model download only
- One-shot dictation (records while holding, not streaming)
- Clipboard-based paste (95%+ compatibility across applications)

## Credits

- **Whisper**: OpenAI's speech recognition model
- **openai-whisper**: Official Whisper implementation by OpenAI
- **PyTorch**: Deep learning framework
- **pynput**: Cross-platform hotkey library
- **pystray**: System tray icon library

## License

**AGPLv3 (GNU Affero General Public License v3.0)**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/agpl-3.0.html>.

**Key Requirements:**
- ✅ Source code must be made available to users when running over a network
- ✅ Modifications must be released under the same license (AGPLv3)
- ✅ Must provide attribution to original authors
- ❌ Cannot sub-license the software under different terms

See [LICENSE](LICENSE) file for full text.

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or suggestions:
1. Check the logs in `logs/cutewhisper.log`
2. Review the troubleshooting section above
3. Open an issue on GitHub

---

**Enjoy dictating! 🎤→📝**
