import pandas as pd
df = pd.read_csv('assets/products.csv')
print('Total:', len(df))
print('\nAirline counts:')
print(df['airline'].value_counts().head(30))
print('\nSample rows:')
print(df[df['airline']=='CZ'][['airline','product_name','rebate_ratio','office']].head())
