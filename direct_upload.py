import requests
import json
import pandas as pd

# 读取CSV并转换
df = pd.read_csv('assets/products.csv', encoding='utf-8')

# 字段映射
field_mapping = {
    '航司代码': 'airline',
    '航司名称': 'airline_name',
    '产品名称': 'product_name',
    '航线': 'route',
    '订座舱位': 'booking_class',
    '上浮价格': 'price_increase',
    '政策返点': 'rebate_ratio',
    '产品代码': 'policy_code',
    '出票OFFICE': 'office',
    '备注': 'remarks',
    '产品有限期': 'valid_period'
}

# 重命名列
df = df.rename(columns=field_mapping)

# 清理价格数据
import re
def clean_price(val):
    if pd.isna(val):
        return 0
    match = re.search(r'(\d+)', str(val))
    return int(match.group(1)) if match else 0

df['price_increase'] = df['price_increase'].apply(clean_price)
df['rebate_ratio'] = df['rebate_ratio'].apply(clean_price)

# 填充空值
for col in ['office', 'remarks', 'valid_period', 'policy_code']:
    df[col] = df[col].fillna('').astype(str)

# 添加必要字段
import uuid
df['ticket_type'] = 'ALL'
df['policy_identifier'] = ''
df['product_id'] = df.apply(lambda x: str(uuid.uuid4()).replace('-', '')[:16], axis=1)

# 转换为JSON
products_json = df.to_json(orient='records', force_ascii=False)
products_data = json.loads(products_json)

print(f'准备上传 {len(products_data)} 条产品')

# 获取token
login_resp = requests.post(
    'http://localhost:8000/api/login',
    json={'username': 'YNTB', 'password': 'yntb123'}
)

if login_resp.status_code == 200:
    login_data = login_resp.json()
    if login_data.get('success'):
        token = login_data['token']
        print('登录成功')

        # 上传数据
        upload_resp = requests.post(
            'http://localhost:8000/api/upload/products',
            files={'file': ('products.csv', products_json, 'application/json')},
            headers={'Authorization': f'Bearer {token}'}
        )

        print(f'上传状态: {upload_resp.status_code}')
        result = upload_resp.json()
        print(f'上传结果: {result}')

        if result.get('success'):
            print(f"\n成功上传 {result.get('data', {}).get('added_products', 0)} 条产品")
        else:
            print(f'上传失败: {result.get("message")}')
    else:
        print(f'登录失败: {login_data.get("message")}')
else:
    print(f'登录请求失败: {login_resp.status_code}')
