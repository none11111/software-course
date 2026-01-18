@echo off
echo ================================================
echo           教师文档管理系统 - 代码更新工具
echo ================================================
echo.

if "%~1"=="" (
    echo 错误: 请提供新版本zip文件路径
    echo.
    echo 使用方法:
    echo   1. 将新版本zip文件放在项目根目录
    echo   2. 在命令行输入: 更新.bat 新版本.zip
    echo.
    echo 示例:
    echo   更新.bat new_version.zip
    echo.
    pause
    exit /b 1
)

set "ZIP_FILE=%~1"

if not exist "%ZIP_FILE%" (
    echo 错误: 文件不存在 - %ZIP_FILE%
    echo.
    echo 请确认:
    echo   1. 文件路径是否正确
    echo   2. 文件是否存在于当前目录
    echo   3. 文件名是否正确（包括扩展名）
    echo.
    pause
    exit /b 1
)

echo 找到更新文件: %ZIP_FILE%
echo.

echo 正在停止服务器...
python stop.py 2>nul

echo 正在创建备份...
if not exist "media\backups" mkdir "media\backups"

echo 正在更新系统...
python 简单更新.py "%ZIP_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo 系统更新成功完成！
    echo ================================================
    echo.
    echo 下一步操作:
    echo   1. 启动服务器: 双击 start_lan.bat
    echo   2. 访问系统: http://localhost:8000
    echo   3. 检查功能是否正常
    echo.
) else (
    echo.
    echo ================================================
    echo 系统更新失败！
    echo ================================================
    echo.
    echo 故障排除:
    echo   1. 检查Python环境是否正确
    echo   2. 确认zip文件格式正确
    echo   3. 查看错误信息并手动处理
    echo.
)

echo.
pause
