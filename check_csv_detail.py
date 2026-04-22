# -*- coding: utf-8 -*-
import csv
import codecs

csv_file = 'static/26年大客户汇总表-川航.csv'
print("=== Detailed Row 3 Analysis ===")
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i == 3:  # 第4行(0-indexed=3)
            print(f"Total columns: {len(row)}")
            for j in range(min(15, len(row))):
                val = row[j] if j < len(row) else '(N/A)'
                print(f"  cols[{j}]: '{val}'")
            break
