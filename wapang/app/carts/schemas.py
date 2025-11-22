from pydantic import BaseModel
from typing import List

class CartProductRequest(BaseModel):
    item_id: str
    quantity: int
    
class CartItems(BaseModel):
    item_id: str
    item_name: str
    price: int
    quantity: int
    subtotal: int
    
class CartDetails(BaseModel):
    store_id: str
    store_name: str
    delivery_fee: int
    store_total_price: int
    items: List[CartItems]
    
class CartResponse(BaseModel):
    details: List[CartDetails]
    total_price: int