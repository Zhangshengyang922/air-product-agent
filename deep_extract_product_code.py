import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 深度提取产品代码 ===\n")

# 机场代码排除列表
airport_codes = {'KMG', 'PEK', 'PVG', 'SHA', 'CAN', 'SZX', 'CTU', 'XIY', 'TFU', 'HFE', 'HGH', 'WUH', 'CKG',
                 'URC', 'TAO', 'DLC', 'TSN', 'NKG', 'HAK', 'SYX', 'LXA', 'INC', 'CGO', 'CSX', 'KWL',
                 'KWE', 'HET', 'TNA', 'WNZ', 'NNG', 'TYN', 'SJW', 'TCZ', 'JHG', 'SYM', 'LUM', 'LNJ', 'BSD',
                 'PKX', 'XAY', 'URQ', 'NAY', 'YCU', 'JDZ', 'DAX', 'ENY', 'HNY', 'LHW', 'IQN', 'JJN',
                 'LCX', 'LYI', 'NTG', 'QUZ', 'WUS', 'XMN', 'WNZ', 'HSN', 'HGH', 'HYN', 'JUZ', 'KNH',
                 'KHN', 'KOW', 'KHN', 'LCX', 'NNY', 'NGQ', 'NKG', 'NNG', 'NGB', 'NBO', 'NBY', 'KNC',
                 'PZI', 'SHE', 'SJW', 'SYX', 'SZX', 'SWA', 'SYX', 'TNA', 'TNH', 'TEN', 'TYN', 'TXN',
                 'URC', 'WNZ', 'WUH', 'WEF', 'WUX', 'WUS', 'WZH', 'XFN', 'XIL', 'XNN', 'XIC', 'XEN',
                 'YBP', 'YIH', 'YIE', 'YNT', 'YCU', 'YHZ', 'YKH', 'YCU', 'YIH', 'YCU', 'YKH', 'YCU',
                 'ZHA', 'ZYI', 'LXA', 'ZAT', 'ZYI', 'ZUH', 'ZSN', 'ZPZ', 'ZHA', 'ZHJ', 'ZHY', 'ZHH'}

# 系统关键词排除
system_keywords = {'BSP', 'PAT', 'CGP', 'YGP', 'CPAS', 'TMC', 'FB', 'TC', 'GP', 'B2B',
                  'B3B', 'B4B', 'B5B', 'B6B', 'B7B', 'B8B', 'B9B', 'B10B', 'B11B', 'B12B',
                  'B13B', 'B14B', 'B15B', 'B16B', 'B17B', 'B18B', 'B19B', 'B20B', 'B21B', 'B22B',
                  'B23B', 'B24B', 'B25B', 'B26B', 'B27B', 'B28B', 'B29B', 'B30B', 'B31B', 'B32B',
                  'B33B', 'B34B', 'B35B', 'B36B', 'B37B', 'B38B', 'B39B', 'B40B', 'B41B', 'B42B',
                  'B43B', 'W1', 'G5', 'BX', 'GPW1', 'GPW', 'X2', 'X3', 'YGB', 'L1', 'L2', 'L3',
                  'L4', 'L5', 'L6', 'L7', 'U1', 'U2', 'T1', 'T2'}

# 更精确的产品代码模式：
# 1. TC项(XXX)格式中的XXX
# 2. FB项(X)格式中的X
# 3. 产品代码：XXX格式
tc_pattern = re.compile(r'TC\s*[项(（]*([A-Z0-9]+)[)）\s,，]')
fb_pattern = re.compile(r'FB\s*[项(（]*([A-Z0-9]+)[)）\s,，]')
farebasis_pattern = re.compile(r'Farebasis\s*[项(（]*[^)]*后缀[为：：]*([A-Z0-9]+)[)）\s,，]', re.IGNORECASE)
standalone_pattern = re.compile(r'\b([A-Z]{3,6}\d{0,3})\b')

corrected_count = 0

for idx, row in df.iterrows():
    remarks = str(row['remarks']) if pd.notna(row['remarks']) else ''
    booking_class = str(row['booking_class']) if pd.notna(row['booking_class']) else ''
    
    # 先清除明显错误的代码（如机场代码）
    current_code = str(row['product_code']) if pd.notna(row['product_code']) else ''
    if current_code and current_code != 'nan':
        if current_code in airport_codes:
            df.at[idx, 'product_code'] = ''
            print(f"清除错误代码: {row['airline']} - {current_code} (机场代码)")
            corrected_count += 1
            continue
    
    # 如果已经有正确的代码，跳过
    if current_code and current_code != '' and current_code != 'nan':
        continue
    
    # 尝试从备注提取
    found_code = None
    
    # 1. 查找TC项格式
    tc_match = tc_pattern.search(remarks)
    if tc_match:
        code = tc_match.group(1)
        if code not in airport_codes and code not in system_keywords:
            found_code = code
            print(f"从TC项提取: {row['airline']} - {code}")
    
    # 2. 查找FB项格式
    if not found_code:
        fb_match = fb_pattern.search(remarks)
        if fb_match:
            code = fb_match.group(1)
            if code not in airport_codes and code not in system_keywords:
                found_code = code
                print(f"从FB项提取: {row['airline']} - {code}")
    
    # 3. 查找Farebasis后缀格式
    if not found_code:
        fb_match = farebasis_pattern.search(remarks + ' ' + booking_class)
        if fb_match:
            code = fb_match.group(1)
            if code not in airport_codes and code not in system_keywords:
                found_code = code
                print(f"从Farebasis提取: {row['airline']} - {code}")
    
    # 4. 查找独立的字母数字组合
    if not found_code:
        codes = standalone_pattern.findall(remarks)
        for code in codes:
            if code not in airport_codes and code not in system_keywords:
                # 检查代码长度是否合理
                if len(code) >= 3 and len(code) <= 10:
                    found_code = code
                    print(f"从备注提取: {row['airline']} - {code}")
                    break
    
    if found_code:
        df.at[idx, 'product_code'] = found_code
        corrected_count += 1

print(f"\n修正/提取产品代码: {corrected_count}条\n")

# 检查提取结果
has_code = df['product_code'].notna() & (df['product_code'] != '')
print(f"有产品代码: {has_code.sum()} ({has_code.sum()*100/len(df):.1f}%)\n")

# 显示提取的代码样本
print("提取/修正后的产品代码样本:")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code']].head(40)
for idx, row in code_samples.iterrows():
    print(f"  {row['airline']} - {row['product_code']:<15} {row['product_name'][:40]}")

# 保存
df.to_csv('assets/products.csv', index=False, encoding='utf-8-sig')
print(f"\n已保存更新后的数据到 assets/products.csv")
