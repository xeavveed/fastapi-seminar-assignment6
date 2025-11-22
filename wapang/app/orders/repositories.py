from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from wapang.app.orders.models import Order, OrderProduct
from wapang.app.items.models import Product
from wapang.database.async_connection import get_async_db_session


class OrderRepository:
    def __init__(
        self, session: Annotated[Session, Depends(get_async_db_session)]
    ) -> None:
        self.session = session

    async def add_order(
        self,
        order: Order,
        order_products: list[OrderProduct],
        updated_products: list[Product],
    ) -> Order:
        self.session.add(order)
        self.session.add_all(order_products)
        self.session.add_all(updated_products)

        await self.session.flush()
        return order

    async def get_order_by_id(self, order_id: str) -> Order | None:
        orderLoc = select(Order).where(Order.id == order_id)
        return await self.session.scalar(orderLoc)

    async def get_order_products_with_details(
        self, order_id: str
    ) -> Sequence[OrderProduct]:
        orderLoc = (
            select(OrderProduct)
            .options(joinedload(OrderProduct.product).joinedload(Product.store))
            .where(OrderProduct.order_id == order_id)
        )
        return (await self.session.scalars(orderLoc)).all()

    async def get_order_products_for_restock(
        self, order_id: str
    ) -> Sequence[OrderProduct]:
        orderLoc = (
            select(OrderProduct)
            .options(joinedload(OrderProduct.product))
            .where(OrderProduct.order_id == order_id)
        )
        return (await self.session.scalars(orderLoc)).all()

    async def add_objects_to_session(self, objects: list):
        self.session.add_all(objects)
        await self.session.flush()
