from typing import Annotated, Optional, Union, List
from sqlalchemy.orm import Session

from fastapi import Depends
from wapang.app.items.repositories import ItemRepository
from wapang.app.stores.repositories import StoreRepository
from wapang.app.items.schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest
from wapang.app.items.exceptions import (
    NickNameNotSetException,
    NoStoreOwnedException,
    ItemNotFoundException,
    NotYourItemException,
    StoreNotFoundException,
)
from wapang.app.items.models import Product


from wapang.app.reviews.repositories import ReviewRepository
from wapang.app.users.repositories import UserRepository
from wapang.app.reviews.models import Review
from wapang.app.reviews.schemas import (
    ReviewCreate,
    ReviewLoginResponse,
    ReviewLogoutResponse,
)
from wapang.app.reviews.exceptions import ReviewAlreadyExistsException


class ItemService:
    def __init__(
        self,
        item_repository: Annotated[ItemRepository, Depends()],
        store_repository: Annotated[StoreRepository, Depends()],
        review_repository: Annotated[ReviewRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        self.item_repository = item_repository
        self.store_repository = store_repository
        self.review_repository = review_repository
        self.user_repository = user_repository

    async def create_item_for_owner(
        self, user_id: str, item_request: ItemCreateRequest
    ) -> ItemResponse:
        store = await self.store_repository.get_store_by_user(user_id)
        if store is None:
            raise NoStoreOwnedException()

        new_product = Product(
            name=item_request.item_name,
            price=item_request.price,
            stock=item_request.stock,
            store_id=store.id,
        )

        self.item_repository.add_item(new_product)
        await self.item_repository.session.flush()

        return ItemResponse(
            id=new_product.id,
            item_name=new_product.name,
            price=new_product.price,
            stock=new_product.stock,
            store_id=new_product.store_id,
            store_name=store.store_name,
        )

    async def update_item_for_owner(
        self, user_id: str, item_id: str, item_request: ItemUpdateRequest
    ) -> ItemResponse:
        store = await self.store_repository.get_store_by_user(user_id)
        if not store:
            raise NoStoreOwnedException()

        product = await self.item_repository.get_item_by_id(item_id)
        if product is None:
            raise ItemNotFoundException()

        if product.store_id != store.id:
            raise NotYourItemException()

        updated_product = self.item_repository.modify_item(
            product,
            name=item_request.item_name,
            price=item_request.price,
            stock=item_request.stock,
        )
        await self.item_repository.session.flush()

        return ItemResponse(
            id=updated_product.id,
            item_name=updated_product.name,
            price=updated_product.price,
            stock=updated_product.stock,
            store_id=store.id,
            store_name=store.store_name,
        )

    async def list_items(
        self,
        store_id: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        in_stock: bool = False,
    ) -> list[ItemResponse]:

        if store_id is not None:
            store = await self.store_repository.get_store_by_id(store_id)
            if store is None:
                raise StoreNotFoundException()

        products = await self.item_repository.get_items_with_query(
            store_id=store_id,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
        )

        item_responses = []
        for product in products:
            item_responses.append(
                ItemResponse(
                    id=product.id,
                    item_name=product.name,
                    price=product.price,
                    stock=product.stock,
                    store_id=product.store_id,
                    store_name=product.store.store_name,
                )
            )

        return item_responses

    async def delete_item_for_owner(self, user_id: str, item_id: str) -> None:

        store = await self.store_repository.get_store_by_user(user_id)
        if not store:
            raise NoStoreOwnedException()

        product = await self.item_repository.get_item_by_id(item_id)
        if product is None:
            raise ItemNotFoundException()

        if product.store_id != store.id:
            raise NotYourItemException()

        self.item_repository.delete_item(product)
        await self.item_repository.session.flush()

    async def create_review_for_item(
        self, user_id: str, item_id: str, review_req: ReviewCreate
    ) -> ReviewLoginResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        if user and not user.nickname:
            raise NickNameNotSetException()

        product = await self.item_repository.get_item_by_id(item_id)
        if product is None:
            raise ItemNotFoundException()

        existing = await self.review_repository.get_user_review_for_product(user_id, item_id)
        if existing:
            raise ReviewAlreadyExistsException()

        review = Review(
            rating=review_req.rating,
            comment=review_req.comment,
            user_id=user_id,
            product_id=item_id,
        )
        await self.review_repository.add_review(review)
        await self.review_repository.session.flush()

        return ReviewLoginResponse(
            review_id=review.id,
            item_id=review.product_id,
            writer_nickname=review.user.nickname,
            is_writer=True,
            rating=review.rating,
            comment=review.comment,
        )

    async def list_reviews_for_item(
        self, item_id: str, request_user_id: Optional[str] = None
    ) -> Union[List[ReviewLoginResponse], List[ReviewLogoutResponse]]:
        product = await self.item_repository.get_item_by_id(item_id)
        if product is None:
            raise ItemNotFoundException()

        reviews = await self.review_repository.get_reviews_for_product(item_id)
        if request_user_id:
            return [
                ReviewLoginResponse(
                    review_id=r.id,
                    item_id=r.product_id,
                    writer_nickname=(await r.get_user()).nickname,
                    is_writer=(r.user_id == request_user_id),
                    rating=r.rating,
                    comment=r.comment,
                )
                for r in reviews
            ]
        else:
            return [
                ReviewLogoutResponse(
                    review_id=r.id,
                    item_id=r.product_id,
                    writer_nickname=(await r.get_user()).nickname,
                    rating=r.rating,
                    comment=r.comment,
                )
                for r in reviews
            ]
