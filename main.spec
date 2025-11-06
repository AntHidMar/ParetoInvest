# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ParetoInvest\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('ParetoInvest/ui', 'ParetoInvest/ui'), ('ParetoInvest/models', 'ParetoInvest/models'), ('ParetoInvest/libraries', 'ParetoInvest/libraries')],
    hiddenimports=['pandas', 'numpy', 'dateutil', 'pytz', 'requests', 'yfinance', 'ib_insync', 'asyncio', 'timeit'],
    hookspath=['pyinstaller_hooks'],
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
    [],
    exclude_binaries=True,
    name='main',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
