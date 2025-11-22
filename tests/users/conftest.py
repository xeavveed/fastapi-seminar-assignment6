from typing import TYPE_CHECKING, AsyncGenerator

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from httpx import AsyncClient

# tests/users 모듈에서 공통으로 사용하는 fixture를 정의

@pytest_asyncio.fixture
async def store(
    async_client: "AsyncClient",
    another_user_access_token: str
):
    auth_header = {"Authorization": f"Bearer {another_user_access_token}"}
    req = {
        "store_name": "store",
        "address": "address1",
        "email": "fastapi@wafflestudio.com",
        "phone_number": "010-1234-1234",
        "delivery_fee": 500
    }

    res = await async_client.post("/api/stores/", headers=auth_header, json=req)

    assert res.status_code == 201

    return res.json()

@pytest_asyncio.fixture
async def items(
    async_client: "AsyncClient",
    another_user_access_token: str,
    store
):  
    item_list = []
    auth_header = {"Authorization": f"Bearer {another_user_access_token}"}
    for i in range(3):
        req = {
            "item_name": f"item{i}",
            "price": 5000+(1000*i),
            "stock": 100
        }
        res = await async_client.post("/api/items/", headers=auth_header, json=req)
        item_list.append(res.json())
        
        assert res.status_code == 201
    return item_list

@pytest_asyncio.fixture
async def orders(
    async_client: "AsyncClient",
    access_token: str,
    items
):
    order_list = []
    auth_header = {"Authorization": f"Bearer {access_token}"}
    for i in range(3):
        req = {
            "items": [
                {
                    "item_id": items[i]["id"],
                    "quantity": i+1
                }
            ]
        }
        res = await async_client.post("/api/orders/", headers=auth_header, json=req)
        order_list.append(res.json())

        assert res.status_code == 201
    return order_list

@pytest_asyncio.fixture
async def reviews(
    async_client: "AsyncClient",
    access_token: str,
    items
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    req = {
        "nickname": "waffle",
    }
    res = await async_client.patch("/api/users/me", headers=auth_header, json=req)
    assert res.status_code == 200

    req = {
        "rating": 3,
        "comment": "good"
    }
    res = await async_client.post(f"/api/items/{items[0]["id"]}/reviews", headers=auth_header, json=req)
    assert res.status_code == 201
