# WinScope v0.2.0 Release Notes

## 🎉 What's New

### Major Features
- **Enhanced Progress Tracking**: Real-time progress updates for Memory and Disk acquisition modules
- **Improved UI**: Tokyo Night themed interface with better visual feedback
- **Module Status Display**: Clear status indicators for each collection module
- **Comprehensive Logging**: Detailed CSV and text log generation

### Modules Included
- ✅ Memory Acquisition (Volatility Compatible)
- ✅ Disk Acquisition (Autopsy Compatible)
- ✅ Network Collection
- ✅ Registry Export
- ✅ Event Logs Collection
- ✅ Browser Artifacts
- ✅ Live System Information
- ✅ File System Metadata

### Key Improvements
- **Better Error Handling**: Graceful handling of missing tools and permissions
- **Hash Verification**: MD5, SHA-1, and SHA-256 support for evidence integrity
- **Professional Reports**: HTML reports compatible with forensic workflows
- **Modular Architecture**: Easy to extend with new collection modules

## 📋 Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Privileges**: Administrator rights required for most modules
- **RAM**: Minimum 4GB recommended
- **Disk Space**: Varies by collection scope (typically 1-50GB)

## 🚀 Installation

### Basic Installation
1. Download `WinScope-v0.2.0.zip`
2. Extract to a folder of your choice
3. Right-click `WinScope.exe` and select "Run as Administrator"

### Optional: WinPmem for Memory Acquisition
1. Download WinPmem from [Velocidex/WinPmem](https://github.com/Velocidex/WinPmem/releases)
2. Place `winpmem.exe` in `tools/winpmem/` folder
3. Restart WinScope

## 📖 Usage

1. Launch WinScope as Administrator
2. Select desired evidence collection modules
3. Configure output directory and compression settings
4. Click "Start Collection"
5. Monitor progress in real-time
6. Review generated HTML report upon completion

## 🔧 Configuration

WinScope supports:
- Multiple hash algorithms (MD5, SHA-1, SHA-256)
- Compression formats (ZIP, 7-Zip, or none)
- Custom evidence package naming
- Profile saving/loading for repeated collections

## 🐛 Known Issues

- Memory acquisition requires WinPmem to be manually downloaded due to licensing
- Some antivirus software may flag the executable (false positive)
- Large memory acquisitions (>32GB) may take significant time to hash

## 📝 Changelog

### Added
- Progress bar updates for module execution
- System information collection
- Autopsy and Volatility compatibility guides
- Hash verification with multiple algorithms

### Improved
- UI responsiveness during collection
- Error messages and logging
- Module initialization checks

### Fixed
- Progress tracking accuracy
- Memory leak in long-running collections
- Path resolution in packaged executable

## 🔒 Security Notes

- Always run from a trusted source
- Verify file hashes before execution
- Use on systems you have authorization to analyze
- Follow proper chain of custody procedures

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/WinScope/issues)
- **Documentation**: [Project Wiki](https://github.com/YOUR-USERNAME/WinScope/wiki)

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- WinPmem by Velocidex
- PyQt6 for the GUI framework
- The digital forensics community for inspiration

---

**Full Changelog**: https://github.com/YOUR-USERNAME/WinScope/compare/v0.1.0...v0.2.0
