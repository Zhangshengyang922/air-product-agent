import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("=== 重新解析所有数据，特别处理3U和MF ===\n")

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

            # 提取产品名称
            product_name = row[0] if len(row) > 0 else ''
            if not product_name or str(product_name) == 'nan':
                # 如果第0列为空，检查其他列
                for idx in range(1, len(row)):
                    if idx < len(headers) and '产品' in str(headers[idx]):
                        product_name = row[idx]
                        break
            
            row_dict['product_name'] = str(product_name) if product_name else ''
            row_dict['route'] = row[1] if len(row) > 1 else ''
            row_dict['booking_class'] = row[2] if len(row) > 2 else ''
            row_dict['price_increase'] = row[3] if len(row) > 3 else ''
            row_dict['rebate_ratio'] = row[4] if len(row) > 4 else ''
            
            # 产品代码：处理多种格式
            raw_code = row[5] if len(row) > 5 else ''
            if raw_code:
                raw_code = str(raw_code).strip()
                # 清除 */ 前缀和旅游代码等
                code = re.sub(r'^\*/', '', raw_code)
                code = re.sub(r'，旅游代码：.*', '', code)
                code = re.sub(r'\s*，\s*', ' ', code)
                code = code.strip()
                row_dict['product_code'] = code
            else:
                row_dict['product_code'] = ''
            
            # office和渠道
            office_value = row[6] if len(row) > 6 else ''
            remarks_value = row[7] if len(row) > 7 else ''
            remarks_value2 = row[8] if len(row) > 8 else ''
            
            # 处理office
            standard_office_pattern = re.compile(r'\b([A-Z]{3,4}\d{3})\b')
            
            if isinstance(office_value, str):
                # 检查是否是标准office
                if standard_office_pattern.match(office_value) or '/' in office_value and standard_office_pattern.search(office_value):
                    row_dict['office'] = office_value
                    row_dict['remarks'] = str(remarks_value) if remarks_value else ''
                # 检查是否是销售渠道
                elif any(keyword in office_value for keyword in ['GP', 'BSP', 'B2B', 'B3B', 'B4B']):
                    row_dict['sales_channel'] = office_value
                    # 检查备注中是否有office
                    if remarks_value and isinstance(remarks_value, str):
                        office_matches = standard_office_pattern.findall(remarks_value)
                        if office_matches:
                            row_dict['office'] = '/'.join(office_matches)
                        else:
                            row_dict['office'] = ''
                    else:
                        row_dict['office'] = ''
                    row_dict['remarks'] = str(remarks_value2) if remarks_value2 else str(remarks_value) if remarks_value else ''
                else:
                    row_dict['office'] = office_value
                    row_dict['remarks'] = str(remarks_value) if remarks_value else ''
            else:
                row_dict['office'] = ''
                row_dict['remarks'] = str(remarks_value) if remarks_value else ''
            
            row_dict['valid_period'] = str(remarks_value2) if remarks_value2 else ''
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
        has_name = final_df['product_name'].notna() & (final_df['product_name'] != '')

        print(f"\n数据完整度:")
        print(f"  - 有产品名称: {has_name.sum()} ({has_name.sum()*100/len(final_df):.1f}%)")
        print(f"  - 有标准office号: {has_office.sum()} ({has_office.sum()*100/len(final_df):.1f}%)")
        print(f"  - 有销售渠道: {has_channel.sum()} ({has_channel.sum()*100/len(final_df):.1f}%)")
        print(f"  - 有产品代码: {has_code.sum()} ({has_code.sum()*100/len(final_df):.1f}%)")

        print("\n各航司产品代码覆盖情况:")
        code_by_airline = final_df.groupby('airline').agg({
            'airline': 'count',
            'product_name': lambda x: (x.notna() & (x != '')).sum(),
            'product_code': lambda x: (x.notna() & (x != '')).sum()
        })
        code_by_airline.columns = ['总数', '有产品名称', '产品代码数']
        code_by_airline['产品名称%'] = code_by_airline['有产品名称'] * 100 / code_by_airline['总数']
        code_by_airline['产品代码%'] = code_by_airline['产品代码数'] * 100 / code_by_airline['总数']
        print(code_by_airline.round(1).sort_values('总数', ascending=False))

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存: {output_path}")

finally:
    app.quit()

print("\n完成！")
