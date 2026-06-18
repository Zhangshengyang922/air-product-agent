import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/products.csv'

print("=== 最终重新解析产品数据 ===\n")

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
            
            # office和渠道：根据列结构动态判断
            # 标准结构：第6列是office，第7列是备注
            # 特殊结构（如3U）：第6列是票证类型，第7列是office
            office_value = row[6] if len(row) > 6 else ''
            remarks_value = row[7] if len(row) > 7 else ''
            remarks_value2 = row[8] if len(row) > 8 else ''
            
            # 检查第6列是否是office或票证类型
            standard_office_pattern = re.compile(r'^([A-Z]{3,4}\d{3})$')
            
            if isinstance(office_value, str):
                # 如果第6列是office
                if standard_office_pattern.match(office_value) or '/' in office_value:
                    row_dict['office'] = office_value
                    row_dict['remarks'] = str(remarks_value) if remarks_value else ''
                # 如果第6列是票证类型（如GP/BSP）
                elif 'GP' in office_value or 'BSP' in office_value or 'B2B' in office_value:
                    # 第7列可能是office或备注
                    row_dict['sales_channel'] = office_value
                    if isinstance(remarks_value, str) and (standard_office_pattern.match(remarks_value) or 'KMG' in remarks_value):
                        row_dict['office'] = remarks_value
                        row_dict['remarks'] = str(remarks_value2) if remarks_value2 else ''
                    else:
                        row_dict['remarks'] = str(remarks_value) if remarks_value else ''
                else:
                    row_dict['office'] = office_value
                    row_dict['remarks'] = str(remarks_value) if remarks_value else ''
            else:
                row_dict['office'] = ''
                row_dict['remarks'] = str(remarks_value) if remarks_value else ''
            
            row_dict['valid_period'] = str(remarks_value2) if len(row) > 8 and remarks_value2 else ''
            
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

        print("\n各航司产品代码覆盖情况:")
        code_by_airline = final_df.groupby('airline').agg({
            'airline': 'count',
            'product_code': lambda x: (x.notna() & (x != '')).sum()
        })
        code_by_airline.columns = ['总数', '产品代码数']
        code_by_airline['覆盖率'] = code_by_airline['产品代码数'] * 100 / code_by_airline['总数']
        print(code_by_airline.round(1).sort_values('覆盖率', ascending=False))

        # 保存
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n已保存: {output_path}")

finally:
    app.quit()

print("\n完成！")
