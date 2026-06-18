import pandas as pd
df = pd.read_csv('assets/products_backup.csv')
print(f"Backup文件总数: {len(df)}")
print("\n各航司:")
print(df['airline'].value_counts())
print("\n前10行:")
print(df.head(10))
