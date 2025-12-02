import pytest
from pathlib import Path
import tempfile
import shutil
from src.services.config_manager import ConfigManager


class TestConfigManager:

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        config = ConfigManager(self.temp_dir)

        assert config.config is not None
        assert "output_directory" in config.config
        assert "modules" in config.config

    def test_get_config_value(self):
        config = ConfigManager(self.temp_dir)

        algorithms = config.get("hashing.algorithms")
        assert isinstance(algorithms, list)
        assert "md5" in algorithms

    def test_set_config_value(self):
        config = ConfigManager(self.temp_dir)

        config.set("output_directory", "D:/Evidence")
        assert config.get("output_directory") == "D:/Evidence"

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = ConfigManager(self.temp_dir)

        config.set("output_directory", "D:/Test")
        config.set("hashing.algorithms", ["sha256"])

        assert config.save_config() is True

        config2 = ConfigManager(self.temp_dir)
        config2.load_config()

        assert config2.get("output_directory") == "D:/Test"
        assert config2.get("hashing.algorithms") == ["sha256"]

    def test_save_profile(self):
        config = ConfigManager(self.temp_dir)

        config.set("output_directory", "D:/QuickScan")
        success = config.save_profile("Quick Scan", "Fast evidence collection")

        assert success is True

    def test_load_profile(self):
        config = ConfigManager(self.temp_dir)

        config.set("output_directory", "D:/FullForensics")
        config.save_profile("Full Forensics")

        config.set("output_directory", "D:/Other")

        config.load_profile("Full Forensics")

        assert config.get("output_directory") == "D:/FullForensics"

    def test_list_profiles(self):
        config = ConfigManager(self.temp_dir)

        config.save_profile("Profile1", "Description 1")
        config.save_profile("Profile2", "Description 2")

        profiles = config.list_profiles()

        assert len(profiles) == 2
        profile_names = [p["name"] for p in profiles]
        assert "Profile1" in profile_names
        assert "Profile2" in profile_names

    def test_delete_profile(self):
        config = ConfigManager(self.temp_dir)

        config.save_profile("ToDelete")
        assert config.delete_profile("ToDelete") is True

        profiles = config.list_profiles()
        profile_names = [p["name"] for p in profiles]
        assert "ToDelete" not in profile_names

    def test_reset_to_defaults(self):
        config = ConfigManager(self.temp_dir)

        config.set("output_directory", "D:/Modified")

        # Reset
        config.reset_to_defaults()

        default_dir = config.get("output_directory")
        assert default_dir != "D:/Modified"
