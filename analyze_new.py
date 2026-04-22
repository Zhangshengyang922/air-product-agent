# -*- coding: utf-8 -*-
import codecs
import os

static_dir = 'static'

files = [
    '26年大客户汇总表-川航.csv',
    '26年大客户汇总表-国航.csv',
    '26年大客户汇总表-南航.csv'
]

for csv_file in files:
    filepath = os.path.join(static_dir, csv_file)
    print(f"\n{'='*60}")
    print(f"File: {csv_file}")
    print('='*60)
    
    with codecs.open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    if len(lines) < 3:
        print("Not enough lines")
        continue
    
    # Header
    header = lines[1].strip().split(',')
    print(f"\nHeader (first 15 cols):")
    for i in range(min(15, len(header))):
        if header[i]:
            print(f"  [{i}] = '{header[i]}'")
    
    # First data row
    print(f"\nFirst data row:")
    data = lines[2].strip().split(',')
    for i in range(min(15, len(data))):
        if data[i].strip():
            print(f"  [{i}] = '{data[i][:50]}'")
