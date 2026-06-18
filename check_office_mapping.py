import pandas as pd

# 读取当前产品数据
df = pd.read_csv('assets/products.csv')

print("=== 数据结构检查 ===\n")
print(f"总记录数: {len(df)}\n")

print("列名:")
print(df.columns.tolist())
print("\n")

print("前10行数据（关键列）:")
key_cols = ['airline', 'product_name', 'route', 'booking_class', 'price_increase', 
            'rebate_ratio', 'product_code', 'office', 'remarks', 'validity']
available_cols = [col for col in key_cols if col in df.columns]
print(df[available_cols].head(10))
print("\n")

# 检查office列的内容
if 'office' in df.columns:
    print("=== Office列数据检查 ===\n")
    print(f"Office非空记录数: {df['office'].notna().sum()}")
    print(f"Office为空记录数: {df['office'].isna().sum()}")
    
    print("\nOffice列的唯一值（前20个）:")
    office_values = df['office'].dropna().unique()[:20]
    for val in office_values:
        print(f"  {val}")
    
    print("\n可能被误识别的office值（包含关键词的备注）:")
    if 'remarks' in df.columns:
        remarks_with_office = df[df['remarks'].str.contains('OFFICE|Office|office', na=False)]['remarks']
        print(f"找到 {len(remarks_with_office)} 条包含office关键词的备注:")
        for remark in remarks_with_office.head(10):
            print(f"  {remark}")

# 检查product_code列
if 'product_code' in df.columns:
    print("\n=== Product Code列数据检查 ===\n")
    print(f"Product Code非空记录数: {df['product_code'].notna().sum()}")
    print(f"Product Code为空记录数: {df['product_code'].isna().sum()}")
    
    print("\nProduct Code列的唯一值（前20个）:")
    code_values = df['product_code'].dropna().unique()[:20]
    for val in code_values:
        print(f"  {val}")

# 检查是否有备注被当作了office
print("\n=== 数据对齐检查 ===\n")
if 'office' in df.columns and 'remarks' in df.columns:
    # 查看office列中的长文本（可能是备注）
    long_office = df[df['office'].str.len() > 20 if df['office'].dtype == 'object' else False]
    print(f"Office列中可能为备注的记录（长度>20）: {len(long_office)}")
    if len(long_office) > 0:
        print("\n前5条:")
        for idx, row in long_office.head(5).iterrows():
            print(f"  {row['office'][:100]}")
