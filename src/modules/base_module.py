from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum


class ModuleStatus(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class ICollectionModule(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = ModuleStatus.INITIALIZED
        self.progress = 0
        self.error_message = None

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def execute(self) -> bool:
        pass

    def get_status(self) -> ModuleStatus:
        return self.status

    def get_progress(self) -> int:
        return self.progress

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        pass
