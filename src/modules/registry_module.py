import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List
import os

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class RegistryModule(ICollectionModule):
    SYSTEM_HIVES = {
        'SYSTEM': Path('C:/Windows/System32/config/SYSTEM'),
        'SOFTWARE': Path('C:/Windows/System32/config/SOFTWARE'),
        'SAM': Path('C:/Windows/System32/config/SAM'),
        'SECURITY': Path('C:/Windows/System32/config/SECURITY'),
    }

    IMPORTANT_KEYS = [
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
        r'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        r'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',

        r'HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR',

        r'HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters',

        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        r'HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall',

        r'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs',
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "registry"))
        self.collected_files = []

    def initialize(self) -> bool:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.logger.error(
                    "Registry module requires administrator privileges",
                    module="RegistryModule"
                )
                self.status = ModuleStatus.FAILED
                self.error_message = "Administrator privileges required"
                return False

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Registry module initialized, output: {self.output_dir}",
                module="RegistryModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize registry module: {e}",
                module="RegistryModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Copying system registry hives...", module="RegistryModule")
            self._copy_system_hives()
            self.progress = 30

            self.logger.info("Copying user registry hives...", module="RegistryModule")
            self._copy_user_hives()
            self.progress = 50

            self.logger.info("Exporting important registry keys...", module="RegistryModule")
            self._export_important_keys()
            self.progress = 70

            self.logger.info("Generating registry report...", module="RegistryModule")
            self._generate_report()
            self.progress = 85

            self.logger.info("Calculating hashes...", module="RegistryModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                "Registry module completed successfully",
                module="RegistryModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Registry module failed: {e}",
                module="RegistryModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _copy_system_hives(self):
        try:
            hives_dir = self.output_dir / "hives"
            hives_dir.mkdir(exist_ok=True)

            for hive_name, hive_path in self.SYSTEM_HIVES.items():
                try:
                    output_file = hives_dir / hive_name

                    result = subprocess.run(
                        ['reg', 'save', f'HKLM\\{hive_name}', str(output_file)],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        self.collected_files.append(output_file)
                        self.logger.info(
                            f"Saved {hive_name} hive",
                            module="RegistryModule"
                        )
                    else:
                        self.logger.warning(
                            f"Failed to save {hive_name}: {result.stderr}",
                            module="RegistryModule"
                        )

                except Exception as e:
                    self.logger.error(
                        f"Error copying {hive_name}: {e}",
                        module="RegistryModule"
                    )

        except Exception as e:
            self.logger.error(
                f"Failed to copy system hives: {e}",
                module="RegistryModule"
            )

    def _copy_user_hives(self):
        try:
            users_dir = self.output_dir / "users"
            users_dir.mkdir(exist_ok=True)

            users_path = Path('C:/Users')

            if not users_path.exists():
                return

            for user_dir in users_path.iterdir():
                if not user_dir.is_dir():
                    continue

                if user_dir.name in ['Public', 'Default', 'Default User']:
                    continue

                ntuser_path = user_dir / 'NTUSER.DAT'

                if ntuser_path.exists():
                    try:
                        output_file = users_dir / f"{user_dir.name}_NTUSER.DAT"

                        result = subprocess.run(
                            ['reg', 'save', f'HKU\\{user_dir.name}', str(output_file)],
                            capture_output=True,
                            text=True
                        )

                        if result.returncode != 0:
                            try:
                                shutil.copy2(ntuser_path, output_file)
                            except:
                                self.logger.warning(
                                    f"Could not copy NTUSER.DAT for {user_dir.name}",
                                    module="RegistryModule"
                                )
                                continue

                        self.collected_files.append(output_file)
                        self.logger.info(
                            f"Copied NTUSER.DAT for user: {user_dir.name}",
                            module="RegistryModule"
                        )

                    except Exception as e:
                        self.logger.error(
                            f"Error copying NTUSER.DAT for {user_dir.name}: {e}",
                            module="RegistryModule"
                        )

        except Exception as e:
            self.logger.error(
                f"Failed to copy user hives: {e}",
                module="RegistryModule"
            )

    def _export_important_keys(self):
        try:
            keys_dir = self.output_dir / "keys"
            keys_dir.mkdir(exist_ok=True)

            for i, key_path in enumerate(self.IMPORTANT_KEYS):
                try:
                    safe_name = key_path.replace('\\', '_').replace(':', '')
                    output_file = keys_dir / f"{i:02d}_{safe_name}.reg"

                    result = subprocess.run(
                        ['reg', 'export', key_path, str(output_file), '/y'],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0 and output_file.exists():
                        self.collected_files.append(output_file)
                        self.logger.debug(
                            f"Exported key: {key_path}",
                            module="RegistryModule"
                        )
                    else:
                        self.logger.debug(
                            f"Key not found or export failed: {key_path}",
                            module="RegistryModule"
                        )

                except Exception as e:
                    self.logger.error(
                        f"Error exporting key {key_path}: {e}",
                        module="RegistryModule"
                    )

            self.logger.info(
                f"Exported {len([f for f in keys_dir.iterdir()])} registry keys",
                module="RegistryModule"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to export registry keys: {e}",
                module="RegistryModule"
            )

    def _generate_report(self):
        try:
            report_file = self.output_dir / "registry_report.txt"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("Registry Collection Report\n")
                f.write("=" * 80 + "\n\n")

                # 统计信息
                f.write("Collection Summary:\n")
                f.write("-" * 80 + "\n")

                hives_dir = self.output_dir / "hives"
                if hives_dir.exists():
                    hive_count = len(list(hives_dir.iterdir()))
                    f.write(f"System Hives Collected: {hive_count}\n")

                users_dir = self.output_dir / "users"
                if users_dir.exists():
                    user_count = len(list(users_dir.iterdir()))
                    f.write(f"User Hives Collected: {user_count}\n")

                keys_dir = self.output_dir / "keys"
                if keys_dir.exists():
                    key_count = len(list(keys_dir.iterdir()))
                    f.write(f"Registry Keys Exported: {key_count}\n")

                f.write("\n")

                f.write("Collected Files:\n")
                f.write("-" * 80 + "\n")

                for file_path in sorted(self.collected_files):
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    f.write(f"  {file_path.relative_to(self.output_dir)} - {size_mb:.2f}MB\n")

            self.collected_files.append(report_file)

        except Exception as e:
            self.logger.error(
                f"Failed to generate report: {e}",
                module="RegistryModule"
            )

    def _calculate_hashes(self):
        hash_file = self.output_dir / "hashes.txt"

        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write("File Hashes\n")
            f.write("=" * 80 + "\n\n")

            for file_path in self.collected_files:
                if file_path.exists() and file_path != hash_file:
                    hashes = self.hash_calculator.calculate_file_hashes(
                        file_path,
                        self.config.get("hash_algorithms", ["md5", "sha256"])
                    )

                    f.write(f"File: {file_path.relative_to(self.output_dir)}\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"  {algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="RegistryModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Registry module cleanup", module="RegistryModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "registry",
            "name": "Registry Collection",
            "version": "1.0.0",
            "description": "Collects Windows registry hives and exports important keys"
        }
