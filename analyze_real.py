# -*- coding: utf-8 -*-
import codecs

csv_file = 'static/26年大客户汇总表-川航.csv'
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# 打印第2行(表头)和第3行(数据)
print("=== Header (Line 1) ===")
header = lines[1].strip().split(',')
for i, h in enumerate(header[:13]):
    print(f"  [{i}] = '{h}'")

print("\n=== Data (Line 2) ===")
data = lines[2].strip().split(',')
for i, d in enumerate(data[:13]):
    print(f"  [{i}] = '{d}'")

print("\n=== Data (Line 3) ===")
data3 = lines[3].strip().split(',')
for i, d in enumerate(data3[:13]):
    print(f"  [{i}] = '{d}'")

# 统计各列非空数据
print("\n=== Non-empty data count per column ===")
col_counts = {}
for line in lines[2:]:
    if not line.strip():
        continue
    cols = line.strip().split(',')
    for i in range(min(13, len(cols))):
        if cols[i].strip():
            col_counts[i] = col_counts.get(i, 0) + 1

for i in range(13):
    header_name = header[i] if i < len(header) else ''
    count = col_counts.get(i, 0)
    print(f"  [{i}] {header_name}: {count} non-empty values")
