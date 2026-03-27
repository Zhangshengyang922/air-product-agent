#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品数据导入工具
将exported_from_wechat.csv的数据合并到assets/products.csv
"""

import csv
import shutil
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path(__file__).parent
PRODUCTS_CSV = PROJECT_ROOT / "assets" / "products.csv"
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"
BACKUP_DIR = PROJECT_ROOT / "assets" / "backups"

def backup_current_products():
    """备份当前产品文件"""
    if not PRODUCTS_CSV.exists():
        print("❌ 产品文件不存在，无需备份")
        return None
    
    # 创建备份目录
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"products_backup_{timestamp}.csv"
    
    try:
        shutil.copy2(PRODUCTS_CSV, backup_file)
        print(f"✅ 已备份当前产品文件到: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def read_csv_file(csv_path: Path):
    """读取CSV文件"""
    if not csv_path.exists():
        print(f"❌ 文件不存在: {csv_path}")
        return []
    
    products = []
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 跳过空行
                product_name = row.get('产品名称', '').strip()
                route = row.get('航线', '').strip()
                
                # 检查必填字段
                if product_name and route:
                    products.append(row)
        
        print(f"✅ 读取 {csv_path.name}: {len(products)} 条有效记录")
        return products
    except Exception as e:
        print(f"❌ 读取文件失败 {csv_path}: {e}")
        return []

def merge_products(existing_products, new_products):
    """合并产品数据，去重"""
    # 使用产品名称+航线+舱位作为唯一标识
    product_set = set()
    merged = []
    
    # 先添加新数据
    for product in new_products:
        key = f"{product.get('产品名称', '')}_{product.get('航线', '')}_{product.get('订座舱位', '')}"
        product_set.add(key)
        merged.append(product)
    
    # 添加旧数据中不重复的
    duplicate_count = 0
    for product in existing_products:
        key = f"{product.get('产品名称', '')}_{product.get('航线', '')}_{product.get('订座舱位', '')}"
        if key not in product_set:
            merged.append(product)
        else:
            duplicate_count += 1
    
    print(f"✅ 合并完成:")
    print(f"   新产品: {len(new_products)} 条")
    print(f"   保留旧产品: {len(existing_products) - duplicate_count} 条")
    print(f"   重复产品: {duplicate_count} 条")
    print(f"   合并后总计: {len(merged)} 条")
    
    return merged

def save_products(products):
    """保存产品数据到CSV文件"""
    if not products:
        print("❌ 没有数据可保存")
        return False
    
    try:
        # 确保目录存在
        PRODUCTS_CSV.parent.mkdir(parents=True, exist_ok=True)
        
        # 准备字段列表
        fieldnames = [
            '产品名称', '航线', '订座舱位', '上浮价格',
            '政策返点（后返+车辆后返+代理费)', '产品代码',
            '票证类型', '出票OFFICE', '备注', '产品有限期'
        ]
        
        # 写入CSV文件
        with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"✅ 已保存 {len(products)} 条产品数据到: {PRODUCTS_CSV}")
        return True
    except Exception as e:
        print(f"❌ 保存产品文件失败: {e}")
        return False

def show_statistics(products):
    """显示产品统计信息"""
    if not products:
        return
    
    print("\n" + "=" * 80)
    print("📊 产品数据统计")
    print("=" * 80)
    
    # 按航空公司统计
    airlines = {}
    for product in products:
        # 从产品名称中提取航空公司代码 (取前两个字符)
        product_name = product.get('产品名称', '').strip()
        airline = product_name[:2] if product_name else 'UNKNOWN'
        airlines[airline] = airlines.get(airline, 0) + 1
    
    print("\n✈️ 航空公司分布:")
    for airline, count in sorted(airlines.items()):
        print(f"   {airline:10s}: {count:4d} 个产品")
    
    # 按航线类型统计
    route_types = {}
    for product in products:
        route = product.get('航线', '').strip()
        if '云南' in route:
            route_type = '云南进出港'
        elif '全国' in route:
            route_type = '全国航线'
        elif '成都' in route:
            route_type = '成都进出港'
        elif '贵阳' in route:
            route_type = '贵阳进出港'
        elif '东海岸' in route:
            route_type = '东海岸代码'
        else:
            route_type = '其他航线'
        
        route_types[route_type] = route_types.get(route_type, 0) + 1
    
    print("\n🛤️ 航线类型分布:")
    for route_type, count in sorted(route_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {route_type:15s}: {count:4d} 个产品")
    
    # 按票证类型统计
    ticket_types = {}
    for product in products:
        ticket_type = product.get('票证类型', '').strip() or 'UNKNOW'
        ticket_types[ticket_type] = ticket_types.get(ticket_type, 0) + 1
    
    print("\n🎫 票证类型分布:")
    for ticket_type, count in sorted(ticket_types.items()):
        print(f"   {ticket_type:15s}: {count:4d} 个产品")
    
    print("=" * 80)

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 产品数据导入工具")
    print("=" * 80 + "\n")
    
    # 1. 读取导出的新数据
    print("步骤 1/4: 读取新导出的数据...")
    new_products = read_csv_file(EXPORTED_CSV)
    if not new_products:
        print("❌ 无法读取新数据，程序终止")
        return False
    
    # 2. 读取现有产品数据
    print("\n步骤 2/4: 读取现有产品数据...")
    existing_products = read_csv_file(PRODUCTS_CSV)
    
    # 3. 备份当前数据
    print("\n步骤 3/4: 备份当前产品文件...")
    backup_file = backup_current_products()
    
    # 4. 合并数据
    print("\n步骤 4/4: 合并数据并保存...")
    merged_products = merge_products(existing_products, new_products)
    
    # 5. 保存合并后的数据
    success = save_products(merged_products)
    
    if success:
        # 6. 显示统计信息
        show_statistics(merged_products)
        
        print("\n" + "=" * 80)
        print("✅ 数据导入成功！")
        print("=" * 80)
        print(f"\n💡 提示:")
        print(f"   1. 系统会自动检测到文件变化并重新加载数据")
        print(f"   2. 您可以刷新浏览器页面查看更新后的产品数据")
        print(f"   3. 备份文件位置: {backup_file}")
        print(f"\n📁 数据文件: {PRODUCTS_CSV}")
        print("=" * 80)
        
        return True
    else:
        print("\n❌ 数据导入失败！")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
