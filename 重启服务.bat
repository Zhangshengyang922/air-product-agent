@echo off
chcp 65001 > nul
echo =========================================
echo   重启航空智能体服务
echo =========================================
echo.

REM 设置环境变量
set COZE_WORKSPACE_PATH=%~dp0

echo [1/3] 停止现有服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)
echo 已停止服务
echo.

echo [2/3] 等待端口释放...
timeout /t 2 /nobreak > nul
echo.

echo [3/3] 启动新服务...
echo 服务地址: http://localhost:8000
echo 局域网地址: http://192.168.101.2:8000
echo.

start python src/main.py -m http -p 8000

echo.
echo [OK] 服务已启动！
echo.
echo 等待5秒后自动打开浏览器...
timeout /t 5 /nobreak > nul
start http://localhost:8000

echo.
echo 服务已在后台运行
echo 关闭此窗口不会影响服务运行
pause

