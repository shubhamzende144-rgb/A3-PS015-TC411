"""Lab runs never reach a live recovery or a live probe."""
from __future__ import annotations

from ..core.exceptions import SafetyError

LIVE_ACTIONS = frozenset({
    "FIX_DNS", "RESTORE_DNS", "RENEW_DHCP", "RECONNECT_NETWORK",
})

def assert_lab_safe(result: dict) -> None:
    if result.get("deviceChanged"):
        raise SafetyError("A lab result claimed the device changed.")
    if result.get("mode") not in (None, "lab"):
        raise SafetyError("A lab result left lab mode.")
    recovery = result.get("recovery")
    if recovery in LIVE_ACTIONS and result.get("executedLive"):
        raise SafetyError("A lab scenario executed a live recovery action.")
