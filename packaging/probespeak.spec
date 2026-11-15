# PyInstaller spec. Not a verified Windows build until it is run on Windows.
# pyinstaller packaging/probespeak.spec

block_cipher = None

a = Analysis(
    ["src/probespeak/__main__.py"],
    pathex=["src", "agent"],
    binaries=[],
    datas=[],
    hiddenimports=["probespeak_agent", "dns", "PySide6"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="ProbeSpeak", console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="ProbeSpeak")
