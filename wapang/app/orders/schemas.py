from pydantic import BaseModel, Field
from typing import List
from wapang.app.orders.models import OrderStatus


class OrderItemRequest(BaseModel):
    item_id: str
    quantity: int


class OrderCreateRequest(BaseModel):
    items: List[OrderItemRequest]


class OrderItems(BaseModel):
    item_id: str
    item_name: str
    price: int
    quantity: int
    subtotal: int


class OrderDetails(BaseModel):
    store_id: str
    store_name: str
    delivery_fee: int
    store_total_price: int
    items: List[OrderItems]


class SimpleOrderResponse(BaseModel):
    id: str = Field(serialization_alias="order_id")
    total_price: int
    status: OrderStatus

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: str = Field(serialization_alias="order_id")
    details: List[OrderDetails]
    total_price: int
    status: OrderStatus


class OrderPatchRequest(BaseModel):
    status: OrderStatus
