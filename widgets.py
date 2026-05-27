# widgets.py
from PyQt5.QtWidgets import QTabWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config import APP_NAME

class ScrollableTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setUsesScrollButtons(True)
        self.tabBar().setElideMode(Qt.ElideRight)
        self.setMovable(True)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00ff66;
                background: #0a0e12;
                border-radius: 8px;
            }
            QTabBar {
                background: #0a0e12;
            }
            QTabBar::tab {
                background: #1a221a;
                color: #00ffcc;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1a331a;
                color: #00ffcc;
                border-bottom: 2px solid #00ff66;
            }
            QTabBar::tab:hover {
                background: #2a442a;
            }
        """)
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == event.Wheel:
            delta = event.angleDelta().y()
            current = self.currentIndex()
            if delta > 0:
                self.setCurrentIndex(max(0, current - 1))
            else:
                self.setCurrentIndex(min(self.count() - 1, current + 1))
            return True
        return super().eventFilter(obj, event)

class WelcomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v1.0 - Bienvenido")
        self.setModal(True)
        self.setFixedSize(600, 320)
        self.setStyleSheet("""
            QDialog {
                background: #0a0e12;
                border: 2px solid #00ff66;
                border-radius: 16px;
            }
            QLabel {
                color: #00ff99;
                font-size: 14px;
            }
            QPushButton {
                background: #1a221a;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #116611;
            }
            QLineEdit {
                background: #0a0e12;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        layout = QVBoxLayout(self)
        title = QLabel("🔺 KARION IDE v1.0 🔻")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(QLabel("Selecciona la carpeta raíz de tu proyecto:"))
        self.path_edit = QLineEdit()
        layout.addWidget(self.path_edit)
        btn_layout = QHBoxLayout()
        browse = QPushButton("📂 EXAMINAR")
        browse.clicked.connect(self.browse)
        ok = QPushButton("🚀 INICIAR PROYECTO")
        ok.clicked.connect(self.accept)
        btn_layout.addWidget(browse)
        btn_layout.addWidget(ok)
        layout.addLayout(btn_layout)
        self.selected = None

    def browse(self):
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Carpeta del proyecto")
        if folder:
            self.path_edit.setText(folder)
            self.selected = folder

    def get_path(self):
        return self.selected or self.path_edit.text()