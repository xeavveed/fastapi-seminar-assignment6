import uuid
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.database.common import Base


class CartProduct(Base):
    __tablename__ = "cart_products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    count: Mapped[int] = mapped_column(Integer)
    
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship(back_populates="cart_products")  # type: ignore
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="cart_products")  # type: ignore