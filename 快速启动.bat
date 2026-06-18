@echo off
chcp 65001 > nul
echo =========================================
echo   航空公司产品智能体 - 快速启动
echo =========================================
echo.

REM 设置环境变量
set COZE_WORKSPACE_PATH=%~dp0

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.12+
    pause
    exit /b 1
)

echo [2/3] 启动服务...
echo 服务地址: http://localhost:8000
echo 局域网地址: http://192.168.101.2:8000
echo.

python src/main.py -m http -p 8000

pause

