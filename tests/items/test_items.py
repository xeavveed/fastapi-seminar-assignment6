from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_item(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
    item_create_request: dict
):
    res = await async_client.post("/api/items/", json=item_create_request, headers={"Authorization": f"Bearer {access_token}"})
    res_json = res.json()
    assert res.status_code == 201
    assert res_json["item_name"] == item_create_request["item_name"]
    assert res_json["price"] == item_create_request["price"]
    assert res_json["stock"] == item_create_request["stock"]

@pytest.mark.asyncio
async def test_create_item_missing_field(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    req = {
        "item_name": "초콜릿",
        "price": 5000
    }
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_002"
    assert res.json()["error_msg"] == "MISSING REQUIRED FIELDS"

@pytest.mark.asyncio
async def test_create_item_with_long_item_name(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    req = {
        "item_name": "A" * 51,
        "price": 5000,
        "stock": 20
    }
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_create_item_with_negative_price(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    req = {
        "item_name": "초콜릿",
        "price": -5000,
        "stock": 20
    }
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_create_item_with_negative_stock(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    req = {
        "item_name": "초콜릿",
        "price": 5000,
        "stock": -20
    }
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_create_item_with_no_store(
    async_client: AsyncClient,
    access_token: str,
):
    req = {
        "item_name": "초콜릿",
        "price": 5000,
        "stock": 20
    }
    res = await async_client.post("/api/items/", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_011"
    assert res.json()["error_msg"] == "NO STORE OWNED"

@pytest.mark.asyncio
async def test_patch_item(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    res_json = res.json()
    assert res.status_code == 200
    assert res_json["item_name"] == req["item_name"]
    assert res_json["price"] == req["price"]
    assert res_json["stock"] == req["stock"]

@pytest.mark.asyncio
async def test_patch_item_with_long_item_name(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "A" * 51,
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_patch_item_with_negative_price(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "price": -6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_patch_item_with_negative_stock(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "price": 6000,
        "stock": -30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"
    assert res.json()["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_patch_item_with_no_price(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["item_name"] == req["item_name"]
    assert res_json["price"] == item["price"]
    assert res_json["stock"] == req["stock"]

@pytest.mark.asyncio
async def test_patch_item_with_no_stock(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "price": 6000
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["item_name"] == req["item_name"]
    assert res_json["price"] == req["price"]
    assert res_json["stock"] == item["stock"]

@pytest.mark.asyncio
async def test_patch_item_with_no_item_name(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    req = {
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["item_name"] == item["item_name"]
    assert res_json["price"] == req["price"]
    assert res_json["stock"] == req["stock"]

@pytest.mark.asyncio
async def test_patch_item_not_found(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    req = {
        "item_name": "쿠키",
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/9999", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    assert res.json()["error_code"] == "ERR_013"
    assert res.json()["error_msg"] == "ITEM NOT FOUND"

@pytest.mark.asyncio
async def test_patch_item_with_no_store(
    async_client: AsyncClient,
    another_user_access_token: str,
    item: dict
):
    req = {
        "item_name": "쿠키",
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_011"
    assert res.json()["error_msg"] == "NO STORE OWNED"

@pytest.mark.asyncio
async def test_patch_item_of_another_store(
    async_client: AsyncClient,
    another_user_access_token: str,
    item: dict,
    store_2: dict
):
    req = {
        "item_name": "쿠키",
        "price": 6000,
        "stock": 30
    }
    res = await async_client.patch(f"/api/items/{item['id']}", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_014"
    assert res.json()["error_msg"] == "NOT YOUR ITEM"

@pytest.mark.asyncio
async def test_get_items(
    async_client: AsyncClient,
    items: dict,
    store: dict,
):
    query_params = {
        "store_id": store["id"],
        "min_price": 5000,
        "max_price": 9000,
        "in_stock": True,
    }

    res = await async_client.get("/api/items/", params=query_params)
    res_json = res.json()
    assert res.status_code == 200
    for item in res_json:
        assert item["price"] >= query_params["min_price"]
        assert item["price"] <= query_params["max_price"]
        assert item["stock"] > 0

@pytest.mark.asyncio
async def test_get_items_no_store(
    async_client: AsyncClient,
    items: dict
):
    query_params = {
        "store_id": "9999",
        "min_price": 5000,
        "max_price": 9000,
        "in_stock": True,
    }

    res = await async_client.get("/api/items/", params=query_params)
    res_json = res.json()
    assert res.status_code == 404
    assert res_json["error_code"] == "ERR_010"
    assert res_json["error_msg"] == "STORE NOT FOUND"

@pytest.mark.asyncio
async def test_delete_item(
    async_client: AsyncClient,
    access_token: str,
    item: dict
):
    res = await async_client.delete(f"/api/items/{item['id']}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 204

@pytest.mark.asyncio
async def test_delete_item_not_found(
    async_client: AsyncClient,
    access_token: str,
    store: dict,
):
    res = await async_client.delete(f"/api/items/9999", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    assert res.json()["error_code"] == "ERR_013"
    assert res.json()["error_msg"] == "ITEM NOT FOUND"

@pytest.mark.asyncio
async def test_delete_item_no_access(
    async_client: AsyncClient,
    item: dict,
    store: dict,
    store_2: dict,
    another_user_access_token: str,
):
    res = await async_client.delete(f"/api/items/{item['id']}", headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_014"
    assert res.json()["error_msg"] == "NOT YOUR ITEM"

@pytest.mark.asyncio
async def test_get_store_items(
    async_client: AsyncClient,
    store: dict,
    items: dict,
):
    store_id = store["id"]
    res = await async_client.get(f"/api/stores/{store_id}/items")
    res_json = res.json()
    assert res.status_code == 200
    item_ids = {item['id'] for item in items}
    for item in res_json:
        assert item['id'] in item_ids
        assert item['item_name'] in {i['item_name'] for i in items}
        assert item['price'] in {i['price'] for i in items}
        assert item['stock'] in {i['stock'] for i in items}

@pytest.mark.asyncio
async def test_get_store_items_no_store(
    async_client: AsyncClient,
):
    res = await async_client.get(f"/api/stores/9999/items")
    res_json = res.json()
    assert res.status_code == 404
    assert res_json["error_code"] == "ERR_010"
    assert res_json["error_msg"] == "STORE NOT FOUND"