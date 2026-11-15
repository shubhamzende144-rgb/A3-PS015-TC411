"""Permission-gated recovery. Lab mode cannot reach this."""
from __future__ import annotations

from ..bootstrap import install_agent
from ..core.exceptions import SafetyError

install_agent()

from probespeak_agent.thresholds import ALLOWED_ACTIONS  # noqa: E402

class RecoveryService:
    def __init__(self, allow_changes: bool = False, handler=None):
        self.allow_changes = allow_changes
        self._handler = handler

    def handler(self):
        if self._handler is None:
            from probespeak_agent.actions import ActionHandler
            self._handler = ActionHandler(allow_changes=self.allow_changes)
        return self._handler

    def attempt(self, action: str, *, lab: bool, consented: bool) -> dict:
        if lab:
            raise SafetyError("Lab mode cannot change DNS, DHCP, or the network.")
        if action not in ALLOWED_ACTIONS:
            return {"ok": False, "action": action, "error": "Action is not allowlisted."}
        if action in ("FIX_DNS", "RENEW_DHCP", "RECONNECT_NETWORK") and not (self.allow_changes and consented):
            return {"ok": False, "action": action, "error": "Recovery stays off until you allow this change."}
        return self.handler().handle(action)
