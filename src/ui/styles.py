class TokyoNightTheme:
    BG_DARK = "#24283b"
    BG_DARKER = "#1a1b26"
    BG_LIGHT = "#292e42"
    BG_HIGHLIGHT = "#3b4261"

    FG_DEFAULT = "#c0caf5"
    FG_DARK = "#9aa5ce"
    FG_LIGHT = "#ffffff"

    BLUE = "#7aa2f7"
    CYAN = "#7dcfff"
    GREEN = "#9ece6a"
    YELLOW = "#e0af68"
    ORANGE = "#ff9e64"
    RED = "#f7768e"
    PURPLE = "#bb9af7"
    MAGENTA = "#c678dd"

    BORDER = "#414868"
    BORDER_LIGHT = "#545c7e"

    BUTTON_PRIMARY = "#7aa2f7"
    BUTTON_SUCCESS = "#9ece6a"
    BUTTON_DANGER = "#f7768e"
    BUTTON_HOVER = "#89b4fa"

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
        QWidget {{
            background-color: {cls.BG_DARK};
            color: {cls.FG_DEFAULT};
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 10pt;
        }}

        QMainWindow {{
            background-color: {cls.BG_DARK};
        }}

        QLabel {{
            color: {cls.FG_DEFAULT};
            background-color: transparent;
            border: none;
        }}

        QLabel#header {{
            font-size: 14pt;
            font-weight: bold;
            color: {cls.FG_LIGHT};
        }}

        QLabel#subtitle {{
            font-size: 9pt;
            color: {cls.FG_DARK};
        }}

        QPushButton {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 28px;
        }}

        QPushButton:hover {{
            background-color: {cls.BG_HIGHLIGHT};
            border-color: {cls.BORDER_LIGHT};
        }}

        QPushButton:pressed {{
            background-color: {cls.BG_DARKER};
        }}

        QPushButton:disabled {{
            background-color: {cls.BG_DARK};
            color: {cls.FG_DARK};
            border-color: {cls.BORDER};
        }}

        QPushButton#primary {{
            background-color: {cls.BUTTON_PRIMARY};
            color: {cls.FG_LIGHT};
            border: none;
            font-weight: bold;
        }}

        QPushButton#primary:hover {{
            background-color: {cls.BUTTON_HOVER};
        }}

        QPushButton#primary:pressed {{
            background-color: {cls.BLUE};
        }}

        QPushButton#success {{
            background-color: {cls.BUTTON_SUCCESS};
            color: {cls.BG_DARK};
            border: none;
            font-weight: bold;
        }}

        QPushButton#success:hover {{
            background-color: {cls.GREEN};
        }}

        QPushButton#danger {{
            background-color: {cls.BUTTON_DANGER};
            color: {cls.FG_LIGHT};
            border: none;
            font-weight: bold;
        }}

        QPushButton#danger:hover {{
            background-color: {cls.RED};
        }}

        QCheckBox {{
            color: {cls.FG_DEFAULT};
            spacing: 8px;
            padding: 4px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {cls.BORDER};
            border-radius: 4px;
            background-color: {cls.BG_LIGHT};
        }}

        QCheckBox::indicator:hover {{
            border-color: {cls.BORDER_LIGHT};
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QCheckBox::indicator:checked {{
            background-color: {cls.BLUE};
            border-color: {cls.BLUE};
            image: url(none); /* Will add checkmark icon later */
        }}

        QCheckBox::indicator:checked {{
            background-color: {cls.BLUE};
            border-color: {cls.BLUE};
        }}

        QCheckBox:disabled {{
            color: {cls.FG_DARK};
        }}

        QRadioButton {{
            color: {cls.FG_DEFAULT};
            spacing: 8px;
            padding: 4px;
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {cls.BORDER};
            border-radius: 9px;
            background-color: {cls.BG_LIGHT};
        }}

        QRadioButton::indicator:hover {{
            border-color: {cls.BORDER_LIGHT};
        }}

        QRadioButton::indicator:checked {{
            background-color: {cls.BLUE};
            border-color: {cls.BLUE};
        }}

        QLineEdit {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: {cls.BLUE};
        }}

        QLineEdit:focus {{
            border-color: {cls.BLUE};
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QLineEdit:disabled {{
            background-color: {cls.BG_DARK};
            color: {cls.FG_DARK};
        }}

        QTextEdit, QPlainTextEdit {{
            background-color: {cls.BG_DARKER};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {cls.BLUE};
        }}

        QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {cls.BLUE};
        }}

        QComboBox {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 6px 12px;
            min-height: 28px;
        }}

        QComboBox:hover {{
            border-color: {cls.BORDER_LIGHT};
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QComboBox:focus {{
            border-color: {cls.BLUE};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.FG_DEFAULT};
            margin-right: 8px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            selection-background-color: {cls.BLUE};
            selection-color: {cls.FG_LIGHT};
            outline: none;
        }}

        QProgressBar {{
            background-color: {cls.BG_LIGHT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            text-align: center;
            color: {cls.FG_DEFAULT};
            height: 24px;
        }}

        QProgressBar::chunk {{
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {cls.BLUE},
                stop:1 {cls.CYAN}
            );
            border-radius: 5px;
        }}

        QScrollBar:vertical {{
            background-color: {cls.BG_DARK};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.BG_HIGHLIGHT};
            border-radius: 6px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.BORDER_LIGHT};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background-color: {cls.BG_DARK};
            height: 12px;
            border-radius: 6px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {cls.BG_HIGHLIGHT};
            border-radius: 6px;
            min-width: 30px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.BORDER_LIGHT};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        QGroupBox {{
            background-color: {cls.BG_LIGHT};
            border: 1px solid {cls.BORDER};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 500;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 8px;
            color: {cls.BLUE};
            font-weight: bold;
        }}

        QTabWidget::pane {{
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            background-color: {cls.BG_DARK};
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DARK};
            border: 1px solid {cls.BORDER};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 20px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.BG_DARK};
            color: {cls.BLUE};
            font-weight: bold;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QToolTip {{
            background-color: {cls.BG_HIGHLIGHT};
            color: {cls.FG_LIGHT};
            border: 1px solid {cls.BORDER_LIGHT};
            border-radius: 4px;
            padding: 6px;
            font-size: 9pt;
        }}

        QMenuBar {{
            background-color: {cls.BG_DARKER};
            color: {cls.FG_DEFAULT};
            border-bottom: 1px solid {cls.BORDER};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
        }}

        QMenuBar::item:selected {{
            background-color: {cls.BG_HIGHLIGHT};
            color: {cls.FG_LIGHT};
        }}

        QMenu {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 6px 24px 6px 12px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {cls.BG_HIGHLIGHT};
            color: {cls.FG_LIGHT};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {cls.BORDER};
            margin: 4px 8px;
        }}

        QStatusBar {{
            background-color: {cls.BG_DARKER};
            color: {cls.FG_DEFAULT};
            border-top: 1px solid {cls.BORDER};
        }}

        QListWidget {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            padding: 4px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 8px;
            border-radius: 4px;
        }}

        QListWidget::item:selected {{
            background-color: {cls.BLUE};
            color: {cls.FG_LIGHT};
        }}

        QListWidget::item:hover:!selected {{
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QTreeWidget {{
            background-color: {cls.BG_LIGHT};
            color: {cls.FG_DEFAULT};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            outline: none;
        }}

        QTreeWidget::item {{
            padding: 4px;
        }}

        QTreeWidget::item:selected {{
            background-color: {cls.BLUE};
            color: {cls.FG_LIGHT};
        }}

        QTreeWidget::item:hover:!selected {{
            background-color: {cls.BG_HIGHLIGHT};
        }}

        QTreeWidget::branch {{
            background-color: transparent;
        }}

        QSplitter::handle {{
            background-color: {cls.BORDER};
        }}

        QSplitter::handle:hover {{
            background-color: {cls.BORDER_LIGHT};
        }}

        QDialog {{
            background-color: {cls.BG_DARK};
        }}

        QMessageBox {{
            background-color: {cls.BG_DARK};
        }}

        QMessageBox QLabel {{
            color: {cls.FG_DEFAULT};
        }}

        QFrame#sidebar {{
            background-color: {cls.BG_DARKER};
            border-right: 1px solid {cls.BORDER};
        }}

        QTextEdit#logViewer {{
            background-color: {cls.BG_DARKER};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 9pt;
        }}

        QFrame#card {{
            background-color: {cls.BG_LIGHT};
            border: 1px solid {cls.BORDER};
            border-radius: 8px;
            padding: 12px;
        }}

        QLabel#success {{
            color: {cls.GREEN};
            font-weight: bold;
        }}

        QLabel#warning {{
            color: {cls.YELLOW};
            font-weight: bold;
        }}

        QLabel#error {{
            color: {cls.RED};
            font-weight: bold;
        }}

        QLabel#info {{
            color: {cls.BLUE};
            font-weight: bold;
        }}
        """

class LogColors:
    DEBUG = TokyoNightTheme.FG_DARK
    INFO = TokyoNightTheme.CYAN
    SUCCESS = TokyoNightTheme.GREEN
    WARNING = TokyoNightTheme.YELLOW
    ERROR = TokyoNightTheme.RED
    TIMESTAMP = TokyoNightTheme.PURPLE
