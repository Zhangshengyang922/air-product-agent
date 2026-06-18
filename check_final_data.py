import pandas as pd
df = pd.read_csv('assets/products.csv')
print(f"总数: {len(df)}")
print(f"\n列名: {list(df.columns)}")
print(f"\n有返点: {(df['rebate_ratio'].notna() & (df['rebate_ratio']!='')).sum()}")
print(f"有office: {(df['office'].notna() & (df['office']!='')).sum()}")

print("\n前10行:")
print(df[['airline', 'product_name', 'rebate_ratio', 'office']].head(10).to_string(index=False))

print("\nCZ前10行:")
cz_df = df[df['airline']=='CZ']
print(cz_df[['product_name', 'rebate_ratio', 'office']].head(10).to_string(index=False))
