@echo off
chcp 65001 >nul
echo 启动局域网服务器...
python start.py --mode lan
pause
