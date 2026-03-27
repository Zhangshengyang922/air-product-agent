#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查前端修改"""

import sys
import re

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

html_file = "static/index.html"

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("检查前端修改")
print("=" * 80)

# 检查航司名称映射
print("\n1. 检查AIRLINE_NAMES映射:")
airline_match = re.search(r"AIRLINE_NAMES\s*=\s*\{([^}]+)\}", content)
if airline_match:
    airline_content = airline_match.group(1)
    airlines = re.findall(r"'([^']+)':\s*'([^']+)'", airline_content)
    print(f"   找到 {len(airlines)} 个航司映射")

    # 检查关键航司
    key_airlines = ['A6', 'G5', 'GS', 'JR', 'DR']
    for code in key_airlines:
        found = False
        for k, v in airlines:
            if k == code:
                print(f"   ✓ {code}: {v}")
                found = True
                break
        if not found:
            print(f"   ✗ {code}: 未找到")
else:
    print("   未找到AIRLINE_NAMES映射")

# 检查表格列
print("\n2. 检查表格列:")
columns = re.findall(r'<el-table-column[^>]*label="([^"]+)"', content)
print(f"   找到 {len(columns)} 个列:")
for i, col in enumerate(columns, 1):
    print(f"   {i}. {col}")

# 检查备注列位置
print("\n3. 检查备注列位置:")
valid_index = columns.index('有效期') if '有效期' in columns else -1
remarks_index = columns.index('备注') if '备注' in columns else -1

if remarks_index != -1 and valid_index != -1:
    if remarks_index < valid_index:
        print(f"   ✓ 备注列在有效期之前 (备注: {remarks_index+1}, 有效期: {valid_index+1})")
    else:
        print(f"   ✗ 备注列不在有效期之前 (备注: {remarks_index+1}, 有效期: {valid_index+1})")
else:
    print(f"   ✗ 未找到备注或有效期列")

# 检查展开功能
print("\n4. 检查展开功能:")
if 'type="expand"' in content:
    print("   ✗ 存在展开功能")
else:
    print("   ✓ 已移除展开功能")

# 检查展开样式
print("\n5. 检查展开样式:")
if 'product-expand' in content or 'expand-row' in content:
    print("   ✗ 存在展开样式")
else:
    print("   ✓ 已移除展开样式")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
