import logging
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.output_dir: Optional[Path] = None
        self.text_log_path: Optional[Path] = None
        self.csv_log_path: Optional[Path] = None
        self.csv_file = None
        self.csv_writer = None

        self.logger = logging.getLogger("EvidenceCollector")
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def initialize(self, output_dir: Path) -> bool:
        try:
            self.close()

            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            self.text_log_path = self.output_dir / f"collection_{timestamp}.log"
            file_handler = logging.FileHandler(self.text_log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

            self.csv_log_path = self.output_dir / f"collection_{timestamp}.csv"
            self.csv_file = open(self.csv_log_path, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)

            self.csv_writer.writerow([
                'Timestamp',
                'Level',
                'Module',
                'Action',
                'Status',
                'Details',
                'File_Path',
                'File_Size',
                'Hash_MD5',
                'Hash_SHA256'
            ])
            self.csv_file.flush()

            self.info("Logger initialized", module="LoggerService")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize file logging: {e}")
            return False

    def log_collection(
        self,
        module: str,
        action: str,
        status: str,
        details: str = "",
        file_path: str = "",
        file_size: int = 0,
        hash_md5: str = "",
        hash_sha256: str = ""
    ) -> None:
        if self.csv_writer:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.csv_writer.writerow([
                timestamp,
                'COLLECTION',
                module,
                action,
                status,
                details,
                file_path,
                file_size,
                hash_md5,
                hash_sha256
            ])
            self.csv_file.flush()

    def debug(self, message: str, module: str = "") -> None:
        self.logger.debug(f"[{module}] {message}" if module else message)

    def info(self, message: str, module: str = "") -> None:
        self.logger.info(f"[{module}] {message}" if module else message)

    def warning(self, message: str, module: str = "") -> None:
        self.logger.warning(f"[{module}] {message}" if module else message)

    def error(self, message: str, module: str = "", exc_info: bool = False) -> None:
        self.logger.error(f"[{module}] {message}" if module else message, exc_info=exc_info)

    def critical(self, message: str, module: str = "") -> None:
        self.logger.critical(f"[{module}] {message}" if module else message)

    def close(self) -> None:
        if self.csv_file:
            try:
                self.csv_file.close()
            except Exception:
                pass
            finally:
                self.csv_file = None
                self.csv_writer = None

        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                try:
                    handler.close()
                except Exception:
                    pass
                finally:
                    self.logger.removeHandler(handler)

    def reset(self) -> None:
        self.close()
        self.output_dir = None
        self.text_log_path = None
        self.csv_log_path = None
        self._initialized = False

        LoggerService._instance = None


def get_logger() -> LoggerService:
    return LoggerService()
