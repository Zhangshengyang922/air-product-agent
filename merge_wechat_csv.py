# -*- coding: utf-8 -*-
"""
CSV产品数据合并工具
用于将导出的微信产品数据合并到现有产品数据库
"""

import csv
import os
import shutil
from pathlib import Path
from datetime import datetime

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRODUCTS_CSV = ASSETS_DIR / "products.csv"
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"
BACKUP_DIR = ASSETS_DIR / "backups"

# 确保备份目录存在
BACKUP_DIR.mkdir(exist_ok=True)

# 数据库字段映射
FIELD_MAPPINGS = {
    "产品名称": "product_name",
    "航线": "route",
    "订座舱位": "booking_class",
    "上浮价格": "price_increase",
    "政策返点（后返+车辆后返+代理费)": "rebate_ratio",
    "产品代码": "policy_code",
    "票证类型": "ticket_type",
    "出票OFFICE": "office",
    "备注": "remarks",
    "产品有限期": "valid_period"
}


def read_csv_file(file_path: Path) -> list:
    """读取CSV文件并返回数据列表"""
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return [row for row in reader if any(row.values())]  # 过滤空行
    except Exception as e:
        print(f"❌ 读取CSV文件失败 {file_path}: {e}")
        return []


def backup_current_products():
    """备份当前产品数据"""
    if not PRODUCTS_CSV.exists():
        print("⚠️ 当前产品文件不存在，无需备份")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"products_backup_{timestamp}.csv"
    
    try:
        shutil.copy2(PRODUCTS_CSV, backup_file)
        print(f"✅ 已备份现有产品到: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None


def normalize_product(product: dict, field_mappings: dict) -> dict:
    """标准化产品数据格式"""
    normalized = {}
    
    for chinese_field, english_field in field_mappings.items():
        value = product.get(chinese_field, '').strip()
        if value:
            normalized[english_field] = value
    
    # 添加航空公司代码（从产品名称提取）
    product_name = product.get('产品名称', '').strip()
    if product_name:
        # 提取航空公司代码（如CZ、MU等）
        import re
        match = re.match(r'^([A-Z]{2})', product_name)
        if match:
            normalized['airline'] = match.group(1)
        else:
            normalized['airline'] = 'CZ'  # 默认南航
    
    # 添加其他必需字段
    normalized.setdefault('airline', 'CZ')
    normalized.setdefault('ticket_type', 'ALL')
    normalized.setdefault('remarks', '')
    normalized.setdefault('valid_period', '')
    
    return normalized


def merge_products(existing_products: list, exported_products: list) -> list:
    """合并产品数据，去重处理"""
    print(f"📊 现有产品数: {len(existing_products)}")
    print(f"📊 导入产品数: {len(exported_products)}")
    
    # 创建产品唯一标识字典
    product_map = {}
    
    # 先添加现有产品
    for product in existing_products:
        key = f"{product.get('airline', '')}_{product.get('route', '')}_{product.get('booking_class', '')}_{product.get('policy_code', '')}"
        product_map[key] = product
    
    # 添加或更新导入的产品
    added_count = 0
    updated_count = 0
    
    for product in exported_products:
        normalized = normalize_product(product, FIELD_MAPPINGS)
        key = f"{normalized.get('airline', '')}_{normalized.get('route', '')}_{normalized.get('booking_class', '')}_{normalized.get('policy_code', '')}"
        
        if key in product_map:
            # 更新现有产品
            product_map[key] = normalized
            updated_count += 1
        else:
            # 添加新产品
            product_map[key] = normalized
            added_count += 1
    
    merged_products = list(product_map.values())
    
    print(f"📊 合并后产品总数: {len(merged_products)}")
    print(f"✅ 新增产品: {added_count}")
    print(f"✅ 更新产品: {updated_count}")
    
    return merged_products


def save_products(products: list):
    """保存产品数据到CSV文件"""
    ASSETS_DIR.mkdir(exist_ok=True)
    
    # 准备字段列表
    field_names = ['airline', 'product_name', 'route', 'booking_class', 
                  'price_increase', 'rebate_ratio', 'policy_code', 
                  'ticket_type', 'office', 'remarks', 'valid_period']
    
    try:
        with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"✅ 成功保存 {len(products)} 个产品到: {PRODUCTS_CSV}")
        return True
    except Exception as e:
        print(f"❌ 保存产品文件失败: {e}")
        return False


def analyze_products(products: list):
    """分析产品数据统计"""
    if not products:
        print("❌ 没有产品数据")
        return
    
    # 按航空公司统计
    airline_stats = {}
    # 按航线统计  
    route_stats = {}
    # 按票证类型统计
    ticket_type_stats = {}
    
    for product in products:
        airline = product.get('airline', 'CZ')
        airline_stats[airline] = airline_stats.get(airline, 0) + 1
        
        route = product.get('route', '')[:30]  # 只取前30个字符
        if route:
            route_stats[route] = route_stats.get(route, 0) + 1
        
        ticket_type = product.get('ticket_type', 'ALL')
        ticket_type_stats[ticket_type] = ticket_type_stats.get(ticket_type, 0) + 1
    
    print("\n📈 产品统计信息:")
    print("=" * 80)
    
    print(f"\n🈷️  按航空公司统计:")
    for airline, count in sorted(airline_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {airline}: {count} 个产品")
    
    print(f"\n✈️  主要航线 (前10条):")
    for route, count in sorted(route_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {route}: {count} 个产品")
    
    print(f"\n🎫 按票证类型统计:")
    for ticket_type, count in sorted(ticket_type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ticket_type}: {count} 个产品")
    
    print("=" * 80)


def main():
    """主函数"""
    print("=" * 80)
    print("🚀 CSV产品数据合并工具")
    print("=" * 80)
    print()
    
    # 读取现有产品数据
    print("📖 读取现有产品数据...")
    existing_products = read_csv_file(PRODUCTS_CSV)
    
    # 读取导入的产品数据
    print("📖 读取导出的产品数据...")
    exported_products = read_csv_file(EXPORTED_CSV)
    
    if not exported_products:
        print("❌ 没有找到导入的产品数据，程序终止")
        return False
    
    # 备份现有数据
    print("\n💾 备份现有产品数据...")
    backup_file = backup_current_products()
    
    # 合并产品数据
    print("\n🔄 合并产品数据...")
    merged_products = merge_products(existing_products, exported_products)
    
    # 保存合并后的数据
    print("\n💾 保存合并后的产品数据...")
    if save_products(merged_products):
        # 分析统计信息
        analyze_products(merged_products)
        
        print("\n" + "=" * 80)
        print("✅ 产品数据合并完成!")
        print("=" * 80)
        print("\n📝 后续步骤:")
        print("  1. 产品数据已更新到 assets/products.csv")
        print("  2. 系统会自动检测文件变化并重新加载数据")
        print("  3. 刷新浏览器页面查看更新后的产品信息")
        print("  4. 如需查看产品统计，访问 http://localhost:5000/api/stats")
        print("\n💾 备份文件位置:")
        if backup_file:
            print(f"  {backup_file}")
        print("\n" + "=" * 80)
        return True
    else:
        print("\n❌ 产品数据合并失败!")
        return False


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n程序执行失败，请检查错误信息")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
