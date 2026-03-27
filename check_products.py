#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查产品数据"""

import csv

f = open('assets/products.csv', 'r', encoding='utf-8-sig')
r = csv.DictReader(f)
products = list(r)

print(f'总产品数: {len(products)}')

airlines = set()
for row in products:
    name = row.get('产品名称', '')
    if name:
        airlines.add(name[:2])

print(f'航司数: {len(airlines)}')
print(f'航司列表: {sorted(airlines)}')

print(f'\n前5条产品:')
for i, p in enumerate(products[:5], 1):
    name = p.get('产品名称', '未知')
    route = p.get('航线', '未知')[:30]
    print(f'  {i}. {name} - {route}')
