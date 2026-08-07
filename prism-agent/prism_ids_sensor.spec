# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['agent\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('rules', 'rules'), ('models', 'models'), ('.env.agent', '.')],
    hiddenimports=['concurrent.futures', 'asyncio', 'scapy.all', 'scapy.layers.all', 'scapy.layers.inet', 'scapy.layers.l2', 'sklearn.ensemble._forest', 'joblib', 'structlog', 'pydantic', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='prism_ids_sensor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['prism_icon.ico'],
)
