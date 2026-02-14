# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["wurb_main.py"],
    pathex=[],
    binaries=[],
    datas=[("wurb_config_default.yaml","."),
           ("wurb_app/static/css/*","./wurb_app/static/css/"),
           ("wurb_app/static/images/*","./wurb_app/static/images/"),
           ("wurb_app/static/js/*","./wurb_app/static/js/"),
           ("wurb_app/templates/*","./wurb_app/templates/"),
           ("cloudedbats_logo.png","."),
           ],
    hiddenimports=["wurb_api"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="wurb_2026_webserver",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="cloudedbats_logo.png",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wurb_2026_webserver",
)
