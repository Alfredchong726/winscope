from pathlib import Path
import sys

def check_tools():

    project_root = Path(__file__).parent.parent
    tools_dir = project_root / "tools"

    print("=" * 70)
    print("WinScope External Tools Check")
    print("=" * 70)
    print()

    tools_status = []

    winpmem_path = tools_dir / "winpmem" / "winpmem.exe"
    if winpmem_path.exists():
        size_mb = winpmem_path.stat().st_size / (1024 * 1024)
        print(f"✓ WinPmem found: {winpmem_path}")
        print(f"  Size: {size_mb:.2f} MB")
        tools_status.append(("WinPmem", True))
    else:
        print(f"✗ WinPmem NOT found")
        print(f"  Expected at: {winpmem_path}")
        print(f"  Download from: https://github.com/Velocidex/WinPmem/releases")
        tools_status.append(("WinPmem", False))

    print()

    dumpit_path = tools_dir / "dumpit" / "DumpIt.exe"
    if dumpit_path.exists():
        print(f"✓ DumpIt found: {dumpit_path}")
        tools_status.append(("DumpIt", True))
    else:
        print(f"○ DumpIt NOT found (optional)")
        print(f"  Download from: https://www.magnetforensics.com/")
        tools_status.append(("DumpIt", False))

    print()

    rawcopy_path = tools_dir / "rawcopy" / "RawCopy64.exe"
    if rawcopy_path.exists():
        print(f"✓ RawCopy found: {rawcopy_path}")
        tools_status.append(("RawCopy", True))
    else:
        print(f"○ RawCopy NOT found (optional)")
        print(f"  Download from: https://github.com/jschicht/RawCopy")
        tools_status.append(("RawCopy", False))

    print()
    print("=" * 70)
    print("Summary:")
    print("=" * 70)

    for tool_name, found in tools_status:
        status = "✓ Installed" if found else "✗ Missing"
        print(f"{tool_name:<15} {status}")

    print()

    required_tools = ["WinPmem"]
    missing_required = [name for name, found in tools_status
                       if name in required_tools and not found]

    if missing_required:
        print("⚠️  WARNING: Required tools missing!")
        print(f"   Please install: {', '.join(missing_required)}")
        print()
        print("   See tools/README.md for installation instructions")
        return False
    else:
        print("✓ All required tools are installed!")
        return True

if __name__ == "__main__":
    success = check_tools()
    sys.exit(0 if success else 1)
