"""One diagnosis engine: the existing agent rules. This module only explains them."""
from __future__ import annotations

from ..bootstrap import install_agent
from ..core.constants import PLAIN

install_agent()

from probespeak_agent.engine.diagnose import diagnose  # noqa: E402
from probespeak_agent.engine.outcome import decide_recovery_outcome  # noqa: E402

FINDING_TITLE = {
    "NO_FAULT": "No fault observed",
    "DNS_RESOLVER_FAILURE": "DNS resolver failure",
    "GATEWAY_UNREACHABLE": "Gateway unreachable",
    "SIGNIFICANT_PACKET_LOSS": "Significant packet loss",
    "LOADED_LATENCY_INFLATION": "Loaded latency inflation",
    "NONE": "Inconclusive",
}

def explain(diagnosis: dict) -> dict:
    finding = diagnosis["finding"]
    return {
        "finding": finding,
        "title": FINDING_TITLE.get(finding, finding),
        "preliminary": diagnosis["preliminary"],
        "plain": PLAIN.get(finding, diagnosis["summary"]),
        "technical": diagnosis["summary"],
        "recovery": diagnosis.get("recovery"),
        "reasons": list(diagnosis.get("reasons") or []),
        "checks": diagnosis["checks"],
        "trace": diagnosis["trace"],
    }

def verdict_after_retest(action: str | None, after_diagnosis: dict | None, permission: str) -> dict:
    """Resolved only when a permitted recovery is followed by a clean retest."""
    if permission == "declined":
        return {"verdict": "unresolved", "rollback": False,
                "detail": "A fault was found and the change was declined. Status is Unresolved."}
    if not action or after_diagnosis is None:
        preliminary = (after_diagnosis or {}).get("preliminary")
        if preliminary == "no_fault_observed":
            return {"verdict": "no_fault_observed", "rollback": False,
                    "detail": "All checks passed. Nothing was repaired."}
        if preliminary == "inconclusive":
            return {"verdict": "inconclusive", "rollback": False,
                    "detail": "Evidence is incomplete or in conflict. No cause is named."}
        return {"verdict": "unresolved", "rollback": False,
                "detail": "A fault remains and no verified repair is attached."}
    return decide_recovery_outcome(action, after_diagnosis)

def diagnose_measurement(measurement):
    return explain(diagnose(measurement))
