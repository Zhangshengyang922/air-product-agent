# -*- coding: utf-8 -*-
"""
产品信息检索和重新上传工具
用于重新检索产品信息并上传到系统
"""

import os
import csv
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRODUCTS_CSV = ASSETS_DIR / "products.csv"
BACKUP_DIR = ASSETS_DIR / "backups"

# API配置
API_BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{API_BASE_URL}/api/login"
PRODUCTS_API = f"{API_BASE_URL}/api/products"
UPLOAD_PRODUCTS_API = f"{API_BASE_URL}/api/upload/products"

# 登录凭据
USERNAME = "YNTB"
PASSWORD = "yntb123"


class ProductUploader:
    """产品上传器"""
    
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.uploaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
    def login(self) -> bool:
        """登录系统获取token"""
        try:
            response = self.session.post(LOGIN_URL, json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
                    print(f"✅ 登录成功，Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 登录请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def load_csv_products(self, csv_file_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """从CSV文件加载产品数据"""
        if csv_file_path is None:
            csv_file_path = PRODUCTS_CSV
        
        if not csv_file_path.exists():
            print(f"❌ CSV文件不存在: {csv_file_path}")
            return []
        
        products = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # 跳过空行
                for i, row in enumerate(reader, 1):
                    # 检查必填字段
                    product_name = row.get('产品名称', '').strip()
                    route = row.get('航线', '').strip()
                    
                    if not product_name or not route:
                        self.skipped_count += 1
                        continue
                    
                    # 转换为标准格式
                    product = self.convert_csv_to_standard_format(row)
                    products.append(product)
            
            print(f"📊 从CSV文件加载了 {len(products)} 个产品 (跳过 {self.skipped_count} 个无效行)")
            return products
            
        except Exception as e:
            print(f"❌ 读取CSV文件失败: {str(e)}")
            return []
    
    def convert_csv_to_standard_format(self, csv_row: Dict[str, str]) -> Dict[str, Any]:
        """将CSV行转换为标准产品格式"""
        # 从产品名称中提取航空公司代码 (第一个中文字符前的字母)
        product_name = csv_row.get('产品名称', '').strip()
        airline = "CZ"  # 默认南航
        
        if product_name:
            # 尝试从产品名称中提取航空公司代码
            import re
            match = re.match(r'^([A-Z]+)', product_name)
            if match:
                airline = match.group(1)
        
        return {
            "airline": airline,
            "product_name": product_name,
            "route": csv_row.get('航线', '').strip(),
            "booking_class": csv_row.get('订座舱位', '').strip(),
            "price_increase": csv_row.get('上浮价格', '').strip(),
            "rebate_ratio": csv_row.get('政策返点（后返+车辆后返+代理费)', '').strip(),
            "office": csv_row.get('出票OFFICE', '').strip(),
            "remarks": csv_row.get('备注', '').strip(),
            "valid_period": csv_row.get('产品有限期', '').strip(),
            "ticket_type": csv_row.get('票证类型', 'ALL').strip(),
            "policy_identifier": csv_row.get('产品代码', '').strip(),
            "policy_code": csv_row.get('产品代码', '').strip()
        }
    
    def upload_products_via_api(self, products: List[Dict[str, Any]]) -> bool:
        """通过API上传产品"""
        if not self.token:
            print("❌ 未登录，无法上传")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            # 批量上传产品
            batch_size = 50
            total_batches = (len(products) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(products))
                batch_products = products[start_idx:end_idx]
                
                print(f"📤 正在上传第 {batch_num + 1}/{total_batches} 批 ({len(batch_products)} 个产品)...")
                
                # 准备CSV格式的数据
                import io
                output = io.StringIO()
                fieldnames = ['airline', 'product_name', 'route', 'booking_class',
                            'price_increase', 'rebate_ratio', 'office', 'remarks',
                            'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(batch_products)
                
                # 准备文件上传
                files = {
                    'file': ('products_batch.csv', output.getvalue().encode('utf-8-sig'), 'text/csv')
                }
                
                response = self.session.post(
                    UPLOAD_PRODUCTS_API,
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        added_count = result.get('data', {}).get('added_products', 0)
                        skipped_count = result.get('data', {}).get('skipped_products', 0)
                        self.uploaded_count += added_count
                        self.failed_count += skipped_count
                        print(f"   ✅ 成功上传 {added_count} 个产品 (跳过 {skipped_count} 个)")
                    else:
                        print(f"   ❌ 上传失败: {result.get('message')}")
                        self.failed_count += len(batch_products)
                else:
                    print(f"   ❌ 上传请求失败，状态码: {response.status_code}")
                    print(f"   响应: {response.text}")
                    self.failed_count += len(batch_products)
            
            return True
            
        except Exception as e:
            print(f"❌ 上传产品异常: {str(e)}")
            return False
    
    def get_current_products(self) -> List[Dict[str, Any]]:
        """获取当前系统中的产品列表"""
        if not self.token:
            print("❌ 未登录，无法获取产品列表")
            return []
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            response = self.session.get(PRODUCTS_API, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    products = result.get('data', {}).get('products', [])
                    print(f"📊 当前系统中有 {len(products)} 个产品")
                    return products
            
            print(f"❌ 获取产品列表失败: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"❌ 获取产品列表异常: {str(e)}")
            return []
    
    def backup_current_products(self) -> bool:
        """备份当前产品数据"""
        if not PRODUCTS_CSV.exists():
            print("⚠️  产品文件不存在，无需备份")
            return False
        
        try:
            BACKUP_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"products_backup_{timestamp}.csv"
            
            shutil.copy2(PRODUCTS_CSV, backup_file)
            print(f"💾 已备份当前产品到: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ 备份产品文件失败: {str(e)}")
            return False
    
    def reload_products(self) -> bool:
        """重新加载产品数据"""
        print("🔄 正在重新加载产品数据...")
        
        # 触发文件监控重新加载
        try:
            # 读取并写入CSV文件以触发监控
            if PRODUCTS_CSV.exists():
                with open(PRODUCTS_CSV, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                with open(PRODUCTS_CSV, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
                
                print("✅ 产品数据已重新加载")
                return True
            else:
                print("❌ 产品文件不存在")
                return False
                
        except Exception as e:
            print(f"❌ 重新加载产品数据失败: {str(e)}")
            return False
    
    def display_product_statistics(self, products: List[Dict[str, Any]]):
        """显示产品统计信息"""
        if not products:
            print("📊 没有产品数据")
            return
        
        print("\n" + "=" * 80)
        print("📊 产品数据统计")
        print("=" * 80)
        
        # 按航空公司统计
        airline_stats = {}
        for product in products:
            airline = product.get('airline', 'UNKNOWN')
            if airline not in airline_stats:
                airline_stats[airline] = 0
            airline_stats[airline] += 1
        
        print("\n按航空公司统计:")
        for airline, count in sorted(airline_stats.items()):
            print(f"  {airline:10s}: {count:4d} 个产品")
        
        # 按航线统计
        route_stats = {}
        for product in products:
            route = product.get('route', 'UNKNOWN')[:20]  # 只显示前20个字符
            if route not in route_stats:
                route_stats[route] = 0
            route_stats[route] += 1
        
        print(f"\n按航线统计 (前10条):")
        for route, count in sorted(route_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {route:20s}: {count:4d} 个产品")
        
        # 按票证类型统计
        ticket_type_stats = {}
        for product in products:
            ticket_type = product.get('ticket_type', 'UNKNOWN')
            if ticket_type not in ticket_type_stats:
                ticket_type_stats[ticket_type] = 0
            ticket_type_stats[ticket_type] += 1
        
        print(f"\n按票证类型统计:")
        for ticket_type, count in sorted(ticket_type_stats.items()):
            print(f"  {ticket_type:15s}: {count:4d} 个产品")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    print("=" * 80)
    print("🔄 产品信息检索和重新上传工具")
    print("=" * 80)
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 产品文件: {PRODUCTS_CSV}")
    print(f"🌐 API地址: {API_BASE_URL}")
    print("=" * 80)
    print()
    
    # 创建上传器实例
    uploader = ProductUploader()
    
    # 步骤1: 登录系统
    print("步骤 1/5: 登录系统...")
    if not uploader.login():
        print("❌ 登录失败，程序终止")
        return
    
    # 步骤2: 获取当前产品数据
    print("\n步骤 2/5: 获取当前产品数据...")
    current_products = uploader.get_current_products()
    
    # 步骤3: 从CSV加载产品数据
    print("\n步骤 3/5: 从CSV文件加载产品数据...")
    csv_products = uploader.load_csv_products()
    
    if not csv_products:
        print("❌ 没有可上传的产品数据，程序终止")
        return
    
    # 步骤4: 备份当前产品数据
    print("\n步骤 4/5: 备份当前产品数据...")
    uploader.backup_current_products()
    
    # 步骤5: 上传新产品数据
    print("\n步骤 5/5: 上传新产品数据到系统...")
    print(f"📤 准备上传 {len(csv_products)} 个产品...")
    
    success = uploader.upload_products_via_api(csv_products)
    
    # 显示统计信息
    print("\n" + "=" * 80)
    print("📊 上传统计")
    print("=" * 80)
    print(f"✅ 成功上传: {uploader.uploaded_count} 个产品")
    print(f"❌ 失败/跳过: {uploader.failed_count} 个产品")
    print(f"📊 总计: {uploader.uploaded_count + uploader.failed_count} 个产品")
    print("=" * 80)
    
    # 显示产品统计信息
    print("\n" + "=" * 80)
    print("📊 产品数据统计")
    print("=" * 80)
    uploader.display_product_statistics(csv_products)
    
    # 重新加载产品数据
    print("\n🔄 正在重新加载产品数据...")
    uploader.reload_products()
    
    print("\n✅ 产品信息检索和上传完成!")
    print(f"🌐 您可以访问 http://localhost:5000 查看产品数据")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
