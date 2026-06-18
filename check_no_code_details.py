import pandas as pd
import re

df = pd.read_csv('assets/products.csv')

print("=== 检查无产品代码航司的详细信息 ===\n")

# 找出没有产品代码的航司
no_code_airlines = df[df['product_code'].isna() | (df['product_code'] == '')]['airline'].unique()

# 检查几个航司的详细信息
for airline in ['3U', 'MF', 'TV', 'EU', 'KY']:
    print(f"\n{'='*80}")
    print(f"{airline}航司 - 无产品代码记录的详细信息（前10条）")
    print('='*80)
    
    airline_df = df[df['airline'] == airline]
    no_code_df = airline_df[airline_df['product_code'].isna() | (airline_df['product_code'] == '')]
    
    for idx, row in no_code_df.head(10).iterrows():
        print(f"\n产品: {row['product_name']}")
        if pd.notna(row['booking_class']) and row['booking_class']:
            print(f"舱位: {str(row['booking_class'])[:200]}")
        if pd.notna(row['remarks']) and row['remarks']:
            print(f"备注: {str(row['remarks'])[:300]}")
        if pd.notna(row['rebate_ratio']) and row['rebate_ratio']:
            print(f"返点: {str(row['rebate_ratio'])[:100]}")
