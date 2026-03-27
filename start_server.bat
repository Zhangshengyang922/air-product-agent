@echo off
chcp 65001 >nul
echo ========================================
echo 产品管理系统 - 启动服务
echo ========================================
echo.

cd /d "%~dp0"

echo 正在启动服务...
echo.
echo 服务信息:
echo   端口: 8000
echo   访问地址: http://localhost:8000
echo   局域网访问: http://本机IP:8000
echo   登录账号: YNTB / yntb123
echo.

python src\main.py -m http -p 8000

echo.
echo 服务已停止
pause
