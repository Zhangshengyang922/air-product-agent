# -*- coding: utf-8 -*-
import re
import csv
import sys

csv_file = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("开始读取文件...")

# 读取文件
with open(csv_file, 'rb') as f:
    content = f.read()

# 尝试解码
text = content.decode('utf-8', errors='ignore')

print(f"文件长度: {len(text)} 字符")

# 使用csv.reader但处理多行情况
products = []
current_row = []

# 按行分割，但保持引号内的换行
lines = []
current_line = ''
in_quotes = False

for char in text:
    if char == '"':
        in_quotes = not in_quotes
    elif char == '\n' and not in_quotes:
        lines.append(current_line)
        current_line = ''
    else:
        current_line += char

if current_line:
    lines.append(current_line)

print(f"共 {len(lines)} 行")

# 解析每一行，处理引号
headers = ['airline', 'product_name', 'route', 'booking_class', 'price_increase', 'rebate_ratio', 'office', 'remarks', 'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

for line in lines:
    line = line.strip()
    if not line:
        continue

    # 简单的CSV解析（处理引号）
    fields = []
    current_field = ''
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(current_field)
            current_field = ''
        else:
            current_field += char
    fields.append(current_field)

    # 检查是否是新产品（airline列是2字母或数字代码）
    if len(fields) >= 2 and re.match(r'^[A-Z0-9]{2,3}$', fields[0]):
        # 保存上一个产品
        if current_row:
            products.append(current_row.copy())

        # 开始新产品
        current_row = fields[:12]  # 取前12列
        # 填充缺失的列
        while len(current_row) < 12:
            current_row.append('')
    else:
        # 这是remarks的延续
        if current_row and len(current_row) > 7:
            current_row[7] = current_row[7] + '\n' + line

# 保存最后一个产品
if current_row:
    products.append(current_row)

print(f"\n解析完成，共 {len(products)} 个产品")

# 写入新文件
output_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/new_products_parsed.csv'
with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    for product in products:
        writer.writerow(product)

print(f"已保存到: {output_file}")

# 统计各航司
airline_count = {}
for product in products:
    airline = product[0] if product else 'unknown'
    airline_count[airline] = airline_count.get(airline, 0) + 1

print("\n各航司产品数量:")
for airline, count in sorted(airline_count.items()):
    print(f"  {airline}: {count}")

print(f"\n总计: {len(products)} 个产品")
