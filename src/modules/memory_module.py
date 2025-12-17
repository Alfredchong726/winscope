import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
import time

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class MemoryModule(ICollectionModule):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "memory"))
        self.collected_files = []

        self.acquisition_tool = config.get("tool", "winpmem")
        self.winpmem_version = "2.0"

    def initialize(self) -> bool:
        try:
            import ctypes

            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.logger.error(
                    "Memory module requires administrator privileges", module="MemoryModule"
                )
                self.status = ModuleStatus.FAILED
                self.error_message = "Administrator privileges required"
                return False

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Memory module initialized, output: {self.output_dir}", module="MemoryModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize memory module: {e}", module="MemoryModule", exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Collecting system information...", module="MemoryModule")
            system_info = self._collect_system_info()
            self.progress = 10

            self.logger.info("Acquiring memory image...", module="MemoryModule")
            memory_file = self._acquire_memory()
            if not memory_file:
                return False
            self.progress = 70

            self.logger.info("Generating Volatility metadata...", module="MemoryModule")
            self._generate_volatility_metadata(memory_file, system_info)
            self.progress = 85

            self.logger.info("Calculating memory image hash...", module="MemoryModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info("Memory module completed successfully", module="MemoryModule")
            return True

        except Exception as e:
            self.logger.error(f"Memory module failed: {e}", module="MemoryModule", exc_info=True)
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_system_info(self) -> Dict[str, Any]:
        import platform
        import psutil

        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "acquisition_time": datetime.now().isoformat(),
        }

        info_file = self.output_dir / "system_info.json"
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)

        self.collected_files.append(info_file)

        return info

    def _acquire_memory_with_winpmem(self, winpmem_path: Path, output_file: Path) -> bool:
        try:
            if self.winpmem_version == "3.0":
                cmd = [str(winpmem_path), str(output_file), "--format", "raw"]
            else:
                cmd = [str(winpmem_path), str(output_file)]

            self.logger.info(
                f"Starting memory acquisition with command: {' '.join(cmd)}", module="MemoryModule"
            )

            start_time = time.time()

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            elapsed_time = time.time() - start_time

            if result.stdout:
                self.logger.debug(
                    f"WinPmem stdout (first 500 chars): {result.stdout[:500]}",
                    module="MemoryModule",
                )

            if result.stderr:
                self.logger.debug(f"WinPmem stderr: {result.stderr}", module="MemoryModule")

            self.logger.info(
                f"WinPmem process completed with return code: {result.returncode}",
                module="MemoryModule",
            )

            if not output_file.exists():
                self.logger.error("Memory dump file was not created", module="MemoryModule")
                self._create_winpmem_error_report(
                    winpmem_path,
                    cmd,
                    result.returncode,
                    result.stdout,
                    result.stderr,
                    "Output file not created",
                )
                return False

            file_size_bytes = output_file.stat().st_size
            file_size_gb = file_size_bytes / (1024**3)
            file_size_mb = file_size_bytes / (1024**2)

            self.logger.info(
                f"Memory dump file created: {file_size_gb:.2f} GB ({file_size_mb:.2f} MB)",
                module="MemoryModule",
            )

            min_size_mb = 100

            if file_size_mb < min_size_mb:
                self.logger.warning(
                    f"Memory dump seems too small: {file_size_mb:.2f} MB (expected at least {min_size_mb} MB)",
                    module="MemoryModule",
                )

                self.logger.warning(
                    "The file has been kept for inspection, but may be invalid",
                    module="MemoryModule",
                )

            self.logger.info(
                f"✓ Memory acquisition completed in {elapsed_time:.1f} seconds",
                module="MemoryModule",
            )

            self.collected_files.append(output_file)

            self._create_acquisition_metadata(
                output_file, elapsed_time, result.returncode, result.stdout
            )

            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Memory acquisition timed out (>1 hour)", module="MemoryModule")
            return False

        except Exception as e:
            self.logger.error(
                f"Error during memory acquisition: {e}", module="MemoryModule", exc_info=True
            )
            return False

    def _create_acquisition_metadata(
        self, memory_file: Path, elapsed_time: float, return_code: int, stdout: str
    ):
        try:
            metadata_file = self.output_dir / "acquisition_metadata.json"

            import json
            from datetime import datetime

            memory_ranges = []
            acquisition_method = "Unknown"

            if stdout:
                for line in stdout.split("\n"):
                    if line.startswith("Start"):
                        memory_ranges.append(line.strip())
                    elif "Acquitision mode" in line or "Acquisition mode" in line:
                        acquisition_method = line.split(":")[-1].strip()

            metadata = {
                "file": memory_file.name,
                "file_size_bytes": memory_file.stat().st_size,
                "file_size_gb": round(memory_file.stat().st_size / (1024**3), 2),
                "acquisition_time": datetime.now().isoformat(),
                "elapsed_time_seconds": round(elapsed_time, 1),
                "tool": "WinPmem",
                "tool_version": self.winpmem_version,
                "acquisition_method": acquisition_method,
                "memory_ranges": memory_ranges,
                "return_code": return_code,
                "status": "completed",
            }

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)

            self.collected_files.append(metadata_file)

            self.logger.info(f"Acquisition metadata saved: {metadata_file}", module="MemoryModule")

        except Exception as e:
            self.logger.error(f"Failed to create acquisition metadata: {e}", module="MemoryModule")

    def _create_winpmem_error_report(
        self,
        winpmem_path: Path,
        command: list,
        return_code: int,
        stdout: str,
        stderr: str,
        error_reason: str,
    ):
        try:
            error_file = self.output_dir / "winpmem_error_report.txt"

            with open(error_file, "w", encoding="utf-8") as f:
                f.write(
                    """
                        ╔═══════════════════════════════════════════════════════════════════════╗
                        ║           WinPmem Memory Acquisition Error Report                      ║
                        ╚═══════════════════════════════════════════════════════════════════════╝

                        """
                )
                f.write(f"Error Reason: {error_reason}\n\n")

                f.write("Command Executed:\n")
                f.write("-" * 70 + "\n")
                f.write(f"{' '.join(command)}\n\n")

                f.write(f"Return Code: {return_code}\n\n")

                f.write("Standard Output:\n")
                f.write("-" * 70 + "\n")
                f.write(stdout if stdout else "(empty)\n")
                f.write("\n")

                f.write("Standard Error:\n")
                f.write("-" * 70 + "\n")
                f.write(stderr if stderr else "(empty)\n")
                f.write("\n")

                f.write(
                    """
                        Troubleshooting:
                        ----------------
                        1. Check if you're running as Administrator
                        2. Ensure sufficient disk space (size = RAM size)
                        3. Try disabling antivirus temporarily
                        4. Check Windows Event Viewer for driver errors
                        5. Try alternative tool: DumpIt or FTK Imager

                        Manual Acquisition:
                        -------------------
                        Try running WinPmem manually:
                        """
                )
                f.write(f"cd {winpmem_path.parent}\n")
                f.write(f"winpmem.exe manual_memory.raw\n")

            self.collected_files.append(error_file)
            self.logger.info(f"Created error report: {error_file}", module="MemoryModule")

        except Exception as e:
            self.logger.error(f"Failed to create error report: {e}", module="MemoryModule")

    def _acquire_memory(self) -> Optional[Path]:
        output_file = self.output_dir / f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.raw"

        try:
            project_root = Path(__file__).parent.parent.parent
            winpmem_path = project_root / "tools" / "winpmem" / "winpmem.exe"

            self.logger.info(f"Looking for WinPmem at: {winpmem_path}", module="MemoryModule")

            if not winpmem_path.exists():
                self.logger.warning(f"WinPmem not found at: {winpmem_path}", module="MemoryModule")
                self._create_instruction_file(winpmem_path)
                return None

            self.logger.info("Detecting WinPmem version...", module="MemoryModule")

            try:
                version_result = subprocess.run(
                    [str(winpmem_path), "--help"], capture_output=True, text=True, timeout=10
                )

                version_output = version_result.stdout + version_result.stderr

                if "Version 3" in version_output or "v3." in version_output:
                    self.winpmem_version = "3.0"
                elif "Version 2" in version_output or "v2." in version_output:
                    self.winpmem_version = "2.0"
                else:
                    self.winpmem_version = "2.0"

                self.logger.info(
                    f"Detected WinPmem version: {self.winpmem_version}", module="MemoryModule"
                )

            except Exception as e:
                self.logger.warning(
                    f"Could not detect WinPmem version, assuming 2.0: {e}", module="MemoryModule"
                )
                self.winpmem_version = "2.0"

            success = self._acquire_memory_with_winpmem(winpmem_path, output_file)

            if success:
                return output_file
            else:
                return None

        except Exception as e:
            self.logger.error(
                f"Error during memory acquisition: {e}", module="MemoryModule", exc_info=True
            )
            return None

    def _detect_winpmem_version(self, winpmem_path: Path) -> dict:
        try:
            result = subprocess.run(
                [str(winpmem_path), "--help"], capture_output=True, text=True, timeout=10
            )

            output = result.stdout + result.stderr

            version = "unknown"
            if "v4" in output.lower() or "4.0" in output:
                version = "4.0"
            elif "v3" in output.lower() or "3.0" in output:
                version = "3.0"
            elif "v2" in output.lower() or "2.0" in output:
                version = "2.0"

            supports_format = "--format" in output or "-f" in output
            supports_output = "-o" in output or "--output" in output

            return {
                "version": version,
                "supports_format": supports_format,
                "supports_output": supports_output,
                "help_output": output,
            }

        except Exception as e:
            self.logger.error(f"Failed to detect version: {e}", module="MemoryModule")
            return None

    def _build_winpmem_command(
        self, winpmem_path: Path, output_file: Path, version_info: dict
    ) -> list:
        cmd = [str(winpmem_path)]

        if version_info["version"] == "4.0":
            cmd.append(str(output_file))

        elif version_info["version"] == "3.0":
            if version_info["supports_output"]:
                cmd.extend(["-o", str(output_file)])
            else:
                cmd.append(str(output_file))

        else:
            cmd.append(str(output_file))

        return cmd

    def _create_instruction_file(self, winpmem_path: Path, error: str = None):
        instruction_file = self.output_dir / "MEMORY_ACQUISITION_INSTRUCTIONS.txt"

        with open(instruction_file, "w", encoding="utf-8") as f:
            f.write(
                f"""
                    ╔═══════════════════════════════════════════════════════════════════════╗
                    ║           Memory Acquisition Instructions                             ║
                    ╚═══════════════════════════════════════════════════════════════════════╝

                    {f"❌ Error: {error}" if error else "⚠️  WinPmem Not Found"}

                    Expected Location:
                    ------------------
                    {winpmem_path}

                    📥 How to Download WinPmem:
                    ---------------------------
                    1. Visit: https://github.com/Velocidex/WinPmem/releases
                    2. Download the latest release (winpmem_mini_x64_*.exe)
                    3. Rename to: winpmem.exe
                    4. Place at: {winpmem_path.parent}

                    Current directory listing:
                    {'-' * 40}
                    """
            )

            tools_dir = winpmem_path.parent
            if tools_dir.exists():
                f.write(f"Contents of {tools_dir}:\n")
                for item in tools_dir.iterdir():
                    f.write(f"  - {item.name}\n")
            else:
                f.write(f"Directory does not exist: {tools_dir}\n")

            f.write(
                f"""

                    💡 Manual Memory Acquisition:
                    ------------------------------
                    If you have WinPmem installed elsewhere, you can run it manually:

                    1. Open Command Prompt as Administrator
                    2. Navigate to WinPmem location
                    3. Run: winpmem.exe memory.raw
                    4. Place memory.raw in: {self.output_dir}

                    📋 Alternative Tools:
                    ---------------------
                    1. DumpIt (Magnet Forensics)
                    Download: https://www.magnetforensics.com/

                    2. FTK Imager (AccessData)
                    Download: https://www.exterro.com/

                    3. Belkasoft RAM Capturer
                    Download: https://belkasoft.com/ram-capturer

                    For Volatility Analysis:
                    ------------------------
                    vol.py -f memory.raw windows.info
                    vol.py -f memory.raw windows.pslist
                    vol.py -f memory.raw windows.netscan
                    """
            )

        self.collected_files.append(instruction_file)

    def _create_error_report(self, winpmem_path: Path, cmd: list, result, error_msg: str):
        error_file = self.output_dir / "winpmem_error_report.txt"

        with open(error_file, "w", encoding="utf-8") as f:
            f.write(
                f"""
                    ╔═══════════════════════════════════════════════════════════════════════╗
                    ║              WinPmem Error Report                                     ║
                    ╚═══════════════════════════════════════════════════════════════════════╝

                    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    Command Executed:
                    -----------------
                    {' '.join(str(x) for x in cmd)}

                    Return Code: {result.returncode}

                    STDOUT:
                    -------
                    {result.stdout if result.stdout else '(empty)'}

                    STDERR:
                    -------
                    {result.stderr if result.stderr else '(empty)'}

                    Error Message:
                    --------------
                    {error_msg}

                    Troubleshooting:
                    ----------------
                    1. Verify Administrator Privileges
                    - Right-click WinScope > Run as Administrator

                    2. Check Antivirus
                    - Some antivirus software blocks memory acquisition tools
                    - Add exception for: {winpmem_path}

                    3. Verify WinPmem Integrity
                    - Re-download from official source
                    - Check file is not corrupted

                    4. Test WinPmem Manually
                    - Open Command Prompt as Administrator
                    - Run: {winpmem_path} --help
                    - If this fails, WinPmem installation is problematic

                    5. Check Disk Space
                    - Memory dump requires space equal to RAM size
                    - Verify sufficient space at output location

                    6. Try Alternative Format
                    - Some systems require specific WinPmem versions
                    - Try WinPmem v3.x or v4.x

                    For Support:
                    ------------
                    - GitHub Issues: https://github.com/Velocidex/WinPmem/issues
                    - Include this error report when seeking help
                    """
            )

        self.collected_files.append(error_file)
        self.logger.info(f"Created error report: {error_file}", module="MemoryModule")

    def _generate_volatility_metadata(self, memory_file: Path, system_info: Dict):
        try:
            metadata_file = self.output_dir / "volatility_analysis_guide.txt"

            os_version = system_info.get("os_version", "")
            architecture = system_info.get("architecture", "")

            if "Windows-10" in os_version:
                if "AMD64" in architecture or "x86_64" in architecture:
                    profile = "Win10x64"
                else:
                    profile = "Win10x86"
            elif "Windows-11" in os_version:
                profile = "Win10x64"
            else:
                profile = "WinXPSP2x86"

            with open(metadata_file, "w") as f:
                f.write(
                    f"""
Volatility Analysis Guide
==========================

Memory Image: {memory_file.name}
Size: {memory_file.stat().st_size / (1024**3):.2f} GB
Acquired: {system_info.get('acquisition_time', '')}

System Information:
-------------------
OS: {system_info.get('os', '')} {system_info.get('os_release', '')}
Version: {system_info.get('os_version', '')}
Architecture: {system_info.get('architecture', '')}
Total Memory: {system_info.get('total_memory_gb', 0)} GB

Volatility 2.x Commands:
------------------------
Profile: {profile}

# List processes
volatility -f {memory_file.name} --profile={profile} pslist

# List network connections
volatility -f {memory_file.name} --profile={profile} netscan

# Dump process memory
volatility -f {memory_file.name} --profile={profile} memdump -p PID -D output/

# List DLLs
volatility -f {memory_file.name} --profile={profile} dlllist

# Find hidden processes
volatility -f {memory_file.name} --profile={profile} psxview

# Extract command history
volatility -f {memory_file.name} --profile={profile} cmdscan
volatility -f {memory_file.name} --profile={profile} consoles

# Registry analysis
volatility -f {memory_file.name} --profile={profile} hivelist
volatility -f {memory_file.name} --profile={profile} printkey -K "SAM\\Domains\\Account\\Users"

# Malware detection
volatility -f {memory_file.name} --profile={profile} malfind
volatility -f {memory_file.name} --profile={profile} apihooks


Volatility 3.x Commands:
------------------------
# List processes
vol.py -f {memory_file.name} windows.pslist

# List network connections
vol.py -f {memory_file.name} windows.netscan

# Dump process
vol.py -f {memory_file.name} windows.memmap --pid PID --dump

# List DLLs
vol.py -f {memory_file.name} windows.dlllist

# Command history
vol.py -f {memory_file.name} windows.cmdline

# Registry
vol.py -f {memory_file.name} windows.registry.hivelist
vol.py -f {memory_file.name} windows.registry.printkey

# Malware detection
vol.py -f {memory_file.name} windows.malfind


Recommended Analysis Workflow:
-------------------------------
1. Identify running processes (pslist)
2. Check network connections (netscan)
3. Look for hidden/suspicious processes (psxview, malfind)
4. Extract command history (cmdscan, consoles)
5. Analyze registry for persistence (printkey)
6. Dump suspicious process memory for further analysis

For more information:
- Volatility 2: https://github.com/volatilityfoundation/volatility
- Volatility 3: https://github.com/volatilityfoundation/volatility3
- Volatility Cheat Sheet: https://downloads.volatilityfoundation.org/releases/2.4/CheatSheet_v2.4.pdf

"""
                )

            self.collected_files.append(metadata_file)

        except Exception as e:
            self.logger.error(f"Failed to generate Volatility metadata: {e}", module="MemoryModule")

    def _calculate_hashes(self):
        hash_file = self.output_dir / "hashes.txt"

        with open(hash_file, "w", encoding="utf-8") as f:
            f.write("Memory Image Hashes\n")
            f.write("=" * 80 + "\n\n")

            for file_path in self.collected_files:
                if file_path.exists() and file_path.suffix in [".raw", ".dmp"]:
                    self.logger.info(
                        f"Calculating hash for {file_path.name} (this may take a while)...",
                        module="MemoryModule",
                    )

                    hashes = self.hash_calculator.calculate_file_hashes(file_path, ["sha256"])

                    f.write(f"File: {file_path.name}\n")
                    f.write(f"Size: {file_path.stat().st_size / (1024**3):.2f} GB\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"{algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="MemoryModule",
                        action="Memory image collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_sha256=hashes.get("sha256", ""),
                    )

    def cleanup(self) -> None:
        self.logger.debug("Memory module cleanup", module="MemoryModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "memory",
            "name": "Memory Acquisition (Volatility Compatible)",
            "version": "1.0.0",
            "description": "Acquires physical memory for analysis with Volatility framework",
        }
