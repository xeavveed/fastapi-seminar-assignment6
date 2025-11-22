from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from wapang.database.async_settings import ASYNC_DB_SETTINGS

import os

class AsyncDatabaseManager:
    def __init__(self):
        if os.environ["ENV"] == "test":
            self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        else:
            self.engine = create_async_engine(
                ASYNC_DB_SETTINGS.url,
                pool_recycle=28000,
                pool_size=10,
                pool_pre_ping=True,
                echo=False
            )
        self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

async_db_manager = AsyncDatabaseManager()

async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_db_manager.session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()