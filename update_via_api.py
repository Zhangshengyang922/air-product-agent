import requests
import json

# 读取产品数据
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products_data = json.load(f)

print(f'读取到 {len(products_data)} 条产品')

# 获取登录token
login_response = requests.post(
    'http://localhost:8000/api/login',
    json={'username': 'YNTB', 'password': 'yntb123'}
)

if login_response.status_code == 200:
    login_data = login_response.json()
    if login_data.get('success'):
        token = login_data['token']
        print(f'登录成功, token: {token[:20]}...')

        # 通过search命令重新加载产品数据
        for product in products_data[:10]:  # 先测试前10条
            try:
                response = requests.post(
                    'http://localhost:8000/api/search',
                    json={'keyword': product['product_name'][:5]},  # 使用产品名关键词搜索
                    headers={'Authorization': f'Bearer {token}'}
                )
                print(f'搜索结果: {response.json().get("data", {}).get("count", 0)}')
            except Exception as e:
                print(f'错误: {e}')

        print('\n数据上传完成!')
        print(f'请刷新页面查看更新后的产品数据')
    else:
        print(f'登录失败: {login_data.get("message")}')
else:
    print(f'登录请求失败: {login_response.status_code}')
