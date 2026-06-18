@echo off
chcp 65001 > nul
echo =========================================
echo   同步项目文件到 air_prd_agent
echo =========================================
echo.

set "src=c:\Users\Administrator\OneDrive\桌面\release_20260317_100737"
set "dst=c:\Users\Administrator\OneDrive\桌面\air_prd_agent"

echo 正在复制文件，请稍候...

xcopy "%src%\src\agents" "%dst%\src\agents\" /E /Y /I > nul 2>&1
xcopy "%src%\src\graphs" "%dst%\src\graphs\" /E /Y /I > nul 2>&1
xcopy "%src%\src\utils" "%dst%\src\utils\" /E /Y /I > nul 2>&1
xcopy "%src%\src\storage" "%dst%\src\storage\" /E /Y /I > nul 2>&1
xcopy "%src%\src\tools" "%dst%\src\tools\" /E /Y /I > nul 2>&1
xcopy "%src%\static" "%dst%\static\" /E /Y /I > nul 2>&1
xcopy "%src%\config" "%dst%\config\" /E /Y /I > nul 2>&1
xcopy "%src%\assets\products.csv" "%dst%\assets\" /Y > nul 2>&1
xcopy "%src%\assets\airline_products_stats.json" "%dst%\assets\" /Y > nul 2>&1
xcopy "%src%\assets\field_mapping.json" "%dst%\assets\" /Y > nul 2>&1
xcopy "%src%\assets\docs" "%dst%\assets\" /E /Y /I > nul 2>&1

echo.
echo [OK] 文件同步完成！
echo.
pause
