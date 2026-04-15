import requests
import sys

USER_SERVICE_URL = "http://localhost:8081"

print("=" * 50)
print("测试用户服务连接...")
print("=" * 50)

try:
    r = requests.get(f"{USER_SERVICE_URL}/")
    print(f"✓ 用户服务根路径响应: {r.status_code}")
    print(f"  内容: {r.text}")
except Exception as e:
    print(f"✗ 无法连接用户服务: {e}")
    print("\n请确保用户服务正在运行:")
    print("  cd user-service")
    print("  python main.py")
    sys.exit(1)

print("\n" + "=" * 50)
print("测试获取用户列表...")
print("=" * 50)
try:
    r = requests.get(f"{USER_SERVICE_URL}/api/users")
    print(f"✓ 状态码: {r.status_code}")
    print(f"✓ 响应: {r.json()}")
except Exception as e:
    print(f"✗ 失败: {e}")
