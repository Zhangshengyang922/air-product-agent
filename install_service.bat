@echo off
chcp 65001 >nul
echo ====================================
echo 航空产品智能体 - NSSM服务安装
echo ====================================
echo.

:: 获取脚本所在目录
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: 检查nssm是否已安装
echo [1/4] 检查nssm安装状态...

where nssm >nul 2>&1
if %errorlevel% neq 0 (
    echo nssm未安装，正在下载...
    
    :: 下载nssm到临时目录
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.64.zip' -OutFile '%TEMP%\nssm.zip'"
    
    :: 解压nssm
    powershell -Command "Expand-Archive -Path '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\' -Force"
    
    :: 复制nssm到项目目录
    xcopy /Y "%TEMP%\nssm-2.64\nssm.exe" "%PROJECT_DIR%" >nul 2>&1
    del "%TEMP%\nssm.zip"
    rmdir /S /Q "%TEMP%\nssm-2.64" 2>nul
    
    echo nssm安装完成！
) else (
    echo nssm已安装！
)

echo.
echo [2/4] 停止旧服务（如有）...
nssm stop AirAgent 2>nul
nssm remove AirAgent confirm 2>nul

echo.
echo [3/4] 注册新服务...
nssm install AirAgent "%PROJECT_DIR%Scripts\python.exe" "python.exe src\main.py -m http -p 8000"
nssm set AirAgent AppDirectory "%PROJECT_DIR%"
nssm set AirAgent DisplayName "航空产品智能体服务"
nssm set AirAgent Description "航空产品管理系统智能体，运行在8000端口"
nssm set AirAgent Start SERVICE_AUTO_START

echo.
echo [4/4] 启动服务...
nssm start AirAgent

echo.
echo ====================================
echo  服务安装完成！
echo ====================================
echo.
echo 服务名称: AirAgent
echo 访问地址: http://localhost:8000
echo 登录账号: YNTB / yntb123
echo.
echo 常用命令:
echo   nssm start AirAgent    - 启动服务
echo   nssm stop AirAgent     - 停止服务
echo   nssm restart AirAgent  - 重启服务
echo   nssm status AirAgent   - 查看状态
echo   sc delete AirAgent     - 删除服务
echo.
echo 按任意键退出...
pause >nul
