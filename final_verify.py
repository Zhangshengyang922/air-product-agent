import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 最终数据验证 ===\n")

print(f"总记录数: {len(df)}\n")

# 检查产品代码
print("产品代码样本（有product_code的记录）:")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code']].head(15)
for idx, row in code_samples.iterrows():
    print(f"  {row['airline']} - {row['product_code']:<15} {row['product_name'][:35]}")

print("\n" + "="*80 + "\n")

# 检查office号
print("标准office号样本:")
office_samples = df[df['office'].notna() & (df['office'] != '')][['airline', 'product_name', 'office']].head(15)
for idx, row in office_samples.iterrows():
    print(f"  {row['airline']} - {row['office']:<35} {row['product_name'][:30]}")

print("\n" + "="*80 + "\n")

# 检查销售渠道
print("销售渠道样本:")
channel_samples = df[df['sales_channel'].notna() & (df['sales_channel'] != '')][['airline', 'product_name', 'sales_channel']].head(15)
for idx, row in channel_samples.iterrows():
    print(f"  {row['airline']} - {row['sales_channel']:<20} {row['product_name'][:40]}")

print("\n" + "="*80 + "\n")

# 各航司数据统计
print("各航司数据统计:")
stats = df.groupby('airline').agg({
    'airline': 'count',
    'product_code': lambda x: (x.notna() & (x != '')).sum(),
    'office': lambda x: (x.notna() & (x != '')).sum(),
    'sales_channel': lambda x: (x.notna() & (x != '')).sum()
})
stats.columns = ['总数', '产品代码', '标准office', '销售渠道']
stats['产品代码%'] = stats['产品代码'] * 100 / stats['总数']
stats['标准office%'] = stats['标准office'] * 100 / stats['总数']
stats['销售渠道%'] = stats['销售渠道'] * 100 / stats['总数']
print(stats.round(1).sort_values('总数', ascending=False))
