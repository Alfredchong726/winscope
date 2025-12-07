================================================================================
Evidence Collection Tool for Windows Incident Response
Version 0.1.0 - Alpha Release
================================================================================

DESCRIPTION
-----------
A comprehensive tool for collecting digital evidence from Windows systems
during incident response and forensic investigations.

FEATURES
--------
✓ Network Collection - Active connections, ARP cache, routing tables
✓ Live System - Running processes, services, scheduled tasks
✓ Browser Artifacts - History, bookmarks, cookies from Chrome/Edge/Firefox
✓ File System - Recent files, startup items, temp files
✓ Registry - System and user registry hives
✓ Event Logs - Windows event logs

SYSTEM REQUIREMENTS
-------------------
- Operating System: Windows 10/11 (64-bit)
- Privileges: Some modules require Administrator rights
- Disk Space: At least 500 MB free space
- RAM: Minimum 4 GB

INSTALLATION
------------
No installation required! Simply run EvidenceCollectionTool.exe

USAGE
-----
1. Run EvidenceCollectionTool.exe (Right-click > Run as Administrator recommended)
2. Select the modules you want to execute
3. Configure output directory and settings
4. Click "Start Collection"
5. Wait for collection to complete
6. Click "View Report" to see results

IMPORTANT NOTES
---------------
⚠ Administrator Privileges Required For:
  - Registry Collection
  - Event Logs Collection
  - Some system files access

⚠ Evidence Handling:
  - All collected evidence is cryptographically hashed
  - Maintain proper chain of custody
  - Store evidence securely

GETTING HELP
------------
- Check the Help menu in the application
- Visit: https://github.com/yourusername/evidence-collection-tool
- Report issues: https://github.com/yourusername/evidence-collection-tool/issues

LICENSE
-------
MIT

DISCLAIMER
----------
This tool is intended for authorized forensic investigations and incident
response activities only. Users are responsible for ensuring they have
proper authorization before collecting evidence from any system.
