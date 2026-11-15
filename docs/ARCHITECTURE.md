# Architecture

ProbeSpeak still has two front ends and one diagnosis engine.

- The website stays in the repository root (`npm run dev`, port 8080).
- The local agent stays in `agent/probespeak_agent`. It measures, applies the rules, and is the only code allowed to attempt DNS or DHCP changes.
- The desktop package in `src/probespeak` imports that agent. It does not keep a second copy of the thresholds or the rules.

Desktop flow:

1. Lab mode calls `simulation/lab.py`, which replays a stored scenario. A safety check refuses any result that says the device changed.
2. Live mode calls `measurements/live.py`: routing-table gateway discovery, the agent's four instruments, and separate TCP connects to 1.1.1.1, 8.8.8.8, and 9.9.9.9. TCP results are shown beside the verdict. They do not override the four-check rules.
3. `diagnosis/engine.py` turns the agent result into plain language and applies the same resolved / unresolved / inconclusive / no-fault rule.
4. `persistence/database.py` stores the run in SQLite (WAL). Two identical named faults in a row become an incident.
5. Recovery goes through `recovery/service.py` only after the run is live, the action is allowlisted, settings enable changes, and the user confirms the dialog.

The window is PySide6. Long work is a `QThread`. History, incidents, and exports read the SQLite file under `~/.probespeak`.
