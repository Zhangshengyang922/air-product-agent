# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd
import os

# 文件路径
file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'
original_backup = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products_backup.csv'

print("开始重新合并产品数据...")

# 读取原始备份（225条）
original_df = pd.read_csv(original_backup)
print(f"读取原始产品数量: {len(original_df)}")

# 备份当前文件
current_df = pd.read_csv(output_path)
current_backup = output_path.replace('.csv', '_current_backup.csv')
current_df.to_csv(current_backup, index=False, encoding='utf-8-sig')
print(f"已备份当前文件到: {current_backup}")

# 使用xlwings读取新产品
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
        print(f"  读取 {sheet.name}...")

        used_range = sheet.used_range
        data = used_range.value

        if data and len(data) > 1:
            if not isinstance(data[0], list):
                continue

            headers = clean_columns(data[0])

            try:
                df = pd.DataFrame(data[1:], columns=headers)
                df['source_sheet'] = sheet.name
                all_data.append(df)
            except:
                pass

    wb.close()

    if all_data:
        merged_new = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"\n新产品总记录数: {len(merged_new)}")

        # 标准化新产品
        standardized_new = pd.DataFrame()

        # 提取航司
        standardized_new['airline'] = merged_new['source_sheet'].str.extract(r'^([A-Z0-9]+)')[0]

        # 映射所有列
        col_mapping = {
            '产品名称': 'product_name',
            '航线': 'route',
            '订座舱位': 'booking_class',
            '上浮价格': 'price_increase',
            '政策返点（后返+车辆后返+代理费)': 'rebate_ratio',  # CZ专用
            '政策返点': 'rebate_ratio',  # 其他
            '产品代码': 'policy_identifier',
            '票证类型': 'ticket_type',
            '出票office': 'office',
            '出票office': 'office',  # 大写O
            '备注': 'remarks',
            '产品有限期': 'valid_period',
            '政策代码': 'policy_code'
        }

        # 首先尝试精确匹配
        for src_col, target_col in col_mapping.items():
            if src_col in merged_new.columns and target_col not in standardized_new.columns:
                standardized_new[target_col] = merged_new[src_col]

        # 如果还没有，尝试通用列名
        if 'product_name' not in standardized_new.columns:
            for col in merged_new.columns:
                if 'none' not in col and 'airline' not in col and 'source' not in col:
                    standardized_new['product_name'] = merged_new[col]
                    break

        # 清理空航司
        standardized_new = standardized_new[standardized_new['airline'].notna() & (standardized_new['airline'] != '')]
        standardized_new = standardized_new.reset_index(drop=True)

        print(f"标准化后新产品数量: {len(standardized_new)}")

        # 合并原始产品和新产品
        final_df = pd.concat([original_df, standardized_new], ignore_index=True)
        print(f"合并后总产品数: {len(final_df)}")

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存到: {output_path}")

        # 数据质量检查
        print("\n数据质量检查:")
        non_empty_rebate = final_df['rebate_ratio'].notna() & (final_df['rebate_ratio'] != '')
        non_empty_office = final_df['office'].notna() & (final_df['office'] != '')

        print(f"有返点数据: {non_empty_rebate.sum()} ({non_empty_rebate.sum()*100/len(final_df):.1f}%)")
        print(f"有office数据: {non_empty_office.sum()} ({non_empty_office.sum()*100/len(final_df):.1f}%)")

        # 各航司统计
        print("\n各航司产品数量(前20):")
        print(final_df['airline'].value_counts().head(20))

finally:
    app.quit()

print("\n完成！")
