import pandas as pd

df = pd.read_csv('assets/products.csv')

print("=== 检查3U和MF的产品代码 ===\n")

for airline in ['3U', 'MF']:
    print(f"\n{'='*80}")
    print(f"{airline}航司 - 产品代码情况")
    print('='*80)
    
    airline_df = df[df['airline'] == airline]
    has_code = airline_df[airline_df['product_code'].notna() & (airline_df['product_code'] != '')]
    no_code = airline_df[airline_df['product_code'].isna() | (airline_df['product_code'] == '')]
    
    print(f"\n有产品代码: {len(has_code)}条")
    print("样本:")
    for idx, row in has_code.head(10).iterrows():
        print(f"  {row['product_code']:<20} {row['product_name'][:40]}")
    
    print(f"\n无产品代码: {len(no_code)}条")
    print("样本:")
    for idx, row in no_code.head(10).iterrows():
        print(f"  {row['product_name'][:40]}")
        if pd.notna(row['booking_class']) and row['booking_class']:
            print(f"    舱位: {str(row['booking_class'])[:60]}")
