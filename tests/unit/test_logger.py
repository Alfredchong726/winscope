import pytest
from pathlib import Path
import tempfile
import shutil
import time
from src.services.logger import LoggerService, get_logger


class TestLoggerService:

    def setup_method(self):
        if LoggerService._instance:
            LoggerService._instance.reset()

        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        if LoggerService._instance:
            LoggerService._instance.close()
            LoggerService._instance.reset()

        time.sleep(0.1)

        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                time.sleep(0.5)
                shutil.rmtree(self.temp_dir)

    def test_singleton_pattern(self):
        logger1 = LoggerService()
        logger2 = LoggerService()
        assert logger1 is logger2

    def test_get_logger_function(self):
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2

    def test_initialize_creates_files(self):
        logger = LoggerService()
        success = logger.initialize(self.temp_dir)

        assert success is True
        assert logger.text_log_path is not None
        assert logger.csv_log_path is not None
        assert logger.text_log_path.exists()
        assert logger.csv_log_path.exists()

    def test_log_collection(self):
        logger = LoggerService()
        logger.initialize(self.temp_dir)

        logger.log_collection(
            module="TestModule",
            action="Test Action",
            status="Success",
            details="Test details",
            file_path="/test/path",
            file_size=1024,
            hash_md5="abc123",
            hash_sha256="def456"
        )

        logger.csv_file.flush()

        csv_content = logger.csv_log_path.read_text(encoding='utf-8')
        assert "TestModule" in csv_content
        assert "Test Action" in csv_content
        assert "Success" in csv_content
        assert "abc123" in csv_content
        assert "def456" in csv_content

    def test_multiple_log_levels(self):
        logger = LoggerService()
        logger.initialize(self.temp_dir)

        logger.debug("Debug message", module="Test")
        logger.info("Info message", module="Test")
        logger.warning("Warning message", module="Test")
        logger.error("Error message", module="Test")

        log_content = logger.text_log_path.read_text(encoding='utf-8')

        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content

    def test_close_and_reopen(self):
        logger = LoggerService()

        logger.initialize(self.temp_dir)
        logger.info("First message")
        first_log_path = logger.text_log_path
        logger.close()

        time.sleep(0.1)

        logger.initialize(self.temp_dir)
        logger.info("Second message")
        second_log_path = logger.text_log_path

        assert first_log_path != second_log_path
        assert first_log_path.exists()
        assert second_log_path.exists()
