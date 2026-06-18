@echo off
chcp 65001 > nul
echo =========================================
echo   检查服务状态
echo =========================================
echo.

echo [1/2] 检查端口8000...
netstat -ano | findstr :8000
if errorlevel 1 (
    echo.
    echo [警告] 端口8000上没有运行的服务
) else (
    echo.
    echo [OK] 服务正在运行
)

echo.
echo [2/2] 检查进程...
wmic process where "name='python.exe'" get processid,commandline | findstr main.py
if errorlevel 1 (
    echo [警告] 未找到运行main.py的Python进程
) else (
    echo [OK] 找到运行中的服务进程
)

echo.
pause
