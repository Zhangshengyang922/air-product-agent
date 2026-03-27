@echo off
chcp 65001 >nul
echo ========================================
echo 产品管理系统 - 更新产品数据
echo ========================================
echo.

cd /d "%~dp0"

echo 操作说明:
echo.
echo 1. 将Excel文件放到本目录
echo    文件名: exported_from_wechat.xlsx
echo.
echo 2. 按任意键开始导入...
echo.

pause >nul

echo.
echo 正在导入产品数据...
echo.

python final_import.py

echo.
echo ========================================
echo 导入完成！
echo ========================================
echo.
echo 下一步:
echo 1. 刷新Web页面查看数据
echo    http://localhost:8000
echo 2. 如果未自动更新，请重启服务
echo.
pause
