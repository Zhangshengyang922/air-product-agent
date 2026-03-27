import pandas as pd
from pathlib import Path
from collections import defaultdict

# 读取products.csv
csv_path = Path("assets/products_with_382_empty_airline.csv")
df = pd.read_csv(csv_path)

print(f"原始数据: {len(df)} 行")

# 过滤掉airline为空的记录
df = df[df['airline'].notna() & (df['airline'] != '')]
print(f"去除airline为空后: {len(df)} 行")

# 去除完全重复的行
df = df.drop_duplicates()
print(f"去除完全重复后: {len(df)} 行")

# 智能合并策略:
# 只有当 airline + product_name + route + booking_class + price_increase + rebate_ratio + policy_code + office 都相同时才合并
# 如果只有其中几个字段不同,说明是同一产品的不同变体,应该保留

key_fields = ['airline', 'product_name', 'route', 'booking_class', 'price_increase', 'rebate_ratio', 'policy_code', 'office']

# 处理NaN值
for col in key_fields:
    df[col] = df[col].fillna('')

# 创建组合键
df['dedup_key'] = df[key_fields].apply(
    lambda x: '|'.join(x.astype(str)), axis=1
)

# 去除完全重复的记录(基于所有关键字段)
df_clean = df.drop_duplicates(subset=['dedup_key'], keep='first')
del df_clean['dedup_key']

print(f"去除完全重复后(基于所有关键字段): {len(df_clean)} 行")

# 保存合并后的文件
output_path = Path("assets/products_smart_merged.csv")
df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n已保存到: {output_path}")

# 统计信息
print(f"\n=== 合并后统计 ===")
print(f"总产品数: {len(df_clean)}")
print(f"航司数量: {df_clean['airline'].nunique()}")

print(f"\n航空公司分布:")
airline_counts = df_clean['airline'].value_counts()
for airline, count in airline_counts.items():
    print(f"  {airline}: {count}个")

print(f"\n政策代码统计:")
has_code = df_clean['policy_code'].notna() & (df_clean['policy_code'] != '') & (df_clean['policy_code'] != '-')
no_code = ~has_code
print(f"  有政策代码: {has_code.sum()}个 ({has_code.sum()/len(df_clean)*100:.1f}%)")
print(f"  无政策代码: {no_code.sum()}个 ({no_code.sum()/len(df_clean)*100:.1f}%)")

# 显示南航的统计
cz_data = df_clean[df_clean['airline'] == 'CZ']
print(f"\n南航(CZ)统计:")
print(f"  产品数: {len(cz_data)}个")
print(f"  有政策代码: {(cz_data['policy_code'].notna() & (cz_data['policy_code'] != '') & (cz_data['policy_code'] != '-')).sum()}个")

# 统计还有多少重复的(基于 airline + product_name + route + booking_class)
key_fields_simple = ['airline', 'product_name', 'route', 'booking_class']
df_check = df_clean.copy()
for col in key_fields_simple:
    df_check[col] = df_check[col].fillna('')
df_check['simple_key'] = df_check[key_fields_simple].apply(lambda x: '|'.join(x.astype(str)), axis=1)

simple_duplicates = df_check[df_check.duplicated(subset=['simple_key'], keep=False)]
print(f"\n基于(airline+product_name+route+booking_class)的重复: {len(simple_duplicates)}个产品")
print(f"  这些是同一产品的不同变体(不同的价格/返点/政策代码/office),已保留")
