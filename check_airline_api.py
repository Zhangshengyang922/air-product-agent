#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查航司API"""

import requests
import json

API_BASE = "http://localhost:8000"

try:
    print("正在获取航司列表...")
    response = requests.get(f"{API_BASE}/api/airlines", timeout=5)
    
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    data = response.json()
    print(f"\n返回数据结构:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    
    if 'success' in data and data['success']:
        airlines = data.get('data', {}).get('airlines', [])
        print(f"\n航司数量: {len(airlines)}")
        print("\n前10个航司:")
        for i, airline in enumerate(airlines[:10], 1):
            code = airline.get('code', '?')
            name = airline.get('name', '?')
            print(f"  {i}. {code}: {name}")
    else:
        print(f"\n错误: {data}")
        
except Exception as e:
    print(f"错误: {e}")
    print("请确保服务器正在运行: http://localhost:8000")
