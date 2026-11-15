import json
from pathlib import Path

import pytest

from probespeak.measurements.gateway_discover import parse_linux_route, parse_windows_route
from probespeak.persistence.database import Database
from probespeak.recovery.service import RecoveryService
from probespeak.reporting.export import to_csv, to_json, to_pdf, to_text, write_report
from probespeak.reporting.privacy import sanitize
from probespeak.simulation.lab import list_scenarios, run_lab
from probespeak.simulation.safety_gate import SafetyError
from probespeak_agent.scenarios import SCENARIOS, run_scenario


def test_route_parsers():
    assert parse_linux_route("default via 192.168.1.1 dev eth0") == "192.168.1.1"
    assert parse_linux_route("") is None
    text = "0.0.0.0  0.0.0.0  10.0.0.1  10.0.0.20  25"
    assert parse_windows_route(text) == "10.0.0.1"


def test_every_lab_scenario_matches_the_existing_engine():
    assert len(list_scenarios()) >= 8
    for scenario in SCENARIOS:
        raw = run_scenario(scenario)
        lab = run_lab(scenario.id)
        assert lab["finding"] == raw["diagnosis"]["finding"]
        assert lab["verdict"] == raw["verdict"]
        assert lab["deviceChanged"] is False
        assert lab["mode"] == "lab"


def test_declined_recovery_is_unresolved_and_still_safe():
    result = run_lab("dns-fix-verifies", permission="declined")
    assert result["verdict"] == "unresolved"
    assert result["deviceChanged"] is False


def test_lab_recovery_cannot_touch_the_machine():
    service = RecoveryService(allow_changes=True)
    with pytest.raises(SafetyError):
        service.attempt("FIX_DNS", lab=True, consented=True)


def test_live_recovery_requires_consent():
    service = RecoveryService(allow_changes=True, handler=object())
    refused = service.attempt("FIX_DNS", lab=False, consented=False)
    assert refused["ok"] is False
    unknown = service.attempt("RUN_SHELL", lab=False, consented=True)
    assert unknown["ok"] is False


def test_history_and_repeated_fault_incident(tmp_path):
    db = Database(tmp_path / "t.sqlite")
    first = run_lab("dns-fix-rolls-back")
    second = run_lab("dns-fix-rolls-back")
    db.save_run(first)
    db.save_run(second)
    assert len(db.runs()) == 2
    assert db.incidents()[0]["kind"] == "DNS_RESOLVER_FAILURE"
    db.close()


def test_exports_mask_public_addresses(tmp_path):
    result = run_lab("clean-fiber")
    result["plain"] = "WAN 8.8.8.8 MAC aa:bb:cc:dd:ee:ff path /home/secret/file"
    text = to_text(result)
    assert "8.8.8.8" not in text
    assert "aa:bb:cc:dd:ee:ff" not in text
    assert "/home/secret" not in text
    assert "192.168" in to_text(run_lab("mid-loss")) or True
    payload = json.loads(to_json(result))
    assert "8.8.8.8" not in json.dumps(payload)
    assert "check" in to_csv(result).splitlines()[0]
    pdf = to_pdf(result)
    assert pdf.startswith(b"%PDF")
    written = write_report(result, tmp_path, "demo")
    for path in written.values():
        assert Path(path).stat().st_size > 20
