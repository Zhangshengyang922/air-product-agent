# -*- coding: utf-8 -*-
"""
将KY产品CSV数据转换并合并到products.csv
"""

import pandas as pd
import os

# 读取KY CSV文件
ky_csv_path = 'C:/Users/Administrator/OneDrive/桌面/air_prd_agent/各航司汇总产品-KY.csv'
print(f"正在读取KY CSV: {ky_csv_path}")

ky_df = pd.read_csv(ky_csv_path, encoding='utf-8-sig')

# 只保留前10列有效数据
valid_columns = ['产品名称', '航线', '订座舱位', '上浮价格', '政策返点', '产品代码', '票证类型', '出票OFFICE', '备注', '产品有限期']
ky_df = ky_df[valid_columns]

# 重命名为products.csv格式
column_mapping = {
    '产品名称': 'product_name',
    '航线': 'route',
    '订座舱位': 'booking_class',
    '上浮价格': 'price_increase',
    '政策返点': 'rebate_ratio',
    '产品代码': 'policy_identifier',  # 产品代码映射到policy_identifier
    '票证类型': 'ticket_type',
    '出票OFFICE': 'office',
    '备注': 'remarks',
    '产品有限期': 'valid_period'
}
ky_df = ky_df.rename(columns=column_mapping)

# 添加航司代码
ky_df['airline'] = 'KY'

# 添加空列（products.csv有但KY没有的）
ky_df['policy_code'] = ''
ky_df['sales_channel'] = ''

# 重新排列列顺序与products.csv一致
ky_df = ky_df[['airline', 'product_name', 'route', 'booking_class', 
               'price_increase', 'rebate_ratio', 'office', 'remarks',
               'valid_period', 'ticket_type', 'policy_identifier', 'policy_code', 'sales_channel']]

print(f"KY数据转换完成，共 {len(ky_df)} 条产品")

# 读取现有的products.csv
products_csv_path = 'assets/products.csv'
existing_df = pd.read_csv(products_csv_path, encoding='utf-8-sig')
print(f"现有products.csv有 {len(existing_df)} 条产品")

# 检查是否已有KY数据
ky_count_before = len(existing_df[existing_df['airline'] == 'KY'])
print(f"其中KY航司产品: {ky_count_before} 条")

# 移除现有的KY数据（避免重复）
existing_df = existing_df[existing_df['airline'] != 'KY']
print(f"移除KY数据后剩余: {len(existing_df)} 条产品")

# 合并数据
merged_df = pd.concat([existing_df, ky_df], ignore_index=True)
print(f"合并后总计: {len(merged_df)} 条产品")

# 确保列顺序一致
merged_df = merged_df[['airline', 'product_name', 'route', 'booking_class', 
                       'price_increase', 'rebate_ratio', 'office', 'remarks',
                       'valid_period', 'ticket_type', 'policy_identifier', 'policy_code', 'sales_channel']]

# 保存到CSV文件
merged_df.to_csv(products_csv_path, index=False, encoding='utf-8-sig')
print(f"\n✅ 已成功保存到: {products_csv_path}")

# 验证
verify_df = pd.read_csv(products_csv_path, encoding='utf-8-sig')
ky_count_after = len(verify_df[verify_df['airline'] == 'KY'])
print(f"\n验证: KY航司产品数量 = {ky_count_after} 条")
print("所有航司产品统计:")
print(verify_df['airline'].value_counts().head(10))
