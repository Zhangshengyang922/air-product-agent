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

        # 上传企业微信导出的CSV
        with open('exported_from_wechat-MU.csv', 'rb') as f:
            upload_resp = requests.post(
                'http://localhost:8000/api/upload/products',
                files={'file': ('exported_from_wechat-MU.csv', f, 'text/csv')},
                headers={'Authorization': f'Bearer {token}'}
            )

        print(f'上传状态: {upload_resp.status_code}')
        result = upload_resp.json()
        print(f'上传结果: {result}')

        if result.get('success'):
            data = result.get('data', {})
            print(f"\n成功上传 {data.get('added_products', 0)} 条产品")
            print(f"文件类型: {data.get('file_type')}")
            print(f"总产品数: {data.get('total_products')}")
            print(f"跳过: {data.get('skipped_products', 0)}")
        else:
            print(f'上传失败: {result.get("message")}')
    else:
        print(f'登录失败: {login_data.get("message")}')
else:
    print(f'登录请求失败: {login_resp.status_code}')
