import sys
from typing import Annotated
from fastapi import APIRouter, Depends, status

from wapang.app.auth.utils import login_with_header
from wapang.app.orders.schemas import SimpleOrderResponse
from wapang.app.users.models import User
from wapang.app.users.schemas import (
    OrderResponse,
    ReviewResponse,
    UserSignupRequest,
    UserChangeRequest,
    UserResponse,
)
from wapang.app.users.services import UserService

user_router = APIRouter()


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def signup(
    signup_request: UserSignupRequest, user_service: Annotated[UserService, Depends()]
) -> UserResponse:
    user = await user_service.create_user(
        signup_request.email,
        signup_request.password,
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        address=user.address,
        phone_number=user.phone_number,
    )


@user_router.get("/me")
async def get_me(
    user: Annotated[User, Depends(login_with_header)],
) -> UserResponse:
    return UserResponse.model_validate(user)


@user_router.patch("/me")
async def patch_me(
    change_request: UserChangeRequest,
    user: Annotated[User, Depends(login_with_header)],
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    user = await user_service.modify_user(user, change_request)
    return UserResponse.model_validate(user)


@user_router.get("/me/orders")
async def get_orders(
    user: Annotated[User, Depends(login_with_header)],
    user_service: Annotated[UserService, Depends()],
) -> list[SimpleOrderResponse]:
    orders = await user_service.get_orders(user)
    return [SimpleOrderResponse.model_validate(order) for order in orders]


@user_router.get("/me/reviews")
async def get_reviews(
    user: Annotated[User, Depends(login_with_header)],
    user_service: Annotated[UserService, Depends()],
) -> list[ReviewResponse]:
    reviews = await user_service.get_reviews(user)
    response = []
    for review in reviews:
        response.append(
            ReviewResponse( # TODO update to load product as well
                review_id=review.id,
                item_id=review.product_id,
                item_name=(await review.get_products()).name,
                comment=review.comment,
                rating=review.rating,
            )
        )
    return response
