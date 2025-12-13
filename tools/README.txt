# External Forensic Tools

This directory contains external forensic tools required by WinScope for advanced evidence collection.

## 📥 Required Tools

### 1. WinPmem - Memory Acquisition

**Purpose:** Acquire physical memory (RAM) for forensic analysis

**Download:**
- Official: https://github.com/Velocidex/WinPmem/releases
- Version: Latest stable release
- File: `winpmem_mini_x64_rc2.exe` or `winpmem_mini_x64.exe`

**Installation:**
1. Download `winpmem_mini_x64.exe` from the GitHub releases page
2. Place it in `tools/winpmem/winpmem_mini_x64.exe`
3. Rename to `winpmem.exe` for consistency

**License:** Apache 2.0
**Requirements:** Administrator privileges

**Path in WinScope:**
```
tools/winpmem/winpmem.exe
```

---

### 2. DumpIt - Alternative Memory Acquisition (Optional)

**Purpose:** Alternative memory acquisition tool

**Download:**
- Source: https://www.magnetforensics.com/resources/magnet-dumpit-for-windows/
- Registration required (free)

**Installation:**
1. Download and extract
2. Place `DumpIt.exe` in `tools/dumpit/`

**License:** Commercial (Free for forensic use)

**Path in WinScope:**
```
tools/dumpit/DumpIt.exe
```

---

### 3. RawCopy - Locked File Access (Optional)

**Purpose:** Copy locked files (e.g., registry hives, event logs)

**Download:**
- Source: https://github.com/jschicht/RawCopy
- Latest release

**Installation:**
1. Download `RawCopy64.exe`
2. Place in `tools/rawcopy/`

**Path in WinScope:**
```
tools/rawcopy/RawCopy64.exe
```

---

### 4. Npcap - Network Packet Capture (Optional)

**Purpose:** Capture network traffic in PCAP format for Wireshark

**Download:**
- Official: https://npcap.com/#download
- Install the driver

**Installation:**
1. Download Npcap installer
2. Run installer (requires admin)
3. Check "WinPcap API-compatible Mode"

**License:** Custom (Free for non-commercial use)

---

## 🔒 Security Considerations

**Important:**
- Only download tools from official sources
- Verify checksums/signatures before use
- Keep tools updated
- These tools require administrator privileges

---

## 📋 Quick Setup Checklist

- [ ] Download WinPmem from GitHub
- [ ] Place in `tools/winpmem/winpmem.exe`
- [ ] Verify it runs: `tools\winpmem\winpmem.exe --help`
- [ ] (Optional) Download DumpIt
- [ ] (Optional) Download RawCopy
- [ ] (Optional) Install Npcap

---

## 🚫 What NOT to Include

Do not commit these tools to Git repository:
- They are large binary files
- License restrictions
- Should be downloaded by end users

Instead, WinScope will:
1. Check if tools exist
2. Provide download links if missing
3. Guide users through setup

---

## 🔗 Alternative Sources

If official links are unavailable, check:
- SANS SIFT Workstation (includes many tools)
- Kali Linux forensics packages
- Digital Forensics Framework repositories
