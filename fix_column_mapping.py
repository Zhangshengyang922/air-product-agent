# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
original_backup = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products_backup.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("开始重新解析...")

# 读取原始225条
original_df = pd.read_csv(original_backup)
print(f"原始产品数: {len(original_df)}")

app = xw.App(visible=False)

all_data = []

try:
    wb = app.books.open(file_path)

    print(f"\n读取{len(wb.sheets)}个工作表...")

    for sheet in wb.sheets:
        used_range = sheet.used_range
        data = used_range.value

        if data and len(data) > 1 and isinstance(data[0], list):
            # 不清理列名，保持原样
            headers = data[0]
            try:
                df = pd.DataFrame(data[1:], columns=headers)
                df['source_sheet'] = sheet.name
                all_data.append(df)
            except:
                pass

    wb.close()

    if all_data:
        merged_new = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"新产品总记录: {len(merged_new)}")

        # 使用原始列名映射
        standardized_new = pd.DataFrame()
        standardized_new['airline'] = merged_new['source_sheet'].str.extract(r'^([A-Z0-9]+)')[0]

        # 直接通过列索引映射（不依赖列名）
        # 根据我们看到的结构：产品名称(0), 航线(1), 订座舱位(2), 上浮价格(3), 政策返点(4), 产品代码(5), 票证类型(6), 出票OFFICE(7), 备注(8), 产品有限期(9)

        # 先尝试列名匹配，如果不成功则用索引
        if '产品名称' in merged_new.columns:
            standardized_new['product_name'] = merged_new['产品名称']
        elif len(merged_new.columns) > 1:
            standardized_new['product_name'] = merged_new.iloc[:, 1]

        if '航线' in merged_new.columns:
            standardized_new['route'] = merged_new['航线']
        elif len(merged_new.columns) > 2:
            standardized_new['route'] = merged_new.iloc[:, 2]

        if '订座舱位' in merged_new.columns:
            standardized_new['booking_class'] = merged_new['订座舱位']
        elif len(merged_new.columns) > 3:
            standardized_new['booking_class'] = merged_new.iloc[:, 3]

        if '上浮价格' in merged_new.columns:
            standardized_new['price_increase'] = merged_new['上浮价格']
        elif len(merged_new.columns) > 4:
            standardized_new['price_increase'] = merged_new.iloc[:, 4]

        # 政策返点 - 尝试多种列名
        rebate_col = None
        for col in merged_new.columns:
            if col and ('政策返点' in str(col) or 'rebate' in str(col).lower()):
                rebate_col = col
                break

        if rebate_col:
            standardized_new['rebate_ratio'] = merged_new[rebate_col]
        elif len(merged_new.columns) > 5:
            # 第5列（索引4）通常是政策返点
            standardized_new['rebate_ratio'] = merged_new.iloc[:, 4]

        # 产品代码
        if '产品代码' in merged_new.columns:
            standardized_new['policy_identifier'] = merged_new['产品代码']
        elif len(merged_new.columns) > 6:
            standardized_new['policy_identifier'] = merged_new.iloc[:, 5]

        # 票证类型
        if '票证类型' in merged_new.columns:
            standardized_new['ticket_type'] = merged_new['票证类型']
        elif len(merged_new.columns) > 7:
            standardized_new['ticket_type'] = merged_new.iloc[:, 6]

        # 出票OFFICE
        office_col = None
        for col in merged_new.columns:
            if col and ('office' in str(col).lower() or 'OFFICE' in str(col)):
                office_col = col
                break

        if office_col:
            standardized_new['office'] = merged_new[office_col]
        elif len(merged_new.columns) > 8:
            # 第8列（索引7）通常是office
            standardized_new['office'] = merged_new.iloc[:, 7]

        # 备注
        if '备注' in merged_new.columns:
            standardized_new['remarks'] = merged_new['备注']
        elif len(merged_new.columns) > 9:
            standardized_new['remarks'] = merged_new.iloc[:, 8]

        # 产品有限期
        if '产品有限期' in merged_new.columns:
            standardized_new['valid_period'] = merged_new['产品有限期']
        elif len(merged_new.columns) > 10:
            standardized_new['valid_period'] = merged_new.iloc[:, 9]

        # 政策代码
        if '政策代码' in merged_new.columns:
            standardized_new['policy_code'] = merged_new['政策代码']

        # 清理空航司
        standardized_new = standardized_new[standardized_new['airline'].notna() & (standardized_new['airline'] != '')]
        standardized_new = standardized_new.reset_index(drop=True)

        print(f"标准化后: {len(standardized_new)}")

        # 合并
        final_df = pd.concat([original_df, standardized_new], ignore_index=True)
        print(f"合并后总数: {len(final_df)}")

        # 检查质量
        non_empty_rebate = final_df['rebate_ratio'].notna() & (final_df['rebate_ratio'] != '')
        non_empty_office = final_df['office'].notna() & (final_df['office'] != '')

        print(f"\n有返点: {non_empty_rebate.sum()} ({non_empty_rebate.sum()*100/len(final_df):.1f}%)")
        print(f"有office: {non_empty_office.sum()} ({non_empty_office.sum()*100/len(final_df):.1f}%)")

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存到: {output_path}")

finally:
    app.quit()

print("\n完成！")
