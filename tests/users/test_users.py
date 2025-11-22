from random import choice

import pytest
from httpx import AsyncClient


# users 모듈의 API 테스트 코드

@pytest.mark.asyncio
async def test_signup(
    async_client: AsyncClient,
    user_signup_data: dict
):
    # Arrange(준비)
    req = user_signup_data

    # Act(실행)
    res = await async_client.post("/api/users/", json=req)
    
    # Assert(검증)
    assert res.status_code == 201
    res_json = res.json()
    assert res_json.get("id") is not None
    assert res_json.get("email") == user_signup_data.get("email")

@pytest.mark.asyncio
async def test_signup_missing_email(
    async_client: AsyncClient,
    user_signup_data: dict
):
    req = { k:v for k, v in user_signup_data.items() if k != "email"}

    res = await async_client.post("/api/users/", json=req)
    
    assert res.status_code == 400
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_002"
    assert res_json.get("error_msg") == "MISSING REQUIRED FIELDS"

@pytest.mark.asyncio
async def test_signup_missing_password(
    async_client: AsyncClient,
    user_signup_data: dict
):
    req = { k:v for k, v in user_signup_data.items() if k != "password"}

    res = await async_client.post("/api/users/", json=req)
    
    assert res.status_code == 400
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_002"
    assert res_json.get("error_msg") == "MISSING REQUIRED FIELDS"

@pytest.mark.asyncio
async def test_signup_invalid_email(
    async_client: AsyncClient,
    user_signup_data: dict
):
    req = { k:v for k, v in user_signup_data.items() if k != "email"}
    req["email"] = "invalid.email.format"

    res = await async_client.post("/api/users/", json=req)
    
    assert res.status_code == 400
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_003"
    assert res_json.get("error_msg") == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_signup_short_password(
    async_client: AsyncClient,
    user_signup_data: dict
):
    req = { k:v for k, v in user_signup_data.items() if k != "password"}
    req["password"] = "short"

    res = await async_client.post("/api/users/", json=req)

    assert res.status_code == 400
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_003"
    assert res_json.get("error_msg") == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_signup_long_password(
    async_client: AsyncClient,
    user_signup_data: dict
):
    req = { k:v for k, v in user_signup_data.items() if k != "password"}
    req["password"] = "".join(choice("abcdefghijklmnopqrstuvwxyz") for _ in range(129))

    res = await async_client.post("/api/users/", json=req)

    assert res.status_code == 400
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_003"
    assert res_json.get("error_msg") == "INVALID FIELD FORMAT"


@pytest.mark.asyncio
async def test_signup_email_conflict(
    async_client: AsyncClient,
    user: dict
):
    req = {
        "email": user.get("email"),
        "password": "password321"
    }

    res = await async_client.post("/api/users/", json=req)

    assert res.status_code == 409
    res_json = res.json()
    assert res_json.get("error_code") == "ERR_004"
    assert res_json.get("error_msg") == "EMAIL ALREADY EXISTS"

# TEST GET /api/users/me
@pytest.mark.asyncio
async def test_get_me(
    async_client: AsyncClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    
    res = await async_client.get("/api/users/me", headers=auth_header)
    
    assert res.status_code == 200
    
@pytest.mark.asyncio
async def test_get_me_without_header(
    async_client: AsyncClient
):
    res = await async_client.get("/api/users/me")
    res_json = res.json()
    
    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"
    assert res_json["error_msg"] == "UNAUTHENTICATED"
    
@pytest.mark.asyncio
async def test_get_me_invalid_header(
    async_client: AsyncClient,
    access_token: str
):
    invalid_header = {"Authorization": f"{access_token}"}
    
    res = await async_client.get("/api/users/me", headers=invalid_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_006"
    assert res_json["error_msg"] == "BAD AUTHORIZATION HEADER"
    
@pytest.mark.asyncio
async def test_get_me_invalid_token(
    async_client: AsyncClient,
):
    auth_header = {"Authorization": f"Bearer invalidtoken"}
    
    res = await async_client.get("/api/users/me", headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_007"
    assert res_json["error_msg"] == "INVALID TOKEN"

# TEST PATCH /api/users/me
@pytest.mark.asyncio
async def test_patch_me(
    async_client: AsyncClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    req = {
        "nickname": "waffle",
        "address": "Seoul"
    }

    res = await async_client.patch("/api/users/me", headers=auth_header, json=req)
    res_json=res.json()

    assert res.status_code == 200
    assert res_json["nickname"] == req["nickname"]
    assert res_json["address"] == req["address"]

@pytest.mark.asyncio
async def test_patch_me_random(
    async_client: AsyncClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    possible = {
        "nickname": "waffle",
        "address": "Seoul",
        "phone_number": "010-0000-1111"
    }
    to_update = choice(list(possible.keys()))
    req = {
        to_update: possible[to_update]
    }
    print(to_update)
    res = await async_client.patch("/api/users/me", headers=auth_header, json=req)
    res_json=res.json()

    assert res.status_code == 200
    assert res_json[to_update] == req[to_update]

@pytest.mark.asyncio
async def test_patch_me_invalid_req(
    async_client: AsyncClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    req = {
        "invalid": "content"
    }

    res = await async_client.patch("/api/users/me", headers=auth_header, json=req)
    res_json=res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_patch_me_without_token(
    async_client: AsyncClient
):
    req = {
        "nickname": "waffle"
    }

    res = await async_client.patch("/api/users/me", json=req)
    res_json=res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"
    assert res_json["error_msg"] == "UNAUTHENTICATED"
    
# TEST GET /api/users/me/orders
@pytest.mark.asyncio
async def test_get_me_orders(
    async_client: AsyncClient,
    access_token: str,
    orders
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = await async_client.get("/api/users/me/orders", headers=auth_header)
    res_json = res.json()

    assert res.status_code == 200
    assert len(res_json) == 3
    for i in range(3):
        assert res_json[i]["order_id"] is not None

# TEST GET /api/users/me/reviews
@pytest.mark.asyncio
async def test_get_me_reviews(
    async_client: AsyncClient,
    access_token: str,
    reviews
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = await async_client.get("/api/users/me/reviews", headers=auth_header)
    res_json = res.json()

    assert res.status_code == 200
    assert len(res_json) == 1
    assert res_json[0]["item_name"] == "item0"
    assert res_json[0]["rating"] == 3
    assert res_json[0]["comment"] == "good"