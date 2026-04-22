# -*- coding: utf-8 -*-
import codecs
import os

static_dir = 'static'

csv_files = [
    '26年大客户汇总表-川航.csv',
    '26年大客户汇总表-国航.csv',
    '26年大客户汇总表-南航.csv'
]

for csv_file in csv_files:
    filepath = os.path.join(static_dir, csv_file)
    print(f"\n{'='*60}")
    print(f"File: {csv_file}")
    print('='*60)
    
    with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    if len(lines) < 3:
        print("Not enough lines")
        continue
    
    # Print first 8 lines
    for i in range(min(8, len(lines))):
        row = lines[i].strip().split(',')
        print(f"\nLine {i}: {len(row)} cols")
        for j in range(min(15, len(row))):
            val = row[j] if j < len(row) else ''
            if val:
                print(f"  [{j}] = '{val}'")
