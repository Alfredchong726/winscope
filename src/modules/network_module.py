import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import json
import threading
import time

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

        self.capture_traffic = config.get("capture_traffic", False)
        self.capture_duration = config.get("capture_duration", 60)
        self.capture_filter = config.get("capture_filter", "")

        self.capture_thread = None
        self.stop_capture = False

    def initialize(self) -> bool:
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            if self.capture_traffic:
                if not self._check_capture_tools():
                    self.logger.warning(
                        "Packet capture tools not found, traffic capture will be skipped",
                        module="NetworkModule"
                    )
                    self.capture_traffic = False

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

            if self.capture_traffic:
                self.logger.info(
                    f"Starting packet capture ({self.capture_duration}s)...",
                    module="NetworkModule"
                )
                self._start_packet_capture()
                self.progress = 5

            self.logger.info("Collecting network connections...", module="NetworkModule")
            self._collect_connections()
            self.progress = 20

            self.logger.info("Collecting ARP cache...", module="NetworkModule")
            self._collect_arp_cache()
            self.progress = 35

            self.logger.info("Collecting routing table...", module="NetworkModule")
            self._collect_routing_table()
            self.progress = 50

            self.logger.info("Collecting DNS cache...", module="NetworkModule")
            self._collect_dns_cache()
            self.progress = 65

            self.logger.info("Collecting network interfaces...", module="NetworkModule")
            self._collect_interfaces()
            self.progress = 75

            self.logger.info("Generating analysis guide...", module="NetworkModule")
            self._generate_wireshark_guide()
            self.progress = 80

            if self.capture_traffic and self.capture_thread:
                self.logger.info("Waiting for packet capture to complete...", module="NetworkModule")
                self.capture_thread.join(timeout=self.capture_duration + 10)
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

    def _check_capture_tools(self) -> bool:
        tools = ['tshark', 'dumpcap', 'windump']

        for tool in tools:
            try:
                result = subprocess.run(
                    [tool, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.logger.info(
                        f"Found packet capture tool: {tool}",
                        module="NetworkModule"
                    )
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        instruction_file = self.output_dir / "PACKET_CAPTURE_TOOLS.txt"
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write("""
                    ╔═══════════════════════════════════════════════════════════════════════╗
                    ║           Packet Capture Tools Not Found                              ║
                    ╚═══════════════════════════════════════════════════════════════════════╝

                    To enable network traffic capture in PCAP format, you need to install
                    packet capture tools.

                    📥 Recommended: Wireshark (includes tshark and dumpcap)
                    ----------------------------------------------------------------
                    Download: https://www.wireshark.org/download.html

                    Installation:
                    1. Download Wireshark installer
                    2. During installation, select:
                    ✓ Wireshark
                    ✓ TShark (command-line)
                    ✓ Npcap (packet capture driver)
                    3. Complete installation
                    4. Restart WinScope

                    After installation, tshark will be available in PATH.

                    📋 Manual Packet Capture (Alternative):
                    ----------------------------------------
                    If you want to capture packets manually:

                    1. Using Wireshark GUI:
                    - Open Wireshark
                    - Select network interface
                    - Click "Start Capture"
                    - Save as: network_traffic.pcapng

                    2. Using tshark:
                    tshark -i <interface> -w network_traffic.pcap -a duration:60

                    3. Using tcpdump (if available):
                    tcpdump -i <interface> -w network_traffic.pcap

                    Place the resulting .pcap/.pcapng file in this directory for analysis.

                    🔍 Analyzing PCAP Files:
                    -------------------------
                    Wireshark: wireshark network_traffic.pcap
                    Tshark: tshark -r network_traffic.pcap
                    """)

        self.collected_files.append(instruction_file)
        return False

    def _start_packet_capture(self):
        def capture_packets():
            output_file = self.output_dir / f"network_traffic_{time.strftime('%Y%m%d_%H%M%S')}.pcapng"

            try:
                cmd = [
                    'tshark',
                    '-i', 'any',
                    '-w', str(output_file),
                    '-a', f'duration:{self.capture_duration}'
                ]

                if self.capture_filter:
                    cmd.extend(['-f', self.capture_filter])

                self.logger.info(
                    f"Starting tshark: {' '.join(cmd)}",
                    module="NetworkModule"
                )

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.capture_duration + 30
                )

                if result.returncode == 0 and output_file.exists():
                    size_mb = output_file.stat().st_size / (1024 * 1024)
                    self.logger.info(
                        f"✓ Captured {size_mb:.2f} MB of network traffic",
                        module="NetworkModule"
                    )
                    self.collected_files.append(output_file)
                else:
                    self.logger.error(
                        f"Packet capture failed: {result.stderr}",
                        module="NetworkModule"
                    )

            except subprocess.TimeoutExpired:
                self.logger.warning(
                    "Packet capture timed out",
                    module="NetworkModule"
                )
            except Exception as e:
                self.logger.error(
                    f"Error during packet capture: {e}",
                    module="NetworkModule"
                )

        self.capture_thread = threading.Thread(target=capture_packets, daemon=True)
        self.capture_thread.start()

    def _collect_connections(self):
        try:
            txt_file = self.output_dir / "connections.txt"

            json_file = self.output_dir / "connections.json"

            connections_data = []

            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("Network Connections Analysis\n")
                f.write("=" * 100 + "\n\n")
                f.write("Compatible with: Wireshark, NetworkMiner, Volatility\n\n")

                connections = psutil.net_connections(kind='inet')

                f.write(f"Total Connections: {len(connections)}\n\n")

                f.write("TCP Connections:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'Local Address':<30} {'Remote Address':<30} {'Status':<15} {'PID':<10} {'Process':<20}\n")
                f.write("-" * 100 + "\n")

                for conn in connections:
                    if conn.type == 1:
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                        status = conn.status
                        pid = conn.pid if conn.pid else "N/A"

                        process_name = "N/A"
                        if conn.pid:
                            try:
                                process = psutil.Process(conn.pid)
                                process_name = process.name()
                            except:
                                pass

                        f.write(f"{local:<30} {remote:<30} {status:<15} {str(pid):<10} {process_name:<20}\n")

                        connections_data.append({
                            'type': 'TCP',
                            'local_addr': local,
                            'remote_addr': remote,
                            'status': status,
                            'pid': pid,
                            'process': process_name
                        })

                f.write("\n\nUDP Connections:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'Local Address':<30} {'PID':<10} {'Process':<20}\n")
                f.write("-" * 100 + "\n")

                for conn in connections:
                    if conn.type == 2:
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                        pid = conn.pid if conn.pid else "N/A"

                        process_name = "N/A"
                        if conn.pid:
                            try:
                                process = psutil.Process(conn.pid)
                                process_name = process.name()
                            except:
                                pass

                        f.write(f"{local:<30} {str(pid):<10} {process_name:<20}\n")

                        connections_data.append({
                            'type': 'UDP',
                            'local_addr': local,
                            'pid': pid,
                            'process': process_name
                        })

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_connections': len(connections),
                    'connections': connections_data
                }, f, indent=4, ensure_ascii=False)

            self.collected_files.extend([txt_file, json_file])
            self.logger.info(
                f"Collected {len(connections)} network connections",
                module="NetworkModule"
            )

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
                f.write("ARP Cache Analysis\n")
                f.write("=" * 80 + "\n\n")
                f.write("Purpose: Map IP addresses to MAC addresses\n")
                f.write("Forensic Value: Recent network communications\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"ARP cache saved", module="NetworkModule")

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
                f.write("Routing Table Analysis\n")
                f.write("=" * 80 + "\n\n")
                f.write("Purpose: Network path information\n")
                f.write("Forensic Value: Network configuration, VPN detection\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"Routing table saved", module="NetworkModule")

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
                f.write("DNS Cache Analysis\n")
                f.write("=" * 80 + "\n\n")
                f.write("Purpose: Recent DNS queries\n")
                f.write("Forensic Value: Websites visited, C2 domains, malicious sites\n\n")
                f.write(result.stdout)

            self.collected_files.append(output_file)
            self.logger.info(f"DNS cache saved", module="NetworkModule")

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

            # 保存为JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(interfaces, f, indent=4, ensure_ascii=False)

            self.collected_files.append(output_file)
            self.logger.info(f"Network interfaces saved", module="NetworkModule")

        except Exception as e:
            self.logger.error(f"Failed to collect interfaces: {e}", module="NetworkModule")

    def _generate_wireshark_guide(self):
        try:
            guide_file = self.output_dir / "wireshark_analysis_guide.txt"

            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write("""
                        ╔═══════════════════════════════════════════════════════════════════════╗
                        ║              Wireshark Network Analysis Guide                         ║
                        ╚═══════════════════════════════════════════════════════════════════════╝

                        📊 Opening PCAP Files:
                        ----------------------
                        Wireshark:  wireshark network_traffic.pcapng
                        Tshark:     tshark -r network_traffic.pcapng

                        🔍 Common Display Filters:
                        ---------------------------
                        # HTTP Traffic
                        http

                        # HTTPS/TLS
                        tls or ssl

                        # DNS Queries
                        dns

                        # Specific IP
                        ip.addr == 192.168.1.100

                        # Specific Port
                        tcp.port == 80 or udp.port == 53

                        # SYN Scans (Port Scanning)
                        tcp.flags.syn == 1 and tcp.flags.ack == 0

                        # Failed Connections
                        tcp.flags.reset == 1

                        # Large Packets (>1000 bytes)
                        frame.len > 1000

                        # Suspicious Protocols
                        ftp or telnet or smtp

                        📋 Forensic Analysis Checklist:
                        --------------------------------
                        1. Identify Communication Patterns
                        - Statistics > Conversations
                        - Statistics > Endpoints

                        2. Extract HTTP Objects
                        - File > Export Objects > HTTP

                        3. Follow TCP Streams
                        - Right-click packet > Follow > TCP Stream

                        4. DNS Analysis
                        - dns and (dns.flags.response == 0)  # Queries
                        - dns.qry.name contains "suspicious"

                        5. Detect Port Scans
                        - tcp.flags.syn == 1 and tcp.flags.ack == 0
                        - tcp.analysis.flags

                        6. Find Data Exfiltration
                        - Large uploads: tcp.len > 1000 and ip.src == [internal_ip]
                        - FTP file transfers: ftp-data
                        - HTTP POST: http.request.method == "POST"

                        7. Identify Malware C2
                        - Beaconing: regular intervals in conversations
                        - Non-standard ports: tcp.port != 80 and tcp.port != 443

                        🛠️ Tshark Commands:
                        --------------------
                        # Extract HTTP requests
                        tshark -r network_traffic.pcapng -Y "http.request" -T fields -e http.request.method -e http.host -e http.request.uri

                        # Count packets by protocol
                        tshark -r network_traffic.pcapng -q -z io,phs

                        # Extract DNS queries
                        tshark -r network_traffic.pcapng -Y "dns.flags.response == 0" -T fields -e dns.qry.name

                        # Statistics summary
                        tshark -r network_traffic.pcapng -q -z conv,tcp

                        # Export HTTP objects
                        tshark -r network_traffic.pcapng --export-objects http,./http_objects/

                        🔗 Integration with Other Tools:
                        ---------------------------------
                        NetworkMiner: NetworkMiner.exe network_traffic.pcapng
                        - Extract files, credentials, hostnames

                        Zeek (Bro): zeek -r network_traffic.pcapng
                        - Generate detailed logs

                        Snort: snort -r network_traffic.pcapng -c snort.conf
                        - IDS analysis

                        📚 Resources:
                        -------------
                        - Wireshark User Guide: https://www.wireshark.org/docs/wsug_html/
                        - Display Filter Reference: https://www.wireshark.org/docs/dfref/
                        - Wireshark Tutorial: https://www.wireshark.org/docs/

                        ⚠️  Analysis Tips:
                        ------------------
                        - Look for anomalies in normal traffic patterns
                        - Check for connections to suspicious IPs/domains
                        - Analyze timing patterns for beaconing
                        - Extract and analyze transferred files
                        - Correlate with other evidence (process list, timestamps)
                        """)

            self.collected_files.append(guide_file)

        except Exception as e:
            self.logger.error(
                f"Failed to generate Wireshark guide: {e}",
                module="NetworkModule"
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
                        module="NetworkModule",
                        action="File collected",
                        status="Success",
                        file_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        hash_md5=hashes.get("md5", ""),
                        hash_sha256=hashes.get("sha256", "")
                    )

    def cleanup(self) -> None:
        self.stop_capture = True
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)

        self.logger.debug("Network module cleanup", module="NetworkModule")

    def get_module_info(self) -> Dict[str, Any]:
        return {
            "id": "network",
            "name": "Network Collection (Wireshark Compatible)",
            "version": "2.0.0",
            "description": "Collects network connections and optionally captures traffic in PCAP format for Wireshark analysis"
        }
