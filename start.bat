@echo off
chcp 65001 >nul
echo ====================================
echo 航空产品管理系统
echo 端口: 8000
echo ====================================
echo.

echo [1] 更新产品数据
echo [2] 启动Web服务 (端口8000)
echo [3] 查看产品统计
echo [4] 退出
echo.

set /p choice="请选择操作 (1-4): "

if "%choice%"=="1" goto update
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stats
if "%choice%"=="4" goto end

echo 无效选择！
pause
goto end

:update
echo.
echo 正在更新产品数据...
echo.
python update_products.py
echo.
pause
goto menu

:start
echo.
echo 正在启动Web服务...
echo.
echo 访问地址: http://localhost:8000
echo 登录账号: YNTB / yntb123
echo.
python src/main.py -m http -p 8000
goto end

:stats
echo.
echo 产品数据统计...
echo.
python -c "import csv; f=open('assets/products.csv','r',encoding='utf-8-sig'); r=csv.DictReader(f); airlines=set(); [airlines.add(row['产品名称'][:2]) for row in r if row.get('产品名称')]; print(f'航司: {sorted(airlines)}'); print(f'总产品数: {len(list(csv.DictReader(open(\"assets/products.csv\",\"r\",encoding=\"utf-8-sig\"))))}')"
echo.
pause
goto menu

:menu
goto end

:end
echo.
echo 谢谢使用！
pause
