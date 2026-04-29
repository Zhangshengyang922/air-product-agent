@echo off
chcp 65001 >nul
echo ========================================
echo 部署到阿里云服务器
echo ========================================
echo.

cd /d "%~dp0"

echo 请输入阿里云服务器配置：
echo.

set /p server_ip="服务器公网IP (例如: 123.45.67.89): "
set /p server_user="服务器用户名 (例如: root): "
set /p server_path="部署路径 (例如: /workspace/air_prd_agent): "

echo.
echo ========================================
echo 部署信息确认
echo ========================================
echo 服务器IP: %server_ip%
echo 用户名: %server_user%
echo 部署路径: %server_path%
echo.
echo 正在上传文件...
echo.

:: 创建部署包（排除不必要文件）
echo 正在打包项目文件...

:: 上传核心文件到服务器
echo 上传 src 目录...
scp -r src %server_user%@%server_ip%:%server_path%/src

echo 上传 static 目录...
scp -r static %server_user%@%server_ip%:%server_path%/static

echo 上传 assets 目录...
scp -r assets %server_user%@%server_ip%:%server_path%/assets

echo 上传 config 目录...
scp -r config %server_user%@%server_ip%:%server_path%/config

echo 上传核心文件...
scp main.py requirements.txt Dockerfile .gitignore README.md %server_user%@%server_ip%:%server_path%/

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 接下来在服务器上执行以下命令启动服务：
echo.
echo   cd %server_path%
echo   pip install -r requirements.txt
echo   python src/main.py -m http -p 8000
echo.
echo 或使用Docker:
echo   docker build -t air_prd_agent .
echo   docker run -d -p 8000:8000 air_prd_agent
echo.
pause
