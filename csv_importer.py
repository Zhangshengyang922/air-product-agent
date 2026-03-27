#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV产品数据导入工具
用于上传并解析CSV文件到产品系统
"""

import os
import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def validate_csv_file(file_path: str) -> Dict[str, Any]:
    """
    验证CSV文件格式是否正确

    Args:
        file_path: CSV文件路径

    Returns:
        验证结果字典
    """
    try:
        if not Path(file_path).exists():
            return {
                'valid': False,
                'error': f'文件不存在: {file_path}'
            }

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            if not headers:
                return {
                    'valid': False,
                    'error': 'CSV文件没有列名'
                }

            # 检查必需的列
            required_columns = ['产品名称', '航线', '上浮价格', '产品代码']
            missing_columns = [col for col in required_columns if col not in headers]

            if missing_columns:
                return {
                    'valid': False,
                    'error': f'缺少必需的列: {", ".join(missing_columns)}',
                    'headers': headers
                }

            # 读取前几行数据
            sample_rows = []
            for i, row in enumerate(reader):
                if i >= 3:  # 只读取前3行作为样本
                    break
                sample_rows.append(row)

            return {
                'valid': True,
                'headers': headers,
                'sample_rows': sample_rows,
                'row_count': sum(1 for _ in csv.DictReader(open(file_path, 'r', encoding='utf-8-sig'))),
                'message': f'CSV文件验证成功，包含 {sum(1 for _ in csv.DictReader(open(file_path, "r", encoding="utf-8-sig")))} 行数据'
            }

    except Exception as e:
        return {
            'valid': False,
            'error': f'验证CSV文件时出错: {str(e)}'
        }


def clean_and_normalize_data(row: Dict[str, str]) -> Dict[str, Any]:
    """
    清理和标准化数据

    Args:
        row: CSV行数据

    Returns:
        清理后的数据字典
    """
    # 映射中文字段名到英文字段名
    field_mapping = {
        '产品名称': 'product_name',
        '航线': 'route',
        '订座舱位': 'booking_class',
        '上浮价格': 'price_increase',
        '政策返点（后返+车辆后返+代理费)': 'rebate_ratio',
        '产品代码': 'policy_code',
        '票证类型': 'ticket_type',
        '出票OFFICE': 'office',
        '备注': 'remarks',
        '产品有限期': 'valid_period'
    }

    normalized = {}

    # 从航空公司代码中提取（假设产品代码的第一个字符是航司代码）
    policy_code = row.get('产品代码', '')
    if policy_code and len(policy_code) > 0:
        # 尝试从产品代码中提取航司代码
        airline_candidates = ['CZ', 'MU', 'CA', 'HU', 'FM', 'ZH', '3U', 'MF', 'SC', 'CN']
        for code in airline_candidates:
            if policy_code.startswith('*' + code):
                normalized['airline'] = code
                break
        else:
            # 如果没有匹配到，从产品名称中提取
            product_name = row.get('产品名称', '')
            if product_name:
                normalized['airline'] = product_name[:2] if len(product_name) >= 2 else ''

    # 映射其他字段
    for chinese_field, english_field in field_mapping.items():
        value = row.get(chinese_field, '').strip()
        normalized[english_field] = value

    # 清理价格数据
    price_str = normalized.get('price_increase', '0')
    try:
        # 移除可能的单位或符号
        price_str = str(price_str).replace(',', '').replace('元', '').strip()
        if not price_str:
            price_str = '0'
        normalized['price_increase'] = float(price_str)
    except (ValueError, TypeError):
        normalized['price_increase'] = 0

    # 确保ticket_type不为空
    if not normalized.get('ticket_type'):
        normalized['ticket_type'] = 'ALL'

    # 确保airline不为空
    if not normalized.get('airline'):
        normalized['airline'] = 'CZ'  # 默认设置为南航

    # 添加产品标识（用于唯一标识）
    policy_identifier = normalized.get('policy_code', '')
    if policy_identifier:
        normalized['policy_identifier'] = policy_identifier.replace('*', '')
    else:
        normalized['policy_identifier'] = ''

    return normalized


def import_csv_to_products(
    csv_file_path: str,
    output_csv_path: Optional[str] = None,
    backup_existing: bool = True
) -> Dict[str, Any]:
    """
    将CSV文件导入到产品系统

    Args:
        csv_file_path: 源CSV文件路径
        output_csv_path: 输出CSV文件路径（默认为assets/products.csv）
        backup_existing: 是否备份现有文件

    Returns:
        导入结果字典
    """
    try:
        # 验证CSV文件
        validation_result = validate_csv_file(csv_file_path)
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['error'],
                'details': validation_result
            }

        # 设置输出路径
        if not output_csv_path:
            project_root = Path(__file__).parent
            output_csv_path = project_root / 'assets' / 'products.csv'
        else:
            output_csv_path = Path(output_csv_path)

        print(f'开始导入CSV文件: {csv_file_path}')
        print(f'输出目标: {output_csv_path}')
        print(f'包含 {validation_result["row_count"]} 行数据\n')

        # 备份现有文件
        if backup_existing and output_csv_path.exists():
            backup_name = f'products_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            backup_path = output_csv_path.parent / backup_name
            import shutil
            shutil.copy2(output_csv_path, backup_path)
            print(f'已备份现有文件到: {backup_name}\n')

        # 读取并清理数据
        products = []
        skipped_count = 0

        with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            total_rows = sum(1 for _ in reader)
            f.seek(0)
            next(reader)  # 跳过表头

            for i, row in enumerate(reader):
                try:
                    # 跳过空行
                    if not any(row.values()):
                        skipped_count += 1
                        continue

                    # 清理和标准化数据
                    product = clean_and_normalize_data(row)

                    # 验证必需字段
                    if not product.get('airline') or not product.get('product_name'):
                        skipped_count += 1
                        print(f'⚠️  跳过第 {i+1} 行: 缺少航司代码或产品名称')
                        continue

                    products.append(product)

                    # 显示进度
                    if (i + 1) % 50 == 0:
                        print(f'✓ 已处理 {i+1}/{total_rows} 行')

                except Exception as e:
                    skipped_count += 1
                    print(f'⚠️  第 {i+1} 行处理失败: {str(e)}')
                    continue

        print(f'\n数据处理完成:')
        print(f'  成功: {len(products)} 条')
        print(f'  跳过: {skipped_count} 条')

        # 准备输出的CSV列名
        output_fieldnames = [
            'airline', 'product_name', 'route', 'booking_class',
            'price_increase', 'rebate_ratio', 'office', 'remarks',
            'valid_period', 'ticket_type', 'policy_identifier', 'policy_code'
        ]

        # 保存到CSV文件
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(products)

        print(f'\n✅ 成功导入 {len(products)} 个产品到: {output_csv_path}')

        # 显示统计信息
        airlines = {}
        for product in products:
            airline = product.get('airline', '未知')
            airlines[airline] = airlines.get(airline, 0) + 1

        print('\n导入统计:')
        for airline, count in sorted(airlines.items()):
            print(f'  {airline}: {count} 个产品')

        return {
            'success': True,
            'message': f'成功导入 {len(products)} 个产品',
            'details': {
                'total_rows': total_rows,
                'imported_count': len(products),
                'skipped_count': skipped_count,
                'output_file': str(output_csv_path),
                'airlines': airlines
            }
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'导入失败: {str(e)}',
            'details': str(e)
        }


def main():
    """主函数"""
    print('=' * 80)
    print('CSV产品数据导入工具')
    print('=' * 80)
    print()

    # 获取用户输入
    default_input = Path.home() / 'Desktop' / '各航司汇总产品-CZ.csv'
    default_output = Path(__file__).parent / 'assets' / 'products.csv'

    input_file = input(f'请输入CSV文件路径 (直接回车使用默认: {default_input}): ').strip()
    if not input_file:
        input_file = str(default_input)

    output_file = input(f'请输入输出CSV路径 (直接回车使用默认: {default_output}): ').strip()
    if not output_file:
        output_file = str(default_output)

    # 询问是否备份
    backup = input('是否备份现有文件? (y/n, 默认y): ').strip().lower()
    backup_existing = backup != 'n'

    print()
    print('=' * 80)
    print('配置信息:')
    print(f'输入文件: {input_file}')
    print(f'输出文件: {output_file}')
    print(f'备份现有文件: {"是" if backup_existing else "否"}')
    print('=' * 80)
    print()

    # 执行导入
    result = import_csv_to_products(input_file, output_file, backup_existing)

    print()
    print('=' * 80)
    if result['success']:
        print('✅ 导入成功!')
        print(f'消息: {result["message"]}')

        details = result.get('details', {})
        if details:
            print(f'\n详细信息:')
            print(f'  总行数: {details.get("total_rows", 0)}')
            print(f'  成功导入: {details.get("imported_count", 0)}')
            print(f'  跳过: {details.get("skipped_count", 0)}')
            print(f'  输出文件: {details.get("output_file", "")}')

        print('\n提示:')
        print('  1. 数据已保存到 products.csv')
        print('  2. Web界面会自动刷新并显示新数据')
        print('  3. 如果数据未显示，请刷新浏览器页面')
        print('  4. 服务器运行在 http://localhost:8000')
    else:
        print('❌ 导入失败!')
        print(f'错误: {result["message"]}')
        print('\n请检查:')
        print('  1. CSV文件路径是否正确')
        print('  2. CSV文件格式是否正确')
        print('  3. 是否有必需的列: 产品名称, 航线, 上浮价格, 产品代码')
        print('  4. 文件编码是否为 UTF-8')

    print('=' * 80)


if __name__ == '__main__':
    # 如果有命令行参数，直接执行导入
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        backup = sys.argv[3] if len(sys.argv) > 3 else 'true'
        backup_existing = backup.lower() != 'false'

        result = import_csv_to_products(input_file, output_file, backup_existing)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        main()
