# GPU Optimization Guide for CuteWhisper

## Current Status: CPU Only ❌

Your current configuration:
```python
device='cpu'
compute_type='int8'  # 8-bit integer (CPU optimized)
```

**Transcription speed:** ~5-10 seconds for base model

---

## How to Enable GPU Acceleration

### Option 1: Automatic CUDA Detection (Recommended)

**File:** `main.py` (lines 60-64)

**Change from:**
```python
self.transcriber = WhisperTranscriber(
    model_size=self.config.get('whisper.model_size', 'base'),
    device=self.config.get('whisper.device', 'cpu'),
    compute_type=self.config.get('whisper.compute_type', 'int8')
)
```

**To:**
```python
# Auto-detect CUDA
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
compute_type = 'float16' if device == 'cuda' else 'int8'

self.transcriber = WhisperTranscriber(
    model_size=self.config.get('whisper.model_size', 'base'),
    device=device,
    compute_type=compute_type
)
```

### Option 2: Config File

**Create:** `config/user_config.yaml`
```yaml
whisper:
  model_size: base
  device: cuda  # or 'cpu'
  compute_type: float16  # Use float16 on GPU
  language: auto
```

---

## Performance Comparison

| Configuration | Speed | Memory | Quality |
|--------------|-------|---------|---------|
| CPU + int8 | 5-10s | ~2GB | Same |
| GPU + float16 | 1-2s | ~4GB | Same |
| **Speedup** | **5-10x faster** | | |

---

## Requirements for GPU

### NVIDIA GPU:
- CUDA Toolkit 11.8+ installed
- NVIDIA GPU with compute capability 7.0+
- PyTorch with CUDA support

### Check if CUDA is available:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

Run this in Python:
```bash
./venv/Scripts/python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**If output is `CUDA: True`** → GPU acceleration will work! ✅

**If output is `CUDA: False`** → You need to install PyTorch with CUDA support.

---

## Installing PyTorch with CUDA

### Check CUDA Version:
```bash
nvidia-smi
```

Look for "CUDA Version: XX.X"

### Install PyTorch:
Visit https://pytorch.org/get-started/locally/

For CUDA 11.8:
```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CUDA 12.1:
```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## Quick Test

After enabling GPU, test the speed:

1. Press Ctrl+Space and speak for 5 seconds
2. Release
3. Watch the console for timing

**Expected:**
- CPU: "[STOP] Processing..." → ~5 second wait → "[TEXT]"
- GPU: "[STOP] Processing..." → ~1-2 second wait → "[TEXT]"

---

## Current Visualizer Improvements

### What Changed:

✅ **Removed timer/counter** - Clean look, just bars
✅ **Rounded capsule shape** - 120x30px rounded window
✅ **Better wave animation** - Phase-shifted bars create wave effect
✅ **Improved bar movement** - Bars extend vertically based on audio
✅ **Dark blue theme** - Professional appearance

### Visualizer Specs:
- **Size:** 120x30px (compact capsule)
- **Bars:** 16 bars, 4px wide, 3px spacing
- **Height range:** 2px → 11px (uses most of window)
- **Animation:** Wave pattern with phase shifts
- **Colors:** Dark blue to bright blue gradient

---

## Summary

### GPU Status:
- **Current:** NOT using GPU (CPU only)
- **Potential:** 5-10x speedup with CUDA
- **Action:** Follow guide above to enable

### Visualizer Status:
- ✅ No timer
- ✅ Rounded window
- ✅ Just beautiful animated bars
- ✅ Wave animation pattern
- ✅ Responsive to audio

---

**Next Steps:**
1. Test the new visualizer (Ctrl+Space)
2. Check if you have NVIDIA GPU
3. Enable GPU acceleration if possible
4. Enjoy much faster transcription!
