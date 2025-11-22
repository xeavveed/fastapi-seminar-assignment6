from typing import Annotated, Sequence
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from wapang.database.async_connection import get_async_db_session
from wapang.app.reviews.models import Review


class ReviewRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_db_session)]) -> None:
        self.session = session

    async def add_review(self, review: Review) -> None:
        self.session.add(review)
        await self.session.commit()
    
    async def get_review_by_id(self, review_id: str) -> Review | None:
        reviewLoc = select(Review).where(Review.id == review_id)
        return await self.session.scalar(reviewLoc)
    
    async def get_reviews_for_product(self, product_id: str) -> list[Review]:
        reviewsLoc = select(Review).where(Review.product_id == product_id)
        return (await self.session.scalars(reviewsLoc)).all()

    async def get_user_review_for_product(self, user_id: str, product_id: str) -> Review | None:
        reviewLoc = select(Review).where(
            Review.user_id == user_id,
            Review.product_id == product_id,
        )
        return await self.session.scalar(reviewLoc)

    def modify_review(self, review: Review, **kwargs) -> Review:
        for key, value in kwargs.items():
            setattr(review, key, value)
        return review
    
    async def delete_review(self, review: Review) -> None:
        await self.session.delete(review)