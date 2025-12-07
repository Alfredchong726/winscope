import psutil
import subprocess
import platform
import os
from pathlib import Path
from typing import Dict, Any
import json
import csv
from datetime import datetime

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class LiveSystemModule(ICollectionModule):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "live_system"))
        self.collected_files = []

    def initialize(self) -> bool:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Live system module initialized, output: {self.output_dir}",
                module="LiveSystemModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize live system module: {e}",
                module="LiveSystemModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Collecting process information...", module="LiveSystemModule")
            self._collect_processes()
            self.progress = 15

            self.logger.info("Collecting services...", module="LiveSystemModule")
            self._collect_services()
            self.progress = 30

            self.logger.info("Collecting scheduled tasks...", module="LiveSystemModule")
            self._collect_scheduled_tasks()
            self.progress = 45

            self.logger.info("Collecting logged-in users...", module="LiveSystemModule")
            self._collect_users()
            self.progress = 60

            self.logger.info("Collecting system information...", module="LiveSystemModule")
            self._collect_system_info()
            self.progress = 75

            self.logger.info("Collecting environment variables...", module="LiveSystemModule")
            self._collect_environment()
            self.progress = 90

            self.logger.info("Calculating hashes...", module="LiveSystemModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                "Live system module completed successfully",
                module="LiveSystemModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Live system module failed: {e}",
                module="LiveSystemModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_processes(self):
        try:
            csv_file = self.output_dir / "processes.csv"

            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                writer.writerow([
                    'PID',
                    'Name',
                    'Executable Path',
                    'Command Line',
                    'Parent PID',
                    'Username',
                    'Status',
                    'CPU %',
                    'Memory MB',
                    'Threads',
                    'Created Time'
                ])

                for proc in psutil.process_iter([
                    'pid', 'name', 'exe', 'cmdline', 'ppid',
                    'username', 'status', 'cpu_percent',
                    'memory_info', 'num_threads', 'create_time'
                ]):
                    try:
                        pinfo = proc.info

                        pid = pinfo.get('pid', '')
                        name = pinfo.get('name', '')
                        exe = pinfo.get('exe', 'N/A')

                        cmdline = pinfo.get('cmdline', [])
                        cmdline_str = ' '.join(cmdline) if cmdline else 'N/A'

                        ppid = pinfo.get('ppid', '')
                        username = pinfo.get('username', 'N/A')
                        status = pinfo.get('status', 'N/A')

                        cpu_percent = pinfo.get('cpu_percent', 0)

                        mem_info = pinfo.get('memory_info')
                        memory_mb = round(mem_info.rss / 1024 / 1024, 2) if mem_info else 0

                        num_threads = pinfo.get('num_threads', 0)

                        create_time = pinfo.get('create_time', 0)
                        created = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S') if create_time else 'N/A'

                        writer.writerow([
                            pid, name, exe, cmdline_str, ppid,
                            username, status, cpu_percent, memory_mb,
                            num_threads, created
                        ])

                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

            self.collected_files.append(csv_file)
            self.logger.info(f"Processes saved to: {csv_file}", module="LiveSystemModule")

            json_file = self.output_dir / "processes.json"
            processes_data = []

            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'ppid', 'username']):
                try:
                    pinfo = proc.info
                    processes_data.append({
                        "pid": pinfo.get('pid'),
                        "name": pinfo.get('name'),
                        "exe": pinfo.get('exe'),
                        "cmdline": pinfo.get('cmdline'),
                        "ppid": pinfo.get('ppid'),
                        "username": pinfo.get('username')
                    })
                except:
                    continue

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(processes_data, f, indent=4, ensure_ascii=False)

            self.collected_files.append(json_file)

        except Exception as e:
            self.logger.error(f"Failed to collect processes: {e}", module="LiveSystemModule")

    def _collect_services(self):
        try:
            output_file = self.output_dir / "services.txt"

            result = subprocess.run(
                ['sc', 'query', 'state=', 'all'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Windows Services\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"Services saved to: {output_file}", module="LiveSystemModule")

            self._collect_services_detailed()

        except Exception as e:
            self.logger.error(f"Failed to collect services: {e}", module="LiveSystemModule")

    def _collect_services_detailed(self):
        try:
            csv_file = self.output_dir / "services.csv"

            result = subprocess.run(
                ['wmic', 'service', 'get',
                 'Name,DisplayName,State,StartMode,PathName',
                 '/format:csv'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)

            self.collected_files.append(csv_file)

        except Exception as e:
            self.logger.error(f"Failed to collect detailed services: {e}", module="LiveSystemModule")

    def _collect_scheduled_tasks(self):
        try:
            output_file = self.output_dir / "scheduled_tasks.txt"

            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'LIST', '/v'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Scheduled Tasks\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"Scheduled tasks saved to: {output_file}", module="LiveSystemModule")

            csv_file = self.output_dir / "scheduled_tasks.csv"
            result_csv = subprocess.run(
                ['schtasks', '/query', '/fo', 'CSV', '/v'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write(result_csv.stdout)

            self.collected_files.append(csv_file)

        except Exception as e:
            self.logger.error(f"Failed to collect scheduled tasks: {e}", module="LiveSystemModule")

    def _collect_users(self):
        try:
            output_file = self.output_dir / "users.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Logged-in Users\n")
                f.write("=" * 80 + "\n\n")

                users = psutil.users()

                if users:
                    f.write(f"{'User':<20} {'Terminal':<15} {'Host':<20} {'Started':<20}\n")
                    f.write("-" * 80 + "\n")

                    for user in users:
                        started = datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"{user.name:<20} {user.terminal or 'N/A':<15} "
                               f"{user.host or 'localhost':<20} {started:<20}\n")
                else:
                    f.write("No users currently logged in.\n")

                f.write("\n\n")

                try:
                    result = subprocess.run(
                        ['query', 'user'],
                        capture_output=True,
                        text=True,
                        encoding='cp437'
                    )

                    if result.returncode == 0:
                        f.write("Query User Output:\n")
                        f.write("-" * 80 + "\n")
                        f.write(result.stdout)
                except:
                    pass

            self.collected_files.append(output_file)
            self.logger.info(f"Users saved to: {output_file}", module="LiveSystemModule")

        except Exception as e:
            self.logger.error(f"Failed to collect users: {e}", module="LiveSystemModule")

    def _collect_system_info(self):
        try:
            output_file = self.output_dir / "system_info.json"

            system_info = {}

            system_info['os'] = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node()
            }

            system_info['cpu'] = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'cpu_percent': psutil.cpu_percent(interval=1)
            }

            memory = psutil.virtual_memory()
            system_info['memory'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'percent': memory.percent
            }

            system_info['disks'] = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_info['disks'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent': usage.percent
                    })
                except:
                    continue

            boot_time = psutil.boot_time()
            system_info['boot_time'] = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
            system_info['uptime_seconds'] = int(datetime.now().timestamp() - boot_time)

            net_io = psutil.net_io_counters()
            system_info['network_stats'] = {
                'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(system_info, f, indent=4, ensure_ascii=False)

            self.collected_files.append(output_file)
            self.logger.info(f"System info saved to: {output_file}", module="LiveSystemModule")

        except Exception as e:
            self.logger.error(f"Failed to collect system info: {e}", module="LiveSystemModule")

    def _collect_environment(self):
        try:
            output_file = self.output_dir / "environment.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Environment Variables\n")
                f.write("=" * 80 + "\n\n")

                for key in sorted(os.environ.keys()):
                    value = os.environ[key]
                    f.write(f"{key} = {value}\n")

            self.collected_files.append(output_file)
            self.logger.info(f"Environment saved to: {output_file}", module="LiveSystemModule")

            json_file = self.output_dir / "environment.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(dict(os.environ), f, indent=4, ensure_ascii=False)

            self.collected_files.append(json_file)

        except Exception as e:
            self.logger.error(f"Failed to collect environment: {e}", module="LiveSystemModule")

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
                        module="LiveSystemModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Live system module cleanup", module="LiveSystemModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "live_system",
            "name": "Live System Collection",
            "version": "1.0.0",
            "description": "Collects running processes, services, scheduled tasks, and system information"
        }
