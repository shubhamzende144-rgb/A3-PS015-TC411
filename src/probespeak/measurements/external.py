"""Independent TCP reachability. One failed target is not 'the internet is down'."""
from __future__ import annotations

import socket
import time

from ..core.constants import DEFAULT_TCP_TARGETS

def probe_tcp(host: str, port: int, timeout: float = 2.0) -> dict:
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ms = round((time.perf_counter() - started) * 1000, 1)
            return {"host": host, "port": port, "ok": True, "ms": ms, "error": None}
    except OSError as exc:
        ms = round((time.perf_counter() - started) * 1000, 1)
        return {"host": host, "port": port, "ok": False, "ms": ms, "error": type(exc).__name__}

def probe_targets(targets=DEFAULT_TCP_TARGETS, timeout: float = 2.0) -> dict:
    rows = [probe_tcp(host, port, timeout) for host, port in targets]
    ok = sum(1 for row in rows if row["ok"])
    if ok == len(rows):
        summary = "Every independent TCP target accepted a connection."
    elif ok == 0:
        summary = "No independent TCP target accepted a connection. That is not, by itself, a named cause."
    else:
        summary = f"{ok} of {len(rows)} TCP targets answered. One miss does not mean the internet is down."
    return {"targets": rows, "ok": ok, "total": len(rows), "summary": summary}
