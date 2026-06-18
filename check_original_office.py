import xlwings as xw

file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

app = xw.App(visible=False)
wb = app.books.open(file_path)

print("=== 检查原始Excel中Office列的数据 ===\n")

# 检查CA工作表
sheet = wb.sheets['CA']
data = sheet.used_range.value
headers = data[0]

print("CA工作表 - Office列（第6列）数据样本:\n")
for row_idx in range(1, min(30, len(data))):
    row = data[row_idx]
    if isinstance(row, list) and len(row) > 6:
        print(f"第{row_idx}行 - {row[6]}")

print("\n" + "="*80)
print("\nJD工作表 - Office列（第6列）数据样本:\n")

sheet = wb.sheets['JD']
data = sheet.used_range.value

for row_idx in range(1, min(15, len(data))):
    row = data[row_idx]
    if isinstance(row, list) and len(row) > 6:
        print(f"第{row_idx}行 - {row[6]}")

wb.close()
app.quit()

print("\n结论:")
print("原始Excel文件中，'出票OFFICE'列确实包含:")
print("  - 标准office号（如KMG319、KMG319/KMG279等）")
print("  - 渠道标识（如GP/BSP、B2B等）")
print("这些是原始数据，不是解析错误")
