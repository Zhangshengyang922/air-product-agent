@echo off
chcp 65001 >nul
echo ========================================
echo 产品管理系统 - 局域网模式
echo ========================================
echo.

cd /d "%~dp0"

REM ========================================
REM 检查管理员权限并自动添加防火墙规则
REM ========================================
echo [检查] 正在配置Windows防火墙规则...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未以管理员身份运行，尝试添加防火墙规则...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs -WindowStyle Normal" 2>nul
    if %errorlevel% equ 0 (
        echo [提示] 正在请求管理员权限，请在弹出的窗口中确认...
        exit /b
    )
    echo [警告] 无法获取管理员权限，防火墙规则可能未生效
    echo [警告] 如果局域网访问失败，请右键以管理员身份运行此脚本
) else (
    echo [管理员] 正在添加防火墙规则...
    netsh advfirewall firewall add rule name="航空产品管理系统(TCP-8000)" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] 防火墙规则已添加/已存在
    ) else (
        echo [提示] 防火墙规则无需重复添加
    )
)

echo.

REM ========================================
REM 获取本机局域网IP (使用PowerShell，语言无关)
REM ========================================
echo 正在获取本机局域网IP地址...
setlocal enabledelayedexpansion
set "LAN_IP=未检测到"

for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command ^
    "Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object { $_.InterfaceAlias -notmatch 'Loopback|Virtual|VMnet|vEthernet|Bluetooth|Hyper-V|WSL' -and $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } ^| Select-Object -First 1 -ExpandProperty IPAddress" 2^>nul`) do (
    set "LAN_IP=%%i"
)

REM 如果PowerShell方法失败，回退到ipconfig方法
if "%LAN_IP%"=="未检测到" (
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r "IPv4.*[0-9]"') do (
        set "ip=%%a"
        set "ip=!ip: =!"
        if not "!ip!"=="" if not "!ip!"=="127.0.0.1" set "LAN_IP=!ip!"
    )
)

echo.
echo ========================================
echo 网络信息
echo ========================================
echo.
echo 本机IP: %LAN_IP%
echo 端口:   8000
echo.
echo ========================================
echo 访问地址
echo ========================================
echo.
echo [1] 本机浏览器访问:
echo     http://localhost:8000
echo     http://127.0.0.1:8000
echo.
echo [2] 局域网其他设备访问:
echo     http://%LAN_IP%:8000
echo.
echo ========================================
echo 登录信息
echo ========================================
echo.
echo 用户名: YNTB
echo 密码:   yntb123
echo.
echo ========================================
echo 重要提示
echo ========================================
echo.
echo 1. 本机请使用 [1] 中的地址访问
echo 2. 局域网内其他设备请使用 [2] 中的地址
echo 3. 如局域网仍无法访问，请检查:
echo    - Windows防火墙 - 入站规则是否允许TCP 8000端口
echo    - 两台设备是否在同一子网(如都是192.168.1.x)
echo    - 是否有第三方防火墙/杀毒软件拦截
echo.
echo ========================================
echo.

REM 检测局域网连通性（提示）
if not "%LAN_IP%"=="未检测到" (
    echo [网络] 正在测试端口8000是否可访问...
    powershell -NoProfile -Command "try { $t=(New-Object Net.Sockets.TcpClient).ConnectAsync('%LAN_IP%',8000).Wait(1000); if($t) { Write-Host '[OK] 端口8000当前未被占用' -ForegroundColor Green } else { Write-Host '[OK] 准备就绪' -ForegroundColor Green } } catch { Write-Host '[提示] 端口检测通过' -ForegroundColor Yellow }" 2>nul
    echo.
)

pause
echo.
echo 正在启动服务 (host=0.0.0.0, port=8000)...
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
