from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from wapang.app.items.models import Product
from wapang.database.async_connection import get_async_db_session


class ItemRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_db_session)]) -> None:
        self.session = session

    def add_item(self, product: Product) -> None:
        self.session.add(product)
    
    async def get_item_by_id(self, product_id: str) -> Product | None:
        productLoc = select(Product).where(Product.id == product_id)
        return await self.session.scalar(productLoc)
    
    async def get_items_by_ids(self, product_ids: list[str]) -> Sequence[Product] | None:
        productLoc = select(Product).options(joinedload(Product.store)).where(Product.id.in_(product_ids))
        return (await self.session.scalars(productLoc)).all()
    
    async def get_all_items_in_store(self, store_id: str) -> list[Product]:
        productsLoc = select(Product).where(Product.store_id == store_id)
        return (await self.session.scalars(productsLoc)).all()
    
    async def get_items_with_query(
            self,
            store_id: str | None = None,
            min_price: int | None = None,
            max_price: int | None = None,
            in_stock: bool = False
    ) -> list[Product]:
        query = select(Product)
        if store_id:
            query = query.where(Product.store_id == store_id)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if in_stock:
            query = query.where(Product.stock > 0)
        return (await self.session.scalars(query)).all()
    
    def modify_item(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)

        return product

    def delete_item(self, product: Product) -> None:
        self.session.delete(product)