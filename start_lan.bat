@echo off
chcp 65001 >nul
echo ========================================
echo 产品管理系统 - 局域网模式
echo ========================================
echo.

cd /d "%~dp0"

echo 正在获取本机IP地址...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set ip=%%a
set ip=%ip: =%

echo.
echo ========================================
echo 网络信息
echo ========================================
echo.
echo 本机IP: %ip%
echo 端口: 8000
echo.
echo ========================================
echo 访问地址
echo ========================================
echo.
echo [1] 本地访问:
echo     http://localhost:8000
echo     http://127.0.0.1:8000
echo.
echo [2] 局域网访问:
echo     http://%ip%:8000
echo.
echo [3] 本机访问:
echo     http://%ip%:8000
echo.
echo ========================================
echo 登录信息
echo ========================================
echo.
echo 用户名: YNTB
echo 密码: yntb123
echo.
echo ========================================
echo 提示
echo ========================================
echo.
echo 1. 本机可使用上述任意地址访问
echo 2. 局域网内其他设备请使用: http://%ip%:8000
echo 3. 确保Windows防火墙允许8000端口
echo.
echo ========================================
echo.

pause
echo.
echo 正在启动服务...
echo.
echo 按 Ctrl+C 可停止服务
echo.

python src\main.py -m http -p 8000

echo.
echo.
echo ========================================
echo 服务已停止
echo ========================================
echo.
pause
