import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 检查备注和舱位列中的政策代码 ===\n")

# 检查备注列中是否包含类似产品代码的内容
print("备注列中可能的政策代码（前30条）:\n")
policy_code_pattern = re.compile(r'[A-Z]{2,6}\d{0,3}')

found_codes = {}
for idx, row in df.iterrows():
    remarks = str(row['remarks']) if pd.notna(row['remarks']) else ''
    booking_class = str(row['booking_class']) if pd.notna(row['booking_class']) else ''

    # 在备注中查找
    if remarks and remarks != 'nan':
        # 查找可能的代码（字母+数字组合）
        codes = policy_code_pattern.findall(remarks)
        if codes:
            for code in codes:
                if len(code) >= 3 and len(code) <= 10:  # 合理的代码长度
                    if code not in found_codes:
                        found_codes[code] = []
                    found_codes[code].append({
                        'airline': row['airline'],
                        'product_name': row['product_name'],
                        'remarks': remarks[:100]
                    })

    # 在舱位列中查找
    if booking_class and booking_class != 'nan':
        codes = policy_code_pattern.findall(booking_class)
        if codes:
            for code in codes:
                if len(code) >= 3 and len(code) <= 10:
                    if code not in found_codes:
                        found_codes[code] = []
                    found_codes[code].append({
                        'airline': row['airline'],
                        'product_name': row['product_name'],
                        'booking_class': booking_class[:100]
                    })

print(f"找到 {len(found_codes)} 个可能的政策代码:\n")
for code, items in list(found_codes.items())[:20]:
    print(f"  代码: {code}")
    for item in items[:2]:
        print(f"    {item['airline']} - {item['product_name'][:30]}")
        if 'remarks' in item:
            print(f"    备注: {item['remarks'][:60]}...")
        if 'booking_class' in item:
            print(f"    舱位: {item['booking_class'][:60]}...")
    print()
