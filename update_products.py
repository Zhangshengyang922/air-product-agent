#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
产品数据更新工具 - 支持从CSV文件导入产品数据
端口：8000
"""

import csv
import sys
import shutil
import os
from pathlib import Path
from datetime import datetime

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRODUCTS_CSV = ASSETS_DIR / "products.csv"
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"

def read_csv_file(file_path):
    """读取CSV文件，尝试多种编码"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                products = list(reader)
                headers = reader.fieldnames
                return products, headers, encoding
        except Exception as e:
            print(f'  ❌ 编码 {encoding} 失败: {e}')
            continue
    
    return None, None, None

def backup_current_products():
    """备份当前产品数据"""
    if not PRODUCTS_CSV.exists():
        print('⚠️  当前产品文件不存在，无需备份')
        return False
    
    # 创建备份目录
    backup_dir = ASSETS_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"products_backup_{timestamp}.csv"
    
    try:
        shutil.copy2(PRODUCTS_CSV, backup_file)
        print(f'✅ 已备份到: {backup_file.name}')
        return True
    except Exception as e:
        print(f'❌ 备份失败: {e}')
        return False

def update_products_from_export():
    """从导出的CSV文件更新产品数据"""
    print('='*70)
    print('🔄 产品数据更新工具')
    print('='*70)
    
    # 检查导出文件
    if not EXPORTED_CSV.exists():
        print(f'❌ 未找到导出文件: {EXPORTED_CSV}')
        print(f'\n请确保CSV文件已上传到项目根目录，命名为: {EXPORTED_CSV.name}')
        return False
    
    print(f'📁 导出文件: {EXPORTED_CSV}')
    print(f'📏 文件大小: {EXPORTED_CSV.stat().st_size:,} bytes')
    
    # 读取导出文件
    print('\n📖 读取导出文件...')
    new_products, new_headers, encoding = read_csv_file(EXPORTED_CSV)
    
    if not new_products:
        print('❌ 无法读取导出文件')
        return False
    
    print(f'✅ 使用编码 {encoding} 成功读取')
    print(f'📊 产品数量: {len(new_products)}')
    
    # 显示字段
    print(f'\n📋 字段列表:')
    for i, field in enumerate(new_headers, 1):
        print(f'  {i}. {field}')
    
    # 统计数据
    print(f'\n📈 数据统计:')
    airlines = {}
    routes = set()
    
    for product in new_products:
        name = product.get('产品名称', '')
        if name:
            airline = name[:2] if len(name) >= 2 else '未知'
            if airline not in airlines:
                airlines[airline] = 0
            airlines[airline] += 1
        
        route = product.get('航线', '')
        if route:
            routes.add(route[:30])
    
    print(f'  航空公司数: {len(airlines)}')
    print(f'  航线数: {len(routes)}')
    print(f'\n✈️  航司分布:')
    for airline, count in sorted(airlines.items()):
        print(f'    {airline}: {count} 个产品')
    
    # 备份现有数据
    print(f'\n💾 备份现有数据...')
    backup_current_products()
    
    # 复制新文件
    print(f'\n📝 更新产品数据...')
    try:
        shutil.copy2(EXPORTED_CSV, PRODUCTS_CSV)
        print(f'✅ 产品数据已更新')
        print(f'📁 目标文件: {PRODUCTS_CSV}')
    except Exception as e:
        print(f'❌ 更新失败: {e}')
        return False
    
    # 验证更新结果
    print(f'\n🔍 验证更新结果...')
    verified_products, _, _ = read_csv_file(PRODUCTS_CSV)
    
    if verified_products and len(verified_products) == len(new_products):
        print(f'✅ 验证成功！产品数量一致: {len(verified_products)}')
    else:
        print(f'⚠️  验证警告：产品数量不一致')
    
    print(f'\n{"="*70}')
    print('✅ 产品数据更新完成！')
    print(f'{"="*70}')
    
    print(f'\n📌 下一步操作:')
    print(f'  1. 重启Web服务以加载新数据')
    print(f'     python src/main.py -m http -p 8000')
    print(f'  2. 访问Web界面查看产品数据')
    print(f'     http://localhost:8000')
    print(f'  3. 登录: YNTB / yntb123')
    
    return True

def main():
    """主函数"""
    try:
        success = update_products_from_export()
        return 0 if success else 1
    except Exception as e:
        print(f'❌ 发生错误: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
