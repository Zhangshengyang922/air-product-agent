# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("使用新数据重建产品数据库...")

app = xw.App(visible=False)

all_standardized = []

try:
    wb = app.books.open(file_path)

    for sheet in wb.sheets:
        used_range = sheet.used_range
        data = used_range.value

        if not data or len(data) <= 1 or not isinstance(data[0], list):
            continue

        headers = data[0]
        rows = data[1:]

        try:
            sheet_df = pd.DataFrame(rows, columns=headers)
        except:
            continue

        # 提取航司代码
        airline_code = None
        match = re.match(r'^([A-Z0-9]{2,3})', sheet.name)
        if match:
            airline_code = match.group(1)
        else:
            mapping = {
                '福': 'FU', '北': 'GX', '乌': 'UQ', '长': '9H',
                '华': 'G5', '奥': 'BK', '幸': 'JR', '天': 'GS',
                '青': 'QW', '河': 'NS', '江': 'RY', '多': 'GY', '东': 'DZ'
            }
            for key, code in mapping.items():
                if key in sheet.name:
                    airline_code = code
                    break

        if not airline_code:
            continue

        standardized = pd.DataFrame()
        standardized['airline'] = airline_code

        if len(sheet_df.columns) > 0:
            standardized['product_name'] = sheet_df.iloc[:, 0]
        if len(sheet_df.columns) > 1:
            standardized['route'] = sheet_df.iloc[:, 1]
        if len(sheet_df.columns) > 2:
            standardized['booking_class'] = sheet_df.iloc[:, 2]
        if len(sheet_df.columns) > 3:
            standardized['price_increase'] = sheet_df.iloc[:, 3]
        if len(sheet_df.columns) > 4:
            standardized['rebate_ratio'] = sheet_df.iloc[:, 4]
        if len(sheet_df.columns) > 5:
            standardized['policy_identifier'] = sheet_df.iloc[:, 5]
        if len(sheet_df.columns) > 6:
            standardized['ticket_type'] = sheet_df.iloc[:, 6]
        if len(sheet_df.columns) > 7:
            standardized['office'] = sheet_df.iloc[:, 7]
        if len(sheet_df.columns) > 8:
            standardized['remarks'] = sheet_df.iloc[:, 8]
        if len(sheet_df.columns) > 9:
            standardized['valid_period'] = sheet_df.iloc[:, 9]
        standardized['policy_code'] = ''

        all_standardized.append(standardized)
        print(f"  {sheet.name} ({airline_code}): {len(standardized)} 条")

    wb.close()

    if all_standardized:
        final_df = pd.concat(all_standardized, ignore_index=True)
        print(f"\n产品总数: {len(final_df)}")

        non_empty_rebate = final_df['rebate_ratio'].notna() & (final_df['rebate_ratio'] != '')
        non_empty_office = final_df['office'].notna() & (final_df['office'] != '')

        print(f"有返点: {non_empty_rebate.sum()} ({non_empty_rebate.sum()*100/len(final_df):.1f}%)")
        print(f"有office: {non_empty_office.sum()} ({non_empty_office.sum()*100/len(final_df):.1f}%)")

        print("\n各航司产品数:")
        print(final_df['airline'].value_counts())

        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存: {output_path}")

finally:
    app.quit()

print("\n完成！")
