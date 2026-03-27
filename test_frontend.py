#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试前端修改是否生效"""

import sys
import requests
import re

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

API_BASE = "http://localhost:8000"

def check_html_file():
    print("=" * 50)
    print("检查本地HTML文件")
    print("=" * 50)
    
    with open('static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查AIRLINE_NAMES
    airlines = re.findall(r"'([A-Z0-9]+)':\s*'([^']+)'", content)
    print(f"\n[OK] 本地文件中的航司映射数量: {len(airlines)}")
    
    # 检查备注列
    has_remarks = '备注' in content
    print(f"[OK] 备注列存在: {has_remarks}")
    
    # 检查展开行
    has_expand = 'type="expand"' in content
    print(f"[OK] 展开行已移除: {not has_expand}")
    
    # 检查关键航司
    key_airlines = {'A6', 'GS', 'DR'}
    found = {code for code, name in airlines if code in key_airlines}
    print(f"\n关键航司检查:")
    for code, name in airlines:
        if code in key_airlines:
            print(f"  {code}: {name}")
    
    return {
        'airlines_count': len(airlines),
        'has_remarks': has_remarks,
        'no_expand': not has_expand,
        'key_airlines': found == key_airlines
    }

def check_server():
    print("\n" + "=" * 50)
    print("检查服务器返回的HTML")
    print("=" * 50)
    
    try:
        response = requests.get(API_BASE)
        content = response.text
        
        # 检查AIRLINE_NAMES
        airlines = re.findall(r"'([A-Z0-9]+)':\s*'([^']+)'", content)
        print(f"\n[OK] 服务器返回的航司映射数量: {len(airlines)}")
        
        # 检查备注列
        has_remarks = '备注' in content
        print(f"[OK] 备注列存在: {has_remarks}")
        
        # 检查展开行
        has_expand = 'type="expand"' in content
        print(f"[OK] 展开行已移除: {not has_expand}")
        
        return {
            'airlines_count': len(airlines),
            'has_remarks': has_remarks,
            'no_expand': not has_expand
        }
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return None

if __name__ == '__main__':
    # 检查本地文件
    local_result = check_html_file()
    
    # 检查服务器
    server_result = check_server()
    
    print("\n" + "=" * 50)
    print("总结")
    print("=" * 50)
    
    if server_result:
        if (local_result['airlines_count'] == server_result['airlines_count'] and
            local_result['has_remarks'] == server_result['has_remarks'] and
            local_result['no_expand'] == server_result['no_expand']):
            print("\n[OK] 本地文件和服务器文件一致")
            print("\n[TIP] 建议: 在浏览器中按 Ctrl+Shift+R 强制刷新页面")
        else:
            print("\n[WARN] 本地文件和服务器文件不一致")
            print("可能需要重启服务器")
    else:
        print("\n[WARN] 无法验证服务器状态")
