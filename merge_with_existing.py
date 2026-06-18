# -*- coding: utf-8 -*-
import pandas as pd
import os

# 文件路径
new_products_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/new_products.csv'
existing_products_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'
backup_file = existing_products_file.replace('.csv', '_backup.csv')
merged_file = existing_products_file

print("开始合并产品数据...")

# 读取新产品
print("\n读取新产品数据...")
new_df = pd.read_csv(new_products_file)
print(f"新产品数量: {len(new_df)}")
print(f"新产品列名: {list(new_df.columns)}")

# 读取现有产品
print("\n读取现有产品数据...")
existing_df = pd.read_csv(existing_products_file)
print(f"现有产品数量: {len(existing_df)}")
print(f"现有产品列名: {list(existing_df.columns)}")

# 备份现有产品
print(f"\n备份现有产品到: {backup_file}")
existing_df.to_csv(backup_file, index=False, encoding='utf-8-sig')

# 统一新产品的列名
print("\n标准化新产品列名...")
new_df_clean = pd.DataFrame()

# 从新产品中提取航司代码（从source_sheet列）
new_df_clean['airline'] = new_df['source_sheet'].str.extract(r'^([A-Z0-9]+)')[0]

# 映射其他列
new_df_clean['product_name'] = new_df['产品名称'] if '产品名称' in new_df.columns else ''
new_df_clean['route'] = new_df['航线'] if '航线' in new_df.columns else ''
new_df_clean['booking_class'] = new_df['订座舱位'] if '订座舱位' in new_df.columns else ''

# 处理价格列
price_col = None
for col in ['上浮价格', '上浮/下浮价格', 'price_increase']:
    if col in new_df.columns:
        price_col = col
        break
new_df_clean['price_increase'] = new_df[price_col] if price_col else ''

# 处理返点列
rebate_col = None
for col in ['政策返点', '政策返点（后返+车辆后返+代理费)', 'rebate_ratio']:
    if col in new_df.columns:
        rebate_col = col
        break
new_df_clean['rebate_ratio'] = new_df[rebate_col] if rebate_col else ''

new_df_clean['office'] = new_df['出票office'] if '出票office' in new_df.columns else ''
new_df_clean['remarks'] = new_df['备注'] if '备注' in new_df.columns else ''
new_df_clean['valid_period'] = new_df['产品有限期'] if '产品有限期' in new_df.columns else ''
new_df_clean['ticket_type'] = new_df['票证类型'] if '票证类型' in new_df.columns else ''
new_df_clean['policy_identifier'] = new_df['产品代码'] if '产品代码' in new_df.columns else ''
new_df_clean['policy_code'] = ''

# 清理数据 - 移除空航司的行
new_df_clean = new_df_clean[new_df_clean['airline'].notna() & (new_df_clean['airline'] != '')]
new_df_clean = new_df_clean.reset_index(drop=True)

print(f"清理后新产品数量: {len(new_df_clean)}")

# 合并数据
print("\n合并产品数据...")
merged_df = pd.concat([existing_df, new_df_clean], ignore_index=True)
print(f"合并后总产品数: {len(merged_df)}")

# 保存合并后的文件
print(f"\n保存合并后的产品到: {merged_file}")
merged_df.to_csv(merged_file, index=False, encoding='utf-8-sig')

# 统计各航司产品数量
print("\n各航司产品数量统计:")
airline_counts = merged_df['airline'].value_counts().head(30)
for airline, count in airline_counts.items():
    print(f"  {airline}: {count}")

print(f"\n总计: {len(merged_df)} 个产品")
print("\n合并完成！")
