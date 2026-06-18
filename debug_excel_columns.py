import xlwings as xw
import pandas as pd

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("=== 检查Excel文件列结构 ===\n")

app = xw.App(visible=False)
wb = app.books.open(file_path)

# 检查前3个工作表的详细结构
sheet_count = 0
for sheet in wb.sheets:
    if sheet_count >= 3:
        break
    print(f"\n{'='*60}")
    print(f"工作表: {sheet.name}")
    print('='*60)
    
    used_range = sheet.used_range
    data = used_range.value
    
    if not data or len(data) < 2:
        print("  无数据")
        continue
    
    headers = data[0]
    print(f"\n列数: {len(headers)}")
    print(f"\n列名（按顺序）:")
    for idx, header in enumerate(headers):
        print(f"  第{idx}列: {header}")
    
    # 显示前3行数据
    print(f"\n前3行数据:")
    for row_idx in range(1, min(4, len(data))):
        print(f"\n  第{row_idx}行:")
        for col_idx, cell in enumerate(data[row_idx]):
            if col_idx < len(headers):
                header = headers[col_idx]
                value = str(cell)[:50] if cell is not None else ""
                print(f"    {header}: {value}")

wb.close()
app.quit()

print("\n" + "="*60)
print("=== 数据列对应关系分析 ===")
print("="*60)
print("\n根据之前的检查，标准列顺序应该是:")
print("  第0列: 产品名称")
print("  第1列: 航线")  
print("  第2列: 订座舱位")
print("  第3列: 上浮价格")
print("  第4列: 政策返点")
print("  第5列: 产品代码")
print("  第6列: 出票OFFICE")
print("  第7列: 备注")
print("  第8列: 产品有效期")
print("\n但实际数据中:")
print("  office列存储的是备注内容（第7列）")
print("  真正的office号（第6列）和产品代码（第5列）没有正确提取")
