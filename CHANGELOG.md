# Changelog

All notable changes to CuteWhisper will be documented in this file.

## [Unreleased] - January 2025

### Fixed - Executable Build Issues

**Critical fixes for PyInstaller builds:**

1. **Whisper Assets Bundling**
   - Fixed transcription failing with "No such file or directory: whisper/assets/mel_filters.npz"
   - Manually bundled Whisper assets (mel_filters.npz, tiktoken files) in spec file
   - Transcription now works correctly in the standalone executable

2. **Video/Animation Assets**
   - Fixed audio visualizer animation not loading in exe
   - Added assets folder bundling for cute_cat.mp4
   - Recording indicator now displays video animation properly

3. **PyTorch Dependencies**
   - Fixed "ModuleNotFoundError: No module named 'unittest'" crash
   - Removed `unittest` from excludes list (required by PyTorch)
   - Exe now launches without crashes

4. **Build Documentation**
   - Added comprehensive "Important Build Fixes" section to BUILD.md
   - Added specific troubleshooting for exe issues
   - Documented all critical spec file configurations

### Changed

- Updated README.md with "Recent Updates" section documenting exe fixes
- Added "Executable Issues" troubleshooting section to README
- Added quick build commands to README for convenience
- Updated project structure to include CuteWhisper.spec
- Improved BUILD.md with detailed troubleshooting for common build issues

### License

- Changed from MIT to **AGPLv3 (GNU Affero General Public License v3.0)**
- Ensures source code availability for network deployments
- Requires modifications to be released under same license

## Previous Features

### Core Functionality
- Press-and-hold dictation with configurable hotkeys
- Real-time audio visualization with video playback
- Clipboard preservation during text injection
- Multi-microphone support with device selection
- Transcription history with SQLite database
- GUI settings window with live hotkey reloading
- Windows toast notifications
- System tray integration
- GPU acceleration (CUDA) support

### Technical Implementation
- Dynamic hotkey configuration (no restart required)
- Thread-safe UI components
- Automatic fallback from clipboard to typing
- Comprehensive error handling for model downloads
- OpenAI Whisper integration (openai-whisper package)
- PyTorch backend with optional CUDA support

---

## Version History

### Version 1.0.0 (Initial Release)
- First stable release
- All core features implemented
- AGPLv3 licensing

---

**For detailed build instructions, see [BUILD.md](BUILD.md)**
**For usage documentation, see [README.md](README.md)**
