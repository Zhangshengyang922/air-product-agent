# -*- coding: utf-8 -*-
import csv
import codecs

csv_file = 'static/26年大客户汇总表-川航.csv'
print("=== Checking CSV Structure ===")
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i > 5:
            break
        cols9 = row[9] if len(row) > 9 else ''
        print(f"Row {i}: cols[9]='{cols9}' | customer='{row[1][:20] if len(row)>1 else ''}'")

print("\n=== Rows with person data ===")
count = 0
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i < 2:
            continue
        if len(row) > 9 and row[9].strip():
            print(f"Row {i}: person='{row[9]}', customer='{row[1][:25] if len(row)>1 else ''}'")
            count += 1
            if count >= 10:
                print("... (more)")
                break
