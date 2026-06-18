import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 检查政策代码和office号 ===\n")

print(f"总记录数: {len(df)}\n")

# 检查产品代码（政策代码）
print("=== 产品代码（policy_code）检查 ===\n")
print(f"产品代码列是否存在: {'policy_code' in df.columns}")
if 'policy_code' in df.columns:
    print(f"有产品代码记录数: {df['policy_code'].notna().sum()}")
    print(f"产品代码唯一值: {df['policy_code'].dropna().unique()}")
else:
    print("缺少policy_code列！")

# 检查product_code列
print("\n=== Product Code列检查 ===\n")
if 'product_code' in df.columns:
    print(f"有product_code记录数: {df['product_code'].notna().sum()}")
    print("\nProduct Code样本（前30条）:")
    code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code']].head(30)
    for idx, row in code_samples.iterrows():
        print(f"  {row['airline']} - {row['product_code']}")
else:
    print("缺少product_code列！")

# 检查office号是否有误识别的情况
print("\n=== Office号检查 ===\n")
if 'office' in df.columns:
    print(f"有office记录数: {df['office'].notna().sum()}")
    
    # 检查office列中的异常值（可能是备注或其他信息）
    office_df = df[df['office'].notna() & (df['office'] != '')]
    
    # 查找包含关键词的office值（可能是误识别）
    print("\n可能被误识别为office的值（包含特定关键词）:")
    keywords = ['服务', '产品', '权益', '免费', '提供', '享受', '有效', '限', '注意', '旅客', '会员']
    for keyword in keywords:
        suspicious = office_df[office_df['office'].str.contains(keyword, na=False)]
        if len(suspicious) > 0:
            print(f"\n包含'{keyword}'的记录 ({len(suspicious)}条):")
            for idx, row in suspicious.head(5).iterrows():
                print(f"  {row['airline']} - {row['office'][:60]}")
    
    # 显示所有office值
    print(f"\n所有Office值样本（前50条）:")
    office_values = office_df['office'].unique()[:50]
    for val in office_values:
        print(f"  {val}")

# 显示列结构
print("\n=== 数据列结构 ===\n")
print("所有列名:")
for i, col in enumerate(df.columns):
    print(f"  {i}. {col}")
