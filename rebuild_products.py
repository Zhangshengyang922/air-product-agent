#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import csv
from pathlib import Path
import re

# 读取原始政策数据
all_policies = r"C:\Users\Administrator\OneDrive\桌面\release_20260317_100737\assets\policies_data\all_airlines_policies.csv"
df = pd.read_csv(all_policies, encoding='utf-8-sig')

print(f"原始数据总行数: {len(df)}")

# 扩展产品数据,将包含多个价格/舱位的行拆分为独立产品
all_products = []

for idx, row in df.iterrows():
    airline = str(row.get('航空公司', '')).strip()
    product_name = str(row.get('产品名称', '')).strip()
    route = str(row.get('航线', '')).strip()
    booking_class = str(row.get('订座舱位', '')).strip()
    price_increase = str(row.get('上浮价格', '')).strip()
    rebate_ratio = str(row.get('做单', '')).strip()
    fare_basis = str(row.get('运价标识', '')).strip()
    office = str(row.get('出票OFFICE', '')).strip()
    remarks = str(row.get('备注', '')).strip()
    valid_period = str(row.get('产品有限期', '')).strip()

    # 如果产品名称或价格为空,跳过
    if not product_name or product_name == 'nan':
        continue

    # 解析价格变体 (如 "220/250/300" 或 "70元:30,100元:40")
    prices = []
    rebates = []

    # 尝试匹配 "价格1/价格2/价格3" 格式
    if '/' in price_increase:
        price_parts = price_increase.split('/')
        for p in price_parts:
            p = p.strip()
            # 提取数字
            nums = re.findall(r'\d+\.?\d*', p)
            if nums:
                prices.append(nums[0])
    else:
        # 提取单个价格
        nums = re.findall(r'\d+\.?\d*', price_increase)
        if nums:
            prices = [nums[0]]

    # 尝试匹配返点变体 (如 "70/80" 或 "70元:30,100元:40")
    if '/' in rebate_ratio:
        rebate_parts = rebate_ratio.split('/')
        for r in rebate_parts:
            r = r.strip()
            nums = re.findall(r'\d+\.?\d*', r)
            if nums:
                rebates.append(nums[0])
    else:
        # 提取单个返点
        nums = re.findall(r'\d+\.?\d*', rebate_ratio)
        if nums:
            rebates = [nums[0]]

    # 如果有多个价格变体,为每个变体创建产品
    if len(prices) > 1:
        for i, price in enumerate(prices):
            rebate = rebates[i] if i < len(rebates) else (rebates[0] if rebates else '')
            product = {
                'airline': airline,
                'product_name': product_name,
                'route': route,
                'booking_class': booking_class,
                'price_increase': price,
                'rebate_ratio': rebate,
                'office': office,
                'remarks': remarks,
                'valid_period': valid_period,
                'ticket_type': 'ALL',
                'policy_identifier': fare_basis,
                'policy_code': fare_basis
            }
            all_products.append(product)
    else:
        # 单一产品
        price = prices[0] if prices else price_increase
        rebate = rebates[0] if rebates else rebate_ratio
        product = {
            'airline': airline,
            'product_name': product_name,
            'route': route,
            'booking_class': booking_class,
            'price_increase': price,
            'rebate_ratio': rebate,
            'office': office,
            'remarks': remarks,
            'valid_period': valid_period,
            'ticket_type': 'ALL',
            'policy_identifier': fare_basis,
            'policy_code': fare_basis
        }
        all_products.append(product)

print(f"扩展后产品总数: {len(all_products)}")

# 统计各航司产品数
from collections import Counter
airline_counts = Counter([p['airline'] for p in all_products])
print("\n各航司产品数量:")
for airline, count in sorted(airline_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {airline}: {count} 条")

# 保存到CSV
output_file = Path(__file__).parent / "assets" / "products.csv"
fieldnames = ['airline', 'product_name', 'route', 'booking_class',
              'price_increase', 'rebate_ratio', 'office', 'remarks',
              'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"\n已保存到: {output_file}")
