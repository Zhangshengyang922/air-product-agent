@echo off
echo ========================================
echo 重启服务器并更新产品航司字段
echo ========================================

echo.
echo 1. 停止现有服务器...
taskkill /F /IM python.exe 2>nul

echo.
echo 2. 启动服务器...
start /B python src/main.py

echo.
echo 3. 等待服务器启动...
timeout /t 5 /nobreak

echo.
echo 4. 更新产品航司字段...
python call_update_api.py

echo.
echo 完成!
pause
