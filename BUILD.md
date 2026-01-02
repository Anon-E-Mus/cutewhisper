# Building CuteWhisper Executable

This guide explains how to build a standalone Windows executable for CuteWhisper.

## Quick Build (Recommended)

### Prerequisites

1. **Python 3.8 or higher** installed
2. **Git** (optional, for cloning repository)

### Step-by-Step Build

1. **Open Command Prompt** in the CuteWhisper directory

2. **Create virtual environment** (if not already done):
   ```cmd
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

5. **Run the build script**:
   ```cmd
   build.bat
   ```

That's it! The executable will be created in `dist\CuteWhisper.exe` with all necessary files included.

**Note**: The build script automatically copies:
- Configuration files (`config/`)
- Assets folder (`assets/cute_cat.mp4`) for the audio visualizer
- Creates required directories (`models/`, `temp/`, `data/`, `logs/`)

## Manual Build (Advanced)

If you prefer manual control over the build process:

### 1. Install PyInstaller

```cmd
pip install pyinstaller
```

### 2. Build the executable

```cmd
pyinstaller CuteWhisper.spec --clean
```

### 3. Copy configuration files and assets

```cmd
REM Copy config files
mkdir dist\config
copy config\default_config.yaml dist\config\

REM CRITICAL: Copy assets folder (for video animation)
mkdir dist\assets
copy assets\cute_cat.mp4 dist\assets\

REM Create required directories
mkdir dist\models
mkdir dist\temp
mkdir dist\data
mkdir dist\logs
```

### 4. Test the executable

```cmd
cd dist
CuteWhisper.exe
```

## Build Output

After building, you'll have:

```
dist/
├── CuteWhisper.exe          # Main executable
├── config/
│   └── default_config.yaml  # Default configuration
├── assets/
│   └── cute_cat.mp4         # Audio visualizer video (CRITICAL)
├── models/                   # Whisper models (downloaded on first run)
├── temp/                     # Temporary audio files
├── data/                     # Database and history
└── logs/                     # Application logs
```

**Important**: The `assets/` folder must be included for the audio visualizer animation to work!

## Distribution

### For Personal Use

Simply copy the entire `dist` folder to any Windows machine and run `CuteWhisper.exe`.

### For Distribution

1. **Create a ZIP archive**:
   ```cmd
   cd dist
   tar -a -c -f CuteWhisper-Windows.zip *
   # Or use Windows Explorer to ZIP the folder
   ```

2. **Distribute the ZIP** with installation instructions:
   - Extract ZIP
   - Run `CuteWhisper.exe`
   - First run downloads Whisper model

## Important Build Fixes

The following fixes are **critical** for the executable to work correctly. These are already implemented in `CuteWhisper.spec`.

### 1. Whisper Assets Bundling

**Problem**: Whisper requires `mel_filters.npz` and tiktoken files that are not automatically included.

**Solution**: The spec file manually collects Whisper assets:

```python
# CRITICAL: Manually collect whisper assets (mel_filters.npz, tiktoken files)
try:
    import whisper
    whisper_assets_dir = os.path.join(os.path.dirname(whisper.__file__), 'assets')
    if os.path.exists(whisper_assets_dir):
        datas += [(whisper_assets_dir, 'whisper/assets')]
except ImportError:
    pass
```

**Without this fix**: Transcription fails with "No such file or directory: whisper/assets/mel_filters.npz"

### 2. Video Assets Bundling

**Problem**: The audio visualizer video file (`cute_cat.mp4`) must be bundled.

**Solution**: The spec file includes the assets folder:

```python
# CRITICAL: Collect assets folder (video files)
assets_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'assets')
if os.path.exists(assets_dir):
    datas += [(assets_dir, 'assets')]
```

**Without this fix**: Recording indicator shows "Video file not found" warning

### 3. PyTorch Dependencies

**Problem**: PyTorch requires `unittest` module.

**Solution**: Keep `unittest` out of the excludes list:

```python
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
    'IPython',
    'pytest',
    # 'unittest',  # NEEDED by PyTorch, do not exclude
],
```

**Without this fix**: Exe crashes with "ModuleNotFoundError: No module named 'unittest'"

## Build Options

### Reduce Executable Size

**IMPORTANT**: Do NOT exclude `unittest` - PyTorch requires it!

Edit `CuteWhisper.spec` and add more packages to the `excludes` list:

```python
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
    'IPython',
    'pytest',
    # 'unittest',  # NEEDED by PyTorch, do not exclude
    'PyQt5',
    'PySide2',
],
```

### Add Custom Icon

1. Create an `.ico` file (e.g., `icon.ico`)
2. Edit `CuteWhisper.spec`:
   ```python
   icon='icon.ico',
   ```

### Windowed Mode (No Console)

Change `console=True` to `console=False` in `CuteWhisper.spec`:

```python
exe = EXE(
    ...
    console=False,  # Hide console window
    ...
)
```

**Note**: Set `console=False` only if you've implemented file-based logging, otherwise you won't see error messages.

## Troubleshooting

### Build Fails: "Module not found"

**Solution**: Make sure all dependencies are installed:
```cmd
pip install -r requirements.txt
```

### Build Fails: "PyInstaller not found"

**Solution**: Install PyInstaller:
```cmd
pip install pyinstaller
```

### Exe Crashes on Startup: "ModuleNotFoundError: No module named 'unittest'"

**Cause**: PyTorch requires the `unittest` module, but it's being excluded.

**Solution**: Remove `unittest` from the `excludes` list in `CuteWhisper.spec`:
```python
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
    'IPython',
    'pytest',
    # 'unittest',  # NEEDED by PyTorch, do not exclude
],
```

### Exe Runs But Transcription Fails: "No such file or directory: whisper/assets/mel_filters.npz"

**Cause**: Whisper assets are not bundled into the executable.

**Solution**: The spec file must manually collect Whisper assets (already implemented):
```python
# CRITICAL: Manually collect whisper assets
try:
    import whisper
    whisper_assets_dir = os.path.join(os.path.dirname(whisper.__file__), 'assets')
    if os.path.exists(whisper_assets_dir):
        datas += [(whisper_assets_dir, 'whisper/assets')]
except ImportError:
    pass
```

### Animation Not Working: "Video file not found"

**Cause**: The `cute_cat.mp4` file is not bundled.

**Solution**: The spec file must include the assets folder (already implemented):
```python
# CRITICAL: Collect assets folder (video files)
assets_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'assets')
if os.path.exists(assets_dir):
    datas += [(assets_dir, 'assets')]
```

Also copy assets after build:
```cmd
xcopy assets dist\assets /E /I /Y
```

Or using Python:
```cmd
python -c "import shutil, os; src='assets'; dst='dist/assets'; os.makedirs(dst, exist_ok=True); shutil.copy2(os.path.join(src, 'cute_cat.mp4'), dst)"
```

### Exe Crashes on Startup

**Possible causes**:
1. Missing dependencies → Rebuild with `--clean` flag
2. Antivirus blocking → Add to antivirus exceptions
3. Missing config files → Copy `config/` folder to `dist/`
4. Missing Whisper assets → See "Important Build Fixes" section above
5. Excluding `unittest` → Remove from excludes list

### Exe is Too Large

**Expected sizes**:
- Without torch: ~50-80 MB
- With torch (CPU): ~200-300 MB
- With torch (CUDA): ~400-600 MB

The size is due to PyTorch dependencies. This is normal.

### Model Download Fails in Exe

The executable will download Whisper models on first run to:
```
models/
```

Make sure this folder exists and is writable.

## Performance Tips

### Build Time Optimization

Build time can be 5-10 minutes. To speed up:

1. **Use UPX compression** (already enabled):
   ```python
   upx=True,
   ```

2. **Disable UPX** for faster builds (larger exe):
   ```python
   upx=False,
   ```

3. **Use one-file mode** (slower startup):
   Change the spec to use `onedir` mode (default).

### Runtime Performance

The executable runs at the same speed as the Python script. No performance loss.

## System Requirements

### Building
- Windows 10/11
- Python 3.8+
- 4GB RAM minimum
- 2GB free disk space

### Running (Built Exe)
- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- 500MB disk space
- Microphone
- Internet connection (first run only, for model download)

## Advanced: Automated Build Script

For CI/CD or automated builds:

```cmd
@echo off
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install pyinstaller
pyinstaller CuteWhisper.spec --clean --noconfirm
if errorlevel 1 exit /b 1
echo Build successful!
```

## Versioning

To version your executable:

1. Update version in `main.py`:
   ```python
   __version__ = '1.0.0'
   ```

2. Add to spec file:
   ```python
   exe = EXE(
       ...
       version='version_info.txt',
       ...
   )
   ```

3. Create `version_info.txt` (Windows format).

## Signing the Executable

For distribution, consider code signing:

```cmd
signtool sign /f certificate.pfx /p password dist\CuteWhisper.exe
```

This prevents Windows SmartScreen warnings.

## Support

If build issues persist:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Review PyInstaller logs in `build/`
3. Check CuteWhisper logs in `logs/cutewhisper.log`

---

**Happy building! 🚀**
