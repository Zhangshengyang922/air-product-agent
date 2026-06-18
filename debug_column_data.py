import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("=== 检查Excel文件中产品代码和office列的实际数据 ===\n")

app = xw.App(visible=False)
wb = app.books.open(file_path)

# 检查几个工作表的详细数据
for sheet in [wb.sheets[0], wb.sheets[4]]:  # MU和CZ
    print(f"\n{'='*80}")
    print(f"工作表: {sheet.name}")
    print('='*80)
    
    used_range = sheet.used_range
    data = used_range.value
    
    if not data or len(data) < 2:
        print("  无数据")
        continue
    
    headers = data[0]
    print(f"\n列结构:")
    for idx, header in enumerate(headers):
        print(f"  第{idx}列: {header}")
    
    print(f"\n前10行数据（第5、6列）:")
    for row_idx in range(1, min(11, len(data))):
        row = data[row_idx]
        if isinstance(row, list) and len(row) > 6:
            print(f"\n第{row_idx}行:")
            print(f"  第0列（产品名称）: {row[0] if len(row) > 0 else ''}")
            print(f"  第4列（政策返点）: {row[4] if len(row) > 4 else ''}")
            print(f"  第5列（产品代码）: {row[5] if len(row) > 5 else ''}")
            print(f"  第6列（出票OFFICE）: {row[6] if len(row) > 6 else ''}")
            print(f"  第7列（备注）: {(str(row[7])[:50] if len(row) > 7 and row[7] else '')[:50]}")

wb.close()
app.quit()

# 检查当前CSV数据
print("\n\n" + "="*80)
print("=== 检查当前CSV中的数据 ===")
print("="*80)

df = pd.read_csv('assets/products.csv')

# 检查product_code列
print("\n产品代码列（product_code）数据:")
code_samples = df[df['product_code'].notna() & (df['product_code'] != '')][['airline', 'product_name', 'product_code', 'office']].head(20)
for idx, row in code_samples.iterrows():
    print(f"{row['airline']} - 产品代码:{row['product_code']:<15} Office:{row['office']:<30} {row['product_name'][:30]}")

# 检查office列中的异常值
print("\n\n可能不是office号的值（如'GP/BSP'等）:")
suspicious_office = df[df['office'].str.contains('GP|BSP|B2B', na=False, case=False)][['airline', 'product_name', 'office']].head(30)
for idx, row in suspicious_office.iterrows():
    print(f"{row['airline']} - {row['office']:<30} {row['product_name'][:40]}")
