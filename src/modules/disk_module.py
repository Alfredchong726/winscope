import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import psutil

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class DiskModule(ICollectionModule):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "disk"))
        self.collected_files = []

        self.image_format = config.get("format", "logical")
        self.target_drives = config.get("target_drives", [])
        self.exclude_system = config.get("exclude_system", True)

    def initialize(self) -> bool:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.logger.error(
                    "Disk module requires administrator privileges",
                    module="DiskModule"
                )
                self.status = ModuleStatus.FAILED
                self.error_message = "Administrator privileges required"
                return False

            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Disk module initialized, output: {self.output_dir}",
                module="DiskModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize disk module: {e}",
                module="DiskModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Enumerating disks and partitions...", module="DiskModule")
            disk_info = self._enumerate_disks()
            self.progress = 10

            if self.image_format == "logical":
                self.logger.info("Performing logical acquisition...", module="DiskModule")
                self._logical_acquisition(disk_info)
                self.progress = 80
            else:
                self.logger.info("Physical imaging requires external tools", module="DiskModule")
                self._create_imaging_instructions(disk_info)
                self.progress = 50

            self.logger.info("Generating Autopsy guide...", module="DiskModule")
            self._generate_autopsy_guide()
            self.progress = 90

            self.logger.info("Calculating hashes...", module="DiskModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                "Disk module completed successfully",
                module="DiskModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Disk module failed: {e}",
                module="DiskModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _enumerate_disks(self) -> Dict[str, Any]:
        disk_info = {
            'partitions': [],
            'total_size_gb': 0
        }

        try:
            partitions = psutil.disk_partitions(all=True)

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    partition_data = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent_used': usage.percent
                    }

                    disk_info['partitions'].append(partition_data)
                    disk_info['total_size_gb'] += partition_data['total_gb']

                except PermissionError:
                    continue

            info_file = self.output_dir / "disk_information.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(disk_info, f, indent=4, ensure_ascii=False)

            self.collected_files.append(info_file)

            self.logger.info(
                f"Found {len(disk_info['partitions'])} partitions, "
                f"total {disk_info['total_size_gb']:.2f} GB",
                module="DiskModule"
            )

        except Exception as e:
            self.logger.error(f"Failed to enumerate disks: {e}", module="DiskModule")

        return disk_info

    def _logical_acquisition(self, disk_info: Dict[str, Any]):
        try:
            logical_dir = self.output_dir / "logical_acquisition"
            logical_dir.mkdir(exist_ok=True)

            for partition_info in disk_info['partitions']:
                mountpoint = partition_info['mountpoint']
                device = partition_info['device']

                if partition_info['fstype'] in ['', 'cdrom']:
                    continue

                self.logger.info(
                    f"Scanning partition: {mountpoint} ({device})",
                    module="DiskModule"
                )

                safe_name = device.replace(':', '').replace('\\', '_')
                output_file = logical_dir / f"file_list_{safe_name}.csv"

                try:
                    self._scan_partition(mountpoint, output_file)
                    self.collected_files.append(output_file)
                except Exception as e:
                    self.logger.error(
                        f"Failed to scan {mountpoint}: {e}",
                        module="DiskModule"
                    )

        except Exception as e:
            self.logger.error(
                f"Logical acquisition failed: {e}",
                module="DiskModule"
            )

    def _scan_partition(self, mountpoint: str, output_file: Path):
        import csv

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                writer.writerow([
                    'Full_Path',
                    'File_Name',
                    'Extension',
                    'Size_Bytes',
                    'Created',
                    'Modified',
                    'Accessed',
                    'Attributes',
                    'MD5',
                    'SHA256'
                ])

                file_count = 0
                max_files = 100000

                root_path = Path(mountpoint)

                for item in root_path.rglob('*'):
                    if file_count >= max_files:
                        self.logger.warning(
                            f"Reached file limit ({max_files}) for {mountpoint}",
                            module="DiskModule"
                        )
                        break

                    try:
                        if item.is_file():
                            stat = item.stat()

                            file_data = [
                                str(item),
                                item.name,
                                item.suffix,
                                stat.st_size,
                                datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                datetime.fromtimestamp(stat.st_atime).isoformat(),
                                '',
                                '',
                                ''
                            ]

                            writer.writerow(file_data)
                            file_count += 1

                    except (PermissionError, OSError):
                        continue

                self.logger.info(
                    f"Scanned {file_count} files from {mountpoint}",
                    module="DiskModule"
                )

        except Exception as e:
            self.logger.error(
                f"Error scanning partition {mountpoint}: {e}",
                module="DiskModule"
            )

    def _create_imaging_instructions(self, disk_info: Dict[str, Any]):
        try:
            instruction_file = self.output_dir / "DISK_IMAGING_INSTRUCTIONS.txt"

            with open(instruction_file, 'w', encoding='utf-8') as f:
                f.write("""
╔═══════════════════════════════════════════════════════════════════════╗
║              Disk Imaging Instructions                                ║
╚═══════════════════════════════════════════════════════════════════════╝

Physical disk imaging requires specialized forensic tools.
WinScope has performed logical acquisition (file listing).

For complete forensic disk images, use one of these professional tools:

""")

                f.write("📊 Detected Disk Information:\n")
                f.write("-" * 70 + "\n")
                for partition in disk_info['partitions']:
                    f.write(f"Drive: {partition['device']}\n")
                    f.write(f"  Mount: {partition['mountpoint']}\n")
                    f.write(f"  Type: {partition['fstype']}\n")
                    f.write(f"  Size: {partition['total_gb']:.2f} GB\n")
                    f.write(f"  Used: {partition['used_gb']:.2f} GB ({partition['percent_used']:.1f}%)\n")
                    f.write("\n")

                f.write("\n")
                f.write("=" * 70 + "\n")
                f.write("RECOMMENDED IMAGING TOOLS\n")
                f.write("=" * 70 + "\n\n")

                f.write("""
1. FTK Imager (FREE - Recommended)
--------------------------------
Download: https://www.exterro.com/ftk-imager

Features:
- Create DD, E01, or AFF images
- Built-in hash verification
- User-friendly GUI
- Most popular forensic tool

Steps:
a) Launch FTK Imager as Administrator
b) File > Create Disk Image
c) Select Physical Drive or Logical Drive
d) Choose image format (E01 recommended)
e) Set destination and case information
f) Click Start to begin imaging

Image Formats:
- Raw (dd): Universal compatibility
- E01: Compressed, with metadata (recommended)
- AFF: Advanced Forensic Format


2. Arsenal Image Mounter + dd
----------------------------
Free alternative for DD images

Download Arsenal Image Mounter:
https://arsenalrecon.com/downloads/

Then use dd for Windows:
http://www.chrysocome.net/dd

Command:
dd if=\\\\.\\PhysicalDrive0 of=disk_image.dd bs=4M


3. Guymager (Linux-based)
-----------------------
Boot from forensic Linux (SIFT, CAINE)

Command:
sudo guymager

Select drive and create E01 or DD image


4. dc3dd (Enhanced dd)
--------------------
Forensic version of dd with hashing

Command:
dc3dd if=\\\\.\\PhysicalDrive0 of=disk.dd hash=md5 hash=sha256 log=hash.txt


5. Commercial Options
-------------------
- EnCase Forensic Imager ($$)
- X-Ways Imager ($$)
- Magnet AXIOM ($$)

""")

                f.write("=" * 70 + "\n")
                f.write("IMPORTANT CONSIDERATIONS\n")
                f.write("=" * 70 + "\n\n")

                f.write(f"""
                        Storage Requirements:
                        - Full image size = disk size ({disk_info['total_size_gb']:.2f} GB)
                        - E01 format: ~60-70% of original (compression)
                        - Ensure sufficient space on destination drive

                        Time Estimates:
                        - USB 2.0: ~30 MB/s (~10 hours for 1TB)
                        - USB 3.0: ~100 MB/s (~3 hours for 1TB)
                        - Internal SATA: ~150 MB/s (~2 hours for 1TB)

                        Best Practices:
                        1. Use write-blocker for suspect drives
                        2. Create hash before and after imaging
                        3. Use E01 format for case management
                        4. Document everything (case notes, timestamps)
                        5. Keep original drive secure
                        6. Make two copies (working + archive)

                        Write Blocking:
                        - Hardware: Tableau, WiebeTech
                        - Software: FTK Imager (built-in)

                        Chain of Custody:
                        - Document who, what, when, where
                        - Record hash values
                        - Keep audit log
                        - Store in secure location
                        """)

                f.write("\n")
                f.write("=" * 70 + "\n")
                f.write("AUTOPSY ANALYSIS\n")
                f.write("=" * 70 + "\n\n")

                f.write("""
After creating the disk image:

1. Open Autopsy
2. Create New Case
3. Add Data Source
4. Select Disk Image or VM File
5. Browse to your .dd or .E01 file
6. Configure ingest modules
7. Start Analysis

Autopsy will:
- Parse file systems
- Extract files
- Generate timeline
- Analyze artifacts
- Create searchable index
""")

            self.collected_files.append(instruction_file)

        except Exception as e:
            self.logger.error(
                f"Failed to create imaging instructions: {e}",
                module="DiskModule"
            )

    def _generate_autopsy_guide(self):
        """生成 Autopsy 分析指南。"""
        try:
            guide_file = self.output_dir / "autopsy_analysis_guide.txt"

            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write("""
╔═══════════════════════════════════════════════════════════════════════╗
║              Autopsy Forensic Analysis Guide                          ║
╚═══════════════════════════════════════════════════════════════════════╝

Autopsy is the premier open-source digital forensics platform.
Download: https://www.autopsy.com/download/

📊 Importing WinScope Evidence:
--------------------------------

1. Logical Acquisition Files:
- Use the CSV file lists in logical_acquisition/
- Import as "Logical Files" data source
- Autopsy will parse timestamps and metadata

2. Full Disk Images (if created):
- Add Data Source > Disk Image
- Select your .dd or .E01 file
- Autopsy will automatically detect file systems

3. Memory Dumps (from Memory Module):
- Add Data Source > Memory Image
- Point to the .raw file
- Enable memory analysis modules

🔍 Recommended Ingest Modules:
-------------------------------
☑ Recent Activity
- Recent documents, searches, downloads

☑ Hash Lookup
- Check against NSRL, known malware hashes

☑ File Type Identification
- Identify files by signature, not extension

☑ Extension Mismatch Detector
- Find files with fake extensions

☑ Embedded File Extractor
- Extract files from archives, docs

☑ EXIF Parser
- Image metadata, GPS coordinates

☑ Email Parser
- PST, MBOX, EML files

☑ Registry Analysis
- Use with Registry Module output

☑ Web Artifacts
- Use with Browser Module output

☑ Timeline Analysis
- Create MACB timeline

☑ Keyword Search
- Search for specific terms

☑ Encryption Detection
- Find encrypted files/volumes

☑ Interesting Files Identifier
- Flag suspicious files


📋 Analysis Workflow:
---------------------

1. Run Ingest Modules (takes time)

2. Review Results by Category:

a) Data Artifacts
    - Recent Documents
    - Web History
    - Web Downloads
    - Web Search
    - Installed Programs
    - Devices Attached

b) File Types
    - Images
    - Videos
    - Documents
    - Executables
    - Archives

c) Timeline
    - File Activity Timeline
    - Correlate events

d) Communications
    - Email
    - Chat logs
    - SMS (if mobile)

e) Analysis Results
    - Hash Set Hits
    - Extension Mismatches
    - Encryption Detected
    - Interesting Items

3. Tag Evidence Items
- Right-click > Add Tag
- Organize findings

4. Create Report
- Tools > Generate Report
- HTML, Excel, or body file format


🎯 Common Investigation Tasks:
-------------------------------

Find User Activity:
- Data Artifacts > Recent Documents
- Data Artifacts > Web History

Find Malware:
- Analysis Results > Hash Set Hits
- Analysis Results > Extension Mismatches
- File Types > Executables (sort by date)

Find Data Theft:
- Data Artifacts > Web Downloads
- Data Artifacts > Devices Attached
- Timeline > Large file copies

Find Communication:
- Data Artifacts > Email
- Communication folder

Timeline Analysis:
- Timeline > File Activity
- Filter by date range
- Export to Excel for visualization


🔗 Integration with Other Tools:
---------------------------------

Sleuth Kit (command-line):
- fls: List files
- icat: Extract file by inode
- mmls: List partitions

Volatility (for memory):
- Export findings to Volatility format
- Cross-reference with memory analysis

Plaso/log2timeline:
- Generate super timeline
- Import into Autopsy

Network Miner (for PCAP):
- Analyze network captures
- Extract transferred files


💡 Tips & Tricks:
-----------------
1. Start with Ingest Modules (be patient)
2. Use Tags to organize findings
3. Create custom keyword lists
4. Use File Search by Attributes
5. Export timeline for offline analysis
6. Take screenshots of key evidence
7. Document everything in case notes
8. Use bookmarks for important findings


⚠️  Common Issues:
------------------
- Slow performance: Increase Java heap size
- Missing results: Ensure ingest modules completed
- Cannot open image: Check file format and permissions
- Large datasets: Use filtering and targeted searches


📚 Resources:
-------------
- Autopsy Documentation: https://sleuthkit.org/autopsy/docs/
- Video Tutorials: YouTube.com/autopsy
- Training: Basis Technology Autopsy Training
- Forums: https://sleuthkit.org/autopsy/forum.php
""")

            self.collected_files.append(guide_file)

        except Exception as e:
            self.logger.error(
                f"Failed to generate Autopsy guide: {e}",
                module="DiskModule"
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

                    f.write(f"File: {file_path.name}\n")
                    for algo, hash_value in hashes.items():
                        f.write(f"  {algo.upper()}: {hash_value}\n")
                    f.write("\n")

                    self.logger.log_collection(
                        module="DiskModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Disk module cleanup", module="DiskModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "disk",
            "name": "Disk Acquisition (Autopsy Compatible)",
            "version": "1.0.0",
            "description": "Performs logical disk acquisition and provides guidance for physical imaging"
        }
