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

# 重新加载产品数据
eprint('\n正在重新加载产品数据...')
reload_url = 'http://localhost:8000/api/reload'
headers = {'Authorization': f'Bearer {token}'}

reload_response = requests.post(reload_url, headers=headers, timeout=30)

if reload_response.status_code == 200:
    result = reload_response.json()
    
    if result.get('success'):
        count = result['data']['count']
        eprint(f'✓ 重新加载成功!')
        eprint(f'✓ 产品总数: {count}')
    else:
        eprint(f'重新加载失败: {result.get("message")}')
else:
    eprint(f'重新加载失败，状态码: {reload_response.status_code}')
    eprint(f'错误信息: {reload_response.text}')

# 再次获取产品列表验证
eprint('\n正在验证产品列表...')
products_url = 'http://localhost:8000/api/products'
products_response = requests.get(products_url, headers=headers, timeout=10)

if products_response.status_code == 200:
    result = products_response.json()
    
    if result.get('success') and 'data' in result:
        data = result['data']
        products = data.get('products', [])
        count = data.get('count', len(products))
        
        eprint(f'✓ 验证成功!')
        eprint(f'✓ 产品总数: {count}')
        
        # 统计各航司产品数量
        airline_count = Counter(p.get('airline', '未知') for p in products)
        eprint('\n各航司产品数量:')
        for airline, count in sorted(airline_count.items(), key=lambda x: x[1], reverse=True):
            eprint(f'  {airline}: {count}')
        
        eprint(f'\n✓ 实际统计总数: {sum(airline_count.values())}')
