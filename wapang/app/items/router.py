from typing import Annotated, Optional, Union
from fastapi import APIRouter, Depends, Query, Response, status

from wapang.app.auth.utils import login_with_header, optional_login_with_header
from wapang.app.items.models import Product
from wapang.app.users.models import User
from wapang.app.items.schemas import (
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemResponse
)
from wapang.app.reviews.schemas import (
    ReviewCreate,
    ReviewLoginResponse,
    ReviewLogoutResponse,
)
from wapang.app.items.services import ItemService

item_router = APIRouter()


@item_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_item(
    item: ItemCreateRequest,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
):
    return await item_service.create_item_for_owner(user.id, item)


@item_router.patch("/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(
    item_id: str,
    item: ItemUpdateRequest,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
):
    return await item_service.update_item_for_owner(user.id, item_id, item)

@item_router.get("/", status_code=status.HTTP_200_OK)
async def get_items(
    store_id: Optional[str] = Query(default=None),
    min_price: Optional[int] = Query(default=None),
    max_price: Optional[int] = Query(default=None),
    in_stock: bool = Query(default=False),
    item_service: ItemService = Depends(ItemService)
) -> list[ItemResponse]:
    return await item_service.list_items(
        store_id=store_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )

@item_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
):
    await item_service.delete_item_for_owner(user.id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@item_router.post("/{item_id}/reviews", status_code=status.HTTP_201_CREATED)
async def create_review_for_item(
    item_id: str,
    review: ReviewCreate,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
) -> ReviewLoginResponse:
    return await item_service.create_review_for_item(user.id, item_id, review)

@item_router.get("/{item_id}/reviews", status_code=status.HTTP_200_OK)
async def list_reviews_for_item(
    item_id: str,
    user: Annotated[Optional[User], Depends(optional_login_with_header)],
    item_service: Annotated[ItemService, Depends()],
) -> Union[list[ReviewLoginResponse], list[ReviewLogoutResponse]]:
    return await item_service.list_reviews_for_item(item_id, user.id if user else None)