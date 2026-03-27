#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""显示CSV字段"""

import csv

f = open('assets/products.csv', 'r', encoding='utf-8-sig')
r = csv.DictReader(f)

print('字段列表:')
for i, field in enumerate(r.fieldnames, 1):
    print(f'  {i}. {field}')

# 显示第一行数据
f.seek(0)
r = csv.DictReader(f)
first_row = next(r)
print(f'\n第一行数据:')
for key, value in first_row.items():
    print(f'  {key}: {value}')
