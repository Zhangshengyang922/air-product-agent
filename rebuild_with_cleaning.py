import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("=== 重新解析并清理Office数据 ===\n")

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

            # 提取各列数据
            row_dict['product_name'] = row[0] if len(row) > 0 else ''
            row_dict['route'] = row[1] if len(row) > 1 else ''
            row_dict['booking_class'] = row[2] if len(row) > 2 else ''
            row_dict['price_increase'] = row[3] if len(row) > 3 else ''
            row_dict['rebate_ratio'] = row[4] if len(row) > 4 else ''
            row_dict['product_code'] = row[5] if len(row) > 5 else ''
            row_dict['office'] = row[6] if len(row) > 6 else ''
            row_dict['remarks'] = row[7] if len(row) > 7 else ''
            row_dict['valid_period'] = row[8] if len(row) > 8 else ''

            # 处理office和销售渠道
            office_value = str(row_dict['office']) if row_dict['office'] else ''

            # 标准office模式：3-4位字母+3位数字
            standard_office_pattern = re.compile(r'^([A-Z]{3,4}\d{3})$')

            if not office_value or office_value == 'nan':
                row_dict['office'] = ''
                row_dict['sales_channel'] = ''
            elif '/' in office_value:
                parts = office_value.split('/')
                office_parts = []
                channel_parts = []

                for part in parts:
                    part = part.strip()
                    if standard_office_pattern.match(part):
                        office_parts.append(part)
                    else:
                        # 认定为销售渠道标识
                        channel_parts.append(part)

                if office_parts:
                    row_dict['office'] = '/'.join(office_parts)
                    row_dict['sales_channel'] = '/'.join(channel_parts) if channel_parts else ''
                else:
                    row_dict['office'] = ''
                    row_dict['sales_channel'] = office_value
            elif standard_office_pattern.match(office_value):
                # 标准office号
                row_dict['office'] = office_value
                row_dict['sales_channel'] = ''
            else:
                # 销售渠道标识
                row_dict['office'] = ''
                row_dict['sales_channel'] = office_value

            # 添加空列
            row_dict['policy_identifier'] = ''
            row_dict['ticket_type'] = ''

            all_rows.append(row_dict)

        print(f"  {sheet.name} ({airline_code}): {len(rows)} 条")

    wb.close()

    if all_rows:
        final_df = pd.DataFrame(all_rows)
        print(f"\n产品总数: {len(final_df)}")

        # 统计
        has_office = final_df['office'].notna() & (final_df['office'] != '')
        has_channel = final_df['sales_channel'].notna() & (final_df['sales_channel'] != '')
        has_code = final_df['product_code'].notna() & (final_df['product_code'] != '')

        print(f"\n数据完整度:")
        print(f"  - 有标准office号: {has_office.sum()} ({has_office.sum()*100/len(final_df):.1f}%)")
        print(f"  - 有销售渠道: {has_channel.sum()} ({has_channel.sum()*100/len(final_df):.1f}%)")
        print(f"  - 有产品代码: {has_code.sum()} ({has_code.sum()*100/len(final_df):.1f}%)")

        print("\n各航司office覆盖情况:")
        office_by_airline = final_df.groupby('airline').agg({
            'airline': 'count',
            'office': lambda x: (x.notna() & (x != '')).sum()
        })
        office_by_airline.columns = ['总数', '标准office数']
        office_by_airline['覆盖率'] = office_by_airline['标准office数'] * 100 / office_by_airline['总数']
        print(office_by_airline.round(1).sort_values('覆盖率', ascending=False))

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存: {output_path}")

finally:
    app.quit()

print("\n完成！")
