from fastapi import APIRouter

from wapang.app.users.router import user_router
from wapang.app.auth.router import auth_router
from wapang.app.stores.router import store_router
from wapang.app.items.router import item_router
from wapang.app.orders.router import order_router
from wapang.app.reviews.router import review_router
from wapang.app.carts.router import cart_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(store_router, prefix="/stores", tags=["stores"])
api_router.include_router(item_router, prefix="/items", tags=["items"])
api_router.include_router(order_router, prefix="/orders", tags=["orders"])
api_router.include_router(review_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(cart_router, prefix="/carts", tags=["carts"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
