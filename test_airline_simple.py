#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单测试航司名称"""

import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from utils.airline_names import AIRLINE_NAMES

# 加载CSV
df = pd.read_csv(project_root / "assets" / "products.csv", encoding='utf-8-sig')

print("CSV中的航司:")
airlines = df['航司代码'].unique()
for a in sorted(airlines):
    count = len(df[df['航司代码'] == a])
    name = AIRLINE_NAMES.get(a, '未知')
    print(f"  {a:5s} -> {name:15s} ({count:3d}条)")

print(f"\n总计: {len(airlines)}个航司")
