@echo off
chcp 65001 > nul
echo =========================================
echo   后台启动航空智能体服务
echo =========================================
echo.

REM 设置环境变量
set COZE_WORKSPACE_PATH=%~dp0

echo [1/2] 检查端口8000...
netstat -ano | findstr :8000
if not errorlevel 1 (
    echo [警告] 端口8000已被占用
    echo 请先停止现有服务或使用其他端口
    pause
    exit /b 1
)

echo [2/2] 后台启动服务...
echo 服务地址: http://localhost:8000
echo 局域网地址: http://192.168.101.2:8000
echo.

start "Airline Agent" python src/main.py -m http -p 8000

echo.
echo [OK] 服务已在后台启动！
echo.

pause
