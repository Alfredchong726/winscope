# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

project_root = Path(SPECPATH)

datas = []

winpmem_path = project_root / 'tools' / 'winpmem' / 'winpmem.exe'
if winpmem_path.exists():
    datas.append((str(winpmem_path), 'tools/winpmem'))
    print(f"✓ Found WinPmem: {winpmem_path}")
else:
    print(f"⚠ WinPmem not found - will generate instructions at runtime")
    # 创建空目录结构
    tools_dir = project_root / 'tools' / 'winpmem'
    tools_dir.mkdir(parents=True, exist_ok=True)
    datas.append((str(tools_dir), 'tools/winpmem'))

readme_files = [
    'README.md',
]

for readme in readme_files:
    readme_path = project_root / readme
    if readme_path.exists():
        datas.append((str(readme_path), '.'))

print(f"\n📦 Data files to include: {len(datas)} items")

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'json',
        'csv',
        'pathlib',
        'subprocess',
        'threading',
        'hashlib',
        'zipfile',
        'sqlite3',
        'datetime',
        'time',
        'platform',
        'getpass',
        'socket',
        'psutil',
        'src.modules.base_module',
        'src.modules.memory_module',
        'src.modules.network_module',
        'src.modules.disk_module',
        'src.modules.registry_module',
        'src.modules.eventlogs_module',
        'src.modules.browser_module',
        'src.modules.live_system_module',
        'src.modules.filesystem_module',
        'src.services.logger',
        'src.services.hash_calculator',
        'src.services.config_manager',
        'src.services.privilege_manager',
        'src.services.report_generator',
        'src.core.evidence_controller',
        'src.ui.main_window',
        'src.ui.widgets',
        'src.ui.styles',
        'src.ui.module_info',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'unittest',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WinScope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/winscope_icon.ico',
    uac_admin=True,
    uac_uiaccess=False,
)

print("\n" + "="*70)
print("✓ PyInstaller configuration complete")
print("="*70)
print(f"Output: dist/WinScope.exe")
print(f"Console: No (GUI application)")
print(f"Admin privileges: Required")
print("="*70 + "\n")
