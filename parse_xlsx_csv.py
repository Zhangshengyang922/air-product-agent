# -*- coding: utf-8 -*-
import xlwings as xw
import pandas as pd
import os

# 文件路径
file_path = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'
output_path = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/new_products.csv'

print("开始读取Excel文件...")

# 使用xlwings读取
app = xw.App(visible=False)

try:
    wb = app.books.open(file_path)

    print(f"工作表数量: {len(wb.sheets)}")

    all_data = []

    # 遍历所有工作表
    for sheet in wb.sheets:
        print(f"\n读取工作表: {sheet.name}")

        # 读取数据
        used_range = sheet.used_range
        data = used_range.value

        if data and len(data) > 1:  # 有数据且超过标题行
            # 检查数据格式
            if not isinstance(data[0], list):
                print(f"  跳过 {sheet.name}: 数据格式不正确")
                continue

            # 转换为DataFrame
            try:
                df = pd.DataFrame(data[1:], columns=data[0])

                # 添加来源工作表信息
                df['source_sheet'] = sheet.name

                all_data.append(df)
                print(f"  读取 {len(df)} 条记录")
            except Exception as e:
                print(f"  读取 {sheet.name} 失败: {e}")

    # 关闭工作簿
    wb.close()

    # 合并所有数据
    if all_data:
        # 统一列名（转换为小写并去掉空格）
        for df in all_data:
            df.columns = [str(col).lower().replace(' ', '_').strip() for col in df.columns]

        # 使用外连接合并所有数据
        merged_df = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"\n合并后总记录数: {len(merged_df)}")

        # 保存为CSV
        merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"已保存到: {output_path}")

        # 显示列名
        print(f"\n列名: {list(merged_df.columns)}")

        # 统计各航司
        if 'airline' in merged_df.columns:
            print("\n各航司产品数量:")
            print(merged_df['airline'].value_counts())

finally:
    app.quit()

print("\n完成！")
