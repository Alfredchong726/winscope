from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.ui.module_info import ModuleInfo
from src.ui.styles import TokyoNightTheme


class ModuleCard(QFrame):
    toggled = pyqtSignal(str, bool)
    info_requested = pyqtSignal(str)

    def __init__(self, module_info: ModuleInfo, parent=None):
        super().__init__(parent)
        self.module_info = module_info
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()

        # Icon
        icon_label = QLabel(self.module_info.icon)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)

        name_label = QLabel(self.module_info.name)
        name_label.setObjectName("header")
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.module_info.enabled_by_default)
        self.checkbox.stateChanged.connect(self._on_toggle)
        header_layout.addWidget(self.checkbox)

        layout.addLayout(header_layout)

        desc_label = QLabel(self.module_info.description)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("subtitle")
        layout.addWidget(desc_label)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(16)

        time_label = QLabel(f"⏱️ {self.module_info.estimated_time}")
        time_label.setObjectName("subtitle")
        info_layout.addWidget(time_label)

        storage_label = QLabel(f"💿 {self.module_info.storage_required}")
        storage_label.setObjectName("subtitle")
        info_layout.addWidget(storage_label)

        if self.module_info.requires_admin:
            admin_label = QLabel("🔒 Requires Admin")
            admin_label.setStyleSheet(f"color: {TokyoNightTheme.YELLOW};")
            info_layout.addWidget(admin_label)

        info_layout.addStretch()

        info_btn = QPushButton("ℹ️")
        info_btn.setMaximumWidth(32)
        info_btn.setToolTip("Show detailed information")
        info_btn.clicked.connect(lambda: self.info_requested.emit(self.module_info.id))
        info_layout.addWidget(info_btn)
        layout.addLayout(info_layout)

        category_label = QLabel(f"📦 {self.module_info.category.upper()}")
        category_label.setObjectName("subtitle")
        category_label.setStyleSheet(f"""
            background-color: {TokyoNightTheme.BG_HIGHLIGHT};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 8pt;
        """)
        layout.addWidget(category_label, alignment=Qt.AlignmentFlag.AlignLeft)

    def _on_toggle(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self.module_info.id, is_checked)

    def set_enabled(self, enabled: bool):
        self.checkbox.setEnabled(enabled)
        self.setEnabled(enabled)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)

class LogViewer(QTextEdit):
    MAX_LINES = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.line_count = 0

    def _setup_ui(self):
        self.setObjectName("logViewer")

        self.setReadOnly(True)

        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.setFont(font)

        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

    def append_log(self, message: str, level: str = "INFO"):
        from datetime import datetime
        from src.ui.styles import LogColors, TokyoNightTheme

        color_map = {
            "DEBUG": LogColors.DEBUG,
            "INFO": LogColors.INFO,
            "SUCCESS": LogColors.SUCCESS,
            "WARNING": LogColors.WARNING,
            "ERROR": LogColors.ERROR
        }
        message_color = color_map.get(level.upper(), LogColors.INFO)

        timestamp = datetime.now().strftime("%H:%M:%S")

        html_parts = []
        html_parts.append(f'<span style="color: {LogColors.TIMESTAMP};">[{timestamp}]</span>')
        html_parts.append(f'<span style="color: {message_color}; font-weight: bold;"> {level}:</span>')
        html_parts.append(f'<span style="color: {TokyoNightTheme.FG_DEFAULT};"> {message}</span>')

        html = " ".join(html_parts)

        self.append(html)
        self.line_count += 1

        self._trim_old_lines()

        self._scroll_to_bottom()

    def _trim_old_lines(self):
        if self.line_count > self.MAX_LINES:
            lines_to_remove = self.line_count - self.MAX_LINES

            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)

            cursor.movePosition(
                cursor.MoveOperation.Down,
                cursor.MoveMode.KeepAnchor,
                lines_to_remove
            )

            cursor.removeSelectedText()

            self.line_count = self.MAX_LINES

    def _scroll_to_bottom(self):
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        self.clear()
        self.line_count = 0

    def append_separator(self):
        separator = '<span style="color: {color};">{line}</span>'.format(
            color=TokyoNightTheme.BORDER,
            line="─" * 80
        )
        self.append(separator)


class StatusCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("header")

        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        main_layout.addWidget(self.title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        main_layout.addLayout(self.content_layout)

        main_layout.addStretch()

    def add_info_row(self, label: str, value: str, value_color: str = None):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        label_widget = QLabel(f"{label}:")
        label_widget.setObjectName("subtitle")

        label_font = QFont()
        label_font.setPointSize(9)
        label_widget.setFont(label_font)

        row_layout.addWidget(label_widget)

        value_widget = QLabel(value)

        value_font = QFont()
        value_font.setPointSize(9)

        if value_color:
            value_widget.setStyleSheet(
                f"color: {value_color}; font-weight: bold;"
            )
            value_font.setBold(True)

        value_widget.setFont(value_font)
        row_layout.addWidget(value_widget)

        row_layout.addStretch()

        self.content_layout.addLayout(row_layout)

    def add_custom_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)

    def clear_content(self):
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def update_title(self, new_title: str):
        self.title = new_title
        self.title_label.setText(new_title)

    def set_highlighted(self, highlighted: bool):
        if highlighted:
            self.setStyleSheet(f"""
                QFrame#card {{
                    border: 2px solid {TokyoNightTheme.BLUE};
                    background-color: {TokyoNightTheme.BG_HIGHLIGHT};
                }}
            """)
        else:
            self.setStyleSheet("")
