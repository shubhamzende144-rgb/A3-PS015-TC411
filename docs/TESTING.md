# Testing

```bash
PYTHONPATH=src:agent python3 -m pytest tests agent/tests -q
```

What is covered without a network:

- Linux and Windows route-table parsing
- All stored lab scenarios against the existing agent engine
- Declined recovery stays Unresolved
- Lab mode cannot call FIX_DNS
- Live recovery refuses a missing consent and a non-allowlisted action
- SQLite history and a repeated-fault incident
- Text, Markdown, JSON, CSV, and PDF export, including masking of a public IP, a MAC address, and a home path

The PySide6 window test runs only where Qt's shared libraries load (`QT_QPA_PLATFORM=offscreen`). This environment does not have `libEGL`, so that test is skipped here. It is not a passing UI test.

Live probes and a Windows `ProbeSpeak.exe` were not executed here.
