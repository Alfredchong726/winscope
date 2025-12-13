import subprocess
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

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

    def initialize(self) -> bool:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.logger.error(
                    "Memory module requires administrator privileges",
                    module="MemoryModule"
                )
                self.status = ModuleStatus.FAILED
                self.error_message = "Administrator privileges required"
                return False

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Memory module initialized, output: {self.output_dir}",
                module="MemoryModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize memory module: {e}",
                module="MemoryModule",
                exc_info=True
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
            self.logger.info(
                "Memory module completed successfully",
                module="MemoryModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Memory module failed: {e}",
                module="MemoryModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_system_info(self) -> Dict[str, Any]:
        import platform
        import psutil

        info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'acquisition_time': datetime.now().isoformat(),
        }

        info_file = self.output_dir / "system_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4)

        self.collected_files.append(info_file)

        return info

    def _acquire_memory(self) -> Path:
        output_file = self.output_dir / f"memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.raw"

        try:
            project_root = Path(__file__).parent.parent.parent

            winpmem_path = project_root / "tools" / "winpmem" / "winpmem.exe"

            self.logger.info(
                f"Looking for WinPmem at: {winpmem_path}",
                module="MemoryModule"
            )

            if not winpmem_path.exists():
                self.logger.warning(
                    f"WinPmem not found at: {winpmem_path}",
                    module="MemoryModule"
                )

                instruction_file = self.output_dir / "MEMORY_ACQUISITION_INSTRUCTIONS.txt"
                with open(instruction_file, 'w', encoding='utf-8') as f:
                    f.write(f"""
                        ╔═══════════════════════════════════════════════════════════════════════╗
                        ║           Memory Acquisition Tool Not Found                           ║
                        ╚═══════════════════════════════════════════════════════════════════════╝

                        WinPmem is required for memory acquisition but was not found.

                        Expected Location:
                        ------------------
                        {winpmem_path}

                        📥 How to Download:
                        -------------------
                        1. Visit: https://github.com/Velocidex/WinPmem/releases
                        2. Download: winpmem_mini_x64.exe (latest version)
                        3. Rename to: winpmem.exe
                        4. Place at: {winpmem_path}

                        💡 Alternative Tools:
                        ---------------------
                        If you have another memory acquisition tool:

                        1. DumpIt (Magnet Forensics)
                        - Download from: https://www.magnetforensics.com/
                        - Command: DumpIt.exe /O memory.raw

                        2. FTK Imager (AccessData)
                        - GUI-based, select "Capture Memory"

                        3. Magnet RAM Capture
                        - GUI-based memory capture

                        📋 Manual Memory Acquisition Steps:
                        ------------------------------------
                        1. Download and run WinPmem (as Administrator):

                        winpmem.exe memory.raw

                        2. Place the resulting .raw file in this directory:
                        {self.output_dir}

                        3. For Volatility analysis:

                        # Volatility 2
                        volatility -f memory.raw --profile=Win10x64 pslist

                        # Volatility 3
                        vol.py -f memory.raw windows.pslist

                        ⚠️  Important Notes:
                        --------------------
                        - Administrator privileges required
                        - Memory acquisition can take 5-15 minutes
                        - Ensure sufficient disk space (size = RAM size)
                        - Do not interrupt the process

                        For more information, see:
                        {project_root / 'tools' / 'README.md'}
                        """)

                self.collected_files.append(instruction_file)
                self.logger.info(
                    f"Created instruction file: {instruction_file}",
                    module="MemoryModule"
                )

                return None

            self.logger.info(
                f"Starting memory acquisition with WinPmem...",
                module="MemoryModule"
            )

            result = subprocess.run(
                [str(winpmem_path), str(output_file), "--format", "raw"],
                capture_output=True,
                text=True,
                timeout=3600
            )

            if result.returncode == 0 and output_file.exists():
                size_gb = output_file.stat().st_size / (1024**3)
                self.logger.info(
                    f"✓ Memory acquired successfully: {size_gb:.2f} GB",
                    module="MemoryModule"
                )
                self.collected_files.append(output_file)
                return output_file
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                self.logger.error(
                    f"Memory acquisition failed: {error_msg}",
                    module="MemoryModule"
                )
                return None

        except subprocess.TimeoutExpired:
            self.logger.error(
                "Memory acquisition timed out (>1 hour)",
                module="MemoryModule"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Error during memory acquisition: {e}",
                module="MemoryModule",
                exc_info=True
            )
            return None

    def _generate_volatility_metadata(self, memory_file: Path, system_info: Dict):
        try:
            metadata_file = self.output_dir / "volatility_analysis_guide.txt"

            os_version = system_info.get('os_version', '')
            architecture = system_info.get('architecture', '')

            if 'Windows-10' in os_version:
                if 'AMD64' in architecture or 'x86_64' in architecture:
                    profile = "Win10x64"
                else:
                    profile = "Win10x86"
            elif 'Windows-11' in os_version:
                profile = "Win10x64"
            else:
                profile = "WinXPSP2x86"

            with open(metadata_file, 'w') as f:
                f.write(f"""
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

""")

            self.collected_files.append(metadata_file)

        except Exception as e:
            self.logger.error(
                f"Failed to generate Volatility metadata: {e}",
                module="MemoryModule"
            )

    def _calculate_hashes(self):
        hash_file = self.output_dir / "hashes.txt"

        with open(hash_file, 'w', encoding='utf-8') as f:
            f.write("Memory Image Hashes\n")
            f.write("=" * 80 + "\n\n")

            for file_path in self.collected_files:
                if file_path.exists() and file_path.suffix in ['.raw', '.dmp']:
                    self.logger.info(
                        f"Calculating hash for {file_path.name} (this may take a while)...",
                        module="MemoryModule"
                    )

                    hashes = self.hash_calculator.calculate_file_hashes(
                        file_path,
                        ["sha256"]
                    )

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
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Memory module cleanup", module="MemoryModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "memory",
            "name": "Memory Acquisition (Volatility Compatible)",
            "version": "1.0.0",
            "description": "Acquires physical memory for analysis with Volatility framework"
        }
