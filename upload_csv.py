import requests

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

        # 上传CSV文件
        with open('assets/products.csv', 'rb') as f:
            upload_resp = requests.post(
                'http://localhost:8000/api/upload/products',
                files={'file': ('products.csv', f, 'text/csv')},
                headers={'Authorization': f'Bearer {token}'}
            )

        print(f'上传状态: {upload_resp.status_code}')
        result = upload_resp.json()
        print(f'上传结果: {result}')

        if result.get('success'):
            print(f"\n成功上传 {result.get('data', {}).get('added_products', 0)} 条产品")
            print(f"文件类型: {result.get('data', {}).get('file_type')}")
        else:
            print(f'上传失败: {result.get("message")}')
    else:
        print(f'登录失败: {login_data.get("message")}')
else:
    print(f'登录请求失败: {login_resp.status_code}')
