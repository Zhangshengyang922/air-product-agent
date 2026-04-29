@echo off
chcp 65001 >nul
echo ========================================
echo 从GitHub同步最新代码到阿里云
echo ========================================
echo.

cd /d "C:\Users\Administrator\Desktop"

:: 检查是否已有项目目录
if exist "air_prd_agent" (
    echo 检测到已存在项目目录，进入更新模式...
    cd air_prd_agent
    echo.
    echo 正在从GitHub拉取最新代码...
    git pull origin main
) else (
    echo 正在克隆项目...
    git clone https://github.com/Zhangshengyang922/air-product-agent.git air_prd_agent
    cd air_prd_agent
)

echo.
echo ========================================
echo 同步完成！
echo ========================================
echo.
echo 正在启动服务...

:: 启动服务
python src\main.py -m http -p 8000

pause
