@echo off
chcp 65001 >nul
echo ================================================
echo 教师文档管理系统 - 代码更新工具
echo ================================================
echo.

if "%~1"=="" (
    echo 使用方法: update_system.bat ^<新版本zip文件路径^>
    echo 示例: update_system.bat new_version.zip
    echo.
    pause
    exit /b 1
)

set "ZIP_FILE=%~1"

if not exist "%ZIP_FILE%" (
    echo 错误: 文件不存在 - %ZIP_FILE%
    echo.
    pause
    exit /b 1
)

echo 准备更新系统，新版本文件: %ZIP_FILE%
echo 注意: 此操作将更新系统代码，但会保留用户数据
echo.
set /p "CONFIRM=确认继续更新吗？(y/N): "

if /i not "%CONFIRM%"=="y" (
    echo 更新已取消
    echo.
    pause
    exit /b 0
)

echo.
echo 开始更新系统...
echo.

REM 停止服务器（如果正在运行）
echo 停止服务器...
python stop.py 2>nul

REM 运行更新脚本
echo 执行更新...
python quick_update.py "%ZIP_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo ✅ 系统更新完成！
    echo ================================================
    echo 下一步:
    echo 1. 重启服务器: start_lan.bat
    echo 2. 检查系统功能
    echo 3. 如有问题，可从 media\backups\ 恢复
    echo ================================================
) else (
    echo.
    echo ❌ 系统更新失败！
    echo 请检查错误信息并手动处理
)

echo.
pause
