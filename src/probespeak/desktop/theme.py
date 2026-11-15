DARK = """
QWidget { background: #101418; color: #e7eeea; font-size: 13px; }
QFrame#card, QTextEdit, QListWidget, QTableWidget, QLineEdit, QComboBox {
  background: #171d22; border: 1px solid #2a333b; border-radius: 8px;
}
QPushButton { background: #e09a3e; color: #1a1206; border: 0; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
QPushButton:disabled { background: #3a4046; color: #9aa4a0; }
QPushButton#ghost { background: transparent; color: #e7eeea; border: 1px solid #2a333b; }
QListWidget#nav { background: #0c1014; border: 0; }
QListWidget#nav::item { padding: 10px 12px; }
QListWidget#nav::item:selected { background: #24303a; color: #e09a3e; }
QHeaderView::section { background: #171d22; color: #9aa4a0; border: 0; padding: 6px; }
"""

LIGHT = """
QWidget { background: #f4f1ea; color: #1c1915; font-size: 13px; }
QFrame#card, QTextEdit, QListWidget, QTableWidget, QLineEdit, QComboBox {
  background: #fffdf8; border: 1px solid #ddd4c4; border-radius: 8px;
}
QPushButton { background: #9a5b12; color: white; border: 0; border-radius: 6px; padding: 8px 14px; }
QPushButton#ghost { background: transparent; color: #1c1915; border: 1px solid #ddd4c4; }
QListWidget#nav { background: #ebe6dc; border: 0; }
QListWidget#nav::item:selected { background: #fffdf8; color: #9a5b12; }
"""
