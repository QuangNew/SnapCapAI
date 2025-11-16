# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

# Collect Azure Speech SDK files
azure_datas = collect_data_files('azure.cognitiveservices.speech')
azure_binaries = collect_dynamic_libs('azure.cognitiveservices.speech')
azure_hiddenimports = collect_submodules('azure.cognitiveservices.speech')

# Collect CustomTkinter files
ctk_datas = collect_data_files('customtkinter')

# Combine all data files
datas = [
    ('config.json', '.'),
]
datas += azure_datas
datas += ctk_datas

# Combine all binaries
binaries = []
binaries += azure_binaries

# Hidden imports
hiddenimports = [
    'PIL._tkinter_finder',
    'pystray',
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'google.generativeai',
    'customtkinter',
    'tkinter',
    'azure',
    'azure.cognitiveservices',
    'azure.cognitiveservices.speech',
    'azure.cognitiveservices.speech.audio',
    'winotify',
    'win32api',
    'win32con',
    'win32gui',
    'winsound',
    'subprocess',
    'threading',
    'requests',
    'sounddevice',
    'soundfile',
    'numpy',
    'universal_converter',
    'cloudconvert_handler',
    'audio_handler',
]
hiddenimports += azure_hiddenimports

block_cipher = None

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],  # Look for hooks in current directory
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SnapCapAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='SnapCapAI.ico' if os.path.exists('SnapCapAI.ico') else None,
)
