import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any
import json

from src.modules.base_module import ICollectionModule, ModuleStatus
from src.services.logger import get_logger
from src.services.hash_calculator import HashCalculator


class NetworkModule(ICollectionModule):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = get_logger()
        self.hash_calculator = HashCalculator()
        self.output_dir = Path(config.get("output_dir", "network"))
        self.collected_files = []

    def initialize(self) -> bool:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(
                f"Network module initialized, output: {self.output_dir}",
                module="NetworkModule"
            )

            self.status = ModuleStatus.INITIALIZED
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize network module: {e}",
                module="NetworkModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def execute(self) -> bool:
        try:
            self.status = ModuleStatus.RUNNING
            self.progress = 0

            self.logger.info("Collecting network connections...", module="NetworkModule")
            self._collect_connections()
            self.progress = 20

            self.logger.info("Collecting ARP cache...", module="NetworkModule")
            self._collect_arp_cache()
            self.progress = 40

            self.logger.info("Collecting routing table...", module="NetworkModule")
            self._collect_routing_table()
            self.progress = 60

            self.logger.info("Collecting DNS cache...", module="NetworkModule")
            self._collect_dns_cache()
            self.progress = 80

            self.logger.info("Collecting network interfaces...", module="NetworkModule")
            self._collect_interfaces()
            self.progress = 90

            self.logger.info("Calculating hashes...", module="NetworkModule")
            self._calculate_hashes()
            self.progress = 100

            self.status = ModuleStatus.COMPLETED
            self.logger.info(
                "Network module completed successfully",
                module="NetworkModule"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Network module failed: {e}",
                module="NetworkModule",
                exc_info=True
            )
            self.status = ModuleStatus.FAILED
            self.error_message = str(e)
            return False

    def _collect_connections(self):
        try:
            output_file = self.output_dir / "connections.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Network Connections\n")
                f.write("=" * 80 + "\n\n")

                connections = psutil.net_connections(kind='inet')

                f.write(f"Total Connections: {len(connections)}\n\n")

                f.write("TCP Connections:\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Local Address':<25} {'Remote Address':<25} {'Status':<15} {'PID':<10}\n")
                f.write("-" * 80 + "\n")

                for conn in connections:
                    if conn.type == 1:
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                        status = conn.status
                        pid = conn.pid if conn.pid else "N/A"

                        f.write(f"{local:<25} {remote:<25} {status:<15} {pid:<10}\n")

                f.write("\n\nUDP Connections:\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Local Address':<25} {'PID':<10}\n")
                f.write("-" * 80 + "\n")

                for conn in connections:
                    if conn.type == 2:
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        pid = conn.pid if conn.pid else "N/A"

                        f.write(f"{local:<25} {pid:<10}\n")

            self.collected_files.append(output_file)
            self.logger.info(f"Connections saved to: {output_file}", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect connections: {e}", module="NetworkModule")

    def _collect_arp_cache(self):
        try:
            output_file = self.output_dir / "arp_cache.txt"

            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("ARP Cache\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"ARP cache saved to: {output_file}", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect ARP cache: {e}", module="NetworkModule")

    def _collect_routing_table(self):
        try:
            output_file = self.output_dir / "routing_table.txt"

            result = subprocess.run(
                ['route', 'print'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Routing Table\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"Routing table saved to: {output_file}", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect routing table: {e}", module="NetworkModule")

    def _collect_dns_cache(self):
        try:
            output_file = self.output_dir / "dns_cache.txt"

            result = subprocess.run(
                ['ipconfig', '/displaydns'],
                capture_output=True,
                text=True,
                encoding='cp437'
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("DNS Cache\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"DNS cache saved to: {output_file}", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect DNS cache: {e}", module="NetworkModule")

    def _collect_interfaces(self):
        try:
            output_file = self.output_dir / "interfaces.json"

            interfaces = {}

            for interface_name, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "addresses": []
                }

                for addr in addresses:
                    addr_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    interface_info["addresses"].append(addr_info)

                try:
                    stats = psutil.net_if_stats()[interface_name]
                    interface_info["stats"] = {
                        "isup": stats.isup,
                        "duplex": str(stats.duplex),
                        "speed": stats.speed,
                        "mtu": stats.mtu
                    }
                except:
                    pass

                interfaces[interface_name] = interface_info

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(interfaces, f, indent=4, ensure_ascii=False)

            self.collected_files.append(output_file)
            self.logger.info(f"Interfaces saved to: {output_file}", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect interfaces: {e}", module="NetworkModule")

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
                        module="NetworkModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.logger.debug("Network module cleanup", module="NetworkModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "network",
            "name": "Network Collection",
            "version": "1.0.0",
            "description": "Collects network connections, ARP cache, routing table, and DNS cache"
        }
