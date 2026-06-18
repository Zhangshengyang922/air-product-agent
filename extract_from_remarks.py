import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 从备注列提取office号和产品代码 ===\n")

# office号模式：3-4位字母+3位数字
office_pattern = re.compile(r'\b([A-Z]{3,4}\d{3})(?:/([A-Z]{3,4}\d{3}))*\b')

# 产品代码模式（排除机场代码和常见关键词）
# 机场代码排除列表
airport_codes = {'KMG', 'PEK', 'PVG', 'SHA', 'CAN', 'SZX', 'CTU', 'XIY', 'TFU', 'HFE', 'HGH', 'WUH', 'CKG',
                 'URC', 'TAO', 'DLC', 'TSN', 'NKG', 'HGH', 'HAK', 'SYX', 'LXA', 'INC', 'CGO', 'CSX', 'KWL',
                 'KWE', 'HET', 'TNA', 'WNZ', 'NNG', 'TYN', 'SJW', 'TCZ', 'JHG', 'SYM', 'LUM', 'LNJ', 'BSD',
                 'BSP', 'PAT', 'CGP', 'YGP', 'CPAS', 'GQQ', 'PXQ', 'PCJ', 'PYE', 'PXE', 'PPC', 'PTGH'}

# 统计
extracted_office = 0
extracted_code = 0

for idx, row in df.iterrows():
    remarks = str(row['remarks']) if pd.notna(row['remarks']) else ''
    
    # 提取office号
    if remarks and remarks != 'nan':
        office_matches = office_pattern.findall(remarks)
        if office_matches:
            # 提取所有匹配的office号
            offices = []
            for match in office_matches:
                for part in match:
                    if part:  # 检查每个部分
                        offices.append(part)
            
            if offices and not row['office']:  # 如果office列为空
                df.at[idx, 'office'] = '/'.join(offices)
                extracted_office += 1
    
    # 从舱位列提取office号
    booking_class = str(row['booking_class']) if pd.notna(row['booking_class']) else ''
    if booking_class and booking_class != 'nan' and not row['office']:
        office_matches = office_pattern.findall(booking_class)
        if office_matches:
            offices = []
            for match in office_matches:
                for part in match:
                    if part:
                        offices.append(part)
            
            if offices:
                df.at[idx, 'office'] = '/'.join(offices)
                extracted_office += 1

print(f"从备注/舱位列提取office号: {extracted_office}条\n")

# 检查提取后的office覆盖情况
has_office = df['office'].notna() & (df['office'] != '')
print(f"有标准office号: {has_office.sum()} ({has_office.sum()*100/len(df):.1f}%)\n")

print("各航司office覆盖情况:")
office_by_airline = df.groupby('airline').agg({
    'airline': 'count',
    'office': lambda x: (x.notna() & (x != '')).sum()
})
office_by_airline.columns = ['总数', '标准office数']
office_by_airline['覆盖率'] = office_by_airline['标准office数'] * 100 / office_by_airline['总数']
print(office_by_airline.round(1).sort_values('覆盖率', ascending=False))

# 保存
df.to_csv('assets/products.csv', index=False, encoding='utf-8-sig')
print(f"\n已保存更新后的数据到 assets/products.csv")
