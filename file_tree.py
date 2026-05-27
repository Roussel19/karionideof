# file_tree.py
import os
import shutil
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt

class FileTreeWidget(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setHeaderHidden(True)
        self.setIndentation(12)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #0a0e12;
                color: #00ff99;
                border: none;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 3px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #1a331a;
                color: #00ffcc;
                border-left: 2px solid #00ff66;
            }
            QTreeWidget::item:hover {
                background-color: #1a2a1a;
            }
        """)
        self.itemDoubleClicked.connect(self.on_item_double_click)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemExpanded.connect(self.on_item_expanded)

    def on_item_expanded(self, item):
        path = item.data(0, Qt.UserRole + 1)
        if path and os.path.isdir(path):
            self.parent.add_directory_to_watcher(path)
            if item.childCount() == 1 and not item.child(0).data(0, Qt.UserRole + 1):
                item.takeChildren()
                self.populate_tree(item, path, add_placeholder=False)

    def show_context_menu(self, position):
        item = self.itemAt(position)
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #0a0e12;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #116611;
            }
        """)
        new_file = menu.addAction("📄 Nuevo archivo")
        new_folder = menu.addAction("📁 Nueva carpeta")
        delete = menu.addAction("🗑️ Eliminar")
        rename = menu.addAction("✏️ Renombrar")
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == new_file:
            self.create_new_file(item)
        elif action == new_folder:
            self.create_new_folder(item)
        elif action == delete:
            self.delete_item(item)
        elif action == rename:
            self.rename_item(item)

    def get_dir_path(self, item):
        if item is None:
            return self.parent.project_root
        if item.data(0, Qt.UserRole) == 'dir':
            return item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole + 1)
        if path and os.path.isfile(path):
            return os.path.dirname(path)
        return self.parent.project_root

    def create_new_file(self, parent_item):
        name, ok = QInputDialog.getText(self, "Nuevo archivo", "Nombre:")
        if ok and name:
            dir_path = self.get_dir_path(parent_item)
            filepath = os.path.join(dir_path, name)
            if os.path.exists(filepath):
                QMessageBox.warning(self, "Error", "Ya existe")
                return
            try:
                open(filepath, 'w').close()
                self.refresh_directory_item(dir_path)
                self.parent.open_file_from_path(filepath)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def create_new_folder(self, parent_item):
        name, ok = QInputDialog.getText(self, "Nueva carpeta", "Nombre:")
        if ok and name:
            dir_path = self.get_dir_path(parent_item)
            folder_path = os.path.join(dir_path, name)
            if os.path.exists(folder_path):
                QMessageBox.warning(self, "Error", "Ya existe")
                return
            try:
                os.mkdir(folder_path)
                self.refresh_directory_item(dir_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_item(self, item):
        path = item.data(0, Qt.UserRole + 1)
        if not path:
            return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar '{os.path.basename(path)}' permanentemente?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh_directory_item(os.path.dirname(path))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def rename_item(self, item):
        old_path = item.data(0, Qt.UserRole + 1)
        if not old_path:
            return
        new_name, ok = QInputDialog.getText(self, "Renombrar", "Nuevo nombre:", text=os.path.basename(old_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh_directory_item(os.path.dirname(new_path))
                for i in range(self.parent.tabs.count()):
                    editor = self.parent.tabs.widget(i)
                    if getattr(editor, 'filepath', None) == old_path:
                        editor.filepath = new_path
                        self.parent.update_tab_title(i, editor)
                        break
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def refresh_directory_item(self, dir_path):
        item = self.find_item_by_path(dir_path)
        if item:
            expanded = item.isExpanded()
            item.takeChildren()
            self.populate_tree(item, dir_path, add_placeholder=True)
            item.setExpanded(expanded)
        else:
            self.parent.refresh_file_tree()

    def find_item_by_path(self, target_path):
        def search(item):
            path = item.data(0, Qt.UserRole + 1) if item else None
            if path == target_path:
                return item
            for i in range(item.childCount()):
                found = search(item.child(i))
                if found:
                    return found
            return None
        root = self.topLevelItem(0)
        return search(root) if root else None

    def on_item_double_click(self, item, col):
        path = item.data(0, Qt.UserRole + 1)
        if path and os.path.isfile(path):
            self.parent.open_file_from_path(path)

    def populate_tree(self, parent_item, dir_path, add_placeholder=False):
        try:
            with os.scandir(dir_path) as it:
                entries = [e for e in it if not e.name.startswith('.') and e.name not in ('__pycache__', 'node_modules', '.git', 'venv', 'env', '.venv')]
            entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                full_path = entry.path
                name = entry.name
                item = QTreeWidgetItem(parent_item)
                if entry.is_dir():
                    item.setText(0, f"📁 {name}")
                    item.setData(0, Qt.UserRole, 'dir')
                    item.setData(0, Qt.UserRole + 1, full_path)
                    if add_placeholder:
                        item.addChild(QTreeWidgetItem())
                else:
                    icon = self.get_icon_for_file(name)
                    item.setText(0, f"{icon} {name}")
                    item.setData(0, Qt.UserRole, 'file')
                    item.setData(0, Qt.UserRole + 1, full_path)
        except PermissionError:
            pass

    def get_icon_for_file(self, name):
        ext = os.path.splitext(name)[1].lower()
        icons = {
            '.py': '🐍', '.pyx': '🐍', '.pyi': '🐍',
            '.js': '📜', '.mjs': '📜', '.cjs': '📜',
            '.html': '🌐', '.htm': '🌐',
            '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
            '.json': '📦', '.jsonc': '📦',
            '.c': '⚙️', '.h': '🔧', '.cpp': '⚙️', '.cc': '⚙️', '.cxx': '⚙️', '.hpp': '🔧', '.hh': '🔧',
            '.java': '☕', '.class': '☕',
            '.cs': '🎯', '.csx': '🎯',
            '.go': '🏃', '.gohtml': '🏃',
            '.rb': '💎', '.erb': '💎',
            '.php': '🐘', '.phtml': '🐘',
            '.swift': '🦅', '.kt': '🎯', '.kts': '🎯',
            '.rs': '🦀', '.rlib': '🦀',
            '.ts': '📘', '.tsx': '📘',
            '.sh': '🐚', '.bash': '🐚', '.zsh': '🐚',
            '.md': '📝', '.txt': '📄', '.xml': '🔖', '.yml': '⚓', '.yaml': '⚓',
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.mp3': '🎵', '.mp4': '🎬', '.wav': '🎵',
        }
        return icons.get(ext, '📄')