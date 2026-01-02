# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CuteWhisper
Build command: pyinstaller CuteWhisper.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files from config
datas = []
datas += collect_data_files('config')

# Collect hidden imports
hiddenimports = [
    'openai',
    'whisper',
    'torch',
    'numpy',
    'sounddevice',
    'pynput',
    'tkinter',
    '_tkinter',
]

# Collect all whisper dependencies
hiddenimports += collect_submodules('whisper')
hiddenimports += collect_submodules('torch')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'IPython',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CuteWhisper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available
)
