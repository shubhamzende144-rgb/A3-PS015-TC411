"""Network work off the UI thread."""
from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from ..measurements.live import run_live
from ..simulation.lab import run_lab

class DiagnosticWorker(QThread):
    progressed = Signal(str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, kind: str, scenario_id: str | None = None, permission: str = "allowed", include_load: bool = False):
        super().__init__()
        self.kind = kind
        self.scenario_id = scenario_id
        self.permission = permission
        self.include_load = include_load

    def run(self) -> None:
        try:
            self.progressed.emit("Reading measurements")
            if self.kind == "lab":
                self.progressed.emit("Applying the rule engine to stored numbers")
                result = run_lab(self.scenario_id or "clean-fiber", self.permission)
            else:
                self.progressed.emit("Probing gateway, DNS, loss, and — only if allowed — loaded latency")
                result = run_live(include_tcp=True, include_load=self.include_load)
                from ..diagnosis.engine import explain, verdict_after_retest
                explained = explain(result["diagnosis"])
                decision = verdict_after_retest(None, result["diagnosis"], "not_offered")
                result.update({
                    "finding": explained["finding"],
                    "titleFinding": explained["title"],
                    "plain": explained["plain"],
                    "technical": explained["technical"],
                    "checks": explained["checks"],
                    "trace": explained["trace"],
                    "reasons": explained["reasons"],
                    "recovery": explained["recovery"],
                    "verdict": decision["verdict"],
                    "outcomeDetail": decision["detail"],
                    "permission": "not_required",
                    "title": "Live measurement",
                })
            self.progressed.emit("Done")
            self.finished_ok.emit(result)
        except Exception as exc:  # UI must show the failure, not die
            self.failed.emit(f"{type(exc).__name__}: {exc}")
