#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新东航产品数据
"""

import pandas as pd
import os
from pathlib import Path

def update_mu_products():
    # 文件路径
    project_root = Path(__file__).parent
    main_file = project_root / "assets" / "products.csv"
    mu_update_file = project_root / "exported_from_wechat-MU.csv"
    backup_file = project_root / "assets" / f"products_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print("=" * 60)
    print("东航产品数据更新工具")
    print("=" * 60)

    # 备份原文件
    if main_file.exists():
        import shutil
        shutil.copy2(main_file, backup_file)
        print(f"[OK] 已备份原文件到: {backup_file.name}")

    # 读取主数据文件
    print("\n[INFO] 读取主数据文件...")
    main_df = pd.read_csv(main_file, encoding='utf-8-sig')

    # 统计原有数据
    original_count = len(main_df)
    original_mu_count = len(main_df[main_df['航司代码'] == 'MU'])

    print(f"[INFO] 主文件总数据: {original_count} 条")
    print(f"[INFO] 原有东航(MU)数据: {original_mu_count} 条")

    # 读取东航更新文件
    print("\n[INFO] 读取东航更新文件...")
    mu_df = pd.read_csv(mu_update_file, encoding='utf-8-sig')

    print(f"[INFO] 东航更新文件数据: {len(mu_df)} 条")

    # 删除多余的列
    if 'Unnamed: 9' in mu_df.columns:
        mu_df = mu_df.drop(columns=['Unnamed: 9'])

    # 添加缺失的列并设置默认值
    required_columns = ['航司代码', '航司名称', '产品名称', '航线', '订座舱位', '上浮价格',
                    '政策返点', '产品代码', '出票OFFICE', '备注', '产品有限期']

    # 添加航司代码
    mu_df['航司代码'] = 'MU'
    mu_df['航司名称'] = '东航'

    # 确保所有列都存在
    for col in required_columns:
        if col not in mu_df.columns:
            mu_df[col] = ''

    # 重新排列列顺序
    mu_df = mu_df[required_columns]

    # 删除主文件中的MU数据
    print("\n[INFO] 删除主文件中的原有东航数据...")
    main_df = main_df[main_df['航司代码'] != 'MU']

    # 合并新数据
    print("[INFO] 合并新的东航数据...")
    updated_df = pd.concat([main_df, mu_df], ignore_index=True)

    # 统计更新后数据
    updated_count = len(updated_df)
    updated_mu_count = len(updated_df[updated_df['航司代码'] == 'MU'])

    print(f"\n[INFO] 更新后总数据: {updated_count} 条")
    print(f"[INFO] 新东航(MU)数据: {updated_mu_count} 条")
    print(f"[INFO] 新增东航数据: {updated_mu_count - original_mu_count} 条")

    # 保存更新后的数据
    print("\n[INFO] 保存更新后的数据...")
    updated_df.to_csv(main_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 数据更新成功! 已保存到: {main_file}")

    # 显示各航司数据分布
    print("\n[INFO] 各航司数据分布:")
    airline_stats = updated_df.groupby('航司代码').size().sort_values(ascending=False)
    for airline, count in airline_stats.items():
        print(f"  {airline}: {count} 条")

    print("\n" + "=" * 60)
    print("更新完成!")
    print("=" * 60)

if __name__ == "__main__":
    update_mu_products()
