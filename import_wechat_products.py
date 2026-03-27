# -*- coding: utf-8 -*-
"""
CSV产品数据导入工具
用于将exported_from_wechat.csv的数据导入到系统
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRODUCTS_CSV = ASSETS_DIR / "products.csv"
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"
BACKUP_DIR = PROJECT_ROOT / "assets" / "backups"


def backup_current_products():
    """备份当前产品数据"""
    if not PRODUCTS_CSV.exists():
        print("ℹ️  产品文件不存在，跳过备份")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"products_backup_{timestamp}.csv"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PRODUCTS_CSV, backup_path)
        print(f"✅ 已备份现有产品到: {backup_name}")
        return backup_path
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None


def read_csv_file(csv_path: Path):
    """读取CSV文件"""
    if not csv_path.exists():
        print(f"❌ 文件不存在: {csv_path}")
        return []
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            print(f"✅ 读取成功: {len(data)} 条记录")
            return data
    except UnicodeDecodeError:
        # 尝试其他编码
        for encoding in ['gbk', 'gb2312', 'utf-8']:
            try:
                with open(csv_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                    print(f"✅ 读取成功 ({encoding}): {len(data)} 条记录")
                    return data
            except Exception:
                continue
        print(f"❌ 无法读取文件，尝试了多种编码")
        return []
    except Exception as e:
        print(f"❌ 读取CSV失败: {e}")
        return []


def normalize_csv_data(data: list, source: str):
    """标准化CSV数据格式"""
    print(f"\n📊 数据统计 ({source}):")
    
    # 统计信息
    total_rows = len(data)
    valid_rows = 0
    invalid_rows = 0
    
    # 字段标准化映射
    standardized = []
    
    for idx, row in enumerate(data, 1):
        # 跳过空行
        if not any(row.values()):
            invalid_rows += 1
            continue
        
        # 检查必需字段
        product_name = row.get('产品名称', '').strip()
        airline = row.get('产品代码', '').strip()
        
        if not product_name:
            invalid_rows += 1
            continue
        
        # 提取航空公司代码 (从产品名称第一个字段)
        import re
        match = re.match(r'^([A-Z]{2,3})', product_name)
        if match:
            airline_code = match.group(1)
        else:
            # 从产品代码中提取
            if airline.startswith('*'):
                airline_code = airline[1:4].upper() if len(airline) > 4 else airline[1:].upper()
            else:
                airline_code = 'CZ'  # 默认南航
        
        # 标准化产品数据
        normalized_product = {
            'airline': airline_code,
            'product_name': product_name,
            'route': row.get('航线', '').strip(),
            'booking_class': row.get('订座舱位', '').strip(),
            'price_increase': row.get('上浮价格', '0').strip(),
            'rebate_ratio': row.get('政策返点（后返+车辆后返+代理费)', '').strip(),
            'policy_code': row.get('产品代码', '').strip(),
            'ticket_type': row.get('票证类型', 'ALL').strip(),
            'office': row.get('出票OFFICE', '').strip(),
            'remarks': row.get('备注', '').strip(),
            'valid_period': row.get('产品有限期', '').strip()
        }
        
        standardized.append(normalized_product)
        valid_rows += 1
    
    print(f"  总行数: {total_rows}")
    print(f"  有效行数: {valid_rows}")
    print(f"  无效行数: {invalid_rows}")
    
    # 按航空公司统计
    airline_stats = {}
    for product in standardized:
        airline = product['airline']
        airline_stats[airline] = airline_stats.get(airline, 0) + 1
    
    print(f"\n✈️  航空公司分布:")
    for airline, count in sorted(airline_stats.items()):
        print(f"  {airline}: {count} 个产品")
    
    return standardized


def merge_csv_data(existing_data: list, new_data: list):
    """合并现有数据和新数据"""
    print(f"\n🔄 合并数据...")
    print(f"  现有数据: {len(existing_data)} 条")
    print(f"  新增数据: {len(new_data)} 条")
    
    # 合并策略：追加新数据
    merged_data = existing_data + new_data
    
    print(f"  合并后: {len(merged_data)} 条")
    return merged_data


def save_csv_data(data: list, csv_path: Path):
    """保存CSV数据"""
    try:
        # 创建备份目录
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 定义CSV字段
        fieldnames = [
            'airline', 'product_name', 'route', 'booking_class',
            'price_increase', 'rebate_ratio', 'policy_code',
            'ticket_type', 'office', 'remarks', 'valid_period'
        ]
        
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ 数据已保存到: {csv_path}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("🚀 CSV产品数据导入工具")
    print("=" * 80)
    print()
    
    # 1. 检查文件是否存在
    print("📋 步骤 1/5: 检查文件")
    print(f"  导出文件: {EXPORTED_CSV}")
    print(f"  产品文件: {PRODUCTS_CSV}")
    print()
    
    if not EXPORTED_CSV.exists():
        print(f"❌ 导出文件不存在: {EXPORTED_CSV}")
        print(f"\n💡 请确保 exported_from_wechat.csv 文件在项目根目录")
        return False
    
    # 2. 备份现有数据
    print("📋 步骤 2/5: 备份现有数据")
    backup_path = backup_current_products()
    print()
    
    # 3. 读取导出数据
    print("📋 步骤 3/5: 读取导出数据")
    exported_data = read_csv_file(EXPORTED_CSV)
    if not exported_data:
        print("❌ 无法读取导出数据")
        return False
    print()
    
    # 4. 标准化导出数据
    print("📋 步骤 4/5: 标准化数据")
    normalized_exported = normalize_csv_data(exported_data, "导出文件")
    print()
    
    # 5. 读取并合并现有数据
    print("📋 步骤 5/5: 合并并保存数据")
    
    if PRODUCTS_CSV.exists():
        existing_data = read_csv_file(PRODUCTS_CSV)
        if existing_data:
            normalized_existing = normalize_csv_data(existing_data, "现有文件")
            merged_data = merge_csv_data(normalized_existing, normalized_exported)
        else:
            merged_data = normalized_exported
    else:
        merged_data = normalized_exported
    
    # 6. 保存合并后的数据
    success = save_csv_data(merged_data, PRODUCTS_CSV)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ 产品数据导入成功!")
        print("=" * 80)
        print()
        print("📋 统计信息:")
        print(f"  总产品数: {len(merged_data)}")
        print()
        print("📝 下一步:")
        print("  1. 访问 http://localhost:5000")
        print("  2. 登录系统 (用户名: YNTB, 密码: yntb123)")
        print("  3. 刷新页面查看新产品")
        print()
        if backup_path:
            print(f"💾 备份文件位置: {backup_path}")
        print()
        
        # 触发文件监控通知
        print("🔄 文件监控会自动检测到变化并更新系统...")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ 产品数据导入失败!")
        print("=" * 80)
        return False


if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
