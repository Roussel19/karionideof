# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSettings

from config import APP_NAME, ORG_NAME
from mainwindow import MainWindow
from widgets import WelcomeDialog

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-sync --disable-default-apps --disable-extensions"
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    app.setWindowIcon(QIcon(resource_path("logo.ico")))

    settings = QSettings(ORG_NAME, APP_NAME)
    last_project = settings.value("last_project", "")
    if last_project and os.path.exists(last_project):
        project = last_project
    else:
        dlg = WelcomeDialog()
        if dlg.exec_() == QDialog.Accepted:
            project = dlg.get_path()
            if not project or not os.path.exists(project):
                project = os.path.expanduser("~")
        else:
            sys.exit(0)

    settings.setValue("last_project", project)
    window = MainWindow(project)
    window.setWindowIcon(QIcon(resource_path("logo.ico")))
    window.show()
    sys.exit(app.exec_())