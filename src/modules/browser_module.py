import shutil
from pathlib import Path
from typing import Dict, Any, List
import os

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class BrowserModule(ICollectionModule):
    BROWSER_PATHS = {
        'chrome': {
            'name': 'Google Chrome',
            'base': 'AppData/Local/Google/Chrome/User Data',
            'files': {
                'history': 'Default/History',
                'cookies': 'Default/Cookies',
                'bookmarks': 'Default/Bookmarks',
                'downloads': 'Default/History'
            }
        },
        'edge': {
            'name': 'Microsoft Edge',
            'base': 'AppData/Local/Microsoft/Edge/User Data',
            'files': {
                'history': 'Default/History',
                'cookies': 'Default/Cookies',
                'bookmarks': 'Default/Bookmarks',
                'downloads': 'Default/History'
            }
        },
        'firefox': {
            'name': 'Mozilla Firefox',
            'base': 'AppData/Roaming/Mozilla/Firefox/Profiles',
            'files': {
                'history': 'places.sqlite',
                'cookies': 'cookies.sqlite',
                'bookmarks': 'places.sqlite',
                'downloads': 'places.sqlite'
            }
        }
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "browser"))
        self.collected_files = []
        self.include_cookies = config.get("include_cookies", False)

    def initialize(self) -> bool:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Browser module initialized, output: {self.output_dir}",
                module="BrowserModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize browser module: {e}",
                module="BrowserModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            user_home = Path.home()
            browsers_found = 0

            for browser_id, browser_config in self.BROWSER_PATHS.items():
                browser_name = browser_config['name']
                self.logger.info(
                    f"Checking for {browser_name}...",
                    module="BrowserModule"
                )

                if self._collect_browser(user_home, browser_id, browser_config):
                    browsers_found += 1

                self.progress += (80 // len(self.BROWSER_PATHS))

            if browsers_found == 0:
                self.logger.warning(
                    "No browser data found",
                    module="BrowserModule"
                )
            else:
                self.logger.info(
                    f"Collected data from {browsers_found} browser(s)",
                    module="BrowserModule"
                )

            self.logger.info("Calculating hashes...", module="BrowserModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            return True

        except Exception as e:
            self.logger.error(
                f"Browser module failed: {e}",
                module="BrowserModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_browser(
        self,
        user_home: Path,
        browser_id: str,
        config: Dict
    ) -> bool:
        try:
            browser_name = config['name']
            base_path = user_home / config['base']

            if not base_path.exists():
                self.logger.debug(
                    f"{browser_name} not found at {base_path}",
                    module="BrowserModule"
                )
                return False

            self.logger.info(
                f"Found {browser_name}, collecting data...",
                module="BrowserModule"
            )

            browser_output = self.output_dir / browser_id
            browser_output.mkdir(parents=True, exist_ok=True)

            collected_any = False

            if browser_id == 'firefox':
                collected_any = self._collect_firefox(base_path, browser_output, config)
            else:
                for file_type, file_path in config['files'].items():
                    if file_type == 'cookies' and not self.include_cookies:
                        continue

                    source_file = base_path / file_path

                    if source_file.exists():
                        dest_file = browser_output / f"{file_type}.db"

                        try:
                            shutil.copy2(source_file, dest_file)

                            self.collected_files.append(dest_file)
                            collected_any = True

                            self.logger.info(
                                f"Collected {browser_name} {file_type}",
                                module="BrowserModule"
                            )
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to copy {browser_name} {file_type}: {e}",
                                module="BrowserModule"
                            )

            if collected_any:
                self._create_browser_metadata(browser_output, browser_name, browser_id)

            return collected_any

        except Exception as e:
            self.logger.error(
                f"Error collecting {config['name']}: {e}",
                module="BrowserModule"
            )
            return False

    def _collect_firefox(
        self,
        profiles_dir: Path,
        output_dir: Path,
        config: Dict
    ) -> bool:
        try:
            collected_any = False

            if not profiles_dir.exists():
                return False

            for profile_dir in profiles_dir.iterdir():
                if not profile_dir.is_dir():
                    continue

                profile_output = output_dir / profile_dir.name
                profile_output.mkdir(parents=True, exist_ok=True)

                for file_type, file_name in config['files'].items():
                    if file_type == 'cookies' and not self.include_cookies:
                        continue

                    source_file = profile_dir / file_name

                    if source_file.exists():
                        dest_file = profile_output / f"{file_type}.db"

                        try:
                            shutil.copy2(source_file, dest_file)
                            self.collected_files.append(dest_file)
                            collected_any = True

                            self.logger.info(
                                f"Collected Firefox {file_type} from profile {profile_dir.name}",
                                module="BrowserModule"
                            )
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to copy Firefox {file_type}: {e}",
                                module="BrowserModule"
                            )
                            return collected_any
        except Exception as e:
            self.logger.error(f"Error collecting Firefox: {e}", module="BrowserModule")
            return False

    def _create_browser_metadata(
        self,
        output_dir: Path,
        browser_name: str,
        browser_id: str
    ):
        try:
            import json
            from datetime import datetime

            metadata = {
                "browser": browser_name,
                "browser_id": browser_id,
                "collection_time": datetime.now().isoformat(),
                "collected_files": [f.name for f in output_dir.iterdir() if f.is_file()]
            }

            metadata_file = output_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)

            self.collected_files.append(metadata_file)

        except Exception as e:
            self.logger.error(
                f"Failed to create metadata: {e}",
                module="BrowserModule"
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

                    f.write(f"File: {file_path.relative_to(self.output_dir)}\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"  {algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="BrowserModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Browser module cleanup", module="BrowserModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "browser",
            "name": "Browser Artifacts Collection",
            "version": "1.0.0",
            "description": "Collects browsing history, bookmarks, and downloads from Chrome, Firefox, and Edge"
        }
