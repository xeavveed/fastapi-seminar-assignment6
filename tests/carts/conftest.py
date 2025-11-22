import pytest_asyncio
from httpx import AsyncClient

from tests.items.conftest import item, items, item_create_request, item_2

@pytest_asyncio.fixture(scope="function")
async def add_to_cart(async_client: "AsyncClient", access_token: str):
	"""Helper to add or update a cart line for the logged-in user."""

	async def _add(item_id: str, quantity: int):
		return await async_client.patch( 
			"/api/carts/",
			json={"item_id": item_id, "quantity": quantity},
			headers={"Authorization": f"Bearer {access_token}"},
		)

	return _add


@pytest_asyncio.fixture(scope="function")
async def get_cart(async_client: "AsyncClient", access_token: str):
	"""Helper to fetch the current cart for the logged-in user."""

	async def _get():
		return await async_client.get(
			"/api/carts/",
			headers={"Authorization": f"Bearer {access_token}"},
		)

	return _get


@pytest_asyncio.fixture(scope="function")
async def clear_cart(async_client: "AsyncClient", access_token: str):
	"""Helper to clear the cart for the logged-in user."""

	async def _clear():
		return await async_client.delete(
			"/api/carts/",
			headers={"Authorization": f"Bearer {access_token}"},
		)

	return _clear


@pytest_asyncio.fixture(scope="function")
async def checkout_cart(async_client: "AsyncClient", access_token: str):
	"""Helper to checkout the cart for the logged-in user."""

	async def _checkout():
		return await async_client.post(
			"/api/carts/checkout/",
			headers={"Authorization": f"Bearer {access_token}"},
		)

	return _checkout

