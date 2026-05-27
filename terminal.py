# terminal.py
import sys
import os
import shlex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QTextCursor

class ProfessionalTerminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e12;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 12px;
                padding: 4px;
            }
        """)
        layout.addWidget(self.output)

        self.input_line = QLineEdit()
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #0a0e12;
                color: #00ff99;
                border: 1px solid #00ff66;
                border-radius: 6px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
                font-size: 12px;
                padding: 6px;
            }
        """)
        self.input_line.returnPressed.connect(self.execute_command)
        layout.addWidget(self.input_line)

        self.process = None
        self.current_dir = os.getcwd()
        self.prompt = "λ " if sys.platform != "win32" else "> "
        self.history = []
        self.history_index = 0

        self.append_output("\x1b[32m╔════════════════════════════════════════╗\x1b[0m\r\n")
        self.append_output(f"\x1b[32m║       KARION TERMINAL v1.0            ║\x1b[0m\r\n")
        self.append_output("\x1b[32m╚════════════════════════════════════════╝\x1b[0m\r\n")
        self.append_output(f"\r\n\x1b[36mCWD:\x1b[0m {self.current_dir}\r\n")
        self.append_output(self.prompt)

        self.input_line.installEventFilter(self)

    def append_output(self, text):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output.setTextCursor(cursor)
        self.output.insertPlainText(text)
        self.output.ensureCursorVisible()

    def eventFilter(self, obj, event):
        if obj == self.input_line and event.type() == event.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.history[self.history_index])
                return True
            elif key == Qt.Key_Down:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input_line.setText(self.history[self.history_index])
                else:
                    self.history_index = len(self.history)
                    self.input_line.clear()
                return True
        return super().eventFilter(obj, event)

    def execute_command(self):
        command = self.input_line.text().strip()
        if not command:
            self.input_line.clear()
            self.append_output(f"\r\n{self.prompt}")
            return

        self.history.append(command)
        self.history_index = len(self.history)
        self.append_output(f"\r\n\x1b[33m{command}\x1b[0m\r\n")

        if command.startswith("cd "):
            new_dir = command[3:].strip()
            if new_dir.startswith('"') and new_dir.endswith('"'):
                new_dir = new_dir[1:-1]
            try:
                os.chdir(new_dir)
                self.current_dir = os.getcwd()
                self.append_output(f"\x1b[36m-> {self.current_dir}\x1b[0m\r\n")
            except Exception as e:
                self.append_output(f"\x1b[31mError: {e}\x1b[0m\r\n")
            self.input_line.clear()
            self.append_output(self.prompt)
            return

        self.process = QProcess()
        self.process.setWorkingDirectory(self.current_dir)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)

        if sys.platform == "win32":
            self.process.start("cmd.exe", ["/c", command])
        else:
            args = shlex.split(command)
            if args:
                self.process.start(args[0], args[1:])
            else:
                self.on_finished()
        self.input_line.setEnabled(False)

    def on_stdout(self):
        data = self.process.readAllStandardOutput()
        if data:
            self.append_output(bytes(data).decode('utf-8', errors='replace'))

    def on_stderr(self):
        data = self.process.readAllStandardError()
        if data:
            self.append_output(bytes(data).decode('utf-8', errors='replace'))

    def on_finished(self):
        self.input_line.setEnabled(True)
        self.input_line.clear()
        self.append_output(self.prompt)

    def set_working_directory(self, path):
        if os.path.exists(path):
            self.current_dir = path
            os.chdir(path)
            self.append_output(f"\r\n\x1b[36mCWD -> {self.current_dir}\x1b[0m\r\n{self.prompt}")

    def clear(self):
        self.output.clear()
        self.append_output("\x1b[32m════════════════ KARION TERMINAL v1.0 ══════════════\x1b[0m\r\n")
        self.append_output(f"\x1b[36mCWD:\x1b[0m {self.current_dir}\r\n{self.prompt}")