import requests
import sys

SHOPPING_SERVICE_URL = "http://localhost:8082"

print("=" * 50)
print("测试购物服务连接...")
print("=" * 50)

try:
    r = requests.get(f"{SHOPPING_SERVICE_URL}/")
    print(f"✓ 购物服务根路径响应: {r.status_code}")
    print(f"  内容: {r.text}")
except Exception as e:
    print(f"✗ 无法连接购物服务: {e}")
    print("\n请确保购物服务正在运行:")
    print("  cd shopping-service")
    print("  python main.py")
    sys.exit(1)

print("\n" + "=" * 50)
print("测试获取商品列表...")
print("=" * 50)
try:
    r = requests.get(f"{SHOPPING_SERVICE_URL}/api/products")
    print(f"✓ 状态码: {r.status_code}")
    print(f"✓ 响应: {r.json()}")
except Exception as e:
    print(f"✗ 失败: {e}")
