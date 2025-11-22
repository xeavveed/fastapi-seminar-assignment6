from typing import Annotated, Optional, Union
from fastapi import APIRouter, Depends, Header, status, Response

from wapang.app.reviews.models import Review
from wapang.app.reviews.schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewLoginResponse,
    ReviewLogoutResponse,
)
from wapang.app.reviews.services import ReviewService
from wapang.app.users.services import UserService
from wapang.app.users.models import User
from wapang.app.auth.utils import login_with_header, optional_login_with_header

review_router = APIRouter()


@review_router.get("/{review_id}", status_code=status.HTTP_200_OK)
async def get_review_detail(
    review_id: str,
    user: Annotated[Optional[User], Depends(optional_login_with_header)],
    review_service: ReviewService = Depends(ReviewService),
) -> Union[ReviewLoginResponse, ReviewLogoutResponse]:
    return await review_service.get_review_one(review_id, user.id if user else None)


@review_router.patch("/{review_id}", status_code=status.HTTP_200_OK)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    user: Annotated[User, Depends(login_with_header)],
    review_service: ReviewService = Depends(ReviewService),
) -> ReviewLoginResponse:
    return await review_service.update_review_for_owner(
        user_id=user.id,
        review_id=review_id,
        req=review_update,
    )


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    user: Annotated[User, Depends(login_with_header)],
    review_service: ReviewService = Depends(ReviewService),
):
    await review_service.delete_review_for_owner(
        user_id=user.id,
        review_id=review_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

