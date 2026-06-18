#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新产品信息脚本
从Excel文件读取新产品信息，与现有产品对比，跳过重复项，更新变化项，添加新增项
"""

import pandas as pd
import csv
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_existing_products(csv_file: Path) -> Dict[Tuple[str, str], Dict]:
    """
    加载现有产品数据

    Args:
        csv_file: CSV文件路径

    Returns:
        字典，键为(airline, product_name)，值为产品数据字典
    """
    existing_products = {}

    if not csv_file.exists():
        logger.warning(f"现有产品文件不存在: {csv_file}")
        return existing_products

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['airline'], row['product_name'])
            existing_products[key] = row

    logger.info(f"加载现有产品 {len(existing_products)} 条")
    return existing_products


def parse_excel_file(excel_file: Path) -> List[Dict]:
    """
    解析Excel文件，提取产品信息

    Args:
        excel_file: Excel文件路径

    Returns:
        产品列表
    """
    try:
        logger.info(f"开始使用xlwings读取Excel文件: {excel_file}")

        import xlwings as xw

        # 使用xlwings读取Excel，它会使用Windows COM接口，可以绕过openpyxl的样式问题
        app = xw.App(visible=False)
        try:
            wb = app.books.open(str(excel_file))
            sheet = wb.sheets[0]

            # 读取所有数据
            used_range = sheet.used_range
            data = used_range.value

            wb.close()
            logger.info(f"读取到 {len(data)} 行数据")

            if not data or len(data) < 2:
                logger.error("Excel文件为空")
                return []

            # 转换为DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            logger.info(f"转换为DataFrame成功，列数: {len(df.columns)}")

        finally:
            app.quit()

        if df.empty:
            logger.error("Excel文件为空或读取失败")
            return []

        logger.info(f"Excel列名: {list(df.columns)}")

        # 标准化列名映射
        column_mapping = {
            '航司代码': 'airline',
            '航空公司': 'airline',
            '航司': 'airline',
            'Airline': 'airline',
            'airlinecode': 'airline',
            'airline_code': 'airline',

            '产品名称': 'product_name',
            '产品名': 'product_name',
            'Product': 'product_name',
            'product_name': 'product_name',

            '航线': 'route',
            '航段': 'route',
            '行程': 'route',
            'Route': 'route',
            'route': 'route',

            '舱位': 'booking_class',
            '订座舱位': 'booking_class',
            'Class': 'booking_class',
            'booking_class': 'booking_class',

            '上浮金额': 'price_increase',
            '上浮价': 'price_increase',
            '上浮价格': 'price_increase',
            '价格': 'price_increase',
            'Price': 'price_increase',
            'price_increase': 'price_increase',

            '后返金额': 'rebate_ratio',
            '后返': 'rebate_ratio',
            '返点': 'rebate_ratio',
            '返佣': 'rebate_ratio',
            '政策返点': 'rebate_ratio',
            'rebate_ratio': 'rebate_ratio',

            'Office号': 'office',
            '出票Office': 'office',
            '出票OFFICE': 'office',
            'Office': 'office',
            'office': 'office',

            '备注': 'remarks',
            '说明': 'remarks',
            'Remark': 'remarks',
            'remarks': 'remarks',

            '有效期': 'valid_period',
            '有效日期': 'valid_period',
            '产品有限期': 'valid_period',
            'valid_period': 'valid_period',

            '票证类型': 'ticket_type',
            'Ticket': 'ticket_type',
            'ticket_type': 'ticket_type',

            '产品代码': 'policy_code',
        }

        # 创建新的列名映射
        df_mapped = df.rename(columns=column_mapping)

        # 打印前几行数据以便调试
        logger.info("前3行数据:")
        for idx in range(min(3, len(df_mapped))):
            logger.info(f"  行 {idx}: {dict(df_mapped.iloc[idx])}")

        # 如果缺少airline列,尝试从product_name中提取
        if 'airline' not in df_mapped.columns:
            logger.warning("缺少airline列,尝试从product_name中提取航司代码")
            df_mapped['airline'] = df_mapped['product_name'].apply(
                lambda x: str(x).split('、')[0].strip().upper() if pd.notna(x) else ''
            )
            logger.info(f"提取航司代码示例: {df_mapped[['product_name', 'airline']].head()}")

        # 确保所有必要的列都存在
        required_columns = ['airline', 'product_name']
        for col in required_columns:
            if col not in df_mapped.columns:
                logger.error(f"缺少必要列: {col}")
                logger.info(f"可用列: {list(df_mapped.columns)}")
                return []

        # 转换为产品字典列表
        products = []
        for idx, row in df_mapped.iterrows():
            # 跳过空行
            if pd.isna(row['product_name']) or str(row['product_name']).strip() == '':
                continue

            # 提取航司代码
            airline = str(row.get('airline', '')).strip().upper()
            product_name = str(row.get('product_name', '')).strip()

            # 如果airline为空,尝试从product_name提取
            if not airline or airline == 'NAN':
                if '、' in product_name:
                    airline = product_name.split('、')[0].strip().upper()
                elif ',' in product_name:
                    airline = product_name.split(',')[0].strip().upper()
                else:
                    airline = 'UNKNOWN'

            # 解析价格字段
            price_value = row.get('price_increase', '')
            price_increase = 0
            if pd.notna(price_value) and str(price_value).strip():
                price_str = str(price_value).strip()
                # 尝试提取数字,处理范围值如"70-120"
                import re
                # 查找所有数字(包括小数)
                numbers = re.findall(r'\d+\.?\d*', price_str)
                if numbers:
                    # 如果是范围,取第一个数字或者平均值
                    if len(numbers) > 1:
                        try:
                            num1 = float(numbers[0])
                            num2 = float(numbers[1])
                            price_increase = (num1 + num2) / 2  # 取平均值
                        except:
                            price_increase = float(numbers[0])
                    else:
                        price_increase = float(numbers[0])

            product = {
                'airline': airline,
                'product_name': product_name,
                'route': str(row.get('route', '')).strip() if pd.notna(row.get('route')) else '',
                'booking_class': str(row.get('booking_class', '')).strip() if pd.notna(row.get('booking_class')) else '',
                'price_increase': price_increase,
                'rebate_ratio': str(row.get('rebate_ratio', '')).strip() if pd.notna(row.get('rebate_ratio')) else '',
                'office': str(row.get('office', '')).strip() if pd.notna(row.get('office')) else '',
                'remarks': str(row.get('remarks', '')).strip() if pd.notna(row.get('remarks')) else '',
                'valid_period': str(row.get('valid_period', '')).strip() if pd.notna(row.get('valid_period')) else '',
                'ticket_type': str(row.get('ticket_type', 'ALL')).strip().upper() if pd.notna(row.get('ticket_type')) else 'ALL',
                'policy_identifier': str(row.get('policy_identifier', '')).strip() if pd.notna(row.get('policy_identifier')) else '',
                'policy_code': str(row.get('policy_code', '')).strip() if pd.notna(row.get('policy_code')) else '',
            }

            # 只添加有效产品（航司和产品名都不为空）
            if product['airline'] and product['product_name']:
                products.append(product)

        logger.info(f"从Excel中提取有效产品 {len(products)} 条")
        return products

    except Exception as e:
        logger.error(f"解析Excel文件失败: {e}", exc_info=True)
        return []


def compare_products(new_products: List[Dict], existing_products: Dict[Tuple[str, str], Dict]):
    """
    对比新旧产品，分类为：新增、更新、跳过

    Args:
        new_products: 新产品列表
        existing_products: 现有产品字典

    Returns:
        (新增产品, 更新产品, 跳过产品)
    """
    added = []
    updated = []
    skipped = []

    for new_prod in new_products:
        key = (new_prod['airline'], new_prod['product_name'])

        if key in existing_products:
            # 检查是否有变化
            old_prod = existing_products[key]

            # 比较所有字段
            has_changes = False
            changed_fields = []

            for field in old_prod.keys():
                old_value = str(old_prod[field]).strip()
                new_value = str(new_prod.get(field, '')).strip()

                # 数值类型特殊处理
                if field == 'price_increase':
                    # 提取价格数值进行比较
                    def extract_price(val):
                        if not val or val == 'nan':
                            return 0
                        import re
                        numbers = re.findall(r'\d+\.?\d*', str(val))
                        if numbers:
                            if len(numbers) > 1:
                                try:
                                    return (float(numbers[0]) + float(numbers[1])) / 2
                                except:
                                    return float(numbers[0])
                            else:
                                return float(numbers[0])
                        return 0

                    old_num = extract_price(old_value)
                    new_num = extract_price(new_value)
                    if old_num != new_num:
                        has_changes = True
                        changed_fields.append(field)
                else:
                    if old_value != new_value:
                        has_changes = True
                        changed_fields.append(field)

            if has_changes:
                updated.append({
                    'product': new_prod,
                    'old_product': old_prod,
                    'changed_fields': changed_fields
                })
            else:
                skipped.append(new_prod)
        else:
            # 新产品
            added.append(new_prod)

    logger.info(f"对比结果: 新增 {len(added)} 条, 更新 {len(updated)} 条, 跳过 {len(skipped)} 条")
    return added, updated, skipped


def save_products(all_products: List[Dict], csv_file: Path):
    """
    保存产品到CSV文件

    Args:
        all_products: 所有产品列表
        csv_file: CSV文件路径
    """
    fieldnames = ['airline', 'product_name', 'route', 'booking_class',
                  'price_increase', 'rebate_ratio', 'office', 'remarks',
                  'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_products)

    logger.info(f"保存 {len(all_products)} 条产品到 {csv_file}")


def print_summary(added: List, updated: List, skipped: List):
    """打印更新摘要"""
    print("\n" + "="*80)
    print("产品更新摘要")
    print("="*80)

    if added:
        print(f"\n[新增] 新增产品 ({len(added)} 条):")
        for prod in added[:10]:  # 只显示前10条
            print(f"  - [{prod['airline']}] {prod['product_name']}")
        if len(added) > 10:
            print(f"  ... 还有 {len(added) - 10} 条")

    if updated:
        print(f"\n[更新] 更新产品 ({len(updated)} 条):")
        for item in updated[:10]:  # 只显示前10条
            prod = item['product']
            changes = ', '.join(item['changed_fields'][:5])
            print(f"  - [{prod['airline']}] {prod['product_name']} (变化: {changes})")
        if len(updated) > 10:
            print(f"  ... 还有 {len(updated) - 10} 条")

    if skipped:
        print(f"\n[跳过] 跳过产品 ({len(skipped)} 条):")
        for prod in skipped[:5]:  # 只显示前5条
            print(f"  - [{prod['airline']}] {prod['product_name']}")
        if len(skipped) > 5:
            print(f"  ... 还有 {len(skipped) - 5} 条")

    print("\n" + "="*80)


def main():
    """主函数"""
    # 文件路径
    excel_file = Path(r"C:\Users\Administrator\OneDrive\桌面\各航司汇总产品.xlsx")
    csv_file = Path(__file__).parent / "assets" / "products.csv"

    print(f"Excel文件: {excel_file}")
    print(f"CSV文件: {csv_file}")
    print(f"Excel文件存在: {excel_file.exists()}")
    print(f"CSV文件存在: {csv_file.exists()}")

    # 1. 加载现有产品
    existing_products = load_existing_products(csv_file)

    # 2. 解析Excel文件
    new_products = parse_excel_file(excel_file)
    if not new_products:
        logger.error("没有提取到新产品，退出")
        return

    # 3. 对比产品
    added, updated, skipped = compare_products(new_products, existing_products)

    # 4. 打印摘要
    print_summary(added, updated, skipped)

    # 5. 合并产品
    all_products = list(existing_products.values())

    # 先移除已更新的产品
    for item in updated:
        key = (item['product']['airline'], item['product']['product_name'])
        all_products = [p for p in all_products if (p['airline'], p['product_name']) != key]

    # 添加更新的产品
    for item in updated:
        all_products.append(item['product'])

    # 添加新产品
    all_products.extend(added)

    logger.info(f"合并后总计: {len(all_products)} 条产品")

    # 6. 保存到CSV
    save_products(all_products, csv_file)

    print(f"\n[完成] 产品更新完成!")
    print(f"总计: {len(all_products)} 条产品")
    print(f"新增: {len(added)} 条")
    print(f"更新: {len(updated)} 条")
    print(f"跳过: {len(skipped)} 条")
    print(f"文件已保存到: {csv_file}")


if __name__ == "__main__":
    main()
