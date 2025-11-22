from httpx import AsyncClient
import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def item_create_request():
    return {
        "item_name": "초콜릿",
        "price": 5000,
        "stock": 20
    }

@pytest_asyncio.fixture(scope="function")
async def item(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
    item_create_request: dict
):
    store_id = store["id"]
    res = await async_client.post("/api/items/", json=item_create_request, headers={"Authorization": f"Bearer {access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["id"] is not None
    assert res_json["item_name"] == item_create_request["item_name"]
    assert res_json["price"] == item_create_request["price"]
    assert res_json["stock"] == item_create_request["stock"]
    return res.json()

@pytest_asyncio.fixture(scope="function")
async def item_2(
    async_client: AsyncClient,
    another_user_access_token: str,
    store_2: dict,
) -> dict:
    req = {
        "item_name": "사탕",
        "price": 3000,
        "stock": 30
    }
    store_id = store_2["id"]
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["item_name"] == req["item_name"]
    assert res_json["price"] == req["price"]
    assert res_json["stock"] == req["stock"]
    return res.json()

@pytest_asyncio.fixture(scope="function")
async def items(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
) -> list[dict]:
    item_list = []
    for i in range(5):
        req = {
            "item_name": f"초콜릿_{i}",
            "price": 5000 + i * 2000,
            "stock": 10 + i * 5
        }
        store_id = store["id"]
        res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
        res_json = res.json()
        assert res.status_code == 201
        assert res_json["item_name"] == req["item_name"]
        assert res_json["price"] == req["price"]
        assert res_json["stock"] == req["stock"]
        item_list.append(res.json())
    req = {
        "item_name": "사탕",
        "price": 3000,
        "stock": 10
    }
    store_id = store["id"]
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["item_name"] == req["item_name"]
    assert res_json["price"] == req["price"]
    assert res_json["stock"] == req["stock"]
    item_list.append(res.json())
    return item_list