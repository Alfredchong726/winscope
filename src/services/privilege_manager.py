import ctypes
import sys
from typing import Tuple
from src.services.logger import get_logger


class PrivilegeManager:
    def __init__(self):
        """Initialize privilege manager."""
        self.logger = get_logger()
        self._is_admin = None

    def is_admin(self) -> bool:
        if self._is_admin is not None:
            return self._is_admin

        try:
            self._is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

            status = "with" if self._is_admin else "without"
            self.logger.info(
                f"Running {status} administrator privileges",
                module="PrivilegeManager"
            )

            return self._is_admin

        except Exception as e:
            self.logger.error(
                f"Failed to check admin status: {e}",
                module="PrivilegeManager"
            )
            self._is_admin = False
            return False

    def request_elevation(self) -> bool:
        if self.is_admin():
            self.logger.info(
                "Already running as administrator",
                module="PrivilegeManager"
            )
            return True

        try:
            self.logger.info(
                "Requesting UAC elevation...",
                module="PrivilegeManager"
            )

            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )

            if ret > 32:
                sys.exit(0)
            else:
                self.logger.warning(
                    "UAC elevation declined or failed",
                    module="PrivilegeManager"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Failed to request elevation: {e}",
                module="PrivilegeManager",
                exc_info=True
            )
            return False

    def check_required_privileges(self, module_name: str) -> Tuple[bool, str]:
        privilege_requirements = {
            "memory": ("admin", "Memory collection requires administrator privileges"),
            "disk": ("admin", "Disk imaging requires administrator privileges"),
            "network": ("user", "Network collection available to all users"),
            "filesystem": ("user", "File system collection available to all users"),
            "registry": ("admin", "Registry collection requires administrator privileges"),
            "live_system": ("user", "Live system collection available to all users"),
            "browser": ("user", "Browser artifacts collection available to all users"),
            "event_logs": ("admin", "Event logs collection requires administrator privileges")
        }

        if module_name not in privilege_requirements:
            return True, "Unknown module, assuming no special privileges needed"

        required_level, message = privilege_requirements[module_name]

        if required_level == "admin" and not self.is_admin():
            return False, message

        return True, "Sufficient privileges"

    def get_privilege_status_report(self) -> dict:
        return {
            "is_admin": self.is_admin(),
            "can_collect_memory": self.is_admin(),
            "can_collect_disk": self.is_admin(),
            "can_collect_registry": self.is_admin(),
            "can_collect_event_logs": self.is_admin(),
            "can_collect_network": True,
            "can_collect_filesystem": True,
            "can_collect_browser": True,
            "can_collect_live_system": True
        }

    def enable_debug_privilege(self) -> bool:
        if not self.is_admin():
            self.logger.warning(
                "Cannot enable debug privilege without admin rights",
                module="PrivilegeManager"
            )
            return False

        try:
            SE_PRIVILEGE_ENABLED = 0x00000002
            TOKEN_ADJUST_PRIVILEGES = 0x00000020
            TOKEN_QUERY = 0x00000008

            token = ctypes.c_void_p()
            ctypes.windll.advapi32.OpenProcessToken(
                ctypes.windll.kernel32.GetCurrentProcess(),
                TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY,
                ctypes.byref(token)
            )

            luid = ctypes.c_int64()
            ctypes.windll.advapi32.LookupPrivilegeValueW(
                None,
                "SeDebugPrivilege",
                ctypes.byref(luid)
            )

            class TOKEN_PRIVILEGES(ctypes.Structure):
                _fields_ = [
                    ("PrivilegeCount", ctypes.c_ulong),
                    ("Luid", ctypes.c_int64),
                    ("Attributes", ctypes.c_ulong)
                ]

            tp = TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Luid = luid.value
            tp.Attributes = SE_PRIVILEGE_ENABLED

            result = ctypes.windll.advapi32.AdjustTokenPrivileges(
                token,
                False,
                ctypes.byref(tp),
                0,
                None,
                None
            )

            if result:
                self.logger.info(
                    "SeDebugPrivilege enabled successfully",
                    module="PrivilegeManager"
                )
                return True
            else:
                self.logger.warning(
                    "Failed to enable SeDebugPrivilege",
                    module="PrivilegeManager"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error enabling debug privilege: {e}",
                module="PrivilegeManager",
                exc_info=True
            )
            return False
