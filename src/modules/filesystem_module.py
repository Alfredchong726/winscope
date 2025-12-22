import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class FilesystemModule(ICollectionModule):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "filesystem"))
        self.collected_files = []

        self.suspicious_extensions = [
            '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs',
            '.scr', '.com', '.pif', '.jar'
        ]

    def initialize(self) -> bool:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Filesystem module initialized, output: {self.output_dir}",
                module="FilesystemModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize filesystem module: {e}",
                module="FilesystemModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Collecting recent files...", module="FilesystemModule")
            self._collect_recent_files()
            self.progress = 20

            self.logger.info("Collecting startup items...", module="FilesystemModule")
            self._collect_startup_items()
            self.progress = 40

            self.logger.info("Scanning temp directories...", module="FilesystemModule")
            self._collect_temp_files()
            self.progress = 60

            self.logger.info("Collecting recycle bin info...", module="FilesystemModule")
            self._collect_recycle_bin()
            self.progress = 80

            self.logger.info("Calculating hashes...", module="FilesystemModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                "Filesystem module completed successfully",
                module="FilesystemModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Filesystem module failed: {e}",
                module="FilesystemModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_recent_files(self):
        try:
            recent_dir = Path.home() / "AppData/Roaming/Microsoft/Windows/Recent"
            output_file = self.output_dir / "recent_files.txt"

            if not recent_dir.exists():
                self.logger.warning("Recent files directory not found", module="FilesystemModule")
                return

            recent_items = []

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Recent Files\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"{'File Name':<50} {'Modified':<20} {'Target':<50}\n")
                f.write("-" * 120 + "\n")

                for item in recent_dir.iterdir():
                    try:
                        if item.is_file():
                            modified = datetime.fromtimestamp(
                                item.stat().st_mtime
                            ).strftime('%Y-%m-%d %H:%M:%S')

                            target = "N/A"
                            if item.suffix.lower() == '.lnk':
                                target = "Shortcut file"

                            f.write(f"{item.name:<50} {modified:<20} {target:<50}\n")

                            recent_items.append({
                                "name": item.name,
                                "modified": modified,
                                "path": str(item),
                                "size": item.stat().st_size
                            })
                    except Exception as e:
                        continue

            json_file = self.output_dir / "recent_files.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(recent_items, f, indent=4, ensure_ascii=False)

            self.collected_files.extend([output_file, json_file])
            self.logger.info(
                f"Collected {len(recent_items)} recent files",
                module="FilesystemModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to collect recent files: {e}",
                module="FilesystemModule"
            )

    def _collect_startup_items(self):
        try:
            output_file = self.output_dir / "startup_items.txt"
            startup_items = []

            user_startup = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

            all_users_startup = Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/StartUp")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Startup Items\n")
                f.write("=" * 80 + "\n\n")

                f.write("User Startup Folder:\n")
                f.write("-" * 80 + "\n")
                if user_startup.exists():
                    for item in user_startup.iterdir():
                        if item.is_file():
                            f.write(f"  {item.name}\n")
                            startup_items.append({
                                "location": "User Startup",
                                "name": item.name,
                                "path": str(item)
                            })
                else:
                    f.write("  (Not found)\n")

                f.write("\n")

                f.write("All Users Startup Folder:\n")
                f.write("-" * 80 + "\n")
                if all_users_startup.exists():
                    for item in all_users_startup.iterdir():
                        if item.is_file():
                            f.write(f"  {item.name}\n")
                            startup_items.append({
                                "location": "All Users Startup",
                                "name": item.name,
                                "path": str(item)
                            })
                else:
                    f.write("  (Not found)\n")

            json_file = self.output_dir / "startup_items.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(startup_items, f, indent=4, ensure_ascii=False)

            self.collected_files.extend([output_file, json_file])
            self.logger.info(
                f"Collected {len(startup_items)} startup items",
                module="FilesystemModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to collect startup items: {e}",
                module="FilesystemModule"
            )

    def _collect_temp_files(self):
        try:
            output_file = self.output_dir / "temp_files.txt"

            temp_dirs = [
                Path(os.environ.get('TEMP', '')),
                Path(os.environ.get('TMP', '')),
                Path("C:/Windows/Temp")
            ]

            all_temp_files = []

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Temporary Files Scan\n")
                f.write("=" * 80 + "\n\n")

                for temp_dir in temp_dirs:
                    if not temp_dir.exists():
                        continue

                    f.write(f"Directory: {temp_dir}\n")
                    f.write("-" * 80 + "\n")

                    try:
                        file_count = 0
                        max_files = 1000

                        for item in temp_dir.iterdir():
                            if file_count >= max_files:
                                f.write(f"  ... (限制{max_files}个文件)\n")
                                break

                            try:
                                if item.is_file():
                                    size_mb = item.stat().st_size / (1024 * 1024)
                                    modified = datetime.fromtimestamp(
                                        item.stat().st_mtime
                                    ).strftime('%Y-%m-%d %H:%M:%S')

                                    f.write(f"  {item.name} - {size_mb:.2f}MB - {modified}\n")

                                    all_temp_files.append({
                                        "directory": str(temp_dir),
                                        "name": item.name,
                                        "size_mb": round(size_mb, 2),
                                        "modified": modified,
                                        "extension": item.suffix.lower()
                                    })

                                    file_count += 1
                            except Exception:
                                continue

                        f.write(f"\nTotal files scanned: {file_count}\n\n")

                    except PermissionError:
                        f.write("  (Access denied)\n\n")

            json_file = self.output_dir / "temp_files.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(all_temp_files, f, indent=4, ensure_ascii=False)

            self.collected_files.extend([output_file, json_file])
            self.logger.info(
                f"Scanned {len(all_temp_files)} temp files",
                module="FilesystemModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to scan temp files: {e}",
                module="FilesystemModule"
            )

    def _collect_recycle_bin(self):
        try:
            output_file = self.output_dir / "recycle_bin.txt"

            recycle_bins = []

            for drive in ['C:', 'D:', 'E:']:
                recycle_path = Path(f"{drive}/$Recycle.Bin")

                if recycle_path.exists():
                    try:
                        for user_bin in recycle_path.iterdir():
                            if user_bin.is_dir():
                                recycle_bins.append(user_bin)
                    except PermissionError:
                        continue

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Recycle Bin Contents\n")
                f.write("=" * 80 + "\n\n")

                if not recycle_bins:
                    f.write("No accessible recycle bin directories found.\n")
                    f.write("(May require administrator privileges)\n")
                else:
                    total_items = 0

                    for bin_dir in recycle_bins:
                        f.write(f"Recycle Bin: {bin_dir}\n")
                        f.write("-" * 80 + "\n")

                        try:
                            for item in bin_dir.iterdir():
                                if item.is_file():
                                    size_mb = item.stat().st_size / (1024 * 1024)
                                    f.write(f"  {item.name} - {size_mb:.2f}MB\n")
                                    total_items += 1
                        except PermissionError:
                            f.write("  (Access denied)\n")

                        f.write("\n")

                    f.write(f"Total items found: {total_items}\n")

            self.collected_files.append(output_file)
            self.logger.info(
                "Recycle bin information collected",
                module="FilesystemModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to collect recycle bin: {e}",
                module="FilesystemModule"
            )

    def _calculate_hashes(self):
        hash_file = self.output_dir / "hashes.txt"

        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write("File Hashes\n")
            f.write("=" * 80 + "\n\n")

            for file_path in self.collected_files:
                if file_path.exists():
                    hashes = self.hash_calculator.calculate_file_hashes(
                        file_path,
                        self.config.get("hash_algorithms", ["md5", "sha256"])
                    )

                    f.write(f"File: {file_path.name}\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"  {algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="FilesystemModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Filesystem module cleanup", module="FilesystemModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "filesystem",
            "name": "File System Collection",
            "version": "1.0.0",
            "description": "Collects recent files, startup items, temp files, and recycle bin information"
        }
