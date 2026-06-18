# -*- coding: utf-8 -*-
import pandas as pd
import os
import sys

# 读取CSV文件，处理可能的编码问题
csv_file = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

try:
    # 尝试用不同编码读取
    for encoding in ['utf-8', 'gbk', 'gb18030', 'utf-8-sig']:
        try:
            df = pd.read_csv(csv_file, encoding=encoding)
            print(f"成功用 {encoding} 编码读取文件")
            print(f"行数: {len(df)}")
            print(f"列名: {list(df.columns)}")
            print("\n前5行数据:")
            print(df.head())
            break
        except Exception as e:
            print(f"{encoding} 编码失败: {e}")
            continue
    else:
        print("所有编码尝试都失败")
        sys.exit(1)

    # 显示各航司产品数量
    print("\n\n各航司产品数量统计:")
    if 'airline' in df.columns:
        print(df['airline'].value_counts())

    # 读取现有产品文件
    existing_products = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'
    existing_df = None
    if os.path.exists(existing_products):
        existing_df = pd.read_csv(existing_products)
        print(f"\n现有产品数量: {len(existing_df)}")
        print(f"现有产品列名: {list(existing_df.columns)}")

    # 合并数据
    if existing_df is not None:
        # 统一列名
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        existing_df.columns = existing_df.columns.str.lower().str.replace(' ', '_')

        # 找出相同的列
        common_cols = list(set(df.columns) & set(existing_df.columns))
        print(f"\n相同列: {common_cols}")

        # 合并
        merged_df = pd.concat([existing_df, df], ignore_index=True)
        print(f"\n合并后总产品数: {len(merged_df)}")

        # 保存合并后的文件
        backup_file = existing_products.replace('.csv', '_backup.csv')
        existing_df.to_csv(backup_file, index=False, encoding='utf-8-sig')
        print(f"已备份原文件到: {backup_file}")

        merged_df.to_csv(existing_products, index=False, encoding='utf-8-sig')
        print(f"已保存合并后的产品到: {existing_products}")

except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
