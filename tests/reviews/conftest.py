from httpx import AsyncClient
import pytest_asyncio

from tests.items.conftest import item, items, item_create_request

@pytest_asyncio.fixture(scope="function")
async def review(
    async_client: AsyncClient,
    access_token: str,
    item: dict
) -> dict:
    
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }

    user_res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]

    req = {
        "rating": 4,
        "comment": "Good"
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})

    res_json = res.json()
    assert res.status_code == 201
    assert res_json["review_id"] is not None
    assert res_json["item_id"] == item["id"]
    assert res_json["writer_nickname"] == user_info["nickname"]
    assert res_json["is_writer"] is True
    assert res_json["rating"] == req["rating"]
    assert res_json["comment"] == req["comment"]

    return res.json()

@pytest_asyncio.fixture(scope="function")
async def another_review(
    async_client: AsyncClient,
    another_user_access_token: str,
    item: dict
) -> dict:
    
    req = {
        "address": "서울시 서초구",
        "nickname": "이와플",
        "phone_number": "010-9876-5432",
    }

    user_res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    user_info = user_res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]

    req = {
        "rating": 3,
        "comment": "Soso"
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})

    res_json = res.json()
    assert res.status_code == 201
    assert res_json["review_id"] is not None
    assert res_json["item_id"] == item["id"]
    assert res_json["writer_nickname"] == user_info["nickname"]
    assert res_json["is_writer"] is True
    assert res_json["rating"] == req["rating"]
    assert res_json["comment"] == req["comment"]

    return res.json()

@pytest_asyncio.fixture(scope="function")
async def reviews(
    async_client: AsyncClient,
    items: list[dict],
    access_token: str
) -> list[dict]:
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }

    user_res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]


    review_list = []
    for item in items:
        req = {
            "rating": 5,
            "comment": "Great"
        }
        res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
        res_json = res.json()
        assert res.status_code == 201
        assert res_json["review_id"] is not None
        assert res_json["item_id"] == item["id"]
        assert res_json["rating"] == req["rating"]
        assert res_json["comment"] == req["comment"]
        review_list.append(res_json)
    
    return review_list