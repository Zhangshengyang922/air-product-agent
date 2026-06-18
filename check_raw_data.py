import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("=== 检查原始Excel中3U、MF航司的数据 ===\n")

app = xw.App(visible=False)

for sheet_name in ['3U', 'MF']:
    sheet = app.books.open(file_path).sheets[sheet_name]
    used_range = sheet.used_range
    data = used_range.value
    
    print(f"\n{'='*80}")
    print(f"{sheet_name}工作表")
    print('='*80)
    
    if not data or len(data) < 2:
        print("无数据")
        continue
    
    headers = data[0]
    print(f"\n列结构:")
    for idx, header in enumerate(headers):
        print(f"  第{idx}列: {header}")
    
    print(f"\n前20行数据（产品名称、舱位、备注）:")
    for row_idx in range(1, min(21, len(data))):
        row = data[row_idx]
        if isinstance(row, list):
            print(f"\n第{row_idx}行:")
            print(f"  第0列（产品名称）: {row[0] if len(row) > 0 else 'nan'}")
            print(f"  第4列（政策返点）: {row[4] if len(row) > 4 else 'nan'}")
            print(f"  第5列（产品代码）: {row[5] if len(row) > 5 else 'nan'}")
            print(f"  第6列（出票OFFICE）: {row[6] if len(row) > 6 else 'nan'}")
            print(f"  第7列（备注）: {(str(row[7])[:100] if len(row) > 7 and row[7] else 'nan')[:100]}")
            print(f"  第8列（有效期）: {row[8] if len(row) > 8 else 'nan'}")

app.quit()
