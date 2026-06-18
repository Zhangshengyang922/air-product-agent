import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 验证office和产品代码数据 ===\n")

print(f"总记录数: {len(df)}\n")

print("数据完整度:")
print(f"  - 产品名称: {df['product_name'].notna().sum()} ({df['product_name'].notna().sum()*100/len(df):.1f}%)")
print(f"  - 政策返点: {df['rebate_ratio'].notna().sum()} ({df['rebate_ratio'].notna().sum()*100/len(df):.1f}%)")
print(f"  - 上浮价格: {df['price_increase'].notna().sum()} ({df['price_increase'].notna().sum()*100/len(df):.1f}%)")
print(f"  - 产品代码: {df['product_code'].notna().sum()} ({df['product_code'].notna().sum()*100/len(df):.1f}%)")
print(f"  - Office号: {df['office'].notna().sum()} ({df['office'].notna().sum()*100/len(df):.1f}%)")

print("\n=== Office号样本（前20条）===")
office_samples = df[df['office'].notna() & (df['office'] != '')][['airline', 'product_name', 'office']].head(20)
for idx, row in office_samples.iterrows():
    print(f"{row['airline']} - {row['product_name'][:30]:30s} -> {row['office']}")

print("\n=== 产品代码样本（前20条）===")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code']].head(20)
for idx, row in code_samples.iterrows():
    print(f"{row['airline']} - {row['product_name'][:30]:30s} -> {row['product_code']}")

print("\n=== 备注样本（前10条）===")
remarks_samples = df[df['remarks'].notna() & (df['remarks'] != '')][['airline', 'product_name', 'remarks']].head(10)
for idx, row in remarks_samples.iterrows():
    print(f"{row['airline']} - {row['product_name'][:20]:20s}")
    print(f"        {str(row['remarks'])[:60]}")

print("\n=== 各航司office覆盖情况 ===")
office_by_airline = df.groupby('airline').apply(
    lambda x: pd.Series({
        '总数': len(x),
        '有office': x['office'].notna().sum(),
        '覆盖率': x['office'].notna().sum() * 100 / len(x)
    })
).round(1)
print(office_by_airline.sort_values('覆盖率', ascending=False))
