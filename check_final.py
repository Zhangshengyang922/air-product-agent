import pandas as pd
df = pd.read_csv('assets/products.csv')
print(f"总数: {len(df)}")
print(f"\nairline列前10个值: {df['airline'].head(10).tolist()}")
print(f"\nairline列唯一值: {df['airline'].unique()}")
print(f"\nairline非空数: {df['airline'].notna().sum()}")
print(f"\n各航司计数: {df['airline'].value_counts()}")
