from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Optional
import json
import time

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
            self.log_message.emit("Generating collection report...", "INFO")

            from src.services.report_generator import ReportGenerator
            import socket
            import platform
            import getpass

            try:
                hostname = socket.gethostname()
            except:
                hostname = "Unknown"

            try:
                ip_address = socket.gethostbyname(hostname)
            except:
                ip_address = "Unknown"

            collection_data = {
                'hostname': hostname,
                'ip_address': ip_address,
                'os_version': f"{platform.system()} {platform.release()}",
                'user': getpass.getuser(),
                'completed_modules': completed,
                'failed_modules': failed_modules,
                'total_modules': len(self.modules)
            }

            self.logger.debug(
                f"Collection data prepared: {collection_data}",
                module="CollectionThread"
            )

            report_gen = ReportGenerator()
            report_path = report_gen.generate_report(
                self.output_dir,
                collection_data
            )

            if report_path and report_path.exists():
                self.log_message.emit(f"Report generated: {report_path.name}", "SUCCESS")
                self.logger.info(f"Report generated successfully: {report_path}")
            else:
                self.log_message.emit("Failed to generate report", "ERROR")
                self.logger.error("Report generation returned None or file not found")

        except ImportError as e:
            error_msg = f"Failed to import ReportGenerator: {e}"
            self.logger.error(error_msg, module="CollectionThread", exc_info=True)
            self.log_message.emit(error_msg, "ERROR")

        except Exception as e:
            error_msg = f"Failed to generate report: {e}"
            self.logger.error(error_msg, module="CollectionThread", exc_info=True)
            self.log_message.emit(error_msg, "ERROR")

    def _compress_evidence(self):
        try:
            import zipfile
            import os

            if not self.config.get("compression", {}).get("enabled", True):
                self.log_message.emit("Compression disabled", "INFO")
                return

            self.log_message.emit("Preparing to compress evidence package...", "INFO")

            files_to_compress = []
            total_size = 0

            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    file_size = file_path.stat().st_size
                    files_to_compress.append({
                        'path': file_path,
                        'size': file_size,
                        'arcname': file_path.relative_to(self.output_dir.parent)
                    })
                    total_size += file_size

            if not files_to_compress:
                self.log_message.emit("No files to compress", "WARNING")
                return

            total_size_gb = total_size / (1024**3)
            file_count = len(files_to_compress)

            if total_size_gb > 10:
                compress_level = 1
                self.log_message.emit(
                    f"Large package detected ({total_size_gb:.2f} GB), using fast compression...",
                    "INFO"
                )
            elif total_size_gb > 5:
                compress_level = 3
                self.log_message.emit(
                    f"Compressing {file_count} files ({total_size_gb:.2f} GB) with balanced compression...",
                    "INFO"
                )
            else:
                compress_level = 6
                self.log_message.emit(
                    f"Compressing {file_count} files ({total_size_gb:.2f} GB)...",
                    "INFO"
                )

            archive_path = self.output_dir.parent / f"{self.output_dir.name}.zip"

            compressed_size = 0
            start_time = time.time()
            last_update = start_time

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compress_level) as zipf:
                for i, file_info in enumerate(files_to_compress, 1):
                    zipf.write(file_info['path'], file_info['arcname'])

                    compressed_size += file_info['size']
                    current_time = time.time()

                    progress_percent = (compressed_size / total_size) * 100

                    if (current_time - last_update >= 1.0) or (i == file_count):
                        elapsed = current_time - start_time

                        if elapsed > 0:
                            speed_mbps = (compressed_size / (1024**2)) / elapsed
                            remaining_bytes = total_size - compressed_size
                            eta_seconds = remaining_bytes / (compressed_size / elapsed) if compressed_size > 0 else 0

                            self.log_message.emit(
                                f"Compressing: {progress_percent:.1f}% "
                                f"({i}/{file_count} files) "
                                f"[{speed_mbps:.1f} MB/s, ETA: {eta_seconds:.0f}s]",
                                "INFO"
                            )
                        else:
                            self.log_message.emit(
                                f"Compressing: {progress_percent:.1f}% ({i}/{file_count} files)",
                                "INFO"
                            )

                        last_update = current_time

            archive_size = archive_path.stat().st_size
            archive_size_gb = archive_size / (1024**3)
            compression_ratio = (1 - archive_size / total_size) * 100
            elapsed_total = time.time() - start_time
            avg_speed = (total_size / (1024**2)) / elapsed_total if elapsed_total > 0 else 0

            self.log_message.emit(
                f"✓ Compression completed in {elapsed_total:.1f}s (avg: {avg_speed:.1f} MB/s)",
                "SUCCESS"
            )

            self.log_message.emit(
                f"Original: {total_size_gb:.2f} GB → Compressed: {archive_size_gb:.2f} GB "
                f"({compression_ratio:.1f}% reduction)",
                "SUCCESS"
            )

            self.log_message.emit(
                f"Archive: {archive_path}",
                "SUCCESS"
            )

        except Exception as e:
            self.logger.error(f"Compression failed: {e}", exc_info=True)
            self.log_message.emit(f"Compression failed: {e}", "ERROR")

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
            "memory": "src.modules.memory_module",
            "disk": "src.modules.disk_module",
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
