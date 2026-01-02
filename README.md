# CuteWhisper

A privacy-focused, local dictation tool for Windows that transcribes speech to text using OpenAI's Whisper model. No internet connection required, no accounts, no subscriptions.

## Features

- **🎤 Press-and-Hold Dictation**: Hold Ctrl+Space to record, release to transcribe
- **🔒 100% Local**: All processing happens on your machine
- **⚡ Fast**: Base model transcribes in ~2 seconds
- **📋 Clipboard Preservation**: Optionally restores your clipboard after pasting
- **🎯 Accurate**: Uses OpenAI's Whisper model for high-quality transcription
- **💻 Cross-App**: Works in Notepad, VS Code, browsers, Discord, and more
- **🔧 Configurable**: Customize model, hotkey, audio settings, and more

## Quick Start

### Option 1: Standalone Executable (Recommended - No Python Required)

1. **Download** the latest `CuteWhisper-Windows.zip`
2. **Extract** to any folder
3. **Run** `CuteWhisper.exe`
4. **Start dictating**:
   - Press and hold **Ctrl+Space**
   - Speak
   - Release Ctrl+Space
   - Text appears in your active window!

**First run will download the Whisper model (~74MB).**

### Option 2: From Source

#### Prerequisites

- Windows 10/11
- Python 3.8 or higher
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
   - Release Ctrl+Space
   - Text appears in your active window!

### Building Your Own Executable

See [BUILD.md](BUILD.md) for detailed instructions on building a standalone .exe file.

## Configuration

CuteWhisper can be customized by creating a `config/user_config.yaml` file:

```yaml
hotkey:
  toggle: 'ctrl+space'  # Change hotkey if needed

audio:
  sample_rate: 16000
  channels: 1

whisper:
  model_size: 'base'  # Options: tiny, base, small, medium, large
  language: 'auto'    # Auto-detect or specify: en, es, fr, de, etc.
  device: 'cpu'       # Use 'cuda' if you have NVIDIA GPU
  compute_type: 'int8'

ui:
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

### "No module named 'faster_whisper'"
```bash
pip install -r requirements.txt
```

### "Microphone not found"
- Check your microphone is connected
- Set it as the default recording device in Windows Sound Settings
- Restart CuteWhisper

### "Text not appearing"
- Make sure the target application window is focused
- Try clicking in the text field before dictating
- If clipboard doesn't work, CuteWhisper automatically falls back to typing

### "Transcription is slow"
- Try a smaller model (`tiny` or `base`)
- Use GPU if available (`device: 'cuda'` in config)

### Model Download Takes Forever
- First run requires downloading the model (~74MB for base)
- Progress bar shows download status
- Models are cached in `models/` folder after download

## Project Structure

```
CuteWhisper/
├── main.py                    # Application entry point
├── audio/
│   └── recorder.py            # Audio capture (thread-safe)
├── stt/
│   └── whisper_wrapper.py     # Whisper transcription
├── injection/
│   └── text_paster.py         # Text injection with clipboard
├── hotkey/
│   └── hotkey_manager.py      # Global hotkey listener
├── config/
│   ├── settings.py            # Configuration management
│   └── default_config.yaml    # Default settings
├── utils/
│   ├── logger.py              # Logging setup
│   ├── cleanup.py             # Temp file cleanup
│   └── progress.py            # Download progress tracker
├── models/                    # Downloaded Whisper models
├── temp/                      # Temporary audio files
└── logs/                      # Application logs
```

## Performance

On a typical laptop (Intel i5, 8GB RAM):
- **Model load**: 2-3 seconds (one-time at startup)
- **Transcription**: 1-2 seconds for 10 seconds of audio
- **Total latency**: ~3-5 seconds from release to paste

## Advanced Usage

### Using GPU (CUDA)

If you have an NVIDIA GPU with CUDA installed:

```yaml
whisper:
  model_size: 'base'
  device: 'cuda'
  compute_type: 'float16'  # Use float16 for GPU
```

### Custom Hotkey

```yaml
hotkey:
  toggle: 'ctrl+shift+d'  # Use any combination
```

### Language Selection

```yaml
whisper:
  language: 'en'  # Force English (faster, more accurate)
```

## Limitations

- Windows only (tested on Windows 10/11)
- Requires online connection for initial model download only
- One-shot dictation (records while holding, not streaming)
- Clipboard-based paste (95%+ compatibility)

## Credits

- **Whisper**: OpenAI's speech recognition model
- **faster-whisper**: Optimized Whisper implementation
- **pynput**: Cross-platform hotkey library

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or suggestions:
1. Check the logs in `logs/cutewhisper.log`
2. Review the troubleshooting section above
3. Open an issue on GitHub

---

**Enjoy dictating! 🎤→📝**
