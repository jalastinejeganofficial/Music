# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

datas = [
    ('static', 'static'),
    ('assets', 'assets')
]

hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.on',
    'uvicorn.lifespans.off',
    'fastapi',
    'pydantic',
    'yt_dlp',
    'yt_dlp.extractor',
    'bs4',
    'webview',
    'clr_loader',
    'pythonnet'
]

excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'numpy',
    'pandas',
    'IPython',
    'ipykernel',
    'ipywidgets',
    'sphinx',
    'docutils',
    'jedi',
    'pygments',
    'pytest',
    'tornado',
    'zmq',
    'notebook',
    'jupyter',
    'jupyterlab',
    'nbformat',
    'nbconvert',
    'botocore',
    'boto3',
    'azure',
    'google',
    'pytz',
    'PIL.TkImagePlugin',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'qtpy'
]

# Pick icon based on platform
icon_file = 'assets/icon.ico' if sys.platform.startswith('win') else 'assets/icon.png'

a = Analysis(
    ['desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Music',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Music'
)
