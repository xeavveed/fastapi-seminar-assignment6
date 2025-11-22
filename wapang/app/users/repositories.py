from typing import Annotated, Sequence
import asyncio
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from wapang.app.reviews.models import Review
from wapang.app.users.models import User
from wapang.app.orders.models import Order
from wapang.database.async_connection import get_async_db_session


class UserRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_db_session)]) -> None:
        self.session = session

    async def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)

        await self.session.flush()

        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.session.scalar(select(User).where(User.id == user_id))

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def modify_user(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.commit()
        return user

    async def get_all_orders_from_user(self, user: User) -> Sequence[Order]:
        return (await self.session.scalars(select(Order).where(Order.user_id == user.id))).all()

    async def get_all_reviews_from_user(self, user: User) -> Sequence[Review]:
        return (await self.session.scalars(
            select(Review).where(Review.user_id == user.id)
        )).all()
