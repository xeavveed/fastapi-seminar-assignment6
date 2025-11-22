import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest.fixture
def store_create_request():
    return {
        "store_name": "My Store",
        "address": "1, Gwanak-ro, Gwanak-gu, Seoul, Republic of Korea",
        "email": "fastapi@wafflestudio.com",
        "phone_number": "010-1234-5678",
        "delivery_fee": 3500
    }

@pytest_asyncio.fixture
async def store(
    async_client: AsyncClient,
    access_token: str,
    store_create_request: dict,
) -> dict:
    res = await async_client.post("/api/stores/", json=store_create_request, headers={"Authorization": f"Bearer {access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["store_name"] == store_create_request["store_name"]
    assert res_json["address"] == store_create_request["address"]
    assert res_json["email"] == store_create_request["email"]
    assert res_json["phone_number"] == store_create_request["phone_number"]
    assert res_json["delivery_fee"] == store_create_request["delivery_fee"]
    return res.json()

@pytest_asyncio.fixture
async def store_2(
    async_client: AsyncClient,
    another_user_access_token: str,
) -> dict:
    req = {
        "store_name": "Another Store",
        "address": "2, Gwanak-ro, Gwanak-gu, Seoul, Republic of Korea",
        "email": "fastapi2@wafflestudio.com",
        "phone_number": "010-2345-6789",
        "delivery_fee": 4000
    }
    res = await async_client.post("/api/stores/", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["store_name"] == req["store_name"]
    assert res_json["address"] == req["address"]
    assert res_json["email"] == req["email"]
    assert res_json["phone_number"] == req["phone_number"]
    assert res_json["delivery_fee"] == req["delivery_fee"]
    return res.json()