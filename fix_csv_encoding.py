#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CSV文件编码修复工具"""

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

PROJECT_ROOT = Path(__file__).parent
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"
PRODUCTS_CSV = PROJECT_ROOT / "assets" / "products.csv"

def detect_encoding(file_path):
    """检测文件编码"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'big5', 'latin1', 'cp1252']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # 尝试读取前100行
                for _ in range(100):
                    f.readline()
                return encoding
        except:
            continue

    return None

def read_with_fallback(file_path):
    """尝试多种方式读取文件"""
    encodings = [
        'utf-8-sig', 'utf-8', 'gbk', 'gb2312',
        'big5', 'latin1', 'cp1252', 'iso-8859-1'
    ]

    # 首先尝试直接读取
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                reader = csv.DictReader(f)
                products = list(reader)
                headers = reader.fieldnames
                if products:
                    print(f'✅ 使用编码 {encoding} 成功读取')
                    print(f'📊 产品数量: {len(products)}')
                    return products, headers, encoding
        except Exception as e:
            print(f'  ❌ 编码 {encoding} 失败')
            continue

    # 尝试忽略错误读取
    print('\n尝试使用容错模式读取...')
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                reader = csv.DictReader(f)
                products = list(reader)
                headers = reader.fieldnames
                if products:
                    print(f'✅ 使用编码 {encoding} (容错模式) 成功读取')
                    print(f'📊 产品数量: {len(products)}')
                    return products, headers, encoding
        except Exception as e:
            continue

    # 尝试二进制模式读取
    print('\n尝试使用二进制模式读取...')
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # 尝试解码
        for encoding in encodings:
            try:
                text = content.decode(encoding, errors='ignore')
                lines = text.splitlines()
                if len(lines) > 1:
                    reader = csv.DictReader(lines)
                    products = list(reader)
                    headers = reader.fieldnames
                    if products:
                        print(f'✅ 使用编码 {encoding} (二进制模式) 成功读取')
                        print(f'📊 产品数量: {len(products)}')
                        return products, headers, encoding
            except:
                continue
    except Exception as e:
        print(f'❌ 二进制模式失败: {e}')

    return None, None, None

def clean_row(row, fieldnames):
    """清理行数据中的无效字符"""
    cleaned = {}
    for key, value in row.items():
        # 只保留有效字段
        if key is None or key not in fieldnames:
            continue

        if isinstance(value, str):
            # 移除控制字符
            cleaned[key] = ''.join(c for c in value if ord(c) >= 32 or c in '\n\r\t')
        else:
            cleaned[key] = value

    # 确保所有字段都存在
    for field in fieldnames:
        if field not in cleaned:
            cleaned[field] = ''

    return cleaned

def main():
    print('='*70)
    print('🔧 CSV编码修复工具')
    print('='*70)

    if not EXPORTED_CSV.exists():
        print(f'❌ 文件不存在: {EXPORTED_CSV}')
        return 1

    print(f'📁 文件路径: {EXPORTED_CSV}')
    print(f'📏 文件大小: {EXPORTED_CSV.stat().st_size:,} bytes')

    # 检测编码
    print('\n🔍 检测文件编码...')
    encoding = detect_encoding(EXPORTED_CSV)
    if encoding:
        print(f'✅ 检测到编码: {encoding}')
    else:
        print('⚠️  无法自动检测编码')

    # 读取文件
    print('\n📖 尝试读取文件...')
    products, headers, used_encoding = read_with_fallback(EXPORTED_CSV)

    if not products:
        print('❌ 无法读取文件，请检查文件格式')
        return 1

    # 清理数据
    print('\n🧹 清理数据...')
    products = [clean_row(row, headers) for row in products]
    print(f'✅ 清理完成，有效产品数: {len(products)}')

    # 统计信息
    print(f'\n📈 数据统计:')
    airlines = {}
    for product in products:
        name = product.get('产品名称', '')
        if name:
            airline = name[:2] if len(name) >= 2 else '未知'
            if airline not in airlines:
                airlines[airline] = 0
            airlines[airline] += 1

    print(f'  航空公司数: {len(airlines)}')
    print(f'\n✈️  航司分布:')
    for airline, count in sorted(airlines.items()):
        print(f'    {airline}: {count} 个产品')

    # 备份现有文件
    print(f'\n💾 备份现有文件...')
    backup_dir = PROJECT_ROOT / "assets" / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if PRODUCTS_CSV.exists():
        backup_file = backup_dir / f"products_backup_{timestamp}.csv"
        shutil.copy2(PRODUCTS_CSV, backup_file)
        print(f'✅ 已备份到: {backup_file.name}')

    # 保存为新文件
    print(f'\n💾 保存修复后的文件...')
    with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(products)

    print(f'✅ 文件已保存: {PRODUCTS_CSV}')
    print(f'✅ 编码: UTF-8 with BOM')

    print(f'\n{"="*70}')
    print('✅ 修复完成！')
    print(f'{"="*70}')

    return 0

if __name__ == '__main__':
    sys.exit(main())
