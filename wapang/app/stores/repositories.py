from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from wapang.app.users.models import User
from wapang.app.stores.models import Store
from wapang.database.async_connection import get_async_db_session


class StoreRepository:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(get_async_db_session)]
    ) -> None:
        self.session = session

    async def create_store(
        self,
        user_id: str,
        store_name: str,
        address: str,
        email: str,
        phone_number: str,
        delivery_fee: int,
    ) -> Store:
        store = Store(
            user_id=user_id,
            store_name=store_name,
            address=address,
            email=email,
            phone_number=phone_number,
            delivery_fee=delivery_fee,
        )
        self.session.add(store)
        await self.session.flush()
        return store

    async def modify_store(self, store: Store, **kwargs) -> Store:
        for key, value in kwargs.items():
            setattr(store, key, value)
        await self.session.commit()
        return store

    async def get_store_by_id(self, id: str) -> Store | None:
        return await self.session.scalar(select(Store).where(Store.id == id))

    async def get_store_by_name(self, name: str) -> Store | None:
        return await self.session.scalar(select(Store).where(Store.store_name == name))

    async def get_store_by_email(self, email: str) -> Store | None:
        return await self.session.scalar(select(Store).where(Store.email == email))

    async def get_store_by_phone(self, phone_number: str) -> Store | None:
        return await self.session.scalar(
            select(Store).where(Store.phone_number == phone_number)
        )

    async def get_store_by_user(self, user_id: str) -> Store | None:
        return await self.session.scalar(select(Store).where(Store.user_id == user_id))