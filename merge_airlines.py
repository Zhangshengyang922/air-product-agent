#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并9H和BK航司数据到products.csv"""

import pandas as pd
from pathlib import Path

def merge_new_airlines():
    base_path = Path(__file__).parent
    products_file = base_path / "assets" / "products.csv"
    
    # 读取现有products.csv
    df_products = pd.read_csv(products_file, encoding='utf-8-sig')
    
    # 读取9H数据
    df_9h = pd.read_csv(base_path / "assets" / "各航司汇总产品-9H长安.csv", encoding='utf-8-sig')
    df_9h['航司代码'] = '9H'
    df_9h['航司名称'] = '桂林航空'
    # 重命名列以匹配products.csv格式
    df_9h = df_9h.rename(columns={
        '上浮/下浮价格': '上浮价格',
    })
    
    # 读取BK数据
    df_bk = pd.read_csv(base_path / "assets" / "各航司汇总产品-BK奥凯.csv", encoding='utf-8-sig')
    df_bk['航司代码'] = 'BK'
    df_bk['航司名称'] = '奥凯航空'
    
    # 定义products.csv的标准列顺序
    standard_cols = ['航司代码', '航司名称', '产品名称', '航线', '订座舱位', '上浮价格', 
                     '政策返点', '产品代码', '出票OFFICE', '备注', '航司结算方式', '产品有限期']
    
    # 为新数据添加缺失列
    for col in standard_cols:
        if col not in df_9h.columns:
            df_9h[col] = ''
        if col not in df_bk.columns:
            df_bk[col] = ''
    
    # 确保列顺序一致
    df_9h = df_9h[standard_cols]
    df_bk = df_bk[standard_cols]
    
    # 过滤掉空产品行（产品名称为空）
    df_9h = df_9h[df_9h['产品名称'].notna() & (df_9h['产品名称'] != '')]
    df_bk = df_bk[df_bk['产品名称'].notna() & (df_bk['产品名称'] != '')]
    
    # 合并所有数据
    df_combined = pd.concat([df_products, df_9h, df_bk], ignore_index=True)
    
    # 保存
    df_combined.to_csv(products_file, index=False, encoding='utf-8-sig')
    print(f"合并完成！共 {len(df_combined)} 行数据")
    print(f"- 原有产品: {len(df_products)} 行")
    print(f"- 新增9H: {len(df_9h)} 行")
    print(f"- 新增BK: {len(df_bk)} 行")

if __name__ == "__main__":
    merge_new_airlines()
