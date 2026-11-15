# AIORI-3 Hackathon — ProbeSpeak (PS-015)

Team repository for AIORI-3. This tree is the ProbeSpeak console: last-mile fault diagnosis from evidence.

Team introduction: https://youtu.be/bpURKXF7080
website link: https://probespeak.vercel.app/

## Run

```bash
npm install
npm run dev
```

The console listens on port 8080. Lab capture needs no agent. Live mode talks only to `http://127.0.0.1:8765`.


Last-mile fault diagnosis from evidence.

The order is fixed: measure, explain with evidence, ask permission, attempt a safe recovery, retest, verify. If evidence is missing, contradictory, or too small, the result is **Inconclusive**. The console does not invent a cause.

## What is measured

- Gateway reachability
- DNS resolution (cache-bypassing lookup of `cloudflare.com`)
- Packet loss (recomputed from sent and received)
- Congestion / loaded latency (unloaded vs loaded RTT)

## Modes

- **Lab capture** — twelve stored records run through the same rule engine, including scripted retests. Nothing on the device changes.
- **Live agent** — `http://127.0.0.1:8765` only. Connected requires a valid health document. Without it, the run is Inconclusive.

## Outcomes

- **Resolved** — only after a retest in which every check passes.
- **Unresolved** — a fault was identified, recovery was declined, or the retest did not clear it.
- **Inconclusive** — the records do not isolate a cause.
- **No fault observed** — all four checks passed. Nothing was repaired, so this is not Resolved.

## Agent

A full Python measuring-and-recovery agent lives in [`agent/`](agent/README.md). The `public/probespeak-agent.mjs` below is the minimal reference process.

## Desktop application

A PySide6 window uses that same rule engine. The website is unchanged.

```bash
python3 -m pip install -r requirements-desktop.txt
PYTHONPATH=src:agent python3 -m probespeak
```

Lab scenarios do not touch this computer. Live recovery stays off until you allow it. Details, the comparison with the other PS-015 desktop projects, and the Windows build steps are in [docs/DESKTOP.md](docs/DESKTOP.md) and [docs/FEATURE_COMPARISON.md](docs/FEATURE_COMPARISON.md).


Allowlist: `VERIFY_DNS`, `FIX_DNS`, `RESTORE_DNS`, `VERIFY_GATEWAY`, `RENEW_DHCP`, `RECONNECT_NETWORK`, `VERIFY_PACKET_LOSS`, `RETEST`.

DNS recovery must verify the failure, save the current resolvers, apply `1.1.1.1` and `1.0.0.1`, flush, retest, keep only on a clean retest, and roll back otherwise. No arbitrary shell commands.

`public/probespeak-agent.mjs` is a reference process. It measures DNS and refuses system changes. It does not fabricate the other instruments.

The in-app Method page is the operator-facing copy of this note.
