#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证产品数据脚本"""

import csv
import sys
from pathlib import Path

def verify_csv_file(file_path):
    """验证CSV文件"""
    print('='*60)
    print('📊 产品数据验证')
    print('='*60)
    print(f'📁 文件路径: {file_path}')
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print('❌ 文件不存在')
        return False
    
    # 尝试读取文件
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
    products = []
    headers = []
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                products = list(reader)
            print(f'✅ 使用编码 {encoding} 成功读取文件')
            break
        except Exception as e:
            print(f'❌ 编码 {encoding} 失败: {e}')
            continue
    
    if not products:
        print('❌ 无法读取产品数据')
        return False
    
    print(f'\n📊 数据统计:')
    print(f'  总记录数: {len(products)}')
    print(f'  字段数量: {len(headers)}')
    
    print(f'\n📋 字段列表:')
    for i, header in enumerate(headers, 1):
        print(f'  {i}. {header}')
    
    # 统计航司数据
    airlines = {}
    routes = set()
    
    for product in products:
        name = product.get('产品名称', '')
        if name:
            # 提取航司代码
            airline_code = name[:2] if len(name) >= 2 else '未知'
            if airline_code not in airlines:
                airlines[airline_code] = 0
            airlines[airline_code] += 1
        
        route = product.get('航线', '')
        if route:
            routes.add(route[:30])  # 只取前30字符
    
    print(f'\n✈️  航司分布:')
    for airline, count in sorted(airlines.items()):
        print(f'  {airline}: {count} 个产品')
    
    print(f'\n🛣️  航线数量: {len(routes)}')
    
    # 检查必填字段
    required_fields = ['产品名称', '航线', '上浮价格', '政策返点']
    print(f'\n✅ 数据质量检查:')
    
    all_valid = True
    for field in required_fields:
        empty_count = sum(1 for p in products if not p.get(field, '').strip())
        if empty_count > 0:
            print(f'  ⚠️  {field}: {empty_count} 个空值')
            all_valid = False
        else:
            print(f'  ✅ {field}: 全部有值')
    
    print(f'\n{"="*60}')
    if all_valid:
        print('✅ 数据验证通过')
    else:
        print('⚠️  数据存在一些问题，请检查')
    print(f'{"="*60}')
    
    return all_valid

def main():
    """主函数"""
    project_dir = Path(__file__).parent
    
    # 验证现有产品文件
    print('\n1️⃣ 验证现有产品文件:')
    verify_csv_file(project_dir / 'assets' / 'products.csv')
    
    # 验证新的导出文件（如果存在）
    exported_file = project_dir / 'exported_from_wechat.csv'
    if exported_file.exists():
        print('\n2️⃣ 验证新导出的产品文件:')
        verify_csv_file(exported_file)
    else:
        print('\n2️⃣ 未找到新导出的文件: exported_from_wechat.csv')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ 验证过程中出错: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
