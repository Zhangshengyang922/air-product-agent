# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("检查Excel文件结构...\n")

app = xw.App(visible=False)

try:
    wb = app.books.open(file_path)

    # 检查几个主要工作表的结构
    sample_sheets = ['CZ', '3U', 'HU', 'EU', 'CA']

    for sheet_name in sample_sheets:
        if sheet_name in [s.name for s in wb.sheets]:
            sheet = wb.sheets[sheet_name]
            print(f"\n{'='*80}")
            print(f"工作表: {sheet_name}")
            print(f"{'='*80}")

            # 读取前10行数据
            data = sheet.range('A1:L20').value
            if data:
                print(f"\n前10行数据:")
                for i, row in enumerate(data[:10]):
                    row_str = []
                    for j, cell in enumerate(row):
                        if cell is not None:
                            cell_str = str(cell)[:40]  # 限制每个单元格显示长度
                            row_str.append(cell_str)
                        else:
                            row_str.append('')
                    print(f"行{i+1:2d}: {' | '.join(row_str)}")

    # 检查完整列数最多的几个工作表
    print(f"\n\n{'='*80}")
    print("检查列数最多的工作表")
    print(f"{'='*80}\n")

    for sheet in wb.sheets:
        used_range = sheet.used_range
        if used_range.value and len(used_range.value) > 1:
            headers = used_range.value[0]
            if isinstance(headers, list):
                print(f"\n{sheet.name}: {len(headers)} 列")
                print(f"列名: {headers}")
                if len(headers) > 12:
                    print(f"  前12列: {headers[:12]}")
                    print(f"  后续列: {headers[12:]}")

    wb.close()

finally:
    app.quit()

print("\n\n检查完成！")
