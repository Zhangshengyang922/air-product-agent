import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 清理Office数据 ===\n")

# 创建新列：销售渠道
df['sales_channel'] = ''

# 标准化office列，提取真正的office号
standard_office_pattern = re.compile(r'^([A-Z]{3,4}\d{3}(?:/[A-Z]{3,4}\d{3})*)$')

for idx, row in df.iterrows():
    office_value = str(row['office']) if pd.notna(row['office']) else ''

    if office_value == '' or office_value == 'nan':
        df.at[idx, 'office'] = ''
        continue

    # 检查是否是标准office号
    if standard_office_pattern.match(office_value):
        # 这是标准office号，保持不变
        df.at[idx, 'sales_channel'] = '未指定'
    elif '/' in office_value:
        # 可能是多个值混合
        parts = office_value.split('/')
        office_parts = []
        channel_parts = []

        for part in parts:
            part = part.strip()
            if standard_office_pattern.match(part):
                office_parts.append(part)
            elif part in ['GP', 'BSP', 'B2B', 'B3B', 'B4B', 'B5B', 'B6B', 'B7B', 'B8B',
                           'B9B', 'B10B', 'B11B', 'B12B', 'B13B', 'B14B', 'B15B',
                           'B16B', 'B17B', 'B18B', 'B19B', 'B20B', 'B21B', 'B22B',
                           'B23B', 'B24B', 'B25B', 'B26B', 'B27B', 'B28B', 'B29B',
                           'B30B', 'B31B', 'B32B', 'B33B', 'B34B', 'B35B', 'B36B',
                           'B37B', 'B38B', 'B39B', 'B40B', 'B41B', 'B42B', 'B43B']:
                channel_parts.append(part)

        if office_parts:
            df.at[idx, 'office'] = '/'.join(office_parts)
            df.at[idx, 'sales_channel'] = '/'.join(channel_parts) if channel_parts else '未指定'
        else:
            # 没有标准office号，全部作为渠道
            df.at[idx, 'office'] = ''
            df.at[idx, 'sales_channel'] = office_value
    elif office_value in ['GP', 'BSP', 'B2B', 'B3B', 'B4B', 'B5B', 'B6B', 'B7B', 'B8B',
                          'B9B', 'B10B', 'B11B', 'B12B', 'B13B', 'B14B', 'B15B',
                          'B16B', 'B17B', 'B18B', 'B19B', 'B20B', 'B21B', 'B22B',
                          'B23B', 'B24B', 'B25B', 'B26B', 'B27B', 'B28B', 'B29B',
                          'B30B', 'B31B', 'B32B', 'B33B', 'B34B', 'B35B', 'B36B',
                          'B37B', 'B38B', 'B39B', 'B40B', 'B41B', 'B42B', 'B43B']:
        df.at[idx, 'office'] = ''
        df.at[idx, 'sales_channel'] = office_value
    elif 'BSP(仅适用于散客）' in office_value:
        df.at[idx, 'office'] = ''
        df.at[idx, 'sales_channel'] = office_value
    else:
        # 其他情况，保持原样
        df.at[idx, 'sales_channel'] = '未指定'

# 统计
print("清理后统计:")
print(f"总记录数: {len(df)}")
has_office = df['office'].notna() & (df['office'] != '') & (df['office'] != 'nan')
has_channel = df['sales_channel'].notna() & (df['sales_channel'] != '') & (df['sales_channel'] != '未指定')
print(f"有标准office号: {has_office.sum()} ({has_office.sum()*100/len(df):.1f}%)")
print(f"有销售渠道标识: {has_channel.sum()} ({has_channel.sum()*100/len(df):.1f}%)")

print("\n标准office号样本:")
standard_offices = df[df['office'].notna() & (df['office'] != '')]['office'].unique()
for office in standard_offices[:10]:
    print(f"  {office}")

print("\n销售渠道标识样本:")
channels = df[df['sales_channel'].notna() & (df['sales_channel'] != '') & (df['sales_channel'] != '未指定')]['sales_channel'].unique()
for channel in channels[:10]:
    print(f"  {channel}")

print("\n各航司office覆盖情况:")
office_by_airline = df.groupby('airline').agg({
    'airline': 'count',
    'office': lambda x: (x.notna() & (x != '') & (x != 'nan')).sum()
})
office_by_airline.columns = ['总数', '标准office数']
office_by_airline['覆盖率'] = office_by_airline['标准office数'] * 100 / office_by_airline['总数']
print(office_by_airline.round(1).sort_values('覆盖率', ascending=False))

# 保存清理后的数据
df.to_csv('assets/products.csv', index=False, encoding='utf-8-sig')
print(f"\n已保存清理后的数据到 assets/products.csv")
