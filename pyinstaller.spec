block_cipher = None

added_files = [
    ('visualization', 'visualization'),  # (origen, destino en el binario)
]

cli_a = Analysis(
    ['src/aw_nextblock/cli.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='nextblock-ctl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

watcher_a = Analysis(
    ['src/aw_nextblock/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

watcher_pyz = PYZ(watcher_a.pure, watcher_a.zipped_data, cipher=block_cipher)

watcher_exe = EXE(
    watcher_pyz,
    watcher_a.scripts,
    [],
    exclude_binaries=True,
    name='aw-watcher-nextblock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    watcher_exe,
    watcher_a.binaries,
    watcher_a.zipfiles,
    watcher_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='aw-nextblock',
)
