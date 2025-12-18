import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QGroupBox, QRadioButton,
    QCheckBox, QLineEdit, QProgressBar, QSplitter,
    QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction

from src.ui.widgets import ModuleCard, LogViewer, StatusCard
from src.ui.module_info import ModuleRegistry
from src.ui.styles import TokyoNightTheme
from src.services.logger import get_logger
from src.services.config_manager import ConfigManager
from src.services.privilege_manager import PrivilegeManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = get_logger()
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        self.privilege_manager = PrivilegeManager()

        self.selected_modules = set()
        self.is_collecting = False
        self.collection_thread = None

        for module_id in ModuleRegistry.get_default_enabled_modules():
            self.selected_modules.add(module_id)

        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()

        self.update_system_info()

        self.check_privileges()

        self.logger.info("Main window initialized", module="MainWindow")

    def setup_ui(self):
        self.setWindowTitle("Centralized Evidence Collection Tool")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._create_header()
        main_layout.addWidget(header)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(2)

        modules_panel = self._create_modules_panel()
        content_splitter.addWidget(modules_panel)

        config_panel = self._create_config_panel()
        content_splitter.addWidget(config_panel)

        log_panel = self._create_log_panel()
        content_splitter.addWidget(log_panel)

        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setStretchFactor(2, 2)

        main_layout.addWidget(content_splitter)

        action_bar = self._create_action_bar()
        main_layout.addWidget(action_bar)

    def _create_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("card")
        header.setMaximumHeight(120)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        title_layout = QVBoxLayout()

        title_label = QLabel("🔍 Evidence Collection Tool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {TokyoNightTheme.BLUE};")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Centralized Windows Incident Response")
        subtitle_label.setObjectName("subtitle")
        title_layout.addWidget(subtitle_label)

        version_label = QLabel("Version 0.1.0")
        version_label.setObjectName("subtitle")
        title_layout.addWidget(version_label)

        title_layout.addStretch()

        layout.addLayout(title_layout, 1)

        self.system_info_card = StatusCard("System Information")
        layout.addWidget(self.system_info_card, 1)

        return header

    def _create_modules_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidebar")
        panel.setMinimumWidth(320)
        panel.setMaximumWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title_label = QLabel("📦 Collection Modules")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        quick_select_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all_modules)
        quick_select_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all_modules)
        quick_select_layout.addWidget(deselect_all_btn)

        layout.addLayout(quick_select_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 8, 0)

        self.module_cards = {}

        for module in ModuleRegistry.get_all_modules():
            card = ModuleCard(module)

            card.toggled.connect(self._on_module_toggled)
            card.info_requested.connect(self._on_module_info_requested)

            if module.id in self.selected_modules:
                card.set_checked(True)

            scroll_layout.addWidget(card)
            self.module_cards[module.id] = card

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)

        layout.addWidget(scroll)

        return panel

    def _create_config_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(300)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        title_label = QLabel("⚙️ Configuration")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)

        output_group = QGroupBox("Output Directory")
        output_layout = QVBoxLayout(output_group)

        dir_selection_layout = QHBoxLayout()

        self.output_dir_input = QLineEdit()
        default_dir = self.config_manager.get("output_directory")
        self.output_dir_input.setText(default_dir)
        self.output_dir_input.setPlaceholderText("Select output directory...")
        dir_selection_layout.addWidget(self.output_dir_input)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self._browse_output_directory)
        dir_selection_layout.addWidget(browse_btn)

        output_layout.addLayout(dir_selection_layout)
        scroll_layout.addWidget(output_group)

        compression_group = QGroupBox("Compression")
        compression_layout = QVBoxLayout(compression_group)

        self.compression_none_radio = QRadioButton("None (Fastest)")
        self.compression_zip_radio = QRadioButton("ZIP (Compatible)")
        self.compression_7z_radio = QRadioButton("7-Zip (Best compression)")

        compression_format = self.config_manager.get("compression.format", "zip")
        if compression_format == "none":
            self.compression_none_radio.setChecked(True)
        elif compression_format == "zip":
            self.compression_zip_radio.setChecked(True)
        else:
            self.compression_7z_radio.setChecked(True)

        compression_layout.addWidget(self.compression_none_radio)
        compression_layout.addWidget(self.compression_zip_radio)
        compression_layout.addWidget(self.compression_7z_radio)

        scroll_layout.addWidget(compression_group)

        hash_group = QGroupBox("Hash Algorithms")
        hash_layout = QVBoxLayout(hash_group)

        self.hash_md5_check = QCheckBox("MD5 (Fast)")
        self.hash_sha1_check = QCheckBox("SHA-1 (Standard)")
        self.hash_sha256_check = QCheckBox("SHA-256 (Secure)")

        algorithms = self.config_manager.get("hashing.algorithms", ["md5", "sha256"])
        self.hash_md5_check.setChecked("md5" in algorithms)
        self.hash_sha1_check.setChecked("sha1" in algorithms)
        self.hash_sha256_check.setChecked("sha256" in algorithms)

        hash_layout.addWidget(self.hash_md5_check)
        hash_layout.addWidget(self.hash_sha1_check)
        hash_layout.addWidget(self.hash_sha256_check)

        scroll_layout.addWidget(hash_group)

        naming_group = QGroupBox("Evidence Package Naming")
        naming_layout = QVBoxLayout(naming_group)

        self.package_name_input = QLineEdit()
        default_naming = self.config_manager.get(
            "general.package_naming",
            "Evidence_{timestamp}"
        )
        self.package_name_input.setText(default_naming)
        self.package_name_input.setPlaceholderText("Evidence_{timestamp}")

        naming_help = QLabel("Use {timestamp} for automatic timestamp")
        naming_help.setObjectName("subtitle")
        naming_help.setWordWrap(True)

        naming_layout.addWidget(self.package_name_input)
        naming_layout.addWidget(naming_help)

        scroll_layout.addWidget(naming_group)

        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout(advanced_group)

        self.verify_hash_check = QCheckBox("Verify hashes after collection")
        self.verify_hash_check.setChecked(
            self.config_manager.get("hashing.verify_after_collection", True)
        )

        self.create_report_check = QCheckBox("Generate HTML report")
        self.create_report_check.setChecked(
            self.config_manager.get("general.create_report", True)
        )

        advanced_layout.addWidget(self.verify_hash_check)
        advanced_layout.addWidget(self.create_report_check)

        scroll_layout.addWidget(advanced_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        config_buttons_layout = QHBoxLayout()

        save_profile_btn = QPushButton("💾 Save Profile")
        save_profile_btn.clicked.connect(self._save_config_profile)
        config_buttons_layout.addWidget(save_profile_btn)

        load_profile_btn = QPushButton("📂 Load Profile")
        load_profile_btn.clicked.connect(self._load_config_profile)
        config_buttons_layout.addWidget(load_profile_btn)

        layout.addLayout(config_buttons_layout)

        return panel

    def _create_log_panel(self) -> QWidget:
        panel = QFrame()
        panel.setMinimumWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title_label = QLabel("📊 Progress & Logs")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.status_card = StatusCard("Collection Status")
        self.status_card.add_info_row("Status", "Ready", TokyoNightTheme.GREEN)
        self.status_card.add_info_row("Progress", "0%")
        self.status_card.add_info_row("Current Module", "None")
        layout.addWidget(self.status_card)

        progress_label = QLabel("Overall Progress:")
        layout.addWidget(progress_label)

        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setFormat("%p% - %v/%m modules")
        layout.addWidget(self.overall_progress_bar)

        current_label = QLabel("Current Module:")
        layout.addWidget(current_label)

        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setValue(0)
        self.current_progress_bar.setTextVisible(True)
        layout.addWidget(self.current_progress_bar)

        log_label = QLabel("Collection Logs:")
        layout.addWidget(log_label)

        self.log_viewer = LogViewer()
        self.log_viewer.append_log("Application ready", "SUCCESS")
        self.log_viewer.append_log("Select modules and configure settings to begin", "INFO")
        layout.addWidget(self.log_viewer, 1)

        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️ Clear Logs")
        clear_log_btn.clicked.connect(self.log_viewer.clear_logs)
        log_buttons_layout.addWidget(clear_log_btn)

        export_log_btn = QPushButton("💾 Export Logs")
        export_log_btn.clicked.connect(self._export_logs)
        log_buttons_layout.addWidget(export_log_btn)

        view_detailed_log_btn = QPushButton("📄 View Detailed Log")
        view_detailed_log_btn.clicked.connect(self._view_detailed_log)
        log_buttons_layout.addWidget(view_detailed_log_btn)

        layout.addLayout(log_buttons_layout)

        return panel

    def _view_detailed_log(self):
        output_dir = Path(self.output_dir_input.text())

        evidence_dirs = sorted(
            [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('Evidence_')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not evidence_dirs:
            QMessageBox.information(
                self,
                "No Logs",
                "No evidence collections found"
            )
            return

        latest_dir = evidence_dirs[0]

        log_files = list(latest_dir.glob('*.log'))

        if not log_files:
            QMessageBox.information(
                self,
                "No Logs",
                "No log files found in the latest collection"
            )
            return

        log_file = log_files[0]

        import subprocess
        try:
            subprocess.Popen(['notepad.exe', str(log_file)])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open log file: {e}"
            )

    def _create_action_bar(self) -> QWidget:
        action_bar = QFrame()
        action_bar.setObjectName("card")
        action_bar.setMaximumHeight(80)

        layout = QHBoxLayout(action_bar)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        help_label = QLabel("💡 Select modules and configure settings, then click Start Collection")
        help_label.setObjectName("subtitle")
        layout.addWidget(help_label)

        layout.addStretch()

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(self.settings_btn)

        self.help_btn = QPushButton("❓ Help")
        self.help_btn.clicked.connect(self._show_help)
        layout.addWidget(self.help_btn)

        self.view_report_btn = QPushButton("📄 View Report")
        self.view_report_btn.setObjectName("success")
        self.view_report_btn.setEnabled(False)
        self.view_report_btn.clicked.connect(self._view_report)
        layout.addWidget(self.view_report_btn)

        self.stop_btn = QPushButton("⏹️ Stop Collection")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_collection)
        layout.addWidget(self.stop_btn)

        self.start_btn = QPushButton("▶️ Start Collection")
        self.start_btn.setObjectName("primary")
        self.start_btn.setMinimumWidth(180)
        self.start_btn.setMinimumHeight(48)
        self.start_btn.clicked.connect(self._start_collection)
        layout.addWidget(self.start_btn)

        return action_bar

    def setup_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Collection", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_collection)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_config_action = QAction("&Save Configuration", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.triggered.connect(self._save_configuration)
        file_menu.addAction(save_config_action)

        load_config_action = QAction("&Load Configuration", self)
        load_config_action.setShortcut("Ctrl+O")
        load_config_action.triggered.connect(self._load_configuration)
        file_menu.addAction(load_config_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_action)

        privileges_action = QAction("Check &Privileges", self)
        privileges_action.triggered.connect(self.check_privileges)
        tools_menu.addAction(privileges_action)

        tools_menu.addSeparator()

        elevate_action = QAction("Request &Elevation", self)
        elevate_action.triggered.connect(self._request_elevation)
        tools_menu.addAction(elevate_action)

        help_menu = menubar.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self._show_help)
        help_menu.addAction(docs_action)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_bar.showMessage("Ready")

        self.privilege_status_label = QLabel()
        self.status_bar.addPermanentWidget(self.privilege_status_label)

    def update_system_info(self):
        import socket
        import platform
        import getpass

        self.system_info_card.clear_content()

        hostname = socket.gethostname()
        self.system_info_card.add_info_row("Hostname", hostname)

        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "Unknown"
        self.system_info_card.add_info_row("IP Address", ip_address)

        os_version = f"{platform.system()} {platform.release()}"
        self.system_info_card.add_info_row("OS Version", os_version)

        current_user = getpass.getuser()
        self.system_info_card.add_info_row("Current User", current_user)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.system_info_card.add_info_row("Timestamp", timestamp)

    def check_privileges(self):
        is_admin = self.privilege_manager.is_admin()

        if is_admin:
            status_text = "🔓 Administrator"
            status_color = TokyoNightTheme.GREEN
            self.log_viewer.append_log(
                "Running with administrator privileges",
                "SUCCESS"
            )
        else:
            status_text = "🔒 Limited User"
            status_color = TokyoNightTheme.YELLOW
            self.log_viewer.append_log(
                "Running without administrator privileges - some modules may be unavailable",
                "WARNING"
            )

        self.privilege_status_label.setText(status_text)
        self.privilege_status_label.setStyleSheet(
            f"color: {status_color}; font-weight: bold; padding: 0 8px;"
        )

        for module_id, card in self.module_cards.items():
            has_privilege, message = self.privilege_manager.check_required_privileges(module_id)

            if not has_privilege:
                card.set_enabled(False)
                self.log_viewer.append_log(
                    f"Module '{module_id}' disabled: {message}",
                    "WARNING"
                )

    def _on_module_toggled(self, module_id: str, checked: bool):
        if checked:
            self.selected_modules.add(module_id)
            self.log_viewer.append_log(
                f"Module '{module_id}' enabled",
                "INFO"
            )
        else:
            self.selected_modules.discard(module_id)
            self.log_viewer.append_log(
                f"Module '{module_id}' disabled",
                "INFO"
            )

        self.status_bar.showMessage(
            f"{len(self.selected_modules)} module(s) selected"
        )

    def _on_module_info_requested(self, module_id: str):
        module = ModuleRegistry.get_module_by_id(module_id)

        if module:
            info_text = f"""
            <h3>{module.icon} {module.name}</h3>
            <p><b>Description:</b><br>{module.description}</p>
            <p><b>Estimated Time:</b> {module.estimated_time}</p>
            <p><b>Storage Required:</b> {module.storage_required}</p>
            <p><b>Requires Admin:</b> {'Yes' if module.requires_admin else 'No'}</p>
            <p><b>Category:</b> {module.category.title()}</p>
            """

            if module.dependencies:
                info_text += f"<p><b>Dependencies:</b> {', '.join(module.dependencies)}</p>"

            QMessageBox.information(
                self,
                f"Module Information - {module.name}",
                info_text
            )

    def _select_all_modules(self):
        for module_id, card in self.module_cards.items():
            if card.isEnabled():
                card.set_checked(True)
                self.selected_modules.add(module_id)

        self.log_viewer.append_log("All available modules selected", "INFO")

    def _deselect_all_modules(self):
        for card in self.module_cards.values():
            card.set_checked(False)

        self.selected_modules.clear()
        self.log_viewer.append_log("All modules deselected", "INFO")

    def _browse_output_directory(self):
        current_dir = self.output_dir_input.text()

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.output_dir_input.setText(directory)
            self.log_viewer.append_log(
                f"Output directory set to: {directory}",
                "INFO"
            )

    def _save_config_profile(self):
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self,
            "Save Configuration Profile",
            "Profile Name:"
        )

        if ok and name:
            self._update_config_from_ui()

            success = self.config_manager.save_profile(name, "User saved profile")

            if success:
                self.log_viewer.append_log(
                    f"Configuration profile '{name}' saved",
                    "SUCCESS"
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"Profile '{name}' saved successfully!"
                )
            else:
                self.log_viewer.append_log(
                    f"Failed to save profile '{name}'",
                    "ERROR"
                )
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to save profile"
                )

    def _load_config_profile(self):
        from PyQt6.QtWidgets import QInputDialog

        profiles = self.config_manager.list_profiles()

        if not profiles:
            QMessageBox.information(
                self,
                "No Profiles",
                "No saved profiles found"
            )
            return

        profile_names = [p["name"] for p in profiles]

        name, ok = QInputDialog.getItem(
            self,
            "Load Configuration Profile",
            "Select Profile:",
            profile_names,
            0,
            False
        )

        if ok and name:
            success = self.config_manager.load_profile(name)

            if success:
                self._update_ui_from_config()

                self.log_viewer.append_log(
                    f"Configuration profile '{name}' loaded",
                    "SUCCESS"
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"Profile '{name}' loaded successfully!"
                )
            else:
                self.log_viewer.append_log(
                    f"Failed to load profile '{name}'",
                    "ERROR"
                )

    def _update_config_from_ui(self):
        self.config_manager.set("output_directory", self.output_dir_input.text())

        if self.compression_none_radio.isChecked():
            compression = "none"
        elif self.compression_zip_radio.isChecked():
            compression = "zip"
        else:
            compression = "7z"
        self.config_manager.set("compression.format", compression)

        algorithms = []
        if self.hash_md5_check.isChecked():
            algorithms.append("md5")
        if self.hash_sha1_check.isChecked():
            algorithms.append("sha1")
        if self.hash_sha256_check.isChecked():
            algorithms.append("sha256")
        self.config_manager.set("hashing.algorithms", algorithms)

        self.config_manager.set("general.package_naming", self.package_name_input.text())

        self.config_manager.set("hashing.verify_after_collection", self.verify_hash_check.isChecked())
        self.config_manager.set("general.create_report", self.create_report_check.isChecked())

    def _update_ui_from_config(self):
        self.output_dir_input.setText(
            self.config_manager.get("output_directory", "")
        )

        compression = self.config_manager.get("compression.format", "zip")
        if compression == "none":
            self.compression_none_radio.setChecked(True)
        elif compression == "zip":
            self.compression_zip_radio.setChecked(True)
        else:
            self.compression_7z_radio.setChecked(True)

        algorithms = self.config_manager.get("hashing.algorithms", ["md5", "sha256"])
        self.hash_md5_check.setChecked("md5" in algorithms)
        self.hash_sha1_check.setChecked("sha1" in algorithms)
        self.hash_sha256_check.setChecked("sha256" in algorithms)

        self.package_name_input.setText(
            self.config_manager.get("general.package_naming", "Evidence_{timestamp}")
        )

        self.verify_hash_check.setChecked(
            self.config_manager.get("hashing.verify_after_collection", True)
        )
        self.create_report_check.setChecked(
            self.config_manager.get("general.create_report", True)
        )

    def _export_logs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"collection_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_viewer.toPlainText())

                self.log_viewer.append_log(
                    f"Logs exported to: {filename}",
                    "SUCCESS"
                )
                QMessageBox.information(
                    self,
                    "Success",
                    "Logs exported successfully!"
                )
            except Exception as e:
                self.log_viewer.append_log(
                    f"Failed to export logs: {e}",
                    "ERROR"
                )
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to export logs: {e}"
                )

    def _start_collection(self):
        if not self.selected_modules:
            QMessageBox.warning(
                self,
                "No Modules Selected",
                "Please select at least one collection module"
            )
            return

        output_dir = self.output_dir_input.text()
        if not output_dir:
            QMessageBox.warning(
                self,
                "No Output Directory",
                "Please select an output directory"
            )
            return

        algorithms = []
        if self.hash_md5_check.isChecked():
            algorithms.append("md5")
        if self.hash_sha1_check.isChecked():
            algorithms.append("sha1")
        if self.hash_sha256_check.isChecked():
            algorithms.append("sha256")

        if not algorithms:
            QMessageBox.warning(
                self,
                "No Hash Algorithms",
                "Please select at least one hash algorithm"
            )
            return

        module_count = len(self.selected_modules)
        reply = QMessageBox.question(
            self,
            "Start Collection",
            f"Start collecting evidence with {module_count} module(s)?\n\n"
            f"Output: {output_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            package_name = self.package_name_input.text().replace("{timestamp}", timestamp)

            final_output_dir = Path(output_dir) / package_name

            config = {
                "output_directory": str(final_output_dir),
                "compression": {
                    "enabled": not self.compression_none_radio.isChecked(),
                    "format": "zip" if self.compression_zip_radio.isChecked() else "7z"
                },
                "hashing": {
                    "algorithms": algorithms,
                    "verify_after_collection": self.verify_hash_check.isChecked()
                },
                "general": {
                    "create_report": self.create_report_check.isChecked()
                },
                "modules": {}
            }

            self._start_real_collection(list(self.selected_modules), final_output_dir, config)

    def _start_real_collection(self, module_ids, output_dir, config):
        from src.core.evidence_controller import EvidenceController

        self.is_collecting = True

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.log_viewer.append_separator()
        self.log_viewer.append_log("Starting evidence collection...", "INFO")

        total_modules = len(module_ids)
        self.overall_progress_bar.setMaximum(total_modules)
        self.overall_progress_bar.setValue(0)
        self.current_progress_bar.setValue(0)

        self.status_card.clear_content()
        self.status_card.add_info_row(
            "Status",
            "Initializing...",
            TokyoNightTheme.BLUE
        )
        self.status_card.add_info_row("Progress", "0%")

        self.evidence_controller = EvidenceController()

        success = self.evidence_controller.start_collection(
            module_ids=module_ids,
            output_dir=output_dir,
            config=config,
            progress_callback=self._on_collection_progress,
            log_callback=self._on_collection_log,
            completion_callback=self._on_collection_complete
        )

        if not success:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to start evidence collection"
            )
            self._reset_ui_after_collection()

    def _on_collection_progress(self, current, total):
        self.overall_progress_bar.setValue(current)

        percentage = int((current / total) * 100) if total > 0 else 0

        self.status_card.clear_content()
        self.status_card.add_info_row(
            "Status",
            "Collecting...",
            TokyoNightTheme.BLUE
        )
        self.status_card.add_info_row(
            "Progress",
            f"{percentage}% ({current}/{total} modules)"
        )

    def _on_collection_log(self, message, level):
        self.log_viewer.append_log(message, level)

    def _on_collection_complete(self, success, message):
        self.is_collecting = False

        if success:
            self.log_viewer.append_log(message, "SUCCESS")

            QMessageBox.information(
                self,
                "Collection Complete",
                f"{message}\n\nClick 'View Report' to see the results."
            )

            self.view_report_btn.setEnabled(True)
        else:
            self.log_viewer.append_log(message, "ERROR")

            QMessageBox.warning(
                self,
                "Collection Failed",
                message
            )

        self.log_viewer.append_separator()
        self._reset_ui_after_collection()

    def _reset_ui_after_collection(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.status_card.clear_content()
        status_text = "Completed" if not self.is_collecting else "Ready"
        status_color = TokyoNightTheme.GREEN if not self.is_collecting else TokyoNightTheme.BLUE

        self.status_card.add_info_row("Status", status_text, status_color)

    def _simulate_collection(self):
        self.is_collecting = True

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.status_card.clear_content()
        self.status_card.add_info_row(
            "Status",
            "Collecting...",
            TokyoNightTheme.BLUE
        )

        total_modules = len(self.selected_modules)
        self.overall_progress_bar.setMaximum(total_modules)
        self.overall_progress_bar.setValue(0)

        self.simulation_progress = 0
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self._update_simulation)
        self.simulation_timer.start(500)

    def _update_simulation(self):
        self.simulation_progress += 1

        if self.simulation_progress <= len(self.selected_modules):
            self.overall_progress_bar.setValue(self.simulation_progress)
            self.current_progress_bar.setValue(50)

            module_list = list(self.selected_modules)
            if self.simulation_progress <= len(module_list):
                current_module = module_list[self.simulation_progress - 1]
                self.log_viewer.append_log(
                    f"Collecting from module: {current_module}",
                    "INFO"
                )

                self.status_card.clear_content()
                self.status_card.add_info_row(
                    "Status",
                    "Collecting...",
                    TokyoNightTheme.BLUE
                )
                self.status_card.add_info_row(
                    "Progress",
                    f"{self.simulation_progress}/{len(self.selected_modules)}"
                )
                self.status_card.add_info_row(
                    "Current Module",
                    current_module
                )
        else:
            self.simulation_timer.stop()
            self._collection_completed()

    def _collection_completed(self):
        self.is_collecting = False

        self.log_viewer.append_log(
            "Evidence collection completed successfully!",
            "SUCCESS"
        )
        self.log_viewer.append_separator()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.view_report_btn.setEnabled(True)

        self.current_progress_bar.setValue(100)

        self.status_card.clear_content()
        self.status_card.add_info_row(
            "Status",
            "Completed",
            TokyoNightTheme.GREEN
        )
        self.status_card.add_info_row(
            "Progress",
            "100%"
        )
        self.status_card.add_info_row(
            "Modules Processed",
            f"{len(self.selected_modules)}/{len(self.selected_modules)}"
        )

        QMessageBox.information(
            self,
            "Collection Complete",
            "Evidence collection completed successfully!\n\n"
            "Click 'View Report' to see the results."
        )

    def _stop_collection(self):
        reply = QMessageBox.question(
            self,
            "Stop Collection",
            "Are you sure you want to stop the collection?\n\n"
            "This will result in incomplete evidence.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'evidence_controller'):
                self.evidence_controller.stop_collection()

            self.log_viewer.append_log(
                "Collection stopped by user",
                "WARNING"
            )

    def _view_report(self):
        output_dir = Path(self.output_dir_input.text())

        evidence_dirs = sorted(
            [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith('Evidence_')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not evidence_dirs:
            QMessageBox.information(
                self,
                "No Reports",
                "No evidence collections found in the output directory"
            )
            return

        latest_dir = evidence_dirs[0]
        report_path = latest_dir / "collection_report.html"

        if not report_path.exists():
            QMessageBox.warning(
                self,
                "Report Not Found",
                f"Report file not found in {latest_dir.name}"
            )
            return

        import webbrowser
        try:
            webbrowser.open(str(report_path.absolute()))
            self.log_viewer.append_log(
                f"Opened report: {report_path}",
                "SUCCESS"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open report: {e}"
            )
            self.log_viewer.append_log(
                f"Failed to open report: {e}",
                "ERROR"
            )

    def _open_settings(self):
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog will be implemented in the next phase"
        )

    def _show_help(self):
        help_text = """
        <h2>Evidence Collection Tool - Help</h2>

        <h3>Getting Started:</h3>
        <ol>
        <li>Select the modules you want to run from the left panel</li>
        <li>Configure collection settings in the middle panel</li>
        <li>Click 'Start Collection' to begin</li>
        </ol>

        <h3>Modules:</h3>
        <ul>
        <li><b>Memory:</b> Captures RAM contents</li>
        <li><b>Disk:</b> Creates disk images</li>
        <li><b>Network:</b> Collects network information</li>
        <li><b>File System:</b> Extracts file metadata</li>
        <li><b>Registry:</b> Exports registry hives</li>
        <li><b>Live System:</b> Captures running processes</li>
        <li><b>Browser:</b> Collects browser artifacts</li>
        <li><b>Event Logs:</b> Copies event logs</li>
        </ul>

        <h3>Requirements:</h3>
        <p>Some modules require administrator privileges.
        Use Tools → Request Elevation to run as administrator.</p>
        """

        QMessageBox.information(
            self,
            "Help",
            help_text
        )

    def _show_about(self):
        about_text = """
        <h2>Centralized Evidence Collection Tool</h2>
        <p><b>Version:</b> 0.1.0</p>
        <p><b>Author:</b> Your Name</p>
        <p><b>Purpose:</b> Final Year Project (FYP)</p>

        <p>A comprehensive tool for Windows incident response
        and digital forensics evidence collection.</p>

        <p><b>Features:</b></p>
        <ul>
        <li>Modular evidence collection</li>
        <li>Tokyo Night themed interface</li>
        <li>Comprehensive logging and reporting</li>
        <li>Hash verification for integrity</li>
        </ul>
        """

        QMessageBox.about(
            self,
            "About",
            about_text
        )

    def _new_collection(self):
        if self.is_collecting:
            QMessageBox.warning(
                self,
                "Collection in Progress",
                "Please wait for current collection to finish"
            )
            return

        self.log_viewer.clear_logs()
        self.log_viewer.append_log("Ready for new collection", "INFO")

        self.overall_progress_bar.setValue(0)
        self.current_progress_bar.setValue(0)

        self.status_card.clear_content()
        self.status_card.add_info_row("Status", "Ready", TokyoNightTheme.GREEN)

        self.view_report_btn.setEnabled(False)

    def _save_configuration(self):
        self._update_config_from_ui()
        success = self.config_manager.save_config()

        if success:
            self.log_viewer.append_log("Configuration saved", "SUCCESS")
            QMessageBox.information(
                self,
                "Success",
                "Configuration saved successfully!"
            )
        else:
            self.log_viewer.append_log("Failed to save configuration", "ERROR")
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save configuration"
            )

    def _load_configuration(self):
        success = self.config_manager.load_config()

        if success:
            self._update_ui_from_config()
            self.log_viewer.append_log("Configuration loaded", "SUCCESS")
        else:
            self.log_viewer.append_log("Failed to load configuration", "WARNING")

    def _request_elevation(self):
        reply = QMessageBox.question(
            self,
            "Request Elevation",
            "This will restart the application with administrator privileges.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.privilege_manager.request_elevation()

    def closeEvent(self, event):
        if self.is_collecting:
            reply = QMessageBox.question(
                self,
                "Collection in Progress",
                "Evidence collection is in progress.\n\n"
                "Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self._update_config_from_ui()
        self.config_manager.save_config()

        self.logger.close()

        event.accept()
