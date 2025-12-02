import sys
from PyQt6.QtWidgets import QApplication


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Centralized Evidence Collection Tool")
    app.setApplicationVersion("0.1.0")

    # TODO: Initialize main window
    print("Application starting...")
    print("PyQt6 successfully imported!")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
