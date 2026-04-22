# -*- coding: utf-8 -*-
import codecs
import os

# 川航CSV详细分析
csv_file = 'static/26年大客户汇总表-川航.csv'
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    content = f.read()

lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# 检查所有非空行的cols[9]和cols[10]
print("\n=== All data rows with cols[9] and cols[10] ===")
count_team = 0
count_person = 0
for i, line in enumerate(lines):
    if i < 2:  # 跳过前两行
        continue
    if not line.strip():
        continue
    cols = line.split(',')
    if len(cols) > 10:
        customer = cols[1].strip() if len(cols) > 1 else ''
        col9 = cols[9].strip() if len(cols) > 9 else ''
        col10 = cols[10].strip() if len(cols) > 10 else ''
        col11 = cols[11].strip() if len(cols) > 11 else ''
        
        if col9 or col10:
            print(f"Row {i}: col9='{col9}', col10='{col10}', col11='{col11}' | {customer[:20]}")
            if col9:
                count_team += 1
            if col10:
                count_person += 1

print(f"\n统计: 有战队(col9)数据: {count_team}条, 有责任人(col10)数据: {count_person}条")

# 检查是否有换行符导致的列错位
print("\n=== 检查原始行数据 ===")
for i in range(2, min(6, len(lines))):
    print(f"\nLine {i}:")
    print(repr(lines[i][:200]))
