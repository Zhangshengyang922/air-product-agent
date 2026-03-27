#!/usr/bin/env python3
"""检查更新后的产品数据"""

import pandas as pd

# 读取更新后的CSV
df = pd.read_csv('products_updated_20260325_134440.csv')

print("=" * 80)
print("更新后的产品数据统计")
print("=" * 80)

total_products = len(df)
null_airline = df['airline'].isna() | (df['airline'] == '')
non_null_airline = df['airline'].notna() & (df['airline'] != '')

print(f"\n总产品数: {total_products}")
print(f"航司为空: {null_airline.sum()} 个")
print(f"航司有值: {non_null_airline.sum()} 个")

# 按航司分组统计
if non_null_airline.sum() > 0:
    print("\n" + "=" * 80)
    print("航司分布:")
    print("=" * 80)

    airline_counts = df[non_null_airline]['airline'].value_counts().sort_index()
    for code, count in airline_counts.items():
        print(f"{code}: {count} 个产品")

# 显示一些更新示例
print("\n" + "=" * 80)
print("更新示例(最近更新的10个产品):")
print("=" * 80)

# 找出有航司的产品示例
sample_products = df[non_null_airline].head(10)
for idx, row in sample_products.iterrows():
    print(f"\n航司: {row['airline']}")
    print(f"产品名称: {row['product_name']}")
    print(f"路线: {str(row['route'])[:60]}...")
