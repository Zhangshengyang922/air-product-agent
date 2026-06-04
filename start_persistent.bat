@echo off
chcp 65001 >nul
echo ====================================
echo 航空产品管理系统 - 常驻运行模式
echo ====================================
echo.

:: 检查是否已安装nssm
where nssm >nul 2>&1
if %errorlevel%==0 (
    echo [方式1] 使用 nssm 服务方式运行
    nssm install AirAgent "python" "src\main.py -m http -p 8000"
    nssm set AirAgent AppDirectory "%~dp0"
    nssm start AirAgent
    echo 服务已安装并启动！
    echo 访问地址: http://localhost:8000
    pause
    exit /b
)

:: 方式2：使用start /b后台运行
echo [方式2] 使用后台运行模式...
cd /d "%~dp0"
start /b pythonw src\main.py -m http -p 8000 >nul 2>&1

:: 等待启动
timeout /t 2 >nul

:: 检查是否运行成功
netstat -an | findstr ":8000" >nul
if %errorlevel%==0 (
    echo.
    echo ====================================
    echo  智能体已成功启动！（常驻后台运行）
    echo ====================================
    echo  访问地址: http://localhost:8000
    echo  登录账号: YNTB / yntb123
    echo.
    echo  此窗口可以关闭，智能体将继续运行！
    echo.
) else (
    echo  启动可能遇到问题，请检查Python环境。
)

echo.
pause
