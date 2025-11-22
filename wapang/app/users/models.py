import uuid
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.common.exceptions import WapangException
from wapang.database.common import Base

from sqlalchemy.ext.asyncio import async_object_session
from wapang.app.stores.models import Store
from wapang.app.orders.models import Order
from wapang.app.reviews.models import Review
from wapang.app.carts.models import CartProduct

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(150))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    
    store: Mapped["Store"] = relationship(back_populates="user", uselist=False)  # type: ignore
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore
    reviews: Mapped[List["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore
    cart_products: Mapped[List["CartProduct"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # type: ignore

    async def get_store(self) -> Store:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["store"])
        return self.store

    async def get_orders(self) -> List[Order]:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["orders"])
        return self.orders

    async def get_reviews(self) -> List[Review]:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["reviews"])
        return self.reviews

    async def get_cart_products(self) -> List[CartProduct]:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["cart_products"])
        return self.cart_products