import xlwings as xw
import pandas as pd
import re

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("=== 检查3U和MF的原始数据问题 ===\n")

app = xw.App(visible=False)

for sheet_name in ['3U', 'MF']:
    sheet = app.books.open(file_path).sheets[sheet_name]
    used_range = sheet.used_range
    data = used_range.value
    
    print(f"\n{'='*80}")
    print(f"{sheet_name}工作表 - 数据结构")
    print('='*80)
    
    if not data or len(data) < 2:
        print("无数据")
        continue
    
    headers = data[0]
    print(f"\n列数: {len(headers)}")
    
    # 检查前30行数据
    empty_name_count = 0
    has_code_count = 0
    
    for row_idx in range(1, min(31, len(data))):
        row = data[row_idx]
        if isinstance(row, list):
            product_name = row[0] if len(row) > 0 else None
            product_code = row[5] if len(row) > 5 else None
            
            if not product_name or str(product_name) == 'nan':
                empty_name_count += 1
            
            if product_code and str(product_code) != 'nan' and str(product_code).strip():
                has_code_count += 1
    
    print(f"\n数据统计:")
    print(f"  总行数: {len(data)-1}")
    print(f"  产品名称为空: {empty_name_count}")
    print(f"  有产品代码: {has_code_count}")

app.quit()

print("\n\n现在读取CSV并比较:")
df = pd.read_csv('assets/products.csv')

for airline in ['3U', 'MF']:
    airline_df = df[df['airline'] == airline]
    total = len(airline_df)
    has_name = airline_df['product_name'].notna().sum()
    has_code = airline_df['product_code'].notna().sum()
    
    print(f"\n{airline}:")
    print(f"  CSV总记录: {total}")
    print(f"  有产品名称: {has_name}")
    print(f"  有产品代码: {has_code}")
