# editor.py
import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, pyqtSignal, QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtGui import QColor
from config import EXT_TO_LANG

# HTML completo con fondo oscuro explícito y carga optimizada
MONACO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body, html { 
            margin: 0; 
            padding: 0; 
            height: 100%; 
            background-color: #0a0e12; 
            overflow: hidden; 
        }
        #editor-container { 
            height: 100%; 
            width: 100%; 
            background-color: #0a0e12; 
        }
    </style>
    <link rel="stylesheet" data-name="vs/editor/editor.main" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.34.1/min/vs/editor/editor.main.min.css">
    <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.34.1/min/vs/loader.js"></script>
</head>
<body>
    <div id="editor-container"></div>
    <script>
        require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.34.1/min/vs' } });
        let editor = null;
        require(['vs/editor/editor.main'], function () {
            editor = monaco.editor.create(document.getElementById('editor-container'), {
                value: '# KarionIDE v1.0\\nprint("Ready")\\n',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 13,
                fontFamily: 'Cascadia Code, Consolas, monospace',
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                cursorBlinking: 'smooth'
            });
            monaco.editor.defineTheme('karion-dark', {
                base: 'vs-dark',
                inherit: true,
                rules: [
                    { token: 'keyword', foreground: '00ffaa', fontStyle: 'bold' },
                    { token: 'string', foreground: 'aaffaa' },
                    { token: 'number', foreground: '77ffcc' },
                    { token: 'comment', foreground: '44aa44', fontStyle: 'italic' },
                    { token: 'variable', foreground: 'ccffcc' },
                    { token: 'type', foreground: '88ffaa' },
                    { token: 'function', foreground: '88ffaa' },
                    { token: 'operator', foreground: '00ff88' }
                ],
                colors: {
                    'editor.background': '#0a0e12',
                    'editor.lineHighlightBackground': '#1a2a1a',
                    'editorCursor.foreground': '#00ff66',
                    'editorLineNumber.foreground': '#00aa55',
                    'editorLineNumber.activeForeground': '#00ff99',
                    'editor.selectionBackground': '#226622',
                    'editor.findMatchBackground': '#115511'
                }
            });
            monaco.editor.setTheme('karion-dark');
            editor.focus();
            window.getEditorContent = function() { return editor.getValue(); };
            window.setEditorContent = function(content) { editor.setValue(content); };
            window.setLanguage = function(lang) { monaco.editor.setModelLanguage(editor.getModel(), lang); };
            window.showFindWidget = function() { editor.getAction('actions.find').run(); };
        });
    </script>
</body>
</html>
"""

class EditorTab(QWidget):
    modificationChanged = pyqtSignal(bool)

    def __init__(self, filepath=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Fondo oscuro en el widget contenedor
        self.setStyleSheet("background-color: #0a0e12;")
        
        self.browser = QWebEngineView()
        # Establecer fondo oscuro en la página ANTES de cargar cualquier contenido
        self.browser.page().setBackgroundColor(QColor(10, 14, 18))  # #0a0e12
        self.browser.setStyleSheet("background-color: #0a0e12; border: none;")
        
        self.filepath = filepath
        self._ready = False
        self._modified = False
        self._last_saved_content = ""

        # Configuración de alto rendimiento
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.NoCache)
        profile.setPersistentStoragePath("")
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, False)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)

        self.browser.setHtml(MONACO_HTML)
        self.browser.loadFinished.connect(self.on_load_finished)
        layout.addWidget(self.browser)

    def on_load_finished(self, ok):
        if ok:
            self._ready = True
            if self.filepath:
                self.open_file(self.filepath)
            else:
                default = '# KarionIDE v1.0\nprint("Ready")\n'
                self.set_content(default)
                self._last_saved_content = default
                self._modified = False
            # Polling cada 800ms para detectar cambios
            self._poll_timer = QTimer()
            self._poll_timer.timeout.connect(self.check_changes)
            self._poll_timer.start(800)

    def check_changes(self):
        if not self._ready:
            return
        current = self.get_content_sync()
        if current is None:
            return
        changed = (current != self._last_saved_content)
        if changed and not self._modified:
            self._modified = True
            self.modificationChanged.emit(True)
        elif not changed and self._modified:
            self._modified = False
            self.modificationChanged.emit(False)

    def open_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.set_content(content)
            self.filepath = path
            self._last_saved_content = content
            self._modified = False
            ext = os.path.splitext(path)[1].lower()
            lang = EXT_TO_LANG.get(ext, 'python')
            self.set_language(lang)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir:\n{e}")

    def save_file(self):
        if not self._ready:
            return False
        if not self.filepath:
            return self.save_as()
        try:
            content = self.get_content_sync()
            if content is None:
                return False
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self._last_saved_content = content
            self._modified = False
            self.modificationChanged.emit(False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Guardar falló:\n{e}")
            return False

    def save_as(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Código (*.py *.js *.html *.css *.json *.c *.cpp *.java);;Todos (*.*)")
        if path:
            self.filepath = path
            return self.save_file()
        return False

    def get_content_sync(self, timeout=2000):
        if not self._ready:
            return ""
        self._content = None
        loop = QEventLoop()
        def callback(res):
            self._content = res
            loop.quit()
        self.browser.page().runJavaScript("window.getEditorContent();", callback)
        QTimer.singleShot(timeout, loop.quit)
        loop.exec_()
        return self._content or ""

    def set_content(self, text):
        if self._ready:
            escaped = json.dumps(text)
            self.browser.page().runJavaScript(f"window.setEditorContent({escaped});")

    def set_language(self, lang):
        if self._ready:
            self.browser.page().runJavaScript(f"window.setLanguage('{lang}');")

    def is_modified(self):
        return self._modified

    def show_find(self):
        if self._ready:
            self.browser.page().runJavaScript("window.showFindWidget();")