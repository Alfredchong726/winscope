from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Optional
import json

from PyQt6.QtCore import QThread, pyqtSignal

from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator
from src.modules.base_module import ICollectionModule, ModuleStatus


class CollectionThread(QThread):
    progress_updated = pyqtSignal(int, int)
    module_started = pyqtSignal(str)
    module_completed = pyqtSignal(str, bool)
    log_message = pyqtSignal(str, str)
    collection_completed = pyqtSignal(bool, str)

    def __init__(
        self,
        modules: List[ICollectionModule],
        output_dir: Path,
        config: Dict
    ):
        super().__init__()
        self.modules = modules
        self.output_dir = Path(output_dir)
        self.config = config
        self.should_stop = False
        self.logger = get_logger()

    def run(self):
        try:
            self.log_message.emit("Initializing collection environment...", "INFO")

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.initialize(self.output_dir)
            self.log_message.emit(f"Output directory: {self.output_dir}", "INFO")

            total_modules = len(self.modules)
            completed = 0
            failed_modules = []

            for i, module in enumerate(self.modules, 1):
                if self.should_stop:
                    self.log_message.emit("Collection stopped by user", "WARNING")
                    self.collection_completed.emit(False, "Stopped by user")
                    return

                module_info = module.get_module_info()
                module_name = module_info.get("name", "Unknown")

                self.log_message.emit(
                    f"Starting module: {module_name}",
                    "INFO"
                )
                self.module_started.emit(module_info.get("id", "unknown"))

                # 初始化模块
                if not module.initialize():
                    self.log_message.emit(
                        f"Failed to initialize module: {module_name}",
                        "ERROR"
                    )
                    failed_modules.append(module_name)
                    self.module_completed.emit(module_info.get("id", "unknown"), False)
                    continue

                success = module.execute()

                if success:
                    self.log_message.emit(
                        f"Module completed successfully: {module_name}",
                        "SUCCESS"
                    )
                    completed += 1
                else:
                    self.log_message.emit(
                        f"Module failed: {module_name}",
                        "ERROR"
                    )
                    failed_modules.append(module_name)

                module.cleanup()

                self.module_completed.emit(module_info.get("id", "unknown"), success)
                self.progress_updated.emit(i, total_modules)

            self.log_message.emit("Generating collection report...", "INFO")
            self._generate_report(completed, failed_modules)

            if self.config.get("compression", {}).get("enabled", False):
                self.log_message.emit("Compressing evidence package...", "INFO")
                self._compress_evidence()

            if failed_modules:
                message = f"Collection completed with {len(failed_modules)} failed module(s)"
                self.log_message.emit(message, "WARNING")
                self.collection_completed.emit(True, message)
            else:
                message = "Collection completed successfully!"
                self.log_message.emit(message, "SUCCESS")
                self.collection_completed.emit(True, message)

        except Exception as e:
            error_msg = f"Collection failed: {str(e)}"
            self.logger.error(error_msg, module="CollectionThread", exc_info=True)
            self.log_message.emit(error_msg, "ERROR")
            self.collection_completed.emit(False, error_msg)

    def stop(self):
        self.should_stop = True
        self.log_message.emit("Stop requested...", "WARNING")

    def _generate_report(self, completed: int, failed_modules: List[str]):
        try:
            from src.services.report_generator import ReportGenerator
            import socket
            import platform
            import getpass

            collection_data = {
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'os_version': f"{platform.system()} {platform.release()}",
                'user': getpass.getuser(),
                'completed_modules': completed,
                'failed_modules': failed_modules,
                'total_modules': len(self.modules)
            }

            report_gen = ReportGenerator()
            report_path = report_gen.generate_report(
                self.output_dir,
                collection_data
            )

            if report_path:
                self.log_message.emit(f"Report generated: {report_path}", "SUCCESS")
            else:
                self.log_message.emit("Failed to generate report", "ERROR")

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}", exc_info=True)
            self.log_message.emit(f"Failed to generate report: {e}", "ERROR")

    def _compress_evidence(self):
        try:
            import zipfile

            compression_format = self.config.get("compression", {}).get("format", "zip")

            if compression_format == "zip":
                archive_name = self.output_dir.parent / f"{self.output_dir.name}.zip"

                with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in self.output_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(self.output_dir.parent)
                            zipf.write(file_path, arcname)

                self.log_message.emit(
                    f"Evidence compressed: {archive_name}",
                    "SUCCESS"
                )

        except Exception as e:
            self.logger.error(f"Failed to compress evidence: {e}", exc_info=True)
            self.log_message.emit(f"Failed to compress evidence: {e}", "ERROR")


class EvidenceController:
    def __init__(self):
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.collection_thread: Optional[CollectionThread] = None
        self.is_running = False

    def start_collection(
        self,
        module_ids: List[str],
        output_dir: Path,
        config: Dict,
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> bool:
        if self.is_running:
            self.logger.warning("Collection already in progress")
            return False

        try:
            modules = self._load_modules(module_ids, output_dir, config)

            if not modules:
                self.logger.error("No modules loaded")
                return False

            self.collection_thread = CollectionThread(modules, output_dir, config)

            if progress_callback:
                self.collection_thread.progress_updated.connect(progress_callback)

            if log_callback:
                self.collection_thread.log_message.connect(log_callback)

            if completion_callback:
                self.collection_thread.collection_completed.connect(completion_callback)

            self.collection_thread.start()
            self.is_running = True

            self.logger.info("Collection started", module="EvidenceController")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start collection: {e}", exc_info=True)
            return False

    def stop_collection(self):
        if self.collection_thread and self.is_running:
            self.collection_thread.stop()
            self.collection_thread.wait()
            self.is_running = False
            self.logger.info("Collection stopped", module="EvidenceController")

    def _load_modules(
        self,
        module_ids: List[str],
        output_dir: Path,
        config: Dict
    ) -> List[ICollectionModule]:
        modules = []

        for module_id in module_ids:
            try:
                module = self._create_module(module_id, output_dir, config)
                if module:
                    modules.append(module)
                else:
                    self.logger.warning(f"Failed to create module: {module_id}")
            except Exception as e:
                self.logger.error(
                    f"Error creating module {module_id}: {e}",
                    exc_info=True
                )

        return modules

    def _create_module(
        self,
        module_id: str,
        output_dir: Path,
        config: Dict
    ) -> Optional[ICollectionModule]:
        module_map = {
            "network": "src.modules.network_module",
            "filesystem": "src.modules.filesystem_module",
            "live_system": "src.modules.live_system_module",
            "browser": "src.modules.browser_module",
            # "memory": "src.modules.memory_module",
            # "disk": "src.modules.disk_module",
            "registry": "src.modules.registry_module",
            "eventlogs": "src.modules.eventlogs_module",
        }

        if module_id not in module_map:
            self.logger.warning(f"Unknown module: {module_id}")
            return None

        try:
            module_path = module_map[module_id]
            parts = module_path.rsplit('.', 1)
            module_name = parts[1]

            import importlib
            mod = importlib.import_module(module_path)

            class_name = ''.join(word.capitalize() for word in module_id.split('_')) + 'Module'
            module_class = getattr(mod, class_name)

            module_config = {
                "output_dir": output_dir / module_id,
                "hash_algorithms": config.get("hashing", {}).get("algorithms", ["md5", "sha256"]),
                **config.get("modules", {}).get(module_id, {})
            }

            return module_class(module_config)

        except Exception as e:
            self.logger.error(
                f"Failed to create module {module_id}: {e}",
                exc_info=True
            )
            return None
