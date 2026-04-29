@echo off
chcp 65001 >nul
echo ========================================
echo CSV数据文件快速更新工具 v3.1
echo ========================================
echo.

cd /d "%~dp0"

:: 创建CSV更新目录（如果不存在）
if not exist "csv_updates" mkdir csv_updates

echo 说明：
echo 1. 请将要更新的CSV文件放入 "csv_updates" 文件夹
echo 2. 支持的文件：
echo    - 各航司汇总产品-*.csv （产品数据）
echo    - 26年大客户汇总表-*.csv （大客户数据）
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

:: 复制产品CSV到static和assets目录
echo [1/5] 更新产品数据文件...
for %%f in (csv_updates\各航司汇总产品-*.csv) do (
    echo 复制到static: %%~nxf
    copy /y "%%f" "static\%%~nxf" >nul
    echo 复制到assets: %%~nxf
    copy /y "%%f" "assets\%%~nxf" >nul
)

:: 复制大客户CSV到static目录
echo [2/5] 更新大客户数据文件...
for %%f in (csv_updates\26年大客户汇总表-*.csv) do (
    echo 复制到static: %%~nxf
    copy /y "%%f" "static\%%~nxf" >nul
)

:: 复制其他CSV文件到static目录
echo [3/5] 更新其他数据文件到static...
for %%f in (csv_updates\*.csv) do (
    set "found=0"
    for %%g in (csv_updates\各航司汇总产品-*.csv csv_updates\26年大客户汇总表-*.csv) do (
        if /i "%%f"=="%%g" set "found=1"
    )
    if "!found!"=="0" (
        echo 复制: %%~nxf
        copy /y "csv_updates\%%~nxf" "static\%%~nxf" >nul
    )
)

:: 合并生成products.csv（自动更新主数据文件）
echo [4/5] 合并生成products.csv...
python -c "import os; import pandas as pd; from pathlib import Path; base_dir = Path(r'%~dp0'); assets_dir = base_dir / 'assets'; products_file = assets_dir / 'products.csv'; csv_files = list(assets_dir.glob('各航司汇总产品-*.csv')); dfs = []; [dfs.append(pd.read_csv(f, encoding='utf-8-sig')) or print(f'已读取: {f.name}') for f in csv_files if f.exists()]; merged = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(); merged.to_csv(products_file, index=False, encoding='utf-8-sig'); print(f'合并完成: {len(merged)} 行'); merged.to_csv(base_dir / 'static' / 'products.csv', index=False, encoding='utf-8-sig')"

:: 清理旧文件（可选）
echo [5/5] 清理csv_updates目录...
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
