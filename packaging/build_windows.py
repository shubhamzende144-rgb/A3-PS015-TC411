"""Prepare a Windows folder build. This script does not claim the exe was tested unless PyInstaller succeeds here."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    if shutil.which("pyinstaller") is None:
        print("PyInstaller is not installed. On Windows: py -3 -m pip install pyinstaller")
        print("Then: py -3 -m PyInstaller packaging/probespeak.spec")
        return 2
    proc = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "packaging/probespeak.spec", "--noconfirm"],
        cwd=ROOT,
    )
    print("Build finished." if proc.returncode == 0 else "Build failed. The exe is not verified.")
    return proc.returncode

if __name__ == "__main__":
    raise SystemExit(main())
