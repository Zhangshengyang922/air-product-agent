@echo off
chcp 65001 >nul
echo ========================================
echo 产品管理系统 - 网络配置
echo ========================================
echo.

cd /d "%~dp0"

echo 请选择运行模式:
echo.
echo [1] 仅本地访问 (localhost)
echo [2] 本地+局域网访问
echo [3] 仅局域网访问
echo [4] 退出
echo.

set /p choice="请选择 (1-4): "

if "%choice%"=="1" goto local_only
if "%choice%"=="2" goto both
if "%choice%"=="3" goto lan_only
if "%choice%"=="4" goto end

echo 无效选择！
pause
goto end

:local_only
echo.
echo ========================================
echo 模式: 仅本地访问
echo ========================================
echo.
echo 访问地址:
echo   本地: http://localhost:8000
echo   127.0.0.1: http://127.0.0.1:8000
echo.
echo 局域网: 不可访问
echo.
echo 登录: YNTB / yntb123
echo.
echo 正在启动服务...
echo.
python src\main.py -m http -p 8000
goto end

:both
echo.
echo ========================================
echo 模式: 本地 + 局域网访问
echo ========================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set ip=%%a
set ip=%ip: =%

echo 访问地址:
echo   本地: http://localhost:8000
echo   127.0.0.1: http://127.0.0.1:8000
echo   局域网: http://%ip%:8000
echo.
echo 登录: YNTB / yntb123
echo.
echo 提示: 局域网内其他设备可通过 http://%ip%:8000 访问
echo.
echo 正在启动服务...
echo.
python src\main.py -m http -p 8000
goto end

:lan_only
echo.
echo ========================================
echo 模式: 仅局域网访问
echo ========================================
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do set ip=%%a
set ip=%ip: =%

echo 访问地址:
echo   局域网: http://%ip%:8000
echo.
echo 本地: http://%ip%:8000 (不使用localhost)
echo.
echo 登录: YNTB / yntb123
echo.
echo 提示: 仅允许局域网访问
echo.
echo 正在启动服务...
echo.
python src\main.py -m http -p 8000
goto end

:end
echo.
echo 服务已停止
pause
