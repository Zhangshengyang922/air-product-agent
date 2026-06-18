# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

app = xw.App(visible=False)

try:
    wb = app.books.open(file_path)

    # 检查几个工作表的列
    for sheet_name in ['CZ', '3U', 'EU']:
        sheet = wb.sheets[sheet_name]
        data = sheet.used_range.value

        if data and len(data) > 1:
            headers = data[0]
            print(f"\n{sheet_name} 工作表列名:")
            for i, header in enumerate(headers):
                print(f"  列{i+1}: {repr(header)}")

            # 查看前几行的第5列（政策返点）
            print(f"\n{sheet_name} 前几行数据:")
            for i, row in enumerate(data[1:5]):
                if isinstance(row, list) and len(row) > 5:
                    print(f"  行{i+2}: 产品={row[0][:30] if row[0] else 'N/A'} | "
                          f"价格={row[3] if len(row) > 3 else 'N/A'} | "
                          f"返点={row[4] if len(row) > 4 else 'N/A'} | "
                          f"office={row[7] if len(row) > 7 else 'N/A'}")

    wb.close()

finally:
    app.quit()
