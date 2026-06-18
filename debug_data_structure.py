import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

app = xw.App(visible=False)

try:
    wb = app.books.open(file_path)
    sheet = wb.sheets['MU']

    # 读取前5行
    data = sheet.range('A1:J6').value

    print("MU工作表前5行原始数据:")
    for i, row in enumerate(data):
        if row:
            row_str = []
            for j, cell in enumerate(row):
                cell_str = str(cell)[:30] if cell else ''
                row_str.append(f"[{j}:{cell_str}]")
            print(f"  行{i}: {' '.join(row_str)}")

    wb.close()

finally:
    app.quit()
