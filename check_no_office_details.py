import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 检查无office号航司的备注内容 ===\n")

# 找出没有标准office号的航司
no_office_airlines = df[df['office'].isna() | (df['office'] == '')]['airline'].unique()
print(f"没有标准office号的航司: {len(no_office_airlines)}个")
print(f"航司代码: {list(no_office_airlines)}\n")

# 查看这些航司的备注内容
for airline in ['CA', 'CZ', '3U', 'EU', 'ZH', 'MF', 'SC', 'DR']:
    print(f"\n{'='*80}")
    print(f"{airline}航司 - 备注内容样本（前15条）")
    print('='*80)
    
    airline_df = df[df['airline'] == airline]
    for idx, row in airline_df.head(15).iterrows():
        print(f"\n产品: {row['product_name'][:50]}")
        if pd.notna(row['remarks']) and row['remarks']:
            print(f"备注: {str(row['remarks'])[:150]}")
        if pd.notna(row['booking_class']) and row['booking_class']:
            print(f"舱位: {str(row['booking_class'])[:150]}")
        if pd.notna(row['rebate_ratio']) and row['rebate_ratio']:
            print(f"返点: {str(row['rebate_ratio'])[:100]}")
