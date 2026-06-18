@echo off
chcp 65001 > nul
echo =========================================
echo   停止航空智能体服务
echo =========================================
echo.

echo 正在查找并停止端口8000上的服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 停止进程 %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo [OK] 服务已停止
echo.

pause
