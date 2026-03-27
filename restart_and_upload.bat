# 重启服务器的批处理脚本
# 停止现有服务器
taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" 2>nul
timeout /t 2

# 启动新服务器
cd /d "%~dp0"
start "AirProduct Server" python src\main.py
