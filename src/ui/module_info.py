from dataclasses import dataclass
from typing import List


@dataclass
class ModuleInfo:
    id: str
    name: str
    description: str
    icon: str
    estimated_time: str
    storage_required: str
    requires_admin: bool
    dependencies: List[str]
    enabled_by_default: bool
    category: str


class ModuleRegistry:
    MODULES = [
        ModuleInfo(
            id="memory",
            name="Memory Collection",
            description="Captures complete RAM contents including running processes, "
                       "network connections, and encryption keys. Essential for detecting "
                       "fileless malware and analyzing volatile data.",
            icon="🧠",
            estimated_time="2-5 minutes",
            storage_required="~4-32 GB (depends on RAM size)",
            requires_admin=True,
            dependencies=[],
            enabled_by_default=True,
            category="volatile"
        ),
        ModuleInfo(
            id="disk",
            name="Disk Collection",
            description="Creates forensic images of physical and logical drives, "
                       "preserving deleted files and system artifacts. Captures MBR/GPT "
                       "structures and file system metadata.",
            icon="💾",
            estimated_time="30+ minutes",
            storage_required="Equal to disk size",
            requires_admin=True,
            dependencies=[],
            enabled_by_default=False,
            category="persistent"
        ),
        ModuleInfo(
            id="network",
            name="Network Collection",
            description="Documents active connections, ARP cache, routing tables, and "
                       "DNS cache. Optionally captures live network traffic for analysis.",
            icon="🌐",
            estimated_time="< 1 minute",
            storage_required="< 10 MB",
            requires_admin=False,
            dependencies=[],
            enabled_by_default=True,
            category="volatile"
        ),
        ModuleInfo(
            id="filesystem",
            name="File System Collection",
            description="Extracts file metadata, timestamps, NTFS attributes, and "
                       "alternate data streams. Identifies suspicious files and "
                       "preserves file system artifacts.",
            icon="📁",
            estimated_time="5-15 minutes",
            storage_required="~100 MB - 1 GB",
            requires_admin=False,
            dependencies=[],
            enabled_by_default=True,
            category="persistent"
        ),
        ModuleInfo(
            id="registry",
            name="Registry Collection",
            description="Exports Windows registry hives containing system configuration, "
                       "user accounts, installed software, and persistence mechanisms. "
                       "Critical for malware and forensic analysis.",
            icon="📋",
            estimated_time="1-3 minutes",
            storage_required="~100-500 MB",
            requires_admin=True,
            dependencies=[],
            enabled_by_default=True,
            category="persistent"
        ),
        ModuleInfo(
            id="live_system",
            name="Live System Collection",
            description="Captures running processes, services, scheduled tasks, and "
                       "user sessions. Essential for understanding system state at "
                       "the moment of collection.",
            icon="⚡",
            estimated_time="< 1 minute",
            storage_required="< 50 MB",
            requires_admin=False,
            dependencies=[],
            enabled_by_default=True,
            category="volatile"
        ),
        ModuleInfo(
            id="browser",
            name="Browser Artifacts",
            description="Extracts browsing history, cookies, cached data, and downloads "
                       "from Chrome, Firefox, Edge, and Internet Explorer. Reveals user "
                       "web activity and potential malicious sites.",
            icon="🌍",
            estimated_time="1-2 minutes",
            storage_required="~50-200 MB",
            requires_admin=False,
            dependencies=[],
            enabled_by_default=True,
            category="persistent"
        ),
        ModuleInfo(
            id="eventlogs",
            name="Event Logs",
            description="Copies Windows event logs including Security, System, Application, "
                       "and PowerShell logs. Critical for timeline analysis and detecting "
                       "suspicious activities.",
            icon="📜",
            estimated_time="2-5 minutes",
            storage_required="~100 MB - 2 GB",
            requires_admin=True,
            dependencies=[],
            enabled_by_default=True,
            category="persistent"
        ),
    ]

    @classmethod
    def get_all_modules(cls) -> List[ModuleInfo]:
        """Get list of all modules."""
        return cls.MODULES.copy()

    @classmethod
    def get_module_by_id(cls, module_id: str) -> ModuleInfo:
        for module in cls.MODULES:
            if module.id == module_id:
                return module
        return None

    @classmethod
    def get_modules_by_category(cls, category: str) -> List[ModuleInfo]:
        return [m for m in cls.MODULES if m.category == category]

    @classmethod
    def get_default_enabled_modules(cls) -> List[str]:
        return [m.id for m in cls.MODULES if m.enabled_by_default]
