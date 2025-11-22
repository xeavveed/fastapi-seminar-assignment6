from typing import Annotated, Optional, Union
from fastapi import Depends

from wapang.app.reviews.models import Review
from wapang.app.reviews.repositories import ReviewRepository
from wapang.app.items.repositories import ItemRepository
from wapang.app.reviews.exceptions import (
    ReviewAlreadyExistsException,
    ReviewNotFoundException,
    NotYourReviewException,
)
from wapang.app.items.exceptions import ItemNotFoundException

from wapang.app.reviews.schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewLoginResponse,
    ReviewLogoutResponse,
)

ResponseOne = Union[ReviewLoginResponse, ReviewLogoutResponse]

class ReviewService:
    def __init__(
        self,
        review_repository: Annotated[ReviewRepository, Depends()],
    ) -> None:
        self.review_repository = review_repository

    async def get_review_one(
        self, review_id: str, request_user_id: Optional[str] = None
    ) -> ResponseOne:
        review = await self.review_repository.get_review_by_id(review_id)
        if review is None:
            raise ReviewNotFoundException()

        if request_user_id:
            return ReviewLoginResponse(
                review_id=review.id,
                item_id=review.product_id,
                writer_nickname=(await review.get_user()).nickname,
                rating=review.rating,
                comment=review.comment,
                is_writer=(review.user_id == request_user_id),
            )
        else:
            return ReviewLogoutResponse(
                review_id=review.id,
                item_id=review.product_id,
                writer_nickname=(await review.get_user()).nickname,
                rating=review.rating,
                comment=review.comment,
            )
    
    async def update_review_for_owner(
        self, user_id: str, review_id: str, req: ReviewUpdate
    ) -> ReviewLoginResponse:
        review = await self.review_repository.get_review_by_id(review_id)
        if review is None:
            raise ReviewNotFoundException()

        if review.user_id != user_id:
            raise NotYourReviewException()

        updated = self.review_repository.modify_review(
            review,
            rating=req.rating if req.rating is not None else review.rating,
            comment=req.comment if req.comment is not None else review.comment,
        )
        await self.review_repository.session.flush()

        return ReviewLoginResponse(
            review_id=updated.id,
            item_id=updated.product_id,
            writer_nickname=updated.user.nickname,
            is_writer=True,
            rating=updated.rating,
            comment=updated.comment
        )

    async def delete_review_for_owner(self, user_id: str, review_id: str) -> None:
        review = await self.review_repository.get_review_by_id(review_id)
        if review is None:
            raise ReviewNotFoundException()

        if review.user_id != user_id:
            raise NotYourReviewException()

        await self.review_repository.delete_review(review)
        await self.review_repository.session.flush()
