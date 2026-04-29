#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并各航司数据到products.csv"""

import pandas as pd
from pathlib import Path

def merge_new_airlines():
    base_path = Path(__file__).parent
    products_file = base_path / "assets" / "products.csv"
    
    # 读取现有products.csv
    df_products = pd.read_csv(products_file, encoding='utf-8-sig')
    print(f"原products.csv: {len(df_products)} 行")
    
    # 定义products.csv的标准列顺序
    standard_cols = ['航司代码', '航司名称', '产品名称', '航线', '订座舱位', '上浮价格', 
                     '政策返点', '产品代码', '出票OFFICE', '备注', '航司结算方式', '产品有限期', '司结算方式', '票证类型']
    
    # 确保原有数据有这些列
    for col in standard_cols:
        if col not in df_products.columns:
            df_products[col] = ''
    
    # 处理MU航司
    mu_file = base_path / "各航司汇总产品-MU.csv"
    if mu_file.exists():
        print(f"\n处理MU数据...")
        df_mu = pd.read_csv(mu_file, encoding='utf-8-sig')
        df_mu['航司代码'] = 'MU'
        df_mu['航司名称'] = '东航'
        # MU的CSV列名和products.csv不同，需要映射
        col_mapping = {
            '上浮价格': '上浮价格',
        }
        df_mu = df_mu.rename(columns=col_mapping)
        # 添加缺失列
        for col in standard_cols:
            if col not in df_mu.columns:
                df_mu[col] = ''
        df_mu = df_mu[standard_cols]
        # 过滤空行
        df_mu = df_mu[df_mu['产品名称'].notna() & (df_mu['产品名称'] != '')]
        print(f"  - MU新数据: {len(df_mu)} 行")
        
        # 删除旧的MU数据，添加新的
        df_products = df_products[df_products['航司代码'] != 'MU']
        print(f"  - 删除旧MU后: {len(df_products)} 行")
        
        df_products = pd.concat([df_products, df_mu], ignore_index=True)
        print(f"  - 合并后: {len(df_products)} 行")
    
    # 处理9H数据
    df_9h = pd.read_csv(base_path / "assets" / "各航司汇总产品-9H长安.csv", encoding='utf-8-sig')
    df_9h['航司代码'] = '9H'
    df_9h['航司名称'] = '长安航空'
    df_9h = df_9h.rename(columns={'上浮/下浮价格': '上浮价格'})
    for col in standard_cols:
        if col not in df_9h.columns:
            df_9h[col] = ''
    df_9h = df_9h[standard_cols]
    df_9h = df_9h[df_9h['产品名称'].notna() & (df_9h['产品名称'] != '')]
    
    # 处理BK数据
    df_bk = pd.read_csv(base_path / "assets" / "各航司汇总产品-BK奥凯.csv", encoding='utf-8-sig')
    df_bk['航司代码'] = 'BK'
    df_bk['航司名称'] = '奥凯航空'
    for col in standard_cols:
        if col not in df_bk.columns:
            df_bk[col] = ''
    df_bk = df_bk[standard_cols]
    df_bk = df_bk[df_bk['产品名称'].notna() & (df_bk['产品名称'] != '')]
    
    print(f"\n新增数据:")
    print(f"  - 9H: {len(df_9h)} 行")
    print(f"  - BK: {len(df_bk)} 行")
    
    # 删除旧数据（如果存在）
    df_products = df_products[~df_products['航司代码'].isin(['9H', 'BK'])]
    
    # 合并所有数据
    df_combined = pd.concat([df_products, df_9h, df_bk], ignore_index=True)
    
    # 保存
    df_combined.to_csv(products_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 合并完成！共 {len(df_combined)} 行数据")

if __name__ == "__main__":
    merge_new_airlines()
