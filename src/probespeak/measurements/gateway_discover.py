"""Default-gateway discovery. A missing gateway is not the same as a failed ping."""
from __future__ import annotations

import re
import subprocess
import sys

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def parse_linux_route(text: str) -> str | None:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "default" and parts[1] == "via":
            return parts[2]
    return None

def parse_windows_route(text: str) -> str | None:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
            return parts[2]
    return None

def discover_gateway(runner=None) -> dict:
    """Return {ip, source, error}. ip is None when the route table has no default."""
    system = sys.platform
    try:
        if system == "win32":
            proc = (runner or subprocess).run(
                ["route", "print", "-4"], capture_output=True, text=True, timeout=8
            )
            ip = parse_windows_route(proc.stdout or "")
            source = "route print -4"
        else:
            proc = (runner or subprocess).run(
                ["ip", "route", "show", "default"], capture_output=True, text=True, timeout=8
            )
            ip = parse_linux_route(proc.stdout or "")
            source = "ip route show default"
        if proc.returncode not in (0, None) and not ip:
            return {"ip": None, "source": source, "error": (proc.stderr or "route command failed").strip()}
        return {"ip": ip, "source": source, "error": None if ip else "No default IPv4 gateway in the routing table."}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ip": None, "source": "unavailable", "error": type(exc).__name__}
