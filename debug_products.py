import sys
import requests
from collections import Counter

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

# 登录
eprint('正在登录...')
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

# 获取所有产品
eprint('\n正在获取产品列表...')
products_url = 'http://localhost:8000/api/products'
headers = {'Authorization': f'Bearer {token}'}

products_response = requests.get(products_url, headers=headers, timeout=10)

if products_response.status_code == 200:
    result = products_response.json()
    
    if result.get('success') and 'data' in result:
        data = result['data']
        products = data.get('products', [])
        count = data.get('count', len(products))
        
        eprint(f'✓ API返回产品总数: {count}')
        
        # 统计各航司产品数量
        airline_count = Counter(p.get('airline', '未知') for p in products)
        eprint('\n各航司产品数量:')
        for airline, count in sorted(airline_count.items(), key=lambda x: x[1], reverse=True):
            eprint(f'  {airline}: {count}')
        
        # 统计总数
        total = sum(airline_count.values())
        eprint(f'\n✓ 实际统计总数: {total}')
        
        # 显示航司列表
        eprint(f'\n航司列表: {sorted(airline_count.keys())}')
    else:
        eprint(f'响应格式错误')
        eprint(f'完整响应: {result}')
else:
    eprint(f'获取产品失败')
    eprint(f'状态码: {products_response.status_code}')
    eprint(f'响应: {products_response.text}')
