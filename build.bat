@echo off
echo ========================================
echo  Building WinScope v0.2.0
echo ========================================
echo.

echo [1/5] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo      Done.
echo.

echo [2/5] Checking for WinPmem...
if exist tools\winpmem\winpmem.exe (
    echo      ✓ WinPmem found
) else (
    echo      ⚠ WinPmem not found - will generate instructions at runtime
)
echo.

echo [3/5] Checking PyInstaller...
uv pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo      Installing PyInstaller...
    uv pip install pyinstaller
) else (
    echo      ✓ PyInstaller already installed
)
echo.

echo [4/5] Building executable...
echo      This may take 2-3 minutes...
pyinstaller build_exe.spec
if errorlevel 1 (
    echo      ✗ Build failed!
    pause
    exit /b 1
)
echo      ✓ Build successful
echo.

echo [5/5] Build complete!
echo.
echo ========================================
echo  Output Location
echo ========================================
echo.
dir dist\WinScope.exe
echo.
echo To run: dist\WinScope.exe
echo.
pause
