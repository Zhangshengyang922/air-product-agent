#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为所有产品添加航司字段"""

import csv
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

PROJECT_ROOT = Path(__file__).parent
PRODUCTS_CSV = PROJECT_ROOT / "assets" / "products.csv"
BACKUP_DIR = PROJECT_ROOT / "assets" / "backups"

# 创建备份目录
BACKUP_DIR.mkdir(exist_ok=True)

# 备份现有文件
backup_file = BACKUP_DIR / f"products_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
shutil.copy(PRODUCTS_CSV, backup_file)
print(f'✅ 已备份到: {backup_file}')

# 读取现有产品
print('📖 读取产品数据...')
with open(PRODUCTS_CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    products = list(reader)

print(f'✅ 读取到 {len(products)} 条产品')

# 为每个产品添加航司字段
print('🔍 分析产品名称提取航司...')

def extract_airline(product_name):
    """从产品名称中提取航司代码"""
    if not product_name:
        return '未知'
    
    # 产品名称格式示例: "MU、GP免费快速安检通道" 或 "CZ南航产品"
    # 提取前2个字符的航司代码
    airline_code = product_name[:2].strip()
    
    # 映射表
    airline_map = {
        'MU': '东航',
        'CZ': '南航',
        'HU': '海南航空',
        'CA': '国航',
        '3U': '四川航空',
        '8L': '祥鹏航空',
        'KY': '昆明航空',
        'ZH': '深圳航空',
        'EU': '成都航空',
        '9H': '长安航空',
        'HO': '吉祥航空',
        'BK': '奥凯航空',
        'GS': '天津航空',
        'G5': '华夏航空',
        'MF': '厦门航空',
        'SC': '山东航空',
        'TV': '西藏航空',
        'GJ': '长龙航空',
        'DR': '桂林航空',
        'QW': '青岛航空',
        'NS': '河北航空',
        'RY': '江西航空',
        'GY': '多彩贵州',
        'DZ': '东海航空',
        'LT': '龙江航空',
        'OQ': '重庆航空',
        'JD': '首都航空',
        'PN': '西部航空',
        'FU': '福州航空',
        'GX': '北部湾航空',
        'UQ': '乌鲁木齐航空',
        'A6': '红土航空',
        'JR': '幸福航空',
        'GP': 'GP',
        '低碳': '低碳'
    }
    
    airline_name = airline_map.get(airline_code, airline_code)
    
    # 如果产品名称中有"航司"相关描述，也提取
    if '东航' in product_name:
        airline_name = '东航'
        airline_code = 'MU'
    elif '南航' in product_name:
        airline_name = '南航'
        airline_code = 'CZ'
    elif '国航' in product_name:
        airline_name = '国航'
        airline_code = 'CA'
    elif '海南航空' in product_name or '海航' in product_name:
        airline_name = '海南航空'
        airline_code = 'HU'
    
    return airline_name

# 统计航司
airlines = {}
for product in products:
    product_name = product.get('产品名称', '')
    airline = extract_airline(product_name)
    product['航司'] = airline
    
    if airline not in airlines:
        airlines[airline] = 0
    airlines[airline] += 1

print(f'✅ 完成！共识别 {len(airlines)} 个航司')

# 显示航司统计
print('\n📊 航司分布：')
sorted_airlines = sorted(airlines.items(), key=lambda x: x[1], reverse=True)
for i, (airline, count) in enumerate(sorted_airlines, 1):
    print(f'  {i:2d}. {airline:10s}: {count:4d} 条')

# 写回文件
print(f'\n💾 保存到 {PRODUCTS_CSV}...')
with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig', newline='') as f:
    fieldnames = ['航司', '产品名称', '航线', '订座舱位', '上浮价格', '政策返点', '产品代码', '出票OFFICE', '备注', '产品有限期']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(products)

print('✅ 完成！产品数据已更新')
