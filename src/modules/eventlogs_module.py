import shutil
from pathlib import Path
from typing import Dict, Any, List
import subprocess

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class EventlogsModule(ICollectionModule):
    LOGS_DIR = Path('C:/Windows/System32/winevt/Logs')

    CRITICAL_LOGS = [
        'Security.evtx',
        'System.evtx',
        'Application.evtx',
        'Windows PowerShell.evtx',
        'Microsoft-Windows-PowerShell%4Operational.evtx',
        'Microsoft-Windows-TaskScheduler%4Operational.evtx',
        'Microsoft-Windows-TerminalServices-LocalSessionManager%4Operational.evtx',
        'Microsoft-Windows-Windows Defender%4Operational.evtx',
        'Microsoft-Windows-Sysmon%4Operational.evtx',
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "eventlogs"))
        self.collected_files = []
        self.collect_all = config.get("collect_all_logs", False)

    def initialize(self) -> bool:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.logger.error(
                    "Event logs module requires administrator privileges",
                    module="EventlogsModule"
                )
                self.status = ModuleStatus.FAILED
                self.error_message = "Administrator privileges required"
                return False

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Event logs module initialized, output: {self.output_dir}",
                module="EventlogsModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize event logs module: {e}",
                module="EventlogsModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            if not self.LOGS_DIR.exists():
                self.logger.error(
                    f"Event logs directory not found: {self.LOGS_DIR}",
                    module="EventlogsModule"
                )
                return False

            self.logger.info("Collecting critical event logs...", module="EventlogsModule")
            self._collect_critical_logs()
            self.progress = 40

            if self.collect_all:
                self.logger.info("Collecting all event logs...", module="EventlogsModule")
                self._collect_all_logs()
            self.progress = 70

            self.logger.info("Generating logs inventory...", module="EventlogsModule")
            self._generate_inventory()
            self.progress = 85

            self.logger.info("Calculating hashes...", module="EventlogsModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                f"Event logs module completed, collected {len(self.collected_files)} files",
                module="EventlogsModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Event logs module failed: {e}",
                module="EventlogsModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_critical_logs(self):
        try:
            critical_dir = self.output_dir / "critical"
            critical_dir.mkdir(exist_ok=True)

            collected_count = 0

            for log_name in self.CRITICAL_LOGS:
                log_path = self.LOGS_DIR / log_name

                if log_path.exists():
                    try:
                        safe_name = log_name.replace('%4', '_')
                        dest_path = critical_dir / safe_name

                        shutil.copy2(log_path, dest_path)

                        self.collected_files.append(dest_path)
                        collected_count += 1

                        size_mb = dest_path.stat().st_size / (1024 * 1024)
                        self.logger.info(
                            f"Collected {log_name} ({size_mb:.2f}MB)",
                            module="EventlogsModule"
                        )

                    except PermissionError:
                        self.logger.warning(
                            f"Permission denied: {log_name}",
                            module="EventlogsModule"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Failed to copy {log_name}: {e}",
                            module="EventlogsModule"
                        )
                else:
                    self.logger.debug(
                        f"Log not found: {log_name}",
                        module="EventlogsModule"
                    )

            self.logger.info(
                f"Collected {collected_count} critical event logs",
                module="EventlogsModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to collect critical logs: {e}",
                module="EventlogsModule"
            )

    def _collect_all_logs(self):
        try:
            all_logs_dir = self.output_dir / "all"
            all_logs_dir.mkdir(exist_ok=True)

            collected_count = 0
            total_size_mb = 0
            max_size_gb = 2

            for log_file in self.LOGS_DIR.iterdir():
                if not log_file.is_file() or not log_file.suffix == '.evtx':
                    continue

                if log_file.name in self.CRITICAL_LOGS:
                    continue

                size_mb = log_file.stat().st_size / (1024 * 1024)
                if total_size_mb + size_mb > (max_size_gb * 1024):
                    self.logger.warning(
                        f"Size limit reached ({max_size_gb}GB), stopping collection",
                        module="EventlogsModule"
                    )
                    break

                try:
                    safe_name = log_file.name.replace('%4', '_')
                    dest_path = all_logs_dir / safe_name

                    shutil.copy2(log_file, dest_path)

                    self.collected_files.append(dest_path)
                    collected_count += 1
                    total_size_mb += size_mb

                except PermissionError:
                    continue
                except Exception as e:
                    self.logger.error(
                        f"Failed to copy {log_file.name}: {e}",
                        module="EventlogsModule"
                    )

            self.logger.info(
                f"Collected {collected_count} additional event logs ({total_size_mb:.2f}MB)",
                module="EventlogsModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to collect all logs: {e}",
                module="EventlogsModule"
            )

    def _generate_inventory(self):
        try:
            inventory_file = self.output_dir / "logs_inventory.txt"

            with open(inventory_file, 'w', encoding='utf-8') as f:
                f.write("Event Logs Inventory\n")
                f.write("=" * 80 + "\n\n")

                f.write("Collection Summary:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Files Collected: {len(self.collected_files)}\n")

                total_size = sum(f.stat().st_size for f in self.collected_files if f.exists())
                f.write(f"Total Size: {total_size / (1024*1024):.2f} MB\n")
                f.write("\n")

                f.write("Collected Files:\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'File Name':<60} {'Size (MB)':<15}\n")
                f.write("-" * 80 + "\n")

                for file_path in sorted(self.collected_files):
                    if file_path.exists():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        rel_path = file_path.relative_to(self.output_dir)
                        f.write(f"{str(rel_path):<60} {size_mb:>10.2f}\n")

            self.collected_files.append(inventory_file)

        except Exception as e:
            self.logger.error(
                f"Failed to generate inventory: {e}",
                module="EventlogsModule"
            )

    def _calculate_hashes(self):
        hash_file = self.output_dir / "hashes.txt"

        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write("File Hashes\n")
            f.write("=" * 80 + "\n\n")

            for file_path in self.collected_files:
                if file_path.exists() and file_path != hash_file:
                    size_mb = file_path.stat().st_size / (1024 * 1024)

                    if size_mb > 100:
                        algorithms = ["sha256"]
                    else:
                        algorithms = self.config.get("hash_algorithms", ["md5", "sha256"])

                    hashes = self.hash_calculator.calculate_file_hashes(
                        file_path,
                        algorithms
                    )

                    f.write(f"File: {file_path.relative_to(self.output_dir)}\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"  {algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="EventlogsModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Event logs module cleanup", module="EventlogsModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "eventlogs",
            "name": "Event Logs Collection",
            "version": "1.0.0",
            "description": "Collects Windows event logs including Security, System, Application, and PowerShell logs"
        }
