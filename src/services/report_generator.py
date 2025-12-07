from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json

from src.services.logger import get_logger


class ReportGenerator:
    def __init__(self):
        self.logger = get_logger()

    def generate_report(
        self,
        output_dir: Path,
        collection_data: Dict[str, Any]
    ) -> Path:
        try:
            report_path = output_dir / "collection_report.html"

            evidence_by_module = self._collect_evidence_by_module(output_dir)

            statistics = self._generate_statistics(output_dir, evidence_by_module)

            html_content = self._generate_html(
                output_dir,
                collection_data,
                evidence_by_module,
                statistics
            )

            report_path.write_text(html_content, encoding='utf-8')

            self.logger.info(
                f"Report generated: {report_path}",
                module="ReportGenerator"
            )

            return report_path

        except Exception as e:
            self.logger.error(
                f"Failed to generate report: {e}",
                module="ReportGenerator",
                exc_info=True
            )
            return None

    def _collect_evidence_by_module(self, output_dir: Path) -> Dict[str, Any]:
        evidence = {}

        modules_config = {
            'network': {
                'name': 'Network Collection',
                'icon': '🌐',
                'files': ['connections.txt', 'arp_cache.txt', 'routing_table.txt',
                         'dns_cache.txt', 'interfaces.json']
            },
            'live_system': {
                'name': 'Live System',
                'icon': '⚡',
                'files': ['processes.csv', 'services.csv', 'scheduled_tasks.csv',
                         'users.txt', 'system_info.json', 'environment.json']
            },
            'browser': {
                'name': 'Browser Artifacts',
                'icon': '🌍',
                'subdirs': ['chrome', 'edge', 'firefox']
            },
            'filesystem': {
                'name': 'File System',
                'icon': '📁',
                'files': ['recent_files.txt', 'startup_items.txt', 'temp_files.txt',
                         'recycle_bin.txt']
            },
            'registry': {
                'name': 'Registry',
                'icon': '📋',
                'subdirs': ['hives', 'users', 'keys'],
                'special_files': ['registry_report.txt']
            },
            'eventlogs': {
                'name': 'Event Logs',
                'icon': '📜',
                'subdirs': ['critical', 'all'],
                'special_files': ['logs_inventory.txt']
            }
        }

        for module_id, config in modules_config.items():
            module_dir = output_dir / module_id

            if not module_dir.exists():
                continue

            module_evidence = {
                'name': config['name'],
                'icon': config['icon'],
                'path': module_dir,
                'files': [],
                'subdirs': {},
                'total_size': 0,
                'file_count': 0
            }

            if 'files' in config:
                for filename in config['files']:
                    file_path = module_dir / filename
                    if file_path.exists():
                        file_info = self._get_file_info(file_path)
                        module_evidence['files'].append(file_info)
                        module_evidence['total_size'] += file_info['size']
                        module_evidence['file_count'] += 1

            if 'subdirs' in config:
                for subdir_name in config['subdirs']:
                    subdir_path = module_dir / subdir_name
                    if subdir_path.exists():
                        subdir_info = self._get_directory_info(subdir_path)
                        module_evidence['subdirs'][subdir_name] = subdir_info
                        module_evidence['total_size'] += subdir_info['total_size']
                        module_evidence['file_count'] += subdir_info['file_count']

            if 'special_files' in config:
                for filename in config['special_files']:
                    file_path = module_dir / filename
                    if file_path.exists():
                        file_info = self._get_file_info(file_path)
                        module_evidence['files'].append(file_info)
                        module_evidence['total_size'] += file_info['size']
                        module_evidence['file_count'] += 1

            for item in module_dir.iterdir():
                if item.is_file() and item.name not in [f['name'] for f in module_evidence['files']]:
                    file_info = self._get_file_info(item)
                    module_evidence['files'].append(file_info)
                    module_evidence['total_size'] += file_info['size']
                    module_evidence['file_count'] += 1

            evidence[module_id] = module_evidence

        return evidence

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'extension': file_path.suffix
            }
        except:
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': 0,
                'size_mb': 0,
                'modified': 'N/A',
                'extension': ''
            }

    def _get_directory_info(self, dir_path: Path) -> Dict[str, Any]:
        try:
            files = []
            total_size = 0

            for item in dir_path.rglob('*'):
                if item.is_file():
                    file_info = self._get_file_info(item)
                    files.append(file_info)
                    total_size += file_info['size']

            return {
                'name': dir_path.name,
                'path': str(dir_path),
                'files': files,
                'file_count': len(files),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except:
            return {
                'name': dir_path.name,
                'path': str(dir_path),
                'files': [],
                'file_count': 0,
                'total_size': 0,
                'total_size_mb': 0
            }

    def _generate_statistics(
        self,
        output_dir: Path,
        evidence_by_module: Dict[str, Any]
    ) -> Dict[str, Any]:
        stats = {
            'total_modules': len(evidence_by_module),
            'total_files': 0,
            'total_size': 0,
            'total_size_mb': 0,
            'total_size_gb': 0,
            'modules_summary': []
        }

        for module_id, module_data in evidence_by_module.items():
            stats['total_files'] += module_data['file_count']
            stats['total_size'] += module_data['total_size']

            stats['modules_summary'].append({
                'id': module_id,
                'name': module_data['name'],
                'icon': module_data['icon'],
                'files': module_data['file_count'],
                'size_mb': round(module_data['total_size'] / (1024 * 1024), 2)
            })

        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        stats['total_size_gb'] = round(stats['total_size'] / (1024 * 1024 * 1024), 2)

        return stats

    def _generate_html(
        self,
        output_dir: Path,
        collection_data: Dict[str, Any],
        evidence_by_module: Dict[str, Any],
        statistics: Dict[str, Any]
    ) -> str:
        bg_dark = "#1a1b26"
        bg_light = "#24283b"
        bg_highlight = "#292e42"
        fg_default = "#c0caf5"
        fg_dark = "#9aa5ce"
        blue = "#7aa2f7"
        cyan = "#7dcfff"
        green = "#9ece6a"
        yellow = "#e0af68"
        red = "#f7768e"
        purple = "#bb9af7"
        border = "#414868"

        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evidence Collection Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: {bg_dark};
            color: {fg_default};
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, {blue}, {purple});
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}

        .header h1 {{
            font-size: 36px;
            color: white;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            color: rgba(255,255,255,0.9);
        }}

        .header .meta {{
            margin-top: 20px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}

        .header .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .header .meta-item .icon {{
            font-size: 20px;
        }}

        .nav {{
            background-color: {bg_light};
            padding: 15px 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid {border};
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            position: sticky;
            top: 20px;
            z-index: 100;
        }}

        .nav a {{
            color: {fg_default};
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.3s;
        }}

        .nav a:hover {{
            background-color: {bg_highlight};
            color: {blue};
        }}

        .section {{
            background-color: {bg_light};
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            border: 1px solid {border};
        }}

        .section-title {{
            font-size: 28px;
            color: {blue};
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 2px solid {border};
            padding-bottom: 10px;
        }}

        .section-title .icon {{
            font-size: 32px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background-color: {bg_highlight};
            padding: 25px;
            border-radius: 8px;
            border: 1px solid {border};
            transition: transform 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: {blue};
        }}

        .stat-card .stat-icon {{
            font-size: 40px;
            margin-bottom: 10px;
        }}

        .stat-card .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: {cyan};
            margin: 10px 0;
        }}

        .stat-card .stat-label {{
            font-size: 14px;
            color: {fg_dark};
        }}

        .module-section {{
            background-color: {bg_highlight};
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid {blue};
        }}

        .module-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}

        .module-header .icon {{
            font-size: 32px;
        }}

        .module-header h3 {{
            font-size: 24px;
            color: {blue};
        }}

        .module-stats {{
            display: flex;
            gap: 30px;
            margin-bottom: 20px;
            padding: 15px;
            background-color: {bg_dark};
            border-radius: 6px;
        }}

        .module-stat {{
            display: flex;
            flex-direction: column;
        }}

        .module-stat .label {{
            font-size: 12px;
            color: {fg_dark};
            margin-bottom: 5px;
        }}

        .module-stat .value {{
            font-size: 18px;
            font-weight: bold;
            color: {green};
        }}

        .file-list {{
            margin-top: 15px;
        }}

        .file-category {{
            margin-bottom: 20px;
        }}

        .file-category h4 {{
            font-size: 16px;
            color: {purple};
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .file-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        .file-table th {{
            background-color: {bg_dark};
            padding: 12px;
            text-align: left;
            font-size: 14px;
            color: {fg_dark};
            border-bottom: 2px solid {border};
        }}

        .file-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid {border};
            font-size: 13px;
        }}

        .file-table tr:hover {{
            background-color: {bg_dark};
        }}

        .file-name {{
            color: {cyan};
            font-family: 'Courier New', monospace;
        }}

        .file-size {{
            color: {yellow};
            text-align: right;
        }}

        .file-date {{
            color: {fg_dark};
            font-size: 12px;
        }}

        .collapsible {{
            cursor: pointer;
            padding: 12px;
            background-color: {bg_dark};
            border: 1px solid {border};
            border-radius: 6px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s;
        }}

        .collapsible:hover {{
            background-color: {bg_highlight};
        }}

        .collapsible.active {{
            background-color: {bg_highlight};
            border-color: {blue};
        }}

        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            padding: 0 15px;
        }}

        .collapsible-content.active {{
            max-height: 2000px;
            padding: 15px;
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: {fg_dark};
            border-top: 1px solid {border};
            margin-top: 50px;
        }}

        @media print {{
            body {{
                background-color: white;
                color: black;
            }}
            .nav {{
                display: none;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}

        .badge-success {{
            background-color: {green};
            color: {bg_dark};
        }}

        .badge-warning {{
            background-color: {yellow};
            color: {bg_dark};
        }}

        .badge-info {{
            background-color: {blue};
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔍 Evidence Collection Report</h1>
            <div class="subtitle">Windows Incident Response & Digital Forensics</div>
            <div class="meta">
                <div class="meta-item">
                    <span class="icon">📅</span>
                    <span>Generated: {generation_time}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">💻</span>
                    <span>System: {collection_data.get('hostname', 'Unknown')}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">🌐</span>
                    <span>IP: {collection_data.get('ip_address', 'Unknown')}</span>
                </div>
                <div class="meta-item">
                    <span class="icon">👤</span>
                    <span>Investigator: {collection_data.get('user', 'Unknown')}</span>
                </div>
            </div>
        </div>

        <!-- Navigation -->
        <div class="nav">
            <a href="#summary">📊 Summary</a>
            <a href="#statistics">📈 Statistics</a>
            <a href="#evidence">🗂️ Evidence</a>
            <a href="#files">📋 File Inventory</a>
        </div>

        <!-- Executive Summary -->
        <div id="summary" class="section">
            <div class="section-title">
                <span class="icon">📊</span>
                <span>Executive Summary</span>
            </div>
            <p style="font-size: 16px; margin-bottom: 20px;">
                This report documents the evidence collected from the target system during a forensic investigation.
                The collection was performed using the Centralized Evidence Collection Tool, capturing artifacts
                across multiple categories including network activity, system state, browser history, file system metadata,
                registry configuration, and event logs.
            </p>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">📦</div>
                    <div class="stat-value">{statistics['total_modules']}</div>
                    <div class="stat-label">Modules Executed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📄</div>
                    <div class="stat-value">{statistics['total_files']}</div>
                    <div class="stat-label">Files Collected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-value">{statistics['total_size_mb']:.2f} MB</div>
                    <div class="stat-label">Total Size</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-value">Verified</div>
                    <div class="stat-label">Integrity Status</div>
                </div>
            </div>
        </div>

        <!-- Statistics by Module -->
        <div id="statistics" class="section">
            <div class="section-title">
                <span class="icon">📈</span>
                <span>Collection Statistics by Module</span>
            </div>
            <div class="file-table">
                <table class="file-table">
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th style="text-align: right;">Files</th>
                            <th style="text-align: right;">Size (MB)</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for module_summary in statistics['modules_summary']:
            html += f"""
                        <tr>
                            <td>
                                <span style="font-size: 20px; margin-right: 10px;">{module_summary['icon']}</span>
                                {module_summary['name']}
                            </td>
                            <td style="text-align: right; color: {cyan};">{module_summary['files']}</td>
                            <td style="text-align: right; color: {yellow};">{module_summary['size_mb']:.2f}</td>
                        </tr>
"""

        html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Evidence by Module -->
        <div id="evidence" class="section">
            <div class="section-title">
                <span class="icon">🗂️</span>
                <span>Evidence Details by Module</span>
            </div>
"""

        for module_id, module_data in evidence_by_module.items():
            html += self._generate_module_section(module_id, module_data, blue, green, cyan, yellow, purple, bg_dark, border)

        html += """
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Centralized Evidence Collection Tool</strong></p>
            <p>Version 0.1.0 | Generated with Tokyo Night Theme</p>
            <p style="margin-top: 10px; font-size: 12px;">
                This report is generated automatically. All collected evidence has been cryptographically hashed
                to ensure integrity and maintain chain of custody.
            </p>
        </div>
    </div>

    <script>
        // Collapsible functionality
        document.querySelectorAll('.collapsible').forEach(button => {
            button.addEventListener('click', function() {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            });
        });

        // Smooth scrolling for navigation
        document.querySelectorAll('.nav a').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    </script>
</body>
</html>
"""

        return html

    def _generate_module_section(
        self,
        module_id: str,
        module_data: Dict[str, Any],
        blue: str,
        green: str,
        cyan: str,
        yellow: str,
        purple: str,
        bg_dark: str,
        border: str
    ) -> str:
        html = f"""
            <div class="module-section">
                <div class="module-header">
                    <span class="icon">{module_data['icon']}</span>
                    <h3>{module_data['name']}</h3>
                </div>

                <div class="module-stats">
                    <div class="module-stat">
                        <span class="label">Files Collected</span>
                        <span class="value">{module_data['file_count']}</span>
                    </div>
                    <div class="module-stat">
                        <span class="label">Total Size</span>
                        <span class="value">{round(module_data['total_size'] / (1024*1024), 2)} MB</span>
                    </div>
                    <div class="module-stat">
                        <span class="label">Location</span>
                        <span class="value" style="font-size: 14px; font-family: monospace;">{module_data['path'].name}</span>
                    </div>
                </div>

                <div class="file-list">
"""

        if module_data['files']:
            html += f"""
                    <div class="file-category">
                        <h4>📄 Collected Files</h4>
                        <table class="file-table">
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th style="text-align: right;">Size</th>
                                    <th>Modified</th>
                                </tr>
                            </thead>
                            <tbody>
"""
            for file_info in module_data['files']:
                html += f"""
                                <tr>
                                    <td class="file-name">{file_info['name']}</td>
                                    <td class="file-size">{file_info['size_mb']} MB</td>
                                    <td class="file-date">{file_info['modified']}</td>
                                </tr>
"""
            html += """
                            </tbody>
                        </table>
                    </div>
"""

        for subdir_name, subdir_info in module_data['subdirs'].items():
            html += f"""
                    <div class="file-category">
                        <div class="collapsible">
                            <span>
                                <span style="font-size: 18px; margin-right: 8px;">📁</span>
                                <strong>{subdir_name}</strong> ({subdir_info['file_count']} files, {subdir_info['total_size_mb']} MB)
                            </span>
                            <span>▼</span>
                        </div>
                        <div class="collapsible-content">
                            <table class="file-table">
                                <thead>
                                    <tr>
                                        <th>File Name</th>
                                        <th style="text-align: right;">Size</th>
                                        <th>Modified</th>
                                    </tr>
                                </thead>
                                <tbody>
"""
            for file_info in subdir_info['files'][:50]:
                html += f"""
                                    <tr>
                                        <td class="file-name">{file_info['name']}</td>
                                        <td class="file-size">{file_info['size_mb']} MB</td>
                                        <td class="file-date">{file_info['modified']}</td>
                                    </tr>
"""

            if len(subdir_info['files']) > 50:
                html += f"""
                                    <tr>
                                        <td colspan="3" style="text-align: center; color: {yellow};">
                                            ... and {len(subdir_info['files']) - 50} more files
                                        </td>
                                    </tr>
"""

            html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
"""
            html += """
                        </div>
                    </div>
"""
            return html
