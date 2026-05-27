# mainwindow.py
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QAction, QFileDialog, QStatusBar,
    QToolBar, QSplitter, QDialog, QVBoxLayout as QVBoxLayoutDialog,
    QHBoxLayout as QHBoxLayoutDialog, QLabel, QPushButton
)
from PyQt5.QtCore import QTimer, QSettings, QFileSystemWatcher, Qt
from PyQt5.QtGui import QKeySequence, QIcon

from config import APP_NAME, ORG_NAME
from terminal import ProfessionalTerminal
from file_tree import FileTreeWidget
from editor import EditorTab
from widgets import ScrollableTabWidget

class CustomConfirmDialog(QDialog):
    def __init__(self, title, message, buttons, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(420, 200)
        self.setStyleSheet("""
            QDialog {
                background: #0a0e12;
                border: 2px solid #00ff66;
                border-radius: 12px;
            }
            QLabel {
                color: #00ff99;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton {
                background: #1a221a;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #116611;
            }
        """)
        layout = QVBoxLayoutDialog(self)
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        btn_layout = QHBoxLayoutDialog()
        for text, val in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=val: self._done(v))
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        self.result = None

    def _done(self, value):
        self.result = value
        self.accept()

    def exec_(self):
        super().exec_()
        return self.result

class MainWindow(QMainWindow):
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle(f"{APP_NAME} v1.0 - {os.path.basename(project_root)}")
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0e12;
            }
            QMenuBar {
                background: #0a0e12;
                color: #00ff99;
                border-bottom: 1px solid #00ff66;
            }
            QMenuBar::item:selected {
                background: #1a331a;
            }
            QMenu {
                background: #0a0e12;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: #116611;
            }
            QToolBar {
                background: #0a0e12;
                border-bottom: 1px solid #00ff66;
                spacing: 8px;
            }
            QToolButton {
                background: #1a221a;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 8px;
                padding: 5px 12px;
            }
            QToolButton:hover {
                background: #116611;
            }
            QStatusBar {
                background: #0a0e12;
                color: #00ff99;
                border-top: 1px solid #00ff66;
            }
            QSplitter::handle {
                background: #00ff66;
                width: 2px;
            }
        """)

        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.on_directory_changed)
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh)
        self._pending_dir = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.h_splitter = QSplitter(Qt.Horizontal)
        self.tree = FileTreeWidget(self)
        self.h_splitter.addWidget(self.tree)
        self.tree.setMinimumWidth(260)

        self.tabs = ScrollableTabWidget()
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.h_splitter.addWidget(self.tabs)
        self.h_splitter.setStretchFactor(1, 1)

        self.v_splitter = QSplitter(Qt.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        self.terminal = ProfessionalTerminal()
        self.terminal.setVisible(False)
        self.v_splitter.addWidget(self.terminal)
        self.v_splitter.setStretchFactor(0, 3)
        self.v_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.v_splitter)

        toolbar = self.addToolBar("Archivo")
        toolbar.setMovable(False)
        new_act = QAction("📄 Nuevo", self); new_act.setShortcut(QKeySequence.New); new_act.triggered.connect(self.new_file)
        open_act = QAction("📂 Abrir", self); open_act.setShortcut(QKeySequence.Open); open_act.triggered.connect(self.open_file)
        save_act = QAction("💾 Guardar", self); save_act.setShortcut(QKeySequence.Save); save_act.triggered.connect(self.save_current)
        saveas_act = QAction("📁 Guardar como", self); saveas_act.setShortcut(QKeySequence.SaveAs); saveas_act.triggered.connect(self.save_current_as)
        refresh_act = QAction("🔄 Refrescar", self); refresh_act.triggered.connect(self.refresh_file_tree)
        find_act = QAction("🔍 Buscar", self); find_act.setShortcut(QKeySequence.Find); find_act.triggered.connect(self.show_find)
        term_act = QAction(">_ Terminal", self); term_act.setShortcut("Ctrl+Shift+T"); term_act.triggered.connect(self.toggle_terminal)
        toolbar.addActions([new_act, open_act, save_act, saveas_act, refresh_act, find_act, term_act])

        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")
        file_menu.addActions([new_act, open_act, save_act, saveas_act])
        edit_menu = menubar.addMenu("Editar")
        edit_menu.addAction(find_act)
        view_menu = menubar.addMenu("Ver")
        view_menu.addAction(term_act)
        file_menu.addSeparator()
        change_proj = QAction("📂 Cambiar proyecto", self); change_proj.triggered.connect(self.change_project)
        file_menu.addAction(change_proj)
        file_menu.addSeparator()
        exit_act = QAction("Salir", self); exit_act.setShortcut(QKeySequence.Quit); exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(f"Proyecto: {self.project_root} | Ctrl+S guardar | Terminal: Ctrl+Shift+T")

        # NO HAY AUTOGUARDADO
        self.refresh_file_tree()
        self.add_directory_to_watcher(self.project_root)
        self.terminal.set_working_directory(self.project_root)
        self.new_file()

    # ========== Funciones auxiliares ==========
    def toggle_terminal(self):
        visible = self.terminal.isVisible()
        self.terminal.setVisible(not visible)
        if not visible:
            self.terminal.set_working_directory(self.project_root)

    def add_directory_to_watcher(self, path):
        if os.path.isdir(path) and path not in self.watcher.directories():
            self.watcher.addPath(path)

    def remove_directory_from_watcher(self, path):
        if path in self.watcher.directories():
            self.watcher.removePath(path)

    def on_directory_changed(self, path):
        if not os.path.exists(path):
            self.remove_directory_from_watcher(path)
            self._pending_dir = os.path.dirname(path) if os.path.exists(os.path.dirname(path)) else self.project_root
        else:
            self._pending_dir = path
        self._refresh_timer.start(300)

    def _do_refresh(self):
        if self._pending_dir:
            self.tree.refresh_directory_item(self._pending_dir)
            self._pending_dir = None

    def refresh_file_tree(self):
        self.tree.clear()
        if not os.path.exists(self.project_root):
            return
        from PyQt5.QtWidgets import QTreeWidgetItem
        root = QTreeWidgetItem(self.tree)
        root.setText(0, f"📁 {os.path.basename(self.project_root)}")
        root.setData(0, Qt.UserRole, 'dir')
        root.setData(0, Qt.UserRole + 1, self.project_root)
        self.tree.populate_tree(root, self.project_root, add_placeholder=True)
        root.setExpanded(True)
        self.add_directory_to_watcher(self.project_root)

    def open_file_from_path(self, path):
        if not os.path.isfile(path):
            return
        for i in range(self.tabs.count()):
            if getattr(self.tabs.widget(i), 'filepath', None) == path:
                self.tabs.setCurrentIndex(i)
                return
        editor = EditorTab(path)
        editor.modificationChanged.connect(lambda mod, idx=self.tabs.count(): self.update_tab_title(idx, editor))
        idx = self.tabs.addTab(editor, os.path.basename(path))
        self.tabs.setCurrentIndex(idx)

    def new_file(self):
        editor = EditorTab()
        editor.modificationChanged.connect(lambda mod, idx=self.tabs.count(): self.update_tab_title(idx, editor))
        idx = self.tabs.addTab(editor, "✨ Nuevo")
        self.tabs.setCurrentIndex(idx)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", self.project_root)
        if path:
            self.open_file_from_path(path)

    def save_current(self):
        editor = self.tabs.currentWidget()
        if editor and editor.save_file():
            idx = self.tabs.currentIndex()
            self.update_tab_title(idx, editor)
            self.status.showMessage("✅ Guardado", 2000)
            if editor.filepath:
                self.tree.refresh_directory_item(os.path.dirname(editor.filepath))

    def save_current_as(self):
        editor = self.tabs.currentWidget()
        if editor and editor.save_as():
            idx = self.tabs.currentIndex()
            self.update_tab_title(idx, editor)
            self.status.showMessage("✅ Guardado como", 2000)
            if editor.filepath:
                self.tree.refresh_directory_item(os.path.dirname(editor.filepath))

    def update_tab_title(self, index, editor):
        if editor.filepath:
            name = os.path.basename(editor.filepath)
        else:
            name = "✨ Nuevo"
        if editor.is_modified():
            name = f"* {name}"
        self.tabs.setTabText(index, name)

    def show_find(self):
        editor = self.tabs.currentWidget()
        if editor:
            editor.show_find()

    def close_tab(self, idx):
        editor = self.tabs.widget(idx)
        if not editor:
            return
        if editor.is_modified():
            dlg = CustomConfirmDialog(
                "Guardar cambios",
                f"¿Guardar los cambios en '{self.tabs.tabText(idx)}'?",
                [("Guardar", "save"), ("No guardar", "discard"), ("Cancelar", "cancel")]
            )
            result = dlg.exec_()
            if result == "save":
                if editor.save_file():
                    self.tabs.removeTab(idx)
                    editor.deleteLater()
            elif result == "discard":
                self.tabs.removeTab(idx)
                editor.deleteLater()
        else:
            self.tabs.removeTab(idx)
            editor.deleteLater()

    def change_project(self):
        modified_list = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor and editor.is_modified():
                modified_list.append(self.tabs.tabText(i))
        if modified_list:
            dlg = CustomConfirmDialog(
                "Guardar cambios",
                f"Hay {len(modified_list)} archivo(s) sin guardar.\n¿Guardar antes de cambiar de proyecto?",
                [("Guardar todo", "save"), ("No guardar", "discard"), ("Cancelar", "cancel")]
            )
            result = dlg.exec_()
            if result == "save":
                for i in range(self.tabs.count()):
                    editor = self.tabs.widget(i)
                    if editor and editor.is_modified() and editor.filepath:
                        editor.save_file()
            elif result == "cancel":
                return
        folder = QFileDialog.getExistingDirectory(self, "Nueva carpeta de proyecto")
        if folder:
            for d in self.watcher.directories():
                self.watcher.removePath(d)
            while self.tabs.count():
                self.tabs.removeTab(0)
            self.project_root = folder
            self.setWindowTitle(f"{APP_NAME} v1.0 - {os.path.basename(folder)}")
            self.refresh_file_tree()
            self.add_directory_to_watcher(folder)
            self.terminal.set_working_directory(folder)
            self.status.showMessage(f"Proyecto cambiado a: {folder}", 3000)
            self.new_file()

    def closeEvent(self, event):
        modified_list = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor and editor.is_modified():
                modified_list.append(self.tabs.tabText(i))
        if modified_list:
            dlg = CustomConfirmDialog(
                "Salir - Cambios sin guardar",
                f"Hay {len(modified_list)} archivo(s) sin guardar.\n¿Qué deseas hacer?",
                [("Guardar todo", "save"), ("No guardar", "discard"), ("Cancelar", "cancel")]
            )
            result = dlg.exec_()
            if result == "save":
                for i in range(self.tabs.count()):
                    editor = self.tabs.widget(i)
                    if editor and editor.is_modified() and editor.filepath:
                        editor.save_file()
                event.accept()
            elif result == "discard":
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()