import sys
import requests
import pandas as pd
from collections import Counter

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

# 1. 检查CSV文件的实际产品数量
csv_file = r'c:\Users\Administrator\OneDrive\桌面\air_prd_agent\assets\products.csv'
df = pd.read_csv(csv_file, encoding='utf-8-sig')
actual_count = len(df)
eprint(f'CSV文件中的产品数量: {actual_count}')

# 2. 登录
eprint('\n正在登录...')
login_url = 'http://localhost:8000/api/login'
login_response = requests.post(login_url, json={
    'username': 'YNTB',
    'password': 'yntb123'
}, timeout=10)

if login_response.status_code != 200:
    eprint(f'登录失败')
    sys.exit(1)

token = login_response.json().get('token', '')
eprint('登录成功')

# 3. 获取当前内存中的产品数量
eprint('\n正在获取内存中的产品数量...')
products_url = 'http://localhost:8000/api/products'
headers = {'Authorization': f'Bearer {token}'}

products_response = requests.get(products_url, headers=headers, timeout=10)

if products_response.status_code == 200:
    result = products_response.json()
    
    if result.get('success') and 'data' in result:
        data = result['data']
        count = data.get('count', len(data.get('products', [])))
        
        eprint(f'内存中的产品数量: {count}')
        eprint(f'CSV文件中的产品数量: {actual_count}')
        
        if count == actual_count:
            eprint('\n✓ 内存和CSV文件中的产品数量一致!')
        else:
            eprint(f'\n✗ 产品数量不一致，相差 {actual_count - count} 个')
            eprint('\n需要重新加载产品数据')
            eprint('\n请按以下步骤操作:')
            eprint('1. 重启服务器: 运行 restart_and_upload.bat')
            eprint('2. 或者调用重新加载API: POST /api/reload')
else:
    eprint(f'获取产品失败')
