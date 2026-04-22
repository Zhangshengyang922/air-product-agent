# -*- coding: utf-8 -*-
import csv
import codecs

files = [
    'static/26年大客户汇总表-川航.csv',
    'static/26年大客户汇总表-国航.csv',
    'static/26年大客户汇总表-南航.csv'
]

for csv_file in files:
    print(f"\n{'='*60}")
    print(f"File: {csv_file}")
    print('='*60)
    
    with codecs.open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        # Print header row
        header = next(reader)
        print(f"Header ({len(header)} cols): {[h[:15] for h in header[:12]]}")
        
        # Print data rows with person
        count = 0
        for i, row in enumerate(reader):
            if len(row) > 10 and row[10].strip():
                print(f"  Row {i+2}: person at col[10]='{row[10][:15]}', customer='{row[1][:20] if len(row)>1 else 'N/A'}'")
                count += 1
                if count >= 3:
                    break
