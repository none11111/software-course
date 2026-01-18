@echo off
chcp 65001 >nul
title 教师文档管理系统 - 从文件夹更新工具
color 0A

echo.
echo ================================================
echo           教师文档管理系统 - 从文件夹更新工具
echo ================================================
echo.

REM 检查是否提供了文件夹路径参数
if "%~1"=="" (
    echo 错误: 请提供新版本代码文件夹路径
    echo.
    echo 使用方法:
    echo   1. 将新版本代码文件夹路径作为参数传入
    echo   2. 在命令行输入: 从文件夹更新.bat "新版本文件夹路径"
    echo.
    echo 示例:
    echo   从文件夹更新.bat "E:\新代码\teacher_doc_system"
    echo   从文件夹更新.bat "C:\Users\用户名\Desktop\新版本"
    echo.
    echo 说明:
    echo   - 新版本文件夹可以是项目根目录，也可以是包含项目的父目录
    echo   - 系统会自动查找包含manage.py的项目目录
    echo   - 更新过程会自动备份用户数据和配置文件
    echo.
    pause
    exit /b 1
)

set "SOURCE_DIR=%~1"

REM 检查目录是否存在
if not exist "%SOURCE_DIR%" (
    echo ❌ 错误: 目录不存在 - %SOURCE_DIR%
    echo.
    echo 请确认:
    echo   1. 目录路径是否正确
    echo   2. 目录是否存在
    echo   3. 路径中是否包含中文字符（建议使用英文路径）
    echo.
    pause
    exit /b 1
)

echo ✅ 找到新版本代码目录: %SOURCE_DIR%
echo.

REM 执行更新
echo 🔄 开始更新系统...
python 从文件夹更新.py "%SOURCE_DIR%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo ✅ 系统更新成功完成！
    echo ================================================
) else (
    echo.
    echo ================================================
    echo ❌ 系统更新失败！
    echo ================================================
    echo.
    echo 🔧 故障排除:
    echo   1. 检查Python环境是否正确
    echo   2. 确认文件夹路径正确
    echo   3. 查看错误信息并手动处理
    echo   4. 如需恢复，请从备份目录恢复
    echo.
)

echo.
pause

