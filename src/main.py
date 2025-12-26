import sys
from PyQt6.QtWidgets import QApplication
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.ui.styles import TokyoNightTheme
from src.services.logger import get_logger


def get_application_path() -> Path:
    if getattr(sys, "frozen", False):
        application_path = Path(sys._MEIPASS)
    else:
        application_path = Path(__file__).parent.parent

    return application_path


def main():
    app_path = get_application_path()

    logger = get_logger()
    logger.info(f"Application path: {app_path}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")

    app = QApplication(sys.argv)

    app.setApplicationName("WinScope")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("APU FYP")

    app.setStyleSheet(TokyoNightTheme.get_stylesheet())

    icon_path = app_path / "resources/icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()

    logger.info("WinScope started successfully")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
