@echo off
chcp 65001 >nul
echo ====================================
echo 航空产品智能体 - 服务管理
echo ====================================
echo.
echo [1] 启动服务
echo [2] 停止服务
echo [3] 重启服务
echo [4] 查看状态
echo [5] 卸载服务
echo [6] 退出
echo.

set /p choice="请选择操作 (1-6): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto remove
if "%choice%"=="6" goto end

:start
echo.
nssm start AirAgent
goto done

:stop
echo.
nssm stop AirAgent
goto done

:restart
echo.
nssm restart AirAgent
goto done

:status
echo.
nssm status AirAgent
goto done

:remove
echo.
nssm stop AirAgent 2>nul
nssm remove AirAgent confirm
echo 服务已卸载！
goto done

:done
echo.
pause

:end
