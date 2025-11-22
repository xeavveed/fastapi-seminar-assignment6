from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_review(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }
    res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]
    req = {
        "rating": 5,
        "comment": "Great"
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 201
    res_json = res.json()
    assert res_json["review_id"] is not None
    assert res_json["item_id"] == item["id"]
    assert res_json["writer_nickname"] == user_info["nickname"]
    assert res_json["is_writer"] is True
    assert res_json["rating"] == req["rating"]
    assert res_json["comment"] == req["comment"]

@pytest.mark.asyncio
async def test_create_review_with_nonexistent_item(
    async_client: AsyncClient,
    access_token: str,
):
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }
    res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]
    req = {
        "rating": 5,
        "comment": "Great"
    }

    item_id = "nonexistent_item_id"
    res = await async_client.post(f"/api/items/{item_id}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_013"
    assert res_json["error_msg"] == "ITEM NOT FOUND"

@pytest.mark.asyncio
async def test_create_review_with_invalid_rating(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }
    res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]

    req = {
        "rating": 6,
        "comment": "Great"
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_create_review_with_invalid_comment(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "address": "서울시 강남구",
        "nickname": "김와플",
        "phone_number": "010-1234-5678",
    }
    res = await async_client.patch("/api/users/me", json=req, headers={"Authorization": f"Bearer {access_token}"})
    user_info = res.json()
    assert user_info["address"] == req["address"]
    assert user_info["nickname"] == req["nickname"]
    assert user_info["phone_number"] == req["phone_number"]

    req = {
        "rating": 4,
        "comment": "A" * 501
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_create_review_with_nickname_not_set(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "rating": 4,
        "comment": "Good"
    }
    res = await async_client.post(f"/api/items/{item['id']}/reviews", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 422
    res_json = res.json()
    assert res_json["error_code"] == "ERR_015"
    assert res_json["error_msg"] == "NICKNAME NOT SET"

@pytest.mark.asyncio
async def test_get_review_with_login(
    async_client: AsyncClient,
    access_token: str,
    review: dict
):
    res = await async_client.get(f"/api/reviews/{review['review_id']}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["review_id"] == review["review_id"]
    assert res_json["item_id"] == review["item_id"]
    assert res_json["writer_nickname"] == review["writer_nickname"]
    assert res_json["is_writer"] is True
    assert res_json["rating"] == review["rating"]
    assert res_json["comment"] == review["comment"]

@pytest.mark.asyncio
async def test_get_review_without_login(
    async_client: AsyncClient,
    review: dict
):
    res = await async_client.get(f"/api/reviews/{review['review_id']}")
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["review_id"] == review["review_id"]
    assert res_json["item_id"] == review["item_id"]
    assert res_json["writer_nickname"] == review["writer_nickname"]
    assert res_json["rating"] == review["rating"]
    assert res_json["comment"] == review["comment"]

@pytest.mark.asyncio
async def test_update_review(
    async_client: AsyncClient,
    access_token: str,
    review: dict
):
    req = {
        "rating": 3,
        "comment": "So-so"
    }
    res = await async_client.patch(f"/api/reviews/{review['review_id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["review_id"] == review["review_id"]
    assert res_json["item_id"] == review["item_id"]
    assert res_json["writer_nickname"] == review["writer_nickname"]
    assert res_json["is_writer"] is True
    assert res_json["rating"] == req["rating"]
    assert res_json["comment"] == req["comment"]

@pytest.mark.asyncio
async def test_update_review_of_another_user(
    async_client: AsyncClient,
    access_token: str,
    another_user_access_token: str,
    review: dict
):
    req = {
        "rating": 3,
        "comment": "So-so"
    }
    res = await async_client.patch(f"/api/reviews/{review['review_id']}", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    res_json = res.json()
    assert res_json["error_code"] == "ERR_023"
    assert res_json["error_msg"] == "NOT YOUR REVIEW"

@pytest.mark.asyncio
async def test_update_review_with_invalid_rating(
    async_client: AsyncClient,
    access_token: str,
    review: dict
):
    req = {
        "rating": 0,
        "comment": "So-so"
    }
    res = await async_client.patch(f"/api/reviews/{review['review_id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_update_review_with_invalid_comment(
    async_client: AsyncClient,
    access_token: str,
    review: dict
):
    req = {
        "rating": 4,
        "comment": "A" * 501
    }
    res = await async_client.patch(f"/api/reviews/{review['review_id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_update_review_with_review_not_found(
    async_client: AsyncClient,
    access_token: str,
):
    req = {
        "rating": 4,
        "comment": "Good"
    }
    review_id = "nonexistent_review_id"
    res = await async_client.patch(f"/api/reviews/{review_id}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_022"
    assert res_json["error_msg"] == "REVIEW NOT FOUND"

@pytest.mark.asyncio
async def test_delete_review(
    async_client: AsyncClient,
    access_token: str,
    review: dict
):
    res = await async_client.delete(f"/api/reviews/{review['review_id']}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 204

    res = await async_client.get(f"/api/reviews/{review['review_id']}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_022"
    assert res_json["error_msg"] == "REVIEW NOT FOUND"

@pytest.mark.asyncio
async def test_delete_review_of_another_user(
    async_client: AsyncClient,
    access_token: str,
    another_user_access_token: str,
    review: dict
):
    res = await async_client.delete(f"/api/reviews/{review['review_id']}", headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    res_json = res.json()
    assert res_json["error_code"] == "ERR_023"
    assert res_json["error_msg"] == "NOT YOUR REVIEW"

@pytest.mark.asyncio
async def test_delete_review_with_review_not_found(
    async_client: AsyncClient,
    access_token: str,
):
    review_id = "nonexistent_review_id"
    res = await async_client.delete(f"/api/reviews/{review_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_022"
    assert res_json["error_msg"] == "REVIEW NOT FOUND"

@pytest.mark.asyncio
async def test_list_reviews_with_login(
    async_client: AsyncClient,
    access_token: str,
    item: dict,
    review: dict,
    another_review: dict
):
    res = await async_client.get(f"/api/items/{item['id']}/reviews", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    for r in res_json:
        if r["review_id"] == review["review_id"]:
            assert r["is_writer"] is True
            assert r["writer_nickname"] == review["writer_nickname"]
            assert r["review_id"] == review["review_id"]
            assert r["rating"] == review["rating"]
            assert r["comment"] == review["comment"]
        elif r["review_id"] == another_review["review_id"]:
            assert r["is_writer"] is False
            assert r["writer_nickname"] == another_review["writer_nickname"]
            assert r["review_id"] == another_review["review_id"]
            assert r["rating"] == another_review["rating"]
            assert r["comment"] == another_review["comment"]
        else:
            assert False

@pytest.mark.asyncio
async def test_list_reviews_without_login(
    async_client: AsyncClient,
    item: dict,
    review: dict,
    another_review: dict
):
    res = await async_client.get(f"/api/items/{item['id']}/reviews")
    assert res.status_code == 200
    res_json = res.json()
    for r in res_json:
        if r["review_id"] == review["review_id"]:
            assert "is_writer" not in r
            assert r["writer_nickname"] == review["writer_nickname"]
            assert r["review_id"] == review["review_id"]
            assert r["rating"] == review["rating"]
            assert r["comment"] == review["comment"]
        elif r["review_id"] == another_review["review_id"]:
            assert "is_writer" not in r
            assert r["writer_nickname"] == another_review["writer_nickname"]
            assert r["review_id"] == another_review["review_id"]
            assert r["rating"] == another_review["rating"]
            assert r["comment"] == another_review["comment"]
        else:
            assert False

@pytest.mark.asyncio
async def test_list_reviews_with_nonexistent_item(
    async_client: AsyncClient,
    access_token: str,
    item: dict,
):
    item_id = "nonexistent_item_id"
    res = await async_client.get(f"/api/items/{item_id}/reviews", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_013"
    assert res_json["error_msg"] == "ITEM NOT FOUND"

@pytest.mark.asyncio
async def test_list_user_reviews(
    async_client: AsyncClient,
    access_token: str,
    reviews: dict,
):
    res = await async_client.get("/api/users/me/reviews", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert len(res_json) == len(reviews)
    for r in res_json:
        found = False
        for review in reviews:
            if r["review_id"] == review["review_id"]:
                found = True
                assert r["item_id"] == review["item_id"]
                assert r["rating"] == review["rating"]
                assert r["comment"] == review["comment"]
                break
        assert found is True