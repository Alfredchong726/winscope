@echo off
REM 打包 Release 版本

echo ========================================
echo Packaging Release
echo ========================================
echo.

REM 设置版本号
set VERSION=0.1.0

REM 创建release目录
if not exist release mkdir release
if not exist release\docs mkdir release\docs

REM 复制EXE
echo Copying executable...
copy dist\EvidenceCollectionTool.exe release\

REM 复制文档
echo Copying documentation...
copy release\README.txt release\
copy release\LICENSE.txt release\

REM 创建ZIP压缩包
echo Creating ZIP archive...
powershell Compress-Archive -Path release\* -DestinationPath EvidenceCollectionTool-v%VERSION%-Windows-x64.zip -Force

echo.
echo ========================================
echo Release package created!
echo ========================================
echo.
echo File: EvidenceCollectionTool-v%VERSION%-Windows-x64.zip
dir EvidenceCollectionTool-v%VERSION%-Windows-x64.zip
echo.

pause
