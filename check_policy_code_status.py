import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 检查政策代码数据状态 ===\n")

print(f"总记录数: {len(df)}\n")

# 检查product_code列
print("Product Code列统计:")
print(f"  有product_code的记录数: {df['product_code'].notna().sum()}")
print(f"  product_code为空: {df['product_code'].isna().sum()}")

# 显示有product_code的记录
print("\n有product_code的记录样本（前30条）:")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code', 'remarks', 'booking_class']].head(30)
for idx, row in code_samples.iterrows():
    print(f"\n{row['airline']} - {row['product_code']}")
    print(f"  产品: {row['product_name'][:40]}")
    if pd.notna(row['remarks']) and row['remarks']:
        print(f"  备注: {str(row['remarks'])[:80]}")
    if pd.notna(row['booking_class']) and row['booking_class']:
        print(f"  舱位: {str(row['booking_class'])[:80]}")

# 检查各航司的product_code覆盖
print("\n\n" + "="*80)
print("各航司产品代码覆盖情况:")
code_by_airline = df.groupby('airline').agg({
    'airline': 'count',
    'product_code': lambda x: (x.notna() & (x != '')).sum()
})
code_by_airline.columns = ['总数', '产品代码数']
code_by_airline['覆盖率'] = code_by_airline['产品代码数'] * 100 / code_by_airline['总数']
print(code_by_airline.round(1).sort_values('覆盖率', ascending=False))
