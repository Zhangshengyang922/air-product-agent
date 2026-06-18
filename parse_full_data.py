#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xlwings as xw
import csv
from pathlib import Path

excel_file = r"C:\Users\Administrator\OneDrive\桌面\CTU152各航司产品政策表.xlsx"
output_file = Path(__file__).parent / "assets" / "products.csv"

app = xw.App(visible=False)
wb = app.books.open(excel_file)

all_products = []
airline_mapping = {
    '国航': 'CA',
    '南航': 'CZ',
    '川航': '3U',
    '东航': 'MU',
    '祥鹏': '8L',
    '深航': 'ZH',
    '成都': 'EU',
    '海航': 'HU',
    '首航': 'JD',
    '福州': 'FU',
    '长龙': 'GJ',
    '藏航': 'TV'
}

print("="*80)
print("开始解析所有产品数据")
print("="*80)

for i, sheet in enumerate(wb.sheets):
    sheet_name = sheet.name
    print(f"\n处理工作表: {sheet_name}")

    data = sheet.used_range.value
    if len(data) <= 1:
        continue

    # 获取航司代码
    airline = airline_mapping.get(sheet_name, sheet_name[:2].upper())

    # 解析数据
    current_airline = None
    current_product_name = None
    current_route = None

    for row_idx in range(1, len(data)):
        row = data[row_idx]

        if not row or len(row) < 2:
            continue

        # 检查是否有新的航司代码或产品名称
        if row[0] and str(row[0]).strip() and len(str(row[0])) == 2:
            current_airline = str(row[0]).strip().upper()

        if row[1] and str(row[1]).strip():
            current_product_name = str(row[1]).strip()

        if row[2] and str(row[2]).strip():
            current_route = str(row[2]).strip()

        # 确保有航司和产品名称
        if not current_airline:
            current_airline = airline

        if not current_product_name:
            continue

        # 构建产品记录
        booking_class = str(row[3]).strip() if len(row) > 3 and row[3] else ''
        price_increase = str(row[4]).strip() if len(row) > 4 and row[4] else ''
        rebate_ratio = str(row[5]).strip() if len(row) > 5 and row[5] else ''
        office = str(row[6]).strip() if len(row) > 6 and row[6] else ''
        remarks = str(row[7]).strip() if len(row) > 7 and row[7] else ''
        valid_period = str(row[8]).strip() if len(row) > 8 and row[8] else ''

        # 只添加有效产品
        if booking_class or price_increase or rebate_ratio:
            product = {
                'airline': current_airline,
                'product_name': current_product_name,
                'route': current_route,
                'booking_class': booking_class,
                'price_increase': price_increase,
                'rebate_ratio': rebate_ratio,
                'office': office,
                'remarks': remarks,
                'valid_period': valid_period,
                'ticket_type': 'ALL',
                'policy_identifier': '',
                'policy_code': ''
            }
            all_products.append(product)

    print(f"  提取产品数: {len([p for p in all_products if p['airline'] == current_airline])}")

wb.close()
app.quit()

print(f"\n{'='*80}")
print(f"总共提取产品: {len(all_products)} 条")
print(f"{'='*80}")

# 统计各航司产品数
from collections import Counter
airline_counts = Counter([p['airline'] for p in all_products])
print("\n各航司产品数量:")
for airline, count in sorted(airline_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {airline}: {count} 条")

# 保存到CSV
fieldnames = ['airline', 'product_name', 'route', 'booking_class',
              'price_increase', 'rebate_ratio', 'office', 'remarks',
              'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"\n已保存到: {output_file}")
