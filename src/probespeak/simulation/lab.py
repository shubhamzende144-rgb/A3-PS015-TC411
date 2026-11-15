"""Replay stored scenarios through the same rule engine. Nothing is probed or changed."""
from __future__ import annotations

from ..bootstrap import install_agent
from ..diagnosis.engine import explain, verdict_after_retest
from .safety_gate import assert_lab_safe

install_agent()

from probespeak_agent.scenarios import SCENARIOS, run_scenario, scenario_by_id  # noqa: E402

def list_scenarios() -> list[dict]:
    return [
        {"id": item.id, "title": item.title, "situation": item.situation, "faultClass": item.fault_class}
        for item in SCENARIOS
    ]

def run_lab(scenario_id: str, permission: str = "allowed") -> dict:
    scenario = scenario_by_id(scenario_id)
    if scenario is None:
        raise KeyError(scenario_id)
    raw = run_scenario(scenario)
    explained = explain(raw["diagnosis"])
    after = explain(raw["afterDiagnosis"]) if raw.get("afterDiagnosis") else None
    if raw["diagnosis"]["recovery"] and permission == "declined":
        decision = verdict_after_retest(raw["diagnosis"]["recovery"], None, "declined")
    elif raw.get("afterDiagnosis"):
        decision = verdict_after_retest(raw["diagnosis"]["recovery"], raw["afterDiagnosis"], permission)
    else:
        decision = verdict_after_retest(None, raw["diagnosis"], "not_offered")
    result = {
        "mode": "lab",
        "deviceChanged": False,
        "executedLive": False,
        "id": raw["id"],
        "title": raw["title"],
        "situation": raw["situation"],
        "finding": explained["finding"],
        "titleFinding": explained["title"],
        "plain": explained["plain"],
        "technical": explained["technical"],
        "checks": explained["checks"],
        "trace": explained["trace"],
        "reasons": explained["reasons"],
        "recovery": explained["recovery"],
        "permission": permission if explained["recovery"] else "not_required",
        "after": after,
        "verdict": decision["verdict"],
        "outcomeDetail": decision["detail"],
        "rollbackNeeded": decision.get("rollback", False),
        "expected": raw["expected"],
        "matched": (
            raw["diagnosis"]["finding"] == raw["expected"]["finding"]
            and raw["verdict"] == raw["expected"]["verdict"]
        ),
    }
    assert_lab_safe(result)
    return result
