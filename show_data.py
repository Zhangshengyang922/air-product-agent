# -*- coding: utf-8 -*-
import codecs

csv_file = 'static/26年大客户汇总表-川航.csv'
with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
print("=== CSV Structure ===")
print(f"Total lines: {len(lines)}")

# Header row (line 1)
header = lines[1].strip().split(',')
print(f"\nHeader (cols 0-12):")
for i in range(min(13, len(header))):
    print(f"  [{i}] = '{header[i]}'")

# Sample data rows
print("\n=== Sample Data Rows ===")
for line_num in [2, 3, 4, 5, 6, 7]:
    if line_num < len(lines):
        row = lines[line_num].strip().split(',')
        customer = row[1] if len(row) > 1 else ''
        list_type = row[8] if len(row) > 8 else ''
        team = row[9] if len(row) > 9 else ''
        person = row[10] if len(row) > 10 else ''
        print(f"Row {line_num}: list='{list_type}', team='{team}', person='{person}' | {customer[:25]}")
