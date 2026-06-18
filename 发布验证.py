import requests
import json

print("=" * 80)
print("智能体发布验证")
print("=" * 80)

# 测试API接口
tests = [
    {
        "name": "获取所有产品",
        "url": "http://localhost:8000/api/products",
        "check": lambda r: r['success'] and r['data']['count'] > 0
    },
    {
        "name": "获取统计数据",
        "url": "http://localhost:8000/api/statistics",
        "check": lambda r: r['success'] and 'total_products' in r['data']
    },
    {
        "name": "按航空公司筛选（MU）",
        "url": "http://localhost:8000/api/products/airline/MU",
        "check": lambda r: r['success'] and len(r['data']['products']) > 0
    },
    {
        "name": "搜索产品（里程优享）",
        "url": "http://localhost:8000/api/products/search?keyword=里程优享",
        "check": lambda r: r['success'] and len(r['data']['products']) > 0
    }
]

results = []
for test in tests:
    try:
        response = requests.get(test['url'])
        data = response.json()
        passed = test['check'](data)
        results.append({
            "name": test['name'],
            "status": "✅ 通过" if passed else "❌ 失败",
            "result": data.get('message', '')
        })
    except Exception as e:
        results.append({
            "name": test['name'],
            "status": "❌ 错误",
            "result": str(e)
        })

# 显示测试结果
print("\nAPI接口测试:")
print("-" * 80)
for result in results:
    print(f"{result['status']} {result['name']}")
    if result['result']:
        print(f"   {result['result']}")

# 统计数据
print("\n" + "=" * 80)
print("产品数据统计:")
print("-" * 80)
try:
    response = requests.get('http://localhost:8000/api/statistics')
    stats = response.json()
    if stats['success']:
        data = stats['data']
        print(f"总产品数: {data['total_products']}")
        print(f"航空公司数: {data['total_airlines']}")
        print(f"航线数: {data['total_routes']}")
        print("\n各航空公司产品数量:")
        for airline, count in sorted(data['products_by_airline'].items())[:10]:
            print(f"  {airline}: {count} 个产品")
        
        print("\n票证类型分布:")
        for ticket_type, count in data['products_by_ticket_type'].items():
            print(f"  {ticket_type}: {count} 个产品")
except Exception as e:
    print(f"获取统计数据失败: {e}")

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)
