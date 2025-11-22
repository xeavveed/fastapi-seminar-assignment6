from typing import List
import uuid
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.common.exceptions import WapangException
from wapang.database.common import Base

from sqlalchemy.ext.asyncio import async_object_session
from wapang.app.items.models import Product


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    store_name: Mapped[str] = mapped_column(String(30), unique=True)
    address: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    delivery_fee: Mapped[int] = mapped_column(Integer)
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="store")  # type: ignore

    products: Mapped[List["Product"]] = relationship(  # type: ignore
        back_populates="store", cascade="all, delete-orphan"
    )

    async def get_products(self) -> List[Product]:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["products"])
        return self.products