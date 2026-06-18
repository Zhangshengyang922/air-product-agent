with open('各航司汇总产品.csv', 'rb') as f:
    data = f.read()
print('First 500 bytes:', repr(data[:500]))
print('\nFile size:', len(data))
