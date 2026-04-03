"""
更新KY航司产品数据
"""
import pandas as pd

# 1. 读取现有的products.csv
print("[STEP 1] 读取现有数据...")
existing_df = pd.read_csv('assets/products.csv', encoding='utf-8-sig')
print(f"现有: {len(existing_df)} 条")

# 2. 读取新的KY CSV
print("\n[STEP 2] 读取KY新数据...")
new_ky_df = pd.read_csv('各航司汇总产品-KY.csv', encoding='utf-8-sig')
new_ky_df = new_ky_df.fillna('')
print(f"新KY数据: {len(new_ky_df)} 条")

# 3. 添加航司代码
new_ky_df['航司代码'] = 'KY'
new_ky_df['航司名称'] = 'KY'

# 4. 删除旧的KY数据
existing_df = existing_df[existing_df['航司代码'] != 'KY']
print(f"删除旧KY后: {len(existing_df)} 条")

# 5. 合并
required_cols = ['航司代码', '航司名称', '产品名称', '航线', '订座舱位', '上浮价格', '政策返点', '产品代码', '出票OFFICE', '备注', '航司结算方式', '产品有限期', '司结算方式', '票证类型']
for col in required_cols:
    if col not in new_ky_df.columns:
        new_ky_df[col] = ''

new_ky_df = new_ky_df[required_cols]
final_df = pd.concat([existing_df, new_ky_df], ignore_index=True)

# 6. 保存
print("\n[STEP 3] 保存数据...")
final_df.to_csv('assets/products.csv', index=False, encoding='utf-8-sig')
print(f"最终: {len(final_df)} 条")

# 7. 统计
print("\n[统计]")
print(f"KY产品数: {len(final_df[final_df['航司代码'] == 'KY'])} 条")
print(f"总航司数: {final_df['航司代码'].nunique()} 个")
print("\n完成!")