@echo off
chcp 65001 >nul
echo ======================================
echo 重启产品管理系统
echo ======================================
echo.

echo [1/3] 停止现有服务...
taskkill /F /PID 25316 >nul 2>&1
if %errorlevel% equ 0 (
    echo √ 服务已停止
) else (
    echo ! 未找到运行中的服务
)

echo.
echo [2/3] 等待2秒...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] 启动新服务...
echo 服务启动中，请稍候...
echo.
echo 访问地址：
echo   - 本地: http://localhost:8000
echo   - 局域网: http://192.168.101.2:8000
echo   - 登录: YNTB / yntb123
echo.
echo 按Ctrl+C停止服务
echo ======================================
echo.

python src/main.py -m http -p 8000
pause
