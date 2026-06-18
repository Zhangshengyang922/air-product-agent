import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 检查清理后的数据 ===\n")

print("列名:", df.columns.tolist())

print("\nOffice列的样本（前20条）:")
for idx, row in df.head(20).iterrows():
    print(f"  {row['airline']} - Office: '{row['office']}'")

print("\nSales_channel列的样本（前20条）:")
for idx, row in df.head(20).iterrows():
    print(f"  {row['airline']} - Channel: '{row['sales_channel']}'")

# 查找包含GP/BSP的记录
print("\n原始包含GP/BSP的记录（应该在office列）:")
gp_records = df[df['office'].str.contains('GP|BSP|B2B', na=False)][['airline', 'product_name', 'office']].head(10)
for idx, row in gp_records.iterrows():
    print(f"  {row['airline']} - {row['office']} - {row['product_name'][:30]}")
