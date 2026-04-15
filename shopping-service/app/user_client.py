import httpx

USER_SERVICE_URL = "http://localhost:8081"


async def verify_user_exists(user_id: int) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
            return response.status_code == 200
    except Exception:
        return False
