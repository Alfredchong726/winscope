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
    print(f"⚠ WinPmem not found at: {winpmem_path}")
    datas.append((str(project_root / 'tools' / 'winpmem'), 'tools/winpmem'))

readme_files = [
    'README.md',
    'tools/README.md',
]

for readme in readme_files:
    readme_path = project_root / readme
    if readme_path.exists():
        parent = str(Path(readme).parent) if Path(readme).parent != Path('.') else '.'
        datas.append((str(readme_path), parent))

print(f"\n📦 Data files to include: {len(datas)} items")

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
        'enum',
        'abc',
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
        'src.ui.module_info',
        'src.ui.styles',
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
        'xml',
        'email',
        'http',
        'urllib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
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
    icon='resources/icon.ico',
    uac_admin=True,
    uac_uiaccess=False,
)

print("\n" + "="*70)
print("✓ PyInstaller configuration complete")
print("="*70)
print(f"Output: dist/WinScope.exe")
print(f"Console: No (GUI Application)")
print(f"Admin privileges: Required")
print("="*70 + "\n")
