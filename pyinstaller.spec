block_cipher = None

import os
from PyInstaller.utils.hooks import collect_data_files

# Collect data files from desktop-notifier
desktop_notifier_data = collect_data_files('desktop_notifier')

added_files = desktop_notifier_data

cli_a = Analysis(
    ['src/aw_nextblock/__main__.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['desktop_notifier.resources'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    cli_a.binaries,      # ← Incluido en el EXE
    cli_a.zipfiles,      # ← Incluido en el EXE
    cli_a.datas,         # ← Incluido en el EXE
    [],
    name='aw-nextblock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

