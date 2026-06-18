import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 从备注和舱位列提取产品代码 ===\n")

# 产品代码模式：根据观察，产品代码通常格式为：
# 1. 字母+数字组合（如BGYX、WFYX40、CVG1）
# 2. 排除机场代码和常见关键词
airport_codes = {'KMG', 'PEK', 'PVG', 'SHA', 'CAN', 'SZX', 'CTU', 'XIY', 'TFU', 'HFE', 'HGH', 'WUH', 'CKG',
                 'URC', 'TAO', 'DLC', 'TSN', 'NKG', 'HAK', 'SYX', 'LXA', 'INC', 'CGO', 'CSX', 'KWL',
                 'KWE', 'HET', 'TNA', 'WNZ', 'NNG', 'TYN', 'SJW', 'TCZ', 'JHG', 'SYM', 'LUM', 'LNJ', 'BSD',
                 'BSP', 'PAT', 'CGP', 'YGP', 'CPAS', 'TMC', 'FB', 'TC'}
system_keywords = {'BSP', 'PAT', 'B2B', 'B3B', 'B4B', 'B5B', 'B6B', 'B7B', 'B8B', 'B9B',
                  'B10B', 'B11B', 'B12B', 'B13B', 'B14B', 'B15B', 'B16B', 'B17B', 'B18B', 'B19B',
                  'B20B', 'B21B', 'B22B', 'B23B', 'B24B', 'B25B', 'B26B', 'B27B', 'B28B', 'B29B',
                  'B30B', 'B31B', 'B32B', 'B33B', 'B34B', 'B35B', 'B36B', 'B37B', 'B38B', 'B39B',
                  'B40B', 'B41B', 'B42B', 'B43B', 'GP', 'TMC', 'TC', 'FB', 'YGB', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7'}

# 产品代码模式：2-6个字母+0-3个数字（排除机场和系统关键词）
product_code_pattern = re.compile(r'\b([A-Z]{2,6}\d{0,3})\b')

extracted_count = 0

for idx, row in df.iterrows():
    # 只处理没有产品代码的记录
    if not pd.isna(row['product_code']) and row['product_code'] != '':
        continue
    
    remarks = str(row['remarks']) if pd.notna(row['remarks']) else ''
    booking_class = str(row['booking_class']) if pd.notna(row['booking_class']) else ''
    
    # 从备注提取
    found_codes = []
    if remarks and remarks != 'nan':
        codes = product_code_pattern.findall(remarks)
        for code in codes:
            if code not in airport_codes and code not in system_keywords:
                # 排除过于短的代码（少于3个字符）或过于长的代码（超过10个字符）
                if len(code) >= 3 and len(code) <= 10:
                    found_codes.append(code)
    
    # 从舱位提取
    if not found_codes and booking_class and booking_class != 'nan':
        codes = product_code_pattern.findall(booking_class)
        for code in codes:
            if code not in airport_codes and code not in system_keywords:
                if len(code) >= 3 and len(code) <= 10:
                    found_codes.append(code)
    
    if found_codes:
        # 去重，选择最可能的代码（通常是最长的或第一个）
        found_codes = list(dict.fromkeys(found_codes))
        # 按长度降序排序，选择最长的（更可能是产品代码）
        found_codes.sort(key=len, reverse=True)
        df.at[idx, 'product_code'] = found_codes[0]
        extracted_count += 1

print(f"提取产品代码: {extracted_count}条\n")

# 检查提取结果
print("提取后的产品代码样本:")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code']].head(30)
for idx, row in code_samples.iterrows():
    print(f"  {row['airline']} - {row['product_code']:<15} {row['product_name'][:40]}")

print("\n" + "="*80 + "\n")

# 统计覆盖情况
has_code = df['product_code'].notna() & (df['product_code'] != '')
print(f"有产品代码: {has_code.sum()} ({has_code.sum()*100/len(df):.1f}%)\n")

print("各航司产品代码覆盖情况:")
code_by_airline = df.groupby('airline').agg({
    'airline': 'count',
    'product_code': lambda x: (x.notna() & (x != '')).sum()
})
code_by_airline.columns = ['总数', '产品代码数']
code_by_airline['覆盖率'] = code_by_airline['产品代码数'] * 100 / code_by_airline['总数']
print(code_by_airline.round(1).sort_values('覆盖率', ascending=False))

# 保存
df.to_csv('assets/products.csv', index=False, encoding='utf-8-sig')
print(f"\n已保存更新后的数据到 assets/products.csv")
