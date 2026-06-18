import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 查找异常的Office值 ===\n")

# 查找所有office值
all_offices = df[df['office'].notna() & (df['office'] != '')]['office'].unique()

# 分类office值
standard_offices = []
suspicious_offices = []

for office in all_offices:
    office_str = str(office)
    # 标准office格式：3-4位字母+3位数字（如KMG319）
    import re
    if re.match(r'^[A-Z]{3,4}\d{3}$', office_str) or '/' in office_str:
        # 检查是否包含/分隔的多个标准office
        parts = office_str.split('/')
        all_valid = all(re.match(r'^[A-Z]{3,4}\d{3}$', p.strip()) for p in parts)
        if all_valid:
            standard_offices.append(office_str)
            continue
    
    # 其他情况都是可疑的
    suspicious_offices.append(office_str)

print(f"标准office数量: {len(standard_offices)}")
print(f"可疑office数量: {len(suspicious_offices)}\n")

print("标准office样本:")
for office in standard_offices[:20]:
    print(f"  {office}")

print("\n可疑office值:")
for office in suspicious_offices:
    # 显示包含这些可疑值的产品
    rows = df[df['office'] == office][['airline', 'product_name', 'office']].head(3)
    print(f"\n  值: {office}")
    for idx, row in rows.iterrows():
        print(f"    {row['airline']} - {row['product_name'][:50]}")
