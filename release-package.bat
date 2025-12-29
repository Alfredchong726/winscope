@echo off
echo ========================================
echo  Creating WinScope v0.2.0 Release Package
echo ========================================
echo.

set VERSION=0.2.0
set RELEASE_DIR=WinScope-v%VERSION%

if not exist dist\WinScope.exe (
    echo ERROR: WinScope.exe not found in dist folder
    echo Please run build.bat first!
    pause
    exit /b 1
)

if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
if exist %RELEASE_DIR%.zip del /q %RELEASE_DIR%.zip

echo [1/4] Creating release directory structure...
mkdir %RELEASE_DIR%
mkdir %RELEASE_DIR%\tools
mkdir %RELEASE_DIR%\tools\winpmem

echo [2/4] Copying WinScope.exe...
copy dist\WinScope.exe %RELEASE_DIR%\

echo [3/4] Copying documentation...
if exist README.md copy README.md %RELEASE_DIR%\
if exist LICENSE copy LICENSE %RELEASE_DIR%\

echo [4/4] Creating usage guide...
(
echo WinScope - Digital Forensics Evidence Collection Tool
echo =====================================================
echo Version: %VERSION%
echo.
echo INSTALLATION:
echo 1. Extract all files to a folder
echo 2. Right-click WinScope.exe and select "Run as Administrator"
echo.
echo OPTIONAL - WinPmem for Memory Acquisition:
echo 1. Download WinPmem from: https://github.com/Velocidex/WinPmem/releases
echo 2. Place winpmem.exe in the tools\winpmem\ folder
echo 3. Restart WinScope
echo.
echo REQUIREMENTS:
echo - Windows 10/11 64-bit
echo - Administrator privileges required for most modules
echo - At least 4GB RAM recommended
echo - Sufficient disk space for evidence collection
echo.
echo USAGE:
echo 1. Launch WinScope.exe as Administrator
echo 2. Select evidence collection modules
echo 3. Configure output directory and settings
echo 4. Click "Start Collection"
echo 5. View generated report when complete
echo.
echo TROUBLESHOOTING:
echo - If application doesn't start, ensure you're running as Administrator
echo - Check Windows Defender hasn't quarantined the executable
echo - Verify sufficient disk space in output directory
echo.
echo For more information, visit:
echo https://github.com/YOUR-USERNAME/WinScope
echo.
) > %RELEASE_DIR%\USAGE.txt

(
echo WinPmem Installation Instructions
echo ==================================
echo.
echo WinPmem is required for memory acquisition functionality.
echo.
echo DOWNLOAD:
echo 1. Visit: https://github.com/Velocidex/WinPmem/releases
echo 2. Download the latest winpmem_mini_x64.exe
echo 3. Rename it to winpmem.exe
echo 4. Place it in this folder
echo.
echo After installation:
echo - Restart WinScope
echo - The Memory Collection module will be enabled
echo.
) > %RELEASE_DIR%\tools\winpmem\README.txt

if exist tools\winpmem\winpmem.exe (
    echo    Copying WinPmem...
    copy tools\winpmem\winpmem.exe %RELEASE_DIR%\tools\winpmem\
)

echo.
echo Creating ZIP archive...
powershell -command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%RELEASE_DIR%.zip' -Force"

echo.
echo ========================================
echo  Release Package Created Successfully!
echo ========================================
echo.
echo Package: %RELEASE_DIR%.zip
echo Size:
dir %RELEASE_DIR%.zip | find ".zip"
echo.
echo Contents:
dir /b %RELEASE_DIR%
echo.
echo Ready for GitHub Release!
echo.
pause
