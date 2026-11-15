# Windows build

Target: Windows 10 or 11, Python 3.11 or newer, for the person building it. End users are not meant to install Python once an exe exists.

This repository does not contain a tested exe. Build it on Windows:

```bat
py -3 -m pip install -r requirements-desktop.txt pyinstaller
py -3 packaging\build_windows.py
```

The script calls PyInstaller with `packaging/probespeak.spec`. Output is `dist/ProbeSpeak/`. The database is created at runtime under the user's `.probespeak` folder, not inside the install directory.

If PyInstaller is missing, the script exits 2 and does not pretend a binary was produced.
