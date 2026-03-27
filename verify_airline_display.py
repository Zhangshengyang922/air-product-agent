#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证前端航司显示"""

import requests
import re

API_BASE = "http://localhost:8000"

print("=" * 60)
print("前端航司显示验证")
print("=" * 60)

try:
    response = requests.get(API_BASE, timeout=5)
    content = response.text
    
    # 检查AIRLINE_NAMES
    print("\n1. 检查 AIRLINE_NAMES 映射:")
    print("-" * 60)
    
    if "AIRLINE_NAMES" not in content:
        print("[ERROR] 未找到 AIRLINE_NAMES!")
    else:
        # 提取所有航司映射
        matches = re.findall(r"'([A-Z0-9]+)':\s*'([^']+)'", content)
        print(f"[OK] 找到 {len(matches)} 个航司映射\n")
        
        # 检查关键航司
        key_airlines = {'A6': '红土航空', 'GS': '天津航空', 'DR': '桂林航空', 'LT': '龙江航空', 'GY': '多彩贵州'}
        
        print("关键航司验证:")
        for code, expected_name in key_airlines.items():
            match = re.search(rf"'{code}':\s*'([^']+)'", content)
            if match:
                actual_name = match.group(1)
                status = "✓" if actual_name == expected_name else "✗"
                print(f"  {status} {code}: {actual_name} {'(正确)' if actual_name == expected_name else f'(应为: {expected_name})'}")
            else:
                print(f"  ✗ {code}: 未找到")
        
        # 检查航司下拉框
        print("\n2. 检查航司下拉框:")
        print("-" * 60)
        
        has_dropdown = 'airlineDropdownList' in content
        has_update_function = 'updateAirlineDropdown' in content
        has_render_function = 'renderAirlines' in content
        
        print(f"航司下拉框元素: {'✓' if has_dropdown else '✗'}")
        print(f"更新航司函数: {'✓' if has_update_function else '✗'}")
        print(f"渲染航司函数: {'✓' if has_render_function else '✗'}")
        
        # 检查航司选择逻辑
        print("\n3. 检查航司选择逻辑:")
        print("-" * 60)
        
        if has_update_function:
            # 查找 updateAirlineDropdown 函数中的AIRLINE_NAMES使用
            name_usage = re.search(r"const name = AIRLINE_NAMES\[airline\.code\]", content)
            code_name_pattern = re.search(r"airline\.code} - \$\{name\}", content)
            
            print(f"使用AIRLINE_NAMES获取航司名称: {'✓' if name_usage else '✗'}")
            print(f"航司显示格式(代码-名称): {'✓' if code_name_pattern else '✗'}")
        
        # 检查API调用
        print("\n4. 检查API调用:")
        print("-" * 60)
        
        has_load_airlines = 'loadAirlines' in content
        has_api_endpoint = '/api/airlines' in content
        
        print(f"loadAirlines函数: {'✓' if has_load_airlines else '✗'}")
        print(f"API端点/api/airlines: {'✓' if has_api_endpoint else '✗'}")
        
        # 总结
        print("\n" + "=" * 60)
        print("验证总结:")
        print("=" * 60)
        
        all_ok = (
            len(matches) >= 36 and
            all(f"'{code}': '{expected_name}'" in content for code, expected_name in key_airlines.items()) and
            has_dropdown and
            has_update_function and
            has_load_airlines and
            has_api_endpoint
        )
        
        if all_ok:
            print("\n[OK] 所有检查通过！")
            print("\n如果航司仍然不显示，请尝试:")
            print("  1. 按 Ctrl+Shift+R 强制刷新浏览器")
            print("  2. 清除浏览器缓存")
            print("  3. 检查浏览器控制台是否有JavaScript错误")
            print("  4. 确认已正确登录")
        else:
            print("\n[FAIL] 部分检查失败，请检查上述详细结果")
        
except Exception as e:
    print(f"\n[ERROR] 检查失败: {e}")
    print("请确保服务器正在运行: http://localhost:8000")

print("\n" + "=" * 60)
