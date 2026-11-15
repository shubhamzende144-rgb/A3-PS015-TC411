from __future__ import annotations

import sys

def main(argv=None) -> int:
    from PySide6.QtWidgets import QApplication
    from .main_window import MainWindow

    app = QApplication(sys.argv if argv is None else argv)
    window = MainWindow()
    window.show()
    return app.exec()
