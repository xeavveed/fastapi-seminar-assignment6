from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from wapang.app.stores.models import Store
from wapang.app.carts.models import CartProduct
from wapang.app.items.models import Product
from wapang.database.async_connection import get_async_db_session


class CartRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_db_session)]) -> None:
        self.session = session
        
    async def get_cart_product(self, user_id: str, product_id: str) -> CartProduct | None:
        cartLoc = select(CartProduct).where(CartProduct.user_id == user_id, CartProduct.product_id == product_id)
        return await self.session.scalar(cartLoc)

    async def get_all_cart_products_with_details(self, user_id: str) -> Sequence[CartProduct]:
        cartLoc = (
            select(CartProduct)
            .options(
                joinedload(CartProduct.product)
                .joinedload(Product.store)
            )
            .where(CartProduct.user_id == user_id)
        )
        return (await self.session.scalars(cartLoc)).all()

    async def add(self, cart_product: CartProduct) -> None:
        self.session.add(cart_product)
        await self.session.commit()

    async def delete(self, cart_product: CartProduct) -> None:
        await self.session.delete(cart_product)
        await self.session.commit()
        
    async def delete_all_cart_products(self, user_id: str) -> None:
        cartLoc = delete(CartProduct).where(CartProduct.user_id == user_id)
        await self.session.execute(cartLoc)