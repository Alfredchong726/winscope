@echo off
REM 构建 Evidence Collection Tool 可执行文件

echo ========================================
echo Building Evidence Collection Tool
echo ========================================
echo.

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 清理旧的构建文件
echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 使用PyInstaller构建
echo.
echo Building executable...
pyinstaller build_exe.spec --clean

REM 检查是否成功
if exist dist\EvidenceCollectionTool.exe (
    echo.
    echo ========================================
    echo Build successful!
    echo ========================================
    echo.
    echo Executable location: dist\EvidenceCollectionTool.exe
    echo.

    REM 显示文件信息
    dir dist\EvidenceCollectionTool.exe
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
)

pause
