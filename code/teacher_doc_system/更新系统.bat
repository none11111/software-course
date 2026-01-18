@echo off
chcp 65001 >nul
title 教师文档管理系统 - 代码更新工具
color 0A

echo.
echo ================================================
echo           教师文档管理系统 - 代码更新工具
echo ================================================
echo.

REM 检查是否提供了zip文件参数
if "%~1"=="" (
    echo 错误: 请提供新版本zip文件路径
    echo.
    echo 使用方法:
    echo   1. 将新版本zip文件放在项目根目录
    echo   2. 在命令行输入: 更新系统.bat 新版本.zip
    echo.
    echo 示例:
    echo   更新系统.bat new_version.zip
    echo.
    pause
    exit /b 1
)

set "ZIP_FILE=%~1"

REM 检查文件是否存在
if not exist "%ZIP_FILE%" (
    echo ❌ 错误: 文件不存在 - %ZIP_FILE%
    echo.
    echo 请确认:
    echo   1. 文件路径是否正确
    echo   2. 文件是否存在于当前目录
    echo   3. 文件名是否正确（包括扩展名）
    echo.
    pause
    exit /b 1
)

echo ✅ 找到更新文件: %ZIP_FILE%
echo.

REM 停止服务器
echo 🔄 正在停止服务器...
python stop.py 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ 服务器已停止
) else (
    echo ⚠️  服务器可能未运行
)
echo.

REM 创建备份
echo 🔄 正在创建备份...
if not exist "media\backups" mkdir "media\backups"
set "BACKUP_NAME=backup_更新前_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_NAME=%BACKUP_NAME: =0%"

REM 备份用户文件
if exist "media\user_files" (
    echo 📁 备份用户文件...
    xcopy "media\user_files" "media\backups\%BACKUP_NAME%\user_files\" /E /I /Q >nul 2>&1
    echo ✅ 用户文件备份完成
) else (
    echo ⚠️  未找到用户文件目录
)

REM 备份配置文件
if exist ".env" (
    echo 📄 备份配置文件...
    copy ".env" "media\backups\%BACKUP_NAME%\.env" >nul 2>&1
    echo ✅ 配置文件备份完成
)
echo.

REM 执行更新
echo 🔄 开始更新系统...
python quick_update.py "%ZIP_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo ✅ 系统更新成功完成！
    echo ================================================
    echo.
    echo 📋 更新内容:
    echo   - 代码文件已更新
    echo   - 数据库已迁移
    echo   - 静态文件已收集
    echo   - 用户数据已保留
    echo.
    echo 🚀 下一步操作:
    echo   1. 启动服务器: 双击 start_lan.bat
    echo   2. 访问系统: http://localhost:8000
    echo   3. 检查功能是否正常
    echo.
    echo 💾 备份位置: media\backups\%BACKUP_NAME%\
    echo.
    echo ================================================
) else (
    echo.
    echo ================================================
    echo ❌ 系统更新失败！
    echo ================================================
    echo.
    echo 🔧 故障排除:
    echo   1. 检查Python环境是否正确
    echo   2. 确认zip文件格式正确
    echo   3. 查看错误信息并手动处理
    echo   4. 如需恢复，请从备份目录恢复
    echo.
    echo 💾 备份位置: media\backups\%BACKUP_NAME%\
    echo ================================================
)

echo.
pause
