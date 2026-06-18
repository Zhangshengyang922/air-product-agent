# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd
import os

# 文件路径
file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products_fixed.csv'
existing_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'
backup_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products_backup2.csv'

print("开始重新解析产品数据...")

# 读取现有产品（保留原始225条）
existing_df = pd.read_csv(existing_file)
print(f"现有产品数量: {len(existing_df)}")

# 备份现有产品
existing_df.to_csv(backup_file, index=False, encoding='utf-8-sig')
print(f"已备份现有产品到: {backup_file}")

# 使用xlwings重新读取
app = xw.App(visible=False)

def clean_columns(cols):
    """清理列名，处理重复"""
    cols = [str(col).lower().replace(' ', '_').strip() for col in cols]
    col_count = {}
    new_cols = []
    for col in cols:
        if col in col_count:
            col_count[col] += 1
            new_cols.append(f"{col}_{col_count[col]}")
        else:
            col_count[col] = 1
            new_cols.append(col)
    return new_cols

all_data = []

try:
    wb = app.books.open(file_path)

    print(f"\n工作表数量: {len(wb.sheets)}")

    for sheet in wb.sheets:
        print(f"\n读取工作表: {sheet.name}")

        # 读取数据
        used_range = sheet.used_range
        data = used_range.value

        if data and len(data) > 1:
            if not isinstance(data[0], list):
                print(f"  跳过 {sheet.name}: 数据格式不正确")
                continue

            # 清理列名
            headers = clean_columns(data[0])

            # 转换为DataFrame
            try:
                df = pd.DataFrame(data[1:], columns=headers)
                df['source_sheet'] = sheet.name
                all_data.append(df)
                print(f"  读取 {len(df)} 条记录")
            except Exception as e:
                print(f"  读取 {sheet.name} 失败: {e}")

    wb.close()

    if all_data:
        # 使用外连接合并
        merged_df = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"\n合并后总记录数: {len(merged_df)}")

        # 标准化列名并映射到统一格式
        print("\n标准化产品数据...")

        standardized_df = pd.DataFrame()

        # 从source_sheet提取航司代码
        standardized_df['airline'] = merged_df['source_sheet'].str.extract(r'^([A-Z0-9]+)')[0]

        # 产品名称 - 多种可能的列名
        for col in ['产品名称', 'product_name', 'none']:
            if col in merged_df.columns:
                standardized_df['product_name'] = merged_df[col]
                break

        # 航线
        for col in ['航线', 'route', 'none_2']:
            if col in merged_df.columns:
                standardized_df['route'] = merged_df[col]
                break

        # 订座舱位
        for col in ['订座舱位', 'booking_class', 'none_3']:
            if col in merged_df.columns:
                standardized_df['booking_class'] = merged_df[col]
                break

        # 上浮价格 - 多种可能的列名
        for col in ['上浮价格', '上浮/下浮价格', 'price_increase', 'none_4']:
            if col in merged_df.columns:
                standardized_df['price_increase'] = merged_df[col]
                break

        # 政策返点 - 优先匹配完整列名
        for col in ['政策返点（后返+车辆后返+代理费)', '政策返点', 'rebate_ratio', 'none_5']:
            if col in merged_df.columns:
                standardized_df['rebate_ratio'] = merged_df[col]
                break

        # 产品代码
        for col in ['产品代码', 'policy_identifier', 'none_6']:
            if col in merged_df.columns:
                standardized_df['policy_identifier'] = merged_df[col]
                break

        # 票证类型
        for col in ['票证类型', 'ticket_type', 'none_7']:
            if col in merged_df.columns:
                standardized_df['ticket_type'] = merged_df[col]
                break

        # 出票OFFICE
        for col in ['出票office', '出票office', '出票office', 'office', 'none_8']:
            if col in merged_df.columns:
                standardized_df['office'] = merged_df[col]
                break

        # 备注
        for col in ['备注', 'remarks', 'none_9']:
            if col in merged_df.columns:
                standardized_df['remarks'] = merged_df[col]
                break

        # 产品有限期
        for col in ['产品有限期', 'valid_period', 'none_10']:
            if col in merged_df.columns:
                standardized_df['valid_period'] = merged_df[col]
                break

        # 政策代码
        for col in ['政策代码', 'policy_code', 'none_11']:
            if col in merged_df.columns:
                standardized_df['policy_code'] = merged_df[col]
                break

        # 清理数据 - 移除空航司的行
        standardized_df = standardized_df[standardized_df['airline'].notna() & (standardized_df['airline'] != '')]
        standardized_df = standardized_df.reset_index(drop=True)

        print(f"清理后新产品数量: {len(standardized_df)}")

        # 统计各航司产品数量
        print("\n新产品各航司统计:")
        print(standardized_df['airline'].value_counts().head(20))

        # 合并现有产品
        print("\n合并现有产品...")
        final_df = pd.concat([existing_df, standardized_df], ignore_index=True)
        print(f"合并后总产品数: {len(final_df)}")

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存到: {output_path}")

        # 检查数据质量
        print("\n数据质量检查:")

        non_empty_rebate = final_df['rebate_ratio'].notna() & (final_df['rebate_ratio'] != '')
        print(f"有返点数据: {non_empty_rebate.sum()} ({non_empty_rebate.sum()*100/len(final_df):.1f}%)")

        non_empty_office = final_df['office'].notna() & (final_df['office'] != '')
        print(f"有office数据: {non_empty_office.sum()} ({non_empty_office.sum()*100/len(final_df):.1f}%)")

        # 显示一些示例
        print("\n返点数据示例:")
        sample = final_df[non_empty_rebate][['airline', 'product_name', 'rebate_ratio']].head(10)
        for _, row in sample.iterrows():
            print(f"  {row['airline']}: {row['product_name'][:30]} - {row['rebate_ratio']}")

        print("\nOffice数据示例:")
        sample = final_df[non_empty_office][['airline', 'product_name', 'office']].head(10)
        for _, row in sample.iterrows():
            print(f"  {row['airline']}: {row['product_name'][:30]} - {row['office']}")

finally:
    app.quit()

print("\n完成！")
