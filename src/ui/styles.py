class TokyoNightTheme:
    BG_DARK = "#1a1b26"
    BG_DARKER = "#16161e"
    BG_LIGHT = "#24283b"
    BG_HIGHLIGHT = "#292e42"

    FG_PRIMARY = "#c0caf5"
    FG_SECONDARY = "#9aa5ce"
    FG_DARK = "#565f89"

    BLUE = "#7aa2f7"
    CYAN = "#7dcfff"
    GREEN = "#9ece6a"
    YELLOW = "#e0af68"
    ORANGE = "#ff9e64"
    RED = "#f7768e"
    MAGENTA = "#bb9af7"

    BORDER = "#414868"
    SELECTION = "#3d59a1"

    @staticmethod
    def get_stylesheet() -> str:
        return f"""
QWidget {{
    background-color: {TokyoNightTheme.BG_DARK};
    color: {TokyoNightTheme.FG_PRIMARY};
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 10pt;
}}

QMainWindow {{
    background-color: {TokyoNightTheme.BG_DARK};
}}

QPushButton {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {TokyoNightTheme.BG_HIGHLIGHT};
    border-color: {TokyoNightTheme.BLUE};
}}

QPushButton:pressed {{
    background-color: {TokyoNightTheme.BG_DARKER};
}}

QPushButton:disabled {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_DARK};
    border-color: {TokyoNightTheme.BG_HIGHLIGHT};
}}

QPushButton#primaryButton {{
    background-color: {TokyoNightTheme.BLUE};
    color: {TokyoNightTheme.BG_DARK};
    font-weight: bold;
    border: none;
}}

QPushButton#primaryButton:hover {{
    background-color: {TokyoNightTheme.CYAN};
}}

QPushButton#primaryButton:pressed {{
    background-color: {TokyoNightTheme.SELECTION};
}}

QPushButton#dangerButton {{
    background-color: {TokyoNightTheme.RED};
    color: {TokyoNightTheme.BG_DARK};
    border: none;
}}

QPushButton#dangerButton:hover {{
    background-color: #ff5370;
}}

QCheckBox {{
    color: {TokyoNightTheme.FG_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {TokyoNightTheme.BORDER};
    border-radius: 3px;
    background-color: {TokyoNightTheme.BG_LIGHT};
}}

QCheckBox::indicator:hover {{
    border-color: {TokyoNightTheme.BLUE};
}}

QCheckBox::indicator:checked {{
    background-color: {TokyoNightTheme.BLUE};
    border-color: {TokyoNightTheme.BLUE};
    image: url(none);
}}

QCheckBox:disabled {{
    color: {TokyoNightTheme.FG_DARK};
}}

QRadioButton {{
    color: {TokyoNightTheme.FG_PRIMARY};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {TokyoNightTheme.BORDER};
    border-radius: 9px;
    background-color: {TokyoNightTheme.BG_LIGHT};
}}

QRadioButton::indicator:checked {{
    background-color: {TokyoNightTheme.BLUE};
    border-color: {TokyoNightTheme.BLUE};
}}

QLineEdit {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    selection-background-color: {TokyoNightTheme.SELECTION};
}}

QLineEdit:focus {{
    border-color: {TokyoNightTheme.BLUE};
}}

QLineEdit:disabled {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_DARK};
}}

QTextEdit, QPlainTextEdit {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    padding: 8px;
    selection-background-color: {TokyoNightTheme.SELECTION};
}}

QProgressBar {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TokyoNightTheme.FG_PRIMARY};
    height: 24px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {TokyoNightTheme.BLUE},
        stop:1 {TokyoNightTheme.CYAN}
    );
    border-radius: 3px;
}}

QLabel {{
    color: {TokyoNightTheme.FG_PRIMARY};
    background-color: transparent;
}}

QLabel#headerLabel {{
    font-size: 14pt;
    font-weight: bold;
    color: {TokyoNightTheme.BLUE};
}}

QLabel#subHeaderLabel {{
    font-size: 11pt;
    font-weight: bold;
    color: {TokyoNightTheme.CYAN};
}}

QLabel#infoLabel {{
    color: {TokyoNightTheme.FG_SECONDARY};
    font-size: 9pt;
}}

QGroupBox {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    color: {TokyoNightTheme.CYAN};
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {TokyoNightTheme.BORDER};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TokyoNightTheme.BLUE};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {TokyoNightTheme.BORDER};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {TokyoNightTheme.BLUE};
}}

QComboBox {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {TokyoNightTheme.BLUE};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {TokyoNightTheme.FG_PRIMARY};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    selection-background-color: {TokyoNightTheme.SELECTION};
    outline: none;
}}

QListWidget {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 8px;
    border-radius: 3px;
}}

QListWidget::item:hover {{
    background-color: {TokyoNightTheme.BG_HIGHLIGHT};
}}

QListWidget::item:selected {{
    background-color: {TokyoNightTheme.SELECTION};
}}

QToolTip {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
}}

QStatusBar {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_SECONDARY};
    border-top: 1px solid {TokyoNightTheme.BORDER};
}}

QMenuBar {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_PRIMARY};
    border-bottom: 1px solid {TokyoNightTheme.BORDER};
}}

QMenuBar::item {{
    padding: 6px 12px;
    background-color: transparent;
}}

QMenuBar::item:selected {{
    background-color: {TokyoNightTheme.BG_HIGHLIGHT};
}}

QMenu {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.FG_PRIMARY};
    border: 1px solid {TokyoNightTheme.BORDER};
}}

QMenu::item {{
    padding: 8px 30px 8px 20px;
}}

QMenu::item:selected {{
    background-color: {TokyoNightTheme.SELECTION};
}}

QFrame[frameShape="4"], /* HLine */
QFrame[frameShape="5"]  /* VLine */
{{
    background-color: {TokyoNightTheme.BORDER};
}}

QTabWidget::pane {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    border: 1px solid {TokyoNightTheme.BORDER};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {TokyoNightTheme.BG_DARKER};
    color: {TokyoNightTheme.FG_SECONDARY};
    border: 1px solid {TokyoNightTheme.BORDER};
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {TokyoNightTheme.BG_LIGHT};
    color: {TokyoNightTheme.BLUE};
}}

QTabBar::tab:hover {{
    background-color: {TokyoNightTheme.BG_HIGHLIGHT};
}}
        """

LOG_COLORS = {
    "DEBUG": TokyoNightTheme.FG_SECONDARY,
    "INFO": TokyoNightTheme.CYAN,
    "WARNING": TokyoNightTheme.YELLOW,
    "ERROR": TokyoNightTheme.RED,
    "CRITICAL": TokyoNightTheme.MAGENTA,
    "SUCCESS": TokyoNightTheme.GREEN,
}
