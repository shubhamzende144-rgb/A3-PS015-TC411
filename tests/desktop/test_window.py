import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
except Exception as exc:  # missing libEGL or PySide6 on this machine
    pytest.skip(f"Qt cannot load here: {exc}", allow_module_level=True)

from probespeak.desktop.main_window import MainWindow
from probespeak.simulation.lab import run_lab


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_window_shows_a_lab_result(app, tmp_path):
    window = MainWindow(db_path=str(tmp_path / "ui.sqlite"))
    window._on_result(run_lab("clean-fiber"))
    assert window.cards["verdict"].value.text() == "no_fault_observed"
    assert window.history_table.rowCount() == 1
    window._recover()
    assert "never changes" in window.recovery_log.toPlainText()
    window.close()
