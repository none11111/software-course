@echo off
chcp 65001 >nul
echo 启动本地开发服务器...
python start.py --mode local
pause
