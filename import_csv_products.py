#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV产品数据导入工具
支持从桌面或其他位置导入CSV文件到系统
"""

import os
import csv
import shutil
from pathlib import Path
from datetime import datetime


def import_csv_to_products(source_csv_path: str, target_products_csv: str):
    """
    导入CSV产品数据到系统

    Args:
        source_csv_path: 源CSV文件路径
        target_products_csv: 目标products.csv路径
    """
    source_path = Path(source_csv_path)
    target_path = Path(target_products_csv)

    if not source_path.exists():
        print(f"错误: 源文件不存在 - {source_path}")
        return False

    try:
        # 备份现有数据
        if target_path.exists():
            backup_name = f"products_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            backup_path = target_path.parent / backup_name
            shutil.copy2(target_path, backup_path)
            print(f"已备份现有数据到: {backup_name}")

        # 读取源文件
        print(f"正在读取源文件: {source_path}")
        with open(source_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            source_data = list(reader)

        print(f"源文件包含 {len(source_data)} 条记录")

        # 写入目标文件
        print(f"正在写入目标文件: {target_path}")
        with open(target_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=source_data[0].keys() if source_data else [])
            writer.writeheader()
            writer.writerows(source_data)

        print(f"✅ 成功导入 {len(source_data)} 条产品记录")

        # 显示前3条记录作为预览
        if source_data:
            print("\n前3条记录预览:")
            for i, record in enumerate(source_data[:3]):
                print(f"\n记录 {i+1}:")
                for key, value in list(record.items())[:5]:  # 只显示前5个字段
                    print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def main():
    print("=" * 60)
    print("CSV产品数据导入工具")
    print("=" * 60)

    # 默认路径
    project_root = Path(__file__).parent
    default_source = Path.home() / "OneDrive" / "桌面" / "各航司汇总产品-CZ.csv"
    default_target = project_root / "assets" / "products.csv"

    print(f"\n默认源文件: {default_source}")
    print(f"默认目标文件: {default_target}")
    print()

    # 使用默认路径
    source_csv = input(f"请输入源CSV文件路径 (直接回车使用默认路径): ").strip()
    if not source_csv:
        source_csv = str(default_source)

    target_csv = input(f"请输入目标products.csv路径 (直接回车使用默认路径): ").strip()
    if not target_csv:
        target_csv = str(default_target)

    print("\n即将执行以下操作:")
    print(f"源文件: {source_csv}")
    print(f"目标文件: {target_csv}")
    print(f"操作类型: 替换现有数据")
    print()

    confirm = input("确认执行? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消操作")
        return

    # 执行导入
    success = import_csv_to_products(source_csv, target_csv)

    if success:
        print("\n" + "=" * 60)
        print("导入完成！")
        print("提示: 请重启项目服务以加载新数据")
        print("=" * 60)


if __name__ == "__main__":
    main()
