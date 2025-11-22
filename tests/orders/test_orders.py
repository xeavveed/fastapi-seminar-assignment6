from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_order(
    async_client: "AsyncClient",
    access_token: str,
    order_items: list[dict]
):
    req = []
    for item in order_items:
        req.append({
            "item_id": item["id"],
            "quantity": 1
        })

    res = await async_client.post("/api/orders/", json={"items": req}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 201
    res_json = res.json()
    assert res_json["order_id"] is not None
    assert res_json["status"] == "ORDERED"
    details = res_json["details"]
    stores = set()
    for item in order_items:
        stores.add(item["store_id"])
    assert len(details) == len(stores)
    for detail in details:
        assert detail["store_id"] in stores
        for item in detail["items"]:
            matched = None
            for req_item in req:
                if req_item["item_id"] == item["item_id"]:
                    matched = req_item
                    break
            assert matched is not None
            assert item["quantity"] == matched["quantity"]
            for order_item in order_items:
                if order_item["id"] == item["item_id"]:
                    assert item["item_name"] == order_item["item_name"]
                    assert item["price"] == order_item["price"]
                    break
    
    total_price = 0
    for detail in details:
        store_total_price = 0
        for item in detail["items"]:
            store_total_price += item["price"] * item["quantity"]
        store_total_price += detail["delivery_fee"]
        assert detail["store_total_price"] == store_total_price
        total_price += store_total_price
    assert res_json["total_price"] == total_price

@pytest.mark.asyncio
async def test_create_order_with_nonexistent_item(
    async_client: "AsyncClient",
    access_token: str,
    order_items: list[dict]
):
    req = []
    for item in order_items:
        req.append({
            "item_id": item["id"],
            "quantity": 1
        })
    req.append({
        "item_id": "test_nonexistent_item_id",
        "quantity": 1
    })

    res = await async_client.post("/api/orders/", json={"items": req}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_013"
    assert res_json["error_msg"] == "ITEM NOT FOUND"

@pytest.mark.asyncio
async def test_create_order_with_not_enough_stock(
    async_client: "AsyncClient",
    access_token: str,
    item: dict,
):
    req = [{
        "item_id": item["id"],
        "quantity": item["stock"] + 10
    }]

    res = await async_client.post("/api/orders/", json={"items": req}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 409
    res_json = res.json()
    assert res_json["error_code"] == "ERR_017"
    assert res_json["error_msg"] == "NOT ENOUGH STOCK"

@pytest.mark.asyncio
async def test_create_order_with_no_items(
    async_client: "AsyncClient",
    access_token: str,
):
    req = []

    res = await async_client.post("/api/orders/", json={"items": req}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 422
    res_json = res.json()
    assert res_json["error_code"] == "ERR_018"
    assert res_json["error_msg"] == "EMPTY ITEM LIST"

@pytest.mark.asyncio   
async def test_create_order_with_zero_quantity(
    async_client: "AsyncClient",
    access_token: str,
    item: dict
):
    req = [{
        "item_id": item["id"],
        "quantity": 0
    }]

    res = await async_client.post("/api/orders/", json={"items": req}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_get_order(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    order_id = order["order_id"]
    res = await async_client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json == order

@pytest.mark.asyncio
async def test_get_order_with_invalid_order_id(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    order_id = "invalid_order_id"
    res = await async_client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_019"
    assert res_json["error_msg"] == "ORDER NOT FOUND"

@pytest.mark.asyncio
async def test_get_order_of_another_user(
    async_client: "AsyncClient",
    access_token: str,
    another_user_access_token: str,
    order: dict,
):
    order_id = order["order_id"]
    res = await async_client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    res_json = res.json()
    assert res_json["error_code"] == "ERR_020"
    assert res_json["error_msg"] == "NOT YOUR ORDER"

@pytest.mark.asyncio
async def test_update_order_status(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    order_id = order["order_id"]
    req = {
        "status": "CANCELED"
    }
    res = await async_client.patch(f"/api/orders/{order_id}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "CANCELED"

    res = await async_client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "CANCELED"

@pytest.mark.asyncio
async def test_update_order_status_already_canceled(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    order_id = order["order_id"]
    req = {
        "status": "CANCELED"
    }
    res = await async_client.patch(f"/api/orders/{order_id}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "CANCELED"

    res = await async_client.patch(f"/api/orders/{order_id}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 409
    res_json = res.json()
    assert res_json["error_code"] == "ERR_021"
    assert res_json["error_msg"] == "INVALID ORDER STATUS"

@pytest.mark.asyncio
async def test_update_order_status_of_another_user(
    async_client: "AsyncClient",
    access_token: str,
    another_user_access_token: str,
    order: dict,
):
    order_id = order["order_id"]
    req = {
        "status": "CANCELED"
    }
    res = await async_client.patch(f"/api/orders/{order_id}", json=req, headers={"Authorization": f"Bearer {another_user_access_token}"})
    assert res.status_code == 403
    res_json = res.json()
    assert res_json["error_code"] == "ERR_020"
    assert res_json["error_msg"] == "NOT YOUR ORDER"

@pytest.mark.asyncio
async def test_update_order_status_with_invalid_order_id(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    order_id = "invalid_order_id"
    req = {
        "status": "CANCELED"
    }
    res = await async_client.patch(f"/api/orders/{order_id}", json=req, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_019"
    assert res_json["error_msg"] == "ORDER NOT FOUND"

@pytest.mark.asyncio
async def test_get_orders_by_user(
    async_client: "AsyncClient",
    access_token: str,
    order: dict,
):
    res = await async_client.get("/api/users/me/orders", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    res_json = res.json()
    assert isinstance(res_json, list)
    assert len(res_json) >= 1