# -*- coding: utf-8 -*-
import codecs

# 川航CSV详细分析 - 打印完整行
csv_file = 'static/26年大客户汇总表-川航.csv'
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

print("=== CSV完整结构分析 ===\n")

# 前3行
for i in range(3):
    if i >= len(lines):
        break
    print(f"--- Line {i} ---")
    cols = lines[i].strip().split(',')
    for j, col in enumerate(cols[:15]):
        print(f"  [{j}] = '{col}'")
    print()

print("\n=== 数据行样例(Line 2-4) ===")
for i in range(2, min(5, len(lines))):
    print(f"\nLine {i}:")
    cols = lines[i].strip().split(',')
    for j, col in enumerate(cols[:15]):
        if col.strip():  # 只打印非空列
            print(f"  [{j}] = '{col}'")
