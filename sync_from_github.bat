@echo off
chcp 65001 >nul
echo ========================================
echo 从GitHub同步最新代码并启动服务
echo ========================================
echo.

:: 先杀掉所有已运行的Python进程，避免端口冲突
echo [1/4] 停止旧服务...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel%==0 (
    echo   旧服务已停止
) else (
    echo   没有正在运行的旧服务
)
echo.

cd /d "C:\Users\Administrator\Desktop"

:: 检查是否已有项目目录
if exist "air_prd_agent" (
    echo [2/4] 检测到已存在项目，强制同步最新代码...
    cd air_prd_agent
    echo   拉取远程最新版本...
    git fetch origin
    echo   强制对齐到 origin/main（丢弃本地修改）...
    git reset --hard origin/main
) else (
    echo [2/4] 首次部署，克隆项目...
    git clone https://github.com/Zhangshengyang922/air-product-agent.git air_prd_agent
    cd air_prd_agent
)

echo.
echo [3/4] 清理Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo   缓存已清理

echo.
echo ========================================
echo [4/4] 启动服务...
echo ========================================
echo.
echo 访问地址: http://47.95.205.44:8000
echo 按 Ctrl+C 停止服务
echo.

python src\main.py -m http -p 8000

pause
