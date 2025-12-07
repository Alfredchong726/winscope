"""
测试UI组件

文件位置: 项目根目录/test_ui_components.py

用途:
- 测试自定义widget是否正常工作
- 预览Tokyo Night主题效果
- 验证组件交互功能
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QProgressBar
)
from PyQt6.QtCore import QTimer
from src.ui.widgets import ModuleCard, LogViewer, StatusCard
from src.ui.module_info import ModuleRegistry
from src.ui.styles import TokyoNightTheme


class TestWindow(QMainWindow):
    """测试窗口类。"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_test_timer()

    def setup_ui(self):
        """配置UI。"""
        self.setWindowTitle("Evidence Collector - UI Components Test")
        self.setGeometry(100, 100, 1000, 700)

        # 中央widget
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # ===== 左侧：模块卡片 =====
        left_layout = QVBoxLayout()

        # 状态卡片
        self.status_card = StatusCard("System Information")
        self.status_card.add_info_row("Hostname", "DESKTOP-TEST")
        self.status_card.add_info_row("IP Address", "192.168.1.100")
        self.status_card.add_info_row("OS Version", "Windows 11 Pro")
        self.status_card.add_info_row(
            "Status",
            "Ready",
            TokyoNightTheme.GREEN
        )
        left_layout.addWidget(self.status_card)

        # 模块卡片滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        # 添加前4个模块卡片
        for module in ModuleRegistry.get_all_modules()[:4]:
            card = ModuleCard(module)
            card.toggled.connect(
                lambda mid, checked: self.on_module_toggled(mid, checked)
            )
            card.info_requested.connect(
                lambda mid: self.on_info_requested(mid)
            )
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        left_layout.addWidget(scroll, 1)

        main_layout.addLayout(left_layout, 1)

        # ===== 右侧：日志和控制 =====
        right_layout = QVBoxLayout()

        # 统计卡片
        self.stats_card = StatusCard("Collection Statistics")
        self.stats_card.add_info_row("Files Collected", "0")
        self.stats_card.add_info_row("Total Size", "0 MB")
        self.stats_card.add_info_row("Duration", "0:00")
        right_layout.addWidget(self.stats_card)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        right_layout.addWidget(self.progress_bar)

        # 测试按钮
        button_layout = QHBoxLayout()

        self.test_info_btn = QPushButton("Test INFO Log")
        self.test_info_btn.setObjectName("primary")
        self.test_info_btn.clicked.connect(self.add_info_log)
        button_layout.addWidget(self.test_info_btn)

        self.test_success_btn = QPushButton("Test SUCCESS Log")
        self.test_success_btn.setObjectName("success")
        self.test_success_btn.clicked.connect(self.add_success_log)
        button_layout.addWidget(self.test_success_btn)

        self.test_error_btn = QPushButton("Test ERROR Log")
        self.test_error_btn.setObjectName("danger")
        self.test_error_btn.clicked.connect(self.add_error_log)
        button_layout.addWidget(self.test_error_btn)

        right_layout.addLayout(button_layout)

        # 日志查看器
        self.log_viewer = LogViewer()
        self.log_viewer.append_log("Application initialized", "SUCCESS")
        self.log_viewer.append_log("Loading modules...", "INFO")
        self.log_viewer.append_separator()
        right_layout.addWidget(self.log_viewer, 1)

        # 清空日志按钮
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.log_viewer.clear_logs)
        right_layout.addWidget(clear_btn)

        main_layout.addLayout(right_layout, 1)

        self.setCentralWidget(central)

    def setup_test_timer(self):
        """设置测试定时器，模拟进度。"""
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # 每100ms更新一次

    def update_progress(self):
        """更新进度条。"""
        self.progress += 1
        if self.progress > 100:
            self.progress = 0

        self.progress_bar.setValue(self.progress)

        # 更新统计
        files = self.progress * 10
        size = self.progress * 2.5
        duration = f"0:{self.progress:02d}"

        self.stats_card.clear_content()
        self.stats_card.add_info_row("Files Collected", str(files))
        self.stats_card.add_info_row("Total Size", f"{size:.1f} MB")
        self.stats_card.add_info_row("Duration", duration)

    def on_module_toggled(self, module_id: str, checked: bool):
        """处理模块复选框切换。"""
        status = "enabled" if checked else "disabled"
        self.log_viewer.append_log(
            f"Module '{module_id}' {status}",
            "INFO"
        )

    def on_info_requested(self, module_id: str):
        """处理信息请求。"""
        self.log_viewer.append_log(
            f"Showing info for module '{module_id}'",
            "INFO"
        )

    def add_info_log(self):
        """添加INFO日志。"""
        self.log_viewer.append_log(
            "This is an informational message",
            "INFO"
        )

    def add_success_log(self):
        """添加SUCCESS日志。"""
        self.log_viewer.append_log(
            "Operation completed successfully!",
            "SUCCESS"
        )

    def add_error_log(self):
        """添加ERROR日志。"""
        self.log_viewer.append_log(
            "An error occurred during the operation",
            "ERROR"
        )


def main():
    """主函数。"""
    app = QApplication(sys.argv)

    # 应用Tokyo Night主题
    app.setStyleSheet(TokyoNightTheme.get_stylesheet())

    # 创建并显示窗口
    window = TestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
