from fastapi import APIRouter, Depends, status
from typing import Annotated

from wapang.app.auth.utils import login_with_header
from wapang.app.orders.schemas import *
from wapang.app.orders.models import *
from wapang.app.orders.services import OrderService
from wapang.app.users.models import User

order_router = APIRouter()


@order_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_orders(
    request: OrderCreateRequest,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()]
) -> OrderResponse:

    order, stores_data = await order_service.create_order(request, user)
    
    return OrderResponse(id=order.id, details=list(stores_data.values()), total_price=order.total_price, status=order.status)

@order_router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_orders(
    order_id: str,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()]
) -> OrderResponse:
    
    order ,stores_data = await order_service.get_order(order_id, user)
    
    return OrderResponse(id=order.id, details=list(stores_data.values()), total_price=order.total_price, status=order.status)

@order_router.patch("/{order_id}", status_code=status.HTTP_200_OK)
async def patch_orders(
    order_id: str,
    request: OrderPatchRequest,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()]
) -> OrderResponse:
    
    order ,stores_data = await order_service.update_order(order_id, request, user)
    
    return OrderResponse(id=order.id, details=list(stores_data.values()), total_price=order.total_price, status=order.status)
