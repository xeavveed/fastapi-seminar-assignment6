import uuid
from typing import List
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.database.common import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer)

    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"))

    store: Mapped["Store"] = relationship(back_populates="products")  # type: ignore

    reviews: Mapped[List["Review"]] = relationship(  # type: ignore
        back_populates="product"
    )

    cart_products: Mapped[List["CartProduct"]] = relationship(  # type: ignore
        back_populates="product", cascade="all, delete-orphan"
    )

    order_products: Mapped[List["OrderProduct"]] = relationship(  # type: ignore
        back_populates="product"
    )
