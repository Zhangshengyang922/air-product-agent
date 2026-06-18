import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 从备注列提取office号（针对无office的记录）===\n")

# office号模式：3-4位字母+3位数字
office_pattern = re.compile(r'\b([A-Z]{3,4}\d{3})\b')

extracted_count = 0

for idx, row in df.iterrows():
    # 只处理没有office的记录
    if not pd.isna(row['office']) and row['office'] != '':
        continue
    
    remarks = str(row['remarks']) if pd.notna(row['remarks']) else ''
    booking_class = str(row['booking_class']) if pd.notna(row['booking_class']) else ''
    
    # 从备注提取
    if remarks and remarks != 'nan':
        offices = office_pattern.findall(remarks)
        if offices:
            df.at[idx, 'office'] = '/'.join(list(dict.fromkeys(offices)))  # 去重
            extracted_count += 1
            continue
    
    # 从舱位提取
    if booking_class and booking_class != 'nan':
        offices = office_pattern.findall(booking_class)
        if offices:
            df.at[idx, 'office'] = '/'.join(list(dict.fromkeys(offices)))
            extracted_count += 1

print(f"提取office号: {extracted_count}条\n")

# 检查提取结果
print("提取后的office样本（从CA、CZ、3U等航司）:")
for airline in ['CA', 'CZ', '3U', 'EU', 'ZH']:
    airline_df = df[df['airline'] == airline]
    office_samples = airline_df[airline_df['office'].notna() & (airline_df['office'] != '')][['product_name', 'office']].head(10)
    print(f"\n{airline}航司:")
    for idx, row in office_samples.iterrows():
        print(f"  {row['office']:<30} {row['product_name'][:40]}")

print("\n" + "="*80 + "\n")

# 统计覆盖情况
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
