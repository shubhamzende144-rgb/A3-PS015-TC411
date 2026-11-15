"""ProbeSpeak desktop shell. Lab results are stored numbers. Live results come from this computer."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QListWidget, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget,
)

from .. import PRODUCT, TAGLINE, __version__
from ..core.constants import MONITOR_CHOICES
from ..monitoring.scheduler import Scheduler
from ..persistence.database import Database
from ..recovery.service import RecoveryService
from ..reporting.export import write_report
from ..simulation.lab import list_scenarios
from .theme import DARK, LIGHT
from .worker import DiagnosticWorker

NAV = [
    "Overview", "Diagnosis", "Results", "Recovery", "Monitoring",
    "History", "Incidents", "Reports", "Simulation lab", "Settings", "About",
]

def card(title: str, body: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    heading = QLabel(title)
    heading.setStyleSheet("color: #9aa4a0; font-size: 11px;")
    value = QLabel(body)
    value.setWordWrap(True)
    value.setObjectName("value")
    layout.addWidget(heading)
    layout.addWidget(value)
    frame.value = value
    return frame

class MainWindow(QMainWindow):
    def __init__(self, db_path: str | None = None):
        super().__init__()
        self.setWindowTitle(f"{PRODUCT} — {TAGLINE}")
        self.resize(1180, 760)
        self.db = Database(db_path or str(Path.home() / ".probespeak" / "desktop.sqlite"))
        self.current: dict | None = None
        self.worker: DiagnosticWorker | None = None
        self.recovery = RecoveryService(allow_changes=False)
        self.scheduler = Scheduler(MONITOR_CHOICES["1 hour"], self._scheduled)
        self._build()
        self.setStyleSheet(DARK)
        self.refresh_history()

    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        row = QHBoxLayout(root)
        self.nav = QListWidget()
        self.nav.setObjectName("nav")
        self.nav.setFixedWidth(200)
        self.nav.addItems(NAV)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex if False else self._go)
        self.stack = QStackedWidget()
        for builder in (
            self._overview, self._diagnosis, self._results, self._recovery,
            self._monitoring, self._history, self._incidents, self._reports,
            self._lab, self._settings, self._about,
        ):
            self.stack.addWidget(builder())
        row.addWidget(self.nav)
        row.addWidget(self.stack, 1)
        self.nav.setCurrentRow(0)

    def _go(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def _overview(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Overview"))
        self.overview_note = QLabel("No run yet. An empty screen is not a pass.")
        self.overview_note.setWordWrap(True)
        layout.addWidget(self.overview_note)
        grid = QHBoxLayout()
        self.cards = {
            "verdict": card("Verdict", "—"),
            "finding": card("Finding", "—"),
            "gateway": card("Gateway", "—"),
            "dns": card("DNS", "—"),
            "loss": card("Packet loss", "—"),
            "latency": card("Loaded latency", "—"),
        }
        for item in self.cards.values():
            grid.addWidget(item)
        layout.addLayout(grid)
        self.tcp_label = QLabel("TCP targets have not been checked.")
        self.tcp_label.setWordWrap(True)
        layout.addWidget(self.tcp_label)
        go = QPushButton("Open diagnosis")
        go.clicked.connect(lambda: self.nav.setCurrentRow(1))
        layout.addWidget(go)
        layout.addStretch(1)
        return page

    def _diagnosis(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Network diagnosis"))
        self.mode = QComboBox()
        self.mode.addItems(["Lab capture", "Live agent"])
        layout.addWidget(self.mode)
        self.load_box = QCheckBox("Allow a bounded loaded-latency transfer on a live run")
        layout.addWidget(self.load_box)
        self.progress = QTextEdit()
        self.progress.setReadOnly(True)
        layout.addWidget(self.progress)
        self.run_btn = QPushButton("Run diagnosis")
        self.run_btn.clicked.connect(self._start_from_diagnosis)
        layout.addWidget(self.run_btn)
        return page

    def _results(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.result_title = QLabel("No result")
        self.result_title.setStyleSheet("font-size: 22px;")
        self.result_plain = QLabel("")
        self.result_plain.setWordWrap(True)
        self.result_tech = QTextEdit()
        self.result_tech.setReadOnly(True)
        layout.addWidget(self.result_title)
        layout.addWidget(self.result_plain)
        layout.addWidget(self.result_tech)
        return page

    def _recovery(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.recovery_text = QLabel("Run a diagnosis first. A change is offered only for a clear DNS or gateway fault.")
        self.recovery_text.setWordWrap(True)
        self.consent = QCheckBox("I understand this can change DNS or renew DHCP on this computer")
        self.recovery_log = QTextEdit()
        self.recovery_log.setReadOnly(True)
        self.recover_btn = QPushButton("Attempt allowlisted recovery")
        self.recover_btn.clicked.connect(self._recover)
        layout.addWidget(self.recovery_text)
        layout.addWidget(self.consent)
        layout.addWidget(self.recover_btn)
        layout.addWidget(self.recovery_log)
        return page

    def _monitoring(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Scheduled checks stay off until you enable them. Only one run executes at a time."))
        self.interval = QComboBox()
        self.interval.addItems(list(MONITOR_CHOICES))
        self.monitor_on = QCheckBox("Enable monitoring")
        self.monitor_on.toggled.connect(self._toggle_monitor)
        self.monitor_status = QLabel("Monitoring is off.")
        layout.addWidget(self.interval)
        layout.addWidget(self.monitor_on)
        layout.addWidget(self.monitor_status)
        layout.addStretch(1)
        return page

    def _history(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Id", "When", "Mode", "Finding", "Verdict"])
        self.history_table.cellClicked.connect(self._open_history)
        layout.addWidget(self.history_table)
        return page

    def _incidents(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.incident_table = QTableWidget(0, 4)
        self.incident_table.setHorizontalHeaderLabels(["Id", "When", "Kind", "Detail"])
        layout.addWidget(self.incident_table)
        note = QLabel("An incident is recorded only when the same named fault appears on two runs in a row.")
        note.setWordWrap(True)
        layout.addWidget(note)
        return page

    def _reports(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Exports the latest run as text, Markdown, JSON, CSV, and PDF. Public IPs, MAC addresses, and home paths are masked."))
        btn = QPushButton("Export latest run")
        btn.clicked.connect(self._export)
        self.export_label = QLabel("Nothing exported.")
        self.export_label.setWordWrap(True)
        layout.addWidget(btn)
        layout.addWidget(self.export_label)
        layout.addStretch(1)
        return page

    def _lab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Simulation uses stored numbers and the same rule engine. It cannot change this computer."))
        self.scenarios = QListWidget()
        for item in list_scenarios():
            self.scenarios.addItem(f"{item['id']} — {item['title']}")
            self.scenarios.item(self.scenarios.count() - 1).setData(Qt.UserRole, item["id"])
        self.scenarios.setCurrentRow(0)
        self.decline = QCheckBox("Decline the simulated recovery")
        run = QPushButton("Run selected lab scenario")
        run.clicked.connect(self._start_lab)
        layout.addWidget(self.scenarios)
        layout.addWidget(self.decline)
        layout.addWidget(run)
        return page

    def _settings(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.theme_box = QCheckBox("Light theme")
        self.theme_box.toggled.connect(self._theme)
        self.allow_changes = QCheckBox("Enable recovery changes (still asks every time)")
        self.allow_changes.toggled.connect(self._arm_recovery)
        layout.addWidget(self.theme_box)
        layout.addWidget(self.allow_changes)
        layout.addWidget(QLabel("Thresholds are the same numbers as the website rule engine. They are not edited here, so the desktop and the site cannot drift apart."))
        layout.addStretch(1)
        return page

    def _about(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        text = QLabel(
            f"{PRODUCT} {__version__}\nPS-015 · AIORI-3\n\n"
            "Python desktop console for last-mile diagnosis. "
            "Measure, explain with evidence, ask permission, attempt a safe recovery, retest, verify.\n\n"
            "The website in this repository is still there. This window uses the same Python rule engine.\n\n"
            "Not finished in this build: a tested Windows .exe, upload-speed measurement, "
            "and a live NIC packet graph. Those are not shown as if they worked."
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        return page

    def _theme(self, light: bool) -> None:
        self.setStyleSheet(LIGHT if light else DARK)

    def _arm_recovery(self, enabled: bool) -> None:
        self.recovery.allow_changes = enabled
        self.recovery._handler = None

    def _start_from_diagnosis(self) -> None:
        if self.mode.currentText().startswith("Lab"):
            self._start_lab()
        else:
            self._start_worker("live", include_load=self.load_box.isChecked())

    def _start_lab(self) -> None:
        item = self.scenarios.currentItem()
        scenario_id = item.data(Qt.UserRole) if item else "clean-fiber"
        permission = "declined" if self.decline.isChecked() else "allowed"
        self._start_worker("lab", scenario_id, permission)

    def _start_worker(self, kind: str, scenario_id: str | None = None, permission: str = "allowed", include_load: bool = False) -> None:
        if self.worker and self.worker.isRunning():
            self.progress.append("A run is already in progress.")
            return
        self.run_btn.setEnabled(False)
        self.worker = DiagnosticWorker(kind, scenario_id, permission, include_load)
        self.worker.progressed.connect(self.progress.append)
        self.worker.finished_ok.connect(self._on_result)
        self.worker.failed.connect(self._on_fail)
        self.worker.start()

    def _on_fail(self, message: str) -> None:
        self.run_btn.setEnabled(True)
        self.progress.append(message)
        QMessageBox.warning(self, "ProbeSpeak", message)

    def _on_result(self, result: dict) -> None:
        self.run_btn.setEnabled(True)
        self.current = result
        self.db.save_run(result)
        self._paint(result)
        self.refresh_history()
        self.nav.setCurrentRow(2)

    def _paint(self, result: dict) -> None:
        checks = result.get("checks") or {}
        self.overview_note.setText(result.get("outcomeDetail") or result.get("plain") or "")
        self.cards["verdict"].value.setText(str(result.get("verdict")))
        self.cards["finding"].value.setText(str(result.get("titleFinding") or result.get("finding")))
        for key, label in (("gateway", "gateway"), ("dns", "dns"), ("loss", "packet_loss"), ("latency", "congestion")):
            check = checks.get(label) or {}
            self.cards[key].value.setText(f"{check.get('band', '—')}\n{check.get('detail', '')}")
        tcp = result.get("tcp")
        self.tcp_label.setText(tcp["summary"] if tcp else "No separate TCP check on this run.")
        self.result_title.setText(f"{result.get('verdict')} — {result.get('titleFinding') or result.get('finding')}")
        self.result_plain.setText(result.get("plain") or "")
        lines = [result.get("technical") or "", ""]
        for entry in result.get("trace") or []:
            lines.append(f"{entry.get('outcome')} · {entry.get('title')}: {entry.get('detail')}")
        if result.get("after"):
            lines += ["", "Retest", result["after"].get("technical") or ""]
        self.result_tech.setPlainText("\n".join(lines))
        action = result.get("recovery") or "none"
        self.recovery_text.setText(
            f"Suggested action: {action}. Mode: {result.get('mode')}. "
            "Lab runs cannot apply it. Live changes stay off until Settings and this page both allow them."
        )

    def _recover(self) -> None:
        if not self.current:
            self.recovery_log.append("No diagnosis yet.")
            return
        if self.current.get("mode") == "lab":
            self.recovery_log.append("Refused. A lab scenario never changes this computer.")
            return
        action = self.current.get("recovery")
        if not action:
            self.recovery_log.append("This finding has no allowlisted recovery.")
            return
        if not self.consent.isChecked():
            self.recovery_log.append("Not started. The permission box is unchecked.")
            return
        answer = QMessageBox.question(self, "Allow this change?", f"Run {action} on this computer?")
        if answer != QMessageBox.Yes:
            self.recovery_log.append("Declined.")
            return
        outcome = self.recovery.attempt(action, lab=False, consented=True)
        self.recovery_log.append(str(outcome.get("error") or outcome.get("log") or outcome))

    def _toggle_monitor(self, enabled: bool) -> None:
        self.scheduler.stop()
        if enabled:
            self.scheduler.interval_s = MONITOR_CHOICES[self.interval.currentText()]
            self.scheduler.start()
            self.monitor_status.setText(f"Monitoring every {self.interval.currentText()}. The first check waits for that interval.")
        else:
            self.monitor_status.setText("Monitoring is off.")

    def _scheduled(self) -> None:
        # Runs off the UI thread. Only a lab-safe no: live measurement, no recovery.
        try:
            from ..measurements.live import run_live
            from ..diagnosis.engine import explain, verdict_after_retest
            result = run_live(include_tcp=True, include_load=False)
            explained = explain(result["diagnosis"])
            decision = verdict_after_retest(None, result["diagnosis"], "not_offered")
            result.update({
                "finding": explained["finding"], "titleFinding": explained["title"],
                "plain": explained["plain"], "technical": explained["technical"],
                "checks": explained["checks"], "trace": explained["trace"],
                "verdict": decision["verdict"], "title": "Scheduled check",
                "recovery": None,
            })
            self.db.save_run(result)
        except Exception:
            return

    def refresh_history(self) -> None:
        runs = self.db.runs()
        self.history_table.setRowCount(len(runs))
        for row, item in enumerate(runs):
            for col, key in enumerate(("id", "created_at", "mode", "finding", "verdict")):
                self.history_table.setItem(row, col, QTableWidgetItem(str(item[key])))
        incidents = self.db.incidents()
        self.incident_table.setRowCount(len(incidents))
        for row, item in enumerate(incidents):
            for col, key in enumerate(("id", "created_at", "kind", "detail")):
                self.incident_table.setItem(row, col, QTableWidgetItem(str(item[key])))

    def _open_history(self, row: int, _col: int) -> None:
        run_id = int(self.history_table.item(row, 0).text())
        result = self.db.run(run_id)
        if result:
            self.current = result
            self._paint(result)
            self.nav.setCurrentRow(2)

    def _export(self) -> None:
        if not self.current:
            self.export_label.setText("Nothing to export. Run a diagnosis first.")
            return
        folder = Path.home() / ".probespeak" / "reports"
        paths = write_report(self.current, folder, "latest")
        self.export_label.setText("Wrote " + ", ".join(paths.values()))

    def closeEvent(self, event) -> None:
        self.scheduler.stop()
        self.db.close()
        super().closeEvent(event)
