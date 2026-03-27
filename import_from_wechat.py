#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业微信CSV文件导入工具
用于将exported_from_wechat.csv的数据导入到系统
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime
import sys

# 项目路径
PROJECT_ROOT = Path(__file__).parent
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"
PRODUCTS_CSV = PROJECT_ROOT / "assets" / "products.csv"
BACKUP_DIR = PROJECT_ROOT / "backups"

def backup_current_products():
    """备份当前产品文件"""
    if not PRODUCTS_CSV.exists():
        print("⚠️ 当前产品文件不存在，无需备份")
        return None
    
    # 确保备份目录存在
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # 创建备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"products_backup_{timestamp}.csv"
    
    try:
        shutil.copy2(PRODUCTS_CSV, backup_file)
        print(f"✅ 已备份现有产品到: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def read_and_merge_csvs():
    """读取并合并CSV文件"""
    
    # 检查导出文件是否存在
    if not EXPORTED_CSV.exists():
        print(f"❌ 导出文件不存在: {EXPORTED_CSV}")
        print(f"请确保已将文件命名为 'exported_from_wechat.csv' 并放在项目根目录")
        return False
    
    print(f"📂 正在读取导出文件: {EXPORTED_CSV}")
    
    # 读取导出文件
    try:
        with open(EXPORTED_CSV, 'r', encoding='utf-8-sig') as f:
            exported_reader = csv.DictReader(f)
            exported_data = list(exported_reader)
            print(f"✅ 读取导出文件成功，共 {len(exported_data)} 行数据")
    except Exception as e:
        print(f"❌ 读取导出文件失败: {e}")
        return False
    
    # 读取现有产品文件
    existing_data = []
    if PRODUCTS_CSV.exists():
        try:
            with open(PRODUCTS_CSV, 'r', encoding='utf-8-sig') as f:
                existing_reader = csv.DictReader(f)
                existing_data = list(existing_reader)
                print(f"✅ 读取现有产品文件成功，共 {len(existing_data)} 行数据")
        except Exception as e:
            print(f"❌ 读取现有产品文件失败: {e}")
            return False
    
    # 合并数据
    print(f"\n📊 数据统计:")
    print(f"  导出文件: {len(exported_data)} 行")
    print(f"  现有数据: {len(existing_data)} 行")
    
    # 去除空行
    exported_data = [row for row in exported_data if any(row.values())]
    existing_data = [row for row in existing_data if any(row.values())]
    
    # 检查重复
    existing_keys = set()
    for row in existing_data:
        key = f"{row.get('产品名称', '')}_{row.get('航线', '')}_{row.get('产品代码', '')}"
        existing_keys.add(key)
    
    # 筛选出新数据
    new_data = []
    for i, row in enumerate(exported_data, 1):
        key = f"{row.get('产品名称', '')}_{row.get('航线', '')}_{row.get('产品代码', '')}"
        if key not in existing_keys:
            new_data.append(row)
        else:
            print(f"  ⚠️ 第{i}行: 重复数据，已跳过")
    
    print(f"\n🆕 新增数据: {len(new_data)} 行")
    print(f"🔄 合并后总计: {len(existing_data) + len(new_data)} 行")
    
    # 合并数据
    merged_data = existing_data + new_data
    
    # 保存到产品文件
    try:
        with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            if merged_data:
                fieldnames = merged_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(merged_data)
        
        print(f"\n✅ 成功保存 {len(merged_data)} 行数据到: {PRODUCTS_CSV}")
        return True
    except Exception as e:
        print(f"❌ 保存产品文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("企业微信CSV产品数据导入工具")
    print("=" * 80)
    print()
    
    # 显示文件信息
    print("📁 文件路径:")
    print(f"  导出文件: {EXPORTED_CSV}")
    print(f"  产品文件: {PRODUCTS_CSV}")
    print(f"  备份目录: {BACKUP_DIR}")
    print()
    
    # 检查导出文件
    if not EXPORTED_CSV.exists():
        print("❌ 导出文件不存在!")
        print(f"请确保文件 '{EXPORTED_CSV.name}' 存在于项目根目录")
        print()
        print("操作步骤:")
        print("1. 打开企业微信在线文档")
        print("2. 点击'文件' → '导出' → 选择 'CSV' 格式")
        print("3. 将导出的文件重命名为 'exported_from_wechat.csv'")
        print("4. 将文件移动到项目根目录")
        print("5. 重新运行此脚本")
        return False
    
    # 确认操作
    print("即将执行以下操作:")
    print("  1. 备份当前产品文件")
    print("  2. 读取导出的CSV文件")
    print("  3. 合并新旧数据")
    print("  4. 保存到产品文件")
    print()
    
    confirm = input("确认继续? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消操作")
        return False
    
    print()
    print("=" * 80)
    
    # 执行备份
    backup_file = backup_current_products()
    if backup_file is None and PRODUCTS_CSV.exists():
        print("❌ 备份失败，操作中止")
        return False
    
    # 执行导入
    success = read_and_merge_csvs()
    
    print()
    print("=" * 80)
    
    if success:
        print("✅ 导入成功!")
        print()
        print("后续步骤:")
        print("1. 确保Web服务正在运行")
        print("2. 访问 http://localhost:5000")
        print("3. 刷新页面查看新产品")
        print("4. 如果数据未更新，重启服务")
        print()
        print("注意:")
        print(f"  备份文件保存在: {backup_file}")
    else:
        print("❌ 导入失败!")
        print("请检查错误信息并重试")
    
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
