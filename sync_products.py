#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
产品数据同步工具
将完整版的产品数据同步到智能体版本
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

class ProductSync:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.products_csv = self.project_root / "assets" / "products.csv"
        self.sync_status_file = self.project_root / "assets" / "sync_status.json"
        self.backup_dir = self.project_root / "assets" / "backups"

    def load_products(self):
        """加载产品数据"""
        if not self.products_csv.exists():
            return None
        return pd.read_csv(self.products_csv, encoding='utf-8-sig')

    def save_products(self, df):
        """保存产品数据"""
        # 创建备份
        if self.products_csv.exists():
            backup_file = self.backup_dir / f"products_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.backup_dir.mkdir(exist_ok=True)
            import shutil
            shutil.copy2(self.products_csv, backup_file)
            print(f"[OK] 已备份到: {backup_file.name}")

        # 保存数据
        df.to_csv(self.products_csv, index=False, encoding='utf-8-sig')
        print(f"[OK] 已保存产品数据: {len(df)} 条")

    def update_from_csv(self, csv_file_path):
        """从CSV文件更新产品数据"""
        print("=" * 60)
        print("产品数据同步工具")
        print("=" * 60)

        # 检查文件
        csv_file = Path(csv_file_path)
        if not csv_file.exists():
            print(f"[X] 文件不存在: {csv_file}")
            return False

        # 读取更新文件
        print(f"\n[INFO] 读取更新文件: {csv_file.name}")
        try:
            update_df = pd.read_csv(csv_file, encoding='utf-8-sig')
        except Exception as e:
            print(f"[X] 读取文件失败: {e}")
            return False

        print(f"[INFO] 更新文件包含 {len(update_df)} 条数据")
        print(f"[INFO] 列名: {update_df.columns.tolist()}")

        # 检查是否有航司代码列
        if '航司代码' not in update_df.columns:
            print("\n[INFO] 检测到缺少航司代码列")

            # 检查是否从企业微信导出的单航司文件
            # 根据产品名称推断航司代码
            airline_code = self.detect_airline_from_file(csv_file)
            if airline_code:
                print(f"[INFO] 检测到航司: {airline_code}")
                update_df['航司代码'] = airline_code
                update_df['航司名称'] = self.get_airline_name(airline_code)
            else:
                print("[X] 无法识别航司代码")
                return False

        # 清理数据：删除多余列
        required_columns = ['航司代码', '航司名称', '产品名称', '航线', '订座舱位', 
                          '上浮价格', '政策返点', '产品代码', '出票OFFICE', '备注', '产品有限期']
        
        # 添加缺失的列
        for col in required_columns:
            if col not in update_df.columns:
                update_df[col] = ''

        # 删除多余的列
        update_df = update_df[required_columns]

        # 读取现有数据
        print("\n[INFO] 读取现有产品数据...")
        existing_df = self.load_products()

        if existing_df is None:
            print("[INFO] 首次导入，创建新数据库")
            self.save_products(update_df)
            self.update_sync_status("首次导入", len(update_df))
            return True

        print(f"[INFO] 现有数据: {len(existing_df)} 条")

        # 获取更新文件的航司代码
        updated_airlines = update_df['航司代码'].unique()
        print(f"[INFO] 更新的航司: {', '.join(updated_airlines)}")

        # 删除需要更新的航司数据
        print("\n[INFO] 删除待更新航司的旧数据...")
        for airline in updated_airlines:
            before_count = len(existing_df)
            existing_df = existing_df[existing_df['航司代码'] != airline]
            deleted_count = before_count - len(existing_df)
            print(f"[INFO] 删除 {airline}: {deleted_count} 条")

        # 合并新数据
        print("[INFO] 合并新数据...")
        updated_df = pd.concat([existing_df, update_df], ignore_index=True)

        # 统计各航司数据
        print(f"\n[INFO] 更新后总计: {len(updated_df)} 条")
        print("[INFO] 各航司数据分布:")
        airline_stats = updated_df.groupby('航司代码').size().sort_values(ascending=False)
        for airline, count in airline_stats.head(10).items():
            print(f"  {airline}: {count} 条")

        # 保存更新后的数据
        self.save_products(updated_df)

        # 更新同步状态
        self.update_sync_status(f"更新航司: {', '.join(updated_airlines)}", len(updated_df))

        print("\n" + "=" * 60)
        print("同步完成!")
        print("=" * 60)

        return True

    def detect_airline_from_file(self, csv_file):
        """从文件名或内容检测航司代码"""
        # 从文件名检测
        filename = csv_file.name.lower()
        if 'mu' in filename or '东航' in filename:
            return 'MU'
        elif 'cz' in filename or '南航' in filename:
            return 'CZ'
        elif '3u' in filename or '川航' in filename or '四川航空' in filename:
            return '3U'
        elif 'ca' in filename or '国航' in filename:
            return 'CA'
        elif 'hu' in filename or '海南航空' in filename:
            return 'HU'

        # 从产品名称检测
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        if '产品名称' in df.columns:
            first_product = df['产品名称'].iloc[0]
            if 'MU' in first_product or '东航' in first_product:
                return 'MU'
            elif 'CZ' in first_product or '南航' in first_product:
                return 'CZ'
            elif '3U' in first_product or '川航' in first_product or '四川航空' in first_product:
                return '3U'
            elif 'CA' in first_product or '国航' in first_product:
                return 'CA'
            elif 'HU' in first_product or '海南航空' in first_product:
                return 'HU'

        return None

    def get_airline_name(self, code):
        """获取航司名称"""
        names = {
            'MU': '东航', 'CZ': '南航', '3U': '四川航空', 'CA': '国航',
            'HU': '海南航空', 'MF': '厦门航空', 'EU': '成都航空', 'ZH': '深圳航空'
        }
        return names.get(code, code)

    def update_sync_status(self, operation, total_count):
        """更新同步状态"""
        status = {
            'last_sync_time': datetime.now().isoformat(),
            'operation': operation,
            'total_products': total_count,
            'airlines': list(pd.read_csv(self.products_csv, encoding='utf-8-sig')['航司代码'].unique())
        }

        with open(self.sync_status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)

        print(f"[OK] 已更新同步状态: {self.sync_status_file}")

    def get_sync_status(self):
        """获取同步状态"""
        if not self.sync_status_file.exists():
            return None

        with open(self.sync_status_file, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    sync = ProductSync()

    # 显示当前同步状态
    status = sync.get_sync_status()
    if status:
        print("\n当前同步状态:")
        print(f"  上次同步时间: {status['last_sync_time']}")
        print(f"  最后操作: {status['operation']}")
        print(f"  总产品数: {status['total_products']}")
        print(f"  航司数: {len(status['airlines'])}")
        print()

    # 检查是否有待同步的文件
    project_root = Path(__file__).parent
    csv_files = list(project_root.glob("exported_from_wechat-*.csv"))
    csv_files.extend(list(project_root.glob("*_products_*.csv")))

    if csv_files:
        print("发现待同步的文件:")
        for i, f in enumerate(csv_files, 1):
            print(f"  {i}. {f.name}")

        # 同步所有文件
        for csv_file in csv_files:
            print(f"\n正在同步: {csv_file.name}")
            if sync.update_from_csv(csv_file):
                print(f"[OK] {csv_file.name} 同步成功")
            else:
                print(f"[X] {csv_file.name} 同步失败")
    else:
        print("未发现待同步的文件")
        print("\n使用方法:")
        print("  python sync_products.py <csv文件路径>")
        print("\n或将企业微信导出的CSV文件放到项目根目录，文件名格式:")
        print("  exported_from_wechat-<航司代码>.csv")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        sync = ProductSync()
        sync.update_from_csv(csv_file)
    else:
        main()
