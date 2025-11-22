import uuid
import enum
from typing import List
from sqlalchemy import Integer, ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.app.carts.exceptions import InvalidFieldFormatException
from wapang.database.common import Base


class OrderStatus(enum.Enum):
    CANCELED = "CANCELED"
    ORDERED = "ORDERED"
    COMPLETE = "COMPLETE"

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))
    total_price: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")  # type: ignore

    order_products: Mapped[List["OrderProduct"]] = relationship(  # type: ignore
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderProduct(Base):
    __tablename__ = "order_products"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    quantity: Mapped[int] = mapped_column(Integer)

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    order: Mapped["Order"] = relationship(back_populates="order_products")  # type: ignore

    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="order_products")  # type: ignore
