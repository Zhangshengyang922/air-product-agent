@echo off
chcp 65001 >nul
echo ========================================
echo CSV数据文件快速更新工具 v3.2
echo ========================================
echo.

cd /d "%~dp0"

:: 创建CSV更新目录（如果不存在）
if not exist "csv_updates" mkdir csv_updates

echo 说明：
echo 1. 请将要更新的CSV文件放入 "csv_updates" 文件夹
echo 2. 支持的文件：
echo    - 各航司汇总产品-*.csv （航司产品数据）
echo    - 26年大客户汇总表-*.csv （大客户数据）
echo    - products.csv （完整产品数据）
echo.
echo 当前 csv_updates 目录内容：
echo.
dir csv_updates\*.csv /b 2>nul
if errorlevel 1 echo    (空文件夹)
echo.

set /p confirm="确认更新? (Y/N): "
if /i not "%confirm%"=="Y" goto end

echo.
echo ========================================
echo 正在更新CSV文件...
echo ========================================
echo.

:: 复制完整products.csv到static和assets目录
echo [1/4] 更新完整产品数据文件...
if exist "csv_updates\products.csv" (
    echo 复制 products.csv
    copy /y "csv_updates\products.csv" "assets\products.csv" >nul
    copy /y "csv_updates\products.csv" "static\products.csv" >nul
)

:: 复制航司CSV到static和assets目录
echo [2/4] 更新航司产品数据文件...
for %%f in (csv_updates\各航司汇总产品-*.csv) do (
    echo 复制: %%~nxf
    copy /y "%%f" "static\%%~nxf" >nul
    copy /y "%%f" "assets\%%~nxf" >nul
)

:: 复制大客户CSV到static目录
echo [3/4] 更新大客户数据文件...
for %%f in (csv_updates\26年大客户汇总表-*.csv) do (
    echo 复制: %%~nxf
    copy /y "%%f" "static\%%~nxf" >nul
)

:: 清理旧文件
echo [4/4] 清理csv_updates目录...
for %%f in (csv_updates\*.csv) do (
    del /q "%%f" 2>nul
)

echo.
echo ========================================
echo CSV文件更新完成！
echo ========================================
echo.

set /p push="是否推送到GitHub并更新阿里云? (Y/N): "
if /i "%push%"=="Y" (
    echo.
    echo 正在提交到GitHub...
    git add static/ assets/
    git commit -m "更新CSV数据 %date% %time%"
    git push origin main
    echo.
    echo 提交完成！
    echo.
    echo 请在阿里云服务器上执行:
    echo   cd C:\Users\Administrator\Desktop\air_prd_agent
    echo   git pull origin main
    echo   python src\main.py -m http -p 8000
) else (
    echo 已跳过GitHub推送
)

echo.
echo 更新日志已保存到 csv_updates\update_log.txt
echo %date% %time% - 更新完成 >> csv_updates\update_log.txt

:end
echo.
pause
