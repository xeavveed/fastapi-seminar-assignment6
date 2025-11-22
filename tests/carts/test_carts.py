from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_add_cart_item(
	async_client: "AsyncClient",
	access_token: str,
	store: dict,
	item: dict,
	get_cart,
	add_to_cart,
):
	quantity = 1
	res = await add_to_cart(item_id=item["id"], quantity=quantity)
	assert res.status_code == 200
	res_json = res.json()
	assert "details" in res_json and isinstance(res_json["details"], list)
	assert "total_price" in res_json and isinstance(res_json["total_price"], int)

	assert len(res_json["details"]) == 1
	detail = res_json["details"][0]
	assert detail["store_id"] == store["id"]
	assert detail["store_name"] == store["store_name"]


	assert detail["delivery_fee"] == store["delivery_fee"]
	assert len(detail["items"]) == 1
	line = detail["items"][0]
	assert line["item_id"] == item["id"]
	assert line["item_name"] == item["item_name"]
	assert line["price"] == item["price"]
	assert line["quantity"] == quantity
	assert line["subtotal"] == item["price"] * quantity

	expected_store_total = line["subtotal"] + store["delivery_fee"]
	assert detail["store_total_price"] == expected_store_total
	assert res_json["total_price"] == expected_store_total

	res2 = await get_cart()
	assert res2.status_code == 200
	assert res2.json() == res_json

@pytest.mark.asyncio
async def test_add_cart_item_not_found(
    add_to_cart,
):
    res = await add_to_cart(item_id="invalid-item-id", quantity=1)

    assert res.status_code == 404
    res_json = res.json()
    assert res_json["error_code"] == "ERR_013"
    assert res_json["error_msg"] == "ITEM NOT FOUND"
    
@pytest.mark.asyncio
async def test_add_cart_item_with_negative_quantity(
    add_to_cart,
    item: dict,
):
    res = await add_to_cart(item_id=item["id"], quantity=-1)

    assert res.status_code == 400
    res_json = res.json()
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

@pytest.mark.asyncio
async def test_update_cart_item_quantity(
	async_client: "AsyncClient",
	access_token: str,
	store: dict,
	item: dict,
	add_to_cart,
):
	res = await add_to_cart(item_id=item["id"], quantity=1)
	assert res.status_code == 200

	res = await add_to_cart(item_id=item["id"], quantity=3)
	assert res.status_code == 200
	res_json = res.json()
	detail = res_json["details"][0]
	line = detail["items"][0]


	assert line["quantity"] == 3
	assert line["subtotal"] == item["price"] * 3
	assert detail["store_total_price"] == item["price"] * 3 + store["delivery_fee"]

@pytest.mark.asyncio
async def test_delete_cart_item_by_zero_quantity(
	async_client: "AsyncClient",
	access_token: str,
	item: dict,
	add_to_cart,
):
	res = await add_to_cart(item_id=item["id"], quantity=1)
	assert res.status_code == 200

	res = await add_to_cart(item_id=item["id"], quantity=0)
	assert res.status_code == 200
	res_json = res.json()
	assert res_json["details"] == []
	assert res_json["total_price"] == 0

@pytest.mark.asyncio
async def test_get_cart_with_multiple_stores(
	async_client: "AsyncClient",
	access_token: str,
	store: dict,
	store_2: dict,
	item: dict,
	item_2: dict,
	get_cart,
	add_to_cart,
):
	r1 = await add_to_cart(item_id=item["id"], quantity=2)
	assert r1.status_code == 200
	r2 = await add_to_cart(item_id=item_2["id"], quantity=1)
	assert r2.status_code == 200

	res = await get_cart()
	assert res.status_code == 200
	res_json = res.json()

	assert len(res_json["details"]) == 2
	total_price = sum(d["store_total_price"] for d in res_json["details"])
	assert res_json["total_price"] == total_price

	by_store = {d["store_id"]: d for d in res_json["details"]}

	d1 = by_store[store["id"]]
	assert d1["store_name"] == store["store_name"]
	assert d1["delivery_fee"] == store["delivery_fee"]
	line1 = d1["items"][0]
	assert line1["item_id"] == item["id"]
	assert line1["quantity"] == 2
	assert line1["subtotal"] == item["price"] * 2

	d2 = by_store[store_2["id"]]
	assert d2["store_name"] == store_2["store_name"]
	assert d2["delivery_fee"] == store_2["delivery_fee"]
	line2 = d2["items"][0]
	assert line2["item_id"] == item_2["id"]
	assert line2["quantity"] == 1
	assert line2["subtotal"] == item_2["price"] * 1

@pytest.mark.asyncio 
async def test_get_empty_cart_for_new_user(
    async_client: "AsyncClient",
    another_user_access_token: str,
):
    res = await async_client.get(
        "/api/carts/",
        headers={"Authorization": f"Bearer {another_user_access_token}"},
    )
    
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["details"] == []
    assert res_json["total_price"] == 0

@pytest.mark.asyncio
async def test_clear_cart(
	clear_cart,
	add_to_cart,
	item: dict,
	get_cart,
):
	r = await add_to_cart(item_id=item["id"], quantity=1)
	assert r.status_code == 200

	res = await clear_cart()
	assert res.status_code == 204

	res = await get_cart()
	assert res.status_code == 200
	res_json = res.json()
	assert res_json["details"] == []
	assert res_json["total_price"] == 0

@pytest.mark.asyncio
async def test_checkout_success(
	async_client: "AsyncClient",
	store: dict,
	item: dict,
	add_to_cart,
	checkout_cart,
	get_cart,
):
	qty = 1
	r = await add_to_cart(item_id=item["id"], quantity=qty)
	assert r.status_code == 200

	res = await checkout_cart()
	assert res.status_code == 201
	res_json = res.json()
	assert res_json["order_id"] is not None
	assert res_json["status"] == "ORDERED"

	assert len(res_json["details"]) == 1
	d = res_json["details"][0]
	assert d["store_id"] == store["id"]
	assert d["delivery_fee"] == store["delivery_fee"]
	line = d["items"][0]
	assert line["item_id"] == item["id"]
	assert line["quantity"] == qty
	assert d["store_total_price"] == line["price"] * qty + store["delivery_fee"]

	res2 = await get_cart()
	assert res2.status_code == 200
	assert res2.json() == {"details": [], "total_price": 0}

@pytest.mark.asyncio
async def test_checkout_empty_cart(
	checkout_cart,
):
	res = await checkout_cart()
	assert res.status_code == 422
	res_json = res.json()
	assert res_json["error_code"] == "ERR_024"
	assert res_json["error_msg"] == "EMPTY ITEM LIST"

@pytest.mark.asyncio
async def test_checkout_not_enough_stock(
	add_to_cart,
	checkout_cart,
	item: dict,
):
	res = await add_to_cart(item_id=item["id"], quantity=item["stock"] + 1)
	assert res.status_code == 200
	res2 = await checkout_cart()
	assert res2.status_code == 409
	res_json = res2.json()
	assert res_json["error_code"] == "ERR_017"
	assert res_json["error_msg"] == "NOT ENOUGH STOCK"