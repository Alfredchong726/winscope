import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.ui.styles import TokyoNightTheme


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("Evidence Collection Tool")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("APU FYP")

    app.setStyleSheet(TokyoNightTheme.get_stylesheet())

    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
