#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试航司名称识别"""

import sys
import os
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from agents.agent import AirlineAgent, create_airline_products
from utils.airline_names import AIRLINE_NAMES
import pandas as pd

# 加载CSV文件
csv_file = project_root / "assets" / "products.csv"
df = pd.read_csv(csv_file, encoding='utf-8-sig')

print("=" * 80)
print("测试航司名称识别")
print("=" * 80)

# 检查CSV字段
print("\nCSV字段：")
[print(f"  {i+1}. {field}") for i, field in enumerate(df.columns, 1)]

# 检查航司代码列
if '航司代码' in df.columns:
    airlines_in_csv = df['航司代码'].unique()
    print(f"\nCSV中的航司代码（共{len(airlines_in_csv)}个）：")
    for airline in sorted(airlines_in_csv):
        count = len(df[df['航司代码'] == airline])
        name = AIRLINE_NAMES.get(airline, airline)
        print(f"  {airline:5s} -> {name:15s} ({count:4d}条)")

# 创建产品对象
print("\n" + "=" * 80)
print("创建产品对象测试")
print("=" * 80)

products = create_airline_products(df)
print(f"\n创建的产品数量: {len(products)}")

# 统计航司
airlines_in_products = set(p.airline for p in products)
print(f"产品中的航司数量: {len(airlines_in_products)}")

print("\n产品中的航司分布：")
for airline in sorted(airlines_in_products):
    count = len([p for p in products if p.airline == airline])
    name = AIRLINE_NAMES.get(airline, airline)
    print(f"  {airline:5s} -> {name:15s} ({count:4d}条)")

# 显示前5个产品
print("\n前5个产品：")
for i, product in enumerate(products[:5], 1):
    print(f"  {i}. [{product.airline}] {AIRLINE_NAMES.get(product.airline, product.airline)} - {product.product_name[:40]}...")
