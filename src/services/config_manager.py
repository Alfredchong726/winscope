import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.services.logger import get_logger


class ConfigManager:
    DEFAULT_CONFIG_DIR = Path.home() / ".evidence_collector"
    DEFAULT_CONFIG_FILE = "config.json"
    PROFILES_FILE = "profiles.json"

    def __init__(self, config_dir: Optional[Path] = None):
        self.logger = get_logger()
        self.config_dir = Path(config_dir) if config_dir else self.DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILE
        self.profiles_file = self.config_dir / self.PROFILES_FILE

        self.config: Dict[str, Any] = self._get_default_config()

        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Config directory ready: {self.config_dir}", module="ConfigManager")
        except Exception as e:
            self.logger.error(
                f"Failed to create config directory: {e}",
                module="ConfigManager"
            )

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "output_directory": str(Path.home() / "Documents" / "Evidence_Collections"),
            "compression": {
                "enabled": True,
                "format": "zip"
            },
            "hashing": {
                "algorithms": ["md5", "sha256"],
                "verify_after_collection": True
            },
            "modules": {
                "memory": {
                    "enabled": True,
                    "dump_format": "raw"
                },
                "disk": {
                    "enabled": False,
                    "create_image": False
                },
                "network": {
                    "enabled": True,
                    "capture_packets": False
                },
                "filesystem": {
                    "enabled": True,
                    "include_system_files": False
                },
                "registry": {
                    "enabled": True,
                    "export_format": "hive"
                },
                "live_system": {
                    "enabled": True
                },
                "browser": {
                    "enabled": True,
                    "browsers": ["chrome", "firefox", "edge"]
                },
                "event_logs": {
                    "enabled": True,
                    "convert_to_csv": False
                }
            },
            "ui": {
                "show_advanced_options": False,
                "log_detail_level": "info",
                "theme": "light"
            },
            "general": {
                "check_admin_privileges": True,
                "create_report": True,
                "package_naming": "Evidence_{timestamp}"
            }
        }

    def load_config(self) -> bool:
        try:
            if not self.config_file.exists():
                self.logger.info(
                    "Config file not found, using defaults",
                    module="ConfigManager"
                )
                return False

            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)

            self.config = self._merge_configs(self._get_default_config(), loaded_config)

            self.logger.info("Configuration loaded successfully", module="ConfigManager")
            return True

        except json.JSONDecodeError as e:
            self.logger.error(
                f"Invalid JSON in config file: {e}",
                module="ConfigManager"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Failed to load config: {e}",
                module="ConfigManager",
                exc_info=True
            )
            return False

    def save_config(self) -> bool:
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            self.logger.info(
                f"Configuration saved to {self.config_file}",
                module="ConfigManager"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to save config: {e}",
                module="ConfigManager",
                exc_info=True
            )
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

        self.logger.debug(
            f"Config updated: {key_path} = {value}",
            module="ConfigManager"
        )

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def save_profile(self, profile_name: str, description: str = "") -> bool:
        try:
            profiles = self._load_profiles()

            profiles[profile_name] = {
                "description": description,
                "config": self.config.copy()
            }

            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=4, ensure_ascii=False)

            self.logger.info(
                f"Profile '{profile_name}' saved",
                module="ConfigManager"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to save profile: {e}",
                module="ConfigManager",
                exc_info=True
            )
            return False

    def load_profile(self, profile_name: str) -> bool:
        try:
            profiles = self._load_profiles()

            if profile_name not in profiles:
                self.logger.warning(
                    f"Profile '{profile_name}' not found",
                    module="ConfigManager"
                )
                return False

            self.config = profiles[profile_name]["config"]

            self.logger.info(
                f"Profile '{profile_name}' loaded",
                module="ConfigManager"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to load profile: {e}",
                module="ConfigManager",
                exc_info=True
            )
            return False

    def list_profiles(self) -> List[Dict[str, str]]:
        try:
            profiles = self._load_profiles()
            return [
                {
                    "name": name,
                    "description": data.get("description", "")
                }
                for name, data in profiles.items()
            ]
        except Exception:
            return []

    def delete_profile(self, profile_name: str) -> bool:
        try:
            profiles = self._load_profiles()

            if profile_name in profiles:
                del profiles[profile_name]

                with open(self.profiles_file, 'w', encoding='utf-8') as f:
                    json.dump(profiles, f, indent=4, ensure_ascii=False)

                self.logger.info(
                    f"Profile '{profile_name}' deleted",
                    module="ConfigManager"
                )
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(
                f"Failed to delete profile: {e}",
                module="ConfigManager",
                exc_info=True
            )
            return False

    def _load_profiles(self) -> Dict:
        if not self.profiles_file.exists():
            return {}

        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def reset_to_defaults(self) -> None:
        self.config = self._get_default_config()
        self.logger.info("Configuration reset to defaults", module="ConfigManager")

    def get_all(self) -> Dict[str, Any]:
        return self.config.copy()
