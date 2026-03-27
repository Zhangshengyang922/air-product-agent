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

        # 直接创建CSV格式的临时文件
        csv_content = """airline,product_name,route,booking_class,price_increase,rebate_ratio,office,remarks,valid_period,ticket_type,policy_identifier,policy_code
HU,智选经济舱,所有航线,Q舱,390,120,,,,,ALL,,
HU,优选经济舱,所有航线,E舱 E舱上浮220元现返70元，上浮250元现返80元,220/250,70/80,,,,,ALL,,
HU,优享贵宾室,适用于HU/CN国内自营航班,H/K/L/M/X/V/N/A/U/T，CVG1(北京）,220,40,CVG1,,2026年9月15日(含）,ALL,,
HU,优享贵宾室,适用于HU/CN国内自营航班,H/K/L/M/X/V/N/A/U/T，CVG1(北京）,220,40,CVG1,,2026年9月15日(含）,ALL,,
"""
        
        with open('temp_products.csv', 'w', encoding='utf-8-sig') as f:
            f.write(csv_content)
        
        # 上传CSV文件
        with open('temp_products.csv', 'rb') as f:
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
        else:
            print(f'上传失败: {result.get("message")}')
    else:
        print(f'登录失败: {login_data.get("message")}')
else:
    print(f'登录请求失败: {login_resp.status_code}')
