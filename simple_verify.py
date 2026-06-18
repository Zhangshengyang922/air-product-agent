import requests
import sys

print("Service Status Check...")
try:
    response = requests.get('http://localhost:8000/api/products', timeout=5)
    data = response.json()
    if data['success']:
        print(f"OK - Total products: {data['data']['count']}")
        
        # Check statistics
        resp2 = requests.get('http://localhost:8000/api/statistics', timeout=5)
        stats = resp2.json()
        if stats['success']:
            sdata = stats['data']
            print(f"OK - Airlines: {sdata['total_airlines']}")
            print(f"OK - Routes: {sdata['total_routes']}")
            print(f"OK - Total: {sdata['total_products']}")
            
            with open('verification_ok.txt', 'w') as f:
                f.write("VERIFICATION SUCCESSFUL\n")
                f.write(f"Products: {data['data']['count']}\n")
                f.write(f"Airlines: {sdata['total_airlines']}\n")
                f.write(f"Routes: {sdata['total_routes']}\n")
            
            print("Verification complete - see verification_ok.txt")
    else:
        print("FAILED - API returned error")
        sys.exit(1)
except Exception as e:
    print(f"FAILED - {e}")
    sys.exit(1)
