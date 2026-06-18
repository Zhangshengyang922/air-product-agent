import pandas as pd

df = pd.read_csv('assets/products.csv')

print('CSV数据样本（有product_code的记录）:')
print(df[df['product_code'].notna()][['airline', 'product_name', 'product_code', 'office']].head(20))
