@echo off
chcp 65001 >nul
echo 停止所有服务...
python stop.py --all
pause
