# config.py
import sys
import os

APP_NAME = "KarionIDE"
ORG_NAME = "Karion"
VERSION = "1.0"

# NO hay AUTOSAVE_INTERVAL porque se ha eliminado el autoguardado
DEBOUNCE_INTERVAL = 100  # No se usa, pero lo dejamos por si acaso

EXT_TO_LANG = {
    '.py': 'python',
    '.js': 'javascript',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.hpp': 'cpp',
    '.java': 'java',
    '.cs': 'csharp',
    '.go': 'go',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.rs': 'rust',
    '.ts': 'typescript'
}