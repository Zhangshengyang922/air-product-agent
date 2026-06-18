# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("最终修复版...")

app = xw.App(visible=False)

all_rows = []

try:
    wb = app.books.open(file_path)

    for sheet in wb.sheets:
        used_range = sheet.used_range
        data = used_range.value

        if not data or len(data) <= 1 or not isinstance(data[0], list):
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

        headers = data[0]
        rows = data[1:]

        for row in rows:
            if not isinstance(row, list):
                continue

            row_dict = {'airline': airline_code}

            if len(row) > 0:
                row_dict['product_name'] = row[0]
            else:
                row_dict['product_name'] = ''

            if len(row) > 1:
                row_dict['route'] = row[1]
            else:
                row_dict['route'] = ''

            if len(row) > 2:
                row_dict['booking_class'] = row[2]
            else:
                row_dict['booking_class'] = ''

            if len(row) > 3:
                row_dict['price_increase'] = row[3]
            else:
                row_dict['price_increase'] = ''

            if len(row) > 4:
                row_dict['rebate_ratio'] = row[4]
            else:
                row_dict['rebate_ratio'] = ''

            if len(row) > 5:
                row_dict['product_code'] = row[5]  # 产品代码
            else:
                row_dict['product_code'] = ''

            if len(row) > 6:
                row_dict['office'] = row[6]  # 出票OFFICE
            else:
                row_dict['office'] = ''

            if len(row) > 7:
                row_dict['remarks'] = row[7]  # 备注
            else:
                row_dict['remarks'] = ''

            if len(row) > 8:
                row_dict['valid_period'] = row[8]  # 产品有限期
            else:
                row_dict['valid_period'] = ''

            row_dict['policy_identifier'] = ''
            row_dict['ticket_type'] = ''

            all_rows.append(row_dict)

        print(f"  {sheet.name} ({airline_code}): {len(rows)} 条")

    wb.close()

    if all_rows:
        final_df = pd.DataFrame(all_rows)
        print(f"\n产品总数: {len(final_df)}")

        # 质量检查
        non_empty_rebate = final_df['rebate_ratio'].notna() & (final_df['rebate_ratio'] != '')
        non_empty_office = final_df['office'].notna() & (final_df['office'] != '')

        print(f"有返点: {non_empty_rebate.sum()} ({non_empty_rebate.sum()*100/len(final_df):.1f}%)")
        print(f"有office: {non_empty_office.sum()} ({non_empty_office.sum()*100/len(final_df):.1f}%)")

        print("\n各航司产品数:")
        print(final_df['airline'].value_counts())

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存: {output_path}")

finally:
    app.quit()

print("\n完成！")
