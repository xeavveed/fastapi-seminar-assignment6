from typing import List
import uuid
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wapang.app.items.models import Product
from wapang.common.exceptions import WapangException
from wapang.database.common import Base
from sqlalchemy.ext.asyncio import async_object_session


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=False)
    
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="reviews")  # type: ignore

    async def get_user(self) -> "User":
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["user"])
        return self.user

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    product: Mapped["Product"] = relationship(back_populates="reviews")  # type: ignore

    async def get_products(self) -> List[Product]:
        session = async_object_session(self)
        if session is None:
            raise WapangException(500, "ERR_000", "Session not found for the user instance.")
        await session.refresh(self, attribute_names=["product"])
        return self.product