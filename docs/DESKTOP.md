# ProbeSpeak desktop

The website stays in `src/` and still runs with `npm run dev`. The desktop window is a second front end on the same Python rules in `agent/probespeak_agent`.

## Run

```bash
python3 -m pip install -r requirements-desktop.txt
PYTHONPATH=src:agent python3 -m probespeak
```

On Windows, `run_probespeak.bat` does the same.

Data is stored in `~/.probespeak/desktop.sqlite`. Reports go to `~/.probespeak/reports/`.

## What a run does

Lab capture loads a stored scenario and the existing rule engine. It does not probe the network and it cannot change DNS.

Live mode discovers the default gateway, runs the agent's four instruments, and adds three TCP connection checks. The loaded-latency transfer starts only if you tick the consent box. Without that box the congestion check is unmeasured and the verdict stays Inconclusive.

Recovery stays off until Settings enables it and the Recovery page is confirmed. Lab results are refused.

## Tests

```bash
PYTHONPATH=src:agent python3 -m pytest tests agent/tests -q
```

## Windows package

Not produced in this environment. On a Windows machine:

```bat
py -3 -m pip install pyinstaller
py -3 packaging\build_windows.py
```

Do not describe `ProbeSpeak.exe` as tested until that command succeeds on Windows.
