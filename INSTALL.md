# CuteWhisper Installation Guide

Complete guide for installing and running CuteWhisper on Windows.

## Table of Contents

1. [Quick Installation (Executable)](#quick-installation-executable)
2. [Installation from Source](#installation-from-source)
3. [First Run Setup](#first-run-setup)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)

---

## Quick Installation (Executable)

**This is the easiest way to install CuteWhisper - no Python required!**

### Step 1: Download

Download the latest `CuteWhisper-Windows.zip` from:

- [GitHub Releases](https://github.com/yourusername/CuteWhisper/releases)
- Or the provided download link

### Step 2: Extract

1. Right-click `CuteWhisper-Windows.zip`
2. Select "Extract All..."
3. Choose a destination folder (e.g., `C:\Program Files\CuteWhisper`)
4. Click "Extract"

### Step 3: Run

1. Open the extracted folder
2. Double-click `CuteWhisper.exe`
3. Click "Run" if Windows SmartScreen appears (see note below)

### Step 4: First Run

- The application will start
- On first run, it downloads the Whisper model (~74MB)
- Wait for "Model loaded and ready!" message
- You're ready to dictate!

**Note:** Windows may show a SmartScreen warning for unsigned executables. Click "More info" → "Run anyway".

---

## Installation from Source

**For developers or advanced users who want to modify CuteWhisper.**

### Requirements

- **Windows 10/11** (64-bit)
- **Python 3.8 or higher**
  - Download from [python.org](https://www.python.org/downloads/)
  - During install, check "Add Python to PATH"
- **Microphone**

### Step 1: Verify Python Installation

Open Command Prompt and check:

```cmd
python --version
```

Should show: `Python 3.8.x` or higher.

### Step 2: Download CuteWhisper

Option A - Using Git:
```cmd
git clone https://github.com/yourusername/CuteWhisper.git
cd CuteWhisper
```

Option B - Download ZIP:
1. Download from GitHub
2. Extract to folder
3. Open Command Prompt in that folder

### Step 3: Create Virtual Environment

Highly recommended to avoid conflicts with other Python packages.

```cmd
python -m venv venv
```

### Step 4: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

Your command prompt should now show `(venv)` at the start.

### Step 5: Install Dependencies

```cmd
pip install -r requirements.txt
```

This may take 5-10 minutes. PyTorch is large.

**If installation fails**, try:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Run CuteWhisper

```cmd
python main.py
```

Or create a shortcut:
1. Right-click desktop → New → Shortcut
2. Location: `cmd /c "cd /d C:\path\to\CuteWhisper && venv\Scripts\activate && python main.py"`
3. Name: CuteWhisper

---

## First Run Setup

### What to Expect

1. **Console window appears** with startup messages
2. **Model download** (first run only):
   ```
   Loading Whisper model 'base'...
   If this is your first time, the model will be downloaded
   [====================] 100% 74MB
   Model loaded successfully!
   ```
3. **System tray icon** appears in notification area
4. **Ready message**:
   ```
   Ready! Close the window or right-click tray icon to quit.
   ```

### Testing Your Installation

1. Open **Notepad** (or any text editor)
2. Press and hold **Ctrl+Space**
3. Speak clearly: "Hello, this is a test"
4. Release **Ctrl+Space**
5. Wait 1-2 seconds
6. Text should appear!

**If it works**, installation is successful! ✅

**If not**, see [Troubleshooting](#troubleshooting).

---

## Configuration

CuteWhisper works great out of the box, but you can customize it.

### Accessing Settings

1. Right-click the **CuteWhisper tray icon**
2. Select **Settings**
3. Configure as needed

### Settings Options

#### General Tab
- **Hotkey**: Change Ctrl+Space to any key combination
- **Clipboard**: Enable/disable clipboard preservation

#### Audio Tab
- **Microphone**: Select specific input device
- **Sample Rate**: 16000 Hz (default) works best

#### Whisper Tab
- **Model Size**: tiny, base, small, medium, large
- **Language**: Auto-detect or specific language
- **GPU Acceleration**: Enable if you have NVIDIA GPU

### Creating Config File Manually

Create `config/user_config.yaml`:

```yaml
hotkey:
  toggle: 'ctrl+space'

audio:
  device: 'Default'
  sample_rate: 16000
  channels: 1

whisper:
  model_size: 'base'
  language: 'auto'
  device: 'cpu'
  compute_type: 'int8'

ui:
  preserve_clipboard: true
```

---

## Troubleshooting

### "Python not recognized"

**Problem**: Python not installed or not in PATH

**Solution**:
1. Install Python from python.org
2. Check "Add Python to PATH" during install
3. Restart Command Prompt

### "No module named 'torch'"

**Problem**: Dependencies not installed

**Solution**:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### "Microphone not found"

**Problem**: No microphone or wrong device selected

**Solution**:
1. Check microphone is plugged in
2. Set as default in Windows Sound Settings
3. In CuteWhisper Settings → Audio → Select correct device
4. Restart CuteWhisper

### "Text not appearing"

**Problem**: Application window not focused

**Solution**:
1. Click in the text field before dictating
2. Make sure target application is active
3. Try different applications (Notepad, Word, etc.)

### "Transcription is slow"

**Problem**: Large model or no GPU

**Solutions**:
- Use smaller model (`tiny` or `base`)
- Enable GPU if available (Settings → Whisper → Use GPU)
- Close other applications to free up RAM

### "Windows Defender SmartScreen"

**Problem**: Unsigned executable warning

**Solution**:
1. Click "More info"
2. Click "Run anyway"
3. Or disable SmartScreen (not recommended)

### Build Issues

See [BUILD.md](BUILD.md) for build-specific troubleshooting.

---

## Uninstallation

### Executable Version

1. Close CuteWhisper (right-click tray icon → Quit)
2. Delete the CuteWhisper folder
3. Optionally delete `AppData\Roaming\CuteWhisper` for settings

### Source Version

1. Deactivate virtual environment:
   ```cmd
   deactivate
   ```
2. Delete the CuteWhisper folder
3. Optionally delete `AppData\Roaming\CuteWhisper`

---

## System Requirements

### Minimum

- Windows 10 (64-bit)
- 4GB RAM
- 500MB free disk space
- Microphone
- Internet connection (first run only)

### Recommended

- Windows 11 (64-bit)
- 8GB RAM
- 2GB free disk space
- NVIDIA GPU (for GPU acceleration)
- High-quality microphone

---

## Next Steps

- **Read the User Guide**: [README.md](README.md)
- **Build Your Own**: [BUILD.md](BUILD.md)
- **Report Issues**: [GitHub Issues](https://github.com/yourusername/CuteWhisper/issues)

---

## Support

Need help?

1. Check logs in `logs/cutewhisper.log`
2. Review [Troubleshooting](#troubleshooting)
3. Open an issue on GitHub

---

**Enjoy dictating with CuteWhisper! 🎤→📝**
