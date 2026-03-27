import requests
import json

# 读取产品数据
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products_data = json.load(f)

print(f'读取到 {len(products_data)} 条产品')

# 上传到后端
response = requests.post(
    'http://localhost:8000/api/upload/json',
    json={'products': products_data},
    headers={'Authorization': 'Bearer test_token'}
)

print(f'响应状态: {response.status_code}')
print(f'响应内容: {response.text}')
