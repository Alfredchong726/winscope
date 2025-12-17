# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

project_root = Path('.').absolute()
src_path = project_root / 'src'

block_cipher = None

a = Analysis(
    ['src/main.py'],  # 入口文件
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        ('tools/README.md', 'tools'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'psutil',
        'src.services.logger',
        'src.services.config_manager',
        'src.services.hash_calculator',
        'src.services.privilege_manager',
        'src.services.report_generator',
        'src.core.evidence_controller',
        'src.modules.network_module',
        'src.modules.live_system_module',
        'src.modules.browser_module',
        'src.modules.filesystem_module',
        'src.modules.registry_module',
        'src.modules.eventlogs_module',
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
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EvidenceCollectionTool',
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
    icon='resources/icon.ico' if Path('resources/icon.ico').exists() else None,
)
