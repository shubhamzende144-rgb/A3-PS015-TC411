"""Strip identifiers that do not belong in a shared report."""
from __future__ import annotations

import re

_MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
_USER_PATH = re.compile(r"(?i)(?:/Users/|/home/|[A-Za-z]:\\Users\\)[^/\\\s]+")
_PUBLIC_IP = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")

def _private(ip: str) -> bool:
    parts = [int(p) for p in ip.split(".")]
    if parts[0] in (10, 127) or ip.startswith("192.168.") or ip.startswith("169.254."):
        return True
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return True
    return False

def sanitize(text: str) -> str:
    text = _MAC.sub("[mac]", text)
    text = _USER_PATH.sub("[path]", text)

    def hide(match: re.Match) -> str:
        ip = match.group(0)
        return ip if _private(ip) else "[public-ip]"

    return _PUBLIC_IP.sub(hide, text)
