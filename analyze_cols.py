# -*- coding: utf-8 -*-
import codecs
import os

static_dir = 'static'

# 分析川航更多行
print("=== 川航更多数据行 ===")
with codecs.open(os.path.join(static_dir, '26年大客户汇总表-川航.csv'), 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

for i in range(2, min(8, len(lines))):
    if not lines[i].strip():
        continue
    data = lines[i].strip().split(',')
    print(f"\nRow {i}:")
    for j in [1, 8, 9, 10, 12, 13]:  # 客户、名单、战队、备注、服务商、责任人
        if j < len(data) and data[j].strip():
            print(f"  [{j}] = '{data[j][:40]}'")

# 分析南航更多行
print("\n\n=== 南航更多数据行 ===")
with codecs.open(os.path.join(static_dir, '26年大客户汇总表-南航.csv'), 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

for i in range(2, min(8, len(lines))):
    if not lines[i].strip():
        continue
    data = lines[i].strip().split(',')
    print(f"\nRow {i}:")
    for j in [1, 8, 9, 10, 11, 12]:  # 客户、名单、战队、备注、有效期、联系人
        if j < len(data) and data[j].strip():
            print(f"  [{j}] = '{data[j][:40]}'")
